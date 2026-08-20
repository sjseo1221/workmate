# M5.2-01 인증·권한 경계 검수 결과

## 기본 정보

- 실행 ID: 20260814-140210
- 상태: 재작업
- 범위: Workmate OIDC/A2A 인증과 Orchestrator 오류 경계

## 실행 결과

| 검증 | 결과 | 근거 |
| --- | --- | --- |
| Workmate 인증·권한 Contract Test | PASS | `python -m unittest tests.test_contract tests.test_internal_chat`, 19건 OK |
| Orchestrator API 인증·오류 테스트 | FAIL | 시스템 Python pytest가 `pygments` 누락으로 import 단계 중단 |
| 프로젝트 가상환경 재시도 | BLOCKED | `backend`에 `.venv`·`venv`가 없어 재실행 환경 없음 |

## 확인된 구현

- Workmate 내부 Skill API는 Bearer 누락·잘못된 JWT·만료·audience 오류를 401로 차단한다.
- 인증된 JWT의 `sub`를 사용자 범위로 사용해 Task 조회를 제한한다.
- A2A Route는 서비스 토큰과 `A2A-Version`을 검증한다.

## 중단 사유와 재개 조건

PASS가 아닌 결과가 있어 자동 승인과 다음 백로그 착수를 중단했다. Orchestrator backend 의존성을 설치하거나 프로젝트 전용 가상환경을 준비한 뒤 동일 테스트를 재실행해야 한다. Secret·공개 Schema·운영 Route는 변경하지 않았다.
