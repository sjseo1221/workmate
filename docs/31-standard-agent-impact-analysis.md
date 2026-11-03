# 31. 표준 Agent 방식 전환 영향도 분석 (조사 문서)

작성일: 2026-09-30
성격: **조사·기록용.** 구현 항목이 아니며, 이 문서로 결정하지 않는다.
관련: [30 LangGraph 전환 계획](30-langgraph-migration-plan.md) · [30-10 ReAct 전환](30-10-w10-react-agent.md) · [05 AI·보안·운영](05-ai-security-operations.md)

> **왜 이 문서가 있나.** "LangChain·LangGraph로 에이전트를 만드는 널리 쓰이는 방식이 무엇이고,
> 기존 `workmate-agent`를 그 방식으로 바꾸면 영향이 어디까지인가"를 조사한 결과다. 계획서
> W0~W10은 이 조사 이전에 작성됐고, 조사 결과 **일부 전제가 달라졌다.** 어떻게 반영할지는
> 아직 결정하지 않았다.

## 1. 표준 방식이 무엇인가

실제로 설치해 실행하여 확인한 사실이다.

| 요소 | 표준 |
| --- | --- |
| 진입점 | `from langchain.agents import create_agent` |
| 구 경로 | `langgraph.prebuilt.create_react_agent` — **DeprecationWarning, v2.0 제거 예정** |
| 형태 | **에이전트 1개 + 도구 N개.** 외부에 보이는 진입점은 하나 |
| 무엇을 할지 | **항상 LLM이 결정** |
| 상태 | messages 중심(`AgentState`) |
| 확인·예산·재시도 | **middleware** |
| 진행 순서 | prebuilt → middleware → `StateGraph`(필요할 때만) |

### 1.1 `langchain` 본체가 표준 진입점을 소유한다

**계획서의 전제와 어긋나는 첫 번째 지점이다.** 0.x 시절 `langchain` 본체는 레거시 체인과
`AgentExecutor`였고, 그래서 [W9-R11](30-9-4-requirements.md)의 "안 쓰는 것" 목록에 들어 있었다.
1.x 본체는 `create_agent` + middleware로 재작성되어 **표준 에이전트 진입점 자체**가 됐다.

단, `AgentExecutor`를 쓰지 않는다는 항목은 그대로 유효하다. `create_agent`는 LangGraph
`CompiledStateGraph`를 반환하며 `AgentExecutor`와 무관하다.

### 1.2 제공되는 middleware

Python `>=3.12,<3.13`(workmate 제약)에서 해석되는 `langchain==1.3.2` 기준 **14개**다.

```
AgentMiddleware, ContextEditingMiddleware, FilesystemFileSearchMiddleware,
HumanInTheLoopMiddleware, LLMToolSelectorMiddleware, ModelCallLimitMiddleware,
ModelFallbackMiddleware, ModelRetryMiddleware, PIIMiddleware, ShellToolMiddleware,
SummarizationMiddleware, TodoListMiddleware, ToolCallLimitMiddleware, ToolRetryMiddleware
```

**계획이 직접 만들기로 한 것과 겹치는 것이 넷이다.**

| 계획 항목 | 표준 middleware | 검증 |
| --- | --- | --- |
| W6 확인 게이트 + `_requires_confirmation()` 4종 | `HumanInTheLoopMiddleware(interrupt_on={...})` | **실행 확인** |
| W10-D5 루프 예산(반복 상한) | `ModelCallLimitMiddleware(run_limit=)` | **실행 확인** |
| W10 "같은 도구 연속 2회" | `ToolCallLimitMiddleware(tool_name=, run_limit=)` | **실행 확인** |
| W8 LLM 재시도 2종 | `ModelRetryMiddleware(max_retries=, retry_on=)` | 시그니처 확인 |
| (계획에 없음) | `ToolRetryMiddleware(tools=, retry_on=)` | **실행 확인** |

`HumanInTheLoopMiddleware`는 `InterruptOnConfig(when=lambda request: ...)`로 **조건부 확인**을
지원한다. workmate의 확인 규칙 4종(`action=="delete"`일 때만, `decision=="reject"`가 있을 때만 …)을
그대로 표현할 수 있다.

## 2. 구조적 차이 — 진입점 개수

| | 표준 | workmate 현재 |
| --- | --- | --- |
| 외부 공개면 | 에이전트 1개 | Agent Card에 **Skill 11개**([runtime.py:66](../workmate-agent/app/a2a/runtime.py#L66)) |
| 결정 주체 | 항상 LLM | 호출자가 `skill_id`로 지정 |
| 응답 | messages(+`structured_response`) | **A2A Artifact** — DataPart(JSON) + text/markdown |
| 상태 | messages | `data`·`markdown`·`warnings`·`task_state` |

### 2.1 호출자별 현황 (실측)

| 호출자 | 호출하는 것 | 성격 |
| --- | --- | --- |
| 오케스트레이터 | 어댑터가 문장을 `assistant_ask`로 넘김([m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py)) | **이미 단일 진입점** |
| [AssistantDrawer.tsx](../workmate-ui/app/views/AssistantDrawer.tsx) | `assistant_ask` **하나** | 자연어 |
| [Briefing.tsx](../workmate-ui/app/views/Briefing.tsx) | `daily_briefing`·`rank_priorities` | **버튼** |
| [Report.tsx](../workmate-ui/app/views/Report.tsx) | `weekly_report` | 버튼 |
| [Search.tsx](../workmate-ui/app/views/Search.tsx) | `search_meetings` | 버튼 |
| [Archive.tsx](../workmate-ui/app/views/Archive.tsx) | `analyze_meeting` | 버튼 |

Drawer가 `analyze_meeting`·`manage_tasks`·`review_action_items`를 직접 부른다는 것은 **사실이
아니다** — 주석과 확인 대기 판정용 문자열 비교다.

`read_email`만 UI에서 쓰이지 않고 나머지 10개는 [workmate-format.ts](../workmate-ui/lib/workmate-format.ts)에
입력 조립 함수가 있다.

### 2.2 기술적 충돌 넷

| # | 충돌 | 근거 |
| --- | --- | --- |
| 1 | **Artifact `data`를 LLM이 다시 쓰게 된다** | 표준에서 최종 응답은 LLM이 만든다. workmate `data`는 Domain 계산값(점수·`source_refs`)과 같아야 한다 |
| 2 | **`response_format`은 에이전트당 1개** | 타입이 `ResponseFormat \| type \| dict \| None` — 단일(**실행 확인**). Skill 11개의 서로 다른 Schema를 담을 수 없다 |
| 3 | **`warnings` 채널이 `AgentState`에 없다** | `daily_briefing`의 3층 부분 실패, Provider 장애 부분 결과를 표현할 자리가 없다 |
| 4 | **UI가 `skill_id`로 응답 포맷을 분기한다** | [workmate-format.ts:282](../workmate-ui/lib/workmate-format.ts#L282) `switch (type)`. 진입점이 하나가 되면 판별자가 소실된다 |

## 3. 선택지 셋

| | 내용 | 대가 |
| --- | --- | --- |
| **A** | `assistant_ask`만 표준(`create_agent` + middleware). 나머지 10개는 공개 Skill 유지 | 진입점 둘 공존 |
| B | 11개를 도구로 접고 에이전트 1개만 공개 | UI 버튼 4화면 재작성 + **결정성 퇴행** |
| C | 현재 계획 유지(커스텀 `StateGraph`만) | middleware 이득 포기 |

### 3.1 B안을 권하지 않는 이유

"오늘 브리핑"은 판단할 여지가 없는 버튼이다. LLM을 끼우면

```
버튼 클릭 → LLM: 어느 도구? → daily_briefing → LLM: 문장으로
          LLM 호출 0회 → 최소 2회, 비용·지연 발생
```

그리고 **LLM이 `rank_priorities`를 고르면 화면이 빈다** — 지금은 구조적으로 불가능한 실패다.

### 3.2 A안이 이미 현재 구조와 같은 모양이다

[runtime.py:72-75](../workmate-agent/app/a2a/runtime.py#L72) 주석에 `assistant_ask`가 "나머지 10개 중
무엇을 호출할지 LLM으로 판단하는 Meta Skill"이라고 적혀 있다. **A안은 그 안쪽만 표준으로 바꾸는
것이고 공개면은 건드리지 않는다.**

같은 10개가 두 얼굴을 갖는다 — 버튼이 부를 때는 공개 Skill, `assistant_ask`가 부를 때는 도구.

## 4. A안 영향도 — 심볼 단위

[assistant_router.py](../workmate-agent/app/workflows/assistant_router.py) 937줄.

| 줄 | 크기 | 심볼 | A안에서 |
| --- | --- | --- | --- |
| 61–197 | **137** | `_SKILL_CATALOG` | **4갈래로 분해 이전**(W10-D7) |
| 255–332 | 78 | `_chat_completion` | 삭제 → `ChatOpenAI` |
| 632–699 | 68 | `route` | 삭제 → ReAct 루프 |
| 525–580 | 56 | `_resolve_context_reference` | 삭제 → 도구로 조회 후 판단 |
| 700–747 | 48 | `phrase_answer` | 삭제 → 에이전트 최종 답변 |
| 333–371 | 39 | `_ARGUMENTS_SCHEMA` | 삭제 → 도구별 Schema |
| 613–631 | 19 | `_history_messages` | 삭제 → Checkpointer |
| 581–597 | 17 | `_format_match_hint` | 삭제 |
| 372–383 | 12 | `_ROUTE_SCHEMA` | 삭제 → tool calling |
| 246–254 | 9 | `RoutedAction` | 삭제 |
| 384–391 | 8 | `_ANSWER_SCHEMA` | 삭제 |
| | **~354** | | **삭제 소계** |
| 221–245 | 25 | `_requires_confirmation` | **middleware 설정으로 이전** |
| 207–220 | 14 | `_ROUTABLE_SKILL_IDS` | 도구 목록으로 대체 |
| 771–916 | **146** | `assistant_ask_workflow` | **재작성**(Artifact 조립만 남김) |
| 398–451 | 54 | context 조회 2개 | 유지 — Repository 호출 |
| 452–516 | 65 | context 조립·포맷 | 대부분 유지 — 프롬프트 주입 |
| 748–770 | 23 | `_default_proposal_task` | 유지 |
| 917–938 | 22 | `_offer_to_add_action_items_as_tasks` | 유지 |
| 598–609 | 12 | `_today` | 유지 — 날짜는 코드 |

**937줄 중 ~354줄 삭제, 146줄 재작성, 137줄 분해 이전, ~180줄 유지.**

### 4.1 계약이 바뀌는 두 곳

**`_history_messages` 삭제.** 지금 UI가 `history`(최대 10턴)를 매 요청에 보낸다. Checkpointer +
`thread_id`로 가면 서버가 들고 있으므로 UI가 보낼 필요가 없다 — `assistantAskInput` 인자가 줄어든다.

**`_resolve_context_reference` 삭제.** "그거 정리해줘"의 지시 대상을 별도 LLM 호출로 찾는 함수다.
ReAct는 도구로 먼저 조회한 뒤 판단하므로 전용 호출이 불필요하다. **LLM 호출이 하나 줄어든다.**

### 4.2 UI 영향

| 파일 | 전체 | 챗봇 관련 | 내용 |
| --- | --- | --- | --- |
| [workmate-format.ts](../workmate-ui/lib/workmate-format.ts) | 460 | **~55** | `assistantAskInput`(216–236), `parseAssistantReply`(245–270), 타입 5개(184–239) |
| [AssistantDrawer.tsx](../workmate-ui/app/views/AssistantDrawer.tsx) | 268 | ~60 | 확인 배너·재요청(84–143), Envelope 파싱(166) |
| [workmate-format.test.mts](../workmate-ui/tests/workmate-format.test.mts) | 445 | 일부 | `parseAssistantReply` 케이스 |

**나머지 405줄은 버튼 화면용이라 무변경이다.** B안이면 460줄 전부 + 판별자 대체 설계가 필요하다.

바뀌는 타입 셋.

```ts
AssistantPendingAction = { skill_id, arguments }                → interrupt payload 구조
AssistantReply = { reply, executed_skill_id, pending_action }   → executed_skill_ids 복수 + 상태
AssistantAskHistoryTurn                                         → 삭제
```

### 4.3 실사용 문제 하나가 해소된다

[AssistantDrawer.tsx:84-93](../workmate-ui/app/views/AssistantDrawer.tsx#L84)의 기록이다.

> 확인 대기 중인 `review_action_items`의 문맥을 다음 요청에 다시 실어 보내야 한다 — 이 정보가 없어
> `manage_tasks`로 잘못 빠지면서 회의 근거 링크(`meeting_evidence`)가 유실된 사례가 있었다.

서버에 상태가 없어 UI가 문맥을 재전송하는 구조다. 표준 방식에서는 그 문맥이 Checkpoint에 얼어붙어
있어 **UI가 다시 보낼 필요가 없다.**

### 4.4 어댑터 영향과 미해결 항목

[m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py) 283줄.

| 항목 | 영향 |
| --- | --- |
| 진입점 | 무변경 — 계속 `assistant_ask` |
| 응답 변환 | Envelope 구조가 바뀌면 수정 |
| 확인 흐름 | **미해결** — 오케스트레이터에 확인 UI가 없다 |

지금은 `pending_action`을 무시해도 Task가 완료된다. `INPUT_REQUIRED`로 멈추면 **Task가 끝나지
않는다.** 어댑터가 자동 승인할지, 확인을 문장으로 되물을지 결정이 필요하다.

### 4.5 테스트 영향

| 파일 | 줄 | 영향 |
| --- | --- | --- |
| [test_assistant_router.py](../workmate-agent/tests/test_assistant_router.py) | **1,019** | 전면 재작성 |
| test_internal_chat.py | 451 | 부분 |
| test_m51_legacy_adapter.py | 253 | 부분 |
| test_weekly_classification.py | 106 | 소폭 |
| **합계** | **1,829** | 계획의 "의존 18개 파일 4,675줄" 중 |

## 5. W1~W10 변경 필요 여부

| 단계 | 변경 | 이유 |
| --- | --- | --- |
| **W1** 계약 스냅샷 | **불필요** (+케이스 2건 권장) | 현재 동작 기록이므로 무영향 |
| **W2** Graph 골격 | **필요** | 의존성·`llm.py`·재시도 소유권 |
| **W3** Skill Subgraph | 작음 | 10개 그대로. "도구로도 불린다" 요구 추가 |
| **W4** Root Graph | 작음 | `assistant_ask` 분기가 에이전트 Subgraph를 가리킴 |
| **W5** 진입점 교체 | **불필요** | `ainvoke` 교체는 동일 |
| **W6** interrupt·계약 | **큼** | 확인 게이트가 middleware로 대체 |
| **W7** 레거시 삭제 | 작음 | 삭제 목록에 `_chat_completion` 등 추가 |
| **W8** 재시도·관측 | **필요** | 노드 `RetryPolicy` vs middleware 경계 |
| **W9** 문서·증빙 | **필요** | "안 쓰는 것" 목록 전제가 깨짐 |
| **W10** ReAct | **큼** | D7-2 재검토, 예산 4종이 middleware |

### 5.1 W2 — 의존성과 재시도 소유권

| 항목 | 현재 계획 | A안 |
| --- | --- | --- |
| 의존성 | `langgraph`·`langchain-openai`·checkpoint 2종 | **`langchain` 본체 추가** |
| `llm.py` | `build_chat_model()` + `RetryPolicy` 2종 | 모델은 그대로. 재시도 소유권 재검토 |

### 5.2 W6 — C2·C3를 자유롭게 설계할 수 없다

| 계약 항목 | 현재 계획 | A안 |
| --- | --- | --- |
| C2 interrupt payload 위치 | 우리가 설계 | **middleware가 정한 모양** |
| C3 resume 요청 형태 | 우리가 설계(권장 a안) | **`Command(resume={"decisions": [...]})`** |
| 확인 게이트 | `requires_confirmation?` 노드 직접 구현 | `HumanInTheLoopMiddleware` |
| 확인 대상 4종 | `_requires_confirmation()` | `InterruptOnConfig(when=lambda ...)` |
| 거부 시 | Task 종료 | **루프 계속, 모델이 대안 제시** |

middleware의 interrupt payload 실제 구조(실행 확인).

```json
{"action_requests": [{"name": "delete_task", "args": {"task_id": "t-2"},
                      "description": "Tool execution requires approval\n..."}],
 "review_configs": [{"action_name": "delete_task",
                     "allowed_decisions": ["approve", "edit", "reject", "respond"]}]}
```

재개는 **`decisions` 키로 감싸야 한다** — 리스트를 바로 넘기면 `TypeError`가 난다.

### 5.3 W8 — 두 체계가 공존한다

**계획의 재시도 2종은 LLM 호출 재시도인데, `ToolRetryMiddleware`는 도구 재시도다.** 다른 것이다.

| 대상 | 현재 코드 | A안 |
| --- | --- | --- |
| 에이전트의 LLM 호출 | `_chat_completion` 3회, 네트워크만 | `ModelRetryMiddleware(max_retries=3, retry_on=...)` |
| 에이전트의 도구 실패 | 없음 | `ToolRetryMiddleware(tools=[...])` |
| **나머지 10개 Skill** | `_call_llm_with_retry` 2회 등 | **노드 `RetryPolicy` 유지** — 에이전트가 아니다 |

`ModelRetryMiddleware`에는 `tools=` 파라미터가 없다. 에이전트의 모델 호출 전체에 적용되므로,
정책이 Skill별로 다른 workmate에서는 **`assistant_ask`의 정책만** 담을 수 있다. 나머지는 노드
`RetryPolicy`가 소유한다.

### 5.4 W10 — 범위가 줄지만 핵심은 남는다

| 계획 항목 | A안 |
| --- | --- |
| D7-2=B 커스텀 `StateGraph` | **재검토** — `create_agent`로 가능 |
| W10-D5 루프 예산 4종 | `ModelCallLimit` + `ToolCallLimit` |
| W10-D2 확인 게이트를 Graph 분기로 | middleware가 담당 |
| **W10-T2 카탈로그 137줄 이전** | **그대로 필요. 최대 위험 유지** |
| **W10-V5 결정적 규칙 보존** | **그대로 필요** |
| W10-V9 선택 안정성 | 그대로 필요 |

**middleware가 해 주는 것은 실행 제어이고, 규칙 보존과 결정성은 여전히 우리 몫이다.**

### 5.5 W1 — 케이스 2건 추가 권장

현재 `assistant_ask` 스냅샷 4건([30-1-5](30-1-5-design.md) §37-40)에는 A안에서 사라지는 두 동작의
"변경 전" 기록이 없다.

| 추가 권장 | 왜 |
| --- | --- |
| `assistant_ask.history_context.json` | `history` 전달이 없어지는 것의 전후 대조 |
| `assistant_ask.context_reference.json` | `_resolve_context_reference` 삭제의 전후 대조 |

## 6. 검증 결과

### 6.1 의존성 충돌 — 없음

**가장 큰 미확인 위험이었고, 해소됐다.** workmate의 고정 버전 11개를 그대로 둔 임시 프로젝트에
LangChain 스택 5개를 더해 `uv lock`으로 해석했다. 대조군(LangChain 없이 재해석)과 비교했다.

| 비교 | 결과 |
| --- | --- |
| 해석 성공 | 91개 패키지, exit 0 |
| **LangChain 추가가 밀리게 하는 기존 패키지** | **0개** |
| 재해석만으로 밀리는 것(LangChain 무관) | 17개 |
| 고정(`==`) 버전 9개 | **전부 유지** |
| `a2a-sdk` + `fastapi` + `langchain` 동시 import | **성공** |

고정 버전 확인: `a2a-sdk 1.1.2` · `fastapi 0.116.1` · `jsonschema 4.26.0` · `psycopg 3.2.10` ·
`uvicorn 0.35.0` · `PyJWT 2.10.1` · `google-auth 2.56.3` · `boto3 1.40.35` · `python-multipart 0.0.20`.
`httpx 0.28.1` · `starlette 0.47.3`도 동일.

**새로 추가되는 패키지 34개.** 주요: `langchain`·`langchain-core`·`langgraph`·`langgraph-checkpoint`(+sqlite/postgres)·`langgraph-prebuilt`·`openai`·`tiktoken`·`langsmith`·`orjson`·`tenacity`·`aiosqlite`·`psycopg-pool`·`sqlite-vec`.

### 6.2 별건으로 발견 — 현재 lockfile이 낡았다

위 17개는 **LangChain과 무관하게** 누구든 `uv lock`을 다시 돌리면 밀린다. 그중 하나가 메이저 업이다.

| 패키지 | 현재 | 재해석 시 |
| --- | --- | --- |
| **`oauthlib`** | 3.3.1 | **4.0.0** (메이저) |
| `google-api-core` | 2.34.0 | 2.40.0 |
| `google-auth-oauthlib` | 1.4.0 | 1.5.0 |
| `pydantic` | 2.13.4 | 2.13.5 |
| `anyio` | 4.14.2 | 4.15.1 |
| (그 외 12개) | | 패치·마이너 |

`oauthlib` 3→4는 Google OAuth 경로에 영향 가능성이 있다. **LangChain 도입과 별개로 확인이 필요한
항목이며, W2-T1에서 lock이 갱신될 때 함께 드러난다.**

### 6.3 버전 상한 — langchain 1.3.2

workmate의 `requires-python = ">=3.12,<3.13"` 제약에서 `langchain`이 **1.3.2**, `langgraph`가
**1.2.2**로 해석된다(상한 없이 해석하면 1.4.3 / 1.2.12). middleware는 14개로, **필요한 넷은 전부
포함**된다.

### 6.4 실행으로 확인한 것

| 항목 | 결과 |
| --- | --- |
| `create_agent` 시그니처·동작 | `model, tools, prompt/system_prompt, middleware, response_format, state_schema, checkpointer, store, interrupt_before/after` |
| `HumanInTheLoopMiddleware` | 승인·거부·**조건부 `when`** 3종 동작 |
| interrupt payload 구조 / `resume={"decisions":[...]}` | 확인 |
| `ModelCallLimitMiddleware` | `run_limit` 초과 시 종료. 사유가 AIMessage로 남음 |
| `ToolCallLimitMiddleware` | **병렬 호출을 합산.** 초과 시 둘 다 차단하고 사유를 ToolMessage로 전달 |
| `ToolRetryMiddleware` | `tools=[...]`로 도구별 정책. 3회째 성공 확인 |
| `ModelRetryMiddleware` | 시그니처 확인. `tools=` 없음 |
| `response_format` | **에이전트당 1개**(단일 타입) |
| **Subgraph 합성** | **두 방식 모두 가능** — §6.5 |
| `astream` 3모드 / `StateGraph`+`ToolNode`+`tools_condition` | 동작 |
| `draw_ascii()` · `draw_mermaid()` · `get_state_history()` | 동작 |

### 6.5 Subgraph 합성 — 두 방식

A안의 성립 여부가 걸린 항목이었고, **둘 다 된다.**

| 방식 | 조건 | 결과 |
| --- | --- | --- |
| **wrapper 노드** | 부모 State가 `messages`를 안 써도 된다 | Root Graph compile·invoke 성공 |
| **`add_node("agent", inner)` 직접** | `messages` 채널이 겹칠 때 | 변환 없이 붙는다 |

`create_agent`의 반환 타입은 `CompiledStateGraph`이므로 일반 Subgraph와 같이 다룰 수 있다.
**`WorkmateState`가 `messages`를 갖지 않아도 wrapper 노드로 `assistant_ask` 분기에 끼울 수 있다.**

### 6.6 아직 확인하지 않은 것

| 항목 | 왜 필요 |
| --- | --- |
| **440개 테스트 통과 여부** | 해석 성공 ≠ 런타임 호환. `oauthlib` 4.0 포함 |
| `AsyncPostgresSaver`와 `psycopg[binary]==3.2.10` 실동작 | 해석은 통과, 연결 미확인 |
| `with_structured_output(method=)` 동등성 | W2-V6의 대상 |
| middleware와 A2A `TaskUpdater` 이벤트 순서 상호작용 | W5·W6의 대상 |

## 7. 이 문서로 결정하지 않은 것

- **선택지 A/B/C 중 무엇을 택할지.** 조사만 했다.
- 계획서 W2·W6·W8·W9·W10 개정 여부와 범위.
- [05번 §1](05-ai-security-operations.md) 개정 시점 — [30-10-10 §1.1](30-10-10-approval.md)의 판단
  (착수 시점에 받는다)이 유지되는지.
- `langchain` 본체를 [W9-R11](30-9-4-requirements.md) "안 쓰는 것" 목록에서 어떻게 정리할지.
- 오케스트레이터 어댑터의 `INPUT_REQUIRED` 처리(§4.4).
- `oauthlib` 3→4 대응(§6.2) — LangChain과 무관한 별건.

## 8. 참조

| 자료 | 내용 |
| --- | --- |
| [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) | 전환 계획 §4 확정 결정 D1~D6 |
| [30-10-10](30-10-10-approval.md) | D7-1~D7-7, 05번 개정안, 승인 경계 |
| [30-6-5](30-6-5-design.md) | W6 계약안 C1~C5 — §5.2의 영향 대상 |
| [30-8-5](30-8-5-design.md) | W8 재시도 설계 — §5.3의 영향 대상 |
| [30-9-4](30-9-4-requirements.md) | W9-R11 "안 쓰는 것" — §1.1의 영향 대상 |
| [assistant_router.py](../workmate-agent/app/workflows/assistant_router.py) | §4 영향도의 대상 |
| [workmate-format.ts](../workmate-ui/lib/workmate-format.ts) | §4.2 UI 계약 경계 |
| [m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py) | §4.4 오케스트레이터 경로 |
