# 오케스트레이터 AI Chat → Workmate Skill 라우팅 구현 계획

작성일: 2026-08-17
상태: 구현 완료(1~5·7단계) — 6단계(실 Docker Compose E2E)·8단계(HANDOFF 공식 증빙)는 범위 밖(아래
"구현 완료 보고" 참고)
경로 참고: 이 문서의 `AI-agent_game_platform/backend/...` 표기는 모노레포 재구성(2026-08-18,
`8e3400e`) 이전 기준이다. 지금 실제 위치는 `AI-agent_game_platform/main_agent/backend/...` —
[25번 문서](25-orchestrator-pull-conflicts.md)의 경로 대조표 참고.

## 배경

사용자가 오케스트레이터(`AI-agent_game_platform`)의 **AI Chat**(`App.tsx` 채팅 패널, Agent Card 표시
이름 "Workmate AI"/"Cat AI Chat")에서 Workmate 에이전트로 라우팅해 Skill들을 실제로 써보려 한다. 이
문서는 그 경로가 어떤 상태였는지 코드로 직접 확인한 결과, 실제로 쓸 수 있게 만드는 구현 계획, 그리고
그 계획을 실제로 구현한 결과(아래 "구현 완료 보고")를 함께 담는다 — 계획 단계에서는 "계획만 작성하고
구현은 하지 않는다"는 제약이 있었지만, 이후 사용자가 구현을 명시적으로 요청해 진행했다.

[19-workmate-ui-orchestrator-port-plan.md](19-workmate-ui-orchestrator-port-plan.md)는 오케스트레이터
프론트 안에 **7개 구조화 화면**(브리핑·주간보고·할 일 관리·회의 녹음·회의 관리·회의록 검색·제안함)을
이식하는 계획이고, 이 문서는 그와 별개로 **오케스트레이터가 이미 갖고 있는 채팅 UI 하나**를 통해
자연어로 Skill을 쓰는 경로만 다룬다 — 범위가 겹치지 않는다.

**범위**: 챗봇(AI Chat) 경로만. 7개 구조화 화면 이식(19번 문서), Workmate 저장소 안의 Drawer 자체
변경(18번 문서)은 이 문서의 범위가 아니다.

**전제**: [15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md)의 "Skill별 기능
설명"은 `daily_briefing`·`weekly_report`·`analyze_meeting`·`search_meetings`·`rank_priorities`뿐
아니라 `get_meeting_analysis`·`review_action_items`·`review_proposal`·`manage_tasks`·`read_email`·
`assistant_ask`까지 **11개 Skill 전부를 Agent Card에 공개**하는 것으로 정의한다. 이 계획은 그
정의가 실제 코드(`app/a2a/runtime.py`의 `_SKILLS`)에 반영된 뒤를 전제로 한다 — 지금 코드는 아직
5개만 공개하므로, 아래 "단계 구분" 1단계가 이 계획의 실제 출발점이다.

## 목표

오케스트레이터 AI Chat에 자연어로 입력했을 때, 사용자가 실제로 요청한 내용에 맞는 Workmate Skill이
실행되고 그 결과가 채팅 답변으로 돌아오게 만든다. 11개 Skill이 전부 공개되므로, 18번 문서가 구현한
자연어 라우팅(`assistant_ask`가 나머지 10개 Skill을 대신 호출)을 어댑터가 그대로 재사용하는 경로
하나로 목표를 달성한다.

## 원칙 — 기존 Workmate 기능 비영향

오케스트레이터와 합치는 과정에서 나오는 모든 `workmate-agent` 쪽 수정은 **기존 Workmate 기능(Drawer
프론트, 내부 skill-chat REST(`internal_chat.py`), 독립 A2A 계약, 기존 테스트가 이미 고정해 둔
필드·동작)에 영향을 주지 않아야 한다.** 오케스트레이터 통합은 부가 기능이지, 기존 기능을 대체하는
게 아니다. 실무 기준:

- 기존 소비처가 이미 읽고 있는 필드(예: `WorkflowResult.text` — `internal_chat.py`와
  `test_daily_briefing.py` 등 여러 테스트가 `json.loads(result.text)`로 파싱함)는 값을 바꾸지 않고,
  새 필드를 **추가**하는 방향으로만 확장한다.
- 수정 전 반드시 그 필드·함수를 실제로 소비하는 코드를 전부 찾아(Drawer 프론트, `internal_chat.py`,
  `assistant_ask`/`phrase_answer()`, 레거시 어댑터, 관련 테스트) 각각 영향이 없는지 확인한 뒤
  진행한다.
- 수정 후 `workmate-agent`의 전체 테스트 스위트를 실행해 회귀가 없는지 확인한다.
- 오케스트레이터(`AI-agent_game_platform`) 저장소 자체는 이 프로젝트가 직접 고칠 수 없으므로(G6),
  거기서 필요한 수정은 "오케스트레이터 담당자에게 전달할 요청 목록"에 모아 별도로 요청한다 — 이
  원칙은 우리가 통제 가능한 `workmate-agent` 쪽 수정에 적용된다.

## 현재 상태 (코드로 직접 확인)

### 1. 오케스트레이터 AI Chat 자체엔 Skill 판별이 없다

호출 흐름: `App.tsx` 채팅 패널 → `POST /api/chats/{agent_name}/reply`(또는 `/api/route`) →
`resolve_chat_agent()` → `RouterLLM.select()` → `build_agent_request()` → `A2AClient.send_message()`
(`AI-agent_game_platform/backend/app/main.py`, `router.py`, `a2a_client.py`).

- `RouterLLM`(`router.py`)이 LLM으로 판별하는 건 **어느 Agent로 보낼지**(`workmate-agent` /
  `video-agent` / `dev-agent` / `game-qna-agent` 중 하나)뿐이다. Workmate 안의 **Skill 단위 판별은
  전혀 없다**.
- `build_agent_request()`(`main.py:197-207`)는 `agent_name == "workmate-agent"`일 때 무조건
  `request["skill_id"] = "daily_briefing"`을 고정한다. 사용자가 "주간보고 작성해줘"라고 치든
  "회의 검색해줘"라고 치든 Workmate에는 항상 `daily_briefing`이 가고, `DailyBriefingInput`(02번
  문서)엔 자유 텍스트를 받는 필드 자체가 없어 사용자가 실제로 뭘 물었는지는 그냥 버려진다.
- 이 문제는 Agent Card에 Skill이 몇 개 있든 그대로 남는다 — `build_agent_request()`가 `skill_id`를
  고정해 보내는 이상, 오케스트레이터 저장소를 고치지 않는 한 별도 어댑터가 계속 필요하다.

### 2. 실제로 A2A 계약대로 동작하는 경로는 legacy adapter뿐이고, 이것도 LLM이 아니라 키워드 규칙이다

`workmate-agent/tools/m51_legacy_adapter.py`(`docker-compose.workmate-local.yml`의
`workmate-adapter` 서비스)가 실제로 Skill을 다시 판별해 공개 A2A 계약에 맞게 채워 넣는 유일한
코드다. 어댑터 자체 docstring이 이유를 명시한다:

> 담당 Orchestrator의 채팅 경로는 Skill을 고르지 못하고 항상 `daily_briefing`을 보낸다. 해당
> 저장소를 수정할 수 없으므로 이 어댑터가 사용자 문장에서 Skill을 다시 판정하고 Workflow 필수
> 입력을 채운다.

**오케스트레이터 저장소(`AI-agent_game_platform`)는 이 프로젝트가 직접 고칠 수 없다**는 전제가 이미
이 프로젝트 안에 있다(M5.1 이력, `HANDOFF.md` 참고). 이 문서는 그 전제를 그대로 유지하고, 우리가
통제 가능한 `workmate-agent` 쪽(공개 Skill 목록·어댑터)만으로 계획을 세운다(사용자 확인 완료 —
지금도 이 저장소를 직접 고칠 수 있는 상황이 아니다).

어댑터의 한계:

- `_infer_skill()`은 LLM이 아니라 **정규식/토큰 키워드 매칭**이다(회의+검색어, 회의+분석어, 주간
  키워드, 우선순위 키워드, 나머지는 `daily_briefing`). 18번 문서가 문자열 유사도 접근을 시도했다가
  한계에 부딪혀 전용 LLM 매칭 호출(`_resolve_context_reference`)로 교체한 것과 같은 동의어·표현
  차이 문제(예: "신입사원 환영회"↔"신규 입사자 환영회")를 그대로 재현할 소지가 크다.
- 지금은 공개 5개 Skill만 다룬다 — 나머지 6개(`get_meeting_analysis`·`review_action_items`·
  `review_proposal`·`manage_tasks`·`read_email`·`assistant_ask`)는 아직 공개 Agent Card에 없어
  어댑터도 알지 못한다.
- `user_id`는 실사용자 인증이 아니라 `M51_ADAPTER_DEFAULT_USER_ID`라는 고정 데모 UUID다 —
  오케스트레이터가 실사용자를 구분해 전달하지 않기 때문이다(19번 문서 "결정 1"이 REST/OIDC
  경로에서 지적한 것과 같은 근본 문제).
- 인증은 자체 발급하지 않는다 — 오케스트레이터가 보낸 `Authorization` 헤더(Service Bearer Token)를
  그대로 Workmate 공개 A2A로 전달한다(`_workmate_request()`, `m51_legacy_adapter.py:274`). 아래
  "설계"가 새 인증 장치 없이 그대로 확장 가능한 이유다.

### 3. `assistant_ask`를 이 경로에 태우려면 걸리는 것

- `_ASYNC_SKILLS`(`analyze_meeting`·`assistant_ask`를 백그라운드로 돌리고 Task Polling을 열어주는
  분기)는 **`app/internal_chat.py`(내부 skill-chat REST)에만 있다.** `app/a2a/runtime.py`의 공개
  A2A 실행기(`RuntimeBootstrapExecutor.execute()`)는 Skill 종류를 가리지 않고 `registry.execute()`를
  그 코루틴 안에서 끝까지 기다린 뒤에야 완료 이벤트를 만든다 — 공개 A2A 경로엔 이런 백그라운드/
  Polling 분기가 없다.
  > **해결(2026-08-17, 구현 완료)**: a2a-sdk의 `DefaultRequestHandler.on_message_send()`는 기본이
  > Blocking이라 정말 Task가 끝날 때까지 응답을 들고 있는다 — 코드(`on_message_send` Docstring:
  > "waits for the final result")와 실측(느린 Fake Workflow로 직접 호출) 둘 다로 확인했다. 다만
  > SDK가 `SendMessageRequest.configuration.return_immediately`(REST에서는
  > `configuration.returnImmediately`)라는 표준 옵션을 이미 제공한다 — 이 값을 `true`로 보내면
  > `TASK_STATE_SUBMITTED` 상태로 즉시 응답하고, 이미 존재하는 `GET /a2a/v1/tasks/{id}` 프록시로
  > 완료를 Polling할 수 있다(오케스트레이터의 `A2AClient.send_message()`가 Task 응답을 받으면
  > 자동으로 `poll_task()`로 넘어가므로 어댑터 쪽에 새 Route가 필요 없다). 어댑터의 모든
  > `message:send` 요청에 이 옵션을 실어 보내도록 구현했다 — `RuntimeBootstrapExecutor`를 고치는
  > "백그라운드 분기 추가"(범위 확장)는 필요 없었다.
- `assistant_ask`의 출력(`{"type": "assistant_reply", "data": {"reply", "executed_skill_id",
  "pending_action"}}`)은 공개 `WorkmateResultEnvelope`/`TypedResult`
  (`docs/schemas/workmate-skill-schemas.schema.json`)에 정의된 5개 `result.type` 중 어디에도 속하지
  않는다 — Drawer 프론트(`parseAssistantReply`)만 이해하는 비공식 포맷이다. 다만
  `_artifact_parts()`(`app/a2a/runtime.py:257-278`)는 `result.markdown`이 있으면 별도
  `text/markdown` Part도 함께 만들고, 오케스트레이터의 `_extract_answer()`(`a2a_client.py:44-57`)는
  Data Part의 `data`가 아니라 아무 Part의 `.text`든 이어붙이는 방식이라 — 단순 텍스트 답변만
  받는 경우엔 별도 출력 Schema 확장 없이도 동작할 가능성이 높다. `pending_action`(확인 배너) 자체를
  구조적으로 인식하려면 오케스트레이터 프론트에 새 UI(확인/취소 버튼)가 필요한데, 이건 우리가 직접
  만들 수 없는 저장소다.
- `assistant_ask`는 `payload.context`(최근 회의·대기 제안 목록)와 `payload.history`(대화 이력)로
  "그 회의"·"그 메일" 같은 지칭 질문을 이름으로 매칭한다(`app/workflows/assistant_router.py::
  _format_context`, `_resolve_context_reference`). 이 Context는 Drawer 프론트가 화면 상태에서 만들어
  매 요청에 실어 보내는데, 오케스트레이터/어댑터는 그런 화면 상태 자체가 없다 — Context 없이
  호출하면 `_format_context(None)` → `"(회의·제안 Context 없음)"`으로 채워져, 이름으로 지칭하는
  질문엔 "정보가 없습니다"로만 답할 가능성이 높다.

## 문제 정의 (Gap 요약)

| # | Gap | 근거 |
| --- | --- | --- |
| G1 | Skill 판별이 오케스트레이터엔 없고, 어댑터엔 있지만 LLM이 아니라 키워드 규칙이다 — Agent Card 공개 범위와 무관하게 남는 문제다 | `router.py`(에이전트 판별만), `m51_legacy_adapter.py::_infer_skill()`, `main.py::build_agent_request()` |
| G2 | 어댑터가 공개 5개 Skill만 알고 6개 신규 Skill을 모른다 | `m51_legacy_adapter.py`, `app/a2a/runtime.py::_SKILLS` |
| G3 | 실사용자 식별이 없다 — 어댑터는 고정 데모 `user_id` 하나만 쓴다 | `M51_ADAPTER_DEFAULT_USER_ID` |
| G4 | 오케스트레이터의 Task Polling이 `INPUT_REQUIRED`/`AUTH_REQUIRED`를 처리하지 못해 확인이 필요한 응답은 타임아웃으로 보인다 — **다만 실제로는 발생하지 않는다**(구현 중 확인): `RuntimeBootstrapExecutor`는 `assistant_ask`의 `pending_action` 유무와 무관하게 항상 `TASK_STATE_COMPLETED`로 끝낸다. `pending_action`은 A2A Task 상태가 아니라 JSON 응답 안 값이라 G5(안내 문구)만으로 충분하다 | `a2a_client.py::poll_task()`, `app/a2a/runtime.py::RuntimeBootstrapExecutor.execute()` |
| G5 | `assistant_ask`의 확인(`pending_action`) UX를 오케스트레이터 채팅 UI가 표시·재전송할 방법이 없다(버튼 없음) | `App.tsx` 채팅 패널, 18번 문서 |
| G6 | 오케스트레이터 저장소(`AI-agent_game_platform`)를 이 프로젝트가 직접 수정할 수 없다 | `m51_legacy_adapter.py` docstring, M5.1 이력 |
| G7 | ✅ 해결(2026-08-17) — 공개 A2A `message:send`는 기본이 Blocking이지만, 어댑터가 `configuration.returnImmediately=true`를 실어 보내 `TASK_STATE_SUBMITTED`로 즉시 받고 기존 `GET /a2a/v1/tasks/{id}` 프록시로 Polling한다 | `m51_legacy_adapter.py::_workmate_request()`, `.venv/.../default_request_handler.py::on_message_send` |
| G8 | `assistant_ask`는 회의·제안 Context에 의존한다 — Workmate가 사용자의 최근 회의·제안을 각각 최근 10건까지 서버에서 직접 채우도록 결정했고(어댑터 변경 불필요), 그 10건 밖은 여전히 못 찾는다 | `app/workflows/assistant_router.py` |

## 설계

**어댑터가 `skill_id`를 `assistant_ask`로 고정해, 지금과 같은 인증으로 공개 A2A에 프록시한다.**

- `_infer_skill()`(정규식 키워드 매칭)과 `_fill_skill_payload()`(Skill별 payload 채우기)를 제거한다.
- 오케스트레이터에서 들어오는 모든 채팅 요청을 `skill_id="assistant_ask"`,
  `payload={"text": 사용자 문장, "user_id": DEFAULT_USER_ID}`로 고정해 그대로 공개
  `/a2a/message:send`에 보낸다 — Skill 판별(`route()`)과 나머지 10개 Skill 호출은 `assistant_ask`
  내부에서 전부 처리된다(18번 문서 그대로 재사용).
- 인증·Task 상태 조회 경로는 기존 공개 A2A 그대로 재사용한다 — 어댑터가 이미 오케스트레이터의
  `Authorization` 헤더를 그대로 전달하고 있으므로 새 인증 장치가 필요 없다.
- **회의·제안 Context(G8)는 어댑터가 아니라 Workmate 쪽에서 채운다.** `assistant_ask`가 호출자
  (Drawer든 이 어댑터든)가 보내는 `context`에만 기대지 않고, 사용자의 최근 회의·제안을 각각 최근
  10건까지 서버가 직접 조회해 채운다 — 대화 이력을 최근 10턴까지만 기억하는 것과 같은 기준
  (`_MAX_HISTORY_TURNS`)이다. 회의 10건은 기존 `MeetingRepository`를 최근순으로 조회하면 되고
  (`GET /api/v1/meetings`가 이미 같은 저장소를 쓴다), 제안 10건은 지금 서버에 전혀 남지 않으므로
  (발행 즉시 SSE로만 흘러감) 최근 10건을 기억할 방법을 새로 만들어야 한다 — 세부 구현은 아래
  "단계 구분" 4단계에서 다룬다. 이 방식이면 **어댑터는 Context를 위해 아무것도 새로 보낼 필요가
  없다** — REST 추가 호출도, 그를 위한 OIDC 인증도 필요 없어진다.
- G7(공개 A2A가 Skill 완료까지 응답을 막는지)은 실측으로 확인·해결했다 — `configuration.returnImmediately=true`로 우회한다(위 "현재 상태 3" 해결 박스).

키워드 규칙만 6개 신규 Skill까지 확장하는 대안은 추천하지 않는다 — 18번 문서가 문자열 유사도
접근에서 겪은 것과 같은 한계(표현이 살짝 다른 질문을 놓침)가 반복될 개연성이 높고, `assistant_ask`가
이미 LLM 기반으로 이 문제를 풀어 뒀다.

## 상세 설계(안)

| 구성 요소 | 지금 | 적용 후 |
| --- | --- | --- |
| `POST /a2a/v1/message:send` | `_infer_skill()` 키워드 매칭(공개 5개만 인식) → 공개 `/a2a/message:send` 프록시 | 항상 `skill_id=assistant_ask` → 같은 공개 `/a2a/message:send` 프록시(11개 전체를 대신 호출 가능) |
| `GET /a2a/v1/tasks/{id}` | 공개 `/a2a/tasks/{id}` 프록시 | 코드 변경 없음 — 다만 `returnImmediately` 도입 후 실제 완료된 답은 대부분 이 경로로 온다(레거시 변환도 이 경로에 적용하도록 확장, G7) |
| 인증 | 오케스트레이터가 보낸 `Authorization` 헤더(Service Bearer Token)를 그대로 전달 | 변경 없음 |
| `user_id` | 요청 payload의 고정 문자열(`M51_ADAPTER_DEFAULT_USER_ID`) | 변경 없음 |
| Skill 판별 | 어댑터의 정규식 키워드(공개 5개만 대상) | `assistant_ask` 내부 LLM Router(`route()`) — 11개 전체 대상 |
| 신규 6개 Skill 접근성 | 불가(공개 계약 밖) | 가능 — Agent Card 공개 후 `assistant_ask`가 대신 호출 |
| 확인이 필요한 응답(`pending_action`) | 개념 자체 없음 | 자동 실행하지 않고 안내 문구만 덧붙여 반환 — 오케스트레이터 프론트에 확인 버튼을 추가할 수 없어(G6) 이 범위로 확정 |
| 회의·제안 Context | 없음(공개 5개는 Context를 안 씀) | Workmate(`assistant_ask` 내부)가 사용자의 최근 회의·제안을 각각 최근 10건까지 서버에서 직접 채운다(G8) — 어댑터 변경 불필요 |
| Task 완료 대기 방식 | 공개 A2A `TaskState` 그대로, 기본 Blocking | `message:send`에 `configuration.returnImmediately=true`를 실어 SUBMITTED로 즉시 받고 `GET /tasks/{id}`로 Polling(G7 해결) |

## 단계 구분 (계획 — 각 단계 실제 착수는 후속)

| 단계 | 범위 | 결과 |
| --- | --- | --- |
| 1단계 | 15번 문서 정의를 코드에 반영 — 6개 Skill을 `app/a2a/runtime.py`의 `_SKILLS`로 옮기고 Agent Card에 노출 | ✅ 완료 — `_INTERNAL_ONLY_SKILLS`를 없애고 `_SKILLS` 11개로 합침. `approved_skill_definitions()`도 `_SKILLS`만 반환하도록 단순화(내부 전용 목록 구조 자체가 사라져 "정리는 범위 아님"이라던 우려가 해소됨) |
| 2단계 | 공개 A2A 실행기가 Skill 완료까지 `message:send` 응답을 막는지 확인(G7) | ✅ 완료 — 실측으로 Blocking 확인, `configuration.returnImmediately`로 해결(위 "현재 상태 3") |
| 3단계 | `m51_legacy_adapter.py`의 `_infer_skill()`/`_fill_skill_payload()` 제거, `assistant_ask` 고정 호출로 교체 | ✅ 완료 — 어댑터 전체를 다시 씀(`ASSISTANT_ASK_SKILL_ID` 고정, 빈 문장만 사전 검증) |
| 4단계 | `assistant_ask`가 회의·제안 Context를 최근 10건까지 서버에서 직접 채우도록 구현(G8) | ✅ 완료 — 회의는 `app.meeting_api.list_meetings` 재사용, 제안은 `proposal_hub`(SSE 발행 전 검토 대기 상태를 이미 메모리에 들고 있던 것)에 `recent()` 메서드 추가 |
| 5단계 | `pending_action` 응답에 안내 문구를 덧붙이는 처리 구현 | ✅ 완료 — `_legacy_response()`가 JSON Data Part에서 `pending_action`을 읽어 안내를 덧붙임 |
| 6단계 | `docker-compose.workmate-local.yml` 프로필로 End-to-End 확인 — 11개 Skill 전체가 채팅으로 정확히 실행되는지 | ⬜ 범위 밖 — 실제 오케스트레이터 저장소·실 Provider(OpenAI 등)가 함께 떠 있는 환경이 필요해 이번 구현 세션에서는 안 함(아래 "구현 완료 보고") |
| 7단계 | 기존 `test_m51_legacy_adapter.py` 갱신 + 신규 계약 테스트 | ✅ 완료 — 8→9개 테스트로 재작성(키워드 매핑 테스트 제거, 고정 라우팅·레거시 응답 변환·`returnImmediately` 대응 검증 추가), `test_assistant_router.py`에 Context 기본값 테스트 6개 추가, `test_runtime_boot.py`·`test_internal_chat.py`·`test_contract.py` 갱신 |
| 8단계 | `HANDOFF.md`/`M5.1` 증빙 갱신 | ⬜ 범위 밖 — 이 작업은 M5.1 같은 마일스톤 번호가 없는 부속 계획이라 `docs/evidence/` 공식 승인 절차 대상이 아니다(아래 "구현 완료 보고") |

## 검증 계획

- 단위: 어댑터의 `assistant_ask` 고정 요청 조립, Task 상태 변환 각각의 성공·실패 경로. — ✅
  `test_m51_legacy_adapter.py` 9개.
- 계약: 기존 5개 Skill로 들어오던 요청이 여전히 응답을 받는지 회귀 확인 — 프로토콜 경계(A2A
  message:send/tasks)는 유지해야 한다. — ✅ `test_contract.py`(11개 Skill이 모두 Agent Card에
  나열되는지는 `test_runtime_boot.py::test_agent_card_is_public_and_declares_http_json_streaming`).
- G7 확인: ✅ 완료 — 느린 Fake Workflow로 직접 측정, `returnImmediately` 없이는 1.28초(Workflow의
  `sleep(1.2)`만큼) Blocking, 있으면 0.03초로 즉시 `SUBMITTED` 반환을 확인했다. 실제
  `analyze_meeting`(STT+LLM, 수십 초~분 단위)으로 측정하진 않았지만, SDK 동작 자체가 확인된 이상
  Skill 소요 시간과 무관하게 성립한다.
- G8 확인: ✅ 단위 수준(`_default_meetings_context`/`_default_proposals_context`/`_with_default_context`
  6개 테스트)으로 채우는 로직 자체는 검증했다. "그 회의 분석해줘" 같은 실제 자연어 질문이 서버가
  채운 Context만으로 맞게 매칭되는지는 실 LLM 호출이 필요해 6단계(End-to-End)로 남긴다.
- End-to-End: ⬜ 범위 밖 — `docker-compose.workmate-local.yml`로 오케스트레이터 → 어댑터 →
  Workmate 공개 A2A 왕복을 실제 Provider로 확인하는 것은 실제 오케스트레이터 저장소가 함께 떠 있는
  환경이 필요해 이번 세션에서 하지 않았다(아래 "구현 완료 보고").
- 확인 필요 응답(`pending_action`)이 안내 문구와 함께 안전하게 돌아오는지: ✅
  `test_legacy_response_appends_a_confirmation_notice_when_pending_action_is_present`.

## 미결정 사항

(2026-08-17) 계획 단계에서 유일하게 남아 있던 Q2(G7 — 공개 A2A의 완료 대기 방식)는 구현 중
`configuration.returnImmediately`로 해결했다(위 "현재 상태 3"). 더 이상 남은 미결정 사항이 없다.

## 리스크

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 단일 데모 계정이 모든 오케스트레이터 사용자를 대표 | 실사용자별 데이터 분리 불가 | MVP 범위에서는 허용, 멀티 유저 필요해지면 재설계(19번 문서와 동일 판단) |
| `pending_action` 안내만으로는 실제 확인 UX가 없어 사용성이 떨어짐 | 파괴적 동작을 채팅으로는 끝까지 못 함 | 오케스트레이터 프론트에 확인 버튼을 추가할 수 없어(G6) 감수한다 — 파괴적 동작의 실제 확인은 Workmate 화면(Drawer 등)에서 진행하도록 안내 문구로 유도 |
| G8 — 서버가 기억하는 최근 10건 밖의 회의·제안은 지칭하지 못함 | 오래된 회의·이미 지나간 제안을 "그때 그거"처럼 지칭하면 여전히 못 찾을 수 있음 | 10건은 Drawer의 대화 이력 캡(`_MAX_HISTORY_TURNS`)과 같은 기준으로 맞춘 값 — 부족하면 개수만 조정 |
| G7 해결의 잔여 위험 — `returnImmediately`는 최초 연결이 안 막히게만 할 뿐, 오케스트레이터 자체 `poll_task()`의 30초 Timeout은 그대로다 | `analyze_meeting`처럼 30초를 넘는 Skill이 선택되면 Workmate는 계속 처리 중이어도 오케스트레이터는 실패로 본다 | 이번 구현 범위 밖 — 6단계(실 E2E)에서 실측 필요, 넘으면 `poll_timeout` 조정이나 `assistant_ask` 프롬프트에서 이 경로일 때 오래 걸리는 Skill 선택 제한을 재검토 |
| 오케스트레이터가 그 사이 코드/포트/CORS를 바꿈 | 어댑터 URL·CORS 재조정 필요 | 19번 문서의 결정과 함께 반영 |

## 구현 완료 보고 (2026-08-17)

이 계획의 1~5·7단계를 실제로 구현했다. 6단계(실 Docker Compose E2E)와 8단계(HANDOFF 공식 증빙)는
아래 이유로 이번 세션에서 하지 않았다.

### 바뀐 파일

- `workmate-agent/app/a2a/runtime.py` — `_INTERNAL_ONLY_SKILLS`를 없애고 6개 Skill을 `_SKILLS`로
  합쳐 11개 전부 Agent Card에 노출(1단계). `approved_skill_definitions()`는 이제 `_SKILLS`만
  반환한다.
- `workmate-agent/app/internal_chat.py` — Docstring의 "승인 Skill 5개"를 11개로 정정.
- `workmate-agent/app/workflows/assistant_router.py` — `_with_default_context()`·
  `_default_meetings_context()`·`_default_proposals_context()` 추가(4단계). 호출자가 `context`를
  안 보내면 서버가 최근 10건까지 직접 채운다.
- `workmate-agent/app/workflows/assistant_skills.py` — 모듈 Docstring을 "내부 전용" 전제에서
  "공개 Skill이기도 하다"로 정정.
- `workmate-agent/app/proposal_api.py` — `ProposalHub.recent()` 추가(4단계) — 이미 메모리에 있던
  검토 대기 제안 목록을 그대로 노출한다.
- `workmate-agent/tools/m51_legacy_adapter.py` — 전면 재작성(3·5단계): 키워드 매칭 전부 제거,
  `assistant_ask` 고정 호출, `configuration.returnImmediately`(G7), `pending_action` 안내 문구
  (G5), Task Polling 응답까지 포함한 레거시 변환.
- 테스트: `tests/test_m51_legacy_adapter.py`(전면 재작성, 9개), `tests/test_assistant_router.py`
  (+6개), `tests/test_runtime_boot.py`·`tests/test_internal_chat.py`·`tests/test_contract.py`
  (Skill 개수·목록 갱신).

### 계획에 없었던 발견 — G7을 실측으로 확인하고 SDK 표준 옵션으로 해결

계획 시점엔 "공개 A2A가 Skill 완료까지 응답을 막는지 SDK 내부 구현이라 확인 못 함"이라고 미결정으로
남겼었다. 구현 중 a2a-sdk 소스(`DefaultRequestHandler.on_message_send`)를 직접 읽고, 가짜 지연
Workflow로 실측까지 해서 확인했다 —

- `returnImmediately` 없이 보내면 1.5초짜리 Workflow가 그대로 1.28초를 응답에 물고 있다가
  `TASK_STATE_COMPLETED`로 끝난다(Blocking).
- 요청에 `configuration.returnImmediately: true`를 실으면 같은 Workflow가 0.03초 만에
  `TASK_STATE_SUBMITTED`만 돌려준다.

이건 `analyze_meeting`·`assistant_ask`만 특별 취급하는 `_ASYNC_SKILLS`(내부 skill-chat 전용) 같은
백그라운드 분기를 공개 실행기에 새로 만드는 대신, A2A 프로토콜이 이미 정의해 둔 표준 옵션 하나로
푼 것이다 — `RuntimeBootstrapExecutor`는 전혀 안 건드렸다. 어댑터의 `GET /a2a/v1/tasks/{id}` 프록시가
이미 있었으므로, 완료된 답은 이제 대부분 `message:send`가 아니라 이 Polling 경로로 온다 — 그래서
레거시 응답 변환(`_legacy_response`, `invoked_skill`·`pending_action` 안내 추가)도 `GetTask`가
돌려주는 (감싸지 않은) bare `Task` 모양까지 같이 처리하도록 넓혔다(안 그러면 실제 완료된 답에는
변환이 하나도 안 먹는 채로 남을 뻔했다).

부수적으로 G4("오케스트레이터가 `INPUT_REQUIRED`를 못 받는다")도 이 과정에서 다시 확인했다 —
`RuntimeBootstrapExecutor`는 애초에 `pending_action`이 있든 없든 항상 `TASK_STATE_COMPLETED`로
끝난다(`pending_action`은 A2A 프로토콜 상태가 아니라 JSON 응답 안의 값이다). 그래서 G4가 우려한
"INPUT_REQUIRED 처리 못 함" 상황 자체가 이 통합에서는 생기지 않는다 — G5(안내 문구)만으로 충분하다.

### 검증

- 단위/계약 테스트: `python -m unittest discover -s tests` — **404개 PASS, 12 SKIP, 0 FAIL**
  (전체 스위트, `.venv` 인터프리터 기준).
- 위 "검증 계획"에 표시한 항목 중 End-to-End(6단계)만 남기고 전부 자동/실측으로 확인했다.

### 6·8단계를 하지 않은 이유

- **6단계(실 Docker Compose E2E)**: `AI-agent_game_platform`(오케스트레이터) 저장소가 실제로
  기동돼 있고 실 Provider(OpenAI 등) 자격 증명이 갖춰진 통합 환경이 필요하다 — 이 구현 세션의
  범위(코드 변경·단위/계약 테스트)를 넘어선다. 사용자가 `docker-compose.workmate-local.yml`
  프로필로 직접 띄워 확인하는 것을 권장한다.
- **8단계(`HANDOFF.md`/`M5.1` 증빙 갱신)**: `HANDOFF.md`의 완료 항목 표는 `docs/06-delivery-plan.md`
  마일스톤(M0~M5) 번호에 매인 공식 승인 절차(`docs/evidence/Mx/My/runs/.../result.md`)를 전제로
  한다. 이 문서(20번)는 그 마일스톤 체계 밖의 부속 계획이라 억지로 끼워 넣지 않았다 — 필요하면
  별도로 M5.1 후속 항목을 정의해 그 절차를 따르는 게 맞다.

## 오케스트레이터 담당자에게 전달할 요청 목록 (2026-08-18)

이 문서 본문(1~8단계)과는 별개로, 2026-08-18에 오케스트레이터 AI Chat을 실제로 띄워 "Workmate AI"
탭·"Main Chatbot"(오늘 브리핑 화면 라우터 위젯)을 직접 써보며 발견한 문제들이다. 전부
`AI-agent_game_platform` 저장소(팀원 소유) 쪽 수정이 필요해 이 프로젝트가 직접 반영할 수 없다 —
낱개로 요청하지 않고 아래 표를 모아 담당자에게 한 번에 전달한다.

| # | 문제 | 위치 | 현재 상태 | 요청할 수정 |
| --- | --- | --- | --- | --- |
| R1 | 모든 A2A `message:send` 요청이 `messageId`를 고정 문자열 `"main-agent"`로 보냄 — workmate-agent의 멱등성 검사(`persistence.py::record_message`)가 같은 ID로 다른 payload가 오면 `ValueError`를 던지므로, 같은 채팅에서 두 번째 질문부터 항상 500/502로 실패했다 | `backend/app/a2a_client.py:81`(HTTP+JSON 경로) | ✅ 로컬 clone에 임시 적용·재현 검증 완료 — 재빌드한 `main-agent` 컨테이너로 연속으로 다른 질문 2개를 보내 둘 다 200과 실제 `daily_briefing` 응답을 확인했다(이전엔 두 번째부터 항상 실패). 커밋·푸시는 하지 않았다 — 정식 반영은 담당자 쪽에서 | `request.get("request_id", "main-agent")` → `request.get("request_id") or str(uuid.uuid4())`(+ `import uuid`). `video_agent_client.py::send_message()`가 이미 같은 패턴으로 구현·테스트(`test_send_message_uses_a_fresh_message_id_every_call`, `backend/tests/test_video_agent_client.py:42-58`)돼 있어 그대로 재사용하면 됨 |
| R2 | "Main Chatbot"(오늘 브리핑 화면의 라우터 위젯)이 백엔드로 요청을 보내면 `CHAT_AGENT_NAMES`에 `"Main Chatbot"` 키가 없어 `resolve_chat_agent_fallback()`이 그 이름을 그대로 돌려주고, `cards`에서 못 찾아 항상 404 → 프론트가 하드코딩된 안내 문구("질문을 확인했습니다...")로 덮어씀. RouterLLM이 정상 판별해도 이 경로 자체엔 영향 없지만, 판별에 실패하는 순간 이 404로 떨어진다 | `backend/app/main.py:104-110`(`CHAT_AGENT_NAMES`), `main.py:186-189`(fallback) | ⬜ 미반영 — 재현만 확인, 로컬 수정은 안 함(대신 "Workmate AI" 탭으로 우회 중) | `CHAT_AGENT_NAMES`에 `"Main Chatbot": "workmate-agent"` 매핑 추가 |
| R3 | CORS `allow_origins`가 5173/4173/3000 고정 목록이라, 프론트가 다른 포트(예: 5400)로 뜨면 preflight가 400으로 막혀 브라우저에서 `fetch()`가 "Failed to fetch"로 실패한다(서버는 살아 있어도 브라우저가 응답을 막음) | `backend/app/main.py:29-35`(`CORSMiddleware`) | ⬜ 미반영 — 프론트를 표준 포트(5173)로 재기동해 우회함 | 목록에 실제 쓰는 포트를 추가하거나, `allow_origin_regex`로 로컬 개발 포트 전체를 허용(운영 환경 설정과는 분리 필요) |
| R4 | `chat_reply()`가 `A2AError`를 HTTPException으로 감쌀 때 `detail`에 dict(`{"code","status","message"}`)를 그대로 넣는다. 프론트는 `detail`을 문자열로 가정하고 `new Error(detail)`을 만들어, 실제로는 `"[object Object]"`로 렌더링되며 진짜 에러 메시지가 화면에서 사라진다(R1을 진단할 때 컨테이너 로그를 직접 봐야 했던 이유) | `backend/app/main.py:303-304` | ⬜ 미반영 | `detail=exc.to_dict()["error"]` → `detail=exc.to_dict()["error"]["message"]`(또는 `str(exc)`)로 문자열 통일 — 같은 함수의 다른 except 분기(`detail=str(exc)`, 306행)와 형식이 맞춰짐 |
| R5 | 오케스트레이터가 담당자 식별값을 아예 안 보낸다 — 프론트의 "담당자" 드롭다운(`assignee.ts`)이 고른 이름(`assigneeName`)은 `payload.owner`로 백엔드까지는 오지만, `build_agent_request()`가 이걸 workmate-agent로 나가는 A2A 요청에 안 넣는다(로컬 Task Log 기록에만 씀, `main.py:323` 등). 그 결과 workmate-agent는 어떤 담당자가 물었는지 구분할 수 없어 고정 데모 사용자(`"service"`)로만 실행되고, `daily_briefing`이 항상 0건으로 나온다 | `backend/app/main.py`(`build_agent_request()`, `ChatReplyRequest`), `backend/app/a2a_client.py`(`send_message()`) | ✅ 2026-08-18 로컬 clone에 적용·종단 간 검증 완료(아래 참고) — 커밋·푸시는 안 함, 정식 반영은 담당자 쪽에서 | 정확히 두 지점, 각 한 줄. ① `main.py:286` 근처 `chat_reply()`에서 `request = build_agent_request(...)` 다음 줄에 `request["owner"] = payload.owner` 추가. ② `a2a_client.py:87-93`의 `send_message()`가 만드는 `metadata` dict(`SendMessageRequest.metadata` — `Message.metadata`가 아니다)에 `"owner": request.get("owner")` 추가. workmate-agent 쪽(`app/a2a/runtime.py`의 `RuntimeBootstrapExecutor._resolve_user_id()`)이 이 `metadata.owner`를 읽어 `ASSIGNEE_USER_IDS`로 매핑하도록 이미 구현·테스트 완료 — 로컬 재현으로 "Workmate AI" 채팅의 `daily_briefing` 응답에 실제 Task 데이터("우선순위 2건: 재화·경매장 처리 가이드 공유, 수정된 트랜잭션 로직 PR 반영")가 나오는 것까지 확인했다. "서선정"만 실제 Workmate 계정(Google 연동 데이터 있음)이고 나머지 3명은 아직 Workmate 계정 자체가 없어 매핑돼도 빈 결과만 나온다("서선정"의 실제 user_id와 자릿수·형식(숫자 21자리)만 맞춘 placeholder). 회의·일정·메일 신호는 이 컨테이너에 Google OAuth 토큰이 연결돼 있지 않아 여전히 0건이다(별도 작업 필요) |
| R6 | `build_agent_request()`가 `agent_name == "workmate-agent"`일 때 `skill_id`를 무조건 `"daily_briefing"`으로 고정한다(이 문서 "현재 상태" 1번, G1과 동일한 근본 문제) — 그 결과 "주간보고 작성해줘"처럼 다른 걸 물어도 항상 `daily_briefing`만 실행되고, `daily_briefing`의 메일 신호도 `assistant_ask`의 LLM 요약 없이 Gmail 원문 snippet(추적용 폭 없는 공백 문자 포함)이 그대로 노출된다(2026-08-18, Workmate 자체 "Workmate 어시스턴트" 위젯과 응답을 비교해 발견) | `backend/app/main.py:208-209`(`build_agent_request()`) | ✅ 2026-08-18 로컬 clone에 적용·종단 간 검증 완료 — 커밋·푸시는 안 함, 정식 반영은 담당자 쪽에서 | `request["skill_id"] = "daily_briefing"` → `request["skill_id"] = "assistant_ask"` **한 줄**. `a2a_client.py`는 안 건드려도 된다 — 원래는 `assistant_ask`가 요구하는 `payload.text`가 없어서 `a2a_client.py`도 같이 고쳐야 했는데, `app/workflows/assistant_router.py::assistant_ask_workflow()`가 `text` 없으면 `message`/`input`도 받아주도록 workmate-agent 쪽에서 이미 흡수했다(`m51_legacy_adapter.py`가 하던 것과 같은 호환 로직, 테스트 2개 포함 구현 완료: `test_message_key_is_accepted_when_text_is_absent`, `test_text_takes_priority_over_message_when_both_are_present`). 이 한 줄이 반영되면 11개 Skill 전체가 이 채팅에서 자연어로 실행되고(원래 이 문서 "목표"), 메일 요약도 `phrase_answer()`가 다듬어 준다 — R5(담당자 식별)와 같은 파일이라 한 번에 같이 요청하면 된다. 유일한 감안 사항: `analyze_meeting`처럼 오래 걸리는 Skill이 선택되면 `a2a_client.py`가 `configuration.returnImmediately`를 안 보내 응답을 끝까지 물고 있는다(G7과 같은 문제, `daily_briefing`/`weekly_report`/우선순위 같은 빠른 질문엔 무관). 최종 검증: "Workmate AI" 채팅에 "오늘 브리핑 알려줘"를 보내면 이제 `phrase_answer()`가 다듬은 자연어 답("오늘 브리핑입니다.\n\n- 오늘 일정: 0건\n- 메일 신호: 3건...")이 오고, 메일 신호도 Gmail 원문 대신 한 줄 요약(예: "Tae Soo Kim님 등 여러 사람들이 LinkedIn에서 의견을 나눔 — CHI 2026 논문(Honorable Mention Award) 공유")으로 나와 Workmate 자체 "Workmate 어시스턴트" 위젯과 형식까지 동일해졌다 |

**R5 구현 중 발견한 별도 버그**: 처음엔 `RuntimeBootstrapExecutor._resolve_user_id()`가 `context.message.metadata`를 읽도록 구현했으나, 실측 결과 `a2a_client.py`가 보내는 최상위 `metadata`는 `Message`가 아니라 `SendMessageRequest`(REST 요청 자체)의 필드였다 — a2a-sdk의 `SendMessageRequest.DESCRIPTOR.fields`가 `['tenant', 'message', 'configuration', 'metadata']`로 `message`와 `metadata`가 형제 필드임을 실측으로 확인했다. `context.metadata`(SDK가 이미 dict로 변환해 제공)로 읽도록 고쳐서 해결했다 — 워크플로우 함수를 직접 호출하면 정상 동작하는데 A2A 경로로만 안 되는 게 이 버그의 증상이었다.

**로컬 DB 연결**: `docker-compose.yml`의 `workmate-agent` 서비스에 `../workmate-agent/.runtime:/app/.runtime` 볼륨 마운트를 추가했다 — 이전엔 컨테이너를 새로 띄울 때마다 빈 SQLite가 생겨 어떤 user_id를 넣어도 결과가 비어 있었다. 로컬에서 `python -m app.server`로 직접 떠 있는 workmate-agent(Workmate 어시스턴트 위젯이 붙는 인스턴스)와 SQLite 파일을 공유하므로, 두 프로세스가 동시에 쓰면 드물게 파일 잠금 경합이 있을 수 있다 — 데모 목적으로만 감수, 운영에서는 Postgres(`DATABASE_URL`)로 교체 필요.

**로컬 Google 연동 연결(2026-08-18 후속)**: `../google-oauth-test/token.json:/app/google-oauth-test/token.json` 볼륨과 `GOOGLE_TOKEN_FILE=/app/google-oauth-test/token.json` 환경변수를 추가해 Gmail·Calendar 신호도 연결했다 — 컨테이너 안에서는 `daily_briefing.py`의 기본 토큰 경로 추정(`Path(__file__).resolve().parents[3]`)이 리포 레이아웃과 안 맞아 항상 빗나가므로 명시적으로 지정해야 했다. `load_google_credentials()`가 만료 시 같은 파일에 갱신된 토큰을 다시 쓰므로(`refresh_token` 보유) 로컬 프로세스와 공유해도 계속 유효하다. 최종 검증: "Workmate AI" 채팅의 `daily_briefing` 응답에 메일 신호 3건(실제 제목·본문 포함)과 우선순위 2건이 모두 나와 Workmate 자체 "Workmate 어시스턴트" 위젯 응답과 동일해졌다 — 일정만 여전히 0건인데, 위젯 쪽도 동일하게 0건이라 실제로 오늘 일정이 없는 것으로 보인다(버그 아님).

| R7 | R6 반영 후(=`assistant_ask`가 실제로 호출됨) `analyze_meeting`처럼 확인이 필요한 동작을 고르면 `assistant_ask`가 `pending_action`을 함께 돌려주는데, 채팅 UI엔 그걸 표시·재전송할 확인 버튼이 없어(G5) 그냥 텍스트만 오면 대화가 확인을 기다리며 멈춘 것처럼 보인다("분석하다가 죽었다"는 오해, 2026-08-19 실사용 중 발견) | `backend/app/a2a_client.py`(`_extract_answer`류), `backend/app/main.py:308`(`chat_reply()`) | ✅ 2026-08-19 로컬 clone에 적용·재현 검증 완료 — 커밋·푸시는 안 함 | `a2a_client.py`에 `_extract_pending_action(body)` 추가(Artifact의 JSON Data Part에서 `pending_action` 읽기 — `message:send`/`GET tasks/{id}` 두 응답 모양 다 처리, `workmate-agent/tools/m51_legacy_adapter.py::_legacy_response`와 같은 로직), `send_message()`/`poll_task()` 반환값에 `"pending_action"` 포함. `main.py::chat_reply()`가 `result.get("pending_action")`이 있으면 `answer` 끝에 `workmate-agent`의 `_PENDING_ACTION_NOTICE`와 동일한 문구("\n\n(이 요청은 실행 확인이 필요합니다 — Workmate 화면에서 직접 진행해 주세요.)")를 덧붙임. 검증: "오늘 한 회의 분석해줘" → `"'회의 8월 19일 09:45' 회의를 분석하겠습니다.\n\n(이 요청은 실행 확인이 필요합니다...)"` 확인 |

| R8 | R7의 "텍스트 안내만"으로는 확인이 필요한 동작(`analyze_meeting` 등)을 채팅에서 끝까지 실행할 방법이 없었다 — 사용자가 "확인"이라고 말해도 아무 일도 안 일어나 대화가 멈춘 것처럼 보임 | `backend/app/main.py::chat_reply()`, `backend/app/a2a_client.py::send_message()`, `frontend/src/App.tsx` 채팅 패널 | ✅ 2026-08-19 로컬 clone에 적용·종단 간(curl) 검증 완료 — 커밋·푸시는 안 함 | `ChatReplyRequest`에 `confirmed_skill_id`/`confirmed_arguments`(둘 다 optional) 추가 → 있으면 `a2a_client.py`가 워크메이트로 보내는 Data Part에 그대로 실어 재전송한다(`assistant_ask_workflow`가 이미 지원하는 계약이라 workmate-agent 쪽 변경 불필요, 18번 문서). 응답의 `pending_action`은 R7의 텍스트 안내 대신 `{skill_id, arguments}` **구조 그대로** 돌려준다(그 모양이 아닌 경우에만 R7의 안내 문구로 안전하게 폴백). `App.tsx`는 이 값을 받으면 답변 텍스트 아래 "확인/취소" 카드(기존 Task proposal 카드와 같은 렌더링 패턴)를 그리고, 확인을 누르면 `confirmed_skill_id`로 재전송한다. `analyze_meeting` 확인→실제 실행까지 curl로 종단 간 검증했다(부작용 없는 `daily_briefing`으로 배선만 검증, 실제 회의 분석은 비용이 들어 임의 실행하지 않음). |
| R9 | R8 적용 후에도 확인 카드가 **탭을 옮기거나 새로고침만 해도 사라졌다** — 대화 이력을 서버에서 다시 불러올 때 평문 텍스트로만 복원돼 확인할 수단이 없어짐(2026-08-19 실사용 중 발견) | `frontend/src/App.tsx`(세션 로드 `useEffect`), `backend/app/conversation_store.py`, `backend/app/main.py`(`ChatMessageRequest`/`save_chat_message`) | ✅ 2026-08-19 로컬 clone에 적용·재현 검증 완료 | `messages` 테이블에 `metadata`(nullable TEXT, JSON) 컬럼을 추가한다 — 기존 행은 전부 NULL로 남아 하위 호환(다른 채팅들이 읽던 필드는 그대로). `ChatMessageRequest`/`ConversationStore.append()`에 `pending_action`(optional)을 추가해 assistant 메시지와 함께 저장한다. 이력을 불러올 때(`rebuildChatFromHistory()`) **세션의 마지막 메시지에 `pending_action`이 있을 때만** 확인 카드로 복원한다 — 뒤에 이미 다른 메시지(확인 결과·취소 안내 등)가 쌓였다면 처리된 요청이라는 뜻이라 실수로 두 번 실행되지 않도록 평문으로만 보여준다. 카드 재전송에 필요한 원문 질문은 바로 앞 user 메시지를 재사용한다. |
| R10 | 확인 카드가 떠 있을 때 버튼 대신 "응"/"네" 같은 텍스트로 답하면 아무 반응이 없었다 — 이 채팅 경로가 대화 이력을 워크메이트에 안 보내(G8, R8 이후에도 유지된 제약) LLM이 "응"이 뭘 가리키는지 알 도리가 없어 그냥 일반적인 되물음("무엇을 도와드릴까요?")으로 답함(2026-08-19 실사용 중 발견 — "이 Action Item을 할 일로 추가할까요?"에 "응"으로 답했는데 할 일이 하나도 안 생긴 사례로 재현) | `frontend/src/App.tsx::submit()` | ✅ 2026-08-19 로컬 clone에 적용·재현 검증 완료 | LLM에 다시 판단을 맡기는 대신(G1이 이미 지적한 비결정성 리스크를 굳이 또 안 만듦) **순수 클라이언트 로직**으로 처리한다 — 화면에 뜬 마지막 채팅 항목이 확인 카드(`pending-action`, `state==="pending"`)이고 입력이 정확히 "응"/"네"/"넵"/"예"/"확인"/"좋아"/"오케이"/"yes"/"y"(긍정) 또는 "아니"/"아니요"/"아니오"/"취소"/"no"/"n"(부정)와 **일치할 때만** 새 질문으로 안 보내고 그 카드의 확인/취소를 누른 것처럼 처리한다. 정확히 일치할 때만 잡아 "아니 근데 그건" 같은 오탐을 피한다. |

R1은 로컬에서 적용·재현 검증까지 끝났고, R5·R6·R7·R8·R9·R10은 받는 쪽(workmate-agent) 구현·테스트까지 끝나 오케스트레이터가 코드 몇 줄만 추가하면 바로 동작한다(R8·R9·R10은 workmate-agent를 아예 안 건드리고 오케스트레이터 저장소 안에서만 완결된다). R2~R4는 원인만 확인된 상태다(재현됨, 수정 코드는 제안 수준). 열 건을 모아 PR 또는 이슈 하나로 요청하는 걸 권장한다 — R1은 매 채팅마다 재현되는 활성 장애라 우선순위가 가장 높고, R6·R7·R8은 서로 이어지는 한 묶음이다(R8은 R7이 먼저 반영돼야 의미가 생기고, R7은 R6가 먼저 반영돼야 `pending_action` 자체가 생긴다). R9·R10은 R8이 만든 확인 카드 UI에 대한 보강이라 R8과 함께 반영하는 게 자연스럽다.

### 22번 문서(오늘 브리핑·주간 업무보고 재이식) 관련 대기 항목

[22번 문서](22-today-briefing-weekly-report-port-plan.md)는 오케스트레이터 핵심부(공용 컴포넌트,
라우팅, 백엔드, 다른 화면과 공유하는 CSS)를 새로 건드리지 않는 걸 원칙으로 계획됐다(22번 문서
§0). 계획대로면 이 표에 추가할 항목이 없어야 정상이다. 구현 중 불가피하게 핵심부를 고쳐야 하는
상황이 생기면, 그 자리에서 처리하지 않고 여기 **R11부터** 위와 같은 형식(`# | 문제 | 위치 |
현재 상태 | 요청할 수정`)으로 이어서 기록한다.

## 관련 문서

- [15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md) — Workmate 화면·Skill
  기능 정의(Source of Truth). "Skill별 기능 설명" 표가 11개 Skill 전부를 "공개(Agent Card)"로
  정의한다 — 이 문서의 전제.
- [18-workmate-assistant-implementation-plan.md](18-workmate-assistant-implementation-plan.md) —
  `assistant_ask` 자연어 Router의 실제 설계·구현. 이 문서의 설계는 그 결과물을 그대로 재사용하는
  것이 핵심이다.
- [19-workmate-ui-orchestrator-port-plan.md](19-workmate-ui-orchestrator-port-plan.md) — 오케스트레이터
  ↔ Workmate 인증(OIDC) 문제를 REST 7개 화면 기준으로 먼저 다룬 문서.
- [m5.1-orchestrator-payload-plan.md](m5.1-orchestrator-payload-plan.md), `HANDOFF.md`의 M5.1
  이력 — 오케스트레이터 저장소를 직접 고칠 수 없다는 전제와 `m51_legacy_adapter.py`가 만들어진
  배경.
- `workmate-agent/tools/m51_legacy_adapter.py`, `AI-agent_game_platform/backend/app/{main,router,a2a_client,registry}.py` —
  이 문서의 모든 "현재 상태" 서술의 근거 코드.
