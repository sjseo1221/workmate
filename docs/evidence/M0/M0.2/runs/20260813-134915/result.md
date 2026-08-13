# M0.2-04 재검수 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: Gmail OAuth 실제 API·Watch 전용 재검수
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-134915
- 코드 버전: `ac0b91c`
- 입력 데이터 버전: 사용자 로컬 OAuth 계정의 비식별 실행 결과

## 2. 최신 실행과 승인

- latest_run_id: 20260813-134915
- latest_run_status: PASS
- latest_approved_run_id: 20260813-134915
- approved_at: 2026-08-13 13:49 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: Gmail readonly Scope, Profile·Message·History 조회, Gmail Watch 등록을 실제 사용자 로컬 실행으로 검증한다.
- 완료 기준:
  - `https://www.googleapis.com/auth/gmail.readonly` Scope 유지
  - Gmail profile/messages/history 검사 모두 `pass`
  - `--watch` 실행에서 Gmail Watch 검사와 `history_id`·`expiration` 존재 여부가 `pass`
  - 설정·단위 테스트·구문 검사·문서 diff가 모두 성공
  - Secret·Token·메일 원문을 증빙에 저장하지 않음
- 백로그 범위: M0.2-04
- 미완료 백로그: 없음

## 4. 구현·검증 경로

- 구현 코드: [`auth_flow.py`](../../../../../../google-oauth-test/auth_flow.py), [`smoke_test.py`](../../../../../../google-oauth-test/smoke_test.py)
- 단위 테스트: [`test_config.py`](../../../../../../google-oauth-test/tests/test_config.py)
- 실행 안내: [`README.md`](../../../../../../google-oauth-test/README.md)
- 기존 성공 이력: [`HISTORY.md`](../../../../../../google-oauth-test/HISTORY.md)
- Schema·Migration·UI: 해당 없음

`smoke_test.py`는 `AuthorizedSession`과 Gmail REST endpoint를 사용한다. 기본 실행은 profile·messages·history를 확인하고 `--watch`는 Gmail Watch를 추가 확인한다. 증빙에는 응답 원문 대신 검사 상태·개수·필드 존재 여부만 기록한다.

## 5. 실행 명령과 결과

결정적 로컬 검증:

```text
cd C:\dev\workmate\google-oauth-test
venv\Scripts\python.exe -m unittest discover -s tests -v
venv\Scripts\python.exe -m py_compile auth_flow.py smoke_test.py
git diff --check
```

- 단위 테스트 3개: `PASS`
- Python 구문 검사: `PASS`
- `git diff --check`: `PASS`

사용자가 제공한 실제 로컬 OAuth 실행:

```text
venv\Scripts\python.exe smoke_test.py
venv\Scripts\python.exe smoke_test.py --watch
```

- 기본 실행: Gmail profile/messages/history 모두 `pass`, message count 1, history ID·history page 존재
- Watch 실행: 위 항목과 Gmail Watch 모두 `pass`, history ID·expiration 존재
- 미실행·경고·수동 검수·차단 항목: 없음

## 6. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Gmail readonly Scope | PASS | `auth_flow.py`, `test_config.py` |
| AuthorizedSession 전송 | PASS | `test_config.py` |
| Gmail profile/messages/history | PASS | 사용자 로컬 `smoke_test.py` 결과 |
| Gmail Watch·history ID·expiration | PASS | 사용자 로컬 `smoke_test.py --watch` 결과 |
| 설정·Secret 제외 규칙 | PASS | `README.md` 및 결과 비식별화 |
| 단위 테스트 3개 | PASS | `python -m unittest discover -s tests -v` |
| 구문 검사 | PASS | `python -m py_compile auth_flow.py smoke_test.py` |
| 문서 diff 검사 | PASS | `git diff --check` |

## 7. 문제와 수정 이력

- 이전 M0.2-04 결과는 Gmail 실제 API 재현을 기존 HISTORY와 사용자 승인으로 기록했다.
- 이번 실행에서는 사용자가 제공한 동일 OAuth 하네스의 실제 로컬 결과에서 Gmail profile/messages/history와 Watch가 모두 `pass`임을 Gmail 전용 증빙으로 분리했다.
- 이전 실행 [`20260813-122007`](../20260813-122007/result.md)은 원본 결과로 보존한다.

## 8. 최종 판단

- 승인 여부: 승인
- 검수 의견: Gmail Scope·실제 조회·Watch·로컬 검증 명령이 모두 정확히 `PASS`이므로 자동 승인 조건을 충족했다.
- 다음 조치: M0.2 통합 재검수
