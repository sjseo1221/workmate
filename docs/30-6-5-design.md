# W6-5 — 설계

> [30-6-w6-interrupt-resume.md](30-6-w6-interrupt-resume.md) §5의 상세 문서.

## 1. 공개 계약 설계안 (승인 대상)

다음 5개 항목이 이번에 확정할 계약이다. **구현 착수 전 사용자 승인을 받는다**([W6-E3](30-6-3-entry-criteria.md)).

### C1 — Task 상태 노출

| | 안 | 평가 |
| --- | --- | --- |
| **a** | **확인 대기를 `TASK_STATE_INPUT_REQUIRED`로 노출** | **권장** — 96번 §7 상태 전이도와 일치. A2A 표준 상태 |
| b | `WORKING` 유지 + 별도 필드로 표시 | 상태만 보는 클라이언트가 구분 못 함 |

**권장: a.** 현재 이 문자열은 agent·UI 어디에도 없으므로 **새로 도입하는 것**이다.

### C2 — interrupt payload 전달 위치

확인 문구·`skill_id`·`arguments`를 어디에 싣는가.

| | 안 | 평가 |
| --- | --- | --- |
| **a** | **`Task.status.message`** | **권장** — 상태에 부속된 정보. 이미 실패 메시지가 여기 들어간다 |
| b | Artifact | Artifact는 **완료 결과**의 자리. 미완료 상태에 Artifact를 넣으면 의미가 흐려진다 |
| c | Task metadata | 조회 경로가 하나 더 생긴다 |

**권장: a.** 선례가 있다 — [`_save_task_status()`](../workmate-agent/app/internal_chat.py#L276)가
실패 원인을 `status.message`에 담는다.

```python
status.message.CopyFrom(Message(
    message_id=f"internal-{task_id}-status",
    role=Role.ROLE_AGENT,
    parts=[Part(text=message_text)],
))
```

확인 payload도 같은 자리에 구조화 Part로 싣는다.

### C3 — resume 요청 형태 (가장 민감)

**왜 민감한가** A2A Route allowlist가 현재 5개다
([runtime.py:325-331](../workmate-agent/app/a2a/runtime.py#L325)).

```
{prefix}/message:send          POST
{prefix}/message:stream        POST
{prefix}/tasks/{id}            GET, HEAD
{prefix}/tasks/{id}:cancel     POST
{prefix}/tasks/{id}:subscribe  POST
```

`AGENTS.md`: "승인된 MVP Route allowlist만 등록하고 제외 Route의 `404` 또는 `405` Contract Test를
유지한다." allowlist 변경은 승인 대상이다.

| | 안 | Route | 평가 |
| --- | --- | --- | --- |
| **a** | **기존 `message:send`에 resume 표식을 실어 보냄** | 변경 없음 | **권장** — allowlist 무변경 |
| b | 새 Route(`tasks/{id}:resume`) 추가 | **allowlist 확대** | 의미는 명확하나 승인 범위가 커진다 |
| c | `tasks/{id}:cancel`처럼 기존 Route 재활용 | 변경 없음 | 취소용 Route에 재개를 얹는 것은 혼란 |

**권장: a.** 요청 payload에 `task_id`와 resume 의사를 담는다. 예:

```json
{"resume": {"task_id": "...", "decision": "confirm"}}
```

또는 `{"resume": {"task_id": "...", "decision": "cancel"}}`.

**단, SDK가 이를 허용하는지 W6-T1에서 확인한다.** a2a-sdk 1.1.2의 `message:send` 핸들러가 임의
payload를 통과시키는지, Task를 이어받는 방식을 지원하는지에 따라 b가 불가피할 수 있다.

### C4 — 취소

| | 안 | 평가 |
| --- | --- | --- |
| **a** | **`CANCELED` 전이** | **권장** — 96번 §7 전이도 |
| b | `COMPLETED` + 취소 안내 | 취소를 정상 완료로 기록하면 이력이 왜곡된다 |

**권장: a.**

**주의:** UI의 `TERMINAL_FAILURE_STATES`에 `TASK_STATE_CANCELED`가 들어 있다
([AssistantDrawer.tsx:42](../workmate-ui/app/views/AssistantDrawer.tsx#L42)). 취소를 오류로 표시하지
않으려면 UI에서 이 분류를 분리해야 한다.

### C5 — 멱등성 Key

| | 안 | 평가 |
| --- | --- | --- |
| **a** | **resume은 원 `message_id`의 멱등성 Key를 유지** | **권장** — 96번 §11-8 |
| b | resume에 새 `message_id` 발급 | 같은 논리적 요청이 둘로 갈린다 |

**권장: a.**

**주의:** [`record_message()`](../workmate-agent/app/a2a/persistence.py#L210)는 같은 `message_id`를
두 번 쓰면 payload 해시가 다를 때 `ValueError`를 낸다. resume 요청의 payload가 원 요청과 다르므로
**해시가 달라진다.**

→ 멱등성 기록 시점을 조정해야 한다. W4의 `persist_result`가 **최종 완료 시 한 번만** 기록하는 구조
(현재 [internal_chat.py](../workmate-agent/app/internal_chat.py)의 `_save_task_status()`가 취하는
방식)를 resume 경로에도 적용한다.

### 1.1 계약안 요약표

| ID | 항목 | 권장안 | Route 영향 | UI 영향 |
| --- | --- | --- | --- | --- |
| C1 | Task 상태 | `INPUT_REQUIRED` | 없음 | **있음** |
| C2 | payload 위치 | `Task.status.message` | 없음 | 있음 |
| C3 | resume 형태 | `message:send`에 표식 | **없음(a안)** | 있음 |
| C4 | 취소 | `CANCELED` | 없음 | 있음 |
| C5 | 멱등성 | 원 Key 유지 | 없음 | 없음 |

**권장안 조합은 Route allowlist를 바꾸지 않는다.** 이것이 a안들을 권하는 주된 이유다.

---

## 2. Assistant Subgraph 구조

[96번 §6](96-workmate-langgraph-target-architecture.md)을 따른다.

```
START → load_conversation_context → resolve_context_references → route_with_llm
  ├─(reply)→ build_direct_reply ──────────────────────────────┐
  ├─(clarify)→ build_clarifying_question ─────────────────────┤
  └─(call_skill)→ validate_skill_and_arguments                │
                    → requires_confirmation?                  │
                        ├─(아니오)→ call_selected_subgraph ───┤
                        └─(예)→ interrupt(pending_action)     │
                                 ├─(취소)→ build_canceled_reply┤
                                 └─(확인)→ call_selected_subgraph
                                              ↓               │
                                         phrase_answer ───────┤
                                                              ↓
                                                   build_assistant_reply → END
```

### 2.1 W3에서 준비된 것

[W3-D5](30-3-5-design.md) §6에서 `build_pending_action_reply`를 독립 노드로 두었다. W6은 **이 노드를
`interrupt()`로 교체**한다.

```
W3:  requires_confirmation? → build_pending_action_reply → END
W6:  requires_confirmation? → interrupt(...) → (재개) call_selected_subgraph
```

노드 경계가 이미 나뉘어 있어 교체 범위가 한 노드로 제한된다.

---

## 3. 외부 상태 불변식 구현 (W6-R4)

### 3.1 노드별 허용 동작

| 노드 | 읽기 | 쓰기 |
| --- | --- | --- |
| `load_conversation_context` | ✓ | ✗ |
| `resolve_context_references` | ✓ | ✗ |
| `route_with_llm` | ✓ (LLM 호출) | ✗ |
| `validate_skill_and_arguments` | ✓ | **✗** |
| `requires_confirmation?` | ✓ | ✗ |
| `interrupt` | — | Checkpoint만 |
| `call_selected_subgraph` | ✓ | **✓ (여기서부터 허용)** |

### 3.2 검증 방법

확인 대상 4종 각각에 대해 "확인 대기 상태에서 DB를 조회해 변경이 없음"을 확인한다.

| Skill | 확인할 것 |
| --- | --- |
| `manage_tasks` (delete) | Task가 아직 존재 |
| `review_proposal` (ignore) | 제안 상태 불변 |
| `review_action_items` (reject) | Action Item 승인 상태 불변 |
| `analyze_meeting` | 분석 결과·transcript 미생성 |

### 3.3 W3에서 이미 확인했어야 하는 것

[W3-V11-4](30-3-7-verification.md)가 같은 항목을 본다. W3 시점의 `build_pending_action_reply` 경로에서
이미 외부 상태가 바뀌고 있다면, W6에서 `interrupt`로 바꿔도 불변식이 깨진 채 남는다.

---

## 4. UI 설계 (W6-R8)

### 4.1 현재 폴링 루프

```js
// AssistantDrawer.tsx:151-163
while (Date.now() - startedAt < POLL_TIMEOUT_MS) {       // 5분
  const task = await skillChatApi.getTask(auth, submitted.task_id);
  const state = task.status.state;
  if (state === "TASK_STATE_COMPLETED") { finalText = ...; break; }
  if (TERMINAL_FAILURE_STATES.has(state)) { throw new ApiError(...); }
  await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));  // 1.5초
}
if (!finalText) throw new ApiError("시간 내에 끝나지 않았습니다. ...");
```

`INPUT_REQUIRED`는 두 조건 어디에도 안 걸려 **5분을 헛돌다 타임아웃**한다.

### 4.2 변경안

```js
if (state === "TASK_STATE_INPUT_REQUIRED") {
  // status.message에서 확인 payload 추출 → 확인 UI 표시 → 폴링 중단
  break;
}
if (state === "TASK_STATE_CANCELED") {
  // 정상 종료로 처리 (실패 아님)
  break;
}
if (TERMINAL_FAILURE_STATES.has(state)) { throw ... }   // CANCELED 제거
```

### 4.3 확인 후 동작

```
현재:  assistantAskInput(text, {confirmedSkillId, confirmedArguments}) → 새 요청
W6:    resume 요청(C3의 형태) → 같은 task_id로 이어하기 → 폴링 재개
```

### 4.4 설계 결정 W6-D1 — 폴링을 재개한다

resume 후 결과를 어떻게 받는가.

| | 안 | 평가 |
| --- | --- | --- |
| a | resume 응답에 결과를 담는다 | 오래 걸리는 Skill에서 타임아웃 |
| **b** | **resume은 수락만 응답하고 폴링 재개** | **채택** — D5=A(폴링 유지)와 일관 |

`analyze_meeting`은 확인 대상이면서 오래 걸린다. a안이면 resume 요청이 몇 분간 열려 있게 된다.

---

## 5. 어댑터 대응

[tools/m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py)는 우리 저장소다.

### 5.1 흡수 가능성 판정 (W6-T1)

| 질문 | 판정 |
| --- | --- |
| 어댑터가 `INPUT_REQUIRED` Task를 받아 옛 `pending_action` 모양으로 번역할 수 있는가 | 확인 필요 |
| 오케스트레이터의 확인 응답을 resume으로 번역할 수 있는가 | 확인 필요 |
| 오케스트레이터가 확인 UI를 그리는 코드를 갖고 있는가 | **확인 필요 — 이것이 관건** |

마지막이 핵심이다. 오케스트레이터가 `pending_action`을 읽어 버튼을 그린다면, 어댑터가 옛 모양을
유지하는 한 그쪽은 수정이 필요 없다.

### 5.2 흡수 불가 시

[30-6-10](30-6-10-approval.md) §3의 절차를 따른다. 승인 없이 오케스트레이터를 수정하지 않는다.

---

## 6. 스냅샷 갱신 절차

W6은 W1 기록 모드를 **정당하게 사용하는 유일한 단계**다([30-1-12](30-1-12-handoff.md) §5.1).

```
1. 변경 전 대조 실행 → 2건 FAIL 확인 (예상된 실패)
2. 차이를 경로 단위로 기록 → "공개 계약 변경 내역"
3. 기록 모드로 스냅샷 갱신 (WORKMATE_SNAPSHOT_RECORD=1)
4. 커밋 diff로 변경 내용 검토
5. 변경 전후를 증빙에 나란히 기록
```

**3번 외의 기록 모드 실행은 사고다.**

---

## 7. 설계 결정 요약

| ID | 결정 | 근거 |
| --- | --- | --- |
| C1~C5 | §1의 권장안 | 승인 대상 |
| W6-D1 | resume 후 폴링 재개 | §4.4 |
| W6-D2 | `build_pending_action_reply` 노드만 교체 | §2.1 |
| W6-D3 | 멱등성 기록은 최종 완료 시 한 번 | §1의 C5 주의 |
| W6-D4 | UI에서 `CANCELED`를 실패 분류에서 제외 | §4.2 |

## 8. 참조

- [96번 §6·§7·§11](96-workmate-langgraph-target-architecture.md)
- [02-a2a-interface.md](02-a2a-interface.md) — 개정 대상
- [30-3-5](30-3-5-design.md) §6 — W3의 노드 경계 준비
- [30-6-10](30-6-10-approval.md) — 승인 경계
