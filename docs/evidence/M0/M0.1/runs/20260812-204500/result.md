# M0.1-02 실행 결과

## 기본 정보

- 마일스톤: M0.1 A2A·Artifact 계약
- 백로그: M0.1-02 공개 A2A 전송 타입 전환
- 상태: 검수 중
- 실행일: 2026-08-12
- 실행 ID: `20260812-204500`
- 코드 브랜치: `feat/M0.1-01-sdk-runtime`

## 구현 경로

- `workmate-agent/app/a2a/runtime.py`
- `workmate-agent/tests/test_contract.py`
- `workmate-agent/tests/test_runtime_boot.py`
- `workmate-agent/pyproject.toml`
- `workmate-agent/uv.lock`
- `workmate-agent/README.md`
- 삭제: `workmate-agent/smoke_test.py` (Legacy 요청 형식)

## 검증 명령과 결과

```text
uv lock --check --cache-dir .uv-cache
uv sync --frozen --cache-dir .uv-cache
uv run --frozen --cache-dir .uv-cache python -m unittest discover -s tests -v
uv run --frozen --cache-dir .uv-cache python -m compileall -q app tests
git diff --check
```

- 승인된 `workmate-skill-schemas.schema.json`으로 5개 Skill 입력 검증: PASS
- 승인된 `a2a-artifact.schema.json`으로 SDK 응답 Artifact 검증: PASS
- SDK `Message` protobuf 직렬화 후 `/a2a/message:send` 호출: PASS
- `/a2a/message:stream` `text/event-stream` 응답: PASS
- Legacy `app.py`·`smoke_test.py` 공개 기준 제거 확인: PASS
- SDK 외 추가 Route·Push·Task 목록 Route 차단 확인: PASS
- 전체 테스트: 7개 PASS

## 문제와 수정

- 최초 Contract Test에서 runtime Artifact의 `description` 누락을 발견했다.
- `TaskUpdater.add_artifact` 대신 SDK `TaskArtifactUpdateEvent`를 사용해 승인 Artifact Schema 필수 필드를 채웠다.

## 범위와 보류

- 실제 Gmail·Calendar·PostgreSQL·LLM Workflow는 구현하지 않았다.
- Workmate 업무 Result 생성과 영속 Task Store는 M0.1-03 이후 범위다.
- Docker Compose는 Docker daemon 미실행으로 이번 실행에서 제외했다.

## 승인

- latest_run_status: PASS (검수 대기)
- latest_approved_run_id: null
- reviewer: null
