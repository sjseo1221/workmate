# W4-5 — 설계

> [30-4-w4-root-graph.md](30-4-w4-root-graph.md) §5의 상세 문서.

## 1. Root Graph 구조

[96번 §4](96-workmate-langgraph-target-architecture.md)를 따른다.

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

## 2. Root 노드 책임

| 노드 | 책임 | 하지 않는 일 |
| --- | --- | --- |
| `initialize_state` | 식별자·`now`·`timezone` 주입, `task_state=WORKING` | 업무 규칙, 입력 Schema 검증(전송 계층이 이미 함) |
| `idempotency_check` | `message_id`로 기존 Task 조회 | 결과 재계산 |
| `restore_result` | 기존 Artifact를 State로 복원 | Skill 실행 |
| `route_skill` | `skill_id` → Subgraph 분기 | 입력 검증 |
| `validate_contract` | 승인 Schema 검증 | 값 보정 |
| `build_artifact` | Artifact 이름·설명·Part 구성 | 전송 직렬화(SDK 몫) |
| `persist_result` | Task Store에 상태·Artifact 저장 | Graph State 저장(Checkpointer 몫) |

**공통 제약(W4-R9):** Root 노드는 Repository·Provider를 직접 호출하지 않는다. 예외는 Task Store로,
이는 공통 실행 계약의 일부다.

---

## 3. 멱등성 — 현재 구현 조사와 설계 결정 W4-D1

### 3.1 조사 결과

[`record_message()`](../workmate-agent/app/a2a/persistence.py#L210)는 `bool`을 반환한다.

```python
def _record_message_sync(self, message_id, task_id, digest, response_json) -> bool:
    row = connection.execute("SELECT request_hash FROM a2a_messages WHERE message_id = ?", ...)
    if row:
        if row[0] != digest:
            raise ValueError("message_id was reused with a different payload")
        return False          # ← 중복 요청
    ...
    return True               # ← 최초 요청
```

그런데 **A2A 경로가 이 반환값을 쓰지 않는다.**

```python
# runtime.py:223 — 반환값을 받지 않는다
await self.task_store.record_message(
    message_id=message_id, task_id=context.task_id, payload=payload,
)
# 이어서 무조건 Workflow를 실행한다
result = await self.registry.execute(WorkflowRequest(...))
```

또한 `response=` 인자를 넘기지 않으므로 `response_json`이 `NULL`로 저장된다 — 즉 **복원할 응답이
저장되지 않는다.**

UI REST 경로는 구조가 다르다. [internal_chat.py:266-272](../workmate-agent/app/internal_chat.py#L266)는
`message_id = f"internal-{task_id}"`로 만드는데 `task_id`가 요청마다 새 `uuid4()`다. 즉 **모든 요청의
`message_id`가 달라 멱등성이 애초에 발동하지 않는다.**

### 3.2 정리

| 항목 | 현재 실제 동작 |
| --- | --- |
| 같은 `message_id` + 같은 payload | **재실행된다** (반환값 무시) |
| 같은 `message_id` + 다른 payload | `ValueError` — 유일하게 동작하는 보호 |
| 기존 응답 복원 | 불가 (A2A 경로는 `response_json`이 NULL) |
| UI REST 경로 | `message_id`가 매번 달라 해당 없음 |

즉 현재 멱등성은 **"충돌 감지"까지만 구현돼 있고 "재생(replay)"은 없다.**

### 3.3 설계 결정 W4-D1

| | 방식 | 동작 변화 | 평가 |
| --- | --- | --- | --- |
| A | 현재 동작 보존(충돌 감지만) | 없음 | 96번 §4의 `restore_result` 노드가 무의미해짐 |
| **B** | **96번 설계대로 구현**(중복 시 복원) | **있음** — 중복 요청이 재실행되지 않음 | **채택** |

**채택: B.** 근거는 세 가지다.

1. [계획서 §1-2](30-langgraph-migration-plan.md): "호환보다 구조 정합성을 우선한다." 운영 중이
   아니므로 동작 변경의 비용이 낮다.
2. [96번 §4](96-workmate-langgraph-target-architecture.md)가 `idempotency_check → restore_result`를
   명시한다. A안을 택하면 이 노드들이 껍데기가 된다.
3. 중복 실행은 부작용이 있는 Skill(`manage_tasks.delete`·`review_proposal` 등)에서 실제 문제다.

### 3.4 B안의 파급

| 항목 | 내용 |
| --- | --- |
| **동작 변경** | A2A 경로에서 같은 `message_id` 재요청 시 Skill이 실행되지 않는다 |
| 스냅샷 | **검출되지 않음** — W1 케이스 27건에 중복 요청 시나리오가 없다(Skill 수준 케이스이므로) |
| 검증 | W4-V3 전용 검증 필요 |
| 기록 | **W9의 "의도적 변경"으로 분류**한다 |
| 저장 | `persist_result`가 `response=`를 넘겨 복원할 응답을 저장해야 한다 |

### 3.5 구현

```
idempotency_check
  ├─ Task Store에서 message_id 조회
  ├─ 없음        → state["idempotent_hit"]=False → route_skill
  ├─ 있음 + 완료 → state["idempotent_hit"]=True  → restore_result
  └─ 있음 + 미완료 → (진행 중) 정책 필요 — §3.6

restore_result
  └─ 저장된 응답을 State의 result로 복원 → build_artifact
```

### 3.6 미해결 항목 — 진행 중 중복

같은 `message_id`가 **아직 실행 중**일 때의 동작은 현재 코드에도 정의돼 있지 않다.

| 선택지 | 동작 |
| --- | --- |
| a | 진행 중 Task Snapshot을 반환(`WORKING` 상태) |
| b | 오류 |
| c | 대기 후 결과 반환 |

**W4-T1에서 a안을 기본으로 정하되**, 이것이 02번 문서의 계약과 맞는지 확인한다. 맞지 않으면 계약
개정 대상으로 W6에 넘긴다.

---

## 4. 라우팅 설계

### 4.1 조건부 Edge

```python
def route_skill(state: WorkmateState) -> str:
    """skill_id에 대응하는 Subgraph 노드 이름을 반환한다.

    dict 조회와 달리 조건부 Edge는 분기 자체가 Graph 구조에 남아
    Checkpoint·이력 조회·시각화 대상이 된다.
    """
    skill_id = state["skill_id"]
    if skill_id not in SKILL_NODE_NAMES:
        raise WorkflowNotImplementedError(f"workflow is not implemented: {skill_id}")
    return skill_id


graph.add_conditional_edges("route_skill", route_skill, path_map=SKILL_NODE_NAMES)
```

### 4.2 path map을 명시하는 이유

| 생략 시 | 명시 시 |
| --- | --- |
| 분기 대상을 정적으로 알 수 없다 | Graph 시각화에 분기가 보인다 |
| 오타가 런타임에만 실패 | 컴파일 시점에 노드 존재 확인 |
| 검사 도구가 경로를 못 따라간다 | 커버리지 계산 가능 |

### 4.3 dict 조회와 조건부 Edge의 실질적 차이

| | `WorkflowRegistry` | 조건부 Edge |
| --- | --- | --- |
| 분기 기록 | 없음 | Checkpoint에 남는다 |
| 상태 전달 | 인자로 직접 | State 채널 |
| 실행 이력 | 없음 | `get_state_history()` |
| 중단·재개 | 불가 | 가능 |

이 차이가 W6(`interrupt`)을 가능하게 한다.

---

## 5. Schema 검증 설계

### 5.1 검증 대상

[96번 §11-9](96-workmate-langgraph-target-architecture.md): "공개 결과는 승인된 Skill·Artifact
Schema를 통과한 뒤에만 `COMPLETED`가 된다."

현재 테스트가 하는 방식을 참고한다
([test_priority_workflow.py:70-85](../workmate-agent/tests/test_priority_workflow.py#L70)).

```python
validator.validate({
    "schema_version": "1.0",
    "request_id": ...,
    "generated_at": ...,
    "data_freshness": {...},
    "warnings": [],
    "result": json.loads(result.text),
})
```

### 5.2 Schema 파일 접근 (W4-R10)

테스트는 상대 경로로 올라간다.

```python
Path(__file__).resolve().parents[2] / "docs" / "schemas" / "workmate-skill-schemas.schema.json"
```

운영 컨테이너에는 `docs/`가 없을 수 있다. 실제로 이 문제가 있었다 — 커밋 `62f38c5`의 메시지가
"vendor docs/schemas + bake into Docker image so schema-validated skill chat works standalone"이다.

**설계 결정 W4-D2:** 기존 vendor 경로를 그대로 쓴다. [internal_chat.py:59-73](../workmate-agent/app/internal_chat.py#L59)의
`_schema_validator()`가 이미 같은 일을 하므로, 그 로딩 방식을 재사용한다. 새 경로 규칙을 만들지
않는다.

### 5.3 검증 실패 시

| 상황 | 처리 |
| --- | --- |
| Schema 위반 | `task_state=FAILED`, 정의된 오류 |
| Schema 파일 로딩 실패 | **명시적 오류.** 조용히 검증을 건너뛰지 않는다 |
| 기존 스냅샷 케이스가 실패 | **구현을 의심한다.** Schema를 완화하지 않는다 |

### 5.4 주의 — 새 검증이 기존 결과를 거부할 수 있다

운영 경로에 없던 검증을 추가하므로, 지금까지 통과하던 결과가 실패할 가능성이 있다.

**W4-T2 착수 시 가장 먼저 할 일:** 스냅샷 케이스 27건의 `expected`를 Schema로 검증해 본다. 전부
통과하면 안전하다. 실패하는 케이스가 있으면 그것이 현재 존재하는 계약 위반이므로, 기록하고 사용자에게
보고한다(고치는 것은 별도 백로그).

---

## 6. Subgraph 주입

```python
def build_workmate_graph(checkpointer=None):
    """Root Graph와 Skill Subgraph를 조립해 컴파일한다.

    Subgraph 맵은 여기서 한 번만 만든다 — Skill이 서로를 직접 import하면
    순환 의존이 되기 때문이다(W3-D2).
    """
    subgraphs = {skill_id: build_skill_graph(skill_id) for skill_id in APPROVED_SKILL_IDS}

    graph = StateGraph(WorkmateState)
    graph.add_node("initialize_state", initialize_state)
    ...
    for skill_id, sub in subgraphs.items():
        if skill_id == "assistant_ask":
            continue                      # 주입이 필요하므로 따로
        graph.add_node(skill_id, sub)
    graph.add_node("assistant_ask", build_assistant_router_graph(subgraphs=subgraphs))
    ...
    return graph.compile(checkpointer=checkpointer)
```

### 6.1 `user_id` 전달

`assistant_ask`가 하위 Skill을 호출할 때 `user_id`가 유실되면 권한 범위가 사라진다. 주입된 Subgraph를
호출할 때 State를 그대로 넘기므로 자동으로 보존되지만, **W4-V1에서 명시적으로 확인**한다.

---

## 7. `runtime_bootstrap` 처리

현재 [runtime.py:356-366](../workmate-agent/app/a2a/runtime.py#L356)에 전송 골격 확인용 Mock
Workflow가 등록돼 있다. `mock=True`를 반환한다.

| 선택지 | 평가 |
| --- | --- |
| A. Root Graph에 노드로 포함 | 운영 Graph에 Mock이 들어간다 — `AGENTS.md` 완료 규칙과 충돌 |
| **B. 제외하고 별도 처리** | **채택** — 공개 Skill이 아니므로 Graph 밖에 둔다 |
| C. 삭제 | 전송 골격 테스트가 쓰고 있는지 확인 필요. W7에서 판단 |

**설계 결정 W4-D3: B.** `route_skill`의 path map에 넣지 않는다. 이 `skill_id`로 호출되면 W4-R7의
미등록 경로를 탄다. 기존 테스트가 `runtime_bootstrap`을 쓰고 있으면 W5에서 진입점 교체 시 함께
정리한다.

---

## 8. 설계 결정 요약

| ID | 결정 | 근거 |
| --- | --- | --- |
| W4-D1 | 멱등성을 96번 설계대로 구현(중복 시 복원) — **동작 변경** | §3.3 |
| W4-D2 | Schema 로딩은 기존 vendor 경로 재사용 | §5.2 |
| W4-D3 | `runtime_bootstrap`을 Root Graph에서 제외 | §7 |
| W4-D4 | path map 명시 필수 | §4.2 |
| W4-D5 | 진행 중 중복은 Task Snapshot 반환(a안) — W4-T1에서 확정 | §3.6 |

## 9. 참조

- [96번 §4](96-workmate-langgraph-target-architecture.md) — Root Graph 의사 코드
- [96번 §10](96-workmate-langgraph-target-architecture.md) — 저장소 책임
- [02-a2a-interface.md](02-a2a-interface.md) — 멱등성 계약
- [`app/a2a/persistence.py`](../workmate-agent/app/a2a/persistence.py) — 현재 멱등성 구현
