# Workmate 어시스턴트(Drawer) 구현 계획 및 완료 보고

작성일: 2026-08-17
상태: 계획 → 구현

## 배경

[15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md)의 "💬 Workmate 어시스턴트
(Drawer)" 절이 정의한 목표 기능(사이드 패널 UI, 어느 화면에서든 진입, 기존 5개 Skill + 신규 4개 Skill
후보)을 실제로 구현하기 위한 계획 문서다(신규 Skill은 구현 도중 `read_email`·`assistant_ask`가 추가로
붙어 최종적으로 6개가 됐다 — 아래 "핵심 설계 결정 1" 참고). 이 문서는:

1. 구현 순서·범위를 미리 정하고(계획 단계),
2. 구현이 끝나면 같은 문서에 완료 보고를 이어서 기록한다(완료 보고 단계) — 별도 이력 문서를 새로 만들지
   않고 계획과 결과를 한 문서에 같이 둔다.

15번 문서가 이미 정의한 **목표**(무엇을 만들 것인가)는 다시 옮겨 적지 않고, 여기서는 **어떻게·어떤
순서로** 만들지만 다룬다.

## 핵심 설계 결정

### 1. 신규 Skill은 "공개(A2A)" 목록에 넣지 않는다

`app/a2a/runtime.py`의 `_SKILLS`(5개, Agent Card·`/a2a/message:send`가 공유하는 **Orchestrator 공개
계약**)와 `app/internal_chat.py`의 `approved_skill_definitions()`(내부 검증·Drawer가 쓰는 **내부
계약**)는 지금까지 같은 5개였다. 이번에 추가하는 4개 신규 Skill(`get_meeting_analysis`·
`review_action_items`·`review_proposal`·`manage_tasks`)은 **내부 계약에만** 추가하고 `_SKILLS`/Agent
Card는 건드리지 않는다.

이유: `_SKILLS`를 넓히면 Service Token으로 호출하는 Orchestrator 공개 계약이 함께 넓어진다 — 이건 팀
공통 Orchestrator 통합 범위의 결정이라 이 저장소 혼자 내릴 결정이 아니다. 반면 내부 계약은
`workmate-ui`(사용자 OIDC 세션)에서만 호출되고 이미 이 세션 안에서 여러 번 확장해 온 경계라, Drawer가
쓸 Skill을 넓히는 데 지장이 없다. `WorkflowRegistry`는 두 경로가 공유하지만(같은 `.register()` 호출),
`approved_skill_definitions()`가 별도 허용 목록이라 내부 챗봇 경로에서만 신규 Skill을 받는다 — 공개
A2A 경로가 SDK 차원에서 Agent Card 밖 skill_id를 이미 거부하는지는 확인하지 않았고(A2A SDK 내부
구현), 안전한 쪽으로 최소 침습만 한다.

**갱신(2026-08-17, 최종 상태)**: 이 원칙은 그대로 유지됐지만 내부 전용 Skill 목록은 이후 두 번 더
늘었다. "Action Item → 할 일 추가"·"이메일 요약" 기능을 만들며 `assistant_ask`(자연어 Router, 아래
"핵심 설계 결정 2" 참고)와 `read_email`(제안함 밖 메일도 최근 30일 범위로 검색·요약)이 같은
`_INTERNAL_ONLY_SKILLS`에 추가됐다. 지금 `app/a2a/runtime.py`의 실제 구성은:

- `_SKILLS`(공개 5개, Agent Card·A2A 계약 — **변경 없음**): `daily_briefing`·`weekly_report`·
  `analyze_meeting`·`search_meetings`·`rank_priorities`.
- `_INTERNAL_ONLY_SKILLS`(내부 전용 6개): `get_meeting_analysis`·`review_action_items`·
  `review_proposal`·`manage_tasks`·`read_email`·`assistant_ask`.
- `approved_skill_definitions()`(내부 계약, Drawer가 쓰는 목록)는 위 11개(5+6)를 합쳐 반환한다.
  `assistant_ask` 자신을 뺀 나머지 10개가 `assistant_ask`가 대신 호출할 수 있는 대상이다.

`GET /.well-known/agent-card.json`은 지금도 공개 5개만 반환한다 — 이 결정이 실제로 지켜지고 있음을
실 서버로 반복 확인해 왔다(아래 "실 서버 확인" 절 참고).

### 2. Skill 입력의 자연어 자동 해석 — LLM Router로 전환 완료 (최초 계획에서 뒤집힘, 2026-08-17)

**최초 계획**은 15번 문서의 "자동 Skill 판별·자연어→구조화 파라미터 추출은 LLM Router가 필요해
범위 밖"이라는 결정을 그대로 따랐다 — 읽기 위주 기존 5개 Skill은 자연어 텍스트 그대로/최소 입력으로
충분하고, 신규 4개 Skill은 Drawer가 Skill별 **최소 구조화 입력**(드롭다운·간단한 폼 필드)을 보여줘
자유 문장을 자동으로 파싱하지 않는 쪽으로 시작했다(아래 "구현 순서"의 1~3단계, "단계 구분" 표의
4단계는 당시 범위 밖으로 명시).

**최종 상태는 이 결정을 뒤집었다.** 15번 문서가 자동 판별을 범위 밖에 둔 이유는 "필요하다는 근거가
아직 없어서"였을 뿐이라, 이후 사용자가 명시적으로 요청해 LLM Router를 추가 구현했고, 지금은 **채팅
UI에 자연어로 입력하면 오케스트레이터/Workmate 에이전트가 아니라 이 Drawer 내부에서 LLM이 Skill과
인자를 직접 판별한다**:

- 내부 전용(6개 중 하나) Skill `assistant_ask`(`app/workflows/assistant_router.py`)가 나머지 10개
  Skill(공개 5개 + 내부 전용 5개)을 대신 호출하는 Meta Skill이다. `route()`가 사용자 문장과
  Context(최근 회의 목록·분석 여부, 대기 중인 이메일/Calendar 제안, 방금 제시한 Action Item 후보
  목록, 최근 10턴 대화 이력)를 함께 보고 ① 그냥 답하기(`reply`) ② Skill 호출(`call_skill` +
  인자) ③ 되묻기 중 하나를 정하고, `phrase_answer()`가 그 결과를 자연스러운 한국어 답으로 바꾼다
  (두 번의 별도 LLM 호출 + 지시어 해석용 `_resolve_context_reference()` 호출 하나, 총 3개).
- Drawer의 Skill 드롭다운과 Skill별 구조화 입력 폼(회의 선택, Action Item 목록, 제안 카드, 할 일
  등록 폼)은 전부 걷어내고 순수 채팅 UI(메시지 입력창 + 대화 목록)로 교체했다 — 사용자가 더는
  Skill을 직접 고르지 않는다. 즉 "쓰기 액션은 구조화 입력, 읽기 액션은 자연어"라는 최초 계획의
  구분 자체가 더는 존재하지 않는다.
- 예외 하나는 남았다 — `manage_tasks`는 자연어 경로에서 `list`/`create`만 허용한다(`update`/
  `delete`는 LLM이 실제로 본 적 없는 `task_id`를 지어낼 위험이 있어 제외, 2026-08-16 결정을 그대로
  유지). task_id가 필요한 수정·삭제는 채팅이 "할 일 관리" 화면을 이용하라고 안내한다(Workflow
  자체는 update/delete도 지원하므로 JSON 모드 직접 호출로는 여전히 가능).

자세한 설계 배경·재현 시나리오·버그 수정 이력은 아래 "자연어 Router 추가 구현 완료" 절부터 문서
끝까지 시간순으로 이어진다.

### 3. 파괴적/비용이 큰 액션은 확인 단계를 한 번 더 거친다

**최초 계획**은 `manage_tasks`(action=`delete`)·`review_proposal`(decision=`ignore`)·
`review_action_items`(decision에 `reject` 포함) 세 경우만 대상으로, Drawer가 "실행" 버튼을 누르기
전에 "정말 실행할까요?" 확인 버튼을 한 번 더 보여주는 방식이었다 — 15번 문서의 Human-in-the-loop
원칙을 따른 것.

**최종 상태**는 대상이 하나 늘고 구현 메커니즘이 바뀌었다. `analyze_meeting`(파괴적이진 않지만
STT+LLM 비용이 들고 되돌릴 수 없는 동작, 2026-08-17 추가)까지 네 경우가 확인 대상이다
(`_requires_confirmation()`, `app/workflows/assistant_router.py`). Drawer가 구조화 폼이었을 때는
화면의 확인 버튼이 그대로 이 역할을 했지만, 채팅 UI로 바뀐 지금은 `route()`가 `pending_action`을
답에 함께 실어 돌려주고, 말풍선 아래 뜨는 "확인"/"취소" 버튼 중 "확인"을 누르면 같은
`skill_id`·`arguments`를 `confirmed_skill_id`로 다시 보내야 실제로 실행된다(이때 Router는 LLM을
다시 부르지 않는다).

### 4. 단계 구분

| 단계 | 범위 | 최초 계획 | 최종 상태(2026-08-17) |
| --- | --- | --- | --- |
| 1단계 | 백엔드 4개 신규 Skill(Workflow + Schema) | ✅ 포함 | ✅ 완료 — 이후 `read_email`·`assistant_ask`가 추가로 붙어 내부 전용 Skill 총 6개(핵심 설계 결정 1 참고) |
| 2단계 | Drawer 컴포넌트(플로팅 버튼·슬라이드 패널·대화 이력·Task Polling 재사용) | ✅ 포함 | ✅ 완료 |
| 3단계 | Skill별 최소 구조화 입력 UI(드롭다운·폼) + 파괴적 액션 확인 단계 | ✅ 포함 | ⚠️ 구조화 입력 UI는 4단계가 뒤집히며 전부 걷어내고 채팅 UI로 교체(확인 단계 자체는 `pending_action` 메커니즘으로 유지, 핵심 설계 결정 3 참고) |
| 4단계 | 자연어→Skill 자동 판별(LLM Router) | ⬜ 범위 밖(15번 문서에서 이미 제외 결정) | ✅ 사용자 요청으로 뒤집혀 구현 완료 — `assistant_ask`가 나머지 10개 Skill을 대신 호출(핵심 설계 결정 2 참고) |
| 5단계 | `manage_tasks`의 update UI를 Drawer 폼으로 세밀하게 다듬기(당시엔 list/create/delete만 폼, update는 JSON 모드로만 가능이 전제) | ⬜ 후속 | ⬜ 전제 자체가 사라짐 — Drawer가 폼이 아니라 채팅이 되면서 `update`/`delete`는 자연어 경로에서 아예 제외하고 "할 일 관리" 화면으로 안내하는 쪽으로 최종 결정(JSON 모드 직접 호출로는 여전히 가능) |

## 구현 순서

1. 백엔드: `app/workflows/assistant_skills.py`(신규) — 4개 Skill Workflow를 기존 REST 함수를 그대로
   호출하는 얇은 어댑터로 구현.
2. 백엔드: `docs/schemas/workmate-skill-schemas.schema.json`에 4개 Input Schema 추가.
3. 백엔드: `app/internal_chat.py`의 `approved_skill_definitions()`를 9개로 확장(공개 `_SKILLS`는
   그대로 5개 유지), `_ASYNC_SKILLS`는 그대로(신규 4개는 모두 짧게 끝나 동기 유지).
4. 백엔드: `app/a2a/runtime.py`의 `workflow_registry()`에 4개 신규 Workflow 등록.
5. 백엔드 테스트: 4개 Skill 각각 성공·실패 경로, `approved_skill_definitions()` 개수 확인.
6. 프론트: `lib/assistant-skills.ts`(신규) — Skill별 표시 이름·입력 종류(자연어/드롭다운/폼) 메타데이터.
7. 프론트: `app/views/AssistantDrawer.tsx`(신규) — 플로팅 버튼 + Drawer 본체.
8. 프론트: `page.tsx`의 `Shell`에 전역 마운트.
9. 프론트 테스트: 순수 로직 함수 단위 테스트.
10. 백엔드·프론트 전체 회귀 재실행, 서버 재기동, 실 동작 확인.
11. 이 문서에 완료 보고 추가.

---

## 구현 완료 보고 (2026-08-17)

계획한 1~3단계(백엔드 4개 신규 Skill, Drawer 컴포넌트, Skill별 최소 구조화 입력 + 파괴적 액션 확인)를
모두 구현했다. 4단계(자연어 자동 판별)는 계획대로 범위 밖으로 남겼고, 5단계(`manage_tasks` update의
Drawer 폼 UI)도 계획대로 후속으로 미뤘다 — 백엔드 `manage_tasks` Skill 자체는 `update` action을 이미
지원하므로 JSON 모드로는 지금도 가능하다.

### 백엔드

- **`app/workflows/assistant_skills.py`(신규)**: 4개 Skill Workflow —
  - `get_meeting_analysis_workflow`: `app/action_item_api.get_meeting_analysis()`를 그대로 호출.
  - `review_action_items_workflow`: `app/action_item_api.review_actions()`를 그대로 호출, `decisions`를
    `ActionDecision` 목록으로 검증.
  - `review_proposal_workflow`: `app/proposal_api._review()`(이메일·Calendar REST 두 엔드포인트가
    공유하는 내부 함수)를 그대로 호출 — 화면(`Proposals.tsx`)과 같은 유사 Task 검사·멱등성 규칙을
    그대로 물려받는다.
  - `manage_tasks_workflow`: `app/task_api.py`의 `list_tasks`/`create_task`/`update_task`/`delete_task`를
    `action` 파라미터로 묶어 그대로 호출.
  - 넷 다 새 업무 규칙을 만들지 않는 얇은 어댑터다 — 실패 시 각 REST 함수가 이미 내던 `HTTPException`을
    그대로 전파해(FastAPI가 CORS 포함 정상 처리), 필드 검증 실패는 `ValueError`로 통일해 422로 변환되게
    했다.
- **`docs/schemas/workmate-skill-schemas.schema.json`**: `GetMeetingAnalysisInput`·
  `ReviewActionItemsInput`(+ `ActionItemDecision`)·`ReviewProposalInput`·`ManageTasksInput` 4개 `$defs`
  추가, 루트 `oneOf`에 등록.
- **`app/a2a/runtime.py`**: `_SKILLS`(공개 5개, Agent Card)는 그대로 두고 `_INTERNAL_ONLY_SKILLS`(신규
  4개)를 별도로 추가 — `approved_skill_definitions()`가 `(*_SKILLS, *_INTERNAL_ONLY_SKILLS)`를 합쳐
  반환한다. `workflow_registry()`에 4개 Workflow를 등록했다(같은 Registry를 공개 A2A 경로와 공유하지만,
  Agent Card에 없어 내부 검증·Drawer 경로에서만 실제로 호출된다).
- **검증**: `tests/test_assistant_skills.py`(신규, 11 tests) — 4개 Skill 각각 성공 경로(실 Repository로
  Task/Meeting/Proposal 생성·검증)와 대표 실패 경로(필수 필드 누락, 미분석 회의 404, 빈 `decisions`,
  잘못된 `source_type`, 지원하지 않는 `action`). `tests/test_internal_chat.py`의 기존
  `test_lists_the_same_five_skills_as_agent_card`를
  `test_lists_the_five_public_skills_plus_internal_only_assistant_skills`로 교체해 "내부 경로가
  Agent Card의 상위집합"이라는 새 계약을 검증. 백엔드 전체 회귀 **295 tests**(`DATABASE_URL` 없이
  283 passed/12 skipped, `WORKMATE_TEST_DATABASE_URL` 포함 295 passed/0 skipped 둘 다 확인).

### 프론트엔드

- **`lib/workmate-format.ts`**: `getMeetingAnalysisInput`·`reviewActionItemsInput`·`reviewProposalInput`·
  `manageTasksInput` 4개 입력 빌더 추가 — 기존 `baseSkillInput()` 패턴을 그대로 따른다.
- **`app/views/AssistantDrawer.tsx`(신규)**: 우측 하단 플로팅 버튼(💬) + 슬라이드 패널. Skill 드롭다운으로
  9개 전부(공개 5개 + 신규 4개) 선택 가능하고, Skill별로 다른 최소 입력 UI를 보여준다 —
  읽기 위주 3개(`daily_briefing`/`weekly_report`/`rank_priorities`)는 버튼만, `search_meetings`는
  질문 입력창, `analyze_meeting`/`get_meeting_analysis`/`review_action_items`는 회의 선택 드롭다운,
  `review_proposal`은 현재 대기 중인 제안 카드 목록(`useProposalNotifications()`를 그대로 재사용),
  `manage_tasks`는 목록 조회 버튼 + 제목·마감일 입력 등록 폼(수정·삭제는 이번 범위에서 제외, 안내
  문구로 명시). 실행 결과는 세션 동안 쌓이는 로그(대화 이력)로 보여준다. `analyze_meeting`은 비동기라
  `GET .../tasks/{id}`를 Polling(17번 갭 문서 #7과 같은 방식)한다. 거절(`review_action_items`)·무시
  (`review_proposal`)는 실행 전에 "정말 실행할까요?" 확인을 한 번 더 거친다(15번 문서 Human-in-the-loop
  원칙) — `manage_tasks` 삭제는 이번 Drawer UI 범위에 없어 해당 확인 UI도 아직 없다(할 일 관리 화면에서
  기존 확인창을 그대로 씀).
- **`app/globals.css`**: `.assistant-fab`/`.assistant-scrim`/`.assistant-drawer`/`.assistant-log`/
  `.assistant-entry`/`.assistant-confirm` 등 신규 클래스 추가 — 어느 화면에서든 겹쳐 여닫는 전역 UI라
  다른 화면처럼 인라인 스타일 위주로 두지 않고 재사용 가능한 클래스로 뺐다.
- **`app/page.tsx`**: `Shell`에 `<AssistantDrawer />`를 전역으로 마운트.
- **검증**: `tests/workmate-format.test.mts`에 4개 입력 빌더 테스트 추가(총 49 tests). `npx tsc --noEmit`
  (오류 없음), `npm run lint`(0 errors — `react-hooks/purity`·`rules-of-hooks` 위반 2건을 고치는 과정을
  거침, 아래 참고), `npm test`(49 tests 통과, `vinext build` 성공).

### 구현 중 발견·수정한 문제

- **React Compiler 순수성 규칙**: `runSkill` 안의 `Date.now()`/`Math.random()`(로그 ID 생성, Polling
  시간 측정)이 "렌더 중 호출될 수 있는 비순수 함수"로 lint 오류가 났다 — `lib/use-skill.ts`의
  `usePollingSkillRunner`와 같은 이유로 `useCallback`으로 감싸 해결했다.
- **Rules of Hooks 위반**: 위 수정으로 `useCallback` 호출이 늘면서, 기존에 있던 `if (!auth.token) return
  null;` 조건부 반환이 그 사이에 끼어 있어 "Hook이 조건부로 호출된다"는 오류가 났다 — 모든 Hook 호출을
  먼저 끝내고 조건부 반환을 JSX 렌더 직전으로 옮겨 해결했다(React Hooks 규칙: 호출 순서 고정).

### 남은 범위(계획대로 후속)

- `manage_tasks`의 `update`를 위한 전용 폼(지금은 자연어로 "수정해줘"라고 해도 Router가 거절하고 "할
  일 관리" 화면을 안내한다 — task_id를 사용자 문장에서 알 방법이 없어서다. 아래 "자연어 Router" 절 참고).
- 내부 API·모듈 이름의 "internal"이 최종 사용자 기능이 된 지금 더는 정확하지 않다는 점(15번 문서에서도
  이미 지적) — 이번 구현에서는 이름을 바꾸지 않았다(엔드포인트 경로 변경은 하위 호환 문제라 별도 결정
  필요).

### 자연어 Router 추가 구현 완료(2026-08-17)

위 "남은 범위"에 있던 "자연어 문장에서 Skill·파라미터를 자동으로 뽑아내는 LLM Router"를, 이후 사용자가
명시적으로 요청해 추가 구현했다 — 15번 문서가 애초에 이를 범위 밖으로 뒀던 건 "필요하다는 근거가 아직
없어서"였을 뿐이었다.

**설계**: 신규 내부 전용(10번째) Skill `assistant_ask`(`app/workflows/assistant_router.py`)가 LLM을 두
번 호출한다 — ① `route()`: 사용자 문장을 보고 기존 9개 Skill 중 어떤 것을 어떤 인자로 부를지(또는 그냥
답하거나 되물을지) 정한다. ② `phrase_answer()`: 실행된 Skill의 구조화 결과(JSON)를 사용자 질문에 대한
자연어 한국어 답으로 바꾼다. `route()`의 출력 Schema는 Skill마다 인자 모양이 달라 `arguments` 필드를
`strict: true` JSON Schema로 고정할 수 없다 — 이 호출만 `email_action_items.py`·`meeting_analysis.py`와
달리 `strict`를 끈다.

**Human-in-the-loop 유지**: 파괴적 조합(`review_action_items`의 `reject` 결정, `review_proposal`의
`ignore` 결정, `manage_tasks`의 `delete`)은 Router가 스스로 실행하지 않고 "이대로 실행할까요?" 확인만
돌려준다(`pending_action`) — Drawer가 확인 버튼을 눌러야 같은 `skill_id`·`arguments`를
`confirmed_skill_id`로 다시 보내 실제로 실행되고, 이땐 Router가 다시 LLM에 묻지 않는다. `manage_tasks`는
`update`/`delete` 자체를 아예 제안하지 않는다 — LLM이 본 적 없는 `task_id`를 지어낼 위험이 있어서다
(기존 Drawer 구조화 폼과 같은 범위 유지).

**ID 해석 문제**: 회의 ID·제안 ID처럼 사용자 문장에 없는 값을 LLM이 지어내지 않도록, 프론트가 이미 아는
최근 회의 목록(`meetingsApi.list`)과 대기 중인 제안 목록(`useProposalNotifications`)을 매 메시지 전송
때 `context`로 함께 보내 이름으로 매칭하게 한다 — 백엔드엔 "대기 중인 제안" 저장소가 없다(제안은 SSE로만
흘러 프론트 상태에만 있다).

**비동기 처리**: `assistant_ask`가 어떤 Skill로 풀릴지는 호출 전엔 알 수 없고, `analyze_meeting`으로
풀리면 STT+LLM만큼 오래 걸릴 수 있다 — 그래서 이 Skill도 `analyze_meeting`과 함께
`app/internal_chat.py`의 `_ASYNC_SKILLS`에 넣어 항상 Task Polling 경로를 태운다. Task Store가
`data`/`markdown`을 저장하지 않는 기존 제약을 피하려고, 결과 Artifact의 `text`에 프론트가 파싱할 수 있는
답변 Envelope(`{"type": "assistant_reply", "data": {"reply", "executed_skill_id", "pending_action"}}`)를
그대로 담는다(`lib/workmate-format.ts`의 `parseAssistantReply`가 읽는다).

**프론트**: `AssistantDrawer.tsx`의 Skill 드롭다운 + Skill별 입력 폼(회의 선택, Action Item 목록, 제안
카드, 할 일 폼)을 전부 걷어내고 채팅 UI(메시지 입력창 + 대화 목록)로 바꿨다 — 이제 Skill 선택 자체가
없다. 확인이 필요한 답변은 말풍선 아래 "확인"/"취소" 버튼이 붙는다.

**검증**: 백엔드 새 테스트 17개(`tests/test_assistant_router.py` 16개 — `route`/`phrase_answer`/
`assistant_ask_workflow` 각각의 성공·실패·파괴적 동작 확인 경로, `tests/test_internal_chat.py` 1개 —
HTTP 경계의 Task Polling 왕복), 전체 317개 통과. 프론트 새 테스트 7개(`assistantAskInput`·
`parseAssistantReply`), 전체 66개 통과, `tsc --noEmit`·`npm run lint` 모두 무오류. 실 서버(재기동한
백엔드, 실제 Postgres 데이터)에 `assistant_ask_workflow`를 직접 호출해 "오늘 브리핑 보여줘" → 실제
Task 1건·메일 신호 10건을 근거로 한 자연스러운 한국어 답변을 받는 것까지 확인했다(Mock 아님).

### 실 서버 확인

백엔드·프론트 재기동 후 확인:
- `approved_skill_definitions()`가 실행 중 프로세스에서 9개(`daily_briefing`·`weekly_report`·
  `analyze_meeting`·`search_meetings`·`rank_priorities`·`get_meeting_analysis`·`review_action_items`·
  `review_proposal`·`manage_tasks`) 반환 확인(자연어 Router `assistant_ask` 추가 이후엔 10개 — 아래
  "자연어 Router 추가 구현 완료" 절 참고).
- `GET /.well-known/agent-card.json`은 여전히 공개 5개만 반환 — 핵심 설계 결정 #1(Orchestrator 공개
  계약 미변경)이 실제로 지켜졌는지 직접 확인.
- 배포된 프론트 번들에 `"Workmate 어시스턴트"`·`"assistant-fab"`·`"manage_tasks"` 문자열이 실제로
  포함된 것을 확인(빌드·배포가 최신 코드를 반영).

### 실사용 중 발견·수정한 버그(2026-08-17)

- **`week_of` 기준일 누락**: "오늘일자 기준으로 지난 일주일 주간보고 작성해줘"라고 물었는데 기간이
  미래(2026-08-17~08-24)로 나왔다. `route()`의 System Prompt에 오늘 날짜가 전혀 없어 LLM이 상대
  시점("지난 주")을 계산할 방법이 없었고, `week_of`를 비운 채 보내 서버 기본값("이번 주" = 오늘부터
  7일)이 그대로 나갔다. `route()`에 타임존 기준 오늘 날짜를 명시적으로 넣고, `week_of`가 "그 날짜가
  속한 주"가 아니라 "그 날짜부터 7일간"이라는 것도 카탈로그에 명시해 고쳤다. 재현 문장으로 직접
  확인 — 이제 `week_of: '2026-08-10'`을 정확히 계산해 기간이 2026-08-10~08-17로 나온다.
- **`arguments` 자유 Schema가 이 LLM Provider에서 신뢰할 수 없었음**: "최근에 이메일로 받은 요청중에
  타임아웃 나는 api 수정 요청받은게 있는데 내용 찾아줘"라고 물으니 "router response has an invalid
  action" 오류가 그대로 노출됐다. 원인을 좁혀보니, Skill마다 인자 모양이 달라 `arguments`를 자유
  `object`로 두고 `strict: true`를 껐던 최초 설계가 문제였다 — 이 Provider는 그 느슨한 Schema를
  사실상 무시하고 **Schema 정의 자체를 완료 결과로 그대로 반환**했다(`route()`가 그걸 `action` 필드가
  없는 응답으로 보고 오류를 냈다). `strict: true`로 바꿔보면 반대로 매 요청이 HTTP 400으로 거부됐다
  (`additionalProperties: false` + 모든 속성이 `required`에 있어야 하는 Strict 모드 요건을, 자유
  `object` `arguments`가 만족하지 못해서다). 최종적으로 모든 Skill의 인자 후보 필드를 한 평평한
  Nullable `object`에 다 펼쳐 놓고(`_ARGUMENTS_SCHEMA`) `strict: true`로 호출하도록 바꿨다 — 실제
  선택된 `skill_id`에 맞는 필드만 채우고 나머지는 `null`로 두게 카탈로그가 안내한다. 부수 효과로,
  `review_proposal` 승인에 필요한 `task`(제목·담당자) 필드는 더는 LLM에 맡기지 않는다 — 담당자는
  항상 호출자 본인으로 결정적이고, 제목은 프론트가 보낸 Context의 제안 원본 제목을 그대로 쓰도록
  `assistant_ask_workflow`가 직접 채운다(`_default_proposal_task`). 재현 문장 포함 6가지 질문으로
  직접 재확인 — 더는 오류 없이 각각 알맞게 답하거나(모르면 되묻기) 알맞은 Skill을 호출한다.
- 새 단위 테스트 9개(오늘 날짜 프롬프트·`strict: true` 전송·Nullable 필드 정리·`review_proposal` 승인
  Task 자동 채움 등) 추가, 백엔드 전체 327개 테스트 통과.
- **정보 질문을 파괴적 Skill로 잘못 골랐던 문제**: "신규 입사자 환영회 언제인지 캘린더에서 찾아줘"라고
  물었는데, 확인 배너("'review_proposal'를 요청하신 내용대로 실행할까요?")가 떴다 — 사용자가 그냥
  일정을 조회하려 했을 뿐인데 LLM이 대기 중인 같은 이름의 Calendar 제안을 **무시(`decision: "ignore"`)
  하려는 요청**으로 오판했다. Human-in-the-loop 확인 단계가 있어 실제로 무시되진 않았지만(설계가
  의도대로 동작), 원인은 두 가지였다 — ① Context에 Calendar 제안의 일정 시각(`due_at`)이 아예 없어
  LLM이 "언제인지"에 직접 답할 방법이 없었고, ② System Prompt가 "Context와 관련 있어 보이는 항목이면
  review_proposal을 써도 된다"고 오해할 여지를 남겼다. `AssistantAskContextProposal`에 `due_at`을
  추가하고(스키마·`lib/workmate-format.ts`·`AssistantDrawer.tsx`의 Context 조립 코드까지), System
  Prompt에 "정보를 묻는 질문과 명시적 실행 요청을 구분하라 — Context에 답이 있으면 미루지 말고 그 값을
  그대로 답하라"는 안내를 추가했다. 부수적으로 `reply`를 `call_skill`일 때도 항상 채우도록 해, 확인
  배너 문구가 더는 Skill ID를 그대로 노출하지 않고("'신규 입사자 환영회' 제안을 무시할게요"처럼) 무엇을
  하려는지 설명한다. 재현 문장과 명시적 실행 요청("무시해줘") 둘 다 실제 Provider로 재확인 — 조회
  질문은 이제 일정 시각을 직접 답하고, 실행 요청만 확인 배너를 띄운다. 새 테스트 2개 추가.
- **위 수정 직후에도 남아 있던 "미루는 답변"**: 같은 질문을 다시 보내니 이번엔 확인 배너 대신
  "'신규 입사자 환영회'가 언제인지 캘린더에서 찾아드릴게요"처럼, 답도 아니고 "모른다"는 인정도 아닌
  **약속형 문장**으로 얼버무렸다(후속 턴이 없어 사실상 무응답과 같다). System Prompt에 "reply는
  즉시 끝나는 최종 답이다 — '찾아드릴게요'·'확인해드릴게요' 같은 약속형 문장 금지, Context에 사실이
  있으면 그대로 인용해 답하고 없으면 '~에 대한 정보가 없습니다'로 정직하게 인정하라"를 명시적으로
  추가했다. 재현 문장으로 8회 반복 확인(Context 없음 5회, due_at 있는 Context 3회) — 약속형 문장은
  한 번도 나오지 않았다. 다만 due_at이 실제로 Context에 있는데도 "정보가 없습니다"로 잘못 답한
  경우가 3회 중 1회 있었다 — 심각한 오답(파괴적 동작·거짓 답변)은 아니지만 LLM의 확률적 한계로 남아
  있는 잔여 불완전성이며, 추가 개선 여지로 기록해 둔다. 새 테스트 1개 추가, 백엔드 전체 330개 테스트
  통과.
- **날짜·시각 답변을 ISO 8601 원문으로 그대로 노출**: "'신입사원 환영회' 일정은
  2026-08-19T05:45:00+09:00입니다" 같은 원문 노출 대신 "2026년 8월 19일 오전 5시 45분입니다"처럼
  자연스러운 한국어로 바꿔 달라는 요청을 받아, `route()`·`phrase_answer()` 두 System Prompt 모두에
  변환 지침과 예시를 추가했다. 실제 Provider로 재확인 — 요청한 형식대로 정확히 나온다. 새 테스트
  2개 추가, 백엔드 전체 332개 테스트 통과.
- **"이메일로 받은 요청 찾아줘"가 항상 "정보 없음"으로 끝난 문제**: "최근에 이메일로 받은 요청중에
  타임아웃 나는 api 수정 요청받은게 있는데 내용 찾아줘"라고 물으면 항상 "제안함이나 메일함에서 직접
  확인해 주세요"로 끝났다. Postgres를 직접 조회해 보니 그 요청은 **이미 승인되어 정확히 일치하는
  제목의 Task로 남아 있었다**(source_type=email) — 이메일 본문 검색 기능이 없는 건 맞지만(설계상
  의도), Router가 `manage_tasks(list)`로 이미 승인된 Task 목록을 확인해 볼 생각을 아예 안 하고
  바로 포기한 게 진짜 원인이었다. Context엔 **대기 중인(미검토)** 제안만 있고, 이미 승인된 제안은
  Task로 바뀌어 있어 Context 밖에 있다는 게 근본 원인이다. `manage_tasks` 카탈로그 설명에 "예전에
  받은 요청을 찾는 질문은 모른다고 답하기 전에 반드시 먼저 action=list로 실제 목록을 조회하라"는
  지침을 추가했다. 실제 사용자 계정·실제 Postgres 데이터로 전체 파이프라인을 다시 실행해 확인 —
  이제 정확히 그 Task를 찾아 제목·상태·마감일까지 설명한다. 새 테스트 1개 추가, 백엔드 전체 333개
  테스트 통과.
- **표현이 살짝 다른 질문은 Context에 답이 있어도 자주 놓침**: 같은 대화에서 "신입사원 환영회는
  언제지?"는 성공했는데(원문 그대로 답함), 거의 같은 취지의 "신입사원 환영회가 언제지?"는 실패했다
  ("정보 없음"). 재현해 10회씩 반복해 보니, Prompt 지침만으로는 "신입사원 환영회"(질문)와 Context의
  "신규 입사자 환영회"(제목)처럼 표현이 다르면 **10번 중 8번**을 놓쳤다 — Prompt 안내만으로 LLM의
  검색 능력에 기대는 데는 한계가 있었다.
  - **1차 시도(문자열 유사도)**: Python으로 사용자 문장과 Context 제목의 최장 공통 부분 문자열
    비율을 계산해 System Prompt에 강조하는 방식을 먼저 시도했다. 실패율이 80%→5%로 줄긴 했지만,
    사용자가 "조사 하나만 바뀌어도 못 찾는 게 확실하다"며 이 방식 자체(문자열 겹침에 기대는 접근)에
    문제를 제기했다 — 표현이 아예 다른 동의어는 여전히 놓칠 근본적 한계가 있었다.
  - **최종 채택(전용 LLM 매칭 호출)**: 사용자에게 대안을 확인한 뒤(문자열 유사도 유지·임베딩 기반
    의미 유사도·전용 LLM 매칭 중 전용 LLM 매칭을 선택), Routing·인자 추출과 같은 프롬프트에서
    판단하게 하던 것을, "이 문장이 번호 붙은 Context 목록 중 무엇을 가리키는가"만 묻는 별도의 작고
    집중된 LLM 호출(`_resolve_context_reference`)로 분리했다. 조사·어미·동의어가 달라도 같은 대상을
    가리키면 찾으라고 명시했다. 같은 재현 시나리오를 20회 반복 — **실패 0/20(0%)**. 관련 없는 질문
    3개(오늘 브리핑·주간보고·할 일 목록)로 오탐(false positive) 여부도 확인 — 모두 제 Skill로
    정상 라우팅되고 무관한 Calendar 제안에 엮이지 않았다. LLM 호출이 하나(총 3개) 늘어 응답이
    조금 느려지지만 정확도 향상이 더 중요하다고 판단했다. 새 테스트 7개(기존 문자열 유사도 테스트는
    전부 교체), 백엔드 전체 340개 테스트 통과.
- **대화 이력 없이 매 요청을 독립적으로 처리 — 짧은 후속 메시지가 맥락을 잃음**: "싱잉사원 환영회
  언제?"(오타)는 "정보 없음"으로 답했는데, 사용자가 오타만 고쳐 "신입사원"이라고 짧게 다시 보내니
  "언제인지" 질문이 아니라 "이 제안을 승인할지 무시할지" 되물었다. 원인은 명확했다 — `assistant_ask`가
  매 메시지를 완전히 독립적으로 처리해, 대화 이력을 전혀 몰랐다("컨텍스트 저장 안 하냐"는 사용자
  질문 그대로). `route()`·전용 매칭 호출(`_resolve_context_reference`) 둘 다 이전 turn을 실제
  user/assistant Chat 메시지로 함께 받도록 `history` 파라미터를 추가했다(`_history_messages()`,
  최근 10턴까지). Schema에 `AssistantAskInput.history` 추가, `AssistantDrawer.tsx`가 매 전송마다
  직전까지의(이번 턴 제외) 완료된 메시지를 `{role, text}`로 스냅샷 떠 함께 보낸다. 재현 시나리오
  (오타 질문 → 짧은 정정)로 5회 반복 확인 — 모두 정확히 날짜로 답했다. 새 테스트 9개(백엔드 6개,
  프론트 2개, `AssistantAskWorkflowTests` 1개) 추가, 백엔드 전체 345개·프론트 68개 테스트 통과.

### Action Item → 할 일 추가 확인(Human-in-the-loop) 추가(2026-08-17)

사용자 요청 — 회의 분석(`analyze_meeting`·`get_meeting_analysis`) 결과를 채팅으로 보여준 뒤, 아직
검토 안 한(pending) Action Item이 있으면 할 일로 추가할지 먼저 물어보게 했다. 자동으로 Task를
만들지 않는다 — 파괴적 동작 확인과 같은 `pending_action` 메커니즘을 그대로 재사용해서(신규 UI 없이)
Drawer가 이미 그릴 줄 아는 확인 배너("취소"/"확인")를 그대로 띄운다. "확인"을 누르면 대기 항목을
전부 승인(=Task 생성)한다 — 일부만 고르고 싶으면 대화 이력이 이제 유지되니 "2번만 승인해줘"처럼
채팅으로 다시 요청하면 된다.

**검증**: 실제 계정·실제 Postgres 데이터로 전체 파이프라인을 두 단계 다 실행해 확인했다 — ①
`get_meeting_analysis`로 이미 저장된 분석(Action Item 3건, 전부 pending)을 조회하니 답변 뒤에
"이 Action Item을 할 일로 추가할까요?"가 붙고 `pending_action`이 올바르게 채워졌다. ② 그 `pending_action`
그대로 `confirmed_skill_id`로 재호출(확인 버튼을 누른 상황)하니 실제로 Action Item 3건이 전부
승인되고, Postgres에 대응하는 Task 3건이 실제로 생성된 것까지 확인했다. 새 테스트 8개 추가, 백엔드
전체 353개 테스트 통과.

### `analyze_meeting` 실행 전 확인·회의 특정 모호성 처리(2026-08-17)

사용자 요청 — 자연어로 "방금 진행한 회의 분석해"라고만 말해도 Router가 Context에서 하나를 골라
곧바로 `analyze_meeting`을 실행해 버렸다. STT+LLM 비용이 드는 작업인데, 회의 제목이 자리표시자
("회의 8월 17일 16:06")라 비슷한 시각의 회의가 여러 개면 엉뚱한 걸 분석할 위험이 있었다.

**수정**: `_is_destructive()`를 `_requires_confirmation()`으로 넓혀 `analyze_meeting`은 무조건
확인이 필요하게 했다(파괴적이진 않아도 되돌릴 수 없는 비용이 드는 동작이라는 새 범주). Skill
카탈로그에는 "Context에서 회의가 하나로 확실히 특정되지 않으면(비슷한 시각의 후보가 여럿이거나
표현이 모호하면) 절대 짐작해서 고르지 말고, 후보를 날짜·시각과 함께 목록으로 보여주며 되물어라"는
지침을 추가했다 — 대화 이력(바로 위 기능)이 있어 사용자가 "16시 51분 회의"처럼 후속 메시지로
특정하면 자연스럽게 이어진다. 하나로 특정된 뒤에도 확인 배너를 거쳐야 실제로 실행된다.

**검증**: 실제 Provider로 4개의 비슷한 시각 회의가 있는 Context에 "방금 진행한 회의 분석해"를
넣어보니, 짐작하지 않고 4개 후보를 번호와 시각으로 나열하며 되물었다. 이어서 대화 이력과 함께
"16시 51분 회의"라고 답하니 정확히 그 회의로 특정해 `analyze_meeting`을 제안했다(확인 필요 상태로).
새 테스트 3개 추가(기존 2개는 `confirmed_skill_id` 경로로 수정), 백엔드 전체 365개 테스트 통과.

### 회의 삭제 후 "회의록에서 보기" 근거 링크가 끊기는 문제(2026-08-17)

사용자가 직접 중복 회의를 정리(삭제)한 뒤, 챗봇으로 Action Item을 승인해 만든 Task 중 하나에서
"회의록에서 보기" 버튼이 안 보인다고 알려왔다. 조사해보니 두 가지가 겹쳐 있었다 — ① 겉보기에
비슷한 제목의 Task가 실은 `source_type="manual"`(직접 만든 Task, 애초에 근거가 없음)이었고,
② 진짜 챗봇 승인으로 만든 Task는 `source_type="action_item"`이 맞는데도 근거 링크가 비어 있었다.
②의 원인은 이번 세션에서 먼저 추가한 회의 삭제 기능(Soft Delete)이었다 — `SQLiteMeetingRepository.get()`이
기본적으로 삭제된 회의를 숨기도록 바꿨는데, Task의 "회의록에서 보기"가 근거를 찾을 때
(`app/task_api.py`의 `_meeting_evidence()`)도 같은 `get()`을 써서, **회의를 지우면 그 회의에서
만든 Task의 근거 링크까지 조용히 사라졌다** — 애초에 "Recording·Transcript·Action Item은 그대로
둔다"고 설계한 회의 삭제 기능의 취지와 어긋났다.

**수정**: `Task`의 `include_deleted`(`app/repositories/tasks.py`)와 같은 패턴으로
`SQLiteMeetingRepository.get()`에 `include_deleted` 매개변수를 추가했다. 근거를 "찾기만" 하는
세 곳(`_meeting_evidence()`, `GET /api/v1/meetings/{id}`, `GET /api/v1/meetings/{id}/analysis`)은
`include_deleted=True`로 조회해 삭제된 회의도 계속 찾는다 — 목록(`GET /api/v1/meetings`)에는
여전히 안 보이고, 녹음 업로드·Transcript 저장처럼 "능동적으로 회의를 계속 쓰는" 나머지 경로는
그대로 삭제된 회의를 막는다. 결과적으로 회의를 삭제해도 "회의록에서 보기"로 들어가면 그 회의
상세·분석 결과를 계속 볼 수 있다(목록 브라우징에서만 사라진다).

**검증**: 실제 DB에서 회의가 삭제된 채로 근거가 비어 있던 그 Task를 재기동한 서버로 다시 조회해
`meeting_evidence`가 정상적으로 채워지는 것을 확인했다. 새 테스트 4개 추가(Repository·API 양쪽,
"삭제 후에도 상세·분석·근거는 살아있고 목록에서만 빠진다"는 계약을 검증), 백엔드 전체 368개
테스트 통과.

### 대화 이력이 무관한 새 질문에 이전 내용을 섞어 답하는 문제(2026-08-17)

회의를 분석한 직후 전혀 다른 주제("시즌 패스 보상 지급 로직 변경 관련 메일 내용 요약해줘")를 물었는데,
방금 분석한 회의 요약을 그 메일 내용인 것처럼 그대로 재사용해 답했다 — 대화 이력(바로 앞 기능)을
"짧은 후속 문장이 무엇을 가리키는지" 판단하는 용도로만 쓰라고 지시했을 뿐, "주제가 다른 새 질문에
이전 turn 내용을 사실처럼 가져다 쓰면 안 된다"는 제약은 없었다.

**수정**: System Prompt의 "대화 이력 사용 원칙"에 이 구분을 명시했다 — 새 질문이 이전 turn과
주제 자체가 다르면 이전 turn의 요약·내용을 답에 절대 가져다 쓰지 말고, 오직 [Context](회의·제안
목록)에 있는 사실만 근거로 삼으라고 했다. 부수적으로, Drawer가 Drawer를 연 시점에 회의 목록을
한 번만 가져와 계속 재사용하던 것도 질문마다 "회의 관리"에서 새로 가져오도록 바꿨다 — 캐시된
목록을 계속 쓰면 그새 새로 생기거나 삭제된 회의를 놓친다.

**검증**: 실제 Provider로 "방금 회의 분석 → 무관한 새 질문" 시나리오를 재현 — 이전엔 무관한
회의 요약을 그대로 답했지만, 이제는 "현재 정보가 없습니다. 메일함에서 직접 확인해 주세요"로
정직하게 답한다. 같은 조건에서 정당한 후속 질문("1"로 회의 후보 선택)은 여전히 정확히
특정되는 것도 함께 확인해, 과교정(overcorrection)이 없음을 검증했다. 새 테스트 1개 추가, 백엔드
전체 369개 테스트 통과.

### Context에 회의 분석 여부가 없어 "아직 분석 안 한 회의"를 근거 없이 단정하는 문제(2026-08-17)

"오늘 한 회의 분석해줘"라고 물었더니 "오늘 회의 중 아직 분석하지 않은 회의 8월 17일 17:20을
분석하겠습니다"처럼 특정 회의를 콕 집어 "아직 분석 안 했다"고 단정했다 — 사실은 바로 앞
대화에서 이미 분석한 회의였다. 원인은 Context의 회의 목록이 애초에 `{meeting_id, title}`
뿐이라 분석 여부라는 정보 자체가 없었다는 것 — "회의목록을 다시 가져오지 않고 이전 대화
내용을 재분석한다"는 사용자 보고와 달리 실제로는 회의 목록은 매 질문 새로 가져오고 있었지만
(바로 앞 수정), 그 목록 자체에 분석 여부가 빠져 있어 LLM이 추측으로 단정한 것이었다.

**수정**: `GET /api/v1/meetings`(목록)·`GET /api/v1/meetings/{id}`(상세) 응답에
`has_analysis`(=`summary` 저장 여부) 필드를 추가하고(`app/meeting_api.py`의 `_meeting_response()`
헬퍼), Drawer의 Context 빌더가 이를 그대로 실어 보내도록 했다(`AssistantDrawer.tsx`,
`lib/workmate-types.ts`, `lib/workmate-format.ts`, 스키마 문서). Router의 `_format_context()`가
회의 줄마다 `[분석 완료]`/`[분석 대기]`/`[분석 여부 불명]`을 렌더링하고, `analyze_meeting`/
`get_meeting_analysis` 카탈로그 설명에 "이미 분석 완료인 회의는, 사용자가 '다시'·'재분석'·'또'처럼
명시하지 않는 한 `get_meeting_analysis`를 우선 써라 — '분석해줘'라고만 말한 것도 재실행 요청이
아니다"를 명시했다. `[분석 여부 불명]`이면 아는 척 단정하지 말라는 문구도 유지했다.

**검증**: 실제 DB의 회의(분석 완료 2건 + 미분석 1건, 모두 오늘 생성)를 그대로 Context에 실어
`route()`를 5회씩 반복 호출 — 수정 전에는 "분석해줘"만으로도 이미 분석된 회의에 `analyze_meeting`을
다시 호출하거나(3회 중 2회) 후보 3개를 전부 나열해 되묻기만 했다. 수정 후에는 (a) 분석 완료
회의 하나만 있을 때 3/3 `get_meeting_analysis`로, (b) 미분석 회의 하나만 있을 때 3/3
`analyze_meeting`으로, (c) 분석 완료 2건 + 미분석 1건이 섞여 있을 때 5/5 모두 그 미분석 회의
하나를 정확히 짚어 `analyze_meeting`을 제안했다(근거 없는 "아직 분석 안 했다" 단정 없이). 새
회귀 테스트 3개 추가(`test_meeting_analysis_status_is_shown_in_the_prompt`,
`test_prompt_prefers_get_meeting_analysis_over_reanalyzing`,
`test_has_analysis_reflects_whether_a_summary_is_saved`) — 백엔드 전체 372개 테스트 통과. 프론트
`tsc`·`eslint`·`npm test`(68개) 모두 통과. 두 서버 재기동 후 배포된 번들에 `has_analysis` 반영
확인.

### "Action Item을 할 일로 추가할까요?" 확인 배너에 번호로 답하면 회의 근거 링크가 끊기는 문제(2026-08-17)

회의 분석 뒤 "이 Action Item을 할 일로 추가할까요?" 확인 배너가 뜬 상태에서, 배너의 확인/취소
버튼 대신 "1번만 할일에 추가해"처럼 자유 문장으로 답하면 할 일은 만들어지지만
`meeting_evidence`가 없어 "회의록에서 보기" 버튼이 안 나왔다.

**원인**: 배너 버튼을 누르면 `confirmed_skill_id`로 원래 `review_action_items` 호출을 그대로
재전송해 정상 동작한다. 하지만 자유 문장으로 답하면 `route()`가 새 질문으로 다시 판단하는데,
Context에 그 Action Item들의 실제 `action_item_id`가 전혀 없었다 — LLM은 "1번"이 무엇을
가리키는지 ID를 알 방법이 없어, `review_action_items`(action_item_id 필요) 대신
`manage_tasks(action=create)`(제목 문자열만 있으면 됨)로 새 할 일을 수동 생성해버렸다. 그 결과
`source_type="manual"`인 Task가 만들어져 회의 근거를 되짚을 수 없었다.

**수정**: `AssistantAskInput.context`에 `pending_action_items`(순서가 있는
`{meeting_id, action_item_id}` 배열) 필드를 추가했다. Drawer가 직전 assistant 메시지에 아직
응답 안 받은 `review_action_items` 확인 배너가 있으면, 그 `arguments.decisions`의
action_item_id를 순서 그대로 이 필드에 실어 다음 메시지와 함께 보낸다. Router의
`_format_context()`가 "방금 제안한 Action Item 후보(번호 순서)"로 렌더링하고,
`review_action_items` 카탈로그 항목에 "이 목록이 있으면 서수 표현(1번·두 번째)은 반드시 그
순서의 action_item_id를 그대로 써라, 모르면서 `manage_tasks(action=create)`로 대신 새 할 일을
만들지 마라"를 명시했다.

**검증**: 실제 화면에서 재현된 대화(회의 분석 결과 + "이 Action Item을 할 일로 추가할까요?" +
"1번만 할일에 추가해")를 그대로 실제 LLM Provider에 5회 호출 — 5/5 모두 `review_action_items`를
정확한 `action_item_id`(목록의 1번째) 하나만으로 정확히 호출했다(이전엔 ID가 없어 이런 케이스
자체를 재현하면 `manage_tasks`로 빠졌다). 새 회귀 테스트 1개 추가
(`test_pending_action_items_are_shown_in_the_prompt_in_order`) — 백엔드 전체 373개 테스트 통과.
프론트 `tsc`·`eslint`·`npm test`(68개) 모두 통과.

이미 이 버그로 잘못 저장돼 있던 실제 데이터 1건("수정된 트랜잭션 로직을 PR로 반영")도 사용자
승인을 받아 DB에서 원래 Action Item에 재연결했다(`source_type`/`source_id` 복구,
`approve_action()`으로 승인 상태 동기화) — 다만 복구 도중 사용자가 그 할 일을 화면에서 직접
삭제해(서버 로그로 확인) 목록에는 더 이상 보이지 않는다. 두 서버 재기동 후 배포된 번들에
`pending_action_items` 반영 확인.

### "오늘 한 회의 분석해줘"에 실제 분석 없이 이전 대화 내용을 그대로 베껴 답하는 문제(2026-08-17)

이전 turn에서 이미 (다른) 회의를 분석해 결과를 보여준 상태에서 "오늘 한 회의 분석해줘"라고
다시 요청했더니, 확인 배너도 없이 곧바로 이전 turn의 분석 결과 텍스트를 그대로 다시 보여줬다
— 실제로는 오늘 아직 분석 안 한 다른 회의가 있는데도 그 회의를 분석하지 않았다.

**원인**: 바로 앞서 고친 "대화 이력이 무관한 새 질문에 이전 내용을 섞어 답하는 문제" 수정은
**주제가 다른** 새 질문만 막았다("회의 분석 직후 메일 요약을 물으면 섞지 마라"). 그런데 이번
요청은 주제가 같다(둘 다 "회의 분석") — Router가 이걸 "이미 답한 것을 다시 보여달라는
후속 질문"으로 오해해, 실제로 `call_skill`을 호출하지 않고 이전 turn 텍스트를 그대로
`action="reply"`로 재사용했다. `analyze_meeting`이 "항상 실행 전 확인 필요"라는 규칙 자체는
멀쩡했지만, Skill을 아예 호출하지 않고 답을 지어냈으니 그 확인 절차 자체를 건너뛴 셈이었다.

**수정**: System Prompt의 "대화 이력 사용 원칙"에 "주제가 같아도 마찬가지다"를 추가했다 —
회의 분석처럼 Skill이 실제로 수행해야 할 동작을 요청하면, 이전 turn에 비슷하거나 같은 회의의
분석 결과가 이미 있어도 그걸 재사용해 `reply`로 답하지 말고 반드시 `call_skill`로 실제
Skill을 호출하라고 명시했다 — 이미 분석된 회의면 `analyze_meeting`이 아니라
`get_meeting_analysis`를 실제로 호출해 저장된 결과를 가져오는 것도 "기억으로 재구성해 답하는
것"과는 다르다고 구분했다.

**검증**: 스크린샷 그대로("오늘 한 회의 분석해줘" → 이전 turn에 다른 회의의 분석 결과가 있는
상태) 재현해 실제 LLM Provider에 5회 호출 — 수정 전엔 이 재현 자체가 곧바로 이전 답을
베끼는 걸로 이어졌지만, 수정 후엔 5/5 모두 오늘의 미분석 회의를 정확히 짚어 `analyze_meeting`을
`call_skill`로 호출했다(이제 확인 배너도 정상적으로 뜬다). 이미 분석된 회의를 "다시
분석해줘"라고 명시한 경우도 5/5 모두 실제로 `analyze_meeting`을 호출해(재분석 명시 시의
기존 예외 규칙과 충돌 없음) 과교정이 없음을 확인했다. 새 회귀 테스트 1개 추가
(`test_prompt_forbids_reusing_previous_analysis_for_a_same_topic_action_request`) — 백엔드
전체 374개 테스트 통과. 백엔드만 바뀐 변경이라 백엔드 서버만 재기동.

### "Action Item 확인 배너"에 번호가 아니라 내용으로 답하면 여전히 같은 함정에 빠지는 문제(2026-08-17)

바로 앞의 `pending_action_items` 수정은 "1번만"·"두 번째만" 같은 **번호** 지칭만 다뤘다. 그런데
실사용에서 같은 배너에 "가이드 공유하는 거만 추가해줘"처럼 **내용**으로 지칭하면 똑같이
`manage_tasks(action=create)`로 잘못 빠져 회의 근거 링크가 끊긴 할 일이 또 생겼다 — 생성된 할 일
제목이 원래 Action Item 제목과 완전히 일치해, LLM이 그 항목을 알아보긴 했지만 ID로 옮기지 못하고
제목 문자열 그대로 새 할 일을 만든 것으로 확인됐다.

**수정**: `review_action_items` 카탈로그 지시를 "번호로 말하든 **내용으로** 말하든 — 바로 앞
assistant 응답의 번호 목록에서 어떤 항목을 가리키는지 먼저 찾아낸 다음 그 번호에 대응하는
`pending_action_items`의 `action_item_id`를 꺼내 써라"로 넓혔다. `pending_action_items` 자체는
ID만 담고 제목이 없으므로, 이 매핑은 history에 남아 있는 직전 assistant 응답의 번호가 매긴
제목 목록과 대조하는 2단계 추론이 필요하다는 점을 명시했다.

**검증**: 실사용에서 재현된 것과 같은 상황(회의 분석 결과 + 확인 배너 + "가이드 공유하는 거만
추가해줘"/"가이드 공유하는 것만 할일에 추가해")을 그대로 실제 LLM Provider에 각 3회씩 호출 —
6/6 모두 정확한 action_item_id(가이드 공유 항목)로 `review_action_items`를 호출했다(수정 전엔
이 시나리오 자체가 `manage_tasks`로 빠지는 걸 실사용에서 재현시켰다). 새 회귀 테스트 1개 추가
(`test_review_action_items_catalog_covers_content_based_selection_too`) — 백엔드 전체 375개
테스트 통과. 백엔드 재기동 후 배포 확인.

이 버그로 이미 잘못 저장된 실제 데이터 1건("재화·경매장 처리 가이드 공유")도 앞서와 같은
방식으로 DB에서 원래 Action Item(A2)에 재연결했다 — 이번엔 삭제되지 않아 목록에 "회의록에서
보기" 버튼이 정상적으로 나타난다.

### "회의 관리" 목록의 분석 상태 배지가 이미 분석된 회의를 "분석 대기"로 잘못 표시하는 문제(2026-08-17)

이미 분석까지 끝난 회의인데 "회의 관리" 목록에서 "분석 대기"로 잘못 표시됐다.

**원인**: `Archive.tsx`의 이 배지는 `GET /api/v1/meetings`(목록) 응답을 안 쓰고, 회의를 펼쳐
상세 분석을 한 번 조회해야만(`MeetingDetail`의 `onAnalyzed` 콜백) 채워지는 클라이언트 전용
`analyzedIds` Set을 따로 들고 있었다(Archive.tsx 자체의 화면 깜빡임 버그를 고치며 이 상태가
생겼다, 17번 갭 문서 #10). 그래서 페이지를 새로 열고 아직 한 번도 펼쳐보지 않은 회의는 실제
분석 여부와 상관없이 무조건 "분석 대기"로 보였다.

**수정**: 마침 바로 앞서 챗봇 Router가 회의 분석 여부를 알 수 있게 `GET /api/v1/meetings`에
추가해 둔 `has_analysis` 필드(이 문서의 "Context에 회의 분석 여부가 없어..." 절 참고)를 이
배지에도 그대로 재사용했다 — `analyzedIds` Set과 `onAnalyzed` 콜백 전체를 걷어내고
`meeting.has_analysis`를 직접 쓴다. 목록을 불러오는 즉시(회의를 펼쳐보지 않아도) 정확한
상태가 보인다.

**검증**: 실제 DB에서 이미 분석된 것으로 확인된 회의(`summary IS NOT NULL`)의 `has_analysis`가
`True`로 응답에 실리는 것을 리포지토리로 직접 확인했다. 프론트 `tsc`·`eslint`(신규 경고 0개,
더 이상 필요 없어진 `eslint-disable` 주석도 함께 제거)·`npm test`(68개) 모두 통과. 프론트
재빌드·재기동 후 배포된 번들 확인.

### 확인 배너가 어떤 회의인지 말하지 않고 뭉뚱그리는 문제(2026-08-17)

"오늘 한 회의 분석해줘"의 확인 배너가 "오늘 한 회의 중 분석 대기인 회의를 분석하겠습니다"처럼
**어떤 회의인지 전혀 말하지 않고** 확인만 물었다 — 사용자가 무엇을 승인하는지 알 수 없었다.

**원인**: `route()`가 `call_skill`을 고를 때 함께 채우는 `reply`가 그대로 확인 배너 문구가
되는데, System Prompt 어디에도 이 `reply`가 Context에서 실제로 고른 대상(회의 제목·날짜·시각
등)을 구체적으로 적어야 한다는 지시가 없었다 — "중요 1"은 `action="reply"`(정보 질문에 바로
답하는 경우)만 다뤘고 `call_skill`의 `reply`는 다루지 않았다.

**수정**: "중요 1" 뒤에 "call_skill을 고를 때도 reply는 채워야 한다 — 확인 배너에 그대로 뜨니
Context에서 고른 대상을 구체적으로 적어라"를 일반 규칙으로 추가하고, `analyze_meeting` 카탈로그
항목에도 같은 지시와 구체적인 예시("'8월 17일 17:31' 회의를 분석하겠습니다")를 명시했다.

**검증**: 스크린샷 상황(오늘 회의 중 미분석 회의가 하나뿐)을 그대로 재현해 실제 LLM Provider에
5회 호출 — 수정 전엔 "분석 대기인 회의를 분석하겠습니다"처럼 뭉뚱그렸지만, 수정 후엔 5/5 모두
"'8월 17일 17:31' 회의를 분석하겠습니다"처럼 대상을 구체적으로 적었다. 새 회귀 테스트 1개 추가
(`test_prompt_requires_confirmation_replies_to_name_the_specific_target`) — 백엔드 전체 376개
테스트 통과. 백엔드만 바뀐 변경이라 백엔드 서버만 재기동.

### 이메일 내용을 물으면 제목을 되풀이할 뿐 실제로 요약하지 못하는 문제(2026-08-17)

"~ 관련 메일 내용을 요약해서 알려줘"라고 물으면 "'X' 메일의 내용은 X와 관련된 내용입니다"처럼
질문을 그대로 되풀이할 뿐 실제 요약이 나오지 않았다.

**원인**: 메일이 처음 동기화될 때(`app/dev_gmail_sync_api.py`) 원문 본문은 "할 일 제목" 하나를
뽑는 LLM 호출에만 잠깐 쓰이고 그 자리에서 버려진다 — 제안(Proposal)에는 그 짧은 제목만 남고
원문은 시스템 어디에도 저장되지 않는다. 챗봇 Context(`AssistantAskContextProposal`)도 그
`title` 하나만 실어 보낸다. 그래서 "요약해줘"라고 물어도 LLM이 가진 재료가 제목 한 줄뿐이라,
"지어내지 마라"는 규칙을 지키는 유일한 방법이 제목을 그대로 되풀이하는 것뿐이었다 — 정직했지만
쓸모없는 답이었다.

**해결 방향 결정**: 캐시된 title/snippet을 조금 더 실어 보내는 대신(1안), 사용자 요청대로
"실시간으로 다시 메일 내용을 가져오는" 방식(재조회형)을 선택했다 — 매 질문마다 Gmail API를 다시
호출해 실제 본문을 가져오고, 그 결과는 저장하지 않는다("제안은 DB에 저장하지 않는다" 기존
원칙과 일관됨).

**구현**: 새 내부 전용 Skill `read_email`을 추가했다(18번 문서 핵심 설계 결정 #1과 같은 패턴 —
공개 Agent Card `_SKILLS`에는 안 넣고 `_INTERNAL_ONLY_SKILLS`에만 추가, `assistant_ask`가 대신
호출하는 6번째 내부 전용 Skill이 됨).
- `app/workflows/assistant_skills.py::read_email_workflow` — `message_id`를 받아
  `GmailAdapter.get_message_with_body()`(이미 `dev_gmail_sync_api.py`가 동기화 시점 추출에
  쓰던 것과 같은 메서드)로 매번 실제 Gmail API를 다시 호출한다. Token이 없거나 인증에
  실패하면 예외를 던지지 않고 `available: false` + 이유를 담은 정상 결과를 돌려줘
  `phrase_answer()`가 자연스럽게 "정보를 못 가져왔습니다"로 답하게 한다. 읽기 전용이라
  `_requires_confirmation()`에 해당 없음 — 확인 없이 바로 실행된다. 본문은 4,000자로
  자른다. `WORKMATE_DEV_GMAIL_SYNC_ENABLED` 뒤에 두지 않았다 — 그 플래그는 "제안함에 새
  메일을 발행하는 개발용 동기화"를 막는 스위치일 뿐, 이미 Context에 나온 메일 하나를 다시
  읽는 것과는 무관하다.
- `app/a2a/runtime.py` — `_INTERNAL_ONLY_SKILLS`에 등록, `registry.register("read_email", ...)`.
- `app/workflows/assistant_router.py` — `_ROUTABLE_SKILL_IDS`에 추가, 카탈로그에 새 항목
  추가("Context의 제안 목록에는 제목만 있고 본문은 없다 — 제목을 그대로 되풀이해 답을 지어내지
  마라, 이 Skill이 실제 본문을 다시 가져온다"), `manage_tasks` 항목의 "이메일 본문 검색 기능
  없음" 문구를 "본문이 필요하면 read_email을 대신 써라"로 정정.

**검증**: 화면에서 재현된 것과 같은 질문("시즌 패스 보상 지급 로직 변경 관련 메일 내용
요약해서 알려줘")과 제안 Context를 그대로 실제 LLM Provider에 5회 호출 — 5/5 모두
`read_email`을 정확한 `message_id`로 호출했다(확인 배너 없이 바로 실행 — 읽기 전용이라
적절하다). `read_email_workflow` 자체도 실제 Gmail 계정(`google-oauth-test/token.json`)으로
End-to-End 검증 — 실제 메일 제목·1,173자 본문을 정상적으로 가져왔다. 신규 단위 테스트 3개
(`test_read_email_returns_no_token_message_when_credentials_are_missing`,
`test_read_email_fetches_the_live_body_when_credentials_are_present`,
`test_read_email_requires_a_message_id`) + Router 카탈로그 테스트 1개
(`test_read_email_catalog_entry_is_present_and_routable`) 추가, 기존 Skill 개수를 검증하던
계약 테스트 2개(`test_internal_chat.py`) 갱신 — 백엔드 전체 380개 테스트 통과. 프론트는
변경 없음(Context 구조가 이미 `message_id`를 실어 보내고 있었다) — `npm test` 68개 통과로
회귀 없음만 재확인. 백엔드 재기동 후 배포 확인.

**후속 회귀(같은 날 발견)**: 재기동한 실 서버로 실제 대화를 재현했더니 "Gmail 인증이 되어
있지 않아 메일 내용을 확인할 수 없습니다"로 잘못 답했다 — Token 파일은 실제로 있는데도였다.
원인은 `_GMAIL_OAUTH_TEST_DIR` 기본 경로 계산의 상대 깊이 버그: `dev_gmail_sync_api.py`(위치
`app/`)는 `Path(__file__).resolve().parents[2]`로 모노레포 루트를 정확히 찾지만,
`assistant_skills.py`는 그보다 한 단계 더 깊은 `app/workflows/`에 있는데도 같은
`parents[2]`를 그대로 써서 `workmate-agent/google-oauth-test`(존재하지 않음)를 가리켰다.
`parents[3]`으로 수정하고, 두 모듈의 기본 경로가 실제로 같은 디렉터리를 가리키는지 비교하는
회귀 테스트(`test_read_email_default_credential_dir_matches_dev_gmail_sync_api`)를 추가했다 —
백엔드 전체 381개 테스트 통과. 실제 Gmail 계정으로 End-to-End 재확인, 백엔드 재기동 후 배포
확인.

**후속 확장(같은 날, 사용자 요청): 제안함에 없는 메일도 제목으로 검색해 읽기, 30일로 제한**

위 `read_email`은 Context의 제안(Proposal) 목록에 `message_id`가 있을 때만 동작했다 — 이미
승인·무시돼 제안함에서 사라졌거나, 애초에 "할 일 후보"로 판단되지 않아 제안으로 뜬 적이 없는
메일은 챗봇이 `message_id` 자체를 알 방법이 없어 "제안함에서 확인해 주세요"로만 답했다(실사용
중 재현). 사용자 요청으로 메일함 전체를 제목·키워드로 검색해 읽어오는 경로를 추가했다 — 단
**검색 범위는 항상 최근 30일로 제한**하고, 이 제한을 결과와 답변에 항상 명시하기로 했다(응답
지연·오래된 메일 오검색 위험을 줄이기 위해서다).

**구현**: `read_email_workflow`(`app/workflows/assistant_skills.py`)가 `message_id` 또는
`query` 중 하나를 받도록 바뀌었다 — `message_id`가 없으면
`GmailAdapter.list_messages(query=f"{query} newer_than:30d", max_results=5)`로 검색해 첫
후보를 읽는다. 검색으로 찾은 경우엔 결과의 `search_window_note`("최근 30일 내 메일만
검색했습니다")를 항상 채우고, `text`/`markdown`에도 그 문구를 직접 덧붙여 `phrase_answer()`가
이 사실을 빠뜨리지 않게 했다(LLM 재량에만 맡기지 않음 — 못 찾았을 때도 이 문구가 붙는다). Router
카탈로그(`assistant_router.py`)에 "Context에 없으면 query로 메일함 전체를 검색하되, 30일 제한을
답에 반드시 언급하라"를 명시했다.

**검증**: 실사용에서 재현된 것과 같은 상황(제안함에 이 메일이 없는 상태에서 "시즌 패스... 메일
내용 요약해줘")을 실제 LLM Provider에 5회 호출 — 5/5 모두 `message_id` 없이 `query`만으로
`read_email`을 호출했다. `read_email_workflow`의 query 검색 경로도 실제 Gmail 계정으로
End-to-End 검증 — 검색어만으로 정확한 메일(제목·본문)을 찾아 가져왔고 `search_window_note`도
정상적으로 채워졌다. 신규 단위 테스트 2개(정상 검색·검색 결과 없음) + Router 카탈로그 테스트
1개 추가 — 백엔드 전체 384개 테스트 통과. 백엔드 재기동 후 배포 확인.

**후속 회귀(같은 날 실사용 중 발견): 검색 실패 시 원인을 알 수 없는 문제**

query 검색 배포 직후 재현했더니 "메일 내용을 가져오지 못해... 사유: Google provider 요청
실패"로만 답해, Gmail이 왜 거절했는지(400 등) 알 방법이 없었다.

**원인 1(진단 불가)**: `app/providers/google.py`의 공용 `_request()`가 4xx 오류를 전부
"Google provider request failed"라는 뭉뚱그린 문구 하나로만 감싸 Google이 실제로 돌려준 오류
메시지(예: 잘못된 검색 연산자)를 버리고 있었다.

**원인 2(추정 근본 원인)**: Router가 사용자 문장에서 뽑은 검색어를 그대로 Gmail `q` 파라미터에
붙이는데, 우연히 `:`(예: "제목:")나 `"`(짝이 안 맞는 따옴표)가 섞이면 Gmail이 이를
`subject:`류 검색 연산자·구문 검색으로 잘못 해석해 400을 낼 수 있다.

**수정**:
- `_request()`가 4xx 응답의 Google 원문 오류 메시지(`error.message`)를 그대로 붙이고, 없으면
  최소한 상태 코드라도 남기게 했다(`google provider request failed: <이유>` 또는
  `... (HTTP 400)`) — 앞으로 같은 문제가 재발해도 원인이 바로 보인다.
- Router가 만든 검색어에서 `:`·`"`를 공백으로 치환하는 `_sanitize_gmail_query_text()`를 추가해
  애초에 Gmail이 연산자로 오해할 문자를 보내지 않게 했다.

**검증**: 새 단위 테스트 4개 추가 — `_request()`의 오류 메시지 보강 2개
(`test_generic_4xx_error_includes_googles_own_message`,
`test_generic_4xx_error_falls_back_to_status_code_when_google_gives_no_message`,
`test_google_adapters.py`), 검색어 정제 1개(`test_read_email_sanitizes_colons_and_quotes_out_of_the_search_query`).
백엔드 전체 387개 테스트 통과. 이 특정 실패의 정확한 재현(Google이 정확히 어떤 400 메시지를
줬는지)은 이 개발 환경의 Gmail API 응답 지연이 매우 불안정해(같은 호출이 수 초~수 분까지
들쭉날쭉) 확정하지 못했다 — 사용자가 다시 겪으면 이제는 오류 메시지 자체에 원인이 드러나므로
바로 알 수 있다. 백엔드 재기동 후 배포 확인.

**진짜 근본 원인(오류 메시지 보강 직후 재현으로 확정)**: 보강된 오류 메시지에 Google이 실제로
돌려준 이유가 "메일 ID 값이 유효하지 않았습니다"(Invalid id value)로 나오면서 원인이
드러났다 — Context.proposals의 `message_id` 필드는 사실 순수 Gmail Message ID가 아니라 email
제안의 **`source_id`**였다. 한 메일에서 Action Item을 여러 개 뽑으면 각각 독립적으로
승인·무시할 수 있게 `_publish_action_items_for_message()`(`app/dev_gmail_sync_api.py`)가
`f"{gmail_message_id}:{index}"` 형태로 만든다(17번 갭 문서 #11) — `review_proposal`은 이
전체 값이 정확히 필요하지만, `read_email`이 그대로 Gmail `messages.get`에 넘기면 콜론 뒤
인덱스 때문에 유효하지 않은 ID가 된다.

**수정**: Context.proposals의 `message_id` 형식 자체는 바꾸지 않았다(바꾸면 `review_proposal`이
깨진다) — 대신 `read_email_workflow`가 Gmail을 호출하기 직전에 `:` 앞부분만 잘라 순수 Message
ID로 정규화한다. Router 프롬프트는 그대로 "Context의 message_id를 그대로 쓴다"고 안내해도 되고,
정규화는 Skill 내부에서만 조용히 처리한다.

**검증**: 새 회귀 테스트 1개 추가
(`test_read_email_strips_the_action_item_index_suffix_from_a_proposal_source_id`) — 실제
제안 형식(`1a00ec3a449ec13e:0`)을 그대로 넣고 Gmail Adapter가 접미사 없는 순수 ID로 호출됐는지
확인한다. 백엔드 전체 388개 테스트 통과. 실제 Gmail 계정으로 같은 형식(`:0` 접미사 포함)의
ID를 넣어 End-to-End 재확인. 백엔드 재기동 후 배포 확인.

**세 번째 회귀(같은 날 실사용 중 발견): 실제로 존재하는 메일도 검색이 못 찾는 문제**

message_id 정규화 배포 직후 다른 메일("v2.4.0 업데이트 정기 배포 및 DB 마이그레이션")로
재현했더니 "관련된 메일을 찾지 못했습니다. 최근 30일 내 메일만 검색했습니다"로 답했다 — 그
메일은 실제로 2일 전에 받은 메일이라 30일 제한과 무관했다.

**원인**: Router가 `query`에 사용자 질문 **원문 전체**를 그대로 채우고 있었다("v2.4.0
업데이트 정기 배포 및 DB 마이그레이션 작업은 언제 예정돼 있는지 메일에서 찾아줘"). Gmail의
기본 `q` 검색은 공백으로 구분된 모든 단어를 AND로 요구한다 — "찾아줘"·"언제"·"있는지"처럼
메일 본문에 없는 단어까지 섞이면 실제로 존재하는 메일도 못 찾는다. 실제 Gmail API로 직접
비교해 확정했다: 원문 전체 검색은 0건, "v2.4.0 정기 배포 DB 마이그레이션"으로 줄인 검색은
정확히 그 메일 1건을 찾았다.

**수정**: `read_email` 카탈로그에 "query는 Gmail 검색창에 넣을 핵심 키워드 2~5개만 골라야
한다 — 질문 원문을 그대로 복사해 넣지 마라"를 구체적인 예시와 함께 명시했다(버전 번호·
프로젝트명·핵심 명사만 남기라는 지침 + 실제 이번 사례를 예시로 사용).

**검증**: 같은 질문을 실제 LLM Provider에 5회 호출 — 수정 전엔 원문 전체를 그대로 복사했지만,
수정 후엔 5/5 모두 "v2.4.0 정기 배포 마이그레이션"류의 짧은 키워드만 골랐다. 이 키워드로
`read_email_workflow`를 실제 Gmail 계정에 대해 End-to-End 재실행해 정확히 그 메일을 찾아
본문을 가져오는 것까지 확인했다. 새 회귀 테스트 1개 추가
(`test_read_email_catalog_requires_keywords_not_the_full_sentence`) — 백엔드 전체 389개
테스트 통과. 백엔드 재기동 후 배포 확인.

### "주간보고 작성해줘"(기간 언급 없음)의 기본 기간이 지난 주가 아니라 다음 주로 나오는 문제(2026-08-17)

아무 기간도 말하지 않고 "주간보고 작성해줘"라고만 했더니 기간이 "2026년 8월 17일~8월 24일"
(오늘부터 앞으로 7일)로 나왔다. 사용자 요청: "주간보고 내용을 기준일자의 일주일 이전부터의
내용을 가져오고 기준일자가 불분명할 경우 오늘 기준으로 할 것."

**원인**: `week_of`가 비어 있으면 Router가 이를 그대로 비워 보냈고, `build_weekly_report_workflow`
자체의 기본값이 "오늘"(순방향 7일, "이번 주")이었다 — "주간보고"는 관행적으로 지난 한 주를
되짚는 보고인데 기본 동작이 반대 방향이었다.

**설계 결정**: `weekly_report` Skill 자체의 기본값(`build_weekly_report_workflow`)은 그대로
뒀다 — "주간 업무보고" 구조화 화면(`Report.tsx`)이 이 기본값을 "이번 주(수신일이 속한 주)"로
명시적으로 의도하고 있어서(자체 주석·03 §5), 여기를 바꾸면 그 화면의 의도된 동작이 깨진다.
대신 챗봇 자연어 Router에서만 `week_of`를 **절대 비워두지 않고 항상 직접 계산**하도록
바꿨다 — 기간 언급이 없으면(기본값) week_of=오늘-7일을 명시적으로 채운다.

**후속 버그(구현 중 자체 발견)**: 처음 작성한 지시문은 "기준일자를 정한 뒤 거기서 7일을
뺀다"는 2단계 규칙이었는데, "지난 주"라는 표현 자체가 이미 "오늘-7일"을 가리키다 보니 LLM이
그 위에 규칙의 "-7일"을 한 번 더 적용해(이중 차감) "지난 주"가 가끔 오늘-14일("지지난 주"의
값)로 나왔다. 지시문을 "정확히 하나의 규칙만 적용, 겹쳐 적용 금지"로 다시 써서 해결했다 —
"이번 주"→오늘, "지난 주"/기본값→오늘-7일, "지지난 주"·"2주 전"→오늘-14일을 서로 독립적인
경우로 분리했다.

**부수 발견(같은 검증 중): `week_of`가 가끔 전체 ISO datetime 문자열로 나옴** — Router가
`week_of`에 순수 `YYYY-MM-DD`가 아니라 `"2026-08-10T00:00:00+09:00"`처럼 시각까지 붙여
보낼 때가 있었는데, `app/domain/weekly.py`의 `_week_date()`가 `date.fromisoformat()`만 써서
바로 실패하며 "week_of must be an ISO date" 오류로 주간보고 자체가 실패했다. `_week_date()`가
실패하면 `datetime.fromisoformat()`으로 한 번 더 시도해 날짜만 뽑아 쓰도록 방어적으로
고쳤다(Router 프롬프트 discipline에만 의존하지 않는 시스템 전역 하드닝).

**검증**: "주간보고 작성해줘"(언급 없음)를 실제 LLM Provider에 5회 호출 — 수정 전엔 오늘+7일,
수정 후엔 5/5 모두 오늘-7일. "이번 주"·"지난 주"·"지지난 주" 세 표현을 각 3회씩 재검증해
이중 차감 버그가 사라지고 각각 오늘·오늘-7일·오늘-14일로 정확히 분리되는 것을 확인했다. 새
회귀 테스트 2개 추가(`test_weekly_report_catalog_defaults_to_the_past_week_not_the_upcoming_week`,
`test_full_iso_datetime_string_is_accepted_and_reduced_to_its_date`) — 백엔드 전체 391개
테스트 통과. 백엔드 재기동 후 배포 확인.

### "주간 업무보고" 화면도 기본 기간을 지난 1주로(사용자 요청, 2026-08-17)

챗봇 자연어 Router의 기본값을 고친 것과 같은 이유로, 사용자가 구조화 "주간 업무보고"
화면(`Report.tsx`)도 날짜를 따로 고르지 않았을 때 기본으로 지난 1주(오늘-7일)를 보여달라고
요청했다.

**구현**: `Report.tsx`가 기존엔 `weekOf`를 `undefined`로 둬 서버 기본값("이번 주")에
의존했다 — 이제 마운트 시 `defaultWeeklyReportWeekOf()`(오늘-7일)를 명시적으로 계산해 채운다.
서버(`weekly_report` Skill) 자체의 기본값은 바꾸지 않았다 — 이 화면만 명시적으로 다른 값을
보내 화면 기본값만 바꿨다. 날짜 이동 버튼 중 "이번 주로"(서버 기본값으로 리셋)는 "최근
1주로"(화면의 새 기본값으로 리셋)로 바꿨다.

이 작업을 하며 `shiftIsoDate`(기존 "이전 주"·"다음 주" 이동 버튼이 쓰던 함수)와
`todayIsoDate`/`defaultWeeklyReportWeekOf`를 컴포넌트 밖 `lib/workmate-format.ts`로 옮기고
`now: Date` 주입 인자를 받게 해 순수 함수로 테스트 가능하게 했다(이 프로젝트의 기존
관례 — `isCalendarProposalToday`와 같은 패턴).

**부수 발견(테스트 작성 중 발견한 기존 버그)**: `shiftIsoDate`가 옮긴 날짜를
`.toISOString().slice(0, 10)`(UTC 변환)으로 문자열화하고 있었는데, **UTC보다 시간대가
앞선(한국 등) 사용자는 로컬 자정이 이미 전날 UTC 오후라 결과 날짜가 하루 밀렸다** — 예를
들어 `shiftIsoDate("2026-08-17", -7)`이 한국 로컬 실행에서 "2026-08-09"를 반환했다(정답은
"2026-08-10"). 이 함수는 새로 만든 기능뿐 아니라 **기존에 이미 있던** "이전 주"·"다음 주"
이동 버튼도 그대로 썼으므로, 이 버그는 이번 작업 전부터 실사용 화면에 있었던 것으로 보인다.
`.toISOString()` 대신 로컬 날짜 필드(`getFullYear`/`getMonth`/`getDate`)로 직접 문자열을
조합하도록 고쳤다.

**검증**: 새 단위 테스트 4개 추가(`shiftIsoDate`, `todayIsoDate`,
`defaultWeeklyReportWeekOf` 각각의 계약 + 회귀 테스트) — 수정 전엔
`defaultWeeklyReportWeekOf(2026-08-17)`가 "2026-08-09"를 반환해 테스트가 즉시 실패해
버그를 그 자리에서 잡았다. 프론트 `tsc`·`eslint`(경고 0개)·`npm test`(71개) 모두 통과.
프론트 재빌드·재기동 후 배포된 번들 확인.

### 챗봇 "주간보고"에 "주요 회의 내용"이 통째로 빠지는 문제(2026-08-17)

"주간 업무보고" 화면(구조화 Markdown)에는 있는 "주요 회의 내용" 섹션이, 챗봇으로 물으면
아예 나오지 않았다.

**원인**: `weekly_report` Skill은 결과를 `data`(구조화 JSON, 공개 A2A 계약)와
`markdown`(그 데이터를 결정론적 템플릿으로 조립한 사람이 읽는 문서) 둘 다로 돌려준다.
"주요 회의 내용"(`meeting_highlights` — `analyze_meeting`이 이미 저장해 둔
`Meeting.summary` 재사용)은 **의도적으로 `data`에는 없고 `markdown`에만** 있다(공개 계약을
이 저장소 혼자 넓히지 않기 위해서, `_render_weekly_report_markdown()` docstring 참고). 화면의
"Markdown 복사" 버튼은 `markdown`을 그대로 쓰지만, 챗봇(`assistant_ask_workflow`)은
`sub_result.data.get("data")`(구조화 JSON)**만** `phrase_answer()`에 넘겼다 — `markdown`
자체를 아예 안 봤으므로 "주요 회의 내용"을 답할 재료가 원천적으로 없었다.

**설계 결정**: 공개 `WeeklyReportResult` JSON Schema(`docs/schemas/workmate-skill-schemas.schema.json`,
`additionalProperties: false`)에 `meeting_highlights`를 추가하는 건 A2A 공개 계약을 넓히는
일이라 하지 않았다(18번 문서 핵심 설계 결정 #1과 같은 원칙). 대신 `phrase_answer()`가
구조화 `data`뿐 아니라 Skill의 `markdown` 원문도 **참고용**으로 함께 받게 했다 — 공개
계약은 그대로 두면서, 챗봇 답변에서만 "JSON에는 없어도 Markdown에 있는 사실은 써도 된다"는
예외를 허용했다.

**구현**: `phrase_answer()`에 `markdown: str | None = None` 매개변수를 추가하고, 주어지면
프롬프트에 "참고용 Markdown 원문"으로 함께 싣는다. `assistant_ask_workflow`가
`sub_result.markdown`을 그대로 전달한다 — `weekly_report`뿐 아니라 markdown이 있는 모든
Skill에 일반적으로 적용된다.

**검증**: 실제 주간보고 데이터(진행 중 업무 1건 + "주요 회의 내용" 1건)를 실제 LLM Provider에
3회 호출 — 수정 전엔 이 내용이 통째로 빠졌지만, 수정 후엔 3/3 모두 답에 "주요 회의 내용"
섹션과 그 구체적 내용(트랜잭션 동시성 이슈 점검 등)이 포함됐다. 새 회귀 테스트 3개 추가
(`phrase_answer`의 markdown 반영 2개, `assistant_ask_workflow`가 `sub_result.markdown`을
그대로 넘기는지 1개) — 백엔드 전체 394개 테스트 통과. 백엔드 재기동 후 배포 확인.
