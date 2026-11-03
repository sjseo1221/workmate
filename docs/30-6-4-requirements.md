# W6-4 — 요구사항 명세

> [30-6-w6-interrupt-resume.md](30-6-w6-interrupt-resume.md) §4의 상세 문서.

## 요약

| ID | 구분 | 한 줄 | 우선순위 | 검증 |
| --- | --- | --- | --- | --- |
| W6-R1 | 기능 | 확인 필요 시 `interrupt()`로 중단 | 필수 | W6-V1 |
| W6-R2 | 기능 | 중단을 `INPUT_REQUIRED`로 표면화 | 필수 | W6-V1 |
| W6-R3 | 기능 | 같은 `thread_id` resume으로 이어 실행 | 필수 | W6-V3 |
| W6-R4 | 제약 | **interrupt 이전에 외부 상태를 바꾸지 않음** | **필수(불변식)** | W6-V2 |
| W6-R5 | 제약 | resume 시 Router LLM 재호출 금지 | 필수 | W6-V4 |
| W6-R6 | 제약 | resume은 새 Task를 만들지 않음 | 필수 | W6-V5 |
| W6-R7 | 기능 | 확인 거부 시 `CANCELED` | 필수 | W6-V6 |
| W6-R8 | 기능 | UI가 `INPUT_REQUIRED`를 인식해 확인 UI 표시 | 필수 | **W6-V7(육안)** |
| W6-R9 | 문서 | 공개 계약 변경을 02번 문서에 반영 | 필수 | W6-V9 |
| W6-R10 | 제약 | 확인 판정 규칙 4종 불변 | 필수 | W6-V1 |
| W6-R11 | 제약 | 의도적 변경 외 스냅샷 25건 PASS | 필수 | W6-V10 |

---

## W6-R1 — interrupt 중단

**설명** 확인이 필요한 동작에서 Graph가 `interrupt()`로 중단한다.

**근거** [96번 §6](96-workmate-langgraph-target-architecture.md)의 Assistant Router Subgraph 구성.

**수용 기준**
- `requires_confirmation?` 판정이 참이면 `interrupt()` 호출
- 하위 Skill이 **실행되지 않는다**
- Checkpoint에 `skill_id`·`arguments`·대화 컨텍스트가 저장된다

**검증** W6-V1 / **우선순위** 필수

---

## W6-R2 — `INPUT_REQUIRED` 표면화

**설명** 중단 상태를 `TASK_STATE_INPUT_REQUIRED`로 외부에 노출한다.

**근거** [96번 §7](96-workmate-langgraph-target-architecture.md)의 상태 전이도.

```
WORKING --interrupt--> INPUT_REQUIRED --Command(resume)--> WORKING
```

**현재 상태:** 이 문자열은 agent 코드에도 UI에도 **존재하지 않는다.** W6에서 처음 생긴다.

**수용 기준**
- 확인 대기 Task를 조회하면 `INPUT_REQUIRED`
- A2A·UI REST 양쪽에서 동일
- 상태 전이가 정의된 경로만 따른다

**검증** W6-V1 / **우선순위** 필수

---

## W6-R3 — resume 재개

**설명** 같은 `thread_id`로 resume하면 멈춘 지점부터 이어 실행한다.

**근거** [96번 §11-8](96-workmate-langgraph-target-architecture.md).

**수용 기준**
- 멈춘 노드부터 실행(처음부터 다시 하지 않는다)
- Checkpoint의 State가 복원된다
- 결과가 정상 실행과 동일하다

**검증** W6-V3 / **우선순위** 필수

---

## W6-R4 — 외부 상태 불변식 (최우선)

**설명** `interrupt` 이전에 외부 상태를 변경하지 않는다.

**근거** [96번 §11-7](96-workmate-langgraph-target-architecture.md): "사용자 확인이 필요한 동작은
`interrupt` 전에는 외부 상태를 변경하지 않는다."

**왜 최우선인가** 이 불변식이 깨지면 **확인 절차 자체가 무의미해진다.** 사용자가 "아니오"를 눌러도
이미 Task가 삭제된 뒤라면 확인을 물어본 이유가 없다.

**수용 기준**
- `validate_skill_and_arguments` 노드가 **검증만** 한다. Repository 쓰기 호출 없음
- 확인 대기 상태에서 DB를 조회해 변경이 없음을 확인
- 확인 대상 4종 각각에 대해 확인

**구현 규칙**

| 노드 | 허용 | 금지 |
| --- | --- | --- |
| `route_with_llm` | LLM 호출(읽기) | 쓰기 |
| `validate_skill_and_arguments` | 조회·검증 | **쓰기** |
| `requires_confirmation?` | 판정 | 쓰기 |
| `interrupt` | State 저장(Checkpoint) | 외부 쓰기 |
| `call_selected_subgraph` | 쓰기 | — (여기서부터 허용) |

**검증** W6-V2 / **우선순위** **필수(불변식)**

---

## W6-R5 — Router LLM 재호출 금지

**설명** resume 시 Router LLM을 다시 부르지 않고 Checkpoint의 검증된 `skill_id`·`arguments`를 쓴다.

**근거** [96번 §6](96-workmate-langgraph-target-architecture.md) 마지막 문단. 현재 코드도 이미 이
규칙을 지킨다([assistant_router.py:794-803](../workmate-agent/app/workflows/assistant_router.py#L794)).

**왜 중요한가** LLM은 결정적이지 않다. 재호출하면 사용자가 확인한 것과 **다른 Skill**이 실행될 수
있다. 사용자는 "Task 삭제"를 확인했는데 "Task 수정"이 실행되는 식이다.

**수용 기준**
- resume 경로에서 LLM 호출 계측 결과 0회
- 실행되는 `skill_id`가 확인 시점의 값과 동일
- `arguments`도 동일

**검증** W6-V4 / **우선순위** 필수

---

## W6-R6 — Task 단일성

**설명** resume은 새 Task를 만들지 않는다.

**근거** [96번 §11-8](96-workmate-langgraph-target-architecture.md): "Resume은 새 Task를 만들지 않고
같은 `thread_id`와 멱등성 Key를 사용한다."

**현재와의 차이** 현재 방식은 `confirmed_skill_id` 재요청이 **새 Task를 만든다**
([internal_chat.py:373](../workmate-agent/app/internal_chat.py#L373)의 `task_id = str(uuid4())`).

**수용 기준**
- resume 전후 Task 수가 같다
- `task_id`가 유지된다
- 멱등성 Key도 유지된다(C5)

**검증** W6-V5 / **우선순위** 필수

---

## W6-R7 — 취소 경로

**설명** 사용자가 확인을 거부하면 `CANCELED`로 종료한다.

**근거** [96번 §6·§7](96-workmate-langgraph-target-architecture.md).

**현재와의 차이** 현재는 취소 개념이 없다. 사용자가 확인 버튼을 안 누르면 아무 일도 일어나지 않고
Task도 남지 않는다.

**수용 기준**
- 거부 시 Task가 `CANCELED`
- 외부 상태가 변경되지 않는다
- 사용자에게 취소 안내가 전달된다

**주의** UI의 `TERMINAL_FAILURE_STATES`에 `TASK_STATE_CANCELED`가 포함돼 있다
([AssistantDrawer.tsx:42](../workmate-ui/app/views/AssistantDrawer.tsx#L42)). 취소를 정상 종료로
다루려면 이 분류도 함께 손봐야 한다.

**검증** W6-V6 / **우선순위** 필수

---

## W6-R8 — UI 확인 흐름

**설명** UI가 `INPUT_REQUIRED`를 인식해 확인 UI를 띄우고 resume을 요청한다.

**근거** D5=A(폴링 유지). 현재 폴링 루프는 이 상태를 모른다.

```js
// AssistantDrawer.tsx:151-163 현재
if (state === "TASK_STATE_COMPLETED") { /* 결과 */ }
if (TERMINAL_FAILURE_STATES.has(state)) { /* 에러 */ }
// 그 외 → 1.5초 후 재폴링, 5분 타임아웃
```

`INPUT_REQUIRED`는 둘 다 아니므로 **5분 폴링 후 타임아웃 에러**가 된다.

**수용 기준**
- `INPUT_REQUIRED` 감지 시 폴링 중단
- Task에서 확인 payload를 꺼내 UI 표시
- 확인 시 resume 요청, 거부 시 취소 요청
- `CANCELED`를 실패가 아닌 정상 종료로 처리

**검증** **W6-V7(육안 검수)** / **우선순위** 필수

---

## W6-R9 — 문서 반영

**설명** 공개 계약 변경을 [02-a2a-interface.md](02-a2a-interface.md)에 반영한다.

**근거** `AGENTS.md`: "변경이 필요하면 관련 문서·Schema·Contract Test를 함께 수정한다."

**수용 기준**
- C1~C5의 확정안이 문서에 반영됨
- 구현과 문서가 일치
- 기존 `pending_action` 방식의 폐기 여부가 명시됨

**검증** W6-V9 / **우선순위** 필수

---

## W6-R10 — 확인 판정 규칙 불변

**설명** [`_requires_confirmation()`](../workmate-agent/app/workflows/assistant_router.py#L221)의
4종 판정을 그대로 유지한다.

**근거** [30-6-2](30-6-2-scope.md) §3.1. 처리 방식과 판정 규칙을 같이 바꾸면 원인 분리가 안 된다.

**수용 기준**

| Skill | 조건 | 유지 |
| --- | --- | --- |
| `analyze_meeting` | 항상 | ✓ |
| `review_action_items` | `decisions`에 `reject` 포함 | ✓ |
| `review_proposal` | `decision == "ignore"` | ✓ |
| `manage_tasks` | `action == "delete"` | ✓ |

**검증** W6-V1 / **우선순위** 필수

---

## W6-R11 — 의도적 변경의 범위

**설명** W1 스냅샷 27건 중 **2건만** 바뀌고 나머지 25건은 그대로다.

**대상**
- `assistant_ask.requires_confirmation`
- `assistant_ask.confirmed_execution`

**수용 기준**
- 25건 PASS(변경 없음)
- 2건은 새 기대값으로 갱신되고, 변경 전후가 증빙에 기록됨
- 다른 Skill의 케이스는 영향 없음

**검증** W6-V10 / **우선순위** 필수

---

## 요구사항 간 의존

```
W6-R1 (interrupt) ─┬→ W6-R2 (INPUT_REQUIRED) ─→ W6-R8 (UI)
                   ├→ W6-R3 (resume) ─┬→ W6-R5 (LLM 재호출 금지)
                   │                   └→ W6-R6 (Task 단일성)
                   └→ W6-R7 (취소)

W6-R4 (외부 상태 불변) ← 전 경로에 적용, 최우선
W6-R10 (판정 규칙 불변) ← 경계 조건
W6-R11 (변경 범위) ← 결과 검증
W6-R9 (문서) ← C1~C5 확정 후
```

## 참조

- [96번 §6·§7·§11](96-workmate-langgraph-target-architecture.md)
- [30-6-5](30-6-5-design.md) — 계약안과 구현 설계
- [30-6-7](30-6-7-verification.md) — 검증 케이스
