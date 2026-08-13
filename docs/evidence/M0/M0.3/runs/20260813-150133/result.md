# M0.3-03 검수 결과

## 1. 기본 정보

- 마일스톤: M0.3 내부 챗봇 API
- 제목: 장기 Task API
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13 15:01 Asia/Seoul
- 실행 ID: 20260813-150133
- 코드 버전: 로컬 작업 브랜치 `feat/M0.1-01-sdk-runtime`
- 입력 데이터 버전: M0.1 A2A Task Store·Checkpoint 영속 경계

## 2. 최신 실행과 승인

- latest_run_id: 20260813-150133
- latest_run_status: PASS
- latest_approved_run_id: 20260813-150133
- approved_at: 2026-08-13 15:01 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: 내부 검증 API에서 Task Snapshot을 조회·Polling하고 Terminal Task 취소를 일관되게 처리한다.
- 완료 기준: 요청 결과가 영속 Task Store에 저장되고, Task 조회·미존재 404·Terminal 취소 409를 검증한다.
- 백로그 범위: M0.3-03
- 미완료·보류 백로그: 없음

## 4. 구현 경로

- 구현 코드: [`app/internal_chat.py`](../../../../../../workmate-agent/app/internal_chat.py), [`app/a2a/persistence.py`](../../../../../../workmate-agent/app/a2a/persistence.py)
- Schema 또는 Migration: 기존 M0.1 A2A Task Store·Artifact 저장 경계 재사용
- UI 코드: 해당 없음. M0.4 범위다.

## 5. 구현 내용

- 내부 메시지 실행 결과를 기존 `PersistentTaskStore` 또는 `PostgresTaskStore`에 Task·Message·Artifact로 저장한다.
- `GET /api/v1/internal/skill-chat/tasks/{id}`에서 사용자 범위가 적용된 Task Snapshot을 반환한다.
- 존재하지 않는 Task는 `404`, 이미 Terminal인 Task 취소는 `409`로 반환한다.
- `POST /api/v1/internal/skill-chat/tasks/{id}:cancel`은 진행 중 Task에만 취소 상태를 기록한다.
- 현재 런타임 준비 Workflow는 즉시 완료되므로 Polling 검증은 완료 Snapshot을 대상으로 수행한다. 실제 비동기 업무 Workflow의 queued/running 구간은 후속 업무 연결에서 확장한다.

## 6. 테스트 파일 경로

- 내부 API·Task 테스트: [`tests/test_internal_chat.py`](../../../../../../workmate-agent/tests/test_internal_chat.py)
- A2A 런타임 회귀: [`tests/test_runtime_boot.py`](../../../../../../workmate-agent/tests/test_runtime_boot.py)
- 공개 A2A Contract Test: [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py)
- 영속 Store 회귀: [`tests/test_persistence.py`](../../../../../../workmate-agent/tests/test_persistence.py)
- Fixture/입력: 자연어 요청, Task 조회, 미존재 Task, Terminal 취소 요청
- 기대 결과: 전체 22개 테스트 PASS

## 7. 실행 명령과 결과

```powershell
cd workmate-agent
.\.venv\Scripts\python.exe -m unittest tests/test_internal_chat.py tests/test_runtime_boot.py tests/test_contract.py tests/test_persistence.py -v
git diff --check
```

- 테스트: 22/22 PASS
- `git diff --check`: PASS
- 미실행·경고·보류·차단: 없음
- 실행 후 생성된 Contract Test용 `.runtime/a2a.sqlite3`는 삭제했으며 커밋하지 않았다.

## 8. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| 실행 결과의 Task 영속 저장 | PASS | `tests/test_internal_chat.py`, `tests/test_persistence.py` |
| Task Snapshot 조회·Polling | PASS | `tests/test_internal_chat.py` |
| 미존재 Task 404 | PASS | `tests/test_internal_chat.py` |
| Terminal Task 취소 409 | PASS | `tests/test_internal_chat.py` |
| A2A·Store 회귀 | PASS | `tests/test_runtime_boot.py`, `tests/test_contract.py`, `tests/test_persistence.py` |
| 변경 범위 diff 검사 | PASS | 실행 ID `20260813-150133` |

## 9. 문제와 수정 이력

- 발견된 문제: 없음
- 원인: 해당 없음
- 수정 내용: 해당 없음
- 재검수 실행 ID: 해당 없음

## 10. 최종 판단

- 승인 여부: 승인 — 자동 승인(검증 명령)
- 검수 의견: 정의된 M0.3-03 검증 명령과 완료 기준이 모두 정확히 PASS하여 자동 승인했다. 실제 업무 Workflow의 장기 실행 구간은 M1~M4 연결 시 적용한다.
- 다음 조치: M0.3-04 인증·Schema·부분 실패

