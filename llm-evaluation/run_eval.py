from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import threading
import time
import urllib.error
import urllib.request
from copy import deepcopy
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    Draft202012Validator = None
    FormatChecker = None

try:
    import psutil
except ImportError:  # 메모리 측정만 생략하고 나머지 평가는 실행한다.
    psutil = None

ROOT = Path(__file__).resolve().parent
WORKMATE_SCHEMA = ROOT.parent / "docs" / "schemas" / "workmate-skill-schemas.schema.json"
SYSTEM_PROMPT = ROOT / "prompts" / "system.txt"

MODEL_PRICES = {
    "openai": {"input": 0.75 / 1_000_000, "output": 4.50 / 1_000_000},
}
NVIDIA_MODELS = {"nvidia_llama", "nvidia_gemma"}
EVALUATOR_VERSION = "metadata-v1"


def sha256_bytes(value: bytes) -> str:
    """바이트 입력의 SHA-256 해시를 반환한다."""
    return hashlib.sha256(value).hexdigest()


def canonical_hash(value: Any) -> str:
    """JSON 값을 정렬·압축 직렬화한 뒤 SHA-256 해시를 반환한다."""
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def file_hash(path: Path) -> str:
    """평가 입력 파일의 내용을 해시한다. Secret 파일에는 호출하지 않는다."""
    return sha256_bytes(path.read_bytes())


class ProviderError(RuntimeError):
    def __init__(
        self,
        error_type: str,
        message: str,
        *,
        retryable: bool = False,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.retryable = retryable
        self.retry_after = retry_after

GENERATION_ONLY_KEYWORDS = {
    "$schema", "default", "examples", "exclusiveMaximum", "exclusiveMinimum",
    "format", "maxLength", "maximum", "minItems", "minLength",
    "minimum", "multipleOf", "pattern", "uniqueItems",
}

FORMAT_CHECKER = FormatChecker() if FormatChecker is not None else None
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATE_TIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


def _valid_date(value: object) -> bool:
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        return False
    date.fromisoformat(value)
    return True


def _valid_date_time(value: object) -> bool:
    if not isinstance(value, str) or not DATE_TIME_PATTERN.fullmatch(value):
        return False
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.tzinfo is not None


if FORMAT_CHECKER is not None:
    FORMAT_CHECKER.checks("date", raises=ValueError)(_valid_date)
    FORMAT_CHECKER.checks("date-time", raises=ValueError)(_valid_date_time)


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        case = json.loads(raw)
        required = {"case_id", "skill_id", "schema_def", "instruction", "input", "expectations"}
        missing = required - case.keys()
        if missing:
            raise ValueError(f"{path}:{line_no} 필수 필드 누락: {sorted(missing)}")
        cases.append(case)
    if not cases:
        raise ValueError("평가 Case가 없습니다.")
    return cases


def build_target_schema(root_schema: dict[str, Any], def_name: str) -> dict[str, Any]:
    definitions = root_schema.get("$defs", {})
    if def_name not in definitions:
        raise ValueError(f"Schema 정의를 찾을 수 없습니다: {def_name}")
    needed: set[str] = set()

    def collect(node: Any) -> None:
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/$defs/"):
                name = ref.rsplit("/", 1)[-1]
                if name not in needed:
                    needed.add(name)
                    collect(definitions[name])
            for value in node.values():
                collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)

    target = deepcopy(definitions[def_name])
    collect(target)
    return {
        "$schema": root_schema.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        **target,
        "$defs": {name: deepcopy(definitions[name]) for name in sorted(needed)},
    }


def build_generation_schema(canonical_schema: dict[str, Any]) -> dict[str, Any]:
    """OpenAI 호환 API와 Ollama가 함께 처리할 생성용 JSON Schema를 만든다."""

    def make_nullable(node: dict[str, Any]) -> dict[str, Any]:
        result = deepcopy(node)
        node_type = result.get("type")
        if isinstance(node_type, str):
            result["type"] = [node_type, "null"]
        elif isinstance(node_type, list):
            if "null" not in node_type:
                result["type"] = [*node_type, "null"]
        else:
            variants = result.get("anyOf")
            if isinstance(variants, list):
                if not any(item.get("type") == "null" for item in variants if isinstance(item, dict)):
                    result["anyOf"] = [*variants, {"type": "null"}]
            else:
                result = {"anyOf": [result, {"type": "null"}]}
        return result

    def convert(node: Any) -> Any:
        if isinstance(node, list):
            return [convert(item) for item in node]
        if not isinstance(node, dict):
            return node

        converted = {
            key: convert(value)
            for key, value in node.items()
            if key not in GENERATION_ONLY_KEYWORDS
        }
        properties = converted.get("properties")
        if isinstance(properties, dict):
            original_required = set(node.get("required", []))
            for key in properties.keys() - original_required:
                properties[key] = make_nullable(properties[key])
            converted["required"] = list(properties)
            converted["additionalProperties"] = False
        if node.get("type") == "array":
            converted["maxItems"] = node.get("maxItems", 10)
        return converted

    return convert(canonical_schema)


def strip_optional_nulls(instance: Any, canonical_schema: dict[str, Any]) -> Any:
    """생성용 Schema가 강제한 선택 필드의 null을 표준 결과에서 제거한다."""
    root_schema = canonical_schema

    def resolve(schema: dict[str, Any]) -> dict[str, Any]:
        ref = schema.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            return root_schema["$defs"][ref.rsplit("/", 1)[-1]]
        return schema

    def clean(value: Any, schema: dict[str, Any]) -> Any:
        schema = resolve(schema)
        properties = schema.get("properties")
        if isinstance(value, dict) and isinstance(properties, dict):
            required = set(schema.get("required", []))
            return {
                key: clean(item, properties[key]) if key in properties else item
                for key, item in value.items()
                if not (item is None and key in properties and key not in required)
            }
        if isinstance(value, list) and isinstance(schema.get("items"), dict):
            return [clean(item, schema["items"]) for item in value]
        return value

    return clean(instance, canonical_schema)


def request_json(
    url: str,
    headers: dict[str, str],
    timeout: int,
    *,
    method: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None,
        headers={"Content-Type": "application/json", **headers},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        if exc.code == 429:
            error_type = "rate_limit"
        elif exc.code in {502, 503, 504}:
            error_type = "http_5xx"
        elif exc.code in {401, 403}:
            error_type = "authentication"
        else:
            error_type = "http_error"
        retry_after = exc.headers.get("Retry-After") if exc.headers else None
        raise ProviderError(
            error_type,
            f"HTTP {exc.code}: {detail}",
            retryable=exc.code == 429 or exc.code in {502, 503, 504},
            retry_after=float(retry_after) if retry_after and retry_after.isdigit() else None,
        ) from exc
    except TimeoutError as exc:
        raise ProviderError("timeout", "The read operation timed out", retryable=True) from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise ProviderError("timeout", "The read operation timed out", retryable=True) from exc
        raise ProviderError("connection", str(exc.reason), retryable=True) from exc


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int) -> dict[str, Any]:
    return request_json(url, headers, timeout, method="POST", payload=payload)[1]


def get_json(url: str, headers: dict[str, str], timeout: int) -> dict[str, Any]:
    return request_json(url, headers, timeout, method="GET")[1]


def parse_json_content(content: Any) -> dict[str, Any]:
    if isinstance(content, dict):
        return content
    text = str(content).strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("최상위 응답은 JSON object여야 합니다.")
    return parsed


class MemorySampler:
    def __init__(self, enabled: bool, ollama_url: str) -> None:
        self.enabled = enabled
        self.ollama_url = ollama_url.rstrip("/")
        self.host_process_rss_peak_mb: float | None = None
        self.ollama_model_size_peak_mb: float | None = None
        self.ollama_vram_peak_mb: float | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(self) -> "MemorySampler":
        if self.enabled:
            self._thread = threading.Thread(target=self._sample, daemon=True)
            self._thread.start()
        return self

    def _sample(self) -> None:
        while not self._stop.is_set():
            if psutil is not None:
                total = 0
                seen = False
                for process in psutil.process_iter(["name", "memory_info"]):
                    try:
                        if "ollama" in (process.info["name"] or "").lower():
                            total += process.info["memory_info"].rss
                            seen = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                if seen:
                    value = total / 1024 / 1024
                    self.host_process_rss_peak_mb = max(self.host_process_rss_peak_mb or 0, value)

            try:
                with urllib.request.urlopen(self.ollama_url + "/api/ps", timeout=1) as response:
                    models = json.loads(response.read().decode("utf-8")).get("models", [])
                if models:
                    model_size = sum(int(model.get("size") or 0) for model in models) / 1024 / 1024
                    vram_size = sum(int(model.get("size_vram") or 0) for model in models) / 1024 / 1024
                    self.ollama_model_size_peak_mb = max(self.ollama_model_size_peak_mb or 0, model_size)
                    self.ollama_vram_peak_mb = max(self.ollama_vram_peak_mb or 0, vram_size)
            except (OSError, ValueError, json.JSONDecodeError):
                pass
            self._stop.wait(0.5)

    def __exit__(self, *_: Any) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)


def model_config(name: str) -> dict[str, str]:
    if name == "openai":
        return {"model": os.getenv("OPENAI_MODEL", "gpt-5.4-mini-2026-03-17")}
    if name == "openai2":
        return {"model": os.getenv("OPENAI_MODEL2", "")}
    if name == "qwen":
        return {"model": os.getenv("OLLAMA_QWEN_MODEL", "qwen2.5:3b")}
    if name == "nvidia_llama":
        return {"model": os.getenv("NVIDIA_LLAMA_MODEL", "meta/llama-3.3-70b-instruct")}
    if name == "nvidia_gemma":
        return {"model": os.getenv("NVIDIA_GEMMA_MODEL", "google/gemma-4-31b-it")}
    raise ValueError(f"지원하지 않는 모델: {name}")


def generation_settings(name: str) -> dict[str, Any]:
    """모델별 생성 설정을 요청과 실행 메타데이터에 동일하게 사용한다."""
    if name in {"openai", "openai2"}:
        return {
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0")),
            "top_p": float(os.getenv("LLM_TOP_P", "1")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "1024")),
            "stream": False,
        }
    if name == "nvidia_llama":
        return {
            "temperature": float(os.getenv("NVIDIA_TEMPERATURE", "0.2")),
            "top_p": float(os.getenv("NVIDIA_TOP_P", "0.7")),
            "max_tokens": int(os.getenv("NVIDIA_MAX_TOKENS", "1024")),
            "stream": False,
        }
    if name == "nvidia_gemma":
        return {
            "temperature": float(os.getenv("NVIDIA_GEMMA_TEMPERATURE", "1.0")),
            "top_p": float(os.getenv("NVIDIA_GEMMA_TOP_P", "0.95")),
            "max_tokens": int(os.getenv("NVIDIA_GEMMA_MAX_TOKENS", "1024")),
            "stream": False,
        }
    return {
        "temperature": None,
        "top_p": None,
        "max_tokens": int(os.getenv("OLLAMA_NUM_PREDICT", "1024")),
        "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "8192")),
        "stream": False,
    }


def build_messages(name: str, case: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, str]]:
    """Case와 Schema로 실제 Provider에 전달할 Prompt 메시지를 만든다."""
    system = SYSTEM_PROMPT.read_text(encoding="utf-8")
    user = case["instruction"] + "\n\n입력:\n" + json.dumps(case["input"], ensure_ascii=False, indent=2)
    if name == "nvidia_gemma":
        user += "\n\n반드시 다음 JSON Schema를 만족하는 JSON 객체만 반환하라:\n" + json.dumps(
            schema, ensure_ascii=False, separators=(",", ":")
        )
        return [{"role": "user", "content": system + "\n\n" + user}]
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def build_run_metadata(
    *, run_id: str, name: str, cases_path: Path, repeat_no: int, timeout: int,
) -> dict[str, Any]:
    """실행 조건을 Secret 없이 기록할 공통 메타데이터를 만든다."""
    price = MODEL_PRICES.get(name)
    resolved_cases_path = cases_path.resolve()
    try:
        case_file = str(resolved_cases_path.relative_to(ROOT.parent)).replace("\\", "/")
    except ValueError:
        case_file = resolved_cases_path.name
    return {
        "run_id": run_id,
        "evaluator_version": EVALUATOR_VERSION,
        "evaluator_commit": os.getenv("EVALUATOR_COMMIT", "unknown"),
        "model_group": name,
        "model": model_config(name)["model"],
        "provider": "openai-compatible" if name in {"openai", "openai2"} else name,
        "case_file": case_file,
        "case_file_hash": file_hash(cases_path),
        "repeat": repeat_no,
        "timeout_seconds": timeout,
        "generation_settings": generation_settings(name),
        "retry_policy": {
            "provider_retries": int(os.getenv("PROVIDER_RETRIES", "1")),
            "retry_delay_seconds": float(os.getenv("PROVIDER_RETRY_DELAY_SECONDS", "2")),
            "schema_repairs": 1,
            "semantic_repairs": 1,
        },
        "pricing": {
            "status": "configured" if price else "unavailable",
            "source": os.getenv("LLM_PRICING_SOURCE", "not configured"),
            "input_usd_per_token": price["input"] if price else None,
            "output_usd_per_token": price["output"] if price else None,
        },
    }


def build_case_metadata(
    base: dict[str, Any], name: str, case: dict[str, Any], schema: dict[str, Any], generation_schema: dict[str, Any],
) -> dict[str, Any]:
    """실행 메타데이터에 Case·Prompt·Schema 해시를 추가한다."""
    messages = build_messages(name, case, schema if name == "nvidia_gemma" else generation_schema)
    return {
        **base,
        "case_id": case["case_id"],
        "case_hash": canonical_hash(case),
        "prompt_hash": canonical_hash(messages),
        "schema_hash": canonical_hash(schema),
        "generation_schema_hash": canonical_hash(generation_schema),
    }


def check_nvidia_models_available(names: list[str], timeout: int) -> dict[str, ProviderError]:
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ProviderError("authentication", "NVIDIA_API_KEY가 설정되지 않았습니다.")
    base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
    retries = int(os.getenv("PROVIDER_RETRIES", "1"))
    retry_delay = float(os.getenv("PROVIDER_RETRY_DELAY_SECONDS", "2"))
    for attempt in range(retries + 1):
        try:
            response = get_json(base_url + "/models", {"Authorization": f"Bearer {api_key}"}, timeout)
            break
        except ProviderError as exc:
            if not exc.retryable or attempt == retries:
                raise
            time.sleep(min(exc.retry_after or retry_delay, 30))
    available = {item.get("id") for item in response.get("data", [])}
    return {
        name: ProviderError(
            "model_unavailable",
            f"NVIDIA API에서 모델을 사용할 수 없습니다: {model_config(name)['model']}",
        )
        for name in names
        if model_config(name)["model"] not in available
    }


def strip_gemma_thought(content: Any) -> Any:
    if not isinstance(content, str):
        return content
    text = content.strip()
    if text.startswith("<|channel>thought") and "<channel|>" in text:
        text = text.rpartition("<channel|>")[2].lstrip()
    if text.startswith("<|channel>final"):
        text = text.removeprefix("<|channel>final").lstrip()
    return text


def call_nvidia_gemma(
    base_url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout: int,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    status, response = request_json(
        base_url.rstrip("/") + "/chat/completions",
        headers,
        timeout,
        method="POST",
        payload=payload,
    )
    while status == 202:
        request_id = response.get("requestId")
        if not isinstance(request_id, str) or not request_id:
            raise ProviderError("invalid_response", "NVIDIA 202 응답에 requestId가 없습니다.")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ProviderError("timeout", "NVIDIA 비동기 응답 대기 시간이 초과됐습니다.", retryable=True)
        time.sleep(min(float(os.getenv("PROVIDER_RETRY_DELAY_SECONDS", "2")), remaining))
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ProviderError("timeout", "NVIDIA 비동기 응답 대기 시간이 초과됐습니다.", retryable=True)
        try:
            status, response = request_json(
                base_url.rstrip("/") + f"/status/{request_id}",
                headers,
                max(1, int(remaining)),
                method="GET",
            )
        except ProviderError as exc:
            if exc.retryable and time.monotonic() < deadline:
                continue
            raise
    if status != 200:
        raise ProviderError("http_error", f"예상하지 못한 NVIDIA 응답 상태입니다: {status}")
    return response


def call_model(name: str, messages: list[dict[str, str]], schema: dict[str, Any], timeout: int) -> dict[str, Any]:
    config = model_config(name)
    if name in {"openai", "openai2"} or name in NVIDIA_MODELS:
        api_key_name = "OPENAI_API_KEY2" if name == "openai2" else "OPENAI_API_KEY" if name == "openai" else "NVIDIA_API_KEY"
        api_key = os.getenv(api_key_name)
        if not api_key:
            raise ProviderError("authentication", f"{api_key_name}가 설정되지 않았습니다.")
        if name == "openai2":
            base_url = os.getenv("OPENAI_BASE_URL2", "")
            if not base_url:
                raise ProviderError("configuration", "OPENAI_BASE_URL2가 설정되지 않았습니다.")
            if not config["model"]:
                raise ProviderError("configuration", "OPENAI_MODEL2가 설정되지 않았습니다.")
        elif name == "openai":
            base_url = "https://api.openai.com/v1"
        else:
            base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        payload: dict[str, Any] = {"model": config["model"], "messages": messages}
        if name != "nvidia_gemma":
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "workmate_result", "strict": True, "schema": schema},
            }
        if name in {"openai", "openai2", "nvidia_llama"}:
            payload.update(generation_settings(name))
        elif name == "nvidia_gemma":
            payload.update({
                "chat_template_kwargs": {"enable_thinking": False},
                **generation_settings(name),
            })
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        response = (
            call_nvidia_gemma(base_url, payload, headers, timeout)
            if name == "nvidia_gemma"
            else post_json(base_url.rstrip("/") + "/chat/completions", payload, headers, timeout)
        )
        usage = response.get("usage", {})
        return {
            "content": strip_gemma_thought(response["choices"][0]["message"]["content"])
            if name == "nvidia_gemma"
            else response["choices"][0]["message"]["content"],
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
            "tokens_per_second": None,
        }

    response = post_json(
        os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/chat",
        {
            "model": config["model"], "messages": messages, "format": schema, "stream": False,
            "options": {
                "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "8192")),
                "num_predict": int(os.getenv("OLLAMA_NUM_PREDICT", "1024")),
            },
        },
        {},
        timeout,
    )
    eval_count = response.get("eval_count", 0)
    eval_duration = response.get("eval_duration", 0)
    return {
        "content": response["message"]["content"],
        "input_tokens": response.get("prompt_eval_count", 0),
        "output_tokens": eval_count,
        "tokens_per_second": round(eval_count / (eval_duration / 1_000_000_000), 2) if eval_duration else None,
    }


def validation_errors(instance: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    if Draft202012Validator is None or FORMAT_CHECKER is None:
        raise RuntimeError("실제 평가 전 requirements.txt를 설치해야 합니다.")
    validator = Draft202012Validator(schema, format_checker=FORMAT_CHECKER)
    return [error.message for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.path))]


def validate_case_inputs(case: dict[str, Any], schema: dict[str, Any]) -> None:
    priorities = case.get("input", {}).get("precomputed_priorities", [])
    if not priorities:
        return
    priority_schema = {
        "$schema": schema["$schema"],
        "$ref": "#/$defs/PriorityItem",
        "$defs": schema["$defs"],
    }
    for index, priority in enumerate(priorities):
        errors = validation_errors(priority, priority_schema)
        breakdown = priority.get("score_breakdown", {})
        if priority.get("score") != sum(value for value in breakdown.values() if isinstance(value, int)):
            errors.append("score와 score_breakdown 합계가 다릅니다.")
        if errors:
            raise ValueError(
                f"{case['case_id']} input.precomputed_priorities[{index}] 오류: " + "; ".join(errors)
            )


def assert_format_validation() -> None:
    schema = {"type": "object", "properties": {"value": {"type": "string", "format": "date-time"}}}
    if not validation_errors({"value": "내일 오전까지"}, schema):
        raise RuntimeError("date-time 형식 검증기가 작동하지 않습니다.")


def collect_source_ids(skill_id: str, output: dict[str, Any]) -> list[str]:
    source_ids = {value for value in output.get("source_refs", []) if isinstance(value, str)}
    if skill_id == "daily_briefing":
        source_ids.update(item.get("task_id") for item in output.get("priorities", []))
        source_ids.update(item.get("source_id") for item in output.get("important_signals", []))
        source_ids.update(item.get("event_id") for item in output.get("calendar_events", []))
    elif skill_id == "weekly_report":
        for category in ("completed", "in_progress", "delayed", "unresolved_issues"):
            for item in output.get(category, []):
                source_ids.add(item.get("task_id"))
                source_ids.update(item.get("source_refs", []))
        for item in output.get("next_week_plans", []):
            source_ids.update(item.get("source_refs", []))
    elif skill_id == "analyze_meeting":
        source_ids.update((output.get("meeting_id"), output.get("transcript_ref")))
        for item in output.get("action_items", []):
            source_ids.update((item.get("evidence_span") or {}).get("meeting_chunk_ids", []))
    elif skill_id == "search_meetings":
        for item in output.get("sources", []):
            source_ids.update((item.get("meeting_id"), item.get("meeting_chunk_id")))
    source_ids.discard(None)
    return sorted(source_ids)


def expectation_score(
    output: dict[str, Any],
    expectations: dict[str, Any],
    *,
    actual_source_ids: list[str] | None = None,
    actual_evidence_texts: list[str] | None = None,
) -> dict[str, Any]:
    text = json.dumps(output, ensure_ascii=False)
    must = expectations.get("must_include", [])
    forbidden = expectations.get("forbidden", [])
    sources = expectations.get("expected_source_ids", [])
    evidence = expectations.get("evidence_texts", [])
    expected_values = expectations.get("expected_values", {})
    actual_source_ids = actual_source_ids if actual_source_ids is not None else output.get("source_refs", [])
    actual_evidence_texts = actual_evidence_texts or []
    checks = {
        "must_include": sum(item in text for item in must) / len(must) if must else 1.0,
        "forbidden_absent": sum(item not in text for item in forbidden) / len(forbidden) if forbidden else 1.0,
        "source_ids": sum(item in actual_source_ids for item in sources) / len(sources) if sources else 1.0,
        "evidence_exact": sum(item in actual_evidence_texts for item in evidence) / len(evidence) if evidence else 1.0,
        "expected_values": (
            sum(output.get(key) == value for key, value in expected_values.items()) / len(expected_values)
            if expected_values else 1.0
        ),
    }
    checks["average"] = round(sum(checks.values()) / len(checks), 4)
    return checks


def grade_output(case: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    skill_id = case["skill_id"]
    expectations = case["expectations"]
    source_ids = collect_source_ids(skill_id, output)
    if skill_id == "search_meetings":
        evidence_texts = [source.get("quote") for source in output.get("sources", []) if source.get("quote")]
    elif skill_id == "analyze_meeting":
        evidence_texts = [item.get("evidence_text") for item in output.get("action_items", []) if item.get("evidence_text")]
    else:
        evidence_texts = []

    base = expectation_score(
        output,
        expectations,
        actual_source_ids=source_ids,
        actual_evidence_texts=evidence_texts,
    )
    checks = {key: value for key, value in base.items() if key != "average"}
    errors = [f"{key} 검사에 실패했습니다." for key, value in checks.items() if value < 1.0]

    def record(name: str, condition: bool, message: str) -> None:
        checks[name] = 1.0 if condition else 0.0
        if not condition:
            errors.append(message)

    if skill_id == "daily_briefing":
        priorities = output.get("priorities", [])
        precomputed = case["input"].get("precomputed_priorities", [])
        record("priority_count", len(priorities) == min(3, len(precomputed)), "Top 3 개수가 사전 계산 결과와 다릅니다.")
        record("priority_ranks", [item.get("rank") for item in priorities] == list(range(1, len(priorities) + 1)), "우선순위 rank가 연속적이지 않습니다.")
        scores = [item.get("score") for item in priorities]
        record("priority_order", scores == sorted(scores, reverse=True), "우선순위가 점수 내림차순이 아닙니다.")
        expected = [
            {key: item.get(key) for key in ("rank", "task_id", "title", "score", "score_breakdown", "reasons")}
            for item in precomputed[:3]
        ]
        actual = [
            {key: item.get(key) for key in ("rank", "task_id", "title", "score", "score_breakdown", "reasons")}
            for item in priorities
        ]
        record("priority_values_preserved", actual == expected, "Priority Service의 사전 계산값이 변경됐습니다.")
        record(
            "priority_score_sums",
            all(item.get("score") == sum((item.get("score_breakdown") or {}).values()) for item in priorities),
            "score와 score_breakdown 합계가 다릅니다.",
        )
        task_ids = {item.get("task_id") for item in case["input"].get("tasks", [])}
        allowed_sources = task_ids | {
            item.get("source_id") for item in case["input"].get("calendar", [])
        } | {
            item.get("source_id") for item in case["input"].get("emails", [])
        } | {
            item.get("action_item_id") for item in case["input"].get("meeting_signals", [])
        }
        declared_sources = set(output.get("source_refs", []))
        declared_sources.update(item.get("event_id") for item in output.get("calendar_events", []))
        declared_sources.update(item.get("source_id") for item in output.get("important_signals", []))
        related_task_ids = {
            task_id
            for item in [*output.get("calendar_events", []), *output.get("important_signals", [])]
            for task_id in item.get("related_task_ids", [])
        }
        record(
            "daily_source_grounding",
            declared_sources <= allowed_sources and related_task_ids <= task_ids,
            "브리핑에 입력에 없는 출처 또는 Task 연결이 포함됐습니다.",
        )
        summary_forbidden = expectations.get("summary_forbidden", [])
        if summary_forbidden:
            record(
                "priority_summary_consistency",
                all(value not in output.get("summary", "") for value in summary_forbidden),
                "브리핑 설명이 사전 계산된 우선순위와 모순됩니다.",
            )

    elif skill_id == "weekly_report":
        period = case["input"].get("period", {})
        expected_period = {key: str(period.get(key, "")).split("T", 1)[0] for key in ("start", "end")}
        record("weekly_period", output.get("period") == expected_period, "주간 보고 기간 경계가 입력과 다릅니다.")
        expected_categories = {
            "completed": {item["task_id"] for item in case["input"].get("tasks", []) if item.get("status") == "done"},
            "in_progress": {item["task_id"] for item in case["input"].get("tasks", []) if item.get("status") == "in_progress"},
            "delayed": {item["task_id"] for item in case["input"].get("tasks", []) if item.get("status") == "blocked"},
            "unresolved_issues": {item["task_id"] for item in case["input"].get("tasks", []) if item.get("status") == "blocked"},
        }
        for category, expected_ids in expected_categories.items():
            actual_ids = {item.get("task_id") for item in output.get(category, [])}
            record(f"weekly_{category}", actual_ids == expected_ids, f"{category} Task 분류가 다릅니다.")
        expected_plan_sources = set(expectations.get("expected_next_week_plan_source_ids", []))
        if expected_plan_sources:
            actual_plan_sources = {
                source_id
                for item in output.get("next_week_plans", [])
                for source_id in item.get("source_refs", [])
            }
            record(
                "weekly_next_week_plans",
                expected_plan_sources <= actual_plan_sources,
                "다음 주 계획의 필수 Task 또는 회의 근거가 누락됐습니다.",
            )
        allowed_sources = {
            item.get("task_id") for item in case["input"].get("tasks", [])
        } | {
            item.get("meeting_id") for item in case["input"].get("meetings", [])
        }
        record(
            "weekly_source_grounding",
            set(collect_source_ids(skill_id, output)) <= allowed_sources,
            "주간 보고에 입력에 없는 출처가 포함됐습니다.",
        )

    elif skill_id == "analyze_meeting":
        chunks = {item["meeting_chunk_id"]: item for item in case["input"].get("chunks", [])}
        spans_valid = True
        evidence_valid = True
        for action in output.get("action_items", []):
            span = action.get("evidence_span", {})
            ids = span.get("meeting_chunk_ids", [])
            selected = [chunks[item_id] for item_id in ids if item_id in chunks]
            spans_valid &= bool(selected) and len(selected) == len(ids)
            if selected:
                spans_valid &= span.get("start_ms") == min(item["start_ms"] for item in selected)
                spans_valid &= span.get("end_ms") == max(item["end_ms"] for item in selected)
                evidence_valid &= action.get("evidence_text") in {item["content"] for item in selected}
        record("meeting_evidence_span", spans_valid, "Action Item 근거 구간이 입력 Chunk와 일치하지 않습니다.")
        record("meeting_evidence_exact", evidence_valid, "evidence_text가 선택된 원문과 정확히 일치하지 않습니다.")
        allowed_sources = set(chunks) | {case["input"].get("meeting_id"), case["input"].get("transcript_ref")}
        record(
            "meeting_source_grounding",
            set(output.get("source_refs", [])) <= allowed_sources,
            "회의 분석에 입력에 없는 출처가 포함됐습니다.",
        )
        if expectations.get("allow_resolved_relative_due_at") is False:
            no_due_at = all(item.get("due_at") is None for item in output.get("action_items", []))
            record("meeting_relative_due_at", no_due_at, "기준 시각 없이 상대 마감일을 절대 시각으로 생성했습니다.")

    elif skill_id == "search_meetings":
        contexts = {
            (item.get("meeting_id"), item.get("meeting_chunk_id")): item
            for item in case["input"].get("contexts", [])
        }
        sources_valid = True
        for source in output.get("sources", []):
            context = contexts.get((source.get("meeting_id"), source.get("meeting_chunk_id")))
            sources_valid &= bool(context) and source.get("quote") == context.get("content")
        record("search_source_context", sources_valid and bool(output.get("sources")), "검색 출처가 입력 Context와 정확히 일치하지 않습니다.")
        answer_required = expectations.get("answer_must_include", [])
        if answer_required:
            record(
                "search_answer_content",
                all(value in output.get("answer", "") for value in answer_required),
                "검색 답변 자체에 필수 내용이 누락됐습니다.",
            )
        quote_required = expectations.get("source_quote_must_include", [])
        if quote_required:
            quotes = [item.get("quote", "") for item in output.get("sources", [])]
            record(
                "search_quote_content",
                all(any(value in quote for quote in quotes) for value in quote_required),
                "검색 출처 인용문에 필수 근거가 누락됐습니다.",
            )

    average = round(sum(checks.values()) / len(checks), 4) if checks else 1.0
    return {**checks, "average": average, "valid": not errors and average == 1.0, "errors": errors}


def run_case(
    name: str, case: dict[str, Any], schema: dict[str, Any], timeout: int,
    run_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    generation_schema = build_generation_schema(schema)
    messages = build_messages(name, case, schema if name == "nvidia_gemma" else generation_schema)
    metadata = build_case_metadata(run_metadata or {}, name, case, schema, generation_schema)
    started = time.perf_counter()
    parsed: dict[str, Any] = {}
    errors: list[str] = []
    provider_error: dict[str, str] | None = None
    evaluation: dict[str, Any] | None = None
    attempt_details: list[dict[str, Any]] = []
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    request_timeout = int(os.getenv("NVIDIA_TIMEOUT", str(timeout))) if name in NVIDIA_MODELS else timeout
    provider_retries = int(os.getenv("PROVIDER_RETRIES", "1"))
    retry_delay = float(os.getenv("PROVIDER_RETRY_DELAY_SECONDS", "2"))
    request_no = 0
    schema_repairs = 0
    semantic_repairs = 0
    repair_type = "initial"
    with MemorySampler(enabled=name == "qwen", ollama_url=ollama_url) as memory:
        for generation_attempt in (1, 2, 3):
            usage: dict[str, Any] | None = None
            for provider_attempt in range(1, provider_retries + 2):
                request_no += 1
                attempt_started = time.perf_counter()
                try:
                    usage = call_model(name, messages, generation_schema, request_timeout)
                except ProviderError as exc:
                    attempt_details.append({
                        "attempt": request_no,
                        "schema_attempt": generation_attempt,
                        "repair_type": repair_type,
                        "provider_attempt": provider_attempt,
                        "latency_ms": round((time.perf_counter() - attempt_started) * 1000, 1),
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "tokens_per_second": None,
                        "error_type": f"provider_{exc.error_type}",
                        "errors": [str(exc)],
                    })
                    if exc.retryable and provider_attempt <= provider_retries:
                        time.sleep(min(exc.retry_after or retry_delay, 30))
                        continue
                    provider_error = {"type": exc.error_type, "message": str(exc)}
                except Exception as exc:
                    attempt_details.append({
                        "attempt": request_no,
                        "schema_attempt": generation_attempt,
                        "repair_type": repair_type,
                        "provider_attempt": provider_attempt,
                        "latency_ms": round((time.perf_counter() - attempt_started) * 1000, 1),
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "tokens_per_second": None,
                        "error_type": "provider_unexpected",
                        "errors": [str(exc)],
                    })
                    provider_error = {"type": "unexpected", "message": str(exc)}
                break
            if provider_error or usage is None:
                break
            try:
                parsed = strip_optional_nulls(parse_json_content(usage["content"]), schema)
                errors = validation_errors(parsed, schema)
            except (json.JSONDecodeError, ValueError) as exc:
                errors = [str(exc)]
            attempt_details.append({
                "attempt": request_no,
                "schema_attempt": generation_attempt,
                "repair_type": repair_type,
                "provider_attempt": provider_attempt,
                "latency_ms": round((time.perf_counter() - attempt_started) * 1000, 1),
                "input_tokens": int(usage.get("input_tokens") or 0),
                "output_tokens": int(usage.get("output_tokens") or 0),
                "tokens_per_second": usage.get("tokens_per_second"),
                "error_type": "schema" if errors else None,
                "errors": errors,
            })
            if errors:
                if schema_repairs >= 1:
                    break
                schema_repairs += 1
                repair_type = "schema"
                messages.extend([
                    {"role": "assistant", "content": str(usage["content"])},
                    {"role": "user", "content": "다음 Schema 오류만 수정해 JSON 객체를 다시 반환하라: " + "; ".join(errors[:5])},
                ])
                continue

            evaluation = grade_output(case, parsed)
            if not evaluation["valid"]:
                attempt_details[-1]["error_type"] = "semantic"
                attempt_details[-1]["errors"] = evaluation["errors"]
            if evaluation["valid"] or semantic_repairs >= 1:
                break
            semantic_repairs += 1
            repair_type = "semantic"
            messages.extend([
                {"role": "assistant", "content": str(usage["content"])},
                {"role": "user", "content": "입력과 업무 규칙을 다시 대조하여 다음 의미 오류만 수정한 JSON 객체를 반환하라: " + "; ".join(evaluation["errors"][:5])},
            ])
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    input_tokens = sum(item["input_tokens"] for item in attempt_details)
    output_tokens = sum(item["output_tokens"] for item in attempt_details)
    price = MODEL_PRICES.get(name)
    cost = round(input_tokens * price["input"] + output_tokens * price["output"], 6) if price else None
    generation_seconds = sum(
        item["output_tokens"] / item["tokens_per_second"]
        for item in attempt_details
        if item["tokens_per_second"] and item["output_tokens"]
    )
    tokens_per_second = round(output_tokens / generation_seconds, 2) if generation_seconds else None
    schema_valid = None if provider_error else not errors
    semantic_valid = None if provider_error else bool(evaluation and evaluation["valid"])
    final_score = None if provider_error else evaluation["average"] if schema_valid and semantic_valid else 0.0
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "case_id": case["case_id"],
        "skill_id": case["skill_id"],
        "model_group": name,
        "model": model_config(name)["model"],
        "run_metadata": metadata,
        "attempts": len(attempt_details),
        "attempt_details": attempt_details,
        "schema_valid": schema_valid,
        "execution_status": "provider_failed" if provider_error else "completed",
        "provider_error": provider_error,
        "schema_errors": [] if provider_error else errors,
        "semantic_valid": semantic_valid,
        "semantic_errors": (evaluation or {}).get("errors", []),
        "final_score": final_score,
        "latency_ms": elapsed_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": cost,
        "tokens_per_second": tokens_per_second,
        "ollama_model_size_mb": round(memory.ollama_model_size_peak_mb, 1) if memory.ollama_model_size_peak_mb is not None else None,
        "ollama_vram_mb": round(memory.ollama_vram_peak_mb, 1) if memory.ollama_vram_peak_mb is not None else None,
        "host_ollama_rss_mb": round(memory.host_process_rss_peak_mb, 1) if memory.host_process_rss_peak_mb is not None else None,
        "expectation": evaluation,
        "output": parsed,
    }


def write_results(results: list[dict[str, Any]], run_id: str | None = None) -> tuple[Path, Path]:
    """JSONL 원본과 CSV 요약에 실행 메타데이터를 보존한다."""
    stamp = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    (ROOT / "results").mkdir(parents=True, exist_ok=True)
    jsonl_path = ROOT / "results" / f"run-{stamp}.jsonl"
    csv_path = ROOT / "results" / f"summary-{stamp}.csv"
    jsonl_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in results) + "\n", encoding="utf-8")
    fields = [
        "run_id", "evaluator_version", "evaluator_commit", "case_file_hash", "case_hash",
        "prompt_hash", "schema_hash", "generation_schema_hash", "model_group", "model", "case_id", "skill_id", "execution_status", "provider_error_type",
        "temperature", "top_p", "max_tokens", "timeout_seconds", "provider_retries", "retry_delay_seconds", "pricing_status",
        "schema_valid", "semantic_valid",
        "final_score", "attempts", "latency_ms", "input_tokens", "output_tokens",
        "estimated_cost_usd", "tokens_per_second", "ollama_model_size_mb", "ollama_vram_mb",
        "host_ollama_rss_mb", "expectation_average",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in results:
            metadata = row.get("run_metadata") or {}
            settings = metadata.get("generation_settings") or {}
            retry_policy = metadata.get("retry_policy") or {}
            pricing = metadata.get("pricing") or {}
            writer.writerow({
                **{key: row.get(key) for key in fields},
                "run_id": metadata.get("run_id"),
                "evaluator_version": metadata.get("evaluator_version"),
                "evaluator_commit": metadata.get("evaluator_commit"),
                "case_file_hash": metadata.get("case_file_hash"),
                "case_hash": metadata.get("case_hash"),
                "prompt_hash": metadata.get("prompt_hash"),
                "schema_hash": metadata.get("schema_hash"),
                "generation_schema_hash": metadata.get("generation_schema_hash"),
                "temperature": settings.get("temperature"),
                "top_p": settings.get("top_p"),
                "max_tokens": settings.get("max_tokens"),
                "timeout_seconds": metadata.get("timeout_seconds"),
                "provider_retries": retry_policy.get("provider_retries"),
                "retry_delay_seconds": retry_policy.get("retry_delay_seconds"),
                "pricing_status": pricing.get("status"),
                "provider_error_type": (row.get("provider_error") or {}).get("type"),
                "expectation_average": (row.get("expectation") or {}).get("average"),
            })
    return jsonl_path, csv_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Workmate LLM 후보 평가 실행기")
    parser.add_argument("--cases", type=Path, default=ROOT / "cases" / "sample_cases.jsonl")
    parser.add_argument("--models", default="openai2")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    root_schema = json.loads(WORKMATE_SCHEMA.read_text(encoding="utf-8"))
    cases = load_cases(args.cases)
    schemas = {case["schema_def"]: build_target_schema(root_schema, case["schema_def"]) for case in cases}
    if Draft202012Validator is not None:
        assert_format_validation()
        for case in cases:
            Draft202012Validator.check_schema(schemas[case["schema_def"]])
            validate_case_inputs(case, schemas[case["schema_def"]])
        print(f"Case {len(cases)}개와 JSON Schema 검증 완료")
    else:
        print(f"Case {len(cases)}개와 Schema 참조 검증 완료 (jsonschema 미설치: 정식 검증 생략)")
    if args.dry_run:
        return
    if Draft202012Validator is None:
        raise RuntimeError("실제 평가 전 pip install -r requirements.txt를 실행하세요.")

    models = [name.strip() for name in args.models.split(",") if name.strip()]
    unknown = set(models) - {"openai", "openai2", "qwen", *NVIDIA_MODELS}
    if unknown:
        raise ValueError(f"지원하지 않는 모델: {sorted(unknown)}")
    preflight_errors: dict[str, ProviderError] = {}
    selected_nvidia = [name for name in models if name in NVIDIA_MODELS]
    if selected_nvidia:
        try:
            preflight_errors.update(check_nvidia_models_available(selected_nvidia, args.timeout))
        except ProviderError as exc:
            preflight_errors.update({name: exc for name in selected_nvidia})
        except Exception as exc:
            preflight_errors.update({name: ProviderError("preflight", str(exc)) for name in selected_nvidia})
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    results = []
    for repeat_no in range(1, args.repeat + 1):
        for name in models:
            for case in cases:
                print(f"[{repeat_no}/{args.repeat}] {name} / {case['case_id']}")
                target_schema = schemas[case["schema_def"]]
                generation_schema = build_generation_schema(target_schema)
                metadata = build_case_metadata(
                    build_run_metadata(
                        run_id=run_id,
                        name=name,
                        cases_path=args.cases,
                        repeat_no=repeat_no,
                        timeout=args.timeout,
                    ),
                    name,
                    case,
                    target_schema,
                    generation_schema,
                )
                try:
                    if name in preflight_errors:
                        raise RuntimeError(preflight_errors[name])
                    result = run_case(name, case, target_schema, args.timeout, metadata)
                except ProviderError as exc:
                    result = {
                        "timestamp": datetime.now(timezone.utc).isoformat(), "case_id": case["case_id"],
                        "skill_id": case["skill_id"], "model_group": name, "model": model_config(name)["model"],
                        "run_metadata": metadata,
                        "execution_status": "provider_failed", "provider_error": {"type": exc.error_type, "message": str(exc)},
                        "schema_valid": None, "semantic_valid": None, "final_score": None,
                        "attempts": 0, "attempt_details": [], "schema_errors": [],
                        "semantic_errors": [], "output": {},
                    }
                except Exception as exc:  # 한 모델 실패가 전체 평가를 중단하지 않게 기록한다.
                    result = {
                        "timestamp": datetime.now(timezone.utc).isoformat(), "case_id": case["case_id"],
                        "skill_id": case["skill_id"], "model_group": name, "model": model_config(name)["model"],
                        "run_metadata": metadata,
                        "execution_status": "execution_failed", "provider_error": None,
                        "schema_valid": None, "semantic_valid": None, "final_score": None,
                        "attempts": 0, "attempt_details": [], "schema_errors": [str(exc)],
                        "semantic_errors": [], "output": {},
                    }
                results.append(result)
    jsonl_path, csv_path = write_results(results, run_id)
    print(f"원본 결과: {jsonl_path}")
    print(f"요약 결과: {csv_path}")
    print(f"실행 환경: {platform.system()} / Python {platform.python_version()}")


if __name__ == "__main__":
    main()
