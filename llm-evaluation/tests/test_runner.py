import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_eval import (
    GENERATION_ONLY_KEYWORDS,
    ProviderError,
    assert_format_validation,
    build_generation_schema,
    build_target_schema,
    call_model,
    call_nvidia_gemma,
    check_nvidia_models_available,
    expectation_score,
    grade_output,
    load_cases,
    run_case,
    strip_gemma_thought,
    strip_optional_nulls,
    validate_case_inputs,
    validation_errors,
)


class EvaluationRunnerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_schema = json.loads((ROOT.parent / "docs" / "schemas" / "workmate-skill-schemas.schema.json").read_text(encoding="utf-8"))
        cls.cases = load_cases(ROOT / "cases" / "sample_cases.jsonl")

    def test_sample_cases_and_schema_refs(self):
        self.assertEqual(4, len(self.cases))
        for case in self.cases:
            target = build_target_schema(self.root_schema, case["schema_def"])
            self.assertEqual("object", target["type"])

    def test_full_cases_contains_five_cases_per_skill(self):
        cases = load_cases(ROOT / "cases" / "full_cases.jsonl")
        self.assertEqual(20, len(cases))
        self.assertEqual(20, len({case["case_id"] for case in cases}))
        counts = {}
        for case in cases:
            counts[case["skill_id"]] = counts.get(case["skill_id"], 0) + 1
        self.assertEqual(
            {"daily_briefing": 5, "weekly_report": 5, "analyze_meeting": 5, "search_meetings": 5},
            counts,
        )
        for case in cases:
            schema = build_target_schema(self.root_schema, case["schema_def"])
            validate_case_inputs(case, schema)

    def test_second_full_case_set_is_distinct_and_valid(self):
        first = load_cases(ROOT / "cases" / "full_cases.jsonl")
        second = load_cases(ROOT / "cases" / "full_cases2.jsonl")
        self.assertEqual(20, len(second))
        self.assertEqual(20, len({case["case_id"] for case in second}))
        self.assertTrue({case["case_id"] for case in first}.isdisjoint(case["case_id"] for case in second))
        first_task_titles = {task["title"] for case in first for task in case["input"].get("tasks", [])}
        second_task_titles = {task["title"] for case in second for task in case["input"].get("tasks", [])}
        self.assertTrue(first_task_titles.isdisjoint(second_task_titles))
        first_meeting_texts = {
            text
            for case in first
            for text in [
                *(item.get("summary") for item in case["input"].get("meetings", [])),
                *(item.get("content") for item in case["input"].get("chunks", [])),
                *(item.get("content") for item in case["input"].get("contexts", [])),
            ]
            if text
        }
        second_meeting_texts = {
            text
            for case in second
            for text in [
                *(item.get("summary") for item in case["input"].get("meetings", [])),
                *(item.get("content") for item in case["input"].get("chunks", [])),
                *(item.get("content") for item in case["input"].get("contexts", [])),
            ]
            if text
        }
        self.assertTrue(first_meeting_texts.isdisjoint(second_meeting_texts))
        self.assertTrue(
            {case["input"].get("query") for case in first if case["input"].get("query")}.isdisjoint(
                case["input"].get("query") for case in second if case["input"].get("query")
            )
        )
        counts = {}
        for case in second:
            counts[case["skill_id"]] = counts.get(case["skill_id"], 0) + 1
            schema = build_target_schema(self.root_schema, case["schema_def"])
            validate_case_inputs(case, schema)
        self.assertEqual(
            {"daily_briefing": 5, "weekly_report": 5, "analyze_meeting": 5, "search_meetings": 5},
            counts,
        )

    def test_invalid_precomputed_priority_is_rejected(self):
        case = json.loads(json.dumps(self.cases[0]))
        case["input"]["precomputed_priorities"][0]["score_breakdown"]["importance"] = 99
        schema = build_target_schema(self.root_schema, case["schema_def"])
        with self.assertRaisesRegex(ValueError, "precomputed_priorities"):
            validate_case_inputs(case, schema)

    def test_date_time_format_is_enforced(self):
        assert_format_validation()
        schema = {"type": "object", "properties": {"due_at": {"type": "string", "format": "date-time"}}}
        self.assertTrue(validation_errors({"due_at": "내일 오전까지"}, schema))
        self.assertTrue(validation_errors({"due_at": "2026-08-06"}, schema))
        self.assertFalse(validation_errors({"due_at": "2026-08-06T09:00:00+09:00"}, schema))

    def test_expectation_score(self):
        score = expectation_score(
            {"title": "QA 서버 빌드", "source_refs": ["task-1"]},
            {"must_include": ["QA 서버"], "forbidden": ["출시 확정"], "expected_source_ids": ["task-1"], "evidence_texts": [], "expected_values": {"title": "QA 서버 빌드"}},
        )
        self.assertEqual(1.0, score["average"])
        mismatch = expectation_score(
            {"insufficient_evidence": True},
            {"expected_values": {"insufficient_evidence": False}},
        )
        self.assertLess(mismatch["average"], 1.0)

    def test_generation_schema_uses_common_subset(self):
        def check(node):
            if isinstance(node, dict):
                self.assertFalse(GENERATION_ONLY_KEYWORDS & node.keys())
                if isinstance(node.get("properties"), dict):
                    self.assertEqual(set(node["properties"]), set(node["required"]))
                    self.assertFalse(node["additionalProperties"])
                if node.get("type") == "array":
                    self.assertGreater(node["maxItems"], 0)
                for value in node.values():
                    check(value)
            elif isinstance(node, list):
                for value in node:
                    check(value)

        for case in self.cases:
            canonical = build_target_schema(self.root_schema, case["schema_def"])
            check(build_generation_schema(canonical))

    def test_optional_nulls_are_removed_before_canonical_validation(self):
        canonical = build_target_schema(self.root_schema, "DailyBriefingResult")
        output = {
            "date": "2026-08-08", "summary": "테스트", "calendar_events": [],
            "important_signals": [], "priorities": [{
                "rank": 1, "task_id": "task-1", "title": "테스트", "score": 80,
                "score_breakdown": None, "reasons": ["마감 임박"],
            }], "source_refs": ["task-1"],
        }
        cleaned = strip_optional_nulls(output, canonical)
        self.assertNotIn("score_breakdown", cleaned["priorities"][0])

    def test_skill_graders_reject_semantic_errors(self):
        daily = self.cases[0]
        priorities = json.loads(json.dumps(daily["input"]["precomputed_priorities"]))
        valid_daily = {
            "summary": "QA 서버 빌드 배포, 로그인 오류 원인 분석, 신규 캐릭터 밸런스 검토",
            "priorities": priorities,
            "source_refs": ["task-101", "task-102", "task-103"],
        }
        self.assertTrue(grade_output(daily, valid_daily)["valid"])
        priorities[0]["score"] = 74
        self.assertFalse(grade_output(daily, valid_daily)["valid"])
        hallucinated_daily = json.loads(json.dumps(valid_daily))
        hallucinated_daily["priorities"] = json.loads(json.dumps(daily["input"]["precomputed_priorities"]))
        hallucinated_daily["important_signals"] = [{"source_id": "made-up-source", "related_task_ids": []}]
        self.assertEqual(0.0, grade_output(daily, hallucinated_daily)["daily_source_grounding"])

        weekly = self.cases[1]
        bad_weekly = {
            "period": {"start": "2026-08-03", "end": "2026-08-09"},
            "summary": "배포 자동화 적용 로그인 오류 분석 캐릭터 데이터 검수 스토어 심사 제출",
            "completed": [{"task_id": "task-201"}], "in_progress": [{"task_id": "task-202"}],
            "delayed": [{"task_id": "task-203"}], "unresolved_issues": [{"task_id": "task-203"}],
            "source_refs": ["task-201", "task-202", "task-203", "task-204", "meeting-31"],
        }
        self.assertEqual(0.0, grade_output(weekly, bad_weekly)["weekly_period"])
        self.assertEqual(0.0, grade_output(weekly, bad_weekly)["weekly_next_week_plans"])

        meeting = self.cases[2]
        altered_evidence = {
            "summary": "원인 분석 결과", "source_refs": ["meeting-401", "transcript-401-v1", "chunk-2"],
            "action_items": [{
                "evidence_text": "이병준: 제가 내일 오전까지 원인 분석 결과를 정리하겠습니다.",
                "evidence_span": {"meeting_chunk_ids": ["chunk-2"], "start_ms": 8000, "end_ms": 16000},
            }],
        }
        self.assertFalse(grade_output(meeting, altered_evidence)["valid"])
        grounded_meeting = {
            "meeting_id": "meeting-401", "transcript_ref": "transcript-401-v1",
            "summary": "원인 분석 결과", "source_refs": [],
            "action_items": [{
                "evidence_text": "제가 내일 오전까지 원인 분석 결과를 정리하겠습니다.",
                "evidence_span": {"meeting_chunk_ids": ["chunk-2"], "start_ms": 8000, "end_ms": 16000},
            }],
        }
        self.assertTrue(grade_output(meeting, grounded_meeting)["valid"])

        search = self.cases[3]
        wrong_status = {
            "answer": "12일 주간 개발 회의", "insufficient_evidence": True,
            "sources": [{
                "meeting_id": "meeting-501", "meeting_chunk_id": "chunk-501-8",
                "quote": "회귀 테스트까지 반영해서 12일 QA 빌드로 확정하겠습니다.",
            }],
        }
        self.assertFalse(grade_output(search, wrong_status)["valid"])
        missing_answer_detail = json.loads(json.dumps(wrong_status))
        missing_answer_detail["answer"] = "주간 개발 회의에서 결정됐습니다."
        missing_answer_detail["insufficient_evidence"] = False
        self.assertEqual(0.0, grade_output(search, missing_answer_detail)["search_answer_content"])

    def test_retry_usage_is_accumulated_and_final_score_is_gated(self):
        case = self.cases[3]
        schema = build_target_schema(self.root_schema, case["schema_def"])
        invalid = {"answer": "", "sources": [], "insufficient_evidence": False}
        valid = {
            "answer": "12일 주간 개발 회의",
            "sources": [{
                "meeting_id": "meeting-501", "meeting_title": "주간 개발 회의",
                "meeting_date": "2026-08-06", "speaker": "김서연",
                "meeting_chunk_id": "chunk-501-8",
                "quote": "회귀 테스트까지 반영해서 12일 QA 빌드로 확정하겠습니다.",
            }],
            "insufficient_evidence": False,
        }
        usages = [
            {"content": json.dumps(invalid), "input_tokens": 10, "output_tokens": 5, "tokens_per_second": None},
            {"content": json.dumps(valid, ensure_ascii=False), "input_tokens": 20, "output_tokens": 7, "tokens_per_second": None},
        ]
        with patch("run_eval.call_model", side_effect=usages):
            result = run_case("openai", case, schema, 10)
        self.assertEqual(2, result["attempts"])
        self.assertEqual(30, result["input_tokens"])
        self.assertEqual(12, result["output_tokens"])
        self.assertEqual(0.000077, result["estimated_cost_usd"])
        self.assertEqual(2, len(result["attempt_details"]))
        self.assertTrue(result["schema_valid"])
        self.assertTrue(result["semantic_valid"])
        self.assertEqual(1.0, result["final_score"])

    def test_semantic_failure_is_repaired_once(self):
        case = self.cases[3]
        schema = build_target_schema(self.root_schema, case["schema_def"])
        incomplete = {
            "answer": "주간 개발 회의에서 결정됐습니다.",
            "sources": [{
                "meeting_id": "meeting-501", "meeting_title": "주간 개발 회의",
                "meeting_date": "2026-08-06", "speaker": "김서연",
                "meeting_chunk_id": "chunk-501-8",
                "quote": "회귀 테스트까지 반영해서 12일 QA 빌드로 확정하겠습니다.",
            }],
            "insufficient_evidence": False,
        }
        repaired = {**incomplete, "answer": "12일 주간 개발 회의에서 결정됐습니다."}
        usages = [
            {"content": json.dumps(incomplete, ensure_ascii=False), "input_tokens": 10, "output_tokens": 5, "tokens_per_second": None},
            {"content": json.dumps(repaired, ensure_ascii=False), "input_tokens": 20, "output_tokens": 7, "tokens_per_second": None},
        ]
        with patch("run_eval.call_model", side_effect=usages) as call:
            result = run_case("openai2", case, schema, 10)

        self.assertEqual(2, call.call_count)
        self.assertEqual("semantic", result["attempt_details"][0]["error_type"])
        self.assertEqual("semantic", result["attempt_details"][1]["repair_type"])
        self.assertTrue(result["semantic_valid"])
        self.assertEqual(1.0, result["final_score"])

    def test_final_semantic_failure_is_recorded_in_attempt_details(self):
        case = self.cases[3]
        schema = build_target_schema(self.root_schema, case["schema_def"])
        incomplete = {
            "answer": "주간 개발 회의에서 결정됐습니다.",
            "sources": [{
                "meeting_id": "meeting-501", "meeting_title": "주간 개발 회의",
                "meeting_date": "2026-08-06", "speaker": "김서연",
                "meeting_chunk_id": "chunk-501-8",
                "quote": "회귀 테스트까지 반영해서 12일 QA 빌드로 확정하겠습니다.",
            }],
            "insufficient_evidence": False,
        }
        usage = {"content": json.dumps(incomplete, ensure_ascii=False), "input_tokens": 10, "output_tokens": 5, "tokens_per_second": None}
        with patch("run_eval.call_model", side_effect=[usage, usage]):
            result = run_case("openai2", case, schema, 10)

        self.assertFalse(result["semantic_valid"])
        self.assertEqual("semantic", result["attempt_details"][-1]["error_type"])
        self.assertTrue(result["attempt_details"][-1]["errors"])

    def test_retryable_provider_error_is_retried_and_classified(self):
        case = self.cases[3]
        schema = build_target_schema(self.root_schema, case["schema_def"])
        valid = {
            "answer": "12일 주간 개발 회의에서 결정됐습니다.",
            "sources": [{
                "meeting_id": "meeting-501", "meeting_title": "주간 개발 회의",
                "meeting_date": "2026-08-06", "speaker": "김서연",
                "meeting_chunk_id": "chunk-501-8",
                "quote": "회귀 테스트까지 반영해서 12일 QA 빌드로 확정하겠습니다.",
            }],
            "insufficient_evidence": False,
        }
        usages = [
            ProviderError("timeout", "timed out", retryable=True),
            {"content": json.dumps(valid, ensure_ascii=False), "input_tokens": 20, "output_tokens": 7, "tokens_per_second": None},
        ]
        with patch.dict(os.environ, {"PROVIDER_RETRIES": "1"}), patch(
            "run_eval.call_model", side_effect=usages
        ), patch("run_eval.time.sleep") as sleep:
            result = run_case("openai", case, schema, 10)
        self.assertEqual("completed", result["execution_status"])
        self.assertIsNone(result["provider_error"])
        self.assertEqual(2, result["attempts"])
        self.assertEqual("provider_timeout", result["attempt_details"][0]["error_type"])
        sleep.assert_called_once()

    def test_provider_failure_is_not_counted_as_schema_failure(self):
        case = self.cases[3]
        schema = build_target_schema(self.root_schema, case["schema_def"])
        with patch.dict(os.environ, {"PROVIDER_RETRIES": "0"}), patch(
            "run_eval.call_model", side_effect=ProviderError("timeout", "timed out", retryable=True)
        ):
            result = run_case("openai", case, schema, 10)
        self.assertEqual("provider_failed", result["execution_status"])
        self.assertEqual("timeout", result["provider_error"]["type"])
        self.assertIsNone(result["schema_valid"])
        self.assertIsNone(result["semantic_valid"])
        self.assertIsNone(result["final_score"])

    def test_nvidia_llama_uses_openai_compatible_endpoint(self):
        response = {
            "choices": [{"message": {"content": '{"answer":"ok"}'}}],
            "usage": {"prompt_tokens": 11, "completion_tokens": 4},
        }
        env = {
            "NVIDIA_BASE_URL": "https://nvidia.example/v1/",
            "NVIDIA_API_KEY": "test-key",
            "NVIDIA_LLAMA_MODEL": "meta/test-model",
        }
        with patch.dict(os.environ, env), patch("run_eval.post_json", return_value=response) as post:
            result = call_model("nvidia_llama", [{"role": "user", "content": "test"}], {"type": "object"}, 10)

        url, payload, headers, timeout = post.call_args.args
        self.assertEqual("https://nvidia.example/v1/chat/completions", url)
        self.assertEqual("meta/test-model", payload["model"])
        self.assertEqual("json_schema", payload["response_format"]["type"])
        self.assertEqual(1024, payload["max_tokens"])
        self.assertEqual(0.2, payload["temperature"])
        self.assertEqual(0.7, payload["top_p"])
        self.assertFalse(payload["stream"])
        self.assertEqual("Bearer test-key", headers["Authorization"])
        self.assertEqual("application/json", headers["Accept"])
        self.assertEqual(10, timeout)
        self.assertEqual(11, result["input_tokens"])
        self.assertEqual(4, result["output_tokens"])

    def test_openai2_uses_configured_openai_compatible_endpoint(self):
        response = {
            "choices": [{"message": {"content": '{"answer":"ok"}'}}],
            "usage": {"prompt_tokens": 9, "completion_tokens": 3},
        }
        env = {
            "OPENAI_BASE_URL2": "https://provider.example/v1/",
            "OPENAI_API_KEY2": "test-key",
            "OPENAI_MODEL2": "openai/test-model",
        }
        with patch.dict(os.environ, env), patch("run_eval.post_json", return_value=response) as post:
            result = call_model("openai2", [{"role": "user", "content": "test"}], {"type": "object"}, 10)

        url, payload, headers, timeout = post.call_args.args
        self.assertEqual("https://provider.example/v1/chat/completions", url)
        self.assertEqual("openai/test-model", payload["model"])
        self.assertEqual("json_schema", payload["response_format"]["type"])
        self.assertEqual("Bearer test-key", headers["Authorization"])
        self.assertEqual(10, timeout)
        self.assertEqual(9, result["input_tokens"])
        self.assertEqual(3, result["output_tokens"])

    def test_nvidia_gemma_uses_documented_payload_and_cleans_thought_prefix(self):
        response = {
            "choices": [{"message": {"content": '<|channel>thought\n<channel|>{"answer":"ok"}'}}],
            "usage": {"prompt_tokens": 13, "completion_tokens": 6},
        }
        env = {
            "NVIDIA_BASE_URL": "https://nvidia.example/v1/",
            "NVIDIA_API_KEY": "test-key",
            "NVIDIA_GEMMA_MODEL": "google/test-gemma",
        }
        with patch.dict(os.environ, env), patch("run_eval.call_nvidia_gemma", return_value=response) as call:
            result = call_model("nvidia_gemma", [{"role": "user", "content": "test"}], {"type": "object"}, 10)

        base_url, payload, headers, timeout = call.call_args.args
        self.assertEqual("https://nvidia.example/v1/", base_url)
        self.assertEqual("google/test-gemma", payload["model"])
        self.assertNotIn("response_format", payload)
        self.assertEqual({"enable_thinking": False}, payload["chat_template_kwargs"])
        self.assertEqual(1024, payload["max_tokens"])
        self.assertEqual(1.0, payload["temperature"])
        self.assertEqual(0.95, payload["top_p"])
        self.assertFalse(payload["stream"])
        self.assertEqual("Bearer test-key", headers["Authorization"])
        self.assertEqual(10, timeout)
        self.assertEqual('{"answer":"ok"}', result["content"])
        self.assertEqual(13, result["input_tokens"])
        self.assertEqual(6, result["output_tokens"])

    def test_nvidia_gemma_prompt_contains_canonical_schema_and_uses_nvidia_timeout(self):
        case = self.cases[3]
        schema = build_target_schema(self.root_schema, case["schema_def"])
        valid = {
            "answer": "12일 주간 개발 회의에서 결정됐습니다.",
            "sources": [{
                "meeting_id": "meeting-501", "meeting_title": "주간 개발 회의",
                "meeting_date": "2026-08-06", "speaker": "김서연",
                "meeting_chunk_id": "chunk-501-8",
                "quote": "회귀 테스트까지 반영해서 12일 QA 빌드로 확정하겠습니다.",
            }],
            "insufficient_evidence": False,
        }
        usage = {
            "content": json.dumps(valid, ensure_ascii=False),
            "input_tokens": 20,
            "output_tokens": 7,
            "tokens_per_second": None,
        }
        with patch.dict(os.environ, {"NVIDIA_TIMEOUT": "37"}), patch(
            "run_eval.call_model", return_value=usage
        ) as call:
            result = run_case("nvidia_gemma", case, schema, 10)

        messages = call.call_args.args[1]
        self.assertEqual(["user"], [message["role"] for message in messages])
        self.assertIn('"format":"date"', messages[0]["content"])
        self.assertEqual(37, call.call_args.args[3])
        self.assertTrue(result["schema_valid"])
        self.assertTrue(result["semantic_valid"])

    def test_nvidia_gemma_202_response_is_polled(self):
        final = {"choices": [{"message": {"content": "{}"}}]}
        with patch(
            "run_eval.request_json",
            side_effect=[(202, {"requestId": "request-1"}), (200, final)],
        ) as request, patch("run_eval.time.sleep"):
            response = call_nvidia_gemma(
                "https://nvidia.example/v1",
                {"model": "google/test-gemma"},
                {"Authorization": "Bearer test-key"},
                10,
            )

        self.assertEqual(final, response)
        self.assertEqual(2, request.call_count)
        self.assertEqual("https://nvidia.example/v1/chat/completions", request.call_args_list[0].args[0])
        self.assertEqual("POST", request.call_args_list[0].kwargs["method"])
        self.assertEqual("https://nvidia.example/v1/status/request-1", request.call_args_list[1].args[0])
        self.assertEqual("GET", request.call_args_list[1].kwargs["method"])

    def test_gemma_thought_cleaner_leaves_normal_json_unchanged(self):
        self.assertEqual('{"answer":"ok"}', strip_gemma_thought('{"answer":"ok"}'))
        self.assertEqual(
            '{"answer":"ok"}',
            strip_gemma_thought('<|channel>thought\nignored<channel|><|channel>final\n{"answer":"ok"}'),
        )

    def test_nvidia_model_availability_is_checked_once(self):
        env = {
            "NVIDIA_BASE_URL": "https://nvidia.example/v1",
            "NVIDIA_API_KEY": "test-key",
            "NVIDIA_LLAMA_MODEL": "meta/test-model",
            "NVIDIA_GEMMA_MODEL": "google/test-gemma",
        }
        with patch.dict(os.environ, env), patch(
            "run_eval.get_json",
            return_value={"data": [{"id": "meta/test-model"}, {"id": "google/test-gemma"}]},
        ) as get:
            errors = check_nvidia_models_available(["nvidia_llama", "nvidia_gemma"], 10)
        self.assertEqual({}, errors)
        get.assert_called_once_with(
            "https://nvidia.example/v1/models",
            {"Authorization": "Bearer test-key"},
            10,
        )

        with patch.dict(os.environ, {**env, "PROVIDER_RETRIES": "1"}), patch(
            "run_eval.get_json",
            side_effect=[
                ProviderError("timeout", "timed out", retryable=True),
                {"data": [{"id": "meta/test-model"}, {"id": "google/test-gemma"}]},
            ],
        ) as get, patch("run_eval.time.sleep") as sleep:
            errors = check_nvidia_models_available(["nvidia_llama", "nvidia_gemma"], 10)
        self.assertEqual({}, errors)
        self.assertEqual(2, get.call_count)
        sleep.assert_called_once()

        with patch.dict(os.environ, env), patch(
            "run_eval.get_json", return_value={"data": [{"id": "meta/test-model"}]}
        ):
            errors = check_nvidia_models_available(["nvidia_llama", "nvidia_gemma"], 10)
        self.assertEqual({"nvidia_gemma"}, set(errors))
        self.assertEqual("model_unavailable", errors["nvidia_gemma"].error_type)


if __name__ == "__main__":
    unittest.main()
