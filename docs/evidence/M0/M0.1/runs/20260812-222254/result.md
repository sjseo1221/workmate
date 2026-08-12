# M0.1-03 검수 결과

## 1. 기본 정보

- 마일스톤: M0.1
- 제목: Workflow·영속 Task 경계
- 담당자: Codex
- 검수자: 미정
- 상태: 검수 중
- 실행일: 2026-08-12
- 실행 ID: `20260812-222254`
- 코드 버전: `workmate-agent@85a4036`
- 입력 데이터 버전: 테스트 Fixture

## 2. 최신 실행과 승인

- latest_run_id: `20260812-222254`
- latest_run_status: 부분 PASS (로컬 테스트 PASS, PostgreSQL·최종 Docker 재검증 보류)
- latest_approved_run_id: `null`
- approved_at: `null`

## 3. 목표와 완료 기준

- 목표: Registry, A2A Task·Message·Artifact·Checkpoint의 영속 경계를 SQLite와 PostgreSQL Adapter로 제공한다.
- 완료 기준: Migration·Task Snapshot·Message 멱등성·Checkpoint 경계를 검증하고, 최종 이미지에 Migration 파일이 포함된 상태로 기동한다.
- 백로그 범위: `M0.1-03`
- 미완료·보류 백로그: 실제 `DATABASE_URL` 연결 검증, 최종 Dockerfile 재빌드·Health·Agent Card 재검증

## 4. 구현 경로

- 구현 코드: [`app/workflows/registry.py`](../../../../../../workmate-agent/app/workflows/registry.py), [`app/a2a/persistence.py`](../../../../../../workmate-agent/app/a2a/persistence.py), [`app/a2a/runtime.py`](../../../../../../workmate-agent/app/a2a/runtime.py)
- Schema 또는 Migration: [`migrations/001_a2a_infrastructure.sql`](../../../../../../workmate-agent/migrations/001_a2a_infrastructure.sql)
- Docker: [`Dockerfile`](../../../../../../workmate-agent/Dockerfile)
- 테스트: [`tests/test_persistence.py`](../../../../../../workmate-agent/tests/test_persistence.py), [`tests/test_migration.py`](../../../../../../workmate-agent/tests/test_migration.py), [`tests/test_postgres_integration.py`](../../../../../../workmate-agent/tests/test_postgres_integration.py)

## 5. 구현 요약

- `WorkflowRegistry`가 공개 Skill 식별자와 실제 업무 Workflow 연결 지점을 관리한다.
- `PersistentTaskStore`가 SQLite 파일에 Task·Message·Artifact·Checkpoint Snapshot을 저장하고 재시작 후 복구한다.
- `PostgresTaskStore`가 동일 계약으로 PostgreSQL Migration을 최초 연결 시 적용한다.
- Message ID와 요청 Hash를 저장해 동일 요청은 멱등 처리하고, 같은 ID의 다른 Payload는 거부한다.
- Dockerfile이 `migrations/`를 이미지에 복사하도록 보강했다.
- 실제 Gmail·Calendar·업무 DB·LLM Workflow는 M1 이후 범위이며 이 작업에서 Mock 업무 응답을 운영 경로에 추가하지 않았다.

## 6. 테스트 파일 경로와 실행 결과

```text
uv lock --check --cache-dir ..\\.uv-cache
uv sync --frozen --cache-dir ..\\.uv-cache
uv run --frozen --cache-dir ..\\.uv-cache python -m unittest discover -s tests -v
uv run --frozen --cache-dir ..\\.uv-cache python -m compileall -q app tests
git diff --check
```

- 결과: 13개 테스트 중 12 PASS, PostgreSQL 통합 테스트 1개는 `DATABASE_URL` 미설정으로 SKIP
- Lock·sync·compile·diff 검사: PASS
- PostgreSQL 통합 테스트: 테스트 파일과 실행 경계는 추가했으나 테스트용 컨테이너 실행이 Docker daemon 응답 지연으로 완료되지 않아 미실행
- 최종 Dockerfile 재빌드: `docker compose build --progress plain`이 Docker daemon 응답 지연으로 시간 초과되어 미완료
- 기존 Docker Compose Health·Agent Card 검증: 이전 실행 `20260812-215216`에서 PASS했으나, `COPY migrations ./migrations` 반영 후 재검증은 보류

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| SQLite Task·Message·Artifact·Checkpoint 재시작 복구 | PASS | [`tests/test_persistence.py`](../../../../../../workmate-agent/tests/test_persistence.py) |
| A2A Infrastructure Migration 필수 테이블·키 | PASS | [`tests/test_migration.py`](../../../../../../workmate-agent/tests/test_migration.py) |
| PostgreSQL 실제 연결·Migration·Task 멱등성 | 보류 | `DATABASE_URL` 테스트 컨테이너 미기동 |
| 최종 Docker 이미지 Migration 파일 포함·Health·Agent Card | 보류 | Docker build timeout |

## 8. 문제와 수정 이력

- 발견된 문제: 현재 Docker daemon이 `docker run`과 `docker compose build` 요청에 응답하지 않아 PostgreSQL 실제 연결 및 최종 이미지 재빌드를 완료하지 못했다.
- 원인: Docker CLI/daemon 명령이 제한 시간 내 종료되지 않았으며, 테스트 컨테이너가 생성되지 않았다.
- 수정 내용: PostgreSQL 통합 테스트를 `DATABASE_URL`이 있을 때만 수행하도록 추가하고, Dockerfile에 Migration 복사 경로를 반영했다.
- 재검수 조건: Docker daemon 정상 응답 후 PostgreSQL 격리 컨테이너를 기동하고 `DATABASE_URL` 통합 테스트와 최종 Compose build·Health·Agent Card를 다시 실행한다.

## 9. 최종 판단

- 승인 여부: 보류
- 검수 의견: 로컬 영속 경계와 Migration 정적 검증은 통과했으나 실제 PostgreSQL과 최종 Docker 이미지 검증이 남아 있어 M0.1-03을 완료로 표시하지 않는다.
- 다음 조치: Docker daemon 정상화 후 PostgreSQL 연결 검증과 최종 Docker 재검증을 재실행한다.
