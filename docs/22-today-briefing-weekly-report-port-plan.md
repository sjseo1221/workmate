# 22. 오늘 브리핑 · 주간 업무보고 재이식 계획

> **상태**: ✅ 구현 완료(2026-08-19) — §8 참조
> **대상 화면**: 좌측 사이드바 `오늘 브리핑`, `주간 업무보고` 2개 화면만. `할 일 관리`(Workmate AI
> 탭 내부, 19번 문서 4단계 기 완료)와 `회의록 검색`(19번 문서 3단계 기 완료, 실데이터 유지 중)은
> 이 문서의 대상이 아니다.
> **선행 문서**: [19번 문서](19-workmate-ui-orchestrator-port-plan.md)(3단계에서 이 두 화면을 먼저
> 이식했다가, 2026-08-19 사용자 요청으로 목업으로 롤백됨), [15번 문서](15-workmate-ui-screens-reference.md)
> **경로 참고**: 이 문서의 `AI-agent_game_platform/frontend/...` 표기는 모노레포 재구성 이전
> 기준이다. 지금 실제 위치는 `AI-agent_game_platform/main_agent/frontend/...` —
> [25번 문서](25-orchestrator-pull-conflicts.md) 참고.
> §🏠 오늘 브리핑 · §📊 주간 업무보고(Source of Truth), [21번 문서](21-orchestrator-workmate-manual-verification-checklist.md)

## 0. 작업 원칙 (필수 준수)

1. **오케스트레이터 쪽 변경을 최소화한다.** `AI-agent_game_platform`은 팀원 소유 저장소다 —
   이 문서의 작업은 이미 우리가 소유하다시피 다뤄온 Workmate 전용 파일(`MainUiPanels.tsx`의
   두 컴포넌트, 그 컴포넌트가 쓰는 `./workmate/*`)**안에서만** 끝내는 게 기본값이다. §5의
   구현 범위가 그렇게 짜여 있다 — `App.tsx`, `styles.css`의 기존(다른 화면이 쓰는) 규칙,
   `backend/`의 어떤 파일도 이 작업 때문에 새로 건드릴 계획이 없다.
2. **불가피하게 오케스트레이터 핵심부(공용 컴포넌트, 라우팅, 백엔드, 다른 화면과 공유하는
   CSS 규칙 등)를 고쳐야 하는 상황이 생기면, 그 자리에서 직접 고치지 않는다.** 대신
   ① 로컬 clone에는 최소 범위로 임시 적용해 동작을 검증하고, ② 그 내용을 20번 문서의
   ["오케스트레이터 담당자에게 전달할 요청 목록"](20-orchestrator-ai-chat-skill-routing-plan.md#오케스트레이터-담당자에게-전달할-요청-목록-2026-08-18)에
   R11부터 이어서 같은 표 형식(`# | 문제 | 위치 | 현재 상태 | 요청할 수정`)으로 기록한다 —
   R1~R10과 동일한 원칙이다. 이 문서(22번)엔 "R11로 20번 문서에 기록함" 정도의 짧은 교차
   참조만 남기고, 상세 내용은 20번 문서 한 곳에 모은다(중복 기록 금지).
3. **Workmate 기존 기능에 영향이 없어야 한다.** 이 문서의 대상은 오늘 브리핑·주간 업무보고
   2개 화면뿐이지만, 실제 수정은 `MainUiPanels.tsx` 한 파일(다른 5개 화면 —
   할 일 관리·회의 녹음·회의 관리·회의록 검색·제안함 — 컴포넌트도 같은 파일에 있다) 안에서
   일어난다. 다음 두 가지를 모두 지킨다.
   - **워크메이트 자체(`workmate-agent`, 포트 8100)**: 이 작업은 프론트엔드 전용이라 백엔드
     Skill(`daily_briefing`/`rank_priorities`/`weekly_report`)이나 그 API를 전혀 건드리지
     않는다 — 코드 변경 자체가 안 생긴다.
   - **오케스트레이터에 이미 이식된 나머지 5개 화면**: `MainUiPanels.tsx` 안에서 새 import·
     새 로컬 컴포넌트(`SkillWarningsBanner` 등)를 추가할 때 기존 컴포넌트의 이름·export·
     동작을 바꾸지 않는다(§5-2). 구현 완료 후 §7 검증 절차에 "나머지 5개 화면 회귀 없음"
     확인 단계를 넣는다.

## 1. 왜 다시 하는가

19번 문서 3단계에서 이 두 화면을 이미 한 번 실데이터로 이식했었다. 그런데 그 구현을 다시 뜯어보니
(이번 계획 작성 과정에서 `workmate-ui/app/views/Briefing.tsx`·`Report.tsx` 원본과 대조) **화면이
"동작은 하지만 `daily_briefing`/`rank_priorities`/`weekly_report`가 실제로 반환하는 값 중 일부를
빠뜨리고 있었다** — 아래 §3 참조. 사용자가 "빠짐없이 동작"을 명시적으로 요구했으므로, 이번엔
원본 화면(`workmate-ui`)이 그리는 필드를 전부 나열하고 하나씩 체크하는 방식으로 다시 이식한다.
직전 구현은 2026-08-19에 목업으로 롤백돼 있는 상태([19번 문서 3단계 롤백 기록](19-workmate-ui-orchestrator-port-plan.md#3단계-구현-완료-2026-08-18))이므로, 지금은 목업에서 다시 시작한다.

## 2. 이미 갖춰진 것 (재사용, 손댈 필요 없음)

19번 문서 2·3단계에서 이식한 배관은 `MainUiPanels.tsx`의 화면 컴포넌트만 롤백됐을 뿐, 그 아래
공용 레이어는 그대로 남아 있고 이미 실서버(포트 8100)로 curl/Playwright 검증까지 끝난 상태다.
그대로 다시 쓴다.

| 파일 | 내용 | 상태 |
|---|---|---|
| `frontend/src/workmate/types.ts` | `DailyBriefingResult`, `PriorityRankingResult`, `PriorityItem`(+`score_breakdown`), `PriorityChange`, `WeeklyReportResult`, `WorkItem`, `PlanItem`, `SkillWarning` | 변경 없음, 이미 완전함 |
| `frontend/src/workmate/format.ts` | `dailyBriefingInput`, `rankPrioritiesInput`, `weeklyReportInput`, `movementLabel`, `formatKoreanDate`, `shiftIsoDate`, `defaultWeeklyReportWeekOf`, `truncateText`, `decodeHtmlEntities` | 변경 없음, 이미 완전함 |
| `frontend/src/workmate/use-skill.ts` | `useSkillRunner<T>(skillId, assignee)` — `{loading, error, data, warnings, run}` | 변경 없음, `warnings`가 이미 상태에 있는데 직전 구현이 그걸 화면에 안 그렸을 뿐 |
| `frontend/src/workmate/api.ts` | `skillChatApi.send()`, `WORKMATE_API_BASE_URL`, 결정 5 담당자 인증(`resolveAssigneeUserId`) | 변경 없음 |

즉 이번 작업은 **새 백엔드 연동이 아니라, 이미 연동된 데이터 중 화면에 안 그려지던 필드를 마저
그리는 작업**이 대부분이다.

## 3. 직전 구현이 빠뜨렸던 것 (`workmate-ui` 원본 대조 결과)

`workmate-ui/app/views/Briefing.tsx`·`Report.tsx`·`shared.tsx`를 원문 그대로 읽고, 롤백 직전
`MainUiPanels.tsx`의 `ReferenceBriefingPanel`(`kind="briefing"`)·`WeeklyReportPanel`과 한 줄씩
대조했다.

| # | 원본(`workmate-ui`)에 있는 것 | 직전 오케스트레이터 구현 | 이번에 할 일 |
|---|---|---|---|
| 1 | `WarningsList` — Skill 호출 중 일부 Provider(Gmail/Calendar/Task/Meeting)가 실패해도 `warnings: SkillWarning[]`로 부분 결과 + 경고 문구를 같이 보여준다(15번 문서 "Provider 실패는 부분 결과 + `warnings`로 표시"). `useSkillRunner`가 이미 `warnings`를 상태로 들고 있다. | **없음** — `warnings`를 아예 화면에 그리지 않음 | 오늘 브리핑·주간 업무보고 두 화면 모두에 경고 배너 추가(§5-1) |
| 2 | `source-status` — Task/Calendar/Gmail/Meeting 4개 소스 중 이번 호출에서 경고가 난 소스만 "지연"으로, 나머지는 "최신"으로 실시간 표시(`degradedSources = new Set(warnings.map(w => w.source))`) | 기존 목업의 `.signal-strip`을 그대로 하드코딩 유지("● Task 최신" 등 4개 다 고정 텍스트) | `.signal-strip`을 `warnings` 기반 동적 렌더링으로 교체(§5-1) |
| 3 | `score_breakdown` — 우선순위 카드에 마감임박도/중요도/지연·차단/회의 약속/일정 연관 5개 배점 내역을 선택적으로 펼쳐 보여줌(`PriorityItem.score_breakdown`, 03번 문서 §6 배점 공식) | **없음** — `item.reasons.join(" · ")`만 표시, `score_breakdown`은 안 씀 | 우선순위 카드에 배점 내역 한 줄 추가(§5-1) |
| 4 | 오늘 브리핑 새로고침 시 `daily_briefing`+`rank_priorities` 동시 재호출 | 동일하게 구현돼 있었음(`load()`) | 유지, 재확인만 |
| 5 | 주간 업무보고 — 이전/다음/최근 1주 이동, Markdown 복사, `WarningsList` | 이동·복사는 구현됨. `WarningsList`만 빠짐(#1과 동일 항목) | §5-1에서 함께 처리 |
| 6 | `RequireToken`(OIDC 토큰 없을 때 안내) | 오케스트레이터는 결정 5로 담당자 우회 인증을 쓰므로 원본 그대로 옮기지 않는 게 맞음(토큰 UI 자체가 없다) | **이식 안 함** — 의도적 축소, 아래 §4 참조 |

## 4. 의도적으로 안 옮기는 것 (축소 범위, 19번 문서 결정 5와 일치)

- **`RequireToken`**: 오케스트레이터는 담당자 선택(`assigneeName`)으로 인증을 우회하므로(결정 5),
  "Bearer Token이 필요합니다" 같은 화면은 애초에 나올 일이 없다. 옮기지 않는다.
- **`useWorkmateAuth()`의 `token` 의존성**: `useSkillRunner`가 이미 `{apiBase, assignee}`로
  바뀌어 있으므로 `token` 관련 분기(`if (!token) return <RequireToken />` 등)는 전부 제거한
  채로 옮긴다 — 이미 2·3단계에서 정한 패턴 그대로.
- **CSS 클래스 이름**: 원본은 `.hero`/`.panel`/`.two-column`/`.muted`/`--red` 같은 `workmate-ui`
  전용 클래스를 쓰지만, 오케스트레이터엔 이미 같은 화면을 그리는 `.report-dashboard`/
  `.briefing-*`/`.weekly-*` CSS가 있다(19번 문서 3단계에서 확인). 새 클래스를 추가하지 않고 그
  기존 className 안에서만 새 엘리먼트(경고 배너, 배점 내역)를 끼워 넣는다.

## 5. 구현 계획

### 5-1. `MainUiPanels.tsx` — 화면 컴포넌트 재작성

`ReferenceBriefingPanel`(`kind="briefing"` 경로만 — `kind="weekly"`는 19번 문서 3단계와 동일하게
죽은 코드로 남겨 둠, `App.tsx`가 그 경로를 호출하지 않음)와 `WeeklyReportPanel`을 19번 문서
3단계 때의 실데이터 버전을 베이스로 다시 작성하되, §3의 빠진 항목 3개를 추가한다.

1. **`useSkillRunner`/`useCallback`/`useEffect` 배선**: 3단계 때와 동일 — `daily_briefing`
   + `rank_priorities`를 함께 호출(오늘 브리핑), `weekly_report`를 `weekOf` 바뀔 때마다 재호출
   (주간 업무보고). `dailyBriefingInput()`/`rankPrioritiesInput()`/`weeklyReportInput(weekOf)`
   그대로 재사용.
2. **경고 배너 컴포넌트 추가**: 새 로컬 컴포넌트 `SkillWarningsBanner({ warnings })`를
   `MainUiPanels.tsx`에 추가(원본의 `WarningsList`에 대응). `warnings.length === 0`이면
   `null`. 새 CSS 클래스를 늘리지 않기 위해, 이미 화면에서 에러 표시에 쓰던 색 토큰(`#bd655b`)을
   인라인 스타일로 재사용한 배너 한 장으로 구현 — 예: `<div style={{ margin: "0 auto 16px",
   maxWidth: 1040, padding: "12px 16px", border: "1px solid #f0c2bd", background: "#fdf1f0",
   borderRadius: 10, color: "#8a3f37", fontSize: 12 }}>...</div>`. 각 warning을
   `{warning.source}: {warning.message}{warning.retryable ? " (재시도 가능)" : ""}` 형식으로 한
   줄씩. 오늘 브리핑(`briefing.warnings` + `priorities.warnings` 합침, 원본과 동일)과 주간
   업무보고(`report.warnings`) 양쪽에 최상단(헤더 바로 아래)에 배치.
3. **`.signal-strip` 동적화**: `SOURCE_LABELS = { task: "Task", calendar: "Calendar",
   email: "Gmail", meeting: "Meeting" }`를 상수로 두고, `degradedSources = new
   Set(warnings.map(w => w.source))`을 계산해 4개 `<span>`을 `{degradedSources.has(key) ?
   "지연" : "최신"}`으로 렌더링. 기존 마크업(`<span>● Task 최신</span>` 형태)의 구조는
   유지하고 텍스트만 동적으로 바꾼다 — CSS 변경 불필요.
4. **`score_breakdown` 렌더링**: `priority-card` 안, `reasons` 줄 아래에 `item.score_breakdown`이
   있을 때만 한 줄 추가 — 05개 배점 항목을 한글 라벨로 나열(원본의 `SCORE_BREAKDOWN_LABELS`
   그대로 포팅: 마감임박도/중요도/지연·차단/회의 약속/일정 연관). `<small>` 태그로 `.priority-card
   small` 기존 스타일(11px, 옅은 색) 재사용.
5. **`WeeklyReportPanel`도 동일 패턴**으로 `SkillWarningsBanner`만 추가. 나머지(주차 이동,
   Markdown 복사, 5개 블록)는 직전 구현이 이미 원본과 1:1로 맞아 손댈 게 없다.
6. **`onConfirm` prop**: 두 컴포넌트 모두 `onConfirm?: () => void`를 이미 타입에 갖고 있지만
   실제로는 아무도 안 쓴다(호출부는 `App.tsx`의 별도 플로팅 "확인 완료" 버튼, `confirmReport()`).
   기존과 동일하게 미사용 상태로 유지 — 이번 작업 범위 아님.

### 5-2. 새로 추가되는 로컬 상수/컴포넌트 (모두 `MainUiPanels.tsx` 내부, export 안 함)

- `SOURCE_LABELS: Record<string, string>`
- `SCORE_BREAKDOWN_LABELS: Record<keyof PriorityScoreBreakdown, string>`
- `SkillWarningsBanner({ warnings }: { warnings: SkillWarning[] })`

`PriorityScoreBreakdown`, `SkillWarning` 타입을 `./workmate/types`에서 새로 import해야 한다(직전
롤백 때 이 타입들도 import에서 빠졌음).

### 5-3. `App.tsx`

변경 없음 — 호출부(`<ReferenceBriefingPanel kind="briefing" assigneeName={assigneeName} />`,
`<WeeklyReportPanel assigneeName={assigneeName} />`)는 이미 3단계 때 배선이 끝나 있고 롤백 때도
안 건드렸다.

## 6. 완결성 체크리스트 (구현 완료 후 이 표를 채워서 문서에 기록한다)

19번 문서 3단계 완료 기록과 같은 형식으로, 이번엔 아래 표의 모든 행을 실서버(포트 8100) 연동
+ Playwright 스크린샷으로 하나씩 확인한다. "빠짐없이"가 이번 요구사항의 핵심이므로, 이 표가
곧 완료 기준이다.

| 화면 | 필드/기능 | 근거(Skill 응답 필드) | 확인 방법 | 확인 결과 |
|---|---|---|---|---|
| 오늘 브리핑 | 날짜, 인사말 요약(`summary`) | `DailyBriefingResult.date`/`.summary` | 화면 확인 | ✅ "8월 19일", "좋은 아침이에요, 서선정님." 실데이터 확인 |
| 오늘 브리핑 | 새로고침 버튼 → 재호출 | — | 클릭 후 네트워크 탭 | ✅ 클릭 시 `skill-chat/messages` 200 응답 2건(`daily_briefing`+`rank_priorities`) 재발생 확인(Playwright 네트워크 로그) |
| 오늘 브리핑 | **소스 상태 4개(Task/Calendar/Gmail/Meeting) 실제 warnings 반영** | `SkillWarning.source` | 의도적으로 한 Provider를 지연시켜 "지연" 뱃지 확인 | ✅ 일부러 실패를 유도할 필요조차 없었다 — 로컬 환경에 Google 자격 증명이 없어 **Gmail·Calendar가 실제로 "지연"**, Task·Meeting은 "최신"으로 정확히 갈려 표시됨 |
| 오늘 브리핑 | **경고 배너(있을 때만)** | `SkillChatResponse.warnings` | 위와 동일 | ✅ 실제 배너에 `email: GOOGLE_TOKEN_FILE or WORKMATE_GOOGLE_ACCESS_TOKEN is required for live Google providers (재시도 가능)`, `calendar: ...` 두 줄이 그대로 노출됨(스크린샷) |
| 오늘 브리핑 | 우선순위 Top 3 카드(순위/제목/점수/사유) | `PriorityRankingResult.priorities` | 화면 확인 | ✅ "수정된 트랜잭션 로직 PR 반영"(50점), "재화·경매장 처리 가이드 공유"(40점) 2건 실데이터(3번째는 데이터 자체가 2건뿐이라 없음 — 정상) |
| 오늘 브리핑 | **`score_breakdown` 배점 내역** | `PriorityItem.score_breakdown` | 화면 확인 | ✅ "마감임박도 20 · 중요도 20 · 지연/차단 0 · 회의 약속 10 · 일정 연관 0" 등 실제 배점 5개 항목 렌더링 확인 |
| 오늘 브리핑 | 순위 변동 라벨(신규/상승/하락) | `PriorityChange` | 담당자를 바꿔가며 재호출해 변동 있는 케이스 확인 | ⚠️ "순위 변동 없음"(`change.reason` fallback) 렌더링은 확인. "신규 진입"/"상승"/"하락" 케이스는 이번 검증 데이터로는 재현이 안 돼(같은 2건이 계속 1·2위) 코드 리뷰로만 확인 — `movementLabel()` 로직 자체는 19번 문서 3단계 때 이미 단위 검증됨 |
| 오늘 브리핑 | 오늘 일정 목록 + "등록됨" 뱃지 | `CalendarItem` | 화면 확인 | ⚠️ 빈 상태("오늘 일정이 없습니다")는 실데이터로 확인. 이 담당자는 오늘 Calendar 일정 자체가 없어 "등록됨" 뱃지 케이스는 데이터 부재로 미확인(코드는 19번 문서 3단계와 동일, 로직 변경 없음) |
| 오늘 브리핑 | 중요 업무 신호 목록 + "등록됨" 뱃지 | `ImportantSignal` | 화면 확인 | ⚠️ 위와 동일 — "중요 신호가 없습니다" 빈 상태만 실데이터 확인(Gmail 연동 자체가 이 환경엔 없음), 목록·뱃지 렌더링은 코드 리뷰로만 확인 |
| 주간 업무보고 | 기간·요약 문단 | `WeeklyReportResult.period`/`.summary` | 화면 확인 | ✅ "8월 12일 — 8월 19일" + LLM이 실제로 생성한 2문단 요약 확인 |
| 주간 업무보고 | **경고 배너(있을 때만)** | `report.warnings` | 위와 동일 | ✅ `weekly_report`는 Gmail/Calendar를 조회하지 않아(15번 문서) `warnings`가 빈 배열 — 배너가 안 뜨는 게 정상이고 실제로 안 떴다(정직하게 "정상 상태 확인"으로 기록, 거짓 "확인함" 아님) |
| 주간 업무보고 | 통계 4칸(완료/진행/지연/미해결) | `WeeklyReportResult.*.length` | 화면 확인 | ✅ 0/2/0/0 실데이터 확인 |
| 주간 업무보고 | 5개 블록(완료/진행/지연/미해결/다음주 계획) | `WorkItem[]`/`PlanItem[]` | 화면 확인 | ✅ 진행 중 업무 2건, 다음 주 계획 2건, 나머지 3개 블록은 "없음" 실데이터 확인 |
| 주간 업무보고 | 계획 배지(확정/이월/제안) | `PlanItem.kind` | 화면 확인 | ✅ "확정"(녹색) 배지 2건 확인. "이월"/"제안"(빨간) 배지는 이번 데이터에 없어 코드 리뷰로만 확인 |
| 주간 업무보고 | 이전/다음/최근 1주 이동 | `weekOf` state | 클릭 후 기간 문구 변경 확인 | ✅ "이전 주" 클릭 → "8월 12일 — 8월 19일"에서 "8월 5일 — 8월 12일"로 실제 재조회·변경 확인, "최근 1주로" 버튼도 그때만 나타남을 확인 |
| 주간 업무보고 | Markdown 복사 | `response.artifact.markdown` | 클릭 후 클립보드 확인 | ✅ 클릭 후 버튼 문구 "복사됨!"로 바뀌고, 클립보드에 실제 `# 주간 보고서\n\n기간: 2026-08-05 ~ 2026-08-12...` 마크다운이 담기는 것까지 확인 |

## 7. 검증 절차

19번 문서 3단계와 동일한 절차를 따른다.

1. `workmate-agent` 백엔드(포트 8100)를 `APP_BASE_URL='http://127.0.0.1:8100/a2a'`로 기동.
2. 오케스트레이터 프론트(`npm run dev` 또는 `npm run build && npx vite preview`)를 기동.
3. 담당자를 "서선정"(실제 Google OIDC sub와 매핑된 유일한 담당자)으로 선택 — 결정 5에 따라
   Task/Meeting 데이터가 있는 계정이어야 값이 실제로 채워진다.
4. `tsc --noEmit`, `vite build` 통과 확인.
5. Playwright로 오늘 브리핑·주간 업무보고 두 화면 스크린샷, §6 체크리스트 표를 하나씩 눈으로
   대조.
6. 경고 배너/소스 상태는 정상 상황에선 안 뜨는 게 정상이다(모든 Provider가 성공하면
   `warnings`가 빈 배열) — 실제로 "지연" 표시가 뜨는 걸 보려면 Gmail/Calendar 자격 증명을
   일부러 무효화하는 등 실패를 유도해야 한다. 그게 번거로우면 **코드 리뷰로 로직만 확인**하고,
   화면 캡처는 "정상 상태에선 배너가 없다"는 것까지만 확인한 뒤 문서에 그렇게 정직하게 기록한다
   (거짓으로 "확인함" 표시하지 않는다).
7. **회귀 확인(§0-3)**: `MainUiPanels.tsx`를 공유하는 나머지 5개 화면(할 일 관리·회의 녹음·
   회의 관리·회의록 검색·제안함)을 Playwright로 한 번씩 열어 이번 변경 전과 동일하게 렌더링되는지
   확인한다 — 특히 새로 추가하는 `SOURCE_LABELS`/`SCORE_BREAKDOWN_LABELS`/
   `SkillWarningsBanner` 같은 로컬 이름이 기존 이름과 충돌하지 않는지는 `tsc --noEmit`(6절)이
   이미 잡아준다. `npm run test:video-agent`도 다시 돌려 회귀가 없는지 확인한다(19번 문서
   3~8단계 완료 기록이 매번 확인해 온 항목과 동일).
8. **오케스트레이터 핵심부를 건드릴 일이 실제로 생기면(§0-2)**, 구현을 멈추고 먼저 20번 문서에
   R11부터 기록한 뒤 진행 여부를 사용자에게 확인받는다 — 계획에 없던 범위 확장이므로 조용히
   진행하지 않는다.
9. 완료되면 이 문서에 "8절 구현 완료" 절을 추가하고, §6 표의 각 행에 실제 확인 결과(스크린샷
   경로 또는 관찰 내용)를 채운다. 19번 문서에도 짧게 교차 참조를 남긴다. §0-2에 해당하는 R11+
   항목이 실제로 생겼다면 여기에도 "R11로 20번 문서에 기록함" 한 줄을 남긴다.

## 8. 구현 완료 (2026-08-19)

**변경 파일은 `AI-agent_game_platform/frontend/src/MainUiPanels.tsx` 한 곳뿐이다.** §0-1 원칙대로
`App.tsx`, `styles.css`, `backend/` 어느 것도 건드리지 않았다 — §0-2(불가피한 핵심부 변경 시
20번 문서에 R11로 기록)가 발동할 일 자체가 없었다.

### 무엇을 했나

- import 블록에 §5 계획대로 `dailyBriefingInput`/`rankPrioritiesInput`/`weeklyReportInput`/
  `movementLabel`/`formatKoreanDate`/`shiftIsoDate`/`defaultWeeklyReportWeekOf`/`truncateText`/
  `decodeHtmlEntities`(모두 `./workmate/format`, 롤백 전부터 손 안 탄 채로 남아 있던 함수)와
  `DailyBriefingResult`/`PriorityRankingResult`/`WeeklyReportResult`/`WorkItem`/`PlanItem`/
  `PriorityScoreBreakdown`/`SkillWarning`(모두 `./workmate/types`)를 다시 추가했다.
- 새 로컬 상수·컴포넌트 3개 추가(export 안 함, `MainUiPanels.tsx` 내부 전용): `SOURCE_LABELS`,
  `SCORE_BREAKDOWN_LABELS`, `SkillWarningsBanner`.
- `ReferenceBriefingPanel`(`kind="briefing"` 경로)과 `WeeklyReportPanel`을 §5 계획대로 다시
  작성했다 — 19번 문서 3단계의 실데이터 배선(Skill 호출·로딩/에러 상태·새로고침·주차 이동·
  Markdown 복사)에, 그때 빠졌던 세 가지(경고 배너, 동적 소스 상태, `score_breakdown`)를 더했다.
  `kind="weekly"` 죽은 코드 경로와 `WeeklyReportBlock`/`WeeklyPlanBlock` 헬퍼도 3단계 때와
  동일하게 유지·재사용했다.

### 검증 결과

1. `tsc --noEmit`, `vite build` 통과(에러 0).
2. `npx vitest run --no-file-parallelism` — **12개 테스트 파일 전부 통과, 75개 테스트 전부
   통과**(19번 문서 3~8단계 완료 기록과 동일한 베이스라인 수치, 회귀 없음). 병렬(`--pool`
   기본값) 실행에서는 Windows 환경 특유의 워커 스폰 타임아웃(코드와 무관, 이전에도 관측된
   환경 이슈)이 간헐적으로 나 일부 파일이 "시작조차 못 함"으로 뜬 적이 있었는데,
   `--no-file-parallelism`으로 재실행하면 매번 전부 통과한다 — 실패가 아니라 워커 풀 기동
   경쟁 조건이라는 뜻이다.
3. 로컬 실서버(`workmate-agent` 포트 8100, 담당자 "서선정")에 오케스트레이터 프론트(`npm run
   dev`, 포트 5173)를 붙여 Playwright로 실사용 검증. §6 체크리스트 표에 항목별 결과를 채웠다 —
   16개 항목 중 12개 ✅(완전 확인), 4개 ⚠️(코드는 있으나 이번 검증 데이터로는 특정 분기를
   재현 못 해 로직 검토로만 확인 — 순위 변동 신규/상승/하락, 일정·신호 "등록됨" 뱃지, 계획
   "이월"/"제안" 배지). ⚠️ 항목은 전부 **데이터 부재**(이 담당자 계정에 해당 케이스가 없음)가
   이유지 코드 결함이 아니다 — 19번 문서 3단계 때 이미 같은 사유로 동일하게 기록됐던 항목들이다.
4. **뜻밖의 좋은 신호**: 소스 상태·경고 배너를 검증하려고 일부러 Provider를 실패시킬 필요가
   없었다 — 이 로컬 환경 자체에 Google 자격 증명이 없어서 Gmail·Calendar가 **실제로** 지연
   상태였고, 그게 그대로 화면에 "지연" 뱃지와 `GOOGLE_TOKEN_FILE or WORKMATE_GOOGLE_ACCESS_TOKEN
   is required for live Google providers` 경고 배너로 나타났다. 직전(3단계) 구현이었다면 이
   실패가 화면에서 완전히 안 보이고 그냥 "메일 신호 0건"으로만 조용히 감춰졌을 상황이다 —
   이번에 추가한 두 기능이 정확히 이런 상황을 위한 것이었다는 게 실사용으로 증명됐다.
5. **회귀 확인(§0-3)**: `MainUiPanels.tsx`를 공유하는 나머지 5개 화면(할 일 관리·회의 녹음 및
   분석·회의 관리·이전 회의록 검색·제안함)을 Playwright로 순서대로 열어 콘솔 에러 0건, 5개
   탭 전부 정상 전환을 확인했다. 제안함 화면의 Google OIDC 안내문·5탭 한 줄 배치(직전 세션에서
   고친 것)도 그대로였다.

### 축소·미확인 사항 (정직하게 기록)

- 순위 변동(신규 진입/상승/하락), 일정·신호의 "등록됨" 뱃지, 계획의 "이월"/"제안" 배지 —
  코드 경로는 3단계 때와 동일해 새로 만든 게 아니지만, 이번 실데이터로는 해당 조건을 못
  만들어서 화면 캡처로 재확인은 못 했다.
- `RequireToken`은 §0/§4의 결정대로 의도적으로 이식하지 않았다(결정 5, 담당자 우회 인증).

R11로 20번 문서에 기록할 항목은 없다 — 오케스트레이터 핵심부를 건드릴 필요 자체가 없었다.
