# M1.4 검수 결과

## 1. 기본 정보

- 마일스톤: M1.4
- 제목: Gmail·Calendar Task 제안
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-215728
- 코드 버전: workmate-agent 현재 작업 트리
- 입력 데이터 버전: M1.2 정규화 Adapter·M1.3 Task Repository 계약

## 2. 최신 실행과 승인

- latest_run_id: `20260813-215728`
- latest_run_status: PASS
- latest_approved_run_id: `20260813-215728`
- approved_at: 2026-08-13 21:57 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: Gmail·Calendar 후보를 SSE 임시 제안으로 전달하고 사용자 승인 시에만 Task를 생성한다.
- 완료 기준: 후보 발행·SSE, 승인·무시, 사용자 범위, Idempotency-Key, 동일 원본 멱등, 유사 Task 재확인 테스트가 PASS한다.
- 백로그 범위: M1.4-01~03
- 미완료·보류 백로그: 없음

## 4. 구현 경로

- [제안 Hub·승인 API](../../../../../workmate-agent/app/proposal_api.py)
- [외부 동기화 후보 발행 경계](../../../../../workmate-agent/app/workflows/external_sync.py)
- [Route 등록](../../../../../workmate-agent/app/main.py)
- Schema: `docs/02-a2a-interface.md`의 제안 Route 계약을 유지하며 공개 A2A Schema는 변경하지 않음

## 5. 테스트 파일 경로

- [M1.4 계약 테스트](../../../../../workmate-agent/tests/test_proposals.py)
- [Google Adapter 회귀](../../../../../workmate-agent/tests/test_google_adapters.py)
- [Sync State 회귀](../../../../../workmate-agent/tests/test_sync_state_repository.py)
- [Task API·Repository 회귀](../../../../../workmate-agent/tests/test_task_api.py), [`test_task_repository.py`](../../../../../workmate-agent/tests/test_task_repository.py)
- Fixture/입력: 테스트 내부의 정규화 GmailMessage·CalendarEvent Fixture
- 모델 평가 Case: 해당 없음

## 6. 구현 요약

- `ProposalHub`가 사용자·원본별 임시 제안과 SSE Queue를 관리한다.
- `ExternalSyncWorkflow.publish_task_proposals()`는 상위 후보 판정이 제공한 `source_id → title` 매핑만 발행한다. 후보가 아닌 외부 항목은 제안하지 않는다.
- `POST /api/v1/email-task-proposals:review`와 `POST /api/v1/calendar-task-proposals:review`는 `approve`·`ignore`를 처리한다.
- 승인 시 `email/message_id`, `calendar/calendar_id:event_id`로 Task 원본을 저장하고 동일 원본은 기존 Task를 반환한다.
- 제목·담당자·마감일이 같은 활성 Task가 있으면 `409 SIMILAR_TASK_EXISTS`를 반환하며 `allow_similar_duplicate=true`일 때만 추가한다.
- 제안과 멱등 캐시는 DB에 저장하지 않는다. Task 저장만 기존 Repository가 담당한다.

## 7. 실행 명령과 결과

```text
cd C:\dev\workmate\workmate-agent
.\.venv\Scripts\python.exe -m unittest tests.test_runtime_boot tests.test_contract tests.test_internal_chat tests.test_internal_chat_ui tests.test_ui_working_fixture tests.test_google_adapters tests.test_sync_state_repository tests.test_task_repository tests.test_task_api tests.test_task_ui tests.test_proposals -q
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

- 전체 관련 회귀 테스트: **51 PASS, 0 FAIL, 0 SKIP**
- Python 구문 검사: **PASS**
- `git diff --check`: **PASS**
- 외부 PostgreSQL 통합 테스트: M1.1/M1.2 승인 증빙에서 완료된 범위이며, 이번 M1.4 실행에서는 외부 DB 미설정 SKIP을 포함하지 않음

## 8. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Gmail 후보 발행·SSE | PASS | [`test_proposals.py`](../../../../../workmate-agent/tests/test_proposals.py) |
| Calendar 후보 발행·`calendar_id:event_id` | PASS | [`test_proposals.py`](../../../../../workmate-agent/tests/test_proposals.py) |
| 승인 시 Task 저장·무시 시 미저장 | PASS | [`test_proposals.py`](../../../../../workmate-agent/tests/test_proposals.py) |
| 동일 원본 멱등성 | PASS | [`test_proposals.py`](../../../../../workmate-agent/tests/test_proposals.py) |
| 유사 Task 재확인 | PASS | [`test_proposals.py`](../../../../../workmate-agent/tests/test_proposals.py) |
| Idempotency-Key·사용자 범위 | PASS | [`test_proposals.py`](../../../../../workmate-agent/tests/test_proposals.py) |
| 기존 M0·M1.2·M1.3 회귀 | PASS | 실행 명령 51개 테스트 |

## 9. 자동 진행 판정

- 정의된 검증 명령: 모두 PASS
- PASS가 아닌 결과: 없음
- 미실행·수동 검수·차단: 없음
- 자동 재작업 착수: 아니오
- 판정: 자동 승인(검증 명령)

## 10. 최종 판단

- 승인 여부: 승인 — 자동 승인(검증 명령)
- 검수 의견: M1.4의 후보 발행, SSE, 승인·무시·중복 방지 계약을 통과했다.
- 의도적으로 제외한 범위: 실제 LLM 후보 판정과 Provider Watch 트리거 자체는 M1.2 Adapter·후속 Workflow가 제공하는 입력 경계로 두었다. 이 실행은 후보로 판정된 정규화 항목의 제안·검토·Task 저장을 검증한다.
- 다음 조치: M1.5 우선순위·브리핑
