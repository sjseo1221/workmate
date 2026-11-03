# W4-1 — 문서 정보와 문서 체계

> [30-4-w4-root-graph.md](30-4-w4-root-graph.md) §1의 상세 문서.

## 1. 단계 식별

| 항목 | 값 |
| --- | --- |
| 단계 코드 | W4 |
| 단계명 | Root Graph 조립 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W3 Skill Subgraph](30-3-w3-skill-subgraphs.md) |
| 후행 단계 | [W5 진입점 교체](30-5-w5-entrypoint-swap.md) |
| 상태 | 대기 |
| 관련 확정 결정 | D6=B(Checkpointer 결합) |

## 2. 단계 성격

W4는 **흩어진 공통 실행 계약을 한곳으로 모으는 단계**다.

현재 "Skill을 실행하기 전후에 반드시 하는 일"은 두 파일에 흩어져 있다.

| 하는 일 | 현재 위치 |
| --- | --- |
| `message_id` 멱등성 확인 | [runtime.py:222-226](../workmate-agent/app/a2a/runtime.py#L222) |
| Task Snapshot 저장 | [runtime.py:214-221](../workmate-agent/app/a2a/runtime.py#L214) |
| `skill_id` → handler 조회 | [registry.py:80-90](../workmate-agent/app/workflows/registry.py#L80) |
| 결과 → Artifact Part 변환 | [runtime.py:289-312](../workmate-agent/app/a2a/runtime.py#L289) |
| Artifact 저장·발행 | [runtime.py:248-260](../workmate-agent/app/a2a/runtime.py#L248) |
| UI REST 경로의 같은 일 | [internal_chat.py:238-302](../workmate-agent/app/internal_chat.py#L238) |

A2A 경로와 UI REST 경로가 **비슷하지만 다르게** 처리한다. W4는 이 공통 계약을 Root Graph 노드로
모아, W5에서 두 진입점이 같은 Graph를 부르게 만든다.

### 2.1 W4가 바꾸는 것

```
[현재]
진입점 ──→ 공통 처리(진입점마다 중복) ──→ Registry dict 조회 ──→ handler

[W4 이후]
진입점 ──→ Root Graph
              ├─ initialize_state
              ├─ idempotency_check
              ├─ route_skill (조건부 Edge)
              ├─ (Skill Subgraph)
              ├─ validate_contract
              ├─ build_artifact
              └─ persist_result
```

### 2.2 W4에서 하지 않는 일

**운영 경로는 여전히 `WorkflowRegistry`다.** W4에서 만든 Root Graph는 테스트에서만 실행된다. 진입점
교체는 W5다.

이 순서를 지키는 이유: Root Graph가 완성되기 전에 진입점을 바꾸면, 실패 시 "Graph 문제인가 진입점
문제인가"를 구분할 수 없다.

## 3. 문서 체계

| 문서 | 대응 절 | 내용 |
| --- | --- | --- |
| [30-4-1](30-4-1-document-info.md) | §1 | 문서 정보·체계·용어 (이 문서) |
| [30-4-2](30-4-2-scope.md) | §2 | 목적, 대체 대상, 범위 |
| [30-4-3](30-4-3-entry-criteria.md) | §3 | 선행 조건 |
| [30-4-4](30-4-4-requirements.md) | §4 | 요구사항 W4-R1~R8 |
| [30-4-5](30-4-5-design.md) | §5 | 설계 — Root 노드, 라우팅, 멱등성, 주입 |
| [30-4-6](30-4-6-wbs.md) | §6 | 작업 분해 W4-T1~T8 |
| [30-4-7](30-4-7-verification.md) | §7 | 검증 설계 W4-V1~V9 |
| [30-4-8](30-4-8-traceability.md) | §8 | 추적성 매트릭스 |
| [30-4-9](30-4-9-exit-criteria.md) | §9 | 완료 정의 |
| [30-4-10](30-4-10-risks.md) | §10 | 위험 등록부 |
| [30-4-11](30-4-11-rollback.md) | §11 | 롤백·중단 기준 |
| [30-4-12](30-4-12-references.md) | §12 | 참조 자료 |

## 4. 식별자 규칙

| 접두 | 의미 | 예 |
| --- | --- | --- |
| `W4-E` | 선행 조건 | `W4-E2` |
| `W4-R` | 요구사항 | `W4-R3` |
| `W4-T` | 작업 | `W4-T5` |
| `W4-V` | 검증 | `W4-V6` |
| `W4-K` | 위험 | `W4-K1` |
| `W4-D` | 설계 결정 | `W4-D1` |

## 5. 용어

| 용어 | 정의 | 주의 |
| --- | --- | --- |
| **Root Graph** | Skill Subgraph들을 묶고 공통 실행 계약을 소유하는 최상위 `StateGraph` | Skill 로직을 갖지 않는다 |
| **조건부 Edge** | `add_conditional_edges`로 구현한 분기 | dict 조회와 달리 Graph 구조에 남는다 |
| **path map** | 조건부 Edge의 반환값 → 노드 이름 매핑 | 명시하지 않으면 정적 검사·시각화가 불가 |
| **멱등성(idempotency)** | 같은 `message_id` 재요청 시 기존 결과를 반환 | Task Store가 원장 |
| **Subgraph 주입** | Root가 컴파일 시점에 Skill Graph 맵을 넘기는 것 | 순환 import 방지 |
| **`runtime_bootstrap`** | 전송 골격 확인용 Mock Workflow | 공개 Skill이 아니다. 처리 방침은 [30-4-5](30-4-5-design.md) §7 |

## 6. 대상 노드

Root Graph가 갖는 노드는 7종이다.

| 노드 | 분류 | 책임 |
| --- | --- | --- |
| `initialize_state` | 공통 | 식별자·`now`·`timezone` 주입, `task_state=WORKING` |
| `idempotency_check` | 공통 | `message_id`로 기존 Task 조회 |
| `restore_result` | 공통 | 기존 Artifact를 State로 복원 |
| `route_skill` | 라우팅 | `skill_id` → Subgraph 분기 |
| (Skill Subgraph 11개) | 위임 | W3 산출물 |
| `validate_contract` | 공통 | 승인 Schema 검증 |
| `build_artifact` | 공통 | Artifact 이름·설명·Part 구성 |
| `persist_result` | 공통 | Task Store에 상태·Artifact 저장 |

## 7. 산출물 위치

```
workmate-agent/
  app/graph/
    __init__.py       build_workmate_graph() 공개 ← W4에서 채움
    root.py           Root StateGraph 조립
    nodes/
      __init__.py
      initialize.py   initialize_state
      idempotency.py  idempotency_check, restore_result
      routing.py      route_skill
      contract.py     validate_contract
      artifact.py     build_artifact
      persist.py      persist_result
  tests/
    test_graph_root.py
docs/evidence/langgraph/W4/runs/{run_id}/result.md
```

## 8. 변경 이력

| 일자 | 변경 | 사유 |
| --- | --- | --- |
| 2026-09-23 | 초판 (상위 문서 §1) | 단계별 상세 계획 |
| 2026-09-29 | 12개 문서로 분해 | 절별 상세화 요청 |
