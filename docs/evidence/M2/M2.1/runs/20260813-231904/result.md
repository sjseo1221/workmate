# M2.1-03 Gmail·Calendar 승인 Task 연결 검수 결과

## 1. 기본 정보

- 마일스톤: M2.1
- 제목: Gmail·Calendar 승인 Task 연결
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-231904

## 2. 구현 요약

- [`weekly_classification.py`](../../../../../../workmate-agent/app/workflows/weekly_classification.py)에 저장된 Task를 주간 분류 항목으로 연결하는 `link_approved_tasks` Workflow 경계를 추가했다.
- Gmail·Calendar 원본은 Provider에서 직접 읽지 않고 Task 원장에 저장된 승인 결과만 포함한다. 외부 Task는 `task_id`와 `source_id`를 모두 `source_refs`로 보존한다.
- 요청 `user_id`와 일치하지 않는 Task, Soft Delete Task, `cancelled` Task는 결과에서 제외한다.
- 결과는 bucket 순서와 `task_id`로 정렬해 결정성을 보장한다.
- [`test_weekly_source_link.py`](../../../../../../workmate-agent/tests/test_weekly_source_link.py)에 Gmail·Calendar source ID, 사용자 격리, 삭제·취소 제외, 결정적 정렬 검증을 추가했다.

## 3. 검증 명령과 결과

```text
.\.venv\Scripts\python.exe -m unittest tests.test_weekly_classification tests.test_weekly_source_link -v
.\.venv\Scripts\python.exe -m compileall -q app
git diff --check
```

| 검수 항목 | 결과 | 근거 |
| --- | --- | --- |
| 주간 기간·상태 분류 회귀 | PASS | 5 tests PASS |
| Gmail·Calendar 승인 source ID 연결 | PASS | `test_links_approved_gmail_and_calendar_sources` |
| 사용자 범위 격리 | PASS | 다른 `assignee_user_id` 결과 제외 |
| Soft Delete·취소 제외 | PASS | `test_soft_deleted_and_cancelled_tasks_are_excluded` |
| 결정적 정렬 | PASS | `test_order_is_deterministic` |
| Python compileall | PASS | `compileall -q app` |
| diff 형식 | PASS | `git diff --check` |

총 8개 테스트 PASS, FAIL 0, SKIP 0이며 수동 검수·외부 Secret·실제 Provider 호출은 포함하지 않았다.

## 4. 자동 승인 및 다음 작업

- 자동 승인: 적용
- 자동 진행 판정: 정의된 검증 명령과 검수 항목이 모두 정확히 PASS
- 자동 진행 보류 사유: 없음
- 최신 승인 실행: `20260813-231904`
- 다음 착수 항목: M2.1-04 회의 Action Item 연결 경계
- 재개 조건: 해당 없음

## 5. 범위와 보류

- 이 백로그는 Gmail·Calendar API를 다시 호출하거나 미승인 Provider 신호를 보고서에 포함하지 않는다. 실제 동기화와 승인 생성은 M1.2/M1.4의 원장을 전제로 한다.
- 회의 Action Item 원본 존재 검증은 M2.1-04에서 별도 경계로 검증한다.

## 6. 최종 판단

- 승인 여부: 승인
- 승인 방식: 자동 승인(검증 명령)
- 검수 의견: 사용자 범위와 승인 Task 원본 참조를 보존하는 로컬 Workflow 경계가 구현되었고, 정의된 회귀 검증이 모두 PASS했다.
