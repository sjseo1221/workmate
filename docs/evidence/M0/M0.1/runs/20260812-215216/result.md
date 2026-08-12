# M0.1-03 구현·검수 결과

## 1. 기본 정보

- 마일스톤: M0.1 A2A·Artifact 계약
- 백로그: M0.1-03 Workflow·Task 실행 경계
- 담당자: Codex
- 검수자: 자동 검증 결과 기록, PostgreSQL 연결 검수 대기
- 상태: 검수 중
- 실행일: 2026-08-12
- 실행 ID: `20260812-215216`
- 코드 버전: `workmate-agent` `82839ac`
- 입력 데이터 버전: 해당 없음
- 작업 유형: Workflow Registry·A2A 인프라 영속 경계

## 2. 최신 실행과 승인

- latest_run_id: `20260812-215216`
- latest_run_status: PASS (SQLite·Contract·Docker), PostgreSQL 연결 보류
- latest_approved_run_id: null
- approved_at: null

## 3. 목표와 완료 기준

- 목표: SDK `AgentExecutor`와 업무 Workflow 사이에 Registry를 두고 A2A 장기 Task의 Snapshot·멱등성·Artifact·Checkpoint 영속 경계를 연결한다.
- 완료 기준: Workflow 선택, `task_id ↔ thread_id`, Message 멱등성, Artifact 저장, 재시작 복구, 취소 표시, A2A 인프라 Migration 검증.
- 백로그 범위: M0.1-03
- 미완료·보류 백로그: PostgreSQL 실제 연결·Migration 실행 검증, M0.1-04 통합 Subscribe 검수

## 4. 구현 내용과 경로

- 구현 요약: `WorkflowRegistry`가 `skill_id`를 전송 독립 `WorkflowRequest`로 연결하고, `PersistentTaskStore`가 SQLite 파일에 Task Snapshot·Message Hash·Artifact·Checkpoint를 저장한다. `DATABASE_URL`이 있으면 `PostgresTaskStore`와 M0.1 SQL Migration을 사용한다.
- 변경 전: SDK `InMemoryTaskStore`와 런타임 내부 Executor만 사용해 프로세스 재시작 시 Task·Artifact 상태가 사라지고 Workflow 선택·멱등성 저장 경계가 없었다.
- 변경 후: Runtime이 영속 Store와 Registry를 생성하고, 실행 전 최소 Task Snapshot을 저장한 뒤 Message·Checkpoint·Artifact를 기록한다. 취소 요청은 영속 상태에 먼저 표시한다.
- 핵심 코드:
  - [registry.py](../../../../../../workmate-agent/app/workflows/registry.py): `WorkflowRegistry`, `WorkflowRequest`, `WorkflowResult`
  - [persistence.py](../../../../../../workmate-agent/app/a2a/persistence.py): `PersistentTaskStore`, `PostgresTaskStore`, Message·Artifact·Checkpoint 저장
  - [runtime.py](../../../../../../workmate-agent/app/a2a/runtime.py): Registry·Store 연결과 SDK Event 변환
- 구현 코드: [runtime.py](../../../../../../workmate-agent/app/a2a/runtime.py), [persistence.py](../../../../../../workmate-agent/app/a2a/persistence.py), [registry.py](../../../../../../workmate-agent/app/workflows/registry.py)
- 의존성·문서: [pyproject.toml](../../../../../../workmate-agent/pyproject.toml), [uv.lock](../../../../../../workmate-agent/uv.lock), [README.md](../../../../../../workmate-agent/README.md)
- Schema 또는 Migration: [001_a2a_infrastructure.sql](../../../../../../workmate-agent/migrations/001_a2a_infrastructure.sql)
- Docker: [Dockerfile](../../../../../../workmate-agent/Dockerfile), [compose.yaml](../../../../../../workmate-agent/compose.yaml)
- UI 코드: 해당 없음
- 제외 범위: Gmail·Calendar·업무 Task Repository·LangGraph 공식 Checkpointer 연결·M0.1-04 전체 Subscribe 통합 검수

## 5. 테스트 파일 경로

- 단위·Persistence Test: [test_persistence.py](../../../../../../workmate-agent/tests/test_persistence.py)
- Migration Contract Test: [test_migration.py](../../../../../../workmate-agent/tests/test_migration.py)
- 기존 SDK Contract Test: [test_contract.py](../../../../../../workmate-agent/tests/test_contract.py)
- 기존 Runtime Boot Test: [test_runtime_boot.py](../../../../../../workmate-agent/tests/test_runtime_boot.py)
- Fixture/입력: 임시 SQLite DB와 SDK Task·Artifact Fixture
- 기대 결과: 전체 테스트 12개 PASS, 재생성 Store에서 Task 복원, 동일 Message Payload 멱등 처리
- 모델 평가 Case: 해당 없음
- 모델 평가 결과: 해당 없음

## 6. 실행 명령과 결과

```text
uv lock --check --cache-dir ..\.uv-cache
uv sync --frozen --cache-dir ..\.uv-cache
uv run --frozen --cache-dir ..\.uv-cache python -m unittest discover -s tests -v
uv run --frozen --cache-dir ..\.uv-cache python -m compileall -q app tests
git diff --check
docker compose up --build -d
docker compose ps --format json
Invoke-RestMethod http://localhost:8001/health/live
Invoke-RestMethod http://localhost:8001/health/ready
Invoke-RestMethod http://localhost:8001/.well-known/agent-card.json
docker compose down
```

- Lock·Sync: PASS
- 전체 단위·Contract·Persistence·Migration Test: 12개 PASS
- Compile: PASS
- Diff 검사: PASS
- Docker 이미지 빌드·컨테이너 기동: PASS
- Compose 상태: `running`, `healthy`
- Health: `alive`, `ready`
- Agent Card: `Workmate AI`, `HTTP+JSON`, protocol `1.0`, streaming `true`
- PostgreSQL 실제 연결: 보류 (`DATABASE_URL` 미설정; 로컬·Docker는 SQLite fallback으로 검증)
- 화면 캡처: 해당 없음
- 함수 문서화: 신규 공개 경계 함수와 핵심 저장 함수에 한글 Docstring 작성

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Registry가 Skill ID를 Workflow로 연결 | PASS | [registry.py](../../../../../../workmate-agent/app/workflows/registry.py), [test_persistence.py](../../../../../../workmate-agent/tests/test_persistence.py) |
| Task·Message·Artifact·Checkpoint SQLite 재시작 복구 | PASS | [persistence.py](../../../../../../workmate-agent/app/a2a/persistence.py), [test_persistence.py](../../../../../../workmate-agent/tests/test_persistence.py) |
| PostgreSQL 인프라 Migration 필수 테이블·Key 선언 | PASS | [001_a2a_infrastructure.sql](../../../../../../workmate-agent/migrations/001_a2a_infrastructure.sql), [test_migration.py](../../../../../../workmate-agent/tests/test_migration.py) |
| Docker·Health·Agent Card 회귀 | PASS | [Dockerfile](../../../../../../workmate-agent/Dockerfile), [compose.yaml](../../../../../../workmate-agent/compose.yaml) |
| PostgreSQL 실제 연결·Migration 실행 | 보류 | `DATABASE_URL` 미설정 |

## 8. 문제와 수정 이력

- 발견된 문제: 첫 실행에서 Message FK가 Task Snapshot보다 먼저 기록됐다.
- 원인: SDK EventQueue 소비 시점보다 Executor의 부가 저장 시점이 빨랐다.
- 수정 내용: Executor가 SDK 이벤트 enqueue 전에 최소 Task Snapshot을 영속 저장하도록 순서를 고정했다. SQLite 연결도 명시적으로 닫아 Windows 임시 DB 삭제 실패를 해소했다.
- 재검수 실행 ID: `20260812-215216`

## 9. 최종 판단

- 승인 여부: 보류
- 검수 의견: 로컬 영속 경계·Migration 계약·Docker 회귀는 통과했으나 PostgreSQL 실제 연결 검증과 M0.1-04 Subscribe 통합 검수가 남아 있다.
- 다음 조치: `DATABASE_URL`을 설정한 PostgreSQL Compose 검증 후 M0.1-04 통합 Contract Test 진행 여부를 사용자에게 확인
