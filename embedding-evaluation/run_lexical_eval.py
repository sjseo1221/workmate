from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

from run_eval import load_env, load_jsonl, percentile, validate_inputs
from run_postgres_eval import ROOT, connect_database, first_rank, query_trigram


def metrics(rows: list[dict], prefix: str) -> dict[str, float]:
    ranks = [row[f"{prefix}_rank"] for row in rows]
    return {
        "hit_at_1": sum(rank == 1 for rank in ranks) / len(rows),
        "hit_at_3": sum(rank is not None and rank <= 3 for rank in ranks) / len(rows),
        "hit_at_5": sum(rank is not None and rank <= 5 for rank in ranks) / len(rows),
        "mrr": statistics.mean(1 / rank if rank else 0 for rank in ranks),
        "p95_ms": percentile([row[f"{prefix}_ms"] for row in rows], 0.95),
    }


def main() -> None:
    corpus = load_jsonl(ROOT / "corpus" / "expanded_meeting_chunks.jsonl")
    cases = load_jsonl(ROOT / "cases" / "lexical_holdout_cases.jsonl")
    validate_inputs(corpus, cases)
    load_env(ROOT / ".env")
    connection = connect_database()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM embedding_eval_chunks")
            if cursor.fetchone()[0] != len(corpus):
                raise RuntimeError("DB 평가 Table이 1,000 Chunk 확장 Corpus와 일치하지 않습니다.")
        rows = []
        for case in cases:
            baseline, baseline_ms = query_trigram(connection, case["query"], case["filters"], 0.05, use_aliases=False)
            expanded, expanded_ms = query_trigram(connection, case["query"], case["filters"], 0.05, use_aliases=True)
            relevant = set(case["relevant_chunk_ids"])
            rows.append({
                "case_id": case["case_id"],
                "query": case["query"],
                "baseline_rank": first_rank(baseline, relevant),
                "expanded_rank": first_rank(expanded, relevant),
                "baseline_ms": baseline_ms,
                "expanded_ms": expanded_ms,
                "baseline_top_5": baseline[:5],
                "expanded_top_5": expanded[:5],
            })
    finally:
        connection.close()

    changed = {"improved": 0, "unchanged": 0, "worsened": 0}
    for row in rows:
        old = row["baseline_rank"] or float("inf")
        new = row["expanded_rank"] or float("inf")
        changed["improved" if new < old else "worsened" if new > old else "unchanged"] += 1
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "corpus_count": len(corpus),
        "case_count": len(cases),
        "baseline": metrics(rows, "baseline"),
        "alias_expanded": metrics(rows, "expanded"),
        "changes": changed,
    }
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    result_path = ROOT / "results" / f"lexical-run-{stamp}.jsonl"
    metrics_path = ROOT / "results" / f"lexical-metrics-{stamp}.json"
    result_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    metrics_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"상세 결과: {result_path}")
    print(f"전체 지표: {metrics_path}")


if __name__ == "__main__":
    main()
