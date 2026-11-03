# W4-12 — 참조 자료

> [30-4-w4-root-graph.md](30-4-w4-root-graph.md) §12의 상세 문서.

"무엇을 참조하는가"가 아니라 **"어디를 왜 읽는가"** 를 기록한다.

## 1. 설계 근거 문서

### 96-workmate-langgraph-target-architecture.md

W4 설계의 1차 출처다. **§4가 Root Graph의 설계도**다.

| 절 | 읽는 이유 | 대응 |
| --- | --- | --- |
| §1 전체 LangGraph 구조 | Root Graph와 전송 계층의 경계 | 범위 정의 |
| §4 Root StateGraph 정의 | **노드 목록과 Edge 구성의 원본** | W4-R1, 전체 설계 |
| §7 Task 상태와 Checkpoint | `task_id ↔ thread_id` 매핑, 멱등성 Store의 위치 | W4-R2, R8 |
| §9 영속 실행 시퀀스 | 멱등성 조회 → Task 저장 → Graph 실행 순서 | W4-R2 |
| §10 구현 경계 | Root Graph가 "SQL과 Provider 세부 구현은 하지 않는다" | W4-R9 |
| §11-2 | 식별자 보존 | W4-R4 |
| §11-9 | "승인된 Schema를 통과한 뒤에만 COMPLETED" | W4-R3 |

**§4의 의사 코드를 그대로 따르되**, 실제 구현에서는 조건부 Edge의 path map·`Command` 반환·Subgraph
입출력 Adapter·오류 Edge를 추가해야 한다(96번 §4 마지막 문단이 이를 명시한다).

### 02-a2a-interface.md

| 읽는 이유 |
| --- |
| 멱등성 계약의 정의 — W4-R2가 구현하려는 대상 |
| Task 상태 값과 전이 |
| Artifact 구조 — `build_artifact`가 만들어야 할 형태 |
| **진행 중 중복 요청에 대한 규정이 있는지**(W4-D5 확정에 필요) |

### 30-langgraph-migration-plan.md

| 절 | 읽는 이유 |
| --- | --- |
| §0.1 전제 | "운영 중 아님 + 설계 정합성 우선" — W4-D1(동작 변경)의 근거 |
| §2.1 | 교체 대상 표 |
| §5 W4 | 단계 정의 |

## 2. 코드 참조

### 2.1 대체 대상 — 무엇을 Graph로 옮기는가

| 위치 | 읽는 이유 |
| --- | --- |
| [runtime.py:197-262](../workmate-agent/app/a2a/runtime.py#L197) | `RuntimeBootstrapExecutor.execute()` 전체 흐름 — Root 노드가 흡수할 대상 |
| [runtime.py:214-221](../workmate-agent/app/a2a/runtime.py#L214) | Task 저장 순서와 그 이유(주석: FK 참조) |
| [runtime.py:222-226](../workmate-agent/app/a2a/runtime.py#L222) | **`record_message()` 호출 — 반환값을 안 쓴다**(W4-D1의 근거) |
| [runtime.py:236-244](../workmate-agent/app/a2a/runtime.py#L236) | `WorkflowRequest` 구성, `thread_id = task_id` |
| [runtime.py:248-260](../workmate-agent/app/a2a/runtime.py#L248) | Artifact 저장·발행 |
| [runtime.py:289-312](../workmate-agent/app/a2a/runtime.py#L289) | **`_artifact_parts()`** — `build_artifact`가 이관할 로직. **text Part 처리를 빠뜨리지 않는다**(W4-K7) |
| [registry.py:57-100](../workmate-agent/app/workflows/registry.py#L57) | `WorkflowRegistry` — 조건부 Edge가 대체할 dict 조회 |
| [registry.py:15-17](../workmate-agent/app/workflows/registry.py#L15) | `WorkflowNotImplementedError` — W4-R7의 기존 동작 |

### 2.2 멱등성 구현

**W4-D1의 근거가 되는 조사 대상이다. 전부 읽는다.**

| 위치 | 읽는 이유 |
| --- | --- |
| [persistence.py:48-60](../workmate-agent/app/a2a/persistence.py#L48) | `a2a_messages` 테이블 스키마 — `request_hash`, `response_json` |
| [persistence.py:210-232](../workmate-agent/app/a2a/persistence.py#L210) | `record_message()` 시그니처 — `response` 인자와 `bool` 반환 |
| [persistence.py:234-257](../workmate-agent/app/a2a/persistence.py#L234) | `_record_message_sync()` — **`return False`(중복), `ValueError`(해시 불일치)** |
| [persistence.py:451-480](../workmate-agent/app/a2a/persistence.py#L451) | Postgres 구현 — 같은 로직 |
| [internal_chat.py:266-272](../workmate-agent/app/internal_chat.py#L266) | UI REST의 `message_id = f"internal-{task_id}"` — **매번 다르다** |
| [test_persistence.py:38-42](../workmate-agent/tests/test_persistence.py#L38) | 중복 호출 테스트가 반환값을 확인하는지 |
| [test_persistence.py:85-88](../workmate-agent/tests/test_persistence.py#L85) | 해시 불일치 `ValueError` 테스트 |

### 2.3 Schema 검증

| 위치 | 읽는 이유 |
| --- | --- |
| [internal_chat.py:59-73](../workmate-agent/app/internal_chat.py#L59) | **`_schema_validator()`** — Schema 로딩 방식. W4-D2가 재사용할 대상 |
| [test_priority_workflow.py:70-85](../workmate-agent/tests/test_priority_workflow.py#L70) | 검증 방식(envelope 구조: `schema_version`·`request_id`·`generated_at`·`data_freshness`·`warnings`·`result`) |
| `docs/schemas/workmate-skill-schemas.schema.json` | 검증 Schema 본체 |

**커밋 `62f38c5`의 메시지도 읽는다** — "vendor docs/schemas + bake into Docker image so
schema-validated skill chat works standalone". W4-K8의 배경이다.

### 2.4 Task Store

| 위치 | 읽는 이유 |
| --- | --- |
| [persistence.py:98-322](../workmate-agent/app/a2a/persistence.py#L98) | `PersistentTaskStore` — `persist_result`가 호출할 인터페이스 |
| [persistence.py:259-280](../workmate-agent/app/a2a/persistence.py#L259) | `save_artifact()` |
| [runtime.py:402-414](../workmate-agent/app/a2a/runtime.py#L402) | `build_task_store()` — 백엔드 선택 |

### 2.5 Skill 목록

| 위치 | 읽는 이유 |
| --- | --- |
| [runtime.py:66-82](../workmate-agent/app/a2a/runtime.py#L66) | `_SKILLS` — path map의 키가 될 11개 |
| [runtime.py:353-388](../workmate-agent/app/a2a/runtime.py#L353) | 현재 등록 목록(12개 = 11 + `runtime_bootstrap`) |
| [runtime.py:356-366](../workmate-agent/app/a2a/runtime.py#L356) | `runtime_workflow` — W4-D3의 대상 |

## 3. 이전 회귀 기록

W4에서 재발하면 안 되는 문제들이다. **HANDOFF.md의 해당 항목을 읽는다.**

| 회귀 | 시점 | W4에서의 관련 |
| --- | --- | --- |
| 구조화 `data`만 있는 결과에서 `text` Part 생략 → Orchestrator가 결과 못 읽음 | 2026-08-14 | W4-K7, `build_artifact` |
| Schema 파일을 Docker 이미지에서 못 찾음 | 커밋 `62f38c5` | W4-K8, `validate_contract` |
| `WorkflowResult.data`가 비면 프론트가 `null`만 읽음 | 2026-08-16 | `build_artifact`가 `data`를 보존하는지 |

## 4. 개발 규칙

### AGENTS.md

| 규칙 | W4에서의 적용 |
| --- | --- |
| 장기 Task의 원장은 영속 Task Store로 유지 | W4-R5 |
| 프로세스 메모리 상태만으로 완료·복구를 판정하지 않음 | 동상 |
| FastAPI Route에 업무 규칙을 직접 작성하지 않음 | W4-R9(같은 취지를 Root 노드에 적용) |
| 공식 SDK가 제공하는 Route를 전부 공개하지 않음 | W4 범위 밖이지만 W5에서 확인 |
| 모든 조회에 `user_id` 조건 적용 | W4-V1-13(주입 경로) |
| 사용자 승인 없이 데이터 모델·공개 A2A Schema 변경 금지 | W4-D1이 Schema는 안 바꾸지만 동작을 바꾼다 — [30-4-9](30-4-9-exit-criteria.md) §3.2 |

## 5. 선후 단계 문서

| 문서 | W4와의 관계 |
| --- | --- |
| [30-2](30-2-w2-graph-foundation.md) | State·어댑터·Checkpointer 제공 |
| [30-2-5](30-2-5-design.md) §4.3 | 저장소 책임 경계표 |
| [30-3](30-3-w3-skill-subgraphs.md) | 합성 대상 Subgraph 11개 |
| [30-3-5](30-3-5-design.md) §4 | Subgraph 주입 인터페이스(W3-D2) |
| [30-1-12](30-1-12-handoff.md) | 스냅샷의 Root 경유 대조 |
| [30-5](30-5-w5-entrypoint-swap.md) | `build_workmate_graph()`의 소비자 |
| [30-5](30-5-w5-entrypoint-swap.md) | **UI REST `message_id` 문제**를 넘겨받는다 |
| [30-6](30-6-w6-interrupt-resume.md) | Checkpointer 결합이 전제 |
| [30-9](30-9-w9-docs-evidence.md) | 동작 변경 3건의 분류 |

## 6. 외부 문서

| 자료 | 확인할 내용 |
| --- | --- |
| LangGraph — 조건부 Edge | `add_conditional_edges`의 `path_map` 인자, 분기 함수 시그니처 |
| LangGraph — Subgraph | 컴파일된 Graph를 노드로 추가하는 방법, State 공유 규칙 |
| LangGraph — Checkpointer 결합 | `compile(checkpointer=...)`, `config={"configurable": {"thread_id": ...}}` |
| jsonschema | `Draft202012Validator`, `FormatChecker` — 기존 테스트가 쓰는 방식 |

## 7. 이 문서 묶음

| 문서 | 대응 절 |
| --- | --- |
| [30-4-1](30-4-1-document-info.md) | §1 문서 정보·용어·노드 목록 |
| [30-4-2](30-4-2-scope.md) | §2 목적, 대체 대상, 범위 |
| [30-4-3](30-4-3-entry-criteria.md) | §3 선행 조건 |
| [30-4-4](30-4-4-requirements.md) | §4 요구사항 W4-R1~R10 |
| [30-4-5](30-4-5-design.md) | §5 설계 — **멱등성 조사**, 라우팅, Schema, 주입, 결정 W4-D1~D5 |
| [30-4-6](30-4-6-wbs.md) | §6 작업 분해 W4-T0~T9 |
| [30-4-7](30-4-7-verification.md) | §7 검증 설계 W4-V1~V9 |
| [30-4-8](30-4-8-traceability.md) | §8 추적성, 노드×요구사항, **동작 변경 추적** |
| [30-4-9](30-4-9-exit-criteria.md) | §9 완료 정의, 승인 경계 |
| [30-4-10](30-4-10-risks.md) | §10 위험 등록부 W4-K1~K9 |
| [30-4-11](30-4-11-rollback.md) | §11 롤백·중단·재개 |
| [30-4-12](30-4-12-references.md) | §12 참조 (이 문서) |
