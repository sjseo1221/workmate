# M0.2-05 검수 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: Calendar OAuth 승인
- 담당자: Codex
- 검수자: 사용자 승인
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-122321
- 코드 버전: `e7afb01`
- 입력 데이터 버전: `google-oauth-test` 설정·OAuth 이력·readonly API 검증

## 2. 최신 실행과 승인

- latest_run_id: 20260813-122321
- latest_run_status: PASS_WITH_CAVEAT (사용자 승인)
- latest_approved_run_id: 20260813-122321
- approved_at: 2026-08-13 12:27 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: Google Calendar readonly OAuth Scope와 Events 조회 및 Calendar Watch 등록 이력을 검수한다.
- 완료 기준: readonly Scope가 유지되고, OAuth·Refresh Token 갱신·Calendar Events·Calendar Watch의 성공 이력이 민감정보 없이 확인되며 테스트 사용자 차단 여부를 기록한다.
- 백로그 범위: M0.2-05
- 미완료·보류 백로그: 없음. 현재 환경에서 실제 Google API 재실행은 네트워크 차단으로 보류됐으나 기존 성공 이력을 사용자 승인함.

## 4. 구현 경로

- 구현 코드: [`auth_flow.py`](../../../../../../google-oauth-test/auth_flow.py), [`smoke_test.py`](../../../../../../google-oauth-test/smoke_test.py)
- Schema 또는 Migration: 해당 없음
- UI 코드: 해당 없음

## 5. 테스트 파일 경로

- 단위 테스트: [`test_config.py`](../../../../../../google-oauth-test/tests/test_config.py)
- 통합 테스트: [`smoke_test.py`](../../../../../../google-oauth-test/smoke_test.py)
- UI 테스트: 해당 없음
- Fixture/입력: `.env.example`와 읽기 전용 Scope 설정
- 기대 결과: `calendar.readonly` Scope, Calendar Events 조회 PASS, Watch 응답의 `resourceId`·`expiration` 존재
- 모델 평가 Case: 해당 없음
- 모델 평가 결과: 해당 없음

## 6. 실행 명령과 결과

```text
cd C:\dev\workmate\google-oauth-test
venv\Scripts\python.exe smoke_test.py --dry-run
venv\Scripts\python.exe -m unittest discover -s tests -v
venv\Scripts\python.exe -m py_compile auth_flow.py smoke_test.py
git diff --check
```

- 실행 로그: dry-run PASS, 설정 단위 테스트 2건 PASS, Python 구문 검사 PASS, `git diff --check` PASS
- 실제 API 재실행: 동일 하네스는 Gmail 조회부터 수행하며 현재 환경의 Google API 연결이 소켓 권한 및 timeout으로 보류됨
- 기존 OAuth 이력: [`HISTORY.md`](../../../../../../google-oauth-test/HISTORY.md)에 2026-08-11 Calendar Events 조회와 Calendar Watch `resourceId`·`expiration` 등록 성공이 기록됨
- 테스트 사용자 차단 여부: 별도 차단 기록 없음. 테스트 계정 사용 원칙을 README에 기록함
- API 응답 또는 Artifact: Calendar 원문·Token·Client Secret은 기록하지 않고 필드 존재 여부만 기록
- 화면 캡처: 해당 없음
- 함수 문서화: `load_config`, `redirect_port`, `authenticate`의 설정·인증 경계를 코드에서 확인

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Calendar readonly Scope 유지 | PASS | [`auth_flow.py`](../../../../../../google-oauth-test/auth_flow.py), [`test_config.py`](../../../../../../google-oauth-test/tests/test_config.py) |
| 설정·Secret 제외 규칙 | PASS | [`README.md`](../../../../../../google-oauth-test/README.md), dry-run 결과 |
| Calendar Events 조회 | PASS (기존 성공 이력) | [`HISTORY.md`](../../../../../../google-oauth-test/HISTORY.md) |
| Calendar Watch `resourceId`·`expiration` 등록 | PASS (기존 성공 이력) | [`HISTORY.md`](../../../../../../google-oauth-test/HISTORY.md) |
| 테스트 사용자 차단 여부 기록 | PASS | [`README.md`](../../../../../../google-oauth-test/README.md) |
| 현재 환경에서 실제 API 재현 | 보류 | 실행 `20260813-122321`, 네트워크 차단 |
| 사용자 승인 | PASS | 이 결과와 `docs/06-delivery-plan.md` M0.2-05 |

## 8. 문제와 수정 이력

- 발견된 문제: 현재 환경에서 Google API 실시간 재현이 불가능하다.
- 원인: Google API 연결 시 Windows 소켓 권한 오류 또는 연결 timeout이 발생했다.
- 수정 내용: 실제 Secret·Token을 출력하지 않고 dry-run·단위 테스트·구문 검사와 기존 Calendar 성공 이력을 분리해 기록했다.
- 재검수 실행 ID: 20260813-122321 (기존 성공 이력 사용자 승인 반영)

## 9. 최종 판단

- 승인 여부: 승인
- 검수 의견: Calendar readonly Scope와 기존 Events·Watch 성공 이력을 사용자가 승인했다. 현재 환경의 외부 API 재실행 보류는 증빙에 남겼다.
- 다음 조치: M0.2 통합 검수
