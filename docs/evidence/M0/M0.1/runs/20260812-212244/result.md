# M0.1-02 구현·Contract 재검수 결과

## 1. 기본 정보

- 마일스톤: M0.1 A2A·Artifact 계약
- 백로그: M0.1-02 공개 A2A 전송 타입 전환
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-12
- 실행 ID: `20260812-212244`
- 코드 버전: `workmate-agent` `0149b921b9c74139774f66c56a174d5b34c671f1`
- 입력 데이터 버전: 승인 Schema 현재 버전
- 작업 유형: API·A2A Contract Test

## 2. 최신 실행과 승인

- latest_run_id: `20260812-212244`
- latest_run_status: PASS (자동 승인)
- latest_approved_run_id: `20260812-212244`
- approved_at: 2026-08-12 21:22:44 +09:00

## 3. 목표와 완료 기준

- 목표: 공개 A2A 경계에서 자체 전송 형식과 Legacy Smoke Test를 제거하고 공식 SDK 타입과 승인 Schema를 기준으로 검증한다.
- 완료 기준: 5개 Skill 입력, Result Envelope·Artifact, SDK Message 전송·Streaming, Route 공개 범위 검증이 모두 PASS한다.
- 백로그 범위: M0.1-02
- 미완료·보류 백로그: 해당 없음

## 4. 구현 내용과 경로

- 구현 요약: 공식 SDK `Message`를 protobuf JSON으로 직렬화해 실제 `/a2a/message:send`와 `/a2a/message:stream` 경로에 전달하고, 승인된 Skill·Artifact Schema로 요청과 응답을 검증하는 Contract Test를 추가했다.
- 변경 전: 루트 `smoke_test.py`가 자체 작성 요청 Envelope와 Legacy 응답 필드를 기준으로 공개 경계를 검사했다. Runtime Artifact에는 승인 Schema 필수 필드인 `description`이 없었다.
- 변경 후: Legacy `smoke_test.py`를 제거하고 `tests/test_contract.py`가 공식 SDK 타입, 승인 Schema, 실제 Runtime Route를 함께 검증한다. Runtime은 `TaskArtifactUpdateEvent`와 SDK `Artifact`를 사용해 `artifact_id`, `name`, `description`, `parts`, `last_chunk`를 명시한다.
- 핵심 코드:
  - `tests/test_contract.py::_sdk_message`: SDK `Message`·`Part`를 공개 HTTP+JSON 요청으로 직렬화
  - `tests/test_contract.py::_schema_root`: Superproject `docs/schemas/` 자동 탐색 및 `WORKMATE_SCHEMA_ROOT` override
  - `PublicA2AContractTests`: 5개 Skill 입력, Result·Artifact, Streaming, Legacy·추가 Route 차단 검증
  - `app/a2a/runtime.py::RuntimeBootstrapExecutor.execute`: 승인 Schema를 충족하는 SDK Artifact 이벤트 발행
- 구현 코드: `workmate-agent/app/a2a/runtime.py`, `workmate-agent/tests/test_contract.py`
- 의존성·문서: `workmate-agent/pyproject.toml`, `workmate-agent/uv.lock`, `workmate-agent/README.md`
- 삭제 코드: `workmate-agent/smoke_test.py`
- Schema 또는 Migration: `docs/schemas/workmate-skill-schemas.schema.json`, `docs/schemas/a2a-artifact.schema.json`을 변경하지 않고 검증 기준으로 사용
- UI 코드: 해당 없음
- 제외 범위: Gmail·Calendar·PostgreSQL·LLM 업무 Workflow와 영속 Task Store는 M0.1-03 범위

### 클릭 가능한 구현·계약 경로

- [runtime.py](../../../../../../workmate-agent/app/a2a/runtime.py)
- [test_contract.py](../../../../../../workmate-agent/tests/test_contract.py)
- [test_runtime_boot.py](../../../../../../workmate-agent/tests/test_runtime_boot.py)
- [pyproject.toml](../../../../../../workmate-agent/pyproject.toml)
- [uv.lock](../../../../../../workmate-agent/uv.lock)
- [workmate-agent README](../../../../../../workmate-agent/README.md)
- [workmate-skill-schemas.schema.json](../../../../../schemas/workmate-skill-schemas.schema.json)
- [a2a-artifact.schema.json](../../../../../schemas/a2a-artifact.schema.json)

`smoke_test.py`는 삭제된 Legacy 파일이므로 링크를 만들지 않고 삭제 사실만 기록한다.

## 5. 테스트 파일 경로

- 단위·Contract Test: `workmate-agent/tests/test_contract.py`, `workmate-agent/tests/test_runtime_boot.py`
- 통합 테스트: FastAPI `TestClient`를 통한 실제 SDK Route 호출
- UI 테스트: 해당 없음
- Fixture/입력: 5개 공개 Skill의 승인 Schema 입력 Fixture
- 기대 결과: 전체 테스트 7개 PASS
- 모델 평가 Case: 해당 없음
- 모델 평가 결과: 해당 없음

### 클릭 가능한 테스트 경로

- [test_contract.py](../../../../../../workmate-agent/tests/test_contract.py)
- [test_runtime_boot.py](../../../../../../workmate-agent/tests/test_runtime_boot.py)

## 6. 실행 명령과 결과

```text
uv lock --check
uv sync --frozen
uv run --frozen python -m unittest discover -s tests -v
uv run --frozen python -m compileall -q app tests
git diff --check
```

- 의존성 Lock·Sync: PASS
- 전체 단위·Contract Test: 7개 PASS
- Compile: PASS
- Diff 검사: PASS
- API 응답 또는 Artifact: SDK Task 완료 응답과 승인 Artifact Schema 검증 PASS
- 비차단 경고: `a2a-sdk==1.1.2` 내부 protobuf 필드 검사에서 DeprecationWarning 발생. Workmate 코드 실패나 현재 완료 조건에는 영향이 없으며 SDK 업그레이드 검토 시 재확인한다.
- 함수 문서화: Contract helper와 Runtime 핵심 함수 Docstring 확인

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| 5개 Skill 입력 Schema | PASS | `workmate-agent/tests/test_contract.py` |
| Result Envelope·Artifact Schema | PASS | `workmate-agent/tests/test_contract.py` |
| SDK Message 전송·Streaming | PASS | `workmate-agent/tests/test_contract.py` |
| Legacy·비허용 Route 제거 | PASS | `workmate-agent/tests/test_contract.py` |
| Lock·Compile·Diff | PASS | 실행 ID `20260812-212244` |

## 8. 문제와 수정 이력

- 발견된 문제: 기존 승인 결과는 구현 경로와 테스트 결과만 나열해 실제 구현 동작을 파악하기 어려웠다.
- 원인: `result.md` 표준 양식에 구현 요약·변경 전후·핵심 코드 필드가 없었다.
- 수정 내용: 승인된 과거 실행을 변경하지 않고 동일 코드 버전을 재검증해 구현 내용이 포함된 새 실행 결과를 생성했다.
- 재검수 실행 ID: `20260812-212244`

## 9. 최종 판단

- 승인 여부: 자동 승인
- 검수 의견: 정의된 검증 명령이 모두 PASS했고 미실행 또는 완료 조건을 막는 항목이 없어 묵시 승인 조건을 충족함
- 다음 조치: M0.1-03 Workflow·영속 Task 경계 구현
