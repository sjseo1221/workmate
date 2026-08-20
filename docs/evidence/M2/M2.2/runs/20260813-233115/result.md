# M2.2-01 다음 주 계획 근거 추출 검수 결과

## 1. 기본 정보

- 마일스톤: M2.2
- 제목: 다음 주 계획 근거 추출
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-233115

## 2. 구현 요약

- [`weekly_classification.py`](../../../../../../workmate-agent/app/workflows/weekly_classification.py)에 `extract_next_week_plans`와 `ExplicitPlan`을 추가했다.
- 다음 주 마감 Task는 `planned`, 미완료 Action Item은 `carry_over`로 분류한다.
- 명시 계획 문장은 비어 있지 않은 `source_refs`가 있을 때만 `planned`로 포함한다.
- 근거가 없는 일반 Task·빈 source_refs·다른 사용자·Soft Delete·완료·취소 항목은 계획 결과에서 제외한다.
- LLM 문장 생성과 제안·확정 의미 평가를 수행하지 않으며, 해당 범위는 후속 M2.2/M2.3 백로그로 분리했다.

## 3. 검증 명령과 결과

```text
.\.venv\Scripts\python.exe -m unittest tests.test_weekly_source_link tests.test_weekly_classification tests.test_m2_1_integration tests.test_contract -v
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

| 검수 항목 | 결과 | 근거 |
| --- | --- | --- |
| 다음 주 마감 Task 추출 | PASS | `test_extracts_only_evidence_backed_next_week_plans` |
| 미완료 Action Item carry-over | PASS | 동일 테스트 |
| 근거 없는 계획 차단 | PASS | 빈 `source_refs` 일반 계획 제외 |
| 사용자·상태 범위 격리 | PASS | 다른 사용자·완료·취소·삭제 항목 제외 |
| weekly_report Schema 회귀 | PASS | Contract 10 tests PASS |
| 전체 회귀·통합 | PASS | 총 23 tests PASS |
| Python compileall | PASS | `compileall -q app tests` |
| diff 형식 | PASS | `git diff --check` |

총 23개 테스트 PASS, FAIL 0, SKIP 0이며 외부 Secret·실제 LLM 호출·수동 의미 검수는 포함하지 않았다.

## 4. 자동 승인 및 다음 작업

- 자동 승인: 적용
- 자동 진행 판정: 정의된 검증 명령과 검수 항목이 모두 정확히 PASS
- 자동 진행 보류 사유: 없음(결정론적 근거 경계 범위)
- 최신 승인 실행: `20260813-233115`
- 다음 착수 항목: M2.2-02 제안·확정 의미 판정 및 LLM 평가 경계
- 재개 조건: LLM 평가 Case와 수동 검수자 지정

## 5. 범위와 보류

- 실제 LLM 호출·프롬프트 평가·제안/확정 의미의 사람 검수는 M2.2-02에서 수행한다.
- 근거가 없는 계획을 확정 계획으로 표시하지 않는 차단 규칙은 이번 백로그에서 완료했다.

## 6. 최종 판단

- 승인 여부: 승인
- 승인 방식: 자동 승인(검증 명령)
- 검수 의견: 다음 주 계획 후보가 원본 근거가 있는 경우에만 생성되고, 근거 없는 계획은 차단되며, 정의된 검증 명령이 모두 PASS했다.
