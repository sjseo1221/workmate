from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            rows.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: 잘못된 JSON: {exc}") from exc
    return rows


def validate_inputs(corpus: list[dict[str, Any]], cases: list[dict[str, Any]]) -> None:
    chunk_ids = [row.get("meeting_chunk_id") for row in corpus]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("Corpus에 중복 meeting_chunk_id가 있습니다.")
    case_ids = [row.get("case_id") for row in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Case에 중복 case_id가 있습니다.")
    known = set(chunk_ids)
    for case in cases:
        required = set(case.get("relevant_chunk_ids", []))
        missing = required - known
        if missing:
            raise ValueError(f"{case['case_id']}: 존재하지 않는 정답 Chunk: {sorted(missing)}")
        if case.get("answerable", True) and not required:
            raise ValueError(f"{case['case_id']}: 답변 가능 Case에 정답 Chunk가 없습니다.")
        if not case.get("answerable", True) and required:
            raise ValueError(f"{case['case_id']}: 답변 불가 Case에 정답 Chunk가 있습니다.")


def request_embeddings(texts: list[str], base_url: str, api_key: str, model: str, timeout: int) -> tuple[list[list[float]], int, float]:
    payload = json.dumps({"model": model, "input": texts}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/embeddings",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    retries = int(os.getenv("PROVIDER_RETRIES", "1"))
    delay = float(os.getenv("PROVIDER_RETRY_DELAY_SECONDS", "2"))
    started = time.perf_counter()
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            data = sorted(body["data"], key=lambda item: item.get("index", 0))
            vectors = [item["embedding"] for item in data]
            if len(vectors) != len(texts):
                raise ValueError(f"요청 {len(texts)}건에 대해 Vector {len(vectors)}건이 반환됐습니다.")
            dimensions = {len(vector) for vector in vectors}
            if len(dimensions) != 1:
                raise ValueError(f"응답 Vector 차원이 일치하지 않습니다: {sorted(dimensions)}")
            latency_ms = round((time.perf_counter() - started) * 1000, 1)
            return vectors, int(body.get("usage", {}).get("total_tokens", 0)), latency_ms
        except urllib.error.HTTPError as exc:
            if exc.code not in {429, 502, 503, 504} or attempt == retries:
                raise RuntimeError(f"Embedding API HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == retries:
                raise RuntimeError(f"Embedding API 연결 실패: {exc}") from exc
        time.sleep(delay)
    raise RuntimeError("Embedding API 재시도 횟수를 초과했습니다.")


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


def matches_filters(document: dict[str, Any], filters: dict[str, Any]) -> bool:
    meeting_ids = set(filters.get("meeting_ids", []))
    if meeting_ids and document.get("meeting_id") not in meeting_ids:
        return False
    participants = set(filters.get("participant_user_ids", []))
    if participants and not participants.intersection(document.get("participant_user_ids", [])):
        return False
    date = document.get("meeting_date", "")
    if filters.get("date_from") and date < filters["date_from"]:
        return False
    if filters.get("date_to") and date >= filters["date_to"]:
        return False
    return True


def rank_documents(query_vector: list[float], corpus: list[dict[str, Any]], document_vectors: list[list[float]], filters: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = [
        {"meeting_chunk_id": document["meeting_chunk_id"], "score": cosine_similarity(query_vector, vector)}
        for document, vector in zip(corpus, document_vectors)
        if matches_filters(document, filters)
    ]
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def percentile(values: list[float], ratio: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[max(0, math.ceil(len(ordered) * ratio) - 1)]


def score_case(case: dict[str, Any], ranked: list[dict[str, Any]], latency_ms: float) -> dict[str, Any]:
    relevant = set(case.get("relevant_chunk_ids", []))
    ranked_ids = [item["meeting_chunk_id"] for item in ranked]
    ranks = [index + 1 for index, chunk_id in enumerate(ranked_ids) if chunk_id in relevant]
    first_rank = min(ranks) if ranks else None
    ideal_dcg = sum(1 / math.log2(index + 2) for index in range(min(len(relevant), 10))) or 1
    dcg = sum(1 / math.log2(rank + 1) for rank in ranks if rank <= 10)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "case_id": case["case_id"],
        "category": case["category"],
        "answerable": case.get("answerable", True),
        "first_relevant_rank": first_rank,
        "hit_at_1": bool(first_rank and first_rank <= 1),
        "hit_at_3": bool(first_rank and first_rank <= 3),
        "hit_at_5": bool(first_rank and first_rank <= 5),
        "recall_at_5": len(relevant.intersection(ranked_ids[:5])) / len(relevant) if relevant else None,
        "reciprocal_rank": 1 / first_rank if first_rank else 0.0,
        "ndcg_at_10": dcg / ideal_dcg,
        "query_latency_ms": latency_ms,
        "top_5": ranked[:5],
    }


def write_results(results: list[dict[str, Any]], summary: dict[str, Any]) -> tuple[Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    jsonl_path = results_dir / f"run-{stamp}.jsonl"
    csv_path = results_dir / f"summary-{stamp}.csv"
    jsonl_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in results), encoding="utf-8")
    fields = ["repeat_no", "case_id", "category", "answerable", "first_relevant_rank", "hit_at_1", "hit_at_3", "hit_at_5", "recall_at_5", "reciprocal_rank", "ndcg_at_10", "query_latency_ms"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({name: row.get(name) for name in fields} for row in results)
    summary_path = results_dir / f"metrics-{stamp}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return jsonl_path, csv_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Workmate Embedding 모델 평가 실행기")
    parser.add_argument("--corpus", type=Path, default=ROOT / "corpus" / "pilot_meeting_chunks.jsonl")
    parser.add_argument("--cases", type=Path, default=ROOT / "cases" / "pilot_cases.jsonl")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_env(ROOT / ".env")
    corpus = load_jsonl(args.corpus)
    cases = load_jsonl(args.cases)
    validate_inputs(corpus, cases)
    print(f"Corpus {len(corpus)}개와 Case {len(cases)}개 검증 완료")
    if args.dry_run:
        return

    base_url = os.getenv("EMBEDDING_BASE_URL", "")
    api_key = os.getenv("EMBEDDING_API_KEY", "")
    model = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
    if not base_url or not api_key:
        raise RuntimeError("EMBEDDING_BASE_URL과 EMBEDDING_API_KEY를 설정하세요.")

    document_vectors, document_tokens, document_latency = request_embeddings(
        [document["content"] for document in corpus], base_url, api_key, model, args.timeout
    )
    dimensions = len(document_vectors[0])
    results = []
    query_tokens = 0
    for repeat_no in range(1, args.repeat + 1):
        for index, case in enumerate(cases, 1):
            print(f"[{repeat_no}/{args.repeat}] [{index}/{len(cases)}] {case['case_id']}")
            vectors, tokens, latency = request_embeddings([case["query"]], base_url, api_key, model, args.timeout)
            query_tokens += tokens
            ranked = rank_documents(vectors[0], corpus, document_vectors, case.get("filters", {}))
            result = score_case(case, ranked, latency)
            result["repeat_no"] = repeat_no
            results.append(result)

    answerable = [row for row in results if row["answerable"]]
    latencies = [row["query_latency_ms"] for row in results]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "dimension": dimensions,
        "corpus_count": len(corpus),
        "case_count": len(cases),
        "repeat": args.repeat,
        "result_count": len(results),
        "hit_at_1": sum(row["hit_at_1"] for row in answerable) / len(answerable),
        "hit_at_3": sum(row["hit_at_3"] for row in answerable) / len(answerable),
        "hit_at_5": sum(row["hit_at_5"] for row in answerable) / len(answerable),
        "mean_reciprocal_rank": statistics.mean(row["reciprocal_rank"] for row in answerable),
        "mean_ndcg_at_10": statistics.mean(row["ndcg_at_10"] for row in answerable),
        "query_latency_p50_ms": percentile(latencies, 0.50),
        "query_latency_p95_ms": percentile(latencies, 0.95),
        "document_batch_latency_ms": document_latency,
        "document_tokens": document_tokens,
        "query_tokens": query_tokens,
    }
    jsonl_path, csv_path = write_results(results, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"원본 결과: {jsonl_path}")
    print(f"요약 결과: {csv_path}")


if __name__ == "__main__":
    main()
