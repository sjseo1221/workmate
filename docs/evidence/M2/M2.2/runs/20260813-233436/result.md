# M2.2-02 제안·확정 의미 판정 및 LLM 평가 경계 검수 결과

## 1. 기본 정보

- 마일스톤: M2.2
- 제목: 제안·확정 의미 판정 및 LLM 평가 경계
- 담당자: Codex
- 검수자: 미정
- 상태: 검수 중
- 실행일: 2026-08-13
- 실행 ID: 20260813-233436

## 2. 구현 요약

- [`weekly_report.py`](../../../../../../workmate-agent/app/workflows/weekly_report.py)에 `validate_next_week_plans`를 추가했다.
- `planned`, `carry_over`, `suggestion` 후보는 허용된 `source_refs`가 있을 때만 Artifact 후보로 통과한다.
- 근거 없는 확정·제안, 허용되지 않은 원본 ID, 빈 제목, 지원하지 않는 kind는 `rejected`에 기록하고 공개 Artifact에는 넣지 않는다.
- 제목 공백 제거와 source ID 중복 제거를 수행하며 결과 순서는 결정적이다.

## 3. 검증 명령과 결과

```text
workmate-agent\.venv\Scripts\python.exe -m unittest tests.test_weekly_plan_grounding tests.test_weekly_source_link tests.test_weekly_classification tests.test_m2_1_integration tests.test_contract -v
workmate-agent\.venv\Scripts\python.exe -m compileall -q app tests
workmate-agent: git diff --check
llm-evaluation\.venv\Scripts\python.exe run_eval.py --dry-run --cases cases/full_cases.jsonl --models openai2 --repeat 1
llm-evaluation\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

| 검수 항목 | 결과 | 근거 |
| --- | --- | --- |
| 근거 있는 planned/carry_over/suggestion 통과 | PASS | `test_accepts_only_grounded_plan_kinds` |
| 근거 없는 계획 차단 | PASS | `test_rejects_ungrounded_and_unknown_source_plans` |
| source_refs 정규화 | PASS | `test_normalizes_title_and_deduplicates_source_refs` |
| Workmate 회귀·Contract | PASS | 26 tests PASS |
| LLM 평가 Case·Schema dry-run | PASS | 20 Case와 JSON Schema 검증 완료 |
| LLM 평가기 자체 테스트 | PASS | 23 tests PASS |
| 실제 LLM Provider 평가 | 미실행 | 비용·외부 호출 및 사용자/검수자 확인 필요 |
| 수동 제안·확정 의미 검수 | 미실행 | 평가 결과 확인 후 검수자 판단 필요 |

로컬 검증은 모두 PASS했지만 실제 LLM Provider 평가와 수동 의미 검수가 미실행이므로 자동 승인 조건을 충족하지 않는다.

## 4. 자동 진행 판정

- 자동 승인: 미적용
- 자동 진행 보류 사유: 실제 LLM 호출과 제안·확정 의미에 대한 수동 검수가 남아 있다.
- 최신 실행 상태: 검수 중
- latest_approved_run_id: 이전 승인 값 유지
- 재개 조건: LLM 평가 Case 실행 결과와 검수자 승인
- 다음 작업: LLM 평가 실행 후 제안·확정 의미 수동 검수

## 5. 범위와 보류

- API Key·실제 LLM 응답·비용·Token은 증빙에 저장하지 않는다.
- dry-run은 Case·Schema·평가기 동작만 검증하며 모델 품질 통과를 의미하지 않는다.
- 실제 Provider 평가가 PASS하고 검수자가 승인하기 전에는 M2.2-02를 완료로 표시하지 않는다.

## 6. 최종 판단

- 승인 여부: 보류
- 검수 의견: grounding validator와 평가기 검증은 PASS이나, 외부 LLM 품질과 사람의 의미 판정이 남아 있어 검수 중으로 유지한다.
