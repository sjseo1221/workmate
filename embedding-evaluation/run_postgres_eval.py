from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import psycopg2
except ModuleNotFoundError:  # pragma: no cover - 실행 환경 안내용
    psycopg2 = None

from run_eval import load_env, load_jsonl, percentile, request_embeddings, validate_inputs


ROOT = Path(__file__).resolve().parent
TABLE = "embedding_eval_chunks"
TERM_ALIASES = {
    "low end": "저사양",
    "low spec": "저사양",
    "entry level": "저사양",
    "device": "기기",
    "shadow quality": "그림자 품질",
    "matchmaking": "매치메이킹",
    "match server": "매치메이킹 서버",
    "backend": "서버",
    "staged rollout": "점진 배포",
    "canary rollout": "점진 배포",
    "rollout": "점진 배포",
    "frame pacing": "프레임 페이싱",
    "budget": "예산",
    "emergency patch": "긴급 패치",
    "hotfix": "긴급 패치",
    "asset bundle": "리소스 번들",
    "resource bundle": "리소스 번들",
    "inactive player": "장기 미접속 사용자",
    "mmr decay": "mmr 감소",
    "shader cache": "셰이더 캐시",
    "prewarm": "사전 준비",
    "warmup": "사전 준비",
    "cache invalidation": "캐시 삭제",
    "cdn purge": "cdn 캐시 삭제",
    "analytics collection": "텔레메트리 수집",
    "telemetry": "텔레메트리",
    "opt out": "수집 거부",
    "save file": "저장 파일",
    "save data": "세이브 데이터",
    "voice chat": "음성 채팅",
    "noise suppression": "잡음 제거",
    "denoiser": "잡음 제거",
}


def normalize_keyword_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w]+", " ", value.lower())).strip()


def expand_query_terms(value: str) -> str:
    expanded = normalize_keyword_text(value)
    for source, target in sorted(TERM_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        expanded = expanded.replace(source, target)
    return normalize_keyword_text(expanded)


def vector_text(vector: list[float]) -> str:
    return "[" + ",".join(format(value, ".9g") for value in vector) + "]"


def connect_database():
    if psycopg2 is None:
        raise RuntimeError("pip install -r requirements.txt를 먼저 실행하세요.")
    password = os.getenv("POSTGRES_PASSWORD", "")
    if not password:
        raise RuntimeError("POSTGRES_PASSWORD를 .env 또는 현재 환경변수에 설정하세요.")
    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "workmate"),
        user=os.getenv("POSTGRES_USER", "workmate"),
        password=password,
        connect_timeout=5,
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("SET jit = off")
    return connection


def database_metadata(connection) -> dict[str, str]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_setting('server_version'), "
            "(SELECT extversion FROM pg_extension WHERE extname = 'vector'), "
            "(SELECT extversion FROM pg_extension WHERE extname = 'pg_trgm')"
        )
        postgres, pgvector, pg_trgm = cursor.fetchone()
    return {"postgres": postgres, "pgvector": pgvector, "pg_trgm": pg_trgm}


def normalize_corpus_rows(corpus: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """기존 평가 필드와 실제 회의록 필드를 같은 검색 입력으로 변환한다."""
    normalized = []
    for row in corpus:
        item = dict(row)
        item.setdefault("meeting_chunk_id", item.pop("chunk_id", None))
        item.setdefault("meeting_title", item.pop("title", None))
        item.setdefault("meeting_date", item.pop("created_at", None))
        item.setdefault("participant_user_ids", item.pop("participants", []))
        required = {"meeting_chunk_id", "meeting_id", "meeting_title", "meeting_date", "content"}
        missing = sorted(name for name in required if not item.get(name))
        if missing:
            raise ValueError(f"Corpus 필드 누락: {missing}")
        normalized.append(item)
    return normalized


def initialize_table(connection, corpus: list[dict[str, Any]], vectors: list[list[float]]) -> None:
    migration = (ROOT / "sql" / "001_pgvector_eval.sql").read_text(encoding="utf-8")
    values = [
        (
            document["meeting_chunk_id"],
            document["meeting_id"],
            document["meeting_title"],
            document["meeting_date"],
            document.get("participant_user_ids", []),
            document["content"],
            normalize_keyword_text(f"{document['meeting_title']} {document['content']}"),
            vector_text(vector),
        )
        for document, vector in zip(corpus, vectors)
    ]
    with connection.cursor() as cursor:
        cursor.execute(migration)
        cursor.executemany(
            f"INSERT INTO {TABLE} "
            "(meeting_chunk_id, meeting_id, meeting_title, meeting_date, participant_user_ids, content, search_text, embedding) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector)",
            values,
        )
        cursor.execute(
            f"CREATE INDEX embedding_eval_chunks_hnsw_idx ON {TABLE} "
            "USING hnsw (embedding vector_cosine_ops)"
        )
        cursor.execute(f"ANALYZE {TABLE}")


def filter_clause(filters: dict[str, Any]) -> tuple[str, list[Any]]:
    conditions: list[str] = []
    params: list[Any] = []
    if filters.get("meeting_ids"):
        conditions.append("meeting_id = ANY(%s)")
        params.append(filters["meeting_ids"])
    if filters.get("participant_user_ids"):
        conditions.append("participant_user_ids && %s::text[]")
        params.append(filters["participant_user_ids"])
    if filters.get("date_from"):
        conditions.append("meeting_date >= %s::date")
        params.append(filters["date_from"])
    if filters.get("date_to"):
        conditions.append("meeting_date < %s::date")
        params.append(filters["date_to"])
    return (" WHERE " + " AND ".join(conditions) if conditions else ""), params


def set_scan_mode(connection, mode: str) -> None:
    settings = {
        "exact": "SET enable_seqscan=on; SET enable_indexscan=off; SET enable_bitmapscan=off",
        "index": "SET enable_seqscan=off; SET enable_indexscan=on; SET enable_bitmapscan=on",
    }
    with connection.cursor() as cursor:
        cursor.execute(settings[mode])


def configure_hnsw(connection, ef_search: int) -> None:
    if ef_search < 1:
        raise ValueError("hnsw ef_search는 1 이상이어야 합니다.")
    with connection.cursor() as cursor:
        cursor.execute(f"SET hnsw.ef_search = {ef_search}")
        cursor.execute("SET hnsw.iterative_scan = strict_order")


def execute_ranked(connection, sql: str, params: list[Any]) -> tuple[list[dict[str, Any]], float]:
    started = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    return [{"meeting_chunk_id": chunk_id, "score": float(score)} for chunk_id, score in rows], elapsed_ms


def query_vector(connection, vector: list[float], filters: dict[str, Any], use_hnsw: bool) -> tuple[list[dict[str, Any]], float]:
    set_scan_mode(connection, "index" if use_hnsw else "exact")
    where, filter_params = filter_clause(filters)
    value = vector_text(vector)
    sql = (
        f"SELECT meeting_chunk_id, 1 - (embedding <=> %s::vector) AS score FROM {TABLE}{where} "
        "ORDER BY embedding <=> %s::vector LIMIT 20"
    )
    return execute_ranked(connection, sql, [value, *filter_params, value])


def query_fts(connection, query: str, filters: dict[str, Any]) -> tuple[list[dict[str, Any]], float]:
    set_scan_mode(connection, "index")
    where, filter_params = filter_clause(filters)
    extra = " AND " if where else " WHERE "
    sql = (
        f"SELECT meeting_chunk_id, ts_rank_cd(content_tsv, plainto_tsquery('simple', %s)) AS score "
        f"FROM {TABLE}{where}{extra}content_tsv @@ plainto_tsquery('simple', %s) "
        "ORDER BY score DESC, meeting_chunk_id LIMIT 20"
    )
    return execute_ranked(connection, sql, [query, *filter_params, query])


def query_trigram_text(connection, query: str, filters: dict[str, Any], min_score: float) -> tuple[list[dict[str, Any]], float]:
    set_scan_mode(connection, "index")
    where, filter_params = filter_clause(filters)
    sql = (
        "WITH candidates AS ("
        f"SELECT meeting_chunk_id, similarity(search_text, %s) AS score FROM {TABLE}{where} "
        "ORDER BY search_text <-> %s LIMIT 20"
        ") SELECT meeting_chunk_id, score FROM candidates WHERE score >= %s "
        "ORDER BY score DESC, meeting_chunk_id"
    )
    return execute_ranked(connection, sql, [query, *filter_params, query, min_score])


def query_trigram(
    connection, query: str, filters: dict[str, Any], min_score: float, use_aliases: bool = False
) -> tuple[list[dict[str, Any]], float]:
    normalized = normalize_keyword_text(query)
    baseline, baseline_ms = query_trigram_text(connection, normalized, filters, min_score)
    expanded = expand_query_terms(query)
    if not use_aliases or expanded == normalized:
        return baseline, baseline_ms
    alias_rows, alias_ms = query_trigram_text(connection, expanded, filters, min_score)
    seen = {row["meeting_chunk_id"] for row in baseline}
    ranked = (baseline + [row for row in alias_rows if row["meeting_chunk_id"] not in seen])[:20]
    return ranked, round(baseline_ms + alias_ms, 3)


def rrf_rank(vector_rows: list[dict[str, Any]], keyword_rows: list[dict[str, Any]], constant: int = 60) -> list[dict[str, Any]]:
    scores: dict[str, float] = {}
    vector_ranks = {row["meeting_chunk_id"]: rank for rank, row in enumerate(vector_rows, 1)}
    for rows in (vector_rows, keyword_rows):
        for rank, row in enumerate(rows, 1):
            chunk_id = row["meeting_chunk_id"]
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (constant + rank)
    return [
        {"meeting_chunk_id": chunk_id, "score": score}
        for chunk_id, score in sorted(
            scores.items(),
            key=lambda item: (-item[1], vector_ranks.get(item[0], math.inf), item[0]),
        )
    ]


def first_rank(ranked: list[dict[str, Any]], relevant: set[str]) -> int | None:
    return next((rank for rank, row in enumerate(ranked, 1) if row["meeting_chunk_id"] in relevant), None)


def ndcg_at_10(ranked: list[dict[str, Any]], relevant: set[str]) -> float:
    ideal = sum(1 / math.log2(index + 2) for index in range(min(len(relevant), 10))) or 1
    actual = sum(
        1 / math.log2(index + 2)
        for index, row in enumerate(ranked[:10])
        if row["meeting_chunk_id"] in relevant
    )
    return actual / ideal


def mode_metrics(rows: list[dict[str, Any]], prefix: str) -> dict[str, float]:
    evaluated = [row for row in rows if row.get("answerable", True)]
    ranks = [row[f"{prefix}_rank"] for row in evaluated]
    return {
        "hit_at_1": sum(rank is not None and rank <= 1 for rank in ranks) / len(evaluated),
        "hit_at_3": sum(rank is not None and rank <= 3 for rank in ranks) / len(evaluated),
        "hit_at_5": sum(rank is not None and rank <= 5 for rank in ranks) / len(evaluated),
        "mrr": statistics.mean(1 / rank if rank else 0 for rank in ranks),
        "mean_ndcg_at_10": statistics.mean(row[f"{prefix}_ndcg_at_10"] for row in evaluated),
        "zero_result_rate": sum(not row[f"{prefix}_top_5"] for row in evaluated) / len(evaluated),
    }


def latency_metrics(rows: list[dict[str, Any]], field: str) -> dict[str, float]:
    values = [row[field] for row in rows]
    return {"p50_ms": percentile(values, 0.50), "p95_ms": percentile(values, 0.95)}


def rank_changes(rows: list[dict[str, Any]], baseline: str, candidate: str) -> dict[str, int]:
    changes = {"improved": 0, "unchanged": 0, "worsened": 0}
    for row in (row for row in rows if row.get("answerable", True)):
        old_rank = row[f"{baseline}_rank"] if row[f"{baseline}_rank"] is not None else math.inf
        new_rank = row[f"{candidate}_rank"] if row[f"{candidate}_rank"] is not None else math.inf
        changes["improved" if new_rank < old_rank else "worsened" if new_rank > old_rank else "unchanged"] += 1
    return changes


def category_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for category in sorted({row["category"] for row in rows}):
        subset = [row for row in rows if row["category"] == category]
        answerable = [row for row in subset if row.get("answerable", True)]
        result[category] = {"case_count": len(subset), "answerable_count": len(answerable)}
        if answerable:
            result[category].update({
                "hnsw": mode_metrics(answerable, "hnsw"),
                "trigram": mode_metrics(answerable, "trigram"),
                "rrf_exact": mode_metrics(answerable, "rrf_exact"),
                "rrf": mode_metrics(answerable, "rrf"),
            })
    return result


def answerability_metrics(rows: list[dict[str, Any]], threshold: float) -> dict[str, float | int]:
    answerable = [row for row in rows if row.get("answerable", True)]
    unanswerable = [row for row in rows if not row.get("answerable", True)]
    false_negative = sum(row["top_dense_score"] < threshold for row in answerable)
    false_positive = sum(row["top_dense_score"] >= threshold for row in unanswerable)
    return {
        "threshold": threshold,
        "answerable_count": len(answerable),
        "unanswerable_count": len(unanswerable),
        "false_negative_count": false_negative,
        "false_positive_count": false_positive,
        "false_negative_rate": false_negative / len(answerable) if answerable else 0.0,
        "false_positive_rate": false_positive / len(unanswerable) if unanswerable else 0.0,
        "accuracy": (len(rows) - false_negative - false_positive) / len(rows),
    }


def request_embeddings_batched(
    texts: list[str], base_url: str, api_key: str, model: str, timeout: int, batch_size: int
) -> tuple[list[list[float]], int, float]:
    vectors: list[list[float]] = []
    total_tokens = 0
    total_ms = 0.0
    for start in range(0, len(texts), batch_size):
        batch_vectors, tokens, latency_ms = request_embeddings(
            texts[start:start + batch_size], base_url, api_key, model, timeout
        )
        vectors.extend(batch_vectors)
        total_tokens += tokens
        total_ms += latency_ms
    return vectors, total_tokens, round(total_ms, 1)


def hnsw_index_used(connection, vector: list[float]) -> bool:
    set_scan_mode(connection, "index")
    with connection.cursor() as cursor:
        cursor.execute(
            f"EXPLAIN SELECT meeting_chunk_id FROM {TABLE} ORDER BY embedding <=> %s::vector LIMIT 5",
            [vector_text(vector)],
        )
        plan = "\n".join(row[0] for row in cursor.fetchall())
    return "embedding_eval_chunks_hnsw_idx" in plan


def write_results(rows: list[dict[str, Any]], metrics: dict[str, Any]) -> tuple[Path, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results = ROOT / "results"
    jsonl_path = results / f"postgres-run-{stamp}.jsonl"
    csv_path = results / f"postgres-summary-{stamp}.csv"
    metrics_path = results / f"postgres-metrics-{stamp}.json"
    jsonl_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    fields = [
        "case_id", "category", "answerable", "predicted_answerable", "top_dense_score", "top_hnsw_score",
        "dense_rank", "fts_rank", "trigram_rank", "rrf_exact_rank", "rrf_rank", "hnsw_rank",
        "hnsw_recall_at_5", "query_embedding_ms", "dense_ms", "fts_ms", "trigram_ms", "hnsw_ms", "hybrid_ms",
        "hybrid_exact_ms",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return jsonl_path, csv_path, metrics_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Workmate PostgreSQL+pgvector 검색 평가")
    parser.add_argument("--corpus", type=Path, default=ROOT / "corpus" / "pilot_meeting_chunks.jsonl")
    parser.add_argument("--cases", type=Path, default=ROOT / "cases" / "pilot_cases.jsonl")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--trigram-min-score", type=float, default=0.05)
    parser.add_argument("--db-warmup", type=int, default=10)
    parser.add_argument("--abstain-score", type=float, default=0.45)
    parser.add_argument("--embedding-batch-size", type=int, default=100)
    parser.add_argument("--hnsw-ef-search", type=int, default=200)
    args = parser.parse_args()

    load_env(ROOT / ".env")
    corpus = normalize_corpus_rows(load_jsonl(args.corpus))
    cases = load_jsonl(args.cases)
    validate_inputs(corpus, cases)
    base_url = os.getenv("EMBEDDING_BASE_URL", "")
    api_key = os.getenv("EMBEDDING_API_KEY", "")
    model = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
    if not base_url or not api_key:
        raise RuntimeError("EMBEDDING_BASE_URL과 EMBEDDING_API_KEY를 설정하세요.")

    document_vectors, document_tokens, document_embedding_ms = request_embeddings_batched(
        [document["content"] for document in corpus], base_url, api_key, model, args.timeout,
        args.embedding_batch_size,
    )
    connection = connect_database()
    try:
        configure_hnsw(connection, args.hnsw_ef_search)
        initialize_table(connection, corpus, document_vectors)
        db_metadata = database_metadata(connection)

        # 지속 연결과 인덱스 페이지를 준비하되 측정값에는 포함하지 않는다.
        for warmup_index in range(args.db_warmup):
            vector = document_vectors[warmup_index % len(document_vectors)]
            query = cases[warmup_index % len(cases)]["query"]
            query_vector(connection, vector, {}, use_hnsw=False)
            query_fts(connection, query, {})
            query_trigram(connection, query, {}, args.trigram_min_score)
            query_vector(connection, vector, {}, use_hnsw=True)

        rows = []
        query_tokens = 0
        for index, case in enumerate(cases, 1):
            print(f"[{index}/{len(cases)}] {case['case_id']}")
            query_vectors, tokens, query_embedding_ms = request_embeddings(
                [case["query"]], base_url, api_key, model, args.timeout
            )
            query_tokens += tokens
            vector = query_vectors[0]
            filters = case.get("filters", {})
            dense, dense_ms = query_vector(connection, vector, filters, use_hnsw=False)
            fts, fts_ms = query_fts(connection, case["query"], filters)
            trigram, trigram_ms = query_trigram(connection, case["query"], filters, args.trigram_min_score)
            hnsw, hnsw_ms = query_vector(connection, vector, filters, use_hnsw=True)
            fusion_started = time.perf_counter()
            hybrid = rrf_rank(hnsw, trigram)
            fusion_ms = round((time.perf_counter() - fusion_started) * 1000, 3)
            exact_fusion_started = time.perf_counter()
            exact_hybrid = rrf_rank(dense, trigram)
            exact_fusion_ms = round((time.perf_counter() - exact_fusion_started) * 1000, 3)
            relevant = set(case["relevant_chunk_ids"])
            exact_top5 = {row["meeting_chunk_id"] for row in dense[:5]}
            hnsw_top5 = {row["meeting_chunk_id"] for row in hnsw[:5]}
            row = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "case_id": case["case_id"],
                "category": case["category"],
                "answerable": case.get("answerable", True),
                "top_dense_score": dense[0]["score"] if dense else -1.0,
                "top_hnsw_score": hnsw[0]["score"] if hnsw else -1.0,
                "hnsw_recall_at_5": len(exact_top5 & hnsw_top5) / len(exact_top5) if exact_top5 else 1.0,
                "query_embedding_ms": query_embedding_ms,
                "dense_ms": dense_ms,
                "fts_ms": fts_ms,
                "trigram_ms": trigram_ms,
                "hnsw_ms": hnsw_ms,
                "hybrid_ms": round(trigram_ms + hnsw_ms + fusion_ms, 3),
                "hybrid_exact_ms": round(trigram_ms + dense_ms + exact_fusion_ms, 3),
            }
            row["predicted_answerable"] = row["top_dense_score"] >= args.abstain_score
            for name, ranked in (
                ("dense", dense), ("fts", fts), ("trigram", trigram),
                ("rrf_exact", exact_hybrid), ("rrf", hybrid), ("hnsw", hnsw),
            ):
                row[f"{name}_rank"] = first_rank(ranked, relevant)
                row[f"{name}_ndcg_at_10"] = ndcg_at_10(ranked, relevant)
                row[f"{name}_top_5"] = ranked[:5]
            rows.append(row)

        metrics = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "dimension": len(document_vectors[0]),
            **db_metadata,
            "corpus_count": len(corpus),
            "case_count": len(cases),
            "trigram_min_score": args.trigram_min_score,
            "db_warmup_queries": args.db_warmup,
            "abstain_score": args.abstain_score,
            "embedding_batch_size": args.embedding_batch_size,
            "hnsw_ef_search": args.hnsw_ef_search,
            "hnsw_iterative_scan": "strict_order",
            "dense_exact": mode_metrics(rows, "dense"),
            "fts_simple": mode_metrics(rows, "fts"),
            "trigram": mode_metrics(rows, "trigram"),
            "rrf_exact_trigram": mode_metrics(rows, "rrf_exact"),
            "rrf_hnsw_trigram": mode_metrics(rows, "rrf"),
            "hnsw": mode_metrics(rows, "hnsw"),
            "rrf_exact_vs_dense": rank_changes(rows, "dense", "rrf_exact"),
            "rrf_vs_hnsw": rank_changes(rows, "hnsw", "rrf"),
            "answerability": answerability_metrics(rows, args.abstain_score),
            "answerability_threshold_sweep": [
                answerability_metrics(rows, threshold)
                for threshold in (0.35, 0.40, 0.45, 0.50, 0.55, 0.60)
            ],
            "by_category": category_metrics(rows),
            "mean_hnsw_recall_at_5": statistics.mean(
                row["hnsw_recall_at_5"] for row in rows if row.get("answerable", True)
            ),
            "latency": {
                "query_embedding": latency_metrics(rows, "query_embedding_ms"),
                "dense_exact_db": latency_metrics(rows, "dense_ms"),
                "fts_db": latency_metrics(rows, "fts_ms"),
                "trigram_db": latency_metrics(rows, "trigram_ms"),
                "hnsw_db": latency_metrics(rows, "hnsw_ms"),
                "hybrid_sequential_db": latency_metrics(rows, "hybrid_ms"),
                "hybrid_exact_sequential_db": latency_metrics(rows, "hybrid_exact_ms"),
            },
            "hnsw_index_used": hnsw_index_used(connection, document_vectors[0]),
            "document_embedding_ms": document_embedding_ms,
            "document_tokens": document_tokens,
            "query_tokens": query_tokens,
        }
    finally:
        connection.close()

    jsonl_path, csv_path, metrics_path = write_results(rows, metrics)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"상세 결과: {jsonl_path}")
    print(f"요약 결과: {csv_path}")
    print(f"전체 지표: {metrics_path}")


if __name__ == "__main__":
    main()
