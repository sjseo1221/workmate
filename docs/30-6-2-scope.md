# W6-2 — 목적과 범위

> [30-6-w6-interrupt-resume.md](30-6-w6-interrupt-resume.md) §2의 상세 문서.

## 1. 목적

"확인이 필요한 동작"의 처리 방식을 **응답 후 재요청**에서 **Graph 중단 후 재개**로 바꾸고, 그 변화를
공개 계약에 반영한다. 이 단계가 D1=B의 실체다.

### 1.1 현재 동작의 상세

```python
# assistant_router.py:869-876
if _requires_confirmation(skill_id, arguments):
    pending_action = {"skill_id": skill_id, "arguments": arguments}
    return WorkflowResult(
        text=json.dumps({"type": "assistant_reply",
                         "data": {"reply": confirm_reply,
                                  "executed_skill_id": None,
                                  "pending_action": pending_action}}),
        ...
    )
```

함수가 **그냥 끝난다.** 서버에는 아무 상태도 남지 않는다.

```js
// AssistantDrawer.tsx:123
? assistantAskInput(text, { confirmedSkillId: confirm.skillId,
                            confirmedArguments: confirm.arguments })
```

사용자가 확인하면 UI가 **새 요청**을 만든다.

```python
# assistant_router.py:794-800
confirmed_skill_id = payload.get("confirmed_skill_id")
if confirmed_skill_id:
    if confirmed_skill_id not in _ROUTABLE_SKILL_IDS:
        raise ValueError(f"unknown confirmed_skill_id: {confirmed_skill_id}")
    skill_id = str(confirmed_skill_id)
    # route()를 다시 안 부른다
```

서버는 `confirmed_skill_id`를 받아 LLM 라우팅을 건너뛰고 실행한다.

### 1.2 현재 방식의 특징

| 항목 | 평가 |
| --- | --- |
| 서버 상태 없음 | 단순하다. 서버 재시작에 영향 없음 |
| 재개 시 LLM 미호출 | 이미 구현돼 있다 — 비용·일관성 측면에서 올바름 |
| 중간 State 유실 | 대화 컨텍스트·해소된 참조가 사라진다 |
| Task 추적 불가 | 확인 대기 중인 Task가 상태로 드러나지 않는다 |
| 취소 정의 없음 | 사용자가 확인을 거부하면 아무 일도 안 일어난다 |
| 클라이언트 신뢰 | `confirmed_skill_id`를 클라이언트가 만들어 보낸다 |

마지막 항목이 미묘하다. 현재 코드는 `_ROUTABLE_SKILL_IDS` 검사로 보호하지만, **서버가 제안하지 않은
조합도 클라이언트가 보낼 수 있다.**

### 1.3 목표 동작

```
1. 사용자 요청
2. Graph: route_with_llm → validate → requires_confirmation? → interrupt()
   ├ Checkpoint에 State 동결 (skill_id, arguments, 대화 컨텍스트 전부)
   └ Task: INPUT_REQUIRED
3. UI: 폴링 중 INPUT_REQUIRED 감지 → 확인 UI
4. 사용자 확인 → 같은 thread_id로 resume
5. Graph: Checkpoint에서 State 복원 → call_selected_subgraph → phrase_answer
```

### 1.4 목표 방식의 이득

| 이득 | 설명 |
| --- | --- |
| 중간 State 보존 | 대화 컨텍스트·해소된 참조가 유지된다 |
| 서버가 제안을 소유 | 클라이언트가 임의 조합을 보낼 수 없다 |
| Task 추적 | 확인 대기가 `INPUT_REQUIRED`로 드러난다 |
| 취소 정의 | `CANCELED` 전이 |
| 구조적 일관성 | 96번 §6·§7 설계와 일치 |

## 2. 범위 내 (In scope)

| ID | 항목 | 산출물 |
| --- | --- | --- |
| S1 | Assistant Subgraph의 `interrupt`/`Command(resume)` | `skills/assistant_router.py` |
| S2 | `INPUT_REQUIRED` Task 상태 표면화 | `runtime.py`, `internal_chat.py` |
| S3 | resume 경로 | 진입점 + Graph |
| S4 | 취소 경로(`CANCELED`) | 동상 |
| S5 | UI 폴링 분기·확인 UI·resume 호출 | [AssistantDrawer.tsx](../workmate-ui/app/views/AssistantDrawer.tsx) |
| S6 | 어댑터 대응 | [tools/m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py) |
| S7 | [02-a2a-interface.md](02-a2a-interface.md) 개정 | 문서 |
| S8 | 스냅샷 갱신(의도적 변경분) | `tests/contracts/` |

## 3. 범위 외 (Out of scope)

| 항목 | 이유 |
| --- | --- |
| **오케스트레이터 저장소 수정** | `AGENTS.md`상 금지. **별도 승인 대상**([30-6-10](30-6-10-approval.md)) |
| 확인 대상 판정 규칙 변경 | 4종을 그대로 유지. 범위를 넓히거나 좁히지 않는다 |
| 스트리밍 전환 | D5=A. 전환 완료 후 별건 |
| Skill 로직 변경 | W3에서 끝났다 |
| `app/workflows/` 삭제 | [W7](30-7-w7-legacy-removal.md) |
| 다른 Skill에 `interrupt` 도입 | `assistant_ask` 경유 확인만 대상 |

### 3.1 확인 판정 규칙을 안 바꾸는 이유

`_requires_confirmation()`의 4종은 2026-08-17 사용자 요청으로 확정된 범위다. W6은 **처리 방식**을
바꾸는 것이지 **무엇을 확인할지**를 바꾸는 것이 아니다.

둘을 같이 바꾸면 "확인이 안 뜬다"는 문제가 생겼을 때 판정 규칙 문제인지 interrupt 문제인지 모른다.

### 3.2 오케스트레이터 경계

`AGENTS.md`:

> 오케스트레이터(`AI-agent_game_platform`) 저장소는 사용자가 그때그때 명시적으로 허용한 경우에만
> 수정한다. 버그를 발견해도 그 자리에서 직접 고치지 않고 먼저 사용자에게 보고해 승인을 받는다.
> 이 규칙은 로컬 실행 확인·디버깅처럼 되돌리기 쉬운 상황에도 예외 없이 적용된다.

W6-T1에서 **어댑터로 흡수 가능한지 먼저 판정**한다. 불가능하면 그 시점에 승인을 요청한다.

## 4. 범위 변경 절차

| 상황 | 처리 |
| --- | --- |
| 계약안 C1~C5 세부 조정 | W6-T1에서 확정. 승인 후 변경은 재승인 |
| UI 변경이 예상보다 큼 | 범위 내. 단 확인 UX 자체를 재설계하면 범위 이탈 |
| 어댑터로 흡수 불가 | **중단하고 승인 요청** |
| Route allowlist 변경 필요 | C3의 결과일 수 있다. 승인 대상 |
| 확인 판정 규칙 변경 필요 | 범위 이탈. 별도 백로그 |

## 5. 성공 기준

W6의 성공은 두 가지다.

| # | 기준 | 검증 |
| --- | --- | --- |
| 1 | 확인·재개·취소가 `interrupt` 기반으로 동작한다 | W6-V1~V6 |
| 2 | **의도적으로 바꾼 것 외에는 아무것도 안 바뀌었다** | 스냅샷 25건 PASS |

2번이 중요하다. W1 케이스 27건 중 `assistant_ask.requires_confirmation`·`confirmed_execution` 2건만
바뀌고 나머지 25건은 그대로여야 한다.

## 6. 참조

- [96번 §6](96-workmate-langgraph-target-architecture.md) — Assistant Router Subgraph와 확인 시퀀스
- [96번 §7](96-workmate-langgraph-target-architecture.md) — Task 상태 전이도
- [30-6-5](30-6-5-design.md) — 계약안과 구현 설계
- [30-6-10](30-6-10-approval.md) — 승인 경계
