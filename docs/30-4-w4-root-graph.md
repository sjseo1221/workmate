# W4 — Root Graph 조립

> **이 문서는 요약과 색인이다.** 각 절의 상세는 아래 12개 문서에 있고, 충돌 시 상세 문서를 기준으로
> 한다.
>
> | 절 | 상세 문서 | 내용 |
> | --- | --- | --- |
> | §1 | [30-4-1](30-4-1-document-info.md) | 문서 정보·용어·Root 노드 7종 |
> | §2 | [30-4-2](30-4-2-scope.md) | 목적, 대체 대상, 범위 |
> | §3 | [30-4-3](30-4-3-entry-criteria.md) | 선행 조건 (**Skill 11개 전부** 필요) |
> | §4 | [30-4-4](30-4-4-requirements.md) | 요구사항 W4-R1~R10 |
> | §5 | [30-4-5](30-4-5-design.md) | 설계 — **멱등성 현재 구현 조사**, 라우팅, Schema, 주입 |
> | §6 | [30-4-6](30-4-6-wbs.md) | 작업 분해 W4-T0~T9 |
> | §7 | [30-4-7](30-4-7-verification.md) | 검증 설계 W4-V1~V9 |
> | §8 | [30-4-8](30-4-8-traceability.md) | 추적성, 노드×요구사항, **동작 변경 추적** |
> | §9 | [30-4-9](30-4-9-exit-criteria.md) | 완료 정의, 승인 경계 |
> | §10 | [30-4-10](30-4-10-risks.md) | 위험 등록부 W4-K1~K9 |
> | §11 | [30-4-11](30-4-11-rollback.md) | 롤백·중단·재개 |
> | §12 | [30-4-12](30-4-12-references.md) | 참조 자료와 읽을 지점 |
>
> **코드 조사에서 나온 것(2026-09-29):** [`record_message()`](../workmate-agent/app/a2a/persistence.py#L210)는
> 중복 여부를 `bool`로 반환하지만 [runtime.py:223](../workmate-agent/app/a2a/runtime.py#L223)이 이를
> **무시한다.** 즉 현재 멱등성은 "같은 `message_id` + 다른 payload" 충돌 감지만 하고, 같은 요청
> 재전송은 **재실행된다.** UI REST는 `message_id`가 매번 달라 아예 발동하지 않는다. 96번 §4 설계대로
> 구현하면 동작이 바뀌며, 이는 스냅샷으로 검출되지 않는다 —
> 결정 W4-D1, 검증 W4-V3([30-4-5](30-4-5-design.md) §3).

## 1. 문서 정보

| 항목 | 값 |
| --- | --- |
| 단계 | W4 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W3 Skill Subgraph](30-3-w3-skill-subgraphs.md) |
| 후행 단계 | [W5 진입점 교체](30-5-w5-entrypoint-swap.md) |
| 상태 | 대기 |

## 2. 목적과 범위

### 2.1 목적

Skill Subgraph들을 하나의 **Root StateGraph**로 묶어, 지금 `WorkflowRegistry`와 `RuntimeBootstrapExecutor`에
흩어져 있는 공통 실행 계약(멱등성·라우팅·결과 검증·Artifact 생성·영속)을 Graph 안으로 모은다.

### 2.2 대체 대상

| 현재 | 위치 | 이후 |
| --- | --- | --- |
| `skill_id → handler` dict 조회 | [registry.py:57](../workmate-agent/app/workflows/registry.py#L57) | `add_conditional_edges` + path map |
| `message_id` 멱등성 확인 | [runtime.py:222-226](../workmate-agent/app/a2a/runtime.py#L222-L226) | `idempotency_check` 노드 |
| Artifact Part 생성 | [runtime.py:289](../workmate-agent/app/a2a/runtime.py#L289) | `build_artifact` 노드 |
| 결과 Schema 검증 | 분산 | `validate_contract` 노드 |

### 2.3 범위 내

- `app/graph/root.py`와 Root 공통 노드 구현
- Subgraph 11개를 Root 노드로 합성
- `build_workmate_graph()` 공개

### 2.4 범위 외

- FastAPI·A2A SDK 진입점 교체 (W5) — W4에서는 Graph가 아직 어디에도 연결되지 않는다
- `interrupt` (W6)
- Task Store 대체 — Task 상태·Artifact 원장은 계속 Task Store가 소유한다(96번 §10)

## 3. 선행 조건

| ID | 조건 | 확인 방법 |
| --- | --- | --- |
| W4-E1 | W3 완료, Skill Subgraph 11개 존재 | `app/graph/skills/` |
| W4-E2 | W3-V1 스냅샷 전건 PASS | W3 증빙 |
| W4-E3 | Skill 간 직접 import 없음 | W3-V9 |

## 4. 요구사항

| ID | 구분 | 요구사항 | 출처 |
| --- | --- | --- | --- |
| W4-R1 | 기능 | Root Graph가 `skill_id`에 따라 Subgraph로 분기한다 | 96번 §4 |
| W4-R2 | 기능 | 동일 `message_id` 재요청 시 기존 결과를 복원한다 | 02번 문서 멱등성 계약 |
| W4-R3 | 기능 | 결과가 승인된 Skill·Artifact Schema를 통과한 뒤에만 `COMPLETED`가 된다 | 96번 §11-9 |
| W4-R4 | 기능 | 식별자 5종을 실행 끝까지 보존한다 | 96번 §11-2 |
| W4-R5 | 제약 | Task 상태·Artifact 원장은 Task Store가 소유한다 | 96번 §10 |
| W4-R6 | 기능 | `assistant_ask` Subgraph가 다른 Subgraph를 호출할 수 있도록 Root가 핸들을 주입한다 | W3 §5.3 |
| W4-R7 | 제약 | 미등록 `skill_id`는 정의된 오류로 종료한다 | [registry.py:15](../workmate-agent/app/workflows/registry.py#L15) 현행 동작 계승 |
| W4-R8 | 기능 | Checkpointer를 붙여 `thread_id`별 실행 State를 영속화한다 | W2 산출물 사용 |

## 5. 설계

### 5.1 Root Graph 구조 (96번 §4)

```
START → initialize_state → idempotency_check ─(기존 완료)→ restore_result ─┐
                                             └(새 요청)→ route_skill        │
                                                            ↓ (조건부 Edge) │
     ┌──────────────────────────────────────────────────────┴────────┐     │
     │ daily_briefing · rank_priorities · weekly_report ·            │     │
     │ analyze_meeting · search_meetings · assistant_skills(5) ·     │     │
     │ assistant_ask                                                  │     │
     └──────────────────────────┬─────────────────────────────────────┘     │
                                ↓                                           │
                        validate_contract ──────────────→ build_artifact ←──┘
                                                               ↓
                                                         persist_result → END
```

### 5.2 Root 노드 책임

| 노드 | 책임 | 하지 않는 일 |
| --- | --- | --- |
| `initialize_state` | 식별자·`now`·`timezone` 주입, `task_state=WORKING` | 업무 규칙 |
| `idempotency_check` | `message_id`로 기존 Task 조회 | 결과 재계산 |
| `restore_result` | 기존 Artifact를 State로 복원 | Skill 실행 |
| `route_skill` | `skill_id` → Subgraph 분기 | 입력 검증(전송 계층이 이미 함) |
| `validate_contract` | 승인 Schema 검증 | 값 보정 |
| `build_artifact` | Artifact 이름·설명·Part 구성 | 전송 직렬화 |
| `persist_result` | Task Store에 상태·Artifact 저장 | Graph State 저장(Checkpointer 몫) |

### 5.3 라우팅 구현

```python
def route_skill(state: WorkmateState) -> str:
    """skill_id에 대응하는 Subgraph 노드 이름을 반환한다.

    dict 조회와 달리 조건부 Edge는 분기 자체가 Graph 구조에 남아
    Checkpoint·이력 조회·시각화 대상이 된다.
    """
```

`add_conditional_edges("route_skill", route_skill, path_map={...})` 형태로 **path map을 명시**한다.
명시하지 않으면 Graph 시각화와 정적 검사에서 분기 대상을 알 수 없다.

### 5.4 멱등성 경계

멱등성 원장은 Task Store가 계속 소유한다(W4-R5). Root 노드는 조회·판정만 한다.

```
message_id 존재? ─예→ restore_result → build_artifact → END   (Skill 미실행)
                └아니오→ route_skill → ...
```

**설계 근거:** 멱등성을 Checkpointer로 옮기면 "외부에 이미 응답한 요청"과 "내부 실행 재개"가 한
저장소에 섞인다. 96번 §10의 경계를 지킨다.

### 5.5 Subgraph 핸들 주입 (W4-R6)

`assistant_ask`는 다른 Skill을 실행해야 하지만 직접 import하면 순환 의존이 생긴다. Root가 컴파일 시점에
Subgraph 맵을 주입한다.

```python
def build_workmate_graph(checkpointer=None):
    """Root Graph와 Skill Subgraph를 조립해 컴파일한다."""
    subgraphs = {skill_id: build(skill_id) for skill_id in APPROVED_SKILL_IDS}
    graph.add_node("assistant_ask", build_assistant_router_graph(subgraphs=subgraphs))
```

## 6. 작업 분해 (WBS)

| ID | 작업 | 선행 | 산출물 |
| --- | --- | --- | --- |
| W4-T1 | Root 공통 노드 6종 구현 | — | `app/graph/nodes/` |
| W4-T2 | `route_skill` + path map 구현 | W4-T1 | `root.py` |
| W4-T3 | Subgraph 11개 합성 | W4-T2 | `root.py` |
| W4-T4 | Subgraph 핸들 주입 경로 구현 | W4-T3 | `root.py`, `skills/assistant_router.py` |
| W4-T5 | Checkpointer 결합·컴파일 | W4-T3 | `build_workmate_graph()` |
| W4-T6 | Root Graph 단위 테스트 | W4-T5 | `tests/test_graph_root.py` |
| W4-T7 | 스냅샷을 Root Graph 경유로 재대조 | W4-T6 | 대조 로그 |
| W4-T8 | 증빙·커밋 | W4-T7 | `result.md` |

W4-T7이 중요하다. W3까지는 Subgraph를 직접 호출해 대조했지만, W4부터는 **Root Graph를 통과한 결과**로
대조해야 공통 노드(검증·Artifact 구성)의 회귀까지 잡힌다.

## 7. 검증 설계

| ID | 검증 항목 | 방법 | 판정 기준 |
| --- | --- | --- | --- |
| W4-V1 | 라우팅 | 11개 `skill_id` 각각 호출 | 해당 Subgraph 실행 |
| W4-V2 | 미등록 Skill | 없는 `skill_id` | 정의된 오류, 500 아님 |
| W4-V3 | 멱등성 | 동일 `message_id` 2회 | 두 번째는 Skill 미실행, 동일 결과 |
| W4-V4 | 식별자 보존 | 종료 State 검사 | 5종 모두 입력값과 동일 |
| W4-V5 | Schema 검증 | 잘못된 결과 주입 | `COMPLETED` 도달 실패 |
| W4-V6 | Root 경유 스냅샷 | W4-T7 | 전건 PASS |
| W4-V7 | Checkpoint 생성 | 실행 후 `thread_id` 이력 조회 | 노드별 Snapshot 존재 |
| W4-V8 | 책임 경계 | Task Store·Checkpointer 쓰기 경로 검사 | 겹치지 않음 |
| W4-V9 | 기존 테스트 | 전체 스위트 | 실패 0 |

## 8. 추적성 매트릭스

| 요구사항 | 작업 | 검증 |
| --- | --- | --- |
| W4-R1 | W4-T2, T3 | W4-V1 |
| W4-R2 | W4-T1 | W4-V3 |
| W4-R3 | W4-T1 | W4-V5 |
| W4-R4 | W4-T1 | W4-V4 |
| W4-R5 | W4-T1 | W4-V8 |
| W4-R6 | W4-T4 | W4-V1 |
| W4-R7 | W4-T2 | W4-V2 |
| W4-R8 | W4-T5 | W4-V7 |

## 9. 완료 정의 (Exit criteria)

1. `build_workmate_graph()` 호출로 컴파일된 Graph가 11개 Skill을 전부 실행할 수 있다.
2. W4-V6(Root 경유 스냅샷 대조)이 전건 PASS.
3. W4-V3(멱등성)·V7(Checkpoint) PASS.
4. 운영 경로는 **아직 기존 Registry** — 전체 테스트가 여전히 통과한다.

## 10. 위험과 완화

| 위험 | 영향 | 완화 |
| --- | --- | --- |
| Root 공통 노드가 Subgraph 결과를 덮어써 값이 달라진다 | 스냅샷 대조 실패 | W4-T7에서 Root 경유 대조를 별도로 수행 |
| 멱등성 판정이 Checkpointer로 새어 나간다 | 상태 원장 이중화 | W4-V8 경로 검사, 96번 §10 검토 |
| Subgraph 주입이 순환 import를 만든다 | 컴파일 실패 | 주입은 `build_workmate_graph()` 한 곳에서만 |
| path map 누락으로 조건부 Edge가 런타임에만 실패 | 특정 Skill 호출 시 장애 | path map 명시 + W4-V1 전 Skill 호출 |

## 11. 롤백·중단 기준

- W4까지는 운영 경로가 기존 Registry이므로 롤백은 커밋 revert로 끝난다.
- **중단 기준:** W4-V3(멱등성)이 만족되지 않으면 W5(진입점 교체)로 넘어가지 않는다. 멱등성은 공개
  A2A 계약이고, 깨진 채 진입점을 바꾸면 중복 실행이 외부에 노출된다.

## 12. 참조

- [96-workmate-langgraph-target-architecture.md](96-workmate-langgraph-target-architecture.md) §4, §7, §10
- [02-a2a-interface.md](02-a2a-interface.md) — 멱등성·Task 계약
- [`app/a2a/runtime.py`](../workmate-agent/app/a2a/runtime.py)
