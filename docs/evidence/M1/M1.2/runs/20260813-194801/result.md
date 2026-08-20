# M1.2 검수 결과

## 1. 기본 정보

- 마일스톤: M1.2 외부 소스 연동
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: `20260813-194801`
- 코드 버전: `workmate-agent` 작업 트리

## 2. 최신 실행과 승인

- latest_run_id: `20260813-194801`
- latest_run_status: PASS
- latest_approved_run_id: `20260813-194801`
- approved_at: 2026-08-13 19:48 Asia/Seoul
- reviewer: 자동 승인(검증 명령)

## 3. 구현 요약

- `GmailAdapter`가 Profile·Messages·History·Pub/Sub Watch REST 응답을 정규화한다.
- `GoogleCalendarAdapter`가 Events·Watch REST 응답을 정규화하고 `calendar_id:event_id` 원본 키를 제공한다.
- `ExternalSyncWorkflow`가 Gmail `historyId`와 Calendar `nextSyncToken`을 `SyncStateRepository`에 저장한다.
- Gmail History·Calendar syncToken `410 Gone`을 Cursor 만료로 변환하고 초기 동기화 경고를 반환한다.
- OAuth 자격 증명은 `AuthorizedSession` 주입 방식이며 Adapter가 Secret·Token을 저장하지 않는다.
- 운영 A2A 공개 응답에는 Provider 원문이나 Mock 결과를 추가하지 않았다.

## 4. 구현·테스트 경로

- Google Adapter: [`google.py`](../../../../../workmate-agent/app/providers/google.py)
- Sync Workflow: [`external_sync.py`](../../../../../workmate-agent/app/workflows/external_sync.py)
- Adapter·Workflow 계약 테스트: [`test_google_adapters.py`](../../../../../workmate-agent/tests/test_google_adapters.py)
- Sync Repository: [`sync_state.py`](../../../../../workmate-agent/app/repositories/sync_state.py)
- OAuth 원본 검증: [`google-oauth-test/README.md`](../../../../../google-oauth-test/README.md)

## 5. 실행 명령과 결과

```text
cd C:\dev\workmate\workmate-agent
.\.venv\Scripts\python.exe -m unittest tests.test_google_adapters -v
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check

cd C:\dev\workmate\google-oauth-test
.\venv\Scripts\python.exe smoke_test.py
.\venv\Scripts\python.exe smoke_test.py --watch
```

- Adapter·Workflow 계약 테스트: PASS (5개)
- OAuth 실제 Gmail Profile·Messages·History: PASS
- OAuth 실제 Calendar Events: PASS
- Gmail·Calendar Watch: PASS
- 새 Adapter 실제 OAuth 세션 호출·정규화: PASS (Gmail 1개, Calendar 76개)
- Calendar `nextSyncToken` 확인: PASS
- `compileall`: PASS
- `uv lock --offline`: PASS
- `git diff --check`: PASS
- 미실행·차단 항목: 없음

초기 샌드박스 실행의 외부 HTTPS는 `WinError 10013`으로 차단됐으나, 권한 상승으로 동일 Provider 검증을 재실행해 정확히 PASS했다. 실패 로그는 보존하되 최신 승인 실행은 성공 결과만 연결한다.

## 6. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Gmail Profile·Messages·History 조회 | PASS | OAuth smoke·Adapter 실제 호출 |
| Calendar Events 조회·정규화 | PASS | OAuth smoke·Adapter 실제 호출 |
| Gmail·Calendar Watch 등록 | PASS | `smoke_test.py --watch` |
| Gmail historyId 저장 경계 | PASS | `ExternalSyncWorkflow`, 계약 테스트 |
| Calendar nextSyncToken 저장 경계 | PASS | `ExternalSyncWorkflow`, 계약 테스트 |
| 410 Cursor 초기화 경고 | PASS | `test_calendar_workflow_resets_expired_cursor` |
| 사용자 승인·Secret 비저장 | PASS | 실행 환경·증빙 검사 |

## 7. 자동 진행 판정

- 자동 진행 판정: 자동 착수
- 자동 진행 보류 사유: 없음 (외부 Provider 사용은 사용자 승인 완료)
- 필요한 조치 또는 사용자 승인: 없음
- 재개 조건: 해당 없음
- 다음 백로그: M1.3 Task 관리

## 8. 최종 판단

- 승인 여부: 승인
- 검수 의견: 정의된 Adapter·Workflow 테스트와 실제 Gmail·Calendar·Watch 검증이 모두 PASS하고 미실행·차단 항목이 없어 자동 승인 처리한다.
- 다음 조치: M1.3 Task 관리
