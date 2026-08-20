# M5.3-05 Compose 통합·회귀 검수 결과

## 기본 정보

- 상태: 재작업
- 실행일: 2026-08-14
- 실행 ID: 20260814-161010
- 대상: Docker Compose 통합 스택 및 Adapter A2A endpoint

## 실행 결과

| 검수 항목 | 결과 | 근거 |
| --- | --- | --- |
| Compose 서비스 기동·health | PASS | `docker compose ... ps`: main-agent, postgres, workmate-agent, workmate-adapter running/healthy |
| Agent Card 조회 | PASS | `GET http://127.0.0.1:8012/.well-known/agent-card.json` 200 |
| A2A endpoint 경로 확인 | PASS | Agent Card의 `/a2a/v1/message:send` 확인 |
| 5개 Skill 통합 호출 | FAIL | 5개 모두 HTTP 500 |

## 실패 원인

1. 검수 입력의 `user_id=fixture-user`가 PostgreSQL UUID 컬럼과 호환되지 않아 `invalid input syntax for type uuid`가 발생했다.
2. Workmate 컨테이너에 `EMBEDDING_BASE_URL` 및 `EMBEDDING_API_KEY`가 없어 Embedding Provider 초기화가 실패했다.
3. 초기 호출은 잘못된 `/message:send`·`/a2a/message:send` 경로로 실행되어 404가 발생했으며, Agent Card 기준 `/a2a/v1/message:send`로 재실행했다.

## 재개 조건

- PostgreSQL Fixture에 등록된 유효한 UUID를 사용해 5개 Skill 요청을 재실행한다.
- Compose 환경에 승인된 Embedding Provider URL·Key를 Secret로 주입하고 Secret이 로그에 노출되지 않는지 확인한다.
- 5개 Skill 응답이 모두 HTTP 성공 및 정상 Task 상태를 반환할 때만 M5.3-05를 승인한다.

## 보안·범위

- 실제 Secret·Token·응답 원문은 저장하지 않았다.
- 이번 실행에서는 코드·Schema 변경을 하지 않았다.
- `docker-compose.smoke-8011.yml`은 8001 포트 충돌을 우회하는 로컬 임시 override이며 원격 Push 대상이 아니다.
