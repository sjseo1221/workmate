# M0.1-03 검수 결과

## 1. 기본 정보

- 마일스톤: M0.1
- 제목: Workflow·영속 Task 경계
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-12
- 실행 ID: `20260812-224743`
- 코드 버전: `workmate-agent@c17d4c2`
- 입력 데이터 버전: 테스트 Fixture

## 2. 최신 실행과 승인

- latest_run_id: `20260812-224743`
- latest_run_status: PASS
- latest_approved_run_id: `20260812-224743`
- approved_at: 2026-08-12 22:47 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: Registry, A2A Task·Message·Artifact·Checkpoint의 영속 경계를 SQLite와 PostgreSQL Adapter로 제공한다.
- 완료 기준: Migration·Task Snapshot·Message 멱등성·Checkpoint 경계를 검증하고, Migration 파일이 포함된 최종 Docker 이미지가 기동되어 Health·Agent Card를 제공한다.
- 백로그 범위: `M0.1-03`
- 미완료·보류 백로그: 없음. M0.1-04 통합 A2A 계약 검수는 별도 백로그다.

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
- Dockerfile이 `migrations/`를 이미지에 복사하며 최종 이미지에서도 파일 존재를 확인했다.
- 실제 Gmail·Calendar·업무 DB·LLM Workflow는 M1 이후 범위이며 이 작업에서 Mock 업무 응답을 운영 경로에 추가하지 않았다.

## 6. 실행 명령과 결과

```text
uv lock --check --cache-dir ..\\.uv-cache
uv sync --frozen --cache-dir ..\\.uv-cache
uv run --frozen --cache-dir ..\\.uv-cache python -m unittest discover -s tests -v
uv run --frozen --cache-dir ..\\.uv-cache python -m compileall -q app tests
git diff --check
```

- 로컬 결과: 13개 테스트 중 12 PASS, PostgreSQL 테스트는 `DATABASE_URL` 미설정 기본 실행에서 SKIP
- PostgreSQL 실제 통합 결과: `DATABASE_URL`을 격리 PostgreSQL 16.14 컨테이너에 연결해 Migration·Task 저장·조회·Message 멱등성·삭제 PASS
- Lock·sync·compile·diff 검사: PASS
- 최종 Docker build: PASS (`docker compose build --progress plain`)
- 최종 이미지 Migration 파일: PASS (`/app/migrations/001_a2a_infrastructure.sql` 존재)
- 최종 Docker 기동: 컨테이너 `healthy`
- Health: `/health/live=alive`, `/health/ready=ready`
- Agent Card: `Workmate AI`, `HTTP+JSON`, protocol `1.0`, streaming `true`, Skill 5개
- 사용한 테스트 PostgreSQL 이미지는 `pgvector/pgvector:pg16`(PostgreSQL 16.14)이며 테스트 종료 후 컨테이너를 제거했다.

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| SQLite Task·Message·Artifact·Checkpoint 재시작 복구 | PASS | [`tests/test_persistence.py`](../../../../../../workmate-agent/tests/test_persistence.py) |
| A2A Infrastructure Migration 필수 테이블·키 | PASS | [`tests/test_migration.py`](../../../../../../workmate-agent/tests/test_migration.py) |
| PostgreSQL 실제 연결·Migration·Task 멱등성 | PASS | [`tests/test_postgres_integration.py`](../../../../../../workmate-agent/tests/test_postgres_integration.py), 실행 ID `20260812-224743` |
| 최종 Docker 이미지 Migration·Health·Agent Card | PASS | Docker build/compose 실행 로그, 실행 ID `20260812-224743` |

## 8. 문제와 수정 이력

- 발견된 문제: Windows 기본 `ProactorEventLoop`는 psycopg async 연결을 지원하지 않았다.
- 원인: psycopg가 Windows에서 Selector 이벤트 루프를 요구한다.
- 수정 내용: PostgreSQL 통합 테스트 실행 시 Windows `WindowsSelectorEventLoopPolicy`를 명시했다. 운영 이미지는 Linux 환경으로 실행된다.
- 재검수 실행 ID: `20260812-224743`

## 9. 최종 판단

- 승인 여부: 자동 승인(검증 명령)
- 검수 의견: M0.1-03의 Registry·영속 Task 경계, PostgreSQL Migration·멱등성, 최종 Docker 이미지 검증을 모두 통과했다.
- 다음 조치: M0.1-04 통합 A2A 계약 검수를 시작한다.
