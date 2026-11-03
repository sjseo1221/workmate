# W4-4 — 요구사항 명세

> [30-4-w4-root-graph.md](30-4-w4-root-graph.md) §4의 상세 문서.

## 요약

| ID | 구분 | 한 줄 | 우선순위 | 검증 |
| --- | --- | --- | --- | --- |
| W4-R1 | 기능 | `skill_id`에 따라 Subgraph로 분기 | 필수 | W4-V1 |
| W4-R2 | 기능 | 동일 `message_id` 재요청 시 기존 결과 복원 | **필수(계약)** | W4-V3 |
| W4-R3 | 기능 | 승인 Schema 통과 후에만 `COMPLETED` | 필수 | W4-V5 |
| W4-R4 | 제약 | 식별자 5종을 끝까지 보존 | 필수 | W4-V4 |
| W4-R5 | 제약 | Task 상태·Artifact 원장은 Task Store가 소유 | 필수 | W4-V8 |
| W4-R6 | 기능 | `assistant_ask`에 Subgraph 핸들 주입 | 필수 | W4-V1 |
| W4-R7 | 제약 | 미등록 `skill_id`는 정의된 오류로 종료 | 필수 | W4-V2 |
| W4-R8 | 기능 | Checkpointer 결합으로 `thread_id`별 State 영속 | 필수 | W4-V7 |
| W4-R9 | 제약 | Root 노드에 업무 규칙을 두지 않음 | 필수 | 코드 검토 |
| W4-R10 | 기능 | Schema 파일을 배포 환경에서도 찾을 수 있음 | 필수 | W4-V5 |
| W4-R11 | 증빙 | **Graph 구조 산출물을 생성해 증빙에 남긴다** | 중요 | W4-V11 |

---

## W4-R1 — Skill 라우팅

**설명** Root Graph가 `state["skill_id"]`에 따라 해당 Skill Subgraph로 분기한다.

**근거** [96번 §4](96-workmate-langgraph-target-architecture.md). `WorkflowRegistry`의 dict 조회를
조건부 Edge로 대체한다.

**수용 기준**
- 공개 Skill 11개 각각을 호출하면 해당 Subgraph가 실행된다
- `add_conditional_edges`에 **path map을 명시**한다
- 분기 함수는 순수 함수다(State를 바꾸지 않는다)

**path map을 명시하는 이유:** 생략하면 분기 대상을 정적으로 알 수 없어, Graph 시각화와 검사에서
누락된다. 런타임에만 실패하는 오타를 못 잡는다.

**검증** W4-V1 / **우선순위** 필수

---

## W4-R2 — 멱등성

**설명** 이미 처리한 `message_id`로 다시 요청하면 Skill을 실행하지 않고 기존 결과를 반환한다.

**근거** [02-a2a-interface.md](02-a2a-interface.md)의 멱등성 계약. 현재
[runtime.py:222-226](../workmate-agent/app/a2a/runtime.py#L222)의 `record_message()`가 담당한다.

**수용 기준**
- 같은 `message_id` 2회 요청 시 두 번째는 Skill 미실행
- 두 응답의 내용이 동일
- 멱등성 원장은 **Task Store**가 계속 소유(W4-R5)
- 부작용이 있는 Skill(Task 생성·삭제 등)에서 특히 중요 — 중복 실행되면 안 된다

**검증** W4-V3 / **우선순위** **필수(공개 계약)**

---

## W4-R3 — Schema 검증 후 완료

**설명** 결과가 승인된 Skill·Artifact Schema를 통과한 뒤에만 `COMPLETED`가 된다.

**근거** [96번 §11-9](96-workmate-langgraph-target-architecture.md).

**현재와의 차이** 지금 운영 경로에는 이 검증이 **없다.** 테스트에서만 한다
([test_priority_workflow.py:70-85](../workmate-agent/tests/test_priority_workflow.py#L70)).
W4에서 운영 경로에 들어간다.

**수용 기준**
- 잘못된 구조의 결과가 `COMPLETED`에 도달하지 못한다
- 검증 실패 시 정의된 오류로 종료한다
- **기존 스냅샷 케이스 27건이 전부 검증을 통과한다** — 통과하지 못하면 Schema가 아니라 구현을 본다

**검증** W4-V5 / **우선순위** 필수

---

## W4-R4 — 식별자 보존

**설명** `user_id`·`request_id`·`message_id`·`task_id`·`thread_id`를 실행 끝까지 보존한다.

**근거** [96번 §11-2](96-workmate-langgraph-target-architecture.md). W2에서 State 수준의 불변식을
정의했고(W2-R3), W4는 **Root 노드가 이를 깨지 않는지**를 본다.

**수용 기준**
- `initialize_state`가 식별자 5종을 State에 넣는다
- 종료 State의 식별자가 입력과 동일
- `restore_result` 경로(멱등성 복원)에서도 보존된다

**검증** W4-V4 / **우선순위** 필수

---

## W4-R5 — 저장소 책임

**설명** Task 상태·Artifact·멱등성의 원장은 A2A Task Store가 소유한다. Checkpointer는 내부 State만
소유한다.

**근거** [96번 §10](96-workmate-langgraph-target-architecture.md).

**수용 기준**
- `persist_result` 노드가 Task Store에 쓴다
- Checkpointer가 Task 상태·Artifact를 쓰지 않는다
- `idempotency_check`가 Task Store를 조회한다(Checkpointer 아님)
- 두 저장소의 연결은 `task_id ↔ thread_id`뿐

**검증** W4-V8 / **우선순위** 필수

---

## W4-R6 — Subgraph 핸들 주입

**설명** `assistant_ask` Subgraph가 다른 Subgraph를 호출할 수 있도록 Root가 맵을 주입한다.

**근거** W3-D2. Skill 간 직접 import를 금지했으므로 주입이 유일한 경로다.

**수용 기준**
- `build_workmate_graph()` 한 곳에서만 주입한다
- `assistant_ask`가 주입된 핸들로 하위 Skill을 실행한다
- 순환 import가 없다
- **하위 Skill 실행 시 `user_id`가 전달된다**(권한 범위 유지)

**검증** W4-V1 / **우선순위** 필수

---

## W4-R7 — 미등록 Skill

**설명** 등록되지 않은 `skill_id`는 정의된 오류로 종료한다.

**근거** 현재 [`WorkflowNotImplementedError`](../workmate-agent/app/workflows/registry.py#L15)와
[internal_chat.py:360-361](../workmate-agent/app/internal_chat.py#L360)의 `422 unknown skill_id`가
같은 동작을 한다.

**수용 기준**
- 없는 `skill_id`로 호출 시 정의된 예외
- 500(예상치 못한 오류)이 아니다
- UI REST 경로의 422 매핑이 유지된다(W5에서 확인)

**검증** W4-V2 / **우선순위** 필수

---

## W4-R8 — Checkpointer 결합

**설명** 컴파일 시 Checkpointer를 결합해 `thread_id`별 실행 State가 영속화된다.

**근거** W6의 `interrupt`가 성립하려면 W4에서 결합돼 있어야 한다.

**수용 기준**
- `build_workmate_graph(checkpointer=...)`로 주입
- 실행 후 `thread_id`로 State 이력 조회 가능
- `thread_id = task_id` 규칙 유지

**검증** W4-V7 / **우선순위** 필수

---

## W4-R9 — Root 노드의 책임 제한

**설명** Root 노드에 업무 규칙을 두지 않는다.

**근거** [96번 §10](96-workmate-langgraph-target-architecture.md): "Root StateGraph — 공통 State,
Skill 분기, 멱등성, 결과 조립 / **SQL과 Provider 세부 구현은 하지 않는다**."

`AGENTS.md`도 같은 취지다: "FastAPI Route에는 업무 규칙을 직접 작성하지 않고 Workflow·Domain 함수로
전달한다."

**수용 기준**
- Root 노드가 Repository를 직접 호출하지 않는다(Task Store 제외 — 이는 공통 계약)
- Provider Client를 호출하지 않는다
- Skill별 분기 로직이 없다(`route_skill`의 path map은 예외)

**검증** 코드 검토 / **우선순위** 필수

---

## W4-R10 — Schema 파일 접근

**설명** `validate_contract`가 쓰는 Schema 파일을 배포 환경에서도 찾을 수 있다.

**근거** 테스트는 `Path(__file__).parents[2] / "docs" / "schemas" / ...`로 상대 경로를 올라간다.
운영 컨테이너에는 `docs/`가 없을 수 있다.

실제로 이 문제가 전에 있었다 — 커밋 `62f38c5`의 메시지가
"vendor docs/schemas + bake into Docker image so schema-validated skill chat works standalone"이다.

**수용 기준**
- Schema 로딩이 배포 환경에서 동작한다
- 로딩 실패 시 조용히 검증을 건너뛰지 않는다(명시적 오류)
- 기존 vendor 방식이 있으면 그것을 따른다

**검증** W4-V5 / **우선순위** 필수

---

## W4-R11 — Graph 구조 산출물

**설명** 컴파일된 Graph에서 구조 다이어그램과 Checkpoint 이력을 생성해 증빙에 남긴다.

**근거** 전환이 "LangGraph로 구현됐다"를 증명하는 것은 코드 스니펫이 아니라 **실행 산출물**이다.
손으로 그린 다이어그램은 코드와 어긋날 수 있지만, Graph 객체에서 생성한 것은 그럴 수 없다.

**수용 기준**

| 산출물 | 생성 방법 | 보여주는 것 |
| --- | --- | --- |
| Graph 다이어그램 | `graph.get_graph().draw_mermaid()` | 노드·Edge·조건부 분기·Subgraph 중첩 |
| Checkpoint 이력 | `graph.get_state_history(config)` | 노드별 State Snapshot과 다음 노드 |

- 두 산출물이 W4 증빙에 첨부된다
- 다이어그램의 노드 목록이 실제 구현과 일치한다(W4-V11-2)

**소비처** [W9](30-9-w9-docs-evidence.md)의 97번 문서 개정. 현재 97번은 "현재는 Registry 기반 경량
Runtime"이라고 적고 있는데, 이 산출물이 그 서술을 대체한다.

**검증** W4-V11 / **우선순위** 중요

---

## 요구사항 간 의존

```
W4-R1 (라우팅) ─┬→ W4-R6 (주입)
                └→ W4-R7 (미등록)

W4-R2 (멱등성) ─→ W4-R5 (저장소 책임)  ← 멱등성 원장이 Task Store여야 함
W4-R3 (Schema 검증) ─→ W4-R10 (파일 접근)
W4-R8 (Checkpointer) ─→ W6 interrupt의 전제

W4-R4 (식별자) ← W2-R3에서 State 수준으로 이미 정의됨
W4-R9 (책임 제한) ← 전 노드에 적용
```

## 참조

- [96번 §4·§10·§11](96-workmate-langgraph-target-architecture.md)
- [02-a2a-interface.md](02-a2a-interface.md) — 멱등성 계약
- [30-4-5](30-4-5-design.md) — 구현 설계
