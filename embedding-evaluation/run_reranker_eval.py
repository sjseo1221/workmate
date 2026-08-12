from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_eval import load_env, load_jsonl, percentile


ROOT = Path(__file__).resolve().parent
LLM_ROOT = ROOT.parent / "llm-evaluation"
RERANK_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["answerable", "ranked_chunk_ids"],
    "properties": {
        "answerable": {"type": "boolean"},
        "ranked_chunk_ids": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 5,
        },
    },
}


def load_llm_runner():
    spec = importlib.util.spec_from_file_location("workmate_llm_eval", LLM_ROOT / "run_eval.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("LLM 평가기를 불러올 수 없습니다.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_decision(result: dict[str, Any], candidate_ids: list[str]) -> list[str]:
    errors = []
    if set(result) != {"answerable", "ranked_chunk_ids"}:
        errors.append("answerable과 ranked_chunk_ids만 반환해야 합니다.")
    if not isinstance(result.get("answerable"), bool):
        errors.append("answerable은 boolean이어야 합니다.")
    ranked = result.get("ranked_chunk_ids")
    if not isinstance(ranked, list) or any(not isinstance(item, str) for item in ranked):
        return [*errors, "ranked_chunk_ids는 문자열 배열이어야 합니다."]
    if len(ranked) != len(set(ranked)):
        errors.append("ranked_chunk_ids에 중복이 있습니다.")
    unknown = set(ranked) - set(candidate_ids)
    if unknown:
        errors.append(f"후보에 없는 ID가 있습니다: {sorted(unknown)}")
    if result.get("answerable") and not ranked:
        errors.append("답변 가능이면 최소 한 개의 Chunk를 선택해야 합니다.")
    if result.get("answerable") is False and ranked:
        errors.append("답변 불가이면 ranked_chunk_ids는 비어 있어야 합니다.")
    return errors


def first_relevant_rank(ranked_ids: list[str], relevant_ids: set[str]) -> int | None:
    return next((rank for rank, chunk_id in enumerate(ranked_ids, 1) if chunk_id in relevant_ids), None)


def ranking_metrics(rows: list[dict[str, Any]], rank_field: str) -> dict[str, float | int]:
    answerable = [row for row in rows if row["answerable"]]
    ranks = [row[rank_field] for row in answerable]
    return {
        "case_count": len(answerable),
        "hit_at_1": sum(rank is not None and rank <= 1 for rank in ranks) / len(ranks),
        "hit_at_3": sum(rank is not None and rank <= 3 for rank in ranks) / len(ranks),
        "hit_at_5": sum(rank is not None and rank <= 5 for rank in ranks) / len(ranks),
        "mrr": statistics.mean(1 / rank if rank else 0 for rank in ranks),
    }


def answerability_metrics(
    rows: list[dict[str, Any]], *, exclude_retrieval_misses: bool = False
) -> dict[str, float | int]:
    evaluated = [row for row in rows if not row.get("provider_error")]
    if exclude_retrieval_misses:
        evaluated = [row for row in evaluated if not row["answerable"] or row["candidate_has_relevant"]]
    answerable = [row for row in evaluated if row["answerable"]]
    unanswerable = [row for row in evaluated if not row["answerable"]]
    false_negative = sum(not row["predicted_answerable"] for row in answerable)
    false_positive = sum(row["predicted_answerable"] for row in unanswerable)
    return {
        "case_count": len(evaluated),
        "answerable_count": len(answerable),
        "unanswerable_count": len(unanswerable),
        "false_negative_count": false_negative,
        "false_negative_rate": false_negative / len(answerable) if answerable else 0.0,
        "false_positive_count": false_positive,
        "false_positive_rate": false_positive / len(unanswerable) if unanswerable else 0.0,
        "accuracy": (len(evaluated) - false_negative - false_positive) / len(evaluated) if evaluated else 0.0,
    }


def rank_changes(rows: list[dict[str, Any]]) -> dict[str, int]:
    changes = {"improved": 0, "unchanged": 0, "worsened": 0, "retrieval_miss": 0}
    for row in (row for row in rows if row["answerable"]):
        if not row["candidate_has_relevant"]:
            changes["retrieval_miss"] += 1
            continue
        old = row["baseline_rank"] or 999
        new = row["reranker_rank"] or 999
        changes["improved" if new < old else "worsened" if new > old else "unchanged"] += 1
    return changes


def build_eval_cases(
    corpus: list[dict[str, Any]],
    expanded_cases: list[dict[str, Any]],
    expanded_results: list[dict[str, Any]],
    lexical_cases: list[dict[str, Any]],
    lexical_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    documents = {}
    for source in corpus:
        row = dict(source)
        row.setdefault("meeting_chunk_id", row.pop("chunk_id", None))
        row.setdefault("meeting_title", row.pop("title", None))
        row.setdefault("meeting_date", row.pop("created_at", None))
        row.setdefault("participant_user_ids", row.pop("participants", []))
        documents[row["meeting_chunk_id"]] = row
    expanded_by_id = {row["case_id"]: row for row in expanded_results}
    lexical_by_id = {row["case_id"]: row for row in lexical_results}
    prepared = []
    for suite, cases, results, candidate_field, rank_field in (
        ("expanded", expanded_cases, expanded_by_id, "rrf_exact_top_5", "rrf_exact_rank"),
        ("lexical_holdout", lexical_cases, lexical_by_id, "expanded_top_5", "expanded_rank"),
    ):
        for case in cases:
            result = results.get(case["case_id"])
            if result is None:
                raise ValueError(f"{case['case_id']}: 저장된 검색 결과가 없습니다.")
            candidate_rows = result[candidate_field]
            candidate_ids = [row["meeting_chunk_id"] for row in candidate_rows]
            missing = set(candidate_ids) - set(documents)
            if missing:
                raise ValueError(f"{case['case_id']}: Corpus에 없는 후보: {sorted(missing)}")
            prepared.append({
                **case,
                "suite": suite,
                "baseline_rank": result.get(rank_field),
                "candidate_ids": candidate_ids,
                "candidates": [
                    {
                        "meeting_chunk_id": chunk_id,
                        "meeting_id": documents[chunk_id]["meeting_id"],
                        "meeting_title": documents[chunk_id]["meeting_title"],
                        "meeting_date": documents[chunk_id]["meeting_date"],
                        "participant_user_ids": documents[chunk_id].get("participant_user_ids", []),
                        "content": documents[chunk_id]["content"],
                    }
                    for chunk_id in candidate_ids
                ],
            })
    return prepared


def build_single_eval_cases(
    corpus: list[dict[str, Any]], cases: list[dict[str, Any]], results: list[dict[str, Any]],
    candidate_field: str, rank_field: str, suite: str,
) -> list[dict[str, Any]]:
    return _build_case_set(
        corpus, cases, {row["case_id"]: row for row in results}, candidate_field, rank_field, suite,
    )


def _build_case_set(
    corpus: list[dict[str, Any]], cases: list[dict[str, Any]], results: dict[str, dict[str, Any]],
    candidate_field: str, rank_field: str, suite: str,
) -> list[dict[str, Any]]:
    documents = {}
    for source in corpus:
        row = dict(source)
        row.setdefault("meeting_chunk_id", row.pop("chunk_id", None))
        row.setdefault("meeting_title", row.pop("title", None))
        row.setdefault("meeting_date", row.pop("created_at", None))
        row.setdefault("participant_user_ids", row.pop("participants", []))
        documents[row["meeting_chunk_id"]] = row
    prepared = []
    for case in cases:
        result = results.get(case["case_id"])
        if result is None:
            raise ValueError(f"{case['case_id']}: 저장된 검색 결과가 없습니다.")
        candidate_rows = result[candidate_field]
        candidate_ids = [row["meeting_chunk_id"] for row in candidate_rows]
        missing = set(candidate_ids) - set(documents)
        if missing:
            raise ValueError(f"{case['case_id']}: Corpus에 없는 후보: {sorted(missing)}")
        prepared.append({
            **case,
            "suite": suite,
            "baseline_rank": result.get(rank_field),
            "candidate_ids": candidate_ids,
            "candidates": [
                {
                    "meeting_chunk_id": chunk_id,
                    "meeting_id": documents[chunk_id]["meeting_id"],
                    "meeting_title": documents[chunk_id]["meeting_title"],
                    "meeting_date": documents[chunk_id]["meeting_date"],
                    "participant_user_ids": documents[chunk_id].get("participant_user_ids", []),
                    "content": documents[chunk_id]["content"],
                }
                for chunk_id in candidate_ids
            ],
        })
    return prepared


def evaluate_case(case: dict[str, Any], llm_runner: Any, timeout: int) -> dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": (
                "당신은 회의록 검색 후보 재정렬기다. 질문의 답을 후보 원문이 명시적으로 뒷받침할 때만 "
                "answerable=true로 판단한다. 여러 후보가 질문의 서로 다른 부분을 함께 뒷받침해도 답변 가능이다. "
                "후속 업무 질문에는 담당자·기한·행동이 명시된 실행 문장을 직접 근거로 인정한다. 추론하거나 "
                "후보에 없는 사실을 만들지 않는다. 질문이 원문의 의미를 자연스럽게 바꿔 표현한 경우 핵심 대상·시점·행동이 "
                "일치하면 답변 가능으로 인정한다. meeting_date와 participant_user_ids 같은 후보 메타데이터는 회의 일자·참여자 "
                "질문을 판단하는 근거로 사용한다. 입력의 filters는 검색 단계에서 적용된 제약조건이므로 후보의 메타데이터와 함께 확인한다. "
                "답변 가능하면 직접적인 근거 순서로 후보 ID를 정렬하고, "
                "답변 불가이면 빈 배열을 반환한다."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {"query": case["query"], "filters": case.get("filters", {}), "candidates": case["candidates"]},
                ensure_ascii=False,
            ),
        },
    ]
    attempts = []
    started = time.perf_counter()
    for attempt in range(2):
        try:
            response = llm_runner.call_model("openai2", messages, RERANK_SCHEMA, timeout)
            parsed = llm_runner.parse_json_content(response["content"])
            errors = validate_decision(parsed, case["candidate_ids"])
            attempts.append({"attempt": attempt + 1, "errors": errors})
            if not errors:
                return {
                    "decision": parsed,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                    "input_tokens": response.get("input_tokens", 0),
                    "output_tokens": response.get("output_tokens", 0),
                    "attempts": attempts,
                    "provider_error": None,
                }
            messages.append({"role": "assistant", "content": json.dumps(parsed, ensure_ascii=False)})
            messages.append({"role": "user", "content": "다음 오류를 수정해 JSON만 다시 반환하라: " + "; ".join(errors)})
        except (llm_runner.ProviderError, ValueError, json.JSONDecodeError) as exc:
            attempts.append({"attempt": attempt + 1, "errors": [str(exc)]})
            if attempt == 1:
                return {
                    "decision": {"answerable": False, "ranked_chunk_ids": []},
                    "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "attempts": attempts,
                    "provider_error": getattr(exc, "error_type", type(exc).__name__),
                }
    raise AssertionError("도달할 수 없는 분기")


def write_results(rows: list[dict[str, Any]], metrics: dict[str, Any]) -> tuple[Path, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    result_dir = ROOT / "results"
    run_path = result_dir / f"reranker-run-{stamp}.jsonl"
    summary_path = result_dir / f"reranker-summary-{stamp}.csv"
    metrics_path = result_dir / f"reranker-metrics-{stamp}.json"
    run_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    fields = [
        "suite", "case_id", "category", "answerable", "candidate_has_relevant", "baseline_rank",
        "predicted_answerable", "reranker_rank", "latency_ms", "input_tokens", "output_tokens", "provider_error",
    ]
    with summary_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return run_path, summary_path, metrics_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Workmate Reranker·답변 가능성 평가")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--limit", type=int, default=0, help="연결 확인용 Case 제한, 0이면 전체")
    parser.add_argument("--case-id", action="append", default=[], help="지정한 Case만 평가, 여러 번 사용 가능")
    parser.add_argument("--corpus", type=Path, help="단일 Corpus 재평가")
    parser.add_argument("--cases", type=Path, help="단일 Case Set 재평가")
    parser.add_argument("--search-result", type=Path, help="--corpus/--cases 검색 결과 JSONL")
    parser.add_argument("--suite-name", default="real_meeting", help="단일 평가 Set 이름")
    parser.add_argument("--expanded-result", type=Path, default=ROOT / "results" / "postgres-run-20260810-163701.jsonl")
    parser.add_argument("--lexical-result", type=Path, default=ROOT / "results" / "lexical-run-20260810-165152.jsonl")
    args = parser.parse_args()

    load_env(LLM_ROOT / ".env")
    llm_runner = load_llm_runner()
    if any(value is not None for value in (args.corpus, args.cases, args.search_result)):
        if not all(value is not None for value in (args.corpus, args.cases, args.search_result)):
            raise ValueError("--corpus, --cases, --search-result를 함께 지정하세요.")
        corpus = load_jsonl(args.corpus)
        cases = build_single_eval_cases(
            corpus, load_jsonl(args.cases), load_jsonl(args.search_result),
            "rrf_exact_top_5", "rrf_exact_rank", args.suite_name,
        )
    else:
        corpus = load_jsonl(ROOT / "corpus" / "expanded_meeting_chunks.jsonl")
        cases = build_eval_cases(
            corpus,
            load_jsonl(ROOT / "cases" / "expanded_cases.jsonl"),
            load_jsonl(args.expanded_result),
            load_jsonl(ROOT / "cases" / "lexical_holdout_cases.jsonl"),
            load_jsonl(args.lexical_result),
        )
    if args.case_id:
        wanted = set(args.case_id)
        cases = [case for case in cases if case["case_id"] in wanted]
        missing = wanted - {case["case_id"] for case in cases}
        if missing:
            raise ValueError(f"존재하지 않는 Case: {sorted(missing)}")
    if args.limit:
        cases = cases[:args.limit]

    rows = []
    for index, case in enumerate(cases, 1):
        print(f"[{index}/{len(cases)}] {case['case_id']}")
        evaluated = evaluate_case(case, llm_runner, args.timeout)
        decision = evaluated.pop("decision")
        relevant = set(case["relevant_chunk_ids"])
        rows.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "suite": case["suite"],
            "case_id": case["case_id"],
            "category": case["category"],
            "answerable": case.get("answerable", True),
            "relevant_chunk_ids": case["relevant_chunk_ids"],
            "candidate_ids": case["candidate_ids"],
            "candidate_has_relevant": bool(relevant & set(case["candidate_ids"])),
            "baseline_rank": case["baseline_rank"],
            "predicted_answerable": decision["answerable"],
            "ranked_chunk_ids": decision["ranked_chunk_ids"],
            "reranker_rank": first_relevant_rank(decision["ranked_chunk_ids"], relevant),
            **evaluated,
        })

    valid_rows = [row for row in rows if not row["provider_error"]]
    latencies = [row["latency_ms"] for row in valid_rows]
    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": llm_runner.model_config("openai2")["model"],
        "case_count": len(rows),
        "provider_error_count": len(rows) - len(valid_rows),
        "candidate_recall": sum(row["candidate_has_relevant"] for row in rows if row["answerable"])
        / sum(row["answerable"] for row in rows),
        "baseline_ranking": ranking_metrics(rows, "baseline_rank"),
        "reranker_ranking": ranking_metrics(rows, "reranker_rank"),
        "answerability": answerability_metrics(rows),
        "reranker_only_answerability": answerability_metrics(rows, exclude_retrieval_misses=True),
        "rank_changes": rank_changes(rows),
        "by_suite": {
            suite: {
                "baseline_ranking": ranking_metrics([row for row in rows if row["suite"] == suite], "baseline_rank"),
                "reranker_ranking": ranking_metrics([row for row in rows if row["suite"] == suite], "reranker_rank"),
                "answerability": answerability_metrics([row for row in rows if row["suite"] == suite]),
            }
            for suite in sorted({row["suite"] for row in rows})
        },
        "latency": {
            "p50_ms": percentile(latencies, 0.50) if latencies else None,
            "p95_ms": percentile(latencies, 0.95) if latencies else None,
        },
        "input_tokens": sum(row["input_tokens"] for row in rows),
        "output_tokens": sum(row["output_tokens"] for row in rows),
    }
    run_path, summary_path, metrics_path = write_results(rows, metrics)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"상세 결과: {run_path}")
    print(f"요약 결과: {summary_path}")
    print(f"전체 지표: {metrics_path}")


if __name__ == "__main__":
    main()
