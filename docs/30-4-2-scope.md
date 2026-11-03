# W4-2 — 목적과 범위

> [30-4-w4-root-graph.md](30-4-w4-root-graph.md) §2의 상세 문서.

## 1. 목적

Skill Subgraph들을 하나의 **Root StateGraph**로 묶어, 지금 `WorkflowRegistry`와
`RuntimeBootstrapExecutor`에 흩어져 있는 공통 실행 계약을 Graph 안으로 모은다.

### 1.1 "공통 실행 계약"이란

Skill이 무엇이든 반드시 일어나는 일들이다.

| 계약 | 왜 공통인가 |
| --- | --- |
| 멱등성 | 같은 `message_id` 재요청은 Skill과 무관하게 기존 결과를 반환해야 한다 |
| 라우팅 | `skill_id`로 실행 대상을 고르는 규칙 |
| 결과 검증 | 승인된 Schema를 통과해야 `COMPLETED`가 된다 |
| Artifact 조립 | 공개 응답 형태는 Skill이 아니라 계약이 정한다 |
| 영속 | Task 상태·Artifact는 Task Store가 원장 |

이 계약이 Skill마다 흩어지면 Skill을 추가할 때마다 빠뜨릴 수 있다. Root Graph에 모으면 **구조적으로
건너뛸 수 없다.**

### 1.2 현재 상태의 문제

같은 계약을 두 진입점이 다르게 처리한다.

| 계약 | A2A 경로 | UI REST 경로 |
| --- | --- | --- |
| 멱등성 | `record_message()` 먼저 | `_persist_task()`에서 나중에 |
| Task 저장 | 실행 전 `submitted` | 동기 경로는 실행 후 |
| Artifact | `_artifact_parts()`로 Part 구성 | dict로 직접 조립 |
| 오류 매핑 | SDK 경유 | `ValueError`→422, `RuntimeError`→503 |

W4에서 Graph로 모으고, W5에서 두 진입점이 같은 Graph를 부르게 하면 이 차이가 사라진다.

## 2. 대체 대상

| 현재 | 위치 | 이후 |
| --- | --- | --- |
| `skill_id → handler` dict 조회 | [registry.py:80-90](../workmate-agent/app/workflows/registry.py#L80) | `add_conditional_edges` + path map |
| `message_id` 멱등성 확인 | [runtime.py:222-226](../workmate-agent/app/a2a/runtime.py#L222) | `idempotency_check` 노드 |
| Artifact Part 생성 | [runtime.py:289-312](../workmate-agent/app/a2a/runtime.py#L289) | `build_artifact` 노드 |
| 결과 Schema 검증 | 분산(테스트에만 존재) | `validate_contract` 노드 |
| Task 상태·Artifact 저장 | [runtime.py:248-260](../workmate-agent/app/a2a/runtime.py#L248) | `persist_result` 노드 |

### 2.1 `validate_contract`는 새로 생기는 것

다른 넷은 기존 코드를 옮기지만, **결과 Schema 검증은 현재 운영 경로에 없다.** 지금은 테스트에서만
`workmate-skill-schemas.schema.json`으로 검증한다
([test_priority_workflow.py:70-85](../workmate-agent/tests/test_priority_workflow.py#L70)).

[96번 §11-9](96-workmate-langgraph-target-architecture.md)는 "공개 결과는 승인된 Skill·Artifact
Schema를 통과한 뒤에만 `COMPLETED`가 된다"고 규정한다. W4에서 이를 운영 경로에 넣는다.

**주의:** 검증을 추가하면 지금까지 통과하던 결과가 실패할 수 있다. W4-V5에서 기존 케이스가 전부
통과하는지 먼저 확인하고, 실패하면 **Schema가 아니라 구현을 의심**한다(스냅샷이 현재 동작을 기록하고
있으므로).

## 3. 범위 내 (In scope)

| ID | 항목 | 산출물 |
| --- | --- | --- |
| S1 | Root 공통 노드 6종 | `app/graph/nodes/` |
| S2 | 조건부 Edge + path map | `root.py` |
| S3 | Skill Subgraph 11개 합성 | `root.py` |
| S4 | Subgraph 핸들 주입 | `root.py` |
| S5 | Checkpointer 결합 | `build_workmate_graph()` |
| S6 | Root Graph 단위 테스트 | `tests/test_graph_root.py` |
| S7 | Root 경유 스냅샷 재대조 | 대조 로그 |

## 4. 범위 외 (Out of scope)

| 항목 | 담당 단계 | 이유 |
| --- | --- | --- |
| FastAPI·A2A SDK 진입점 교체 | [W5](30-5-w5-entrypoint-swap.md) | Graph 완성 후 |
| `interrupt`·`INPUT_REQUIRED` | [W6](30-6-w6-interrupt-resume.md) | 확인 흐름은 W6 |
| Task Store 구조 변경 | — | 외부 원장은 유지(96번 §10) |
| Skill 로직 수정 | W3 | W4는 Subgraph를 호출만 한다 |
| `app/workflows/` 삭제 | [W7](30-7-w7-legacy-removal.md) | 비교 대상 유지 |
| 노드 RetryPolicy 적용 | [W8](30-8-w8-retry-observability.md) | |

### 4.1 Task Store를 대체하지 않는 이유

Checkpointer가 생겼으니 Task Store를 없애도 되지 않느냐는 질문이 자연스럽다. 답은 아니다.

| 저장소 | 소유 | 왜 합칠 수 없나 |
| --- | --- | --- |
| A2A Task Store | 외부 Task 상태, Artifact, `message_id` 멱등성 | 외부 클라이언트가 조회하는 원장. A2A SDK가 직접 쓴다 |
| Checkpointer | 내부 State, 재개 지점 | Graph 내부 구현 세부 |

합치면 "외부에 이미 응답한 요청"과 "내부 실행 재개"가 한 저장소에 섞여, 장애 복구 시 어느 쪽이
진실인지 판정할 수 없다([96번 §10](96-workmate-langgraph-target-architecture.md)).

## 5. 범위 변경 절차

| 상황 | 처리 |
| --- | --- |
| Root 노드 추가·분할 | 구현자 판단. 단 Skill 로직이 들어가면 범위 이탈 |
| `validate_contract`가 기존 결과를 거부 | **구현을 의심한다.** Schema를 완화하지 않는다 |
| Task Store 구조 변경 필요 | 범위 이탈. 사용자 보고 |
| Skill Subgraph 수정 필요 | W3으로 복귀 |
| 공개 응답 모양 변경 필요 | 회귀 가능성. 스냅샷 대조로 먼저 확인 |

## 6. 참조

- [96번 §4](96-workmate-langgraph-target-architecture.md) — Root Graph 의사 코드
- [96번 §10](96-workmate-langgraph-target-architecture.md) — 저장소 책임 경계
- [30-4-5](30-4-5-design.md) — 노드별 설계
