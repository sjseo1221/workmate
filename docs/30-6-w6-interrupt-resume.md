# W6 — 사용자 확인을 interrupt로, 공개 계약 개편

> **이 문서는 요약과 색인이다.** 각 절의 상세는 아래 13개 문서에 있고, 충돌 시 상세 문서를 기준으로
> 한다.
>
> | 절 | 상세 문서 | 내용 |
> | --- | --- | --- |
> | §1 | [30-6-1](30-6-1-document-info.md) | 문서 정보·용어·확인 대상 4종 |
> | §2 | [30-6-2](30-6-2-scope.md) | 목적, 현재/목표 동작, 범위 |
> | §3 | [30-6-3](30-6-3-entry-criteria.md) | 선행 조건 — **승인이 선행 조건에 포함** |
> | §4 | [30-6-4](30-6-4-requirements.md) | 요구사항 W6-R1~R11 |
> | §5 | [30-6-5](30-6-5-design.md) | 설계 — **계약안 C1~C5**, Subgraph, 불변식, UI |
> | §6 | [30-6-6](30-6-6-wbs.md) | 작업 분해 W6-T1~T10 |
> | §7 | [30-6-7](30-6-7-verification.md) | 검증 설계 W6-V1~V11 |
> | §8 | [30-6-8](30-6-8-traceability.md) | 추적성, 계약 항목 추적, **의도적 변경 누적** |
> | §9 | [30-6-9](30-6-9-exit-criteria.md) | 완료 정의 — **자동 승인 불가** |
> | §10 | [30-6-10](30-6-10-approval.md) | **승인 경계** |
> | §11 | [30-6-11](30-6-11-risks.md) | 위험 등록부 W6-K1~K10 |
> | §12 | [30-6-12](30-6-12-rollback.md) | 롤백·중단·재개 |
> | §13 | [30-6-13](30-6-13-references.md) | 참조 자료와 읽을 지점 |
>
> **W6의 특징 셋.**
> (1) **공개 계약을 의도적으로 바꾸는 유일한 단계**다. 스냅샷 27건 중 2건만 바뀌고 나머지 25건은
> 그대로여야 한다.
> (2) **자동 승인 대상이 아니다.** UI 육안 검수와 공개 계약 변경이 `AGENTS.md`의 자동 승인 예외에
> 해당한다. 승인이 **착수 전**(계약안 C1~C5)과 **완료 시**(육안 검수) 두 번 필요하다.
> (3) **"기능은 되는데 위험한" 상태가 셋 있다** — interrupt 이전 외부 상태 변경, resume 시 LLM
> 재호출, 멱등성 Key 충돌. 전부 겉보기에는 정상이라 전용 검증(W6-V2·V4·V5-4) 없이는 발견되지 않는다.

## 1. 문서 정보

| 항목 | 값 |
| --- | --- |
| 단계 | W6 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §4.1, §5 |
| 선행 단계 | [W5 진입점 교체](30-5-w5-entrypoint-swap.md) |
| 후행 단계 | [W7 레거시 삭제](30-7-w7-legacy-removal.md) |
| 상태 | 대기 |
| 관련 결정 | **D1=B** (공개 계약까지 개편), D5=A (폴링 유지) |
| 승인 필요 | §5.1 계약 설계안은 구현 착수 전 사용자 승인 대상 |

## 2. 목적과 범위

### 2.1 목적

"확인이 필요한 동작"의 처리 방식을 **응답 후 재요청**에서 **Graph 중단 후 재개**로 바꾸고, 그 변화를
공개 계약에 반영한다. 이 단계가 D1=B의 실체다.

### 2.2 현재 동작

```
1. 사용자: "그 Task 지워줘"
2. assistant_ask: 확인 필요 판정 → pending_action{skill_id, arguments}를 응답에 싣고 종료
   ※ 서버에는 아무 상태도 남지 않는다
3. UI: 확인 버튼 표시
4. 사용자 확인 → UI가 confirmed_skill_id·confirmed_arguments로 새 요청
5. assistant_ask: LLM 라우팅을 건너뛰고 즉시 실행
```

근거: [assistant_router.py:794-876](../workmate-agent/app/workflows/assistant_router.py#L794-L876),
[AssistantDrawer.tsx:123](../workmate-ui/app/views/AssistantDrawer.tsx#L123)

### 2.3 목표 동작

```
1. 사용자: "그 Task 지워줘"
2. Graph: 확인 필요 판정 → interrupt() → Checkpoint에 State 동결, Task는 INPUT_REQUIRED
3. UI: 폴링 중 INPUT_REQUIRED를 보고 확인 UI 표시
4. 사용자 확인 → 같은 thread_id로 resume
5. Graph: Checkpoint의 검증된 skill_id·arguments로 멈춘 자리에서 이어 실행
```

### 2.4 범위 내

- Assistant Subgraph의 `interrupt`/`Command(resume)` 도입
- `INPUT_REQUIRED` Task 상태 표면화
- 공개 계약 개편과 [02-a2a-interface.md](02-a2a-interface.md) 개정
- [AssistantDrawer.tsx](../workmate-ui/app/views/AssistantDrawer.tsx) 폴링 분기 추가
- [tools/m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py) 대응

### 2.5 범위 외

- 오케스트레이터 저장소(`AI-agent_game_platform`) 수정 — **별도 승인 대상** (§10)
- 스트리밍 전환 (D5=B, 전환 후 별건)

## 3. 선행 조건

| ID | 조건 | 확인 방법 |
| --- | --- | --- |
| W6-E1 | W5 완료, 운영 경로가 Graph | W5-V7 |
| W6-E2 | Checkpointer 동작 — `interrupt`의 성립 조건 | W4-V7 |
| W6-E3 | §5.1 계약 설계안 사용자 승인 | 승인 기록 |

## 4. 요구사항

| ID | 구분 | 요구사항 | 출처 |
| --- | --- | --- | --- |
| W6-R1 | 기능 | 확인이 필요한 동작에서 Graph가 `interrupt()`로 중단한다 | 96번 §6 |
| W6-R2 | 기능 | 중단 상태를 `INPUT_REQUIRED` Task 상태로 표면화한다 | 96번 §7 |
| W6-R3 | 기능 | 같은 `thread_id`로 resume하면 멈춘 지점부터 이어 실행한다 | 96번 §11-8 |
| W6-R4 | 제약 | **`interrupt` 이전에 외부 상태를 변경하지 않는다** | 96번 §11-7 |
| W6-R5 | 제약 | resume 시 Router LLM을 다시 호출하지 않고 Checkpoint의 검증된 값을 쓴다 | 96번 §6, 현행 동작 |
| W6-R6 | 제약 | resume은 새 Task를 만들지 않는다 | 96번 §11-8 |
| W6-R7 | 기능 | 사용자가 확인을 거부하면 `CANCELED`로 종료한다 | 96번 §6 |
| W6-R8 | 기능 | UI가 `INPUT_REQUIRED`를 인식해 확인 UI를 띄우고 resume을 요청한다 | D5=A |
| W6-R9 | 문서 | 공개 계약 변경을 02번 문서에 반영한다 | `AGENTS.md` 구현 규칙 |

## 5. 설계

### 5.1 공개 계약 설계안 (승인 대상)

다음 5개 항목이 이번에 확정할 계약이다. 구현 착수 전 사용자 승인을 받는다.

| 항목 | 설계안 | 대안 | 비고 |
| --- | --- | --- | --- |
| C1 Task 상태 | 확인 대기를 `TASK_STATE_INPUT_REQUIRED`로 노출 | — | 이 문자열은 현재 agent·UI 어디에도 없다 |
| C2 payload 위치 | interrupt payload(확인 문구·`skill_id`·`arguments`)를 `Task.status.message`에 싣는다 | Artifact로 싣기 | Artifact는 완료 결과의 자리이므로 status가 적합 |
| C3 resume 요청 | 같은 `task_id`에 대한 재개 요청으로 표현. 새 `message:send`가 아님 | 기존처럼 새 메시지 | A2A Route allowlist 변경 여부를 함께 검토 |
| C4 취소 | 확인 거부 시 `CANCELED` 전이 | `COMPLETED` + 취소 안내 | 96번 §7 상태 전이도를 따름 |
| C5 멱등성 | resume은 원 `message_id`의 멱등성 Key를 유지 | 새 Key 발급 | W6-R6 |

**C3이 가장 민감하다.** A2A Route allowlist는 현재 `message:send`·`message:stream`·`tasks/{id}`·
`tasks/{id}:cancel`·`tasks/{id}:subscribe` 5개다([runtime.py:325-331](../workmate-agent/app/a2a/runtime.py#L325-L331)).
resume을 어떤 Route로 표현할지에 따라 allowlist와 Contract Test가 바뀐다.

### 5.2 Assistant Subgraph 구조 (96번 §6)

```
START → load_conversation_context → resolve_context_references → route_with_llm
  ├─(reply)→ build_direct_reply ──────────────────┐
  ├─(clarify)→ build_clarifying_question ─────────┤
  └─(call_skill)→ validate_skill_and_arguments    │
                    → requires_confirmation?      │
                        ├─(아니오)→ call_selected_subgraph → phrase_answer ─┤
                        └─(예)→ interrupt(pending_action)                   │
                                 ├─(취소)→ build_canceled_reply ────────────┤
                                 └─(확인·resume)→ call_selected_subgraph ───┘
                                                        → build_assistant_reply → END
```

### 5.3 불변식 W6-R4의 구현

`interrupt` 이전에 외부 상태를 바꾸지 않는다 — 확인 대상 동작(Action Item 거절, 제안 무시, Task 삭제,
비용이 큰 회의 분석)은 **확인 뒤에만** 실행돼야 한다.

구현 규칙:

- `validate_skill_and_arguments`는 **검증만** 한다. Repository 쓰기 호출 금지.
- `requires_confirmation` 판정은 [`_requires_confirmation()`](../workmate-agent/app/workflows/assistant_router.py#L221)의
  현행 규칙을 그대로 옮긴다. 확인 대상 범위를 이번에 바꾸지 않는다.
- 검증 테스트: 확인 대기 상태에서 DB를 조회해 **변경이 없음**을 확인한다.

### 5.4 UI 변경 (D5=A)

현재 폴링 루프는 `COMPLETED`와 실패 3종만 처리한다.

```js
// AssistantDrawer.tsx:151-163 현재
if (state === "TASK_STATE_COMPLETED") { /* 결과 */ }
if (TERMINAL_FAILURE_STATES.has(state)) { /* 에러 */ }   // FAILED, CANCELED, REJECTED
// 그 외 → 1.5초 후 재폴링, 5분 타임아웃
```

`INPUT_REQUIRED`는 어느 쪽에도 안 걸려 **5분 폴링 후 타임아웃 에러**가 된다. 분기를 추가한다.

```js
if (state === "TASK_STATE_INPUT_REQUIRED") {
  // status.message에서 확인 payload를 꺼내 확인 UI 표시 → 폴링 중단
  // 사용자 확인 시 resume 요청, 거부 시 cancel
}
```

`CANCELED`가 현재 실패로 분류돼 있는 점도 함께 손본다(W6-R7의 정상 종료와 충돌).

### 5.5 오케스트레이터 어댑터

[tools/m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py)는 우리 저장소다. 어댑터가
새 프로토콜을 옛 모양으로 번역할 수 있으면 오케스트레이터 저장소를 건드리지 않아도 된다. W6-T1에서
가능 여부를 먼저 판정한다.

## 6. 작업 분해 (WBS)

| ID | 작업 | 선행 | 산출물 |
| --- | --- | --- | --- |
| W6-T1 | 계약 설계안 C1~C5 확정 + 어댑터 흡수 가능성 판정 | — | 설계안, **사용자 승인** |
| W6-T2 | Assistant Subgraph에 `interrupt` 도입 | W6-T1 | `skills/assistant_router.py` |
| W6-T3 | `INPUT_REQUIRED` 상태 전이·표면화 | W6-T2 | `runtime.py`, `internal_chat.py` |
| W6-T4 | resume 경로 구현 | W6-T3 | 진입점 + Graph |
| W6-T5 | 취소 경로 구현 | W6-T3 | `CANCELED` 전이 |
| W6-T6 | UI 폴링 분기·확인 UI·resume 호출 | W6-T4 | `AssistantDrawer.tsx` |
| W6-T7 | 어댑터 대응 | W6-T4 | `m51_legacy_adapter.py` |
| W6-T8 | 02번 문서 개정 | W6-T4 | `02-a2a-interface.md` |
| W6-T9 | 스냅샷 갱신(의도적 변경분 표시) | W6-T4 | `tests/contracts/` |
| W6-T10 | 증빙·커밋 | W6-T9 | `result.md` |

## 7. 검증 설계

| ID | 검증 항목 | 방법 | 판정 기준 |
| --- | --- | --- | --- |
| W6-V1 | interrupt 중단 | Task 삭제 요청 | `INPUT_REQUIRED`, Skill 미실행 |
| W6-V2 | 외부 상태 불변 | 중단 상태에서 DB 조회 | 변경 없음 |
| W6-V3 | resume 재개 | 같은 `thread_id` resume | 멈춘 노드부터 실행, 결과 반환 |
| W6-V4 | LLM 재호출 금지 | resume 시 LLM 호출 계측 | Router LLM 호출 0회 |
| W6-V5 | Task 단일성 | resume 후 Task 수 | 새 Task 미생성 |
| W6-V6 | 취소 경로 | 확인 거부 | `CANCELED`, 외부 상태 불변 |
| W6-V7 | UI 확인 흐름 | 로컬 UI 조작 | 확인 UI 표시 → 실행 → 결과 (**육안 검수**) |
| W6-V8 | 어댑터 | 어댑터 경유 요청 | 정의된 동작 |
| W6-V9 | 계약 문서 일치 | 02번 문서 ↔ 구현 | 불일치 없음 |
| W6-V10 | 전체 테스트 | 스위트 실행 | 실패 0 |

## 8. 추적성 매트릭스

| 요구사항 | 작업 | 검증 |
| --- | --- | --- |
| W6-R1 | W6-T2 | W6-V1 |
| W6-R2 | W6-T3 | W6-V1 |
| W6-R3 | W6-T4 | W6-V3 |
| W6-R4 | W6-T2 | W6-V2 |
| W6-R5 | W6-T4 | W6-V4 |
| W6-R6 | W6-T4 | W6-V5 |
| W6-R7 | W6-T5 | W6-V6 |
| W6-R8 | W6-T6 | W6-V7 |
| W6-R9 | W6-T8 | W6-V9 |

## 9. 완료 정의 (Exit criteria)

1. W6-V1~V6, V8~V10 PASS.
2. **W6-V7(UI 육안 검수)은 사용자 판정 대상** — 자동 승인 대상이 아니다(`AGENTS.md`).
3. 02번 문서가 개정되고 구현과 일치한다.
4. 스냅샷에서 의도적으로 바뀐 케이스가 변경 내역과 함께 기록된다.

## 10. 승인 경계

| 항목 | 처리 |
| --- | --- |
| 공개 A2A 계약 변경 | D1=B로 이미 승인됨. 단 §5.1 C1~C5의 **구체안은 W6-T1에서 재승인** |
| `workmate-ui` 수정 | 전환 범위 안 (계획서 §7.2 동결 구역) |
| 어댑터(`tools/`) 수정 | 우리 저장소, 범위 안 |
| **오케스트레이터 저장소 수정** | `AGENTS.md`상 **금지** — 필요하면 그 시점에 별도 승인 요청 |
| UI 육안 검수 | 사용자 판정, 자동 승인 불가 |

## 11. 위험과 완화

| 위험 | 영향 | 완화 |
| --- | --- | --- |
| `interrupt` 이전에 외부 상태가 바뀐다 | 확인 절차가 무의미해짐 | W6-V2를 필수 검증으로. 검증 노드에서 쓰기 호출 금지 |
| resume 시 LLM을 다시 불러 다른 Skill로 간다 | 사용자가 확인한 것과 다른 동작 실행 | W6-V4 계측. Checkpoint의 검증된 값만 사용 |
| UI가 `INPUT_REQUIRED`를 모르면 5분 타임아웃 | 확인 요청이 오류로 보임 | W6-T6을 W6-T4와 같은 커밋 범위로 묶는다 |
| 오케스트레이터가 새 프로토콜을 못 읽는다 | 팀 통합 경로 단절 | W6-T1에서 어댑터 흡수 가능성을 **먼저** 판정 |
| 계약 변경이 문서에 반영되지 않는다 | 다음 작업자가 옛 계약 기준으로 작업 | W6-V9 |

## 12. 롤백·중단 기준

- W6은 공개 계약과 UI를 동시에 바꾸므로 부분 롤백이 어렵다. `interrupt` 도입 커밋과 UI 커밋을 인접
  배치해 함께 revert할 수 있게 한다.
- **중단 기준:** W6-T1에서 어댑터로 흡수 불가 판정이 나고 오케스트레이터 수정 승인도 받지 못하면,
  A2A 경로는 기존 계약을 유지하고 내부 경로만 개편하는 축소안(D1의 C안)으로 되돌려 사용자에게 확인을
  받는다. 승인 없이 오케스트레이터를 수정하지 않는다.

## 13. 참조

- [96-workmate-langgraph-target-architecture.md](96-workmate-langgraph-target-architecture.md) §6, §7, §11
- [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §4.1
- [02-a2a-interface.md](02-a2a-interface.md) — 개정 대상
