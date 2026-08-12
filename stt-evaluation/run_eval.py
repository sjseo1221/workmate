"""Minimal file-based STT evaluator. Real API calls require explicit local execution."""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).parent


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"'))


def load_cases(path: Path) -> list[dict]:
    cases = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        case = json.loads(raw)
        if not case.get("case_id") or not case.get("audio"):
            raise ValueError(f"line {line_no}: case_id/audio are required")
        cases.append(case)
    if not cases:
        raise ValueError("no cases")
    return cases


def transcribe(client, case: dict, timeout: float) -> tuple[str, float, int]:
    audio_path = ROOT / case["audio"]
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)
    started = time.perf_counter()
    with audio_path.open("rb") as audio:
        response = client.audio.transcriptions.create(
            model=os.environ["OPENAI_STT_MODEL"],
            file=audio,
            language=case.get("language", "ko"),
            response_format="json",
            timeout=timeout,
        )
    return response.text, round((time.perf_counter() - started) * 1000, 1), audio_path.stat().st_size


def score(case: dict, text: str) -> dict:
    missing = [value for value in case.get("must_include", []) if value not in text]
    forbidden = [value for value in case.get("forbidden", []) if value in text]
    return {"semantic_valid": not missing and not forbidden, "missing": missing, "forbidden_found": forbidden}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=float, default=None)
    args = parser.parse_args()
    load_env(ROOT / ".env")
    cases = load_cases(args.cases)
    for case in cases:
        if not (ROOT / case["audio"]).exists() and not args.dry_run:
            raise FileNotFoundError(ROOT / case["audio"])
    if args.dry_run:
        print(f"Validated {len(cases)} STT cases; no API call made.")
        return
    from openai import OpenAI

    if not os.getenv("OPENAI_STT_API_KEY"):
        raise RuntimeError("OPENAI_STT_API_KEY is required")
    client = OpenAI(base_url=os.getenv("OPENAI_STT_BASE_URL"), api_key=os.environ["OPENAI_STT_API_KEY"])
    timeout = args.timeout or float(os.getenv("STT_TIMEOUT_SECONDS", "120"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_path = ROOT / "results" / f"run-{stamp}.jsonl"
    summary_path = ROOT / "results" / f"summary-{stamp}.csv"
    metrics_path = ROOT / "results" / f"metrics-{stamp}.json"
    rows = []
    for case in cases:
        started = time.perf_counter()
        try:
            text, latency, size = transcribe(client, case, timeout)
            result = {"case_id": case["case_id"], **score(case, text), "provider_error": None, "latency_ms": latency, "audio_bytes": size, "text": text}
        except Exception as exc:  # retain one failed case and continue
            result = {"case_id": case["case_id"], "semantic_valid": False, "missing": [], "forbidden_found": [], "provider_error": str(exc), "latency_ms": round((time.perf_counter() - started) * 1000, 1)}
        rows.append(result)
    run_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    with summary_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=["case_id", "semantic_valid", "provider_error", "latency_ms"])
        writer.writeheader(); writer.writerows({key: row.get(key) for key in writer.fieldnames} for row in rows)
    valid = sum(row["semantic_valid"] for row in rows)
    metrics = {"generated_at": datetime.now(timezone.utc).isoformat(), "model": os.environ["OPENAI_STT_MODEL"], "case_count": len(rows), "semantic_valid_count": valid, "semantic_valid_rate": valid / len(rows), "provider_error_count": sum(bool(row["provider_error"]) for row in rows), "results": {"run": str(run_path), "summary": str(summary_path)}}
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
