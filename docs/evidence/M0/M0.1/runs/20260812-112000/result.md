# M0.1-01 실행 결과

## 기본 정보

- 마일스톤: M0.1 A2A·Artifact 계약
- 백로그: M0.1-01 공식 A2A SDK HTTP+JSON 런타임 부트스트랩
- 상태: 검수 중
- 실행일: 2026-08-12
- 실행 ID: `20260812-112000`
- 코드 경로: `workmate-agent` 브랜치 `feat/M0.1-01-sdk-runtime`
- 입력 데이터: 없음

## 구현 경로

- `workmate-agent/app/main.py`
- `workmate-agent/app/a2a/runtime.py`
- `workmate-agent/pyproject.toml`
- `workmate-agent/uv.lock`
- `workmate-agent/Dockerfile`
- `workmate-agent/tests/test_runtime_boot.py`

## 검증 명령과 결과

```text
uv sync --frozen
uv run python -m unittest discover -s tests -v
python -m compileall -q app tests
git diff --check
```

- `a2a-sdk==1.1.2` 해석·설치: PASS
- Agent Card HTTP+JSON·Streaming 선언: PASS
- SDK REST Handler 기반 allowlist Route: PASS
- Bearer Token 및 `A2A-Version: 1.0`: PASS
- SDK `message:send` Task 응답: PASS
- Streaming Route 응답(`text/event-stream`): 수동 확인 PASS
- Docker Compose 실행: 보류 (호스트 Docker daemon 미실행)

## 범위와 보류

- 이번 실행은 공식 SDK 런타임 골격만 검증한다.
- Executor는 업무 Artifact가 아닌 런타임 부트스트랩 Artifact만 반환한다.
- Gmail·Calendar·PostgreSQL·LLM Workflow, 영속 Task Store, 승인된 Skill Artifact Contract Test는 M0.1-02 이후 범위다.
- `workmate-agent/smoke_test.py`는 Legacy Shell 요청 형식이므로 기준 테스트로 연결하지 않는다.

## 승인

- latest_run_status: PASS (검수 대기)
- latest_approved_run_id: null
- reviewer: null
