# workmate-ui 화면·로직을 오케스트레이터로 이식하는 작업 계획 (Option B)

작성일: 2026-08-17
상태: ✅ 1~8단계 전부 완료(2026-08-19, 로컬 clone 구현·검증) — 남은 건 "오케스트레이터 담당자에게
전달할 요청 목록"(R1~R3)을 실제 담당자에게 전달해 오케스트레이터 저장소에 반영하는 것뿐이다.
갱신: 2026-08-18 — 메뉴 구조 변경: 7개 화면을 단일 nav로 통합하는 원안을 폐기하고, 좌측
사이드바의 `오늘 브리핑`/`주간 업무보고` 개별 화면은 그대로 유지, "Workmate AI" 내부 상단 탭
메뉴는 4개(할 일 관리/회의 녹음/회의 관리/회의록 검색)에 `제안함`을 추가해 5개로 확장하는
방향으로 수정.
갱신: 2026-08-18(2차) — 원칙 추가: 오케스트레이터는 **프론트만** 변경하고 **백엔드는 변경하지
않는다**. 이에 따라 "핵심 설계 결정 1"의 옵션 A(오케스트레이터 backend 프록시)는 제외하고
옵션 B(프론트 직접 연결)로 확정. 프론트 변경 사항도 오케스트레이터 저장소(팀원 소유)를 직접
고칠 수 없으므로, 구현 진행하며 "오케스트레이터 담당자에게 전달할 요청 목록" 절에 모아 정리한다
(20번 문서의 R1~R6 패턴과 동일).
갱신: 2026-08-18(3차) — 결정 1에서 "별도로 풀어야 한다"고 남겨둔 OIDC 재입력 UX 문제를 검토해
"결정 5"로 정리. 오케스트레이터가 이미 갖고 있는 "담당자" 선택(`assignee.ts`)을 재사용해
Task·Meeting·스킬챗은 이름 기반 고정 매핑으로 우회하고, Gmail/Calendar 기반 제안함만 실제 OIDC
검증을 유지하는 방안을 채택안으로 기록(착수 전, 세부 값 확정 필요).

## 배경

오케스트레이터(`AI-agent_game_platform`) 프론트의 "Workmate AI" 채팅 화면은 이 저장소 담당자가 맡고
있다. 지금 이 화면의 상단 메뉴는 `할일관리 / 회의녹음및분석 / 회의관리 / 이전회의록검색` 4개이고
내용은 전부 하드코딩된 정적 목업이다. 반면 `workmate-ui`는 이미 실제 `workmate-agent` 백엔드에 연결된
7개 화면(`오늘 브리핑 / 주간 업무보고 / 할 일 관리 / 회의 녹음 / 회의 관리 / 회의록 검색 / 제안함`)을
갖고 있다.

이 문서 작성 전에 다음을 검토했다:

1. 오케스트레이터가 다루는 화면 7개의 라벨은 `workmate-ui`와 동일하게 맞출 것 —
   [workmate-ui/app/page.tsx](../workmate-ui/app/page.tsx)의 `navigation` 배열이 Source of
   Truth다. (2026-08-18 수정: 다만 이 7개를 오케스트레이터 쪽에서 하나의 메뉴로 합치지는
   않는다 — "목표" 절 참고. 처음엔 "7개짜리 단일 메뉴로 맞춘다"는 뜻이었지만, 오케스트레이터의
   기존 2단 구조(좌측 사이드바 개별 화면 2개 + Workmate AI 내부 탭 메뉴)를 유지하는 쪽으로
   바뀌면서 "라벨만 맞추고 배치는 기존 구조를 따른다"로 좁혀졌다.)
2. 오케스트레이터 내부 화면이 `workmate-ui`가 실제로 구현한 기능을 반영하게 할 것 — 두 방식을
   비교했다.
   - **A. iframe 임베드**: `workmate-ui`를 별도 서버로 띄우고 오케스트레이터 화면 안에 통째로
     끼워 넣는 방식. 검토 결과 `workmate-ui`가 자체 사이드바·topbar를 가진 완결된 앱 Shell이라
     오케스트레이터 사이드바와 이중으로 겹치고, OIDC Bearer Token을 새로고침마다 다시 입력해야
     하는 UX([workmate-ui/lib/workmate-auth.tsx](../workmate-ui/lib/workmate-auth.tsx))가 그대로
     남으며, 이 환경에서 `npm run dev`(vinext)가 불안정하다는 문제가 있었다
     ([workmate-ui/README.md](../workmate-ui/README.md) "알려진 한계").
   - **B. 화면·로직 이식**: `workmate-ui/app/views/*.tsx`가 구현한 기능을 오케스트레이터
     프론트 코드로 옮겨와, 오케스트레이터 자체 컴포넌트가 `workmate-agent` API를 직접(또는
     오케스트레이터 backend를 경유해) 호출하게 만드는 방식.
   - `workmate-ui/README.md`가 애초에 "1차로 이 저장소를 완성하고, 2차로 완성된 화면과 로직을
     팀 공통 Orchestrator UI 양식에 맞게 이식해 M5에서 반영한다"고 명시하고 있어, B가 원래
     계획된 방향과 일치한다. **B로 진행하기로 결정**했고, 이 문서는 그 작업 계획이다.

관련 문서:

- [15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md) — 이식 대상 7개 화면의
  기능·조회값 정의(Source of Truth). 이 문서의 화면별 계획은 전부 15번 문서를 근거로 한다.
- [17-workmate-ui-gap-analysis.md](17-workmate-ui-gap-analysis.md) — `workmate-ui` 자체의 갭·구현
  이력. 오케스트레이터로 이식할 때도 같은 제약(예: 화자 분리 미지원, 실시간 자막 항상 빈 문자열)을
  그대로 물려받는다.
- [18-workmate-assistant-implementation-plan.md](18-workmate-assistant-implementation-plan.md) —
  `workmate-ui` 안에서 "오케스트레이터 자체 컴포넌트 + 백엔드 프록시 어댑터" 패턴을 쓴 선례
  (Drawer 구현). 다만 그 작업은 같은 저장소 안 신규 기능 추가였고, 이 문서는 화면 자체를 **다른
  저장소로** 이식하는 것이라 범위가 다르다.
- `AI-agent_game_platform/backend/app/video_agent_client.py` — 오케스트레이터가 이미 쓰고 있는
  "얇은 프록시 어댑터" 패턴의 실제 코드 선례였으나, 2026-08-18 "원칙"(오케스트레이터 백엔드
  변경 안 함)에 따라 이번 계획은 이 패턴을 따르지 않기로 했다 — 참고용으로만 남겨둔다.

## 원칙 — 오케스트레이터는 프론트만 변경, 백엔드는 변경하지 않음

이번 이식 작업은 `AI-agent_game_platform`의 **프론트(`frontend/`)만** 건드리고, **백엔드
(`backend/`)는 손대지 않는다.** 이 원칙이 아래 "핵심 설계 결정 1"을 사실상 결정한다 —
옵션 A(오케스트레이터 backend가 프록시 라우트를 새로 만드는 방식)는 backend 변경이 필요해
**제외**하고, 옵션 B(프론트가 `workmate-agent`를 직접 호출)로 **확정**한다. 이전 초안의 "단기는
B, 필요해지면 A로 전환"이라는 단계적 접근도 이 원칙과 맞지 않으므로 폐기한다 — A로 전환할 일
자체가 없다.

프론트 변경도 예외가 아니다 — `AI-agent_game_platform`은 이 프로젝트가 아니라 팀원이 소유한
저장소라([20번 문서](20-orchestrator-ai-chat-skill-routing-plan.md)의 같은 전제 참고), 프론트
코드라도 이 프로젝트가 직접 반영할 수 없다. 로컬 clone에서 구현·검증까지는 하되, 실제 반영은
담당자에게 요청해야 한다 — 구현이 진행되면서 나오는 변경 사항을 아래 "오케스트레이터 담당자에게
전달할 요청 목록" 절에 모아 20번 문서의 R1~R6와 같은 방식으로 정리한다.

## 목표

오케스트레이터 프론트(`AI-agent_game_platform/frontend`)의 기존 2단 구조(좌측 사이드바의
`오늘 브리핑`/`주간 업무보고` 개별 화면 + "Workmate AI" 안의 상단 탭 메뉴)는 그대로 유지하고,
각 화면의 내용만 `workmate-ui`가 실제로 구현한 기능·데이터로 대체한다. **7개 화면을 하나의 nav로
통합하지 않는다** — 이 결정으로 이전 초안(모든 화면을 단일 7탭 nav로 합치는 안)을 대체한다.

- **좌측 사이드바 개별 화면 2개**: `오늘 브리핑`, `주간 업무보고` — 지금처럼 사이드바에서 직접
  클릭해 들어가는 독립 화면으로 유지하고, 그 화면 안의 내용만 실제 데이터로 교체한다.
- **"Workmate AI" 내부 상단 탭 메뉴**: 지금의 4개(`할일관리`/`회의녹음및분석`/`회의관리`/
  `이전회의록검색`)에 `제안함`을 추가해 **5개**로 확장한다.

목표 메뉴(라벨은 `workmate-ui/app/page.tsx`의 `navigation` 배열과 동일하게 맞추되, 배치는 위
2단 구조를 따른다):

| 위치 | 순서 | 라벨 | `workmate-ui` 원본 컴포넌트 | 15번 문서 절 |
| --- | --- | --- | --- | --- |
| 좌측 사이드바(개별 화면) | 1 | 오늘 브리핑 | `Briefing.tsx` | [🏠 오늘 브리핑](15-workmate-ui-screens-reference.md#-오늘-브리핑-briefingtsx) |
| 좌측 사이드바(개별 화면) | 2 | 주간 업무보고 | `Report.tsx` | [📊 주간 업무보고](15-workmate-ui-screens-reference.md#-주간-업무보고-reporttsx) |
| Workmate AI 내부 탭 | 1 | 할 일 관리 | `Tasks.tsx` | [📋 할 일 관리](15-workmate-ui-screens-reference.md#-할-일-관리-taskstsx) |
| Workmate AI 내부 탭 | 2 | 회의 녹음 | `Meeting.tsx` | [🎙️ 회의 녹음](15-workmate-ui-screens-reference.md#-회의-녹음-meetingtsx) |
| Workmate AI 내부 탭 | 3 | 회의 관리 | `Archive.tsx` | [📁 회의 관리](15-workmate-ui-screens-reference.md#-회의-관리-archivetsx) |
| Workmate AI 내부 탭 | 4 | 회의록 검색 | `Search.tsx` | [🔍 회의록 검색](15-workmate-ui-screens-reference.md#-회의록-검색-searchtsx) |
| Workmate AI 내부 탭 | 5 | 제안함(신규) | `Proposals.tsx` | [📬 제안함](15-workmate-ui-screens-reference.md#-제안함-proposalstsx) |

## 범위

**포함**

- 위 7개 화면의 실제 기능·데이터 이식(하드코딩 목업 대체).
- 위 화면들이 의존하는 `workmate-agent` REST·스킬챗 엔드포인트를 오케스트레이터가 호출할 수 있게
  하는 연결 경로 구축 — 프론트가 `workmate-agent`에 직접 연결한다(아래 "원칙", "핵심 설계 결정 1" 참고).
- 좌측 사이드바 `오늘 브리핑`/`주간 업무보고` 2개 화면은 구조를 그대로 두고 내용만 실제 데이터로
  교체. "Workmate AI" 내부 상단 탭 메뉴는 지금의 4개(`할 일 관리`/`회의 녹음 및 분석`/
  `회의 관리`/`이전 회의록 검색`)에 `제안함`을 추가해 5개로 확장 — 두 nav를 하나로 합치지 않는다.

**제외 (이번 계획 밖)**

- [Workmate 어시스턴트 Drawer](18-workmate-assistant-implementation-plan.md) — `workmate-ui`에만
  있는 기능이고 오케스트레이터에는 이미 별도의 Main Chatbot이 있어 역할이 겹친다. 이식 여부는
  별도로 논의한다.
- 실시간 녹음 중 임시 자막 텍스트 — `workmate-agent`의 STT Provider가 아직 연결되지 않아
  `workmate-ui`에서도 항상 빈 문자열이다(15번 문서 "알려진 한계"). 이식해도 같은 제약을 그대로
  물려받는다.
- 회의 참석자 목록·전체 회의록(Transcript 원문) 화면 — `workmate-ui` 자체도 아직 미구현
  (15번 문서 진행 상태 표: 📁 회의 관리는 "분석 결과 표시~Task 등록만 작성").
- 자연어 → Skill 자동 판별 — 18번 문서와 동일한 이유로 범위 밖 유지(LLM Router 필요, 별도 결정
  사항).
- 멀티 사용자 권한·팀 배정 — Workmate MVP 자체에 없는 개념(15번 문서 "담당자 필드는 만들지
  않는다").

## 현재 상태 대조

| 화면 | 오케스트레이터 현재 (`MainUiPanels.tsx`) | `workmate-ui` 실제 |
| --- | --- | --- |
| 오늘 브리핑 / 주간 업무보고 | `ReferenceBriefingPanel`/`WeeklyReportPanel` — 완전 하드코딩 | `daily_briefing`+`rank_priorities`, `weekly_report` 스킬챗 실데이터 |
| 할 일 관리 | `TaskDetailPanel` — 하드코딩 4행, 버튼 동작 없음 | `/api/v1/tasks` CRUD 실데이터 |
| 회의 녹음 | `RecordingDetailPanel` — 버튼만 있고 동작 없음 | `/api/v1/meetings` 생성+업로드+WebSocket 실시간 녹음 |
| 회의 관리 | `MeetingsDetailPanel` — 하드코딩 3행 | 회의 목록 + `analyze_meeting` 폴링 + Action Item 승인 |
| 회의록 검색 | `MeetingSearchDetailPanel` — 고정 질문·고정 답변 | `search_meetings` Hybrid(Vector+Trigram RRF) 검색 실데이터 |
| 제안함 | 없음 | SSE 실시간 수신 + Gmail/Calendar 동기화 + 승인/무시 |

## 핵심 설계 결정

결정 1은 위 "원칙"에 따라 확정했다. 결정 2~4는 구현 착수 전 확정이 필요하다.

### 결정 1 — ✅ 확정: B(프론트 직접 연결). OIDC 인증 문제는 별도로 풀어야 함

위 "원칙" 절에 따라 옵션 A(오케스트레이터 backend 프록시)는 제외하고 **B로 확정**했다 — 더 이상
열린 결정이 아니다. 다만 B를 택해도 아래 OIDC 인증 문제는 그대로 남아 있어 별도로 풀어야 한다.

`workmate-agent`의 인증 모델은 두 가지가 공존하며 서로 다르다(코드 확인 완료):

- **`/a2a` (A2A 스킬챗)**: `WORKMATE_SERVICE_TOKEN` 고정 시크릿 하나로 인증
  (`workmate-agent/app/a2a/runtime.py`). 오케스트레이터가 지금 "Workmate AI" 채팅에서
  `daily_briefing` skill_id로 호출하는 경로가 바로 이것이다(`backend/app/main.py`의
  `build_agent_request`).
- **`/api/v1/*`, `/api/v1/internal/skill-chat/*` (`workmate-ui`가 쓰는 모든 REST·스킬챗 엔드포인트)**:
  `_authenticated_user()`(`workmate-agent/app/internal_chat.py`)가 요구하는 **Google OIDC ID
  Token**으로 인증한다. `WORKMATE_SERVICE_TOKEN`으로는 이 경로를 호출할 수 없다 — 서로 다른
  인증 체계다.

즉 오케스트레이터가 지금 갖고 있는 서비스 토큰만으로는 이번에 이식할 7개 화면이 쓰는 엔드포인트를
호출할 수 없다 — B를 택해도 이 OIDC 문제 자체는 남는다.

**제외한 옵션 A(참고용 기록)**: 오케스트레이터 backend가 `video-agent` Task API 같은 패턴으로
신규 프록시 라우트를 만들어 대신 호출해주는 방식. `Get-FreshIdToken.ps1`(저장소 루트)의
refresh_token 기반 자동 갱신을 backend 안에 구현하면 풀 수 있었지만, backend 변경이 전제라
"원칙"에 따라 제외했다.

**확정한 옵션 B — 프론트가 `workmate-agent`에 직접 연결**: `workmate-ui`와 동일하게 프론트가
`workmate-agent`를 직접 호출하고, `SettingsModal.tsx`(OIDC 토큰 붙여넣기 UI)도 그대로 이식한다.

- 장점: 백엔드 작업이 없음(`workmate-agent`의 CORS 허용 origin에 오케스트레이터 프론트 포트
  추가만 필요 — 이것도 우리가 통제하는 `workmate-agent` 쪽이라 원칙에 안 걸림), SSE·WebSocket도
  프론트가 표준 브라우저 API로 그대로 연결(설계·검증이 끝난 `workmate-ui` 구현을 그대로 재사용).
- 감안할 점: 오케스트레이터 화면 안에 "Google ID Token을 새로고침마다 다시 붙여넣어야 하는" UX가
  그대로 들어온다 — `workmate-ui`가 이미 겪고 있는 한계를 오케스트레이터도 그대로 떠안는다. 또한
  오케스트레이터 안에 서비스 토큰 기반 인증(A2A, "Workmate AI" 채팅)과 사용자 OIDC 토큰 기반
  인증(이번에 이식하는 REST 7개 화면)이 동시에 존재하게 된다. backend를 못 건드리는 이상 이 UX는
  당장 개선할 방법이 없다 — 실사용에 방해가 될 정도면 그때 "원칙" 자체를 재검토해야 한다.

### 결정 2 — ✅ 확정: `c:\dev\workmate\workmate-agent`

`AI-agent_game_platform`의 실제 docker-compose 3개(`docker-compose.yml`,
`docker-compose.workmate-local.yml`, `docker-compose.smoke-8011.yml`)가 전부 `build: ../workmate-agent`를
쓴다 — `AI-agent_game_platform` 기준 상위 경로라 정확히 이 저장소의 서브모듈
`c:\dev\workmate\workmate-agent`(오늘 세션 내내 실행·인증 코드 조사에 쓴 그 경로)와 같다.
`workmate-agent-main`은 실제 파일시스템에 존재하지 않는 경로이며, `run-local-stack.ps1`(conda
python으로 `uvicorn app:app --port 8001`을 직접 띄우는 옛 방식 — 오늘 쓴 `uv run python -m
app.server` 방식과도 다름)과 2026-08-07자 설계 문서 2개에만 남아있는 죽은 참조로 확인했다.

### 결정 3 — ✅ 확정: `localhost:5173`만 CORS 허용 목록에 추가

오늘 세션에서 오케스트레이터 backend를 `8000→8090`으로 옮겼고(Windows 예약 포트 범위
`7962-8061` 때문), `workmate-ui`도 이미 `workmate-agent`를 `8001→8100`으로 옮긴 이력이 있다
(같은 예약 범위 문제, `workmate-ui/lib/workmate-auth.tsx` 주석 참고). 옵션 B가 확정되면서
오케스트레이터 프론트가 `workmate-agent`를 **직접** 호출하므로(오케스트레이터 backend는
경유하지 않음), `workmate-agent`의 CORS 허용 origin만 넓히면 된다 — 오케스트레이터 backend의
CORS 설정은 이 작업과 무관해 건드릴 필요가 없다. `allow_origin_regex`로 로컬 포트 전체를 여는
대안은 운영 설정과 섞일 위험이 있어(20번 문서 R3와 같은 이유) 채택하지 않는다.

```
WORKMATE_STANDALONE_UI_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,<기존 기본값 유지>
```

### 결정 4 — ✅ 확정: 이동 확인창(confirm)

`workmate-ui`의 실시간 녹음은 "WebSocket 연결 = 세션 시작, 연결이 끊기면(정상 종료든 접속
끊김이든) = 서버가 그 시점까지 받은 Chunk를 자동 병합해 세션 확정"으로 설계돼 있다(15번 문서
"🎙️ 회의 녹음" #3, `workmate-agent/app/recording_stream.py`). `workmate-ui`는 녹음이 단일
전체화면 안에서만 이뤄져 이 문제가 없었지만, 오케스트레이터는 사이드바로 다른 메뉴를 클릭하면
녹음 컴포넌트가 그대로 unmount되며 WebSocket이 끊기고, 그 순간 서버가 세션을 바로 확정해버린다.

녹음 중 다른 메뉴로 이동하려 하면 "이동하면 녹음이 종료됩니다" confirm을 띄우고, 사용자가
확인하면 이동을 허용한다(이동 자체를 막지는 않음). 이동 자체를 비활성화하는 방식은 회의 중
다른 화면을 봐야 하는 실사용과 충돌할 수 있어 채택하지 않는다. 녹음 컴포넌트를 전역에 유지해
언마운트 자체를 막는 방식(WebSocket이 화면 전환과 무관하게 유지됨)은 근본적이지만
오케스트레이터 레이아웃 구조 변경이 필요해 이번 "화면 이식" 범위를 넘어선다 — 확인창 방식이
실사용에서 불편함이 크면 그때 재검토한다. 구체적 구현 지점(React Router blocker/`beforeunload`
등 어떤 API로 이동을 가로챌지)은 6단계 착수 시 오케스트레이터 프론트 코드를 보고 정한다.

### 결정 5 — OIDC 재입력 UX 문제의 해결 방안

결정 1에서 B(프론트 직접 연결)로 확정하면서 "별도로 풀어야 한다"고 남겨둔 문제다. `workmate-ui`와
동일하게 오케스트레이터도 `/api/v1/*`·`/api/v1/internal/skill-chat/*` 호출마다 사용자가 직접
Google ID Token을 붙여넣어야 하고(`SettingsModal.tsx`가 Token을 어떤 storage에도 저장하지 않음,
`workmate-auth.tsx` 참고), Token 자체 수명도 짧다(`Get-FreshIdToken.ps1` 기준 보통 1시간).

검토한 대안:

- **A. `localStorage`에 토큰 저장**: 새로고침 재입력은 없어지지만 1시간 만료는 그대로 남고, 지금
  의도적으로 안 남기던 보안 결정(`workmate-auth.tsx` 주석)만 후퇴시키는 반쪽짜리 개선이라 단독
  채택 안 함.
- **B. Google Identity Services(GIS) JS SDK 자동 재발급**: `client_id`만으로(secret 불필요) 브라우저에
  로그인 상태가 유지되는 한 자동으로 새 ID Token을 받는, 순수 프론트 변경이라 "원칙"에 안 걸리는
  "제대로 된" 방식. 다만 (1) Google Cloud Console에 프론트 Origin 등록이 선행돼야 하고, (2)
  `Get-FreshIdToken.ps1`이 쓰는 Client ID가 데스크톱 앱 타입일 가능성이 있어 웹 앱용 Client ID를
  별도로 새로 만들어야 할 수 있으며, (3) 서드파티 쿠키 차단 브라우저·시크릿 모드에서는 자동 갱신이
  조용히 실패해 결국 수동 클릭이 필요할 수 있다. 이번 계획에서 당장 채택하지 않고, 아래 채택안으로도
  여전히 남는 제안함 화면의 로그인 번거로움을 줄이고 싶어지면 그때 별도로 재검토한다.
- **C. `_authenticated_user()` 검증 자체를 무조건 통과**: `user_id`(=JWT `sub`)가 Task·Meeting·Google
  Credential(`repositories/google_credentials.py`의 PK) 등 시스템 전체의 식별 키라서, 고정값으로
  바꿔도 데이터 연속성 자체는 문제없음을 확인했다. 그러나 (1) env 게이팅 없이 하면 인증이 영구히
  사라지고, (2) 오케스트레이터처럼 팀 공용으로 전환되는 순간 호출자 전원이 하나의 `sub`로 몰려
  데이터가 섞이며, (3) `tests/test_internal_chat.py`의 401 계약(M0.3 OIDC 증빙)과 어긋난다 —
  단독 채택 안 함.
- **D. C를 `WORKMATE_OIDC_DEV_BYPASS` 같은 env로 게이팅**: 편의는 챙기지만 (2)의 "팀원 전원이 한
  사람으로 기록됨" 문제는 그대로 남는다.
- **E. D를 라우터별로 쪼갬**: `task_api.py`/`meeting_api.py`/`internal_chat.py`(스킬챗)만 우회하고,
  Gmail/Calendar 기반 제안함(`proposal_api.py`)은 실제 `_authenticated_user()`를 그대로 유지 —
  제안함의 팀원 간 데이터 혼입(자기 것 아닌 Gmail 제안을 보게 되는 문제)은 막지만, Task/Meeting은
  여전히 하나의 고정 identity로 몰리는 문제가 남는다.

**채택안(F, E의 확장) — 오케스트레이터의 기존 "담당자" 선택을 identity로 재사용**

오케스트레이터 프론트에 이미 4명 고정 목록과 역할별 현재 담당자 선택 UI가 있다
(`AI-agent_game_platform/frontend/src/assignee.ts`의 `assigneeOptions`/`defaultAssignments`,
`AssigneeSwitcher.tsx`) — "Workmate 담당자" 역할에 지금 배정된 사람 이름(기본값 `서선정`)을 이미
알고 있으므로 이를 그대로 재사용한다.

- **오케스트레이터 프론트** (원칙에 따라 우리가 직접 못 고침 — "오케스트레이터 담당자에게 전달할
  요청 목록"에 등록): `workmate-agent` 호출마다 현재 `assignments["Workmate 담당자"]` 값을 커스텀
  헤더 **`X-Workmate-Assignee`**로 함께 보낸다. **HTTP 헤더 값은 ASCII 밖 문자를 담지 못해서**(구현
  중 실제로 확인 — httpx·브라우저 `fetch` 둘 다 한글을 그대로 넣으면 인코딩 예외를 낸다) 반드시
  `encodeURIComponent(name)`으로 percent-encode해서 보내야 한다(예: `encodeURIComponent("서선정")`
  → `%EC%84%9C%EC%84%A0%EC%A0%95`). 서버는 `urllib.parse.unquote`로 이를 그대로 되돌린다.
- **`workmate-agent`(우리 저장소, 직접 구현)**: 정적 매핑 `ASSIGNEE_TO_USER_ID`(4명 이름 →
  고정 `user_id`)를 두고, 아래 "우회 대상"의 `Depends(_authenticated_user)`를 이 매핑을 읽는 새
  Dependency로 교체한다. `서선정`은 지금까지 실사용해온 실제 `sub`(`10464531542706509691`)로
  매핑해 기존 Task·Meeting 데이터 연속성을 유지하고, 나머지 3명(`배동우`/`이승현`/`변해훈`)은
  사람이 읽을 수 있는 고정 placeholder `user_id`(예: `dev-assignee-video`,
  `dev-assignee-develop`, `dev-assignee-gameqna` — 실제 Google `sub`처럼 보이는 임의 숫자열은
  나중에 진짜 계정과 헷갈릴 수 있어 피한다)를 발급한다. 매핑에 없는 이름이 오거나 헤더가 없으면
  400으로 거부한다(조용히 섞이는 것 방지).

**우회 대상 vs 실제 OIDC 유지 — 라우터 전체 스캔 결과**

`_authenticated_user`를 쓰는 라우터를 전수 조사(`grep`)한 결과, 애초 기록에는 `task_api.py`·
`meeting_api.py`·`internal_chat.py`만 적었으나 두 곳이 빠져 있었다 — `action_item_api.py`(회의
관리 화면의 Action Item 승인·조회, `POST /api/v1/meetings/{id}/actions:review` 등 — 이번 계획
포함 범위)와 `transcript_api.py`(`GET /api/v1/meetings/{id}/transcript` — `workmate-ui/lib/
workmate-api.ts`가 실제로 호출). 이 둘도 담당자 이름 우회 대상에 넣지 않으면 회의 관리·회의 녹음
화면의 일부 기능만 여전히 OIDC를 요구하게 된다.

| 그룹 | 라우터 | 비고 |
| --- | --- | --- |
| 우회(담당자 이름 매핑) | `task_api.py`, `meeting_api.py`, `internal_chat.py`, `action_item_api.py`, `transcript_api.py`, `proposal_api.py`, `dev_gmail_sync_api.py`, `dev_calendar_sync_api.py`, `google_oauth_web.py` | 전부 담당자 헤더로 충분 — 2026-08-19 후속 변경(아래) 전에는 뒤 4개만 실제 OIDC 유지 대상이었다 |

~~실제 OIDC 유지: `proposal_api.py`, `dev_gmail_sync_api.py`, `dev_calendar_sync_api.py`,
`google_oauth_web.py` — Gmail/Calendar 기반이거나 Google 계정 연동 자체를 다뤄 진짜 신원이
필요하다는 이유로 예외를 뒀었다.~~ **2026-08-19 후속 변경으로 이 예외를 없앴다** — 아래 "2026-08-19
후속" 참고.

한계(의식적으로 받아들이는 트레이드오프):

- 이건 인증이 아니라 자기 신고다 — 헤더에 어떤 이름을 넣든 서버는 그대로 믿는다. 서버가
  `127.0.0.1`에만 열려 있고 대상이 4명뿐인 신뢰된 로컬 팀 도구라는 전제 하에서만 허용 가능한
  수준이며, 외부에 노출되는 배포에는 이 방식을 쓸 수 없다.
- (2026-08-19 이전 상태, 지금은 아래 "후속 변경"으로 해소) 제안함(Gmail/Calendar 기반)만 실제
  신원이 필요해 그 화면을 열 때는 여전히 진짜 Google 로그인(수동 붙여넣기)이 필요했다 — 나머지
  6개 화면은 토큰 없이 바로 됐다.

### 2026-08-19 후속 — 제안함도 담당자 헤더로 완화(사용자 확인 완료)

**배경**: 제안함의 "Google ID Token 붙여넣기" UX가 실사용에 방해가 될 정도로 불편하다는 피드백이
나왔다(위 "감안할 점"이 예견한 상황). 옵션 B(GIS 자동 재발급)는 Google Cloud Console 설정(Origin
등록, Client ID 타입 확인)이 사용자 쪽에서 선행돼야 해 이번엔 보류하고, 대신 **옵션 C/D/E가
우려했던 "이름만 대면 통과"의 위험**(다른 사람 PC에서 이름만 골라 그 사람의 실제 Gmail·Calendar를
열람할 수 있음)을 사용자에게 명시적으로 설명한 뒤 — **로컬 전용 프로젝트 서버라 그 위험을 감수
가능하다는 확인을 받고** 제안함도 우회 대상에 합류시켰다.

- **`workmate-agent`(우리 저장소)**: `proposal_api.py`·`dev_gmail_sync_api.py`·
  `dev_calendar_sync_api.py`·`google_oauth_web.py`의 모든 라우트를 `Depends(_authenticated_user)`
  에서 `Depends(_authenticated_user_or_assignee)`로 옮겼다(파일당 import 한 줄 + 각 라우트의
  `Depends(...)` 한 곳씩, 총 12곳). 로직 자체(`_authenticated_user_or_assignee`)는 이미 존재하던
  걸 그대로 재사용했다 — `Authorization` 헤더가 있으면 여전히 진짜 OIDC로만 검증하고, 헤더가 아예
  없을 때만 담당자 이름으로 넘어간다. 영향받은 4개 테스트 파일(`test_proposals.py`·
  `test_dev_gmail_sync_api.py`·`test_dev_calendar_sync_api.py`·`test_google_oauth_web.py`)의
  `dependency_overrides`도 같은 이름으로 맞춰 갱신했다. 전체 스위트 `python -m unittest discover -s
  tests` — **439개 PASS, 0 FAIL, 12 SKIP**.
- **오케스트레이터 프론트(로컬 clone, 커밋·푸시 안 함 — R1~R10과 같은 패턴)**: `workmate/api.ts`의
  `proposalsApi`·`devGmailSyncApi`·`devCalendarSyncApi`·`googleAuthApi` 7개 호출과
  `streamSse()`(SSE)를 `"oidc"`에서 `"assignee"` 인증으로 옮겼다. `proposal-notifications.tsx`는
  `config.token` 대신 `config.assignee`를 구독 조건으로 쓰도록 바꿨다. `MainUiPanels.tsx`의
  `ProposalsDetailPanel`에서 토큰 붙여넣기 게이트(`if (!token) return <입력창...>`)를 완전히
  제거하고, 나머지 6개 화면과 똑같이 `assignee: assigneeName`만으로 바로 화면이 열리게 했다 —
  이제 사용자는 "Google 계정 연결" 버튼을 눌러야만(선택 사항, 개인 Gmail/Calendar를 실제로 동기화
  하고 싶을 때만) 진짜 구글 로그인 팝업(`google_oauth_web.py`의 기존 PKCE 흐름 — Google Cloud
  Console 설정 변경 불필요, 기존 Desktop 타입 Client ID의 Loopback 리디렉션 허용을 그대로 재사용)
  을 보게 된다. `api.test.ts`의 관련 테스트 2개도 OIDC 기대값에서 담당자 헤더 기대값으로 다시
  썼다. 검증: `tsc --noEmit`·`vite build` 모두 클린, `vitest run src/workmate/api.test.ts` 10개
  PASS, 실행 중인 workmate-agent(포트 8100)를 재시작해 `curl`로
  `/api/v1/auth/google/status`·`/start`·`/api/v1/notifications/stream` 전부 담당자 헤더만으로
  200을 확인했다(헤더 없이는 여전히 401).
- **여전히 남는 한계**: 이건 여전히 자기 신고이지 인증이 아니다 — 로컬·소수 신뢰 팀 전제가
  깨지면(외부 배포, 팀 확장 등) 이 완화 전체를 재검토해야 한다. 옵션 B(GIS 자동 재발급)는 여전히
  "제대로 된" 대안으로 문서에 남겨둔다 — Google Cloud Console 설정을 사용자가 준비하면 그때
  전환할 수 있다.

상태: ✅ **구현 완료(2026-08-18)** — `workmate-agent` 쪽은 로컬에 실제로 반영하고 전체 테스트로
검증했다. 아래는 착수 전 예측이 아니라 구현하며 실제로 확인·수정한 내용이다.

**구현 내용**

- `app/internal_chat.py`: `ASSIGNEE_TO_USER_ID` 매핑과 `_authenticated_user_or_assignee()`를
  추가했다. `Authorization` 헤더가 있으면 **항상** 기존 `_authenticated_user()`로 검증하고(무효해도
  담당자 헤더로 조용히 안 넘어감 — 그렇지 않으면 아무 토큰이나 넣고 담당자를 사칭할 수 있다),
  헤더가 아예 없을 때만 `X-Workmate-Assignee`를 본다. 이 설계 덕분에 **당초 예상과 달리
  `tests/test_internal_chat.py`는 한 줄도 안 고쳐도 됐다** — 그 파일의 모든 테스트가 실제 Bearer
  토큰을 보내므로 그대로 기존 OIDC 경로를 탄다.
- `task_api.py`/`meeting_api.py`/`action_item_api.py`/`transcript_api.py`/`internal_chat.py`의
  `Depends(_authenticated_user)`를 `Depends(_authenticated_user_or_assignee)`로 교체.
  `proposal_api.py`/`dev_gmail_sync_api.py`/`dev_calendar_sync_api.py`/`google_oauth_web.py`는
  그대로 뒀다.
- `main.py`: CORS `allow_headers`에 `x-workmate-assignee` 추가, 기본 origin에 `localhost:5173` 추가
  (결정 3).
- 신규 `tests/test_assignee_auth.py` 5개 테스트 추가 — 헤더 없음(401), 모르는 이름(400),
  4명 각각 고정 `user_id`로 정확히 스코프 분리되는지, `Authorization`이 있으면(무효해도) 담당자
  헤더로 안 넘어가는지, percent-encode 안 된 값은 500이 아니라 400으로 처리되는지.

**구현하며 실제로 걸린 문제 2건(둘 다 해결)**

1. **`app.dependency_overrides`가 함수 객체를 키로 쓴다**: `test_task_api.py`·`test_meeting_api.py`·
   `test_action_item_api.py`·`test_recording_stream.py` 4개 파일이
   `app.dependency_overrides[_authenticated_user] = ...`로 인증을 흉내 냈는데, 라우트가 이제
   `_authenticated_user_or_assignee`에 의존하므로 이 override가 안 먹혀 21 FAIL + 19 ERROR가
   났다(전수 조사에서 "별도 테스트 파일 없음"이라고 잘못 판단했던 부분 — 실행해보고서야 발견).
   네 파일 모두 import·override 대상을 `_authenticated_user_or_assignee`로 바꿔 해결.
   `tests/test_proposals.py`는 `proposal_api.py` 자체는 그대로지만 `/api/v1/tasks`(이동한
   라우트)를 검증용으로 호출하는 부분이 있어, 두 함수를 **모두** override하도록 추가.
2. **HTTP 헤더 값은 비ASCII 문자를 못 담는다**: 처음엔 `X-Workmate-Assignee: 서선정`을 그대로
   보내는 테스트를 짰는데 `UnicodeEncodeError`로 클라이언트 단에서부터 깨졌다 — httpx도 브라우저
   `fetch`도 마찬가지다. `unquote`/`encodeURIComponent` 기반 percent-encoding으로 고쳤다(위
   "오케스트레이터 프론트" 항목에 반영).

**검증**: `uv run python -m unittest discover -s tests -v` → **435 tests, OK (skipped=12)**.

## 아키텍처 (결정 1: B로 확정)

```
오케스트레이터 프론트 (신규 컴포넌트, frontend/src/workmate/*)
  ├─ workmate-agent를 직접 호출 (workmate-ui/lib/workmate-api.ts 이식)
  └─ SettingsModal 이식 — 사용자가 Google ID Token을 직접 붙여넣음
        │  fetch (CORS, 사용자 OIDC 토큰)
        ▼
workmate-agent (/api/v1/*, /api/v1/internal/skill-chat/*)
```

오케스트레이터 backend는 전혀 관여하지 않는다("원칙" 참고) — `workmate-ui/lib/`의
`workmate-api.ts`·`workmate-auth.tsx`·`workmate-format.ts`를 그대로(또는 최소 수정으로)
가져와 쓴다.

## 단계 구분

| 단계 | 범위 | 비고 |
| --- | --- | --- |
| 1단계 | ✅ 완료(2026-08-18) — "Workmate AI" 내부 상단 탭 메뉴에 `제안함`을 추가해 4개→5개로 확장(자리만 만들고 데이터는 아직 목업 유지). 좌측 사이드바 `오늘 브리핑`/`주간 업무보고`는 구조 변경 없음 | 저위험, 결정 1~4와 무관하게 먼저 할 수 있음 |
| 2단계 | ✅ 완료(2026-08-18) — 아래 "2단계 구현 완료" 참고 | 이후 단계의 전제조건 |
| 3단계 | ✅ 완료(2026-08-18) — 아래 "3단계 구현 완료" 참고 | 가장 단순한 3개 화면 먼저 |
| 4단계 | ✅ 완료(2026-08-18) — 아래 "4단계 구현 완료" 참고 | 단순 REST CRUD |
| 5단계 | ✅ 완료(2026-08-18) — 아래 "5단계 구현 완료" 참고 | 스킬챗 폴링 패턴 필요(18번 문서 `usePollingSkillRunner` 참고) |
| 6단계 | ✅ 완료(2026-08-18) — 아래 "6단계 구현 완료" 참고 | 결정 4(SPA 전환 문제) 처리 포함 |
| 7단계 | ✅ 완료(2026-08-19) — 아래 "7단계 구현 완료" 참고 | 오케스트레이터에 없던 화면이라 신규 사이드 개념(Toast, 종 아이콘 배지)도 함께 이식 필요 |
| 8단계 | ✅ 완료(2026-08-19) — 최종 회귀(`workmate-agent` 435 tests, 프론트 75 tests, 둘 다 OK), [21번 문서](21-orchestrator-workmate-manual-verification-checklist.md) 신규 작성([13번 문서](13-manual-verification-guide.md) 패턴) | |

3~5단계는 REST·스킬챗 위주라 이식 방식이 상대적으로 균일하다. 6·7단계는 WebSocket·SSE라 별도
검토가 필요해 뒤로 미룬다.

### 2단계 구현 완료 (2026-08-18)

`workmate-ui/lib/workmate-api.ts`·`workmate-types.ts`를 `frontend/src/workmate/{api,types}.ts`로
이식했다. `workmate-ui` 원본은 모든 호출에 OIDC Bearer Token 하나만 썼지만, 결정 5로 인증
경로가 갈리므로 `apiFetch`에 `auth: "assignee" | "oidc"`를 추가해 갈랐다 — Task·Meeting·스킬챗
계열은 `X-Workmate-Assignee`(percent-encode 필수), 제안함·Gmail/Calendar 동기화·Google 계정
연결은 그대로 OIDC Bearer. `WorkmateConfig`도 `{ apiBase, token }`에서 `{ apiBase, assignee,
token? }`로 바뀌었다 — `assignee`는 App.tsx가 이미 들고 있는 `assigneeName` state를 그대로 넘기면
되므로, **3~6단계 화면은 `workmate-ui`와 달리 별도 토큰 입력 UI(`SettingsModal`)가 필요 없다**
(원래 아키텍처 다이어그램의 전제가 결정 5로 바뀐 부분 — 토큰 입력 UI는 7단계 제안함에서만 필요).

- 신규 `frontend/src/workmate/types.ts`, `api.ts`, `api.test.ts`(10개, `test:video-agent`
  스크립트가 `src/**/*.test.{ts,tsx}`를 전부 잡으므로 별도 `test:workmate` 스크립트는 추가하지
  않았다 — 추가해도 정확히 같은 걸 두 번 도는 것이라 의미가 없다).
- **최소 동작 확인을 헬스체크보다 한 단계 더 나갔다**: `POST` 없이 실제 로컬 backend(포트
  8100)에 `curl -H "X-Workmate-Assignee: %EC%84%9C%EC%84%A0%EC%A0%95" .../api/v1/tasks` →
  `200 []`, `Origin: http://localhost:5173` + `Access-Control-Request-Headers:
  x-workmate-assignee`로 실제 브라우저 Preflight를 흉내 낸 `OPTIONS` → `200`,
  `access-control-allow-headers`에 `x-workmate-assignee` 포함, `access-control-allow-origin:
  http://localhost:5173` 확인 — 프론트가 실제로 마주칠 CORS·인코딩 제약까지 전부 통과.
- **이 과정에서 발견**: 로컬에 떠 있던 backend 프로세스가 어제 실행분이라 오늘 코드 변경(결정 5,
  CORS 헤더 추가)을 반영 못 하고 있었다(재시작 전엔 `OIDC bearer token is required`, CORS
  Preflight도 거부). Python 프로세스는 코드 변경을 자동 반영하지 않으므로 재시작해서 확인했다 —
  이후 이어지는 단계에서도 프론트만 바꾸는 게 아니라 backend 코드까지 바꿨다면 재시작이 필요하다는
  점을 유의.
- `tsc -b --noEmit`, `vitest run src/workmate/api.test.ts`(10 passed) 통과.

### 3단계 구현 완료 (2026-08-18)

`workmate-ui/lib/workmate-format.ts`(Next.js 의존 없는 순수 함수 모음)를 `frontend/src/workmate/
format.ts`로, `lib/use-skill.ts`를 `use-skill.ts`로 이식했다(`useSkillRunner`는 `{apiBase, token}`
대신 `{apiBase, assignee}`로 바꿔 결정 5에 맞춤).

**파일 계획을 문서 원안에서 바꿨다**: 원래 계획은 `Briefing.tsx`/`Report.tsx`/`Search.tsx`를
새 파일로 만드는 것이었는데, 실제로 보니 오케스트레이터에 이미 `MainUiPanels.tsx`의
`ReferenceBriefingPanel`/`WeeklyReportPanel`/`MeetingSearchDetailPanel`이 이 세 화면과 똑같은
목업으로 존재했고, **그 목업들의 className(`briefing-header`, `priority-grid`, `weekly-metrics`,
`meeting-search-form` 등)이 이미 `styles.css`에 정확히 스타일링돼 있었다**(`workmate-ui`
원본은 `.hero`/`.panel`/`.two-column` 같은 전혀 다른 className을 쓰는데, 오케스트레이터엔 그
CSS가 없다). 그래서 새 파일을 만들어 이식하는 대신, **이 세 기존 컴포넌트의 하드코딩된 내용만
실데이터로 교체**했다 — 문서가 애초에 말한 "내용만 실데이터로 교체"(목표 절)에 오히려 더 맞는
방식이고, 스타일이 이미 갖춰져 있어 화면이 그대로 정상적으로 보인다.

- `ReferenceBriefingPanel`(`kind="briefing"`만 실제 호출 경로 — `kind="weekly"`는 죽은 코드라
  그대로 둠): `daily_briefing` + `rank_priorities`.
- `WeeklyReportPanel`: `weekly_report`, 주차 이동(이전/다음/최근 1주)과 Markdown 복사 포함.
- `MeetingSearchDetailPanel`: `search_meetings`, `TaskQuickActions` → `App.tsx`까지
  `assigneeName`을 새 prop으로 관통시켜 전달(4~7단계 화면들도 이 prop을 그대로 재사용한다).

**실제 로컬 backend(포트 8100)에 붙여 Playwright로 검증**(`assignee=서선정`):
- **오늘 브리핑**: 목업 "85점 QA 서버 빌드 배포" 대신 실제 오늘 날짜(`8월 18일`)와
  "오늘 일정 0건, 메일 신호 0건, 우선순위 0건입니다"(이 assignee로는 아직 Task·Meeting 데이터가
  없어 정직하게 빈 상태로 뜸) — 하드코딩이 사라지고 실제 응답을 그대로 반영하는 걸 확인.
- **주간 업무보고**: 실제 LLM이 생성한 요약 문단("2026-08-11부터 2026-08-18까지... 별도로 보고할
  작업 진행 사항이나 이슈가 확인되지 않았습니다"), 통계 4칸, 5개 블록, 주차 이동 버튼까지 전부 정상.
- **회의록 검색**: 검색을 실행하면 `HTTP 503: DATABASE_URL is required for search_meetings`가
  화면에 뜬다 — **이건 버그가 아니라 로컬 환경 제약이다**. `search_meetings`(Hybrid Vector+Trigram
  검색)는 PostgreSQL이 있어야 하는데, 지금 로컬 backend는 `DATABASE_URL` 없이 SQLite로 떠 있다
  (`workmate-agent/README.md` "`DATABASE_URL`이 없을 때만... SQLite"). 에러 처리 자체(`ApiError`
  → 화면에 메시지로 표시)는 의도대로 동작한다 — Postgres가 붙은 환경에서 재검증하면 될 항목으로
  남겨둔다.
- `tsc -b --noEmit`, `vite build`, `npm run test:video-agent`(75 passed, 회귀 없음) 통과.

**오늘 브리핑 / 주간 업무보고 롤백(2026-08-19)**: 사용자 요청으로 이 두 화면만 3단계 이전
목업으로 되돌렸다(`MeetingSearchDetailPanel`은 대상이 아니라 실데이터 그대로 유지). `frontend/
src/MainUiPanels.tsx`의 `ReferenceBriefingPanel`/`WeeklyReportPanel` 본문을 git HEAD(`313ce66`,
19번 문서 작업 이전 커밋) 버전으로 교체 — `daily_briefing`/`rank_priorities`/`weekly_report`
스킬챗 호출과 그 전용 헬퍼(`WeeklyReportBlock`/`WeeklyPlanBlock`, `dailyBriefingInput` 등)를
제거하고 하드코딩된 원래 목업 내용으로 되돌렸다. `App.tsx`의 호출부(`<ReferenceBriefingPanel
kind="briefing" .../>`, `<WeeklyReportPanel assigneeName={assigneeName} />`)는 건드리지 않았다
(타입에 `assigneeName?`를 남겨 뒀을 뿐 이제 쓰지 않음). `tsc --noEmit` 통과, Playwright로 두
화면 모두 원래 목업 문구("85점 QA 서버 빌드 배포", "8월 3일 — 8월 9일 · 완료 8 / 진행 중 4 /
지연 2 / 주요 회의 6")가 다시 보이는 것을 확인했다. **회의록 검색은 이 롤백 대상이 아니다** —
`search_meetings` 실데이터 연동은 그대로 남아 있다.

**후속**: 이 두 화면은 [22번 문서](22-today-briefing-weekly-report-port-plan.md)에서
`workmate-ui` 원본과 필드 단위로 대조해 다시 실데이터로 이식했다(2026-08-19 완료) — 이번엔
그때 빠졌던 경고 배너·소스 상태 동적화·`score_breakdown`까지 포함한다.

### 4단계 구현 완료 (2026-08-18)

3단계와 같은 방식 — `workmate-ui/app/views/Tasks.tsx`의 로직을 새 파일이 아니라 기존
`TaskDetailPanel`(목업)에 이식했다. 원래 목업엔 "담당자" 컬럼이 있었지만 Workmate MVP엔 그
개념이 없어(15번 문서 "담당자 필드는 만들지 않는다", `workmate-ui`도 그 컬럼이 없음) 빼고, 그
자리에 수정·완료·삭제 액션 버튼을 넣었다 — 컬럼 5개(`.task-table-head`/`.task-table-row`의
기존 5열 grid CSS)는 그대로 유지.

- `GET/POST /api/v1/tasks`, `PATCH/DELETE /api/v1/tasks/{id}` 전부 연결. 필터(전체/진행 중/지연),
  검색, 등록·수정 폼, 완료 토글, 삭제(확인창 포함) 모두 포함.
- **실제 로컬 backend에 대고 생성→완료→삭제 전체 왕복을 Playwright로 실행**: "Stage4 검증용
  Task" 생성 → 목록에 반영(전체 1) → 완료 처리 → 삭제(confirm 다이얼로그 자동 수락) → 목록이
  다시 "조건에 맞는 할 일이 없습니다"(전체 0)로 돌아오는 것까지 확인 — Mock이 아니라 실제
  SQLite Task Store에 쓰고 읽었다.
- `tsc -b --noEmit`, `vite build`, `npm run test:video-agent`(75 passed, 회귀 없음) 통과.

### 5단계 구현 완료 (2026-08-18)

`workmate-ui/app/views/Archive.tsx`를 기존 `MeetingsDetailPanel`(목업)에 이식했다 — 3·4단계와
같은 방식(기존 CSS 재사용). **범위를 하나 좁혔다**: Action Item의 "수정"(제목·설명·마감일·담당자
직접 편집) 인라인 폼은 이번엔 빼고 승인·거절·일괄 승인만 이식했다 — `reviewActions` API 자체는
`decision: "edit"`을 이미 지원하므로, 필요해지면 `workmate-ui`의 `EditForm` 패턴을 그대로 가져와
붙이면 된다(지금은 각 컴포넌트가 아주 길어 가독성을 위해 미룸).

- 회의 목록(새로고침·삭제), 펼치기/접기, 전체 스크립트 보기/접기(`transcript`), `analyze_meeting`
  실행+폴링(`usePollingSkillRunner`), 이미 저장된 분석 재조회(`getAnalysis`, 다시 분석 안 돌림),
  Action Item 승인/거절/일괄 승인(`reviewActions`) 전부 연결.
- **실제 로컬 backend에 테스트 회의를 만들어(`POST /api/v1/meetings`, curl) 검증**: 목록에
  "Stage5 검증용 회의"가 날짜(18 AUG)·"분석 대기" 배지와 함께 정상 표시 → 펼치기 → "전체
  스크립트 보기" → 실제 서버 응답("아직 최종 스크립트가 없습니다...") 그대로 렌더 → "회의 분석
  실행" 버튼도 정상 노출. `analyze_meeting` 자체 실행(STT+LLM)은 실제 녹음 오디오가 있어야
  의미가 있어 6단계(회의 녹음) 이식 후 실제 업로드와 함께 재검증하기로 하고 이번엔 버튼 노출까지만
  확인했다. 검증에 쓴 테스트 회의는 확인 후 삭제(`DELETE`, 204)해 정리했다.
- `tsc -b --noEmit`, `vite build`, `npm run test:video-agent`(75 passed, 회귀 없음) 통과.

### 6단계 구현 완료 (2026-08-18)

`workmate-ui/app/views/Meeting.tsx`(WebSocket 실시간 녹음 + 파일 업로드)와
`lib/audio-pcm16.ts`(리샘플링·PCM16 변환 순수 함수)를 이식했다. **WebSocket 인증이 결정 5의
범위 밖에 있다는 걸 코드로 확인**했다 — `recording_stream.py`의 `_credentials()`는
`_authenticated_user_or_assignee`를 거치지 않고 `Sec-WebSocket-Protocol`의
`bearer.<token>`/`user.<user_id>`만 보는데, **토큰 값 자체는 검증하지 않고 "Bearer 문자열이
비어있지 않은지"만 확인한다**(주석에도 "존재 여부만 확인하는 기존 계약과 같은 수준"이라고
명시돼 있음 — 이 코드가 원래도 약한 인증이었다). 대신 `meeting_repository().get(meeting_id,
user_id)`로 그 회의가 그 `user_id` 소유인지는 확인하므로, REST로 생성할 때 쓴 것과 **같은 고정
`user_id`**를 WebSocket에도 실어 보내야 한다. `internal_chat.py`의 `ASSIGNEE_TO_USER_ID`를
프론트에도 그대로 복제해(`api.ts`의 `resolveAssigneeUserId`) 이름 대신 이미 해석된 id를
Subprotocol에 담아 보낸다 — 두 파일이 어긋나면 회의 녹음이 깨지므로 한쪽을 고치면 다른 쪽도
고쳐야 한다는 주석을 양쪽에 남겼다.

**결정 4(SPA 전환 확인창)도 이번에 실제로 구현**: `RecordingDetailPanel`이 녹음 시작/종료를
`onRecordingChange` 콜백으로 부모(`TaskQuickActions`)에 올려보내고, `TaskQuickActions`는 이걸로
① 자기 자신의 탭 전환(사이드바 안 거치는 이동)을 막고 ② 같은 콜백을 다시 `App.tsx`로 올려보내
사이드바 이동(`handleSectionClick`/`handleChatClick`/`changeAssignee`)까지 막는다 — 이동 자체는
막지 않고 confirm 창만 띄운다(취소하면 그대로 머무름).

**구현 중 실제로 잡은 버그(내가 만든 게 아니라 기존 코드에 있던 것)**: `isRecording` state를
추가하고 나서 `npm run test:video-agent`가 `TaskQuickActions`에서 "Rendered more hooks than
during the previous render"급 오류로 실패했다 — 원인을 보니 `useState(cards[0].id)`가 조건부
`return null` **뒤에** 있어서, `currentChat`이 바뀌며 그 반환문을 타는 렌더와 안 타는 렌더 사이에
Hook 호출 개수가 달라지는 React Hooks 규칙 위반이 이미 있었다(이번에 Hook을 하나 더 추가하면서
비로소 테스트가 이를 잡아냈다). 모든 Hook을 조건부 반환보다 앞으로 옮겨 고쳤다.

- **실제 로컬 backend에 대고 Playwright로 검증**(Chromium `--use-fake-device-for-media-stream`
  으로 가짜 마이크 장치 사용): (1) 파일 업로드 — 합성 WAV 파일을 업로드해 "업로드 완료:
  test-audio.wav (31.3KB)" 확인. (2) **실시간 녹음** — "녹음 시작" 클릭 후 실제 WebSocket
  Handshake가 성공해 "녹음 중" 상태로 전환되는 것까지 확인(핸드셰이크가 실패하면 이 상태
  전환 자체가 안 일어난다 — `resolveAssigneeUserId` 우회가 실제로 동작한다는 증거).
  (3) **결정 4** — 녹음 중 "할 일 관리" 탭을 클릭하면 "녹음 중입니다. 이동하면 녹음이
  종료됩니다. 이동할까요?" confirm이 뜨고, 취소하면 화면이 그대로 "회의 녹음 및 분석"에 머무는
  것까지 확인. (4) "녹음 종료"로 정상 종료. 두 실제 회의(실시간 녹음 1건, 업로드 1건)가 실제
  SQLite에 생성된 것을 `GET /api/v1/meetings`로 확인 후 정리(`DELETE`, 204×2).
- `analyze_meeting` 실제 STT+LLM 실행은 이번엔 검증하지 않았다 — 합성 사인파 WAV라 의미 있는
  전사 결과가 나오지 않는다. 5단계에서 이미 "분석 실행" 버튼 노출은 확인했다.
- `tsc -b --noEmit`, `vite build`, `npm run test:video-agent`(75 passed, Hooks 버그 수정
  포함해 회귀 없음) 통과.

### 7단계 구현 완료 (2026-08-19)

`workmate-ui/lib/proposal-notifications.tsx`(SSE 구독 + 백그라운드 Gmail/Calendar Polling
Context), `lib/proposal-review.ts`, `app/views/Proposals.tsx`를 이식했다. 이 화면만 결정 5의
우회 대상이 아니라 진짜 Google OIDC ID Token이 필요해서(`proposal_api.py`는 그대로 뒀다), 토큰이
없으면 붙여넣기 입력만 보여주는 화면으로 시작한다 — 나머지 6개 화면과 달리 이 화면 하나만
`Get-FreshIdToken.ps1`로 발급받은 토큰이 있어야 열린다.

**범위를 하나 좁혔다**(문서에 이미 기록): 원본은 `ProposalNotificationsProvider`를 앱 Shell
최상단에 마운트해 다른 화면에 가 있어도 SSE가 안 끊겼는데, 여기서는 `제안함` 탭 자신에만
마운트했다 — 그래서 이 탭을 벗어나면 SSE도 끊긴다. 오케스트레이터 Shell 전체에 Provider를 올리는
건 Toast 배치 등 레이아웃 변경이 더 필요해 이후 과제로 남긴다.

**실제 Google 계정으로 완전한 End-to-End 검증**(2026-08-19, `Get-FreshIdToken.ps1`로 실제 ID
Token 발급받아 진행 — 토큰은 검증 후 즉시 파기):

1. 토큰 붙여넣기 → 연결 → `googleAuthApi.status()` 실제 호출로 "내 Google 계정이 연결돼
   있습니다" 정상 표시.
2. **SSE 스트림 실제 연결**: `curl`로 백엔드 자체가 실제 Gmail 기반 제안 데이터를 정상 스트리밍
   하는 것부터 확인했고, 브라우저에서도 최종적으로 "SSE 연결됨"(초록) 확인.
3. **Toast 실시간 알림 동작 확인**: 화면을 연 채로 기다리자 새로 도착한 Calendar 제안("신규
   입사자 환영회", 오늘 일정)에 대해 우측 상단에 실제 Toast가 떴다 — `shouldToastProposal`의
   "Calendar는 당일 것만" 기준이 실제로 동작.
4. 제안 카드 6장이 실제 Gmail·Calendar 데이터로 채워짐(MAIL/CALENDAR 배지, 수신·일정 날짜,
   제목·담당자·마감일·우선순위 입력 필드까지 전부 실데이터) — "무시" 클릭 → 실제
   `POST .../calendar-task-proposals:review` 호출 → 카드 6장→5장으로 정상 감소.

**구현 중 실제로 잡은 버그(dev 서버 한정, 코드 버그 아님— 원인 특정까지 완료)**: `npm run dev`
(Vite dev 서버, `localhost:5173`)에서는 토큰을 넣고 연결해도 "SSE 연결 안 됨"에 계속 멈춰
있었다. 네트워크 트레이스로 보니 `GET .../notifications/stream` 요청이 **두 번** 나가고
첫 번째는 `net::ERR_ABORTED`, 두 번째는 응답 자체가 안 옴 — `main.tsx`가 `<StrictMode>`로
감싸여 있어 React가 개발 모드에서만 Effect를 마운트→정리→재마운트로 두 번 태우는데, 이때
`streamSse`의 `AbortController`가 첫 연결을 끊는 타이밍과 겹치며 두 번째 연결이 걸린 것으로
보인다. **`npm run build && vite preview`(운영 빌드 — StrictMode 이중 호출이 프로덕션에서는
꺼짐)로 테스트하니 요청이 한 번만 나가고 즉시 연결됐다** — 코드 결함이 아니라 dev 서버에서만
보이는 React 개발 모드 특성으로 확인, 실사용(운영 빌드)엔 영향 없다. 이 화면을 로컬에서 확인할
땐 `npm run dev`가 아니라 `npm run build && npx vite preview`를 쓰라고 담당자 요청 목록(R3)에
남겨둔다.
- `tsc -b --noEmit`, `vite build`, `npm run test:video-agent`(75 passed, 회귀 없음) 통과.

## 화면별 상세 이식 계획

| 화면 | 오케스트레이터 신규 파일(안) | 필요 `workmate-agent` 엔드포인트 | 통신 방식 |
| --- | --- | --- | --- |
| 오늘 브리핑 | `frontend/src/workmate/Briefing.tsx` | `daily_briefing`, `rank_priorities` 스킬챗 | REST(동기) |
| 주간 업무보고 | `frontend/src/workmate/Report.tsx` | `weekly_report` 스킬챗 | REST(동기) |
| 할 일 관리 | `frontend/src/workmate/Tasks.tsx` | `GET/POST /api/v1/tasks`, `PATCH/DELETE /api/v1/tasks/{id}` | REST CRUD |
| 회의 녹음 | `frontend/src/workmate/Meeting.tsx` | `POST /api/v1/meetings`, `POST /api/v1/meetings/{id}/recordings`, `WS /api/v1/meetings/{id}/recording-stream` | REST + WebSocket |
| 회의 관리 | `frontend/src/workmate/Archive.tsx` | `GET /api/v1/meetings/{id}/analysis`, `analyze_meeting` 스킬챗(+폴링), `POST /api/v1/meetings/{id}/actions:review` | REST + 스킬챗 폴링 |
| 회의록 검색 | `frontend/src/workmate/Search.tsx` | `POST /api/v1/meetings/search`(`search_meetings`) | REST(동기) |
| 제안함 | `frontend/src/workmate/Proposals.tsx` | `GET /api/v1/notifications/stream`(SSE), `dev/gmail-sync`, `dev/calendar-sync`, 승인/무시 REST | REST + SSE |

각 화면의 정확한 요청·응답 필드는 이 표에 다시 옮겨 적지 않고 [15번 문서](15-workmate-ui-screens-reference.md)의
해당 절(위 "목표" 표의 링크)을 그대로 구현 시점 기준으로 삼는다.

## 프론트 디렉터리 구조(안)

기존 `video-agent/` 폴더(`frontend/src/video-agent/*` — `api.ts`, 컴포넌트, `api.test.ts`)와 같은
패턴으로 `workmate/` 폴더를 신설한다:

```
frontend/src/workmate/
  api.ts                 # workmate-agent를 직접 호출하는 함수 모음 (workmate-ui/lib/workmate-api.ts 이식)
  api.test.ts
  Briefing.tsx
  Report.tsx
  Tasks.tsx
  Meeting.tsx
  Archive.tsx
  Search.tsx
  Proposals.tsx
  ProposalsDetailPanel.tsx  # 신규 5번째 탭 — MainUiPanels.tsx의 TaskQuickActions 분기에 추가
```

## 메뉴 확장(1단계) 변경 지점

두 nav를 하나로 합치지 않으므로, `activeSection`(오늘 브리핑/주간 업무보고)과 `TaskQuickActions`의
`selectedId`(할 일 관리 등)로 나뉜 지금의 상태 분기 구조는 그대로 둔다 — `TaskQuickActions`의
`cards` 배열에 항목 하나만 추가하면 된다.

- [ui-variant.ts](../AI-agent_game_platform/main_agent/frontend/src/ui-variant.ts) `quickActions`
  배열 — 기존 4개 항목은 그대로 두고 `제안함` 1개만 추가해 5개로.
- [MainUiPanels.tsx](../AI-agent_game_platform/main_agent/frontend/src/MainUiPanels.tsx)의
  `TaskQuickActions`(`cards` 배열)에 `제안함` 카드를 추가하고, 그 화면을 렌더할
  `ProposalsDetailPanel`(신규, `Proposals.tsx` 이식 대상)을 다른 4개 패널(`TaskDetailPanel` 등)과
  같은 방식으로 분기에 연결한다. `UpdatedReportNav`(`오늘 브리핑`/`주간 업무보고`)는 구조를
  바꾸지 않는다 — `ReferenceBriefingPanel`/`WeeklyReportPanel`의 내용만 실제 데이터로
  교체한다(3단계).
- [App.tsx](../AI-agent_game_platform/main_agent/frontend/src/App.tsx#L420) 셸 렌더 로직은
  `TaskQuickActions` 쪽 분기에 다섯 번째 케이스(`제안함`)만 추가하면 된다 — `activeSection`/
  `activeChat` 이원 구조 자체는 유지.
  <!-- 25번 문서 계획 3: 위 세 링크는 main_agent/ 이동 후 경로로 갱신(2026-08-19). 이 문서
  나머지 본문의 `AI-agent_game_platform/frontend`·`backend` 언급은 그 시점(모노레포 재구성
  이전) 기준 그대로 남겨뒀다 — 지금 실제 위치는 25번 문서 "3. 19~24번 문서의 경로 표기가
  지금은 틀렸다"의 대조표 참고. -->

## 검증 계획

- 프론트: `frontend/package.json`에 `test:workmate` 스크립트 추가(기존 `test:video-agent`
  패턴 — vitest로 순수 로직·컴포넌트 테스트). 백엔드 테스트는 추가하지 않는다(옵션 A 제외로
  backend 변경 자체가 없음).
- 수동 검수: [13번 문서](13-manual-verification-guide.md)와 같은 형식으로 화면별 체크리스트를
  이 프로젝트에도 추가(7개 화면 × 성공/실패/빈 상태).

## 리스크와 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| `workmate-agent` 대상 저장소 불확실(결정 2) | 잘못된 코드베이스 기준으로 작업할 위험 | 착수 전 확인 |
| 옵션 B의 OIDC 토큰 재입력 UX가 실사용에 방해될 정도로 나쁨 | 사용성 저하가 "원칙"과 충돌 | 이 경우에만 "원칙" 자체를 사용자와 재검토(A 재고려는 backend 변경 승인이 먼저 필요) |
| Windows 포트 예약 범위(7962-8061, 5158-5257 등) | 로컬 개발 중 반복적으로 포트 재조정 필요 | 결정 3에서 실제 포트 확정 후 문서화 |
| 회의 녹음 SPA 전환 시 세션 자동 종료(결정 4) | 사용자가 의도치 않게 녹음을 중단시킬 수 있음 | 6단계에서 이동 확인창 등으로 처리 |
| 프론트 변경도 담당자 요청이 필요(원칙) | 로컬 검증까지 끝나도 실제 반영엔 팀원 협조가 또 필요 | 아래 "오케스트레이터 담당자에게 전달할 요청 목록"에 모아 20번 문서와 같은 방식으로 한 번에 요청 |

## 오케스트레이터 담당자에게 전달할 요청 목록

20번 문서의 "오케스트레이터 담당자에게 전달할 요청 목록"(R1~R6)과 같은 패턴이다 — 이 계획을
구현하면서 로컬 clone에 적용·검증한 프론트 변경 사항을 여기 모아 두고, 나중에 한 번에 담당자에게
요청한다.

| # | 변경 내용 | 위치 | 현재 상태 |
| --- | --- | --- | --- |
| R1 | "Workmate AI" 내부 상단 탭에 `제안함`(5번째) 추가 — 자리만 만들고 데이터는 목업 유지 | `frontend/src/ui-variant.ts`(`quickActions` 배열), `frontend/src/MainUiPanels.tsx`(`TaskQuickActions`의 `cards` 배열 + 신규 `ProposalsDetailPanel`) | 로컬 clone에 적용, `tsc -b`·`vite build`·`npm run test:video-agent`(65 tests) 통과, Playwright로 실제 렌더 스크린샷까지 확인 완료 |
| R2 | `workmate-agent` 호출마다 `X-Workmate-Assignee: encodeURIComponent(assignments["Workmate 담당자"])` 헤더 추가, `할 일 관리`/`회의 녹음`/`회의 관리`/`회의록 검색`/`오늘 브리핑`/`주간 업무보고`를 실데이터로 교체, `제안함`(SSE+Gmail/Calendar) 신규 탭 추가 | `frontend/src/MainUiPanels.tsx`, `frontend/src/App.tsx`, 신규 `frontend/src/workmate/*`(api·types·format·use-skill·audio-pcm16·proposal-notifications·proposal-review) | 2~7단계 전부 로컬 clone에 적용, 실제 로컬 backend에 Playwright로 왕복 검증 완료(아래 각 단계 "구현 완료" 참고) — 담당자에게 실제 반영 요청 대기 |
| R3 | `제안함` 화면은 로컬에서 `npm run dev`가 아니라 `npm run build && npx vite preview`로 확인할 것 — `npm run dev`(StrictMode 이중 마운트)에서는 SSE 연결이 안 된다(코드 결함 아님, 7단계 "구현 완료" 참고) | 검증 방법 안내(코드 변경 아님) | 담당자에게 알림 목적으로 등록 |
| R4 | `제안함`의 "Google ID Token 붙여넣기" 게이트를 제거하고 나머지 6개 화면과 같은 담당자 헤더 인증으로 완화(2026-08-19, 사용자 확인 — 로컬 전용 프로젝트 서버라 리스크 감수, 위 "2026-08-19 후속" 절 참고) — 이제 입력창 없이 바로 열리고, "Google 계정 연결" 버튼을 눌러야만 진짜 구글 로그인 팝업이 뜬다 | `frontend/src/workmate/api.ts`(`proposalsApi`·`devGmailSyncApi`·`devCalendarSyncApi`·`googleAuthApi`·`streamSse` 인증 모드), `frontend/src/workmate/proposal-notifications.tsx`(`token` → `assignee` 구독 조건), `frontend/src/MainUiPanels.tsx`(`ProposalsDetailPanel`의 토큰 게이트 제거), `frontend/src/workmate/api.test.ts` | 로컬 clone에 적용·검증 완료 — `tsc --noEmit`·`vite build` 클린, `vitest run src/workmate/api.test.ts` 10개 PASS. 짝을 이루는 workmate-agent 쪽 변경(`_authenticated_user_or_assignee` 전환, 12곳)은 이미 우리 저장소에 반영·전체 테스트(439개) 통과 완료 — 오케스트레이터 쪽만 반영되면 바로 동작한다 |
| R5 | `주간 업무보고`의 "이전 주"/"다음 주"/"Markdown 복사" 버튼이 요약 문단 길이에 따라 짜부러들어 "이전 주" 같은 두 글자가 세로로 줄바꿈돼 보이는 버그(2026-08-19, 실사용 중 발견) — `workmate-ui`의 `Report.tsx`는 이미 겪고 고쳐둔 문제인데 이식 시 그 CSS 수정이 누락됐었다 | `frontend/src/MainUiPanels.tsx`(`WeeklyReportPanel`의 헤더 — 왼쪽 요약에 `minWidth:0`, 버튼 그룹에 `flexShrink:0`, 버튼마다 `whiteSpace:"nowrap"` 추가) | 로컬 clone에 적용 완료, `tsc --noEmit` 클린 |

## 다음 단계

1. ~~결정 1~5~~ — ✅ 전부 완료(위 각 결정 절 참고).
2. ~~1~8단계 구현·검증~~ — ✅ 전부 완료(2026-08-19). `workmate-agent`(우리 저장소)는 실제로
   커밋 가능한 상태로 로컬에 반영돼 있다. 오케스트레이터(`AI-agent_game_platform`) 쪽 변경은
   "원칙"에 따라 로컬 clone에만 적용·검증했고, 실제 저장소 반영은 아직이다.
3. **남은 유일한 작업**: 위 "오케스트레이터 담당자에게 전달할 요청 목록"(R1~R5)을 오케스트레이터
   담당자에게 전달해 그 저장소에 실제로 반영해달라고 요청한다(20번 문서의 R1~R10와 같은 흐름).
4. 반영 후에는 [21번 문서](21-orchestrator-workmate-manual-verification-checklist.md)의 "사람이
   볼 것" 칸(실제 마이크·실제 회의 분석·Postgres 붙은 회의록 검색·승인 흐름 등, 이번 자동 검증이
   못 다룬 항목)을 담당자나 사용자가 직접 검수한다.
