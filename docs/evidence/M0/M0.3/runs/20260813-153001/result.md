# M0.3-04 검수 결과

## 1. 기본 정보

- 마일스톤: M0.3 내부 챗봇 API
- 제목: 운영 OIDC 인증·Schema·사용자 범위·부분 실패 경계
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13 15:30 Asia/Seoul
- 실행 ID: `20260813-153001`
- 코드 버전: `workmate-agent` `69690bc`
- 입력 데이터 버전: 승인된 Skill Schema `docs/schemas/workmate-skill-schemas.schema.json`

## 2. 최신 실행과 승인

- latest_run_id: `20260813-153001`
- latest_run_status: PASS
- latest_approved_run_id: `20260813-153001`
- approved_at: 2026-08-13 15:30 Asia/Seoul
- reviewer: 자동 승인(검증 명령)

## 3. 구현 요약

- 개발 인증 우회 경로를 제거하고 내부 API가 운영 OIDC JWT 검증 경로만 사용하도록 했다.
- 로컬 JWKS HTTP 서버와 임시 RSA 키를 테스트 Fixture로 사용해 운영 코드의 서명키 조회·JWT 검증을 실행했다.
- 유효 토큰은 JWT `sub`를 사용자 범위로 사용하고, 누락·만료·audience 불일치 토큰은 401로 거부한다.
- JSON 입력은 승인된 Draft 2020-12 Skill Schema로 검증하고, 요청 `user_id`가 인증 주체와 다르면 403으로 거부한다.
- Task Store Context에 인증 사용자를 전달해 다른 사용자의 Task 조회를 404로 차단한다.
- Workflow의 부분 실패 `warnings`를 결과 응답에 보존하는 계약을 검증했다.

## 4. 구현 경로

- [내부 챗봇 OIDC 인증·Schema Route](../../../../../../workmate-agent/app/internal_chat.py)
- [운영 OIDC·JWKS Contract Test](../../../../../../workmate-agent/tests/test_internal_chat.py)
- [의존성 원장](../../../../../../workmate-agent/pyproject.toml)
- [lockfile](../../../../../../workmate-agent/uv.lock)

## 5. 실행 명령과 결과

```text
$env:WORKMATE_INTERNAL_CHAT_ENABLED='true'
$env:WORKMATE_OIDC_ISSUER='https://issuer.test'
$env:WORKMATE_OIDC_AUDIENCE='workmate-internal'
$env:WORKMATE_OIDC_JWKS_URL='http://127.0.0.1:1/jwks.json'
.venv\Scripts\python.exe -m unittest tests/test_internal_chat.py tests/test_persistence.py tests/test_contract.py
.venv\Scripts\python.exe -m compileall -q app
git diff --check
```

- 단위·통합·계약 테스트: **PASS (22건)**
- Python 구문 검사: **PASS**
- `git diff --check`: **PASS**
- OIDC 테스트 범위: 유효 JWT, Bearer 누락, 만료, audience 불일치, 사용자 범위 격리
- 부분 실패 범위: `source`, `code`, `message`, `retryable` Warning 보존
- 테스트 서버는 임시 키와 로컬 JWKS만 사용했으며 Secret·Token을 파일이나 로그에 저장하지 않았다.

## 6. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| 운영 OIDC JWT 서명·issuer·audience 검증 | PASS | `tests/test_internal_chat.py` |
| Bearer 누락·만료·audience 오류 거부 | PASS | `tests/test_internal_chat.py` |
| 요청 `user_id`와 인증 주체 일치 검증 | PASS | `tests/test_internal_chat.py` |
| Task 조회의 사용자 범위 적용 | PASS | `tests/test_internal_chat.py`, `app/a2a/persistence.py` |
| 승인 Skill Schema JSON 검증 | PASS | `tests/test_internal_chat.py`, `docs/schemas/workmate-skill-schemas.schema.json` |
| Provider 부분 실패 Warning 보존 | PASS | `tests/test_internal_chat.py`, `app/workflows/registry.py` |

## 7. 문제와 수정 이력

- 이전 문제: 개발 인증 환경변수에 의존해 운영 OIDC 경로를 직접 검증하지 못했다.
- 수정 내용: 개발 인증 우회 분기를 제거하고 로컬 JWKS HTTP Fixture를 통해 운영 OIDC 코드 경로를 검증했다.
- 비고: 실제 외부 IdP 연결과 Gmail·Calendar 장애 재현은 해당 Provider Workflow 마일스톤(M1~M4)에서 별도로 검증한다.

## 8. 최종 판단

- 승인 여부: **승인 — 자동 승인(검증 명령)**
- 검수 의견: 정의된 검증 명령과 검수 항목이 모두 정확히 PASS했고 미실행 항목이 없어 M0.3-04를 완료 처리한다.
- 다음 조치: 자동 진행 규칙에 따라 M0.4-01 입력 UI를 착수한다. UI 육안 검수는 별도 승인 대상으로 유지한다.
