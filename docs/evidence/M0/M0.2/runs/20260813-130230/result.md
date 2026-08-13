# M0.2-05 재검수 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: Calendar OAuth HTTP 전송 경로 재검수
- 담당자: Codex
- 검수자: 자동 승인 불가
- 상태: 재작업
- 실행일: 2026-08-13
- 실행 ID: 20260813-130230
- 코드 버전: `469e364`
- 입력 데이터 버전: Gmail·Calendar readonly API 및 Watch Fake

## 2. 최신 실행과 승인

- latest_run_id: 20260813-130230
- latest_run_status: FAIL
- latest_approved_run_id: 20260813-122321
- approved_at: 2026-08-13 12:27 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: `httplib2` IPv6 fallback 실패를 제거하고 Gmail·Calendar OAuth API를 재현한다.
- 완료 기준: 모든 회귀 테스트와 실제 OAuth·Gmail·Calendar·Watch 검증이 정확히 `PASS`다.
- 백로그 범위: M0.2-05 재검수
- 미완료·보류 백로그: 실제 OAuth API 재검증 timeout, Watch 미실행

## 4. 구현 경로

- 구현 코드: [`smoke_test.py`](../../../../../../google-oauth-test/smoke_test.py)
- 의존성: [`requirements.txt`](../../../../../../google-oauth-test/requirements.txt)
- Schema 또는 Migration: 해당 없음
- UI 코드: 해당 없음

### 구현 요약

- 변경 전: `google-api-python-client`가 `httplib2`로 Google API에 연결했으며 IPv6 timeout 뒤 IPv4로 fallback하지 못했다.
- 변경 후: `google.auth.transport.requests.AuthorizedSession`으로 Gmail·Calendar REST endpoint를 호출한다.
- 핵심 함수: `request_json`, `run`
- 제외 범위: 실제 Workmate M1.2 Adapter 구현, 시스템 IPv6 설정 변경, `site-packages` 수정, 전역 socket monkeypatch

## 5. 테스트 파일 경로

- 단위 테스트: [`test_config.py`](../../../../../../google-oauth-test/tests/test_config.py)
- 통합 테스트: [`smoke_test.py`](../../../../../../google-oauth-test/smoke_test.py)
- UI 테스트: 해당 없음
- Fixture/입력: OAuth 환경 설정과 Fake REST 응답
- 기대 결과: readonly·Watch REST 호출 및 실제 Provider 검증 PASS
- 모델 평가 Case: 해당 없음
- 모델 평가 결과: 해당 없음

## 6. 실행 명령과 결과

```text
cd C:\dev\workmate\google-oauth-test
venv\Scripts\python.exe -m unittest discover -s tests -v
venv\Scripts\python.exe smoke_test.py --dry-run
venv\Scripts\python.exe -m py_compile auth_flow.py smoke_test.py tests\test_config.py
venv\Scripts\python.exe smoke_test.py
git diff --check
```

- 회귀 테스트: 3건 PASS
- dry-run: PASS
- Python 구문 검사: PASS
- `git diff --check`: PASS
- 실제 OAuth API: Codex 관리형 실행 환경에서 120초 timeout으로 FAIL
- Watch: 실제 OAuth API 실패로 미실행
- 사용자 로컬 진단: `requests` HTTP 401, `httplib2` timeout, IPv4 제한 `httplib2` HTTP 401
- Secret·Token·메일·일정 원문: 출력하거나 증빙에 저장하지 않음

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| `AuthorizedSession` REST 전송 전환 | PASS | [`smoke_test.py`](../../../../../../google-oauth-test/smoke_test.py) |
| readonly·Watch Fake 회귀 테스트 | PASS (3건) | [`test_config.py`](../../../../../../google-oauth-test/tests/test_config.py) |
| dry-run·구문 검사 | PASS | 실행 `20260813-130230` |
| 실제 OAuth·Gmail·Calendar 조회 | FAIL (timeout) | 실행 `20260813-130230` |
| 실제 Gmail·Calendar Watch | 미실행 | 선행 실제 OAuth 조회 실패 |

## 8. 문제와 수정 이력

- 발견된 문제: `httplib2`만 Gmail API 연결 timeout이 발생했다.
- 원인: IPv6 연결 timeout 후 IPv4 주소로 fallback하지 않는 `httplib2` 전송 동작이다. 사용자 로컬에서 IPv4 제한 시 HTTP 401을 받아 확인했다.
- 수정 내용: 테스트 하네스를 `AuthorizedSession` 기반 REST 호출로 변경하고 `httplib2` 의존성을 제거했다.
- 남은 문제: Codex 관리형 실행 환경에서는 수정 후 실제 API 호출도 timeout이므로 사용자 로컬에서 실제 OAuth와 Watch를 재실행해야 한다.
- 재검수 실행 ID: 다음 사용자 로컬 실제 API 실행 결과로 생성

## 9. 최종 판단

- 승인 여부: 미승인
- 검수 의견: 코드·회귀 테스트는 통과했지만 실제 API FAIL과 Watch 미실행이 있어 자동 승인 조건을 충족하지 않는다.
- 다음 조치: 사용자 로컬에서 `smoke_test.py`와 `smoke_test.py --watch`를 실행하고 모든 항목이 PASS일 때 새 실행을 승인한다.
