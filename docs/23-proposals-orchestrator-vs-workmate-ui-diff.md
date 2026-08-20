# 오케스트레이터 vs workmate-ui "제안함" 로직 차이 분석

작성일: 2026-08-19
상태: 분석·기록만(구현 항목 아님) — 실사용 중 두 화면을 나란히 확인하다 나온 질문에 답하기 위해 작성
경로 참고: 아래 `AI-agent_game_platform/frontend`는 모노레포 재구성 이전 기준이다. 지금 실제
위치는 `AI-agent_game_platform/main_agent/frontend/src/MainUiPanels.tsx` —
[25번 문서](25-orchestrator-pull-conflicts.md) 참고.

## 배경

"제안함"(Gmail·Calendar 기반 임시 Task 제안 승인/무시 화면)은 원본 `workmate-ui`(Next.js,
`app/views/Proposals.tsx`)에서 오케스트레이터(`AI-agent_game_platform/frontend`,
`MainUiPanels.tsx`의 `ProposalsDetailPanel`/`ProposalsInner`)로 이식됐다(19번 문서 7단계,
2026-08-18). 그 뒤 2026-08-19에 인증 방식이 한 번 더 바뀌었다(19번 문서 "2026-08-19 후속" 참고).
이 문서는 지금 시점 두 구현의 **실제 코드 차이**를 정리한다 — 새로 뭘 고치자는 계획이 아니라
기록용이다.

## 요약 표

| 항목 | workmate-ui (원본) | 오케스트레이터 (이식본) |
| --- | --- | --- |
| 인증 방식 | Google OIDC ID Token 수동 붙여넣기(`Get-FreshIdToken.ps1`), React state에만 보관, 새로고침마다 재입력 | `X-Workmate-Assignee` 헤더(사이드바 "담당자" 선택) — 2026-08-19부터, 이전엔 여기도 OIDC 필요했음 |
| SSE Provider 마운트 범위 | 앱 Shell 최상단(`page.tsx`) — 화면 전환해도 구독 유지 | "제안함" 탭 자신(`ProposalsDetailPanel`)에만 마운트 — 탭을 벗어나면 SSE 연결도 끊김 |
| 호스트 구조 | Next.js App Router의 독립 라우트(`/proposals`) | `MainUiPanels.tsx` 안의 한 패널 함수 — 탭 전환 시 통째로 리마운트 |
| 인증값 전달 방식 | `useWorkmateAuth()` Context 훅으로 앱 전역에서 읽음 | `WorkmateConfig` 객체를 prop으로 명시적으로 내려받음(Context 없음) |
| API 인증 모드 개념 | 없음 — 모든 호출이 OIDC Bearer 하나로 고정 | `auth: "assignee" \| "oidc"`를 API 함수마다 선택하는 계층이 있음(`api.ts`) — 결정 5의 산물 |
| 개발 서버에서 SSE 동작 | 정상(Next.js dev 서버) | `npm run dev`(Vite, React StrictMode 이중 마운트)에서는 SSE가 안 붙음 — `vite preview`로만 검증 가능 |
| Task 승인 시 필드 편집 UI(`ProposalCard`) | 있음(제목·담당자·마감·우선순위 인라인 편집) | 동일하게 있음 — 1:1 포팅, 로직 차이 없음 |
| 승인/무시 호출 조립(`defaultTaskInput`, Idempotency-Key) | `lib/proposal-review.ts` | `workmate/proposal-review.ts` — import 경로·주석만 다르고 로직은 동일 |
| Toast·데스크톱 알림·백그라운드 Polling 주기 | 있음(`proposal-notifications.tsx`) | 동일 로직 포팅(`workmate/proposal-notifications.tsx`) — 인증값만 `token`→`assignee`로 교체 |

## 항목별 상세

### 1. 인증 방식 — 가장 큰 차이

- **workmate-ui**: `lib/workmate-auth.tsx`의 `useWorkmateAuth()`가 Google ID Token을 오직 React
  state로만 들고 있고 어떤 storage에도 저장하지 않는다(의도적 보안 결정, 코드 주석에 명시).
  토큰이 없으면 `RequireToken` 화면만 보여준다. `proposal_api.py`/`dev_gmail_sync_api.py`/
  `dev_calendar_sync_api.py`/`google_oauth_web.py`는 지금도 `_authenticated_user`(엄격한 OIDC
  전용)만 받는다 — workmate-ui 자체는 이 부분을 바꾼 적이 없다.
- **오케스트레이터**: 처음 이식했을 때는 workmate-ui와 똑같이 OIDC 토큰 붙여넣기 게이트가
  있었다(`ProposalsDetailPanel`의 `if (!token) return <입력창...>`). 2026-08-19에 이 게이트를
  없애고 나머지 6개 화면과 같은 `X-Workmate-Assignee` 헤더 인증으로 통일했다 — 대응하는
  workmate-agent 쪽 변경(`_authenticated_user_or_assignee` 전환, 12개 라우트)도 같은 날 반영했다
  (19번 문서 "2026-08-19 후속" 참고). 로컬 전용 프로젝트 서버라는 전제 하에 사용자가 확인한
  트레이드오프다 — 이름만 대면 통과되는 방식이라 "인증"이 아니라 "자기 신고"에 가깝다.
- 즉 **같은 소스에서 시작했지만 지금은 두 화면의 인증 모델이 실제로 다르다**: workmate-ui는
  여전히 진짜 신원 증명(OIDC)을 요구하고, 오케스트레이터는 이름 선택만으로 통과한다.

### 2. SSE(Server-Sent Events) 구독의 생명주기

- **workmate-ui**: `ProposalNotificationsProvider`가 앱 Shell 최상단에서 한 번 마운트된다 —
  사용자가 "오늘 브리핑"이나 "할 일 관리" 화면에 가 있어도 SSE 연결이 유지되고, 새 제안이
  도착하면 어느 화면에서든 Toast·데스크톱 알림으로 받는다.
- **오케스트레이터**: Provider를 `ProposalsDetailPanel`(제안함 탭 자신)에만 마운트한다 — 19번
  문서 7단계에서 "범위를 하나 좁혔다"고 의도적으로 기록한 제약이다. 제안함 탭을 벗어나면(다른
  4개 Works 탭이나 다른 Agent 채팅으로 이동) SSE 연결도 함께 끊긴다. 오케스트레이터 Shell
  전체에 Provider를 올리려면 Toast 배치 등 셸 레이아웃 변경이 더 필요해 이후 과제로 남아 있다.
- **실사용 영향**: workmate-ui에서는 "제안함을 안 보고 있어도 새 메일 제안이 오면 알림이 뜬다"가
  성립하지만, 오케스트레이터에서는 **제안함 탭을 직접 열어야만** 새 제안을 실시간으로 받는다.

### 3. 호스트 구조 — 독립 페이지 vs 임베디드 패널

- **workmate-ui**: `/proposals`가 Next.js App Router의 독립 라우트다. URL을 직접 열 수 있고,
  페이지 컴포넌트 하나가 전체 화면을 소유한다.
- **오케스트레이터**: `ProposalsDetailPanel`/`ProposalsInner`는 `MainUiPanels.tsx` 안의 함수 하나로,
  App.tsx가 관리하는 "Works" 탭 전환(`activeChat`/`activeSection` state)에 종속된다. 탭을 벗어났다
  돌아오면 컴포넌트가 통째로 리마운트되므로 SSE 재연결, `googleAuthApi.status()` 재조회 등이 매번
  처음부터 다시 일어난다 — workmate-ui의 페이지 이동(다른 라우트로 갔다가 돌아옴)도 마찬가지로
  리마운트되므로 이 자체는 두 구현이 비슷하지만, 오케스트레이터는 "탭"이라는 더 가벼운 단위로
  훨씬 자주 이 리마운트가 일어난다(다른 3개 Agent 채팅 탭을 오갈 때도 포함).

### 4. 인증값 전달 방식 — Context 훅 vs 명시적 prop

- **workmate-ui**: 컴포넌트 트리 어디서든 `useWorkmateAuth()`를 호출해 전역 Context에서 토큰을
  꺼낸다.
- **오케스트레이터**: `App.tsx`가 들고 있는 `assigneeName` state를 `MainUiPanels.tsx`까지 명시적
  prop으로 내려보내고, `ProposalsDetailPanel`이 이를 `WorkmateConfig`로 조립해 자식에게 다시
  prop으로 내린다 — 별도 Context가 없다. 오케스트레이터의 나머지 6개 화면도 전부 이 방식(prop
  drilling)을 쓰므로, 제안함만의 차이라기보다 오케스트레이터 전체의 아키텍처 선택이다.

### 5. API 인증 모드 선택 계층

- **workmate-ui**: `lib/workmate-api.ts`의 모든 호출이 OIDC Bearer 하나로 고정돼 있다 — 인증
  "모드"라는 개념 자체가 없다.
- **오케스트레이터**: `workmate/api.ts`의 `apiFetch()`/`streamSse()`가 `auth: "assignee" | "oidc"`
  파라미터를 받아 호출마다 다른 인증 헤더를 붙인다. 결정 5(19번 문서)가 6개 화면과 제안함을
  가르면서 생긴 구조인데, 2026-08-19 이후로는 11개 호출 전부가 `"assignee"`라서 지금은 이
  분기가 실질적으로 안 쓰인다 — `"oidc"` 분기는 코드에 남아 있지만 호출부에서 아무도 안 쓴다
  (나중에 옵션 B(GIS 자동 재발급)로 되돌아갈 가능성을 남겨둔 것, 19번 문서 결정 5 "채택안" 참고).

### 6. 개발 서버에서 SSE가 붙는지 여부

- **workmate-ui**: `next dev`(Next.js 개발 서버)에서 정상적으로 SSE가 붙는다.
- **오케스트레이터**: `npm run dev`(Vite)는 React 18/19 `StrictMode`의 의도적 이중 마운트-언마운트
  때문에 SSE 연결이 붙었다 끊기는 과정에서 실제로 붙지 않는 현상이 있다(19번 문서 R3, 코드
  결함이 아니라 검증 방법의 문제로 기록됨) — `npm run build && npx vite preview`로 프로덕션
  빌드를 띄워야 SSE 연결을 확인할 수 있다. workmate-ui 쪽은 이 문제가 없다.

### 7. 승인/무시 로직 자체 — 차이 없음

- `ProposalCard`의 인라인 편집 필드(제목·담당자·마감일·우선순위), `defaultTaskInput()`,
  Idempotency-Key 조립, 유사 중복 재확인(`allow_similar_duplicate`) 흐름은 **두 구현이
  기능적으로 동일**하다 — `proposal-review.ts`를 diff해 봐도 import 경로와 주석만 다르고 로직은
  그대로다. 이 부분은 이식 과정에서 드리프트가 없었다.

## 남는 질문 (필요해지면 별도로 재검토)

- 오케스트레이터에도 Provider를 Shell 최상단으로 올려 "다른 화면에 있어도 새 제안 알림을 받는"
  workmate-ui와 같은 경험을 줄지 — Toast 배치 등 셸 레이아웃 변경이 선행돼야 한다(19번 문서
  7단계 "범위를 하나 좁혔다"에 이미 기록된 미결 사항).
- `auth: "oidc"` 분기가 지금은 죽은 코드에 가깝다 — 옵션 B(GIS 자동 재발급) 채택 시점에 다시
  쓰거나, 그때까지도 안 쓰면 정리 대상이 될 수 있다.

## 관련 문서

- [19-workmate-ui-orchestrator-port-plan.md](19-workmate-ui-orchestrator-port-plan.md) — 결정 5(인증
  방식), 7단계(제안함 이식), "2026-08-19 후속"(담당자 헤더로 완화).
- [15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md) — 제안함 화면·Skill
  기능 정의.
