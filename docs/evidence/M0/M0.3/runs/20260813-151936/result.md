# M0.3-04 검수 결과

## 1. 기본 정보

- 마일스톤: M0.3 내부 챗봇 API
- 제목: 인증·Schema·사용자 범위·부분 실패 경계
- 담당자: Codex
- 검수자: 미정
- 상태: 검수 중
- 실행일: 2026-08-13 15:19 Asia/Seoul
- 실행 ID: `20260813-151936`
- 코드 버전: `workmate-agent` `9a9bb55`
- 입력 데이터 버전: 승인된 Skill Schema `docs/schemas/workmate-skill-schemas.schema.json`

## 2. 최신 실행과 승인

- latest_run_id: `20260813-151936`
- latest_run_status: PASS (로컬 검증)
- latest_approved_run_id: `20260813-150133`
- approved_at: 2026-08-13 15:01 Asia/Seoul
- reviewer: 자동 승인(검증 명령) — M0.3-03

운영 OIDC issuer·audience·JWKS를 사용한 실제 토큰 검증은 환경 미설정으로 실행하지 않았다. 따라서 이 실행은 인증 설계·로컬 개발 인증·Schema·권한 범위의 검수 중 결과이며 M0.3-04의 자동 승인은 보류한다.

## 3. 구현 요약

- 내부 Skill API의 `skills`, 메시지, Task 조회·취소 경계에 인증 Dependency를 추가했다.
- 운영 요청은 OIDC JWT의 `sub`를 사용자 범위로 사용하고, Bearer Token 누락·잘못된 토큰·OIDC 설정 누락을 401/503으로 구분한다.
- 테스트 전용 `WORKMATE_INTERNAL_CHAT_DEV_AUTH`는 명시적으로 켠 경우에만 사용할 수 있으며 운영 인증을 대체하지 않는다.
- JSON 입력은 승인된 Draft 2020-12 Skill Schema로 검증하고, 요청의 `user_id`가 인증 주체와 다르면 403으로 거부한다.
- 영속 Task Store 조회·저장에 인증 사용자 Context를 전달해 다른 사용자의 Task가 노출되지 않도록 했다.
- Workflow 결과의 `warnings` 필드는 기존 공통 결과 경계를 그대로 응답에 보존한다. 실제 Provider 부분 실패 생성은 M1~M4 Workflow 구현 범위에서 검증한다.

## 4. 구현 경로

- [내부 챗봇 인증·Schema Route](../../../../../../workmate-agent/app/internal_chat.py)
- [의존성 원장](../../../../../../workmate-agent/pyproject.toml)
- [lockfile](../../../../../../workmate-agent/uv.lock)
- [내부 API 테스트](../../../../../../workmate-agent/tests/test_internal_chat.py)

## 5. 실행 명령과 결과

```text
$env:WORKMATE_INTERNAL_CHAT_ENABLED='true'
$env:WORKMATE_INTERNAL_CHAT_DEV_AUTH='true'
$env:WORKMATE_INTERNAL_CHAT_DEV_USER_ID='contract-user'
.venv\Scripts\python.exe -m unittest tests/test_internal_chat.py tests/test_persistence.py tests/test_contract.py
.venv\Scripts\python.exe -m compileall -q app
git diff --check
```

- 단위·통합·계약 테스트: **PASS (22건)**
- Python 구문 검사: **PASS**
- `git diff --check`: **PASS**
- 포함 검증: 인증 누락 401, 사용자 범위 불일치 403, 다른 사용자 Task 404, 승인 Schema JSON, 자연어 입력, 5개 Skill 목록
- 실행 로그: 테스트 출력에 SDK DeprecationWarning이 있으나 검증 결과를 실패시키지 않았고, Secret·Token 값은 출력하지 않았다.

## 6. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| 인증 Dependency와 Bearer 누락 거부 | PASS (로컬) | `tests/test_internal_chat.py` |
| 요청 `user_id`와 인증 주체 일치 검증 | PASS | `tests/test_internal_chat.py` |
| Task 조회의 사용자 범위 적용 | PASS | `tests/test_internal_chat.py`, `app/a2a/persistence.py` |
| 승인 Skill Schema JSON 검증 | PASS | `tests/test_internal_chat.py`, `docs/schemas/workmate-skill-schemas.schema.json` |
| 운영 OIDC issuer/JWKS 실제 토큰 검증 | 미실행 | OIDC 환경과 테스트 키 미설정 |
| 실제 Provider 부분 실패 생성·복구 | 미실행 | M1~M4 Workflow 구현 전 |

## 7. 문제와 수정 이력

- 발견된 문제: 운영 OIDC issuer·audience·JWKS가 현재 환경에 없어 실제 JWT 서명키 조회와 토큰 검증을 실행하지 못했다.
- 원인: M0.3은 내부 API 경계만 구현했고 운영 인증 공급자 설정은 아직 확정·주입하지 않았다.
- 수정 내용: 개발 인증을 테스트 전용으로 격리하고, 운영 경로는 OIDC 설정 없이는 503을 반환하도록 했다. 인증 사용자 Context를 Task Store에 전달했다.
- 재검수 조건: 테스트용 OIDC issuer/JWKS와 비밀을 Git에 저장하지 않는 실행 환경을 준비한 뒤 유효·만료·잘못된 서명·audience 불일치 토큰 Contract Test를 추가 실행한다.

## 8. 최종 판단

- 승인 여부: **보류(검수 중)**
- 검수 의견: 로컬 인증·Schema·권한 범위 검증은 모두 PASS지만, 운영 OIDC 검증이 미실행되어 자동 승인 조건을 충족하지 않는다.
- 다음 조치: OIDC 테스트 환경을 준비해 실제 JWT Contract Test를 실행하고, 그 결과가 정확히 PASS일 때 M0.3-04를 재검수한다. M0.4는 착수하지 않는다.
