# M0.4-03 재검수 결과

## 1. 기본 정보

- 마일스톤: M0.4 내부 검증 UI
- 제목: Polling 재조회 Artifact metadata 보존 수정
- 담당자: Codex
- 검수자: 검수 중
- 상태: 검수 중
- 실행일: 2026-08-13
- 실행 ID: `20260813-163114`
- 코드 버전: `workmate-agent@8a6e6d5`
- 입력 데이터 버전: `weekly_report` POST→GET Task Snapshot

## 2. 최신 실행과 승인

- latest_run_id: `20260813-163114`
- latest_run_status: PASS (유효 Token 기반 통합 육안 검수 대기)
- latest_approved_run_id: `20260813-161223`
- approved_at: 2026-08-13 16:12 Asia/Seoul
- reviewer: null

## 3. 목표와 완료 기준

- 목표: Polling으로 Task Snapshot을 재조회해도 Mock·실제 업무 결과 표시가 최초 실행과 일치하도록 한다.
- 완료 기준: Artifact metadata에 `mock`·`business_result`를 저장하고 POST→GET 회귀 테스트가 PASS해야 한다.
- 백로그 범위: M0.4-03
- 미완료·보류 백로그: 유효 Token 기반 5개 Skill·Polling·취소·사용자 범위 격리 육안 검수

## 4. 구현 경로

- 구현 코드: [`internal_chat.py`](../../../../../../workmate-agent/app/internal_chat.py), [`internal_chat_ui.py`](../../../../../../workmate-agent/app/internal_chat_ui.py)
- Schema 또는 Migration: 해당 없음 (A2A Artifact 표준 metadata 사용)
- UI 테스트 코드: [`test_internal_chat_ui.py`](../../../../../../workmate-agent/tests/test_internal_chat_ui.py)

## 5. 테스트 파일 경로

- 단위·통합 테스트: [`test_internal_chat.py`](../../../../../../workmate-agent/tests/test_internal_chat.py)
- UI 테스트: [`test_internal_chat_ui.py`](../../../../../../workmate-agent/tests/test_internal_chat_ui.py)
- Fixture/입력: `weekly_report` 자연어 입력
- 기대 결과: POST와 GET 모두 `mock: true`, `business_result: false`
- 모델 평가 Case: 해당 없음
- 모델 평가 결과: 해당 없음

## 6. 실행 명령과 결과

```text
.\.venv\Scripts\python.exe -m unittest tests/test_internal_chat_ui.py tests/test_internal_chat.py tests/test_persistence.py tests/test_contract.py
.\.venv\Scripts\python.exe -m compileall -q app
git diff --check
```

- 테스트 24건: PASS
- `compileall`: PASS
- `git diff --check`: PASS
- POST 응답 Artifact metadata 보존: PASS
- GET Task Snapshot Artifact metadata 보존: PASS
- UI Polling이 `a.metadata`를 읽도록 수정: PASS
- 유효 Token 기반 5개 Skill 통합 육안 검수: 미실행

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Artifact metadata 저장 | PASS | `internal_chat.py`, 회귀 테스트 |
| POST→GET Mock 표시 일치 | PASS | `test_internal_chat.py` |
| Polling UI metadata 표시 | PASS | `internal_chat_ui.py`, `test_internal_chat_ui.py` |
| 5개 Skill 통합 육안 검수 | 미실행 | 유효 OIDC Token 필요 |
| 실제 장기 Task 취소 | 미실행 | 실제 장기 Workflow 필요 |

## 8. 문제와 수정 이력

- 발견된 문제: Polling GET 응답에서 `mock`·`business_result`가 누락되어 UI가 `Mock: 아니오`로 표시했다.
- 원인: Task에 저장한 A2A Artifact가 업무 상태 metadata를 포함하지 않았다.
- 수정 내용: Artifact 표준 `metadata`에 두 필드를 저장하고 UI가 `metadata`를 우선 읽도록 수정했다.
- 재검수 실행 ID: `20260813-163114`

## 9. 최종 판단

- 승인 여부: 미승인
- 검수 의견: POST→GET 상태 일치 문제는 해결됐고 자동 검증은 PASS다. 유효 Token 기반 통합 육안 검수 전까지 `검수 중`으로 유지한다.
- 다음 조치: 사용자 브라우저에서 5개 Skill과 실제 Task 상태 표시를 확인
