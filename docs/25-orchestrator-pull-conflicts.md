# 오케스트레이터 재확인 — pull 이후 충돌·드리프트 기록

작성일: 2026-08-19
상태: ✅ 조사·계획·로컬 반영·검증 완료 — 19~24번 문서로 이식 작업을 하는 동안
`AI-agent_game_platform`(오케스트레이터) 저장소 자체가 팀원 쪽에서 계속 바뀌었고, 그 결과 지금
로컬 clone(`c:\dev\workmate\AI-agent_game_platform`)에 반영된 상태와 19~24번 문서가 전제한 상태
사이에 생긴 차이를 정리했다. "해결 방법 및 계획" 절의 계획 1·2·5(docker-compose 수정)·계획 3
(문서 경로 표기)·계획 4(origin 커밋 merge)까지 전부 **로컬 clone에 실제로 반영하고 `docker
compose build`/`up`/`curl`로 직접 검증**했다 — 결과는 아래 "완료 보고" 절 참고.
`AI-agent_game_platform`은 팀원 소유 저장소라 실제 반영은 여전히 담당자에게 전달해야 한다(각
계획의 "담당자 전달용 요약" 참고) — 이 세션에서 한 건 로컬 clone과 이 저장소(`c:\dev\workmate`)
소유 문서(19~24번)뿐이고, 팀원 저장소로 push하지는 않았다.

## 결론 먼저

- **아직 풀리지 않은 Git merge conflict는 없다.** 로컬 clone(`test/unified-latest`,
  `f9db8ca`)에 conflict marker(`<<<<<<<`)가 남은 파일은 0건이고, 실제 3-way 병합은 이미
  팀원(`Gudą`, `projectares777@gmail.com`)이 `59ea668` 커밋(아래 "커밋 59ea668" 절 참고)으로
  완료해 로컬에 들어와 있다.
- **그 병합이 19~24번 문서가 만든 기능을 깨뜨리지는 않았다** — `unseenCount` 배지, 카드
  snippet·reason, `X-Workmate-Assignee` 인증, Proposals 탭 스코프 SSE, `owner`+`pending_action`
  동시 저장까지 전부 현재 코드에 그대로 남아 있음을 직접 확인했다(아래 "검증한 항목" 참고).
- **다만 5가지는 실제로 조치가 필요했다(→ 모두 이 문서 작성 세션 안에서 로컬 clone에 반영·검증
  완료, 아래 "완료 보고" 참고)** — 원래 우선순위 순(뒤 항목이 앞 항목에 의존):
  1. `main_agent/docker-compose.yml`의 `workmate-agent` 빌드 경로가 모노레포 재구성 이후
     **조용히 엉뚱한 곳을 가리키고 있었다** — 실제 저장소(`c:\dev\workmate\workmate-agent`,
     439개 테스트 통과분) 대신 `AI-agent_game_platform` 안에 남아있는 9개 파일짜리 옛 스텁을
     빌드하고 있었다.
  2. REST 화면(오늘 브리핑/할 일 관리/회의/제안함 등 — 19~24번 문서가 실제로 이식한 화면
     전부)이 쓰는 포트 8100이 컨테이너에서 호스트로 게시돼 있지 않았다 — 1번을 고쳐도 이
     문제는 별도로 남는다.
  3. `docker-compose`의 workmate-agent 서비스가 Gmail/Calendar 관련 env·volume을 여전히
     빠뜨리고 있었다(병합 당시엔 맞는 판단이었지만 지금은 아니다).
  4. 19~24번 문서의 경로 표기가 전부 구조 변경 전 기준이라 지금은 틀려 있었다.
  5. 로컬 clone이 origin보다 커밋 1개 뒤처져 있었다(fetch만 되고 merge 전).
  구체적 수정 방법·실제 반영 결과는 아래 "해결 방법 및 계획"·"완료 보고" 절 참고.

## 배경 — 왜 이 문서가 필요한가

19번 문서(작성 2026-08-17, 8단계 전부 완료 2026-08-19)는 `c:\dev\workmate\AI-agent_game_platform`을
대상으로 "오케스트레이터는 팀원 소유 저장소라 로컬 clone에서 구현·검증까지만 하고, 실제 반영은
담당자에게 요청 목록으로 전달한다"는 전제로 작업했다. 그런데 이 작업이 진행되는 동안
오케스트레이터 저장소 자체가 **같은 로컬 clone 안에서** 팀원 쪽 커밋으로 계속 앞서나갔다 —
`main_agent`/`dev_agent`/`qna_agent`/`video_agent`/`workmate-agent`를 하나의 모노레포로 합치는
대규모 재구성(`8e3400e`), owner별 채팅 세션 분리, video-agent 복구 등. 이 문서는 그 드리프트를
`git log`/`git fetch`/코드 대조로 실제 추적한 결과다.

## 타임라인 (실제 커밋 기록 기준)

```
313ce66 (2026-08-18 11:07) ← 19번 문서 착수 시점 기준 커밋(사용자의 feat/workmate-ui-port 브랜치의 베이스)
  │
  ├─ 사용자 브랜치: feat/workmate-ui-port
  │    └─ 57be15b (2026-08-19 13:55) "feat: port workmate UI per docs/19 plan"
  │       — 19번 문서 2~7단계 전체(제안함 포함) 커밋 1개로 압축
  │
  └─ 오케스트레이터 쪽 브랜치(팀원, 동시 진행)
       ├─ 344144b (08-18 12:51) feat: separate agent chats by owner
       ├─ 2f2b766 / 5f74108 (08-18 16:00) 후속 수정
       ├─ 8e3400e (08-18 16:56) feat: unify 5개 서비스를 모노레포로 통합
       │   → 이 시점부터 frontend/backend 경로가 main_agent/frontend, main_agent/backend로 이동
       └─ f3157bd (08-19 14:54) fix: restore video-agent + owner-session fixes lost in monorepo unify

  59ea668 (08-19 15:16) ← f3157bd와 57be15b를 3-way 병합("Gudą"가 수행)
  c419def / f9db8ca (08-19 15:43~15:52) 로컬 REST stub 추가/제거
  d49d07a  origin/main으로 PR #1 병합(로컬 test/unified-latest는 아직 이 지점까지 안 감)
  a8ec0a7 (08-19 16:39) docs+fix: README, router.py 경고 — origin에는 있음, 로컬엔 fetch만 됨
```

## 커밋 59ea668 — 실제로 무엇을 병합했나

`git show 59ea668`로 확인한 병합 커밋 메시지 요지(팀원 "Gudą"가 직접 남긴 설명):

> Her branch(사용자의 `feat/workmate-ui-port`)는 모노레포 재구성 이전의 오래된 커밋(`313ce66`) 위에
> 만들어져 있었다. 단순 pull이 아니라 실제 3-way 병합(`git merge-tree`, 사용자 브랜치 트리를
> `main_agent/` 아래로 가상 이동시켜 경로를 맞춤)으로 손으로 충돌을 풀었다.

병합에서 실제로 손으로 조정한 지점 3곳(문서화 목적으로 원문 그대로 옮김):

1. **`conversation_store.py` / `main.py`**: `ConversationStore.append/list_messages`와 채팅
   엔드포인트가 `owner`(세션 스코핑, 오케스트레이터 쪽 변경)와 `pending_action`(스킬 실행
   확인/취소, 사용자 쪽 변경)을 **함께** 갖도록 병합.
2. **`App.tsx`**: owner-scoped 채팅/작업 저장소(`agentWorkStorageKey`), Policies 사이드바
   서브메뉴, `PreviewPanel` currentChat 수정(오케스트레이터 쪽)은 유지하면서, 사용자 쪽의
   pending-action 채팅 UI·`rebuildChatFromHistory`·회의 녹음 중 이동 확인창
   (`confirmLeaveRecording`, 19번 문서 결정 4)을 추가.
3. **`docker-compose.yml`**: `game-qa-agent`/`kosa-front`(오케스트레이터 쪽, 사용자 버전엔 둘 다
   빠져 있었음)와 실제 video-agent 연결(오케스트레이터 쪽)은 유지하고 `workmate-agent`의
   `APP_BASE_URL` env var(사용자 쪽)는 받아들였다. **사용자 쪽이 추가한 `GOOGLE_TOKEN_FILE` env
   var + `.runtime/`·google-oauth-test 볼륨 마운트는 뺐다** — 병합 당시 `../workmate-agent`
   체크아웃에 그 기능(Calendar/Gmail 실시간 신호)의 코드가 없다고 판단했기 때문(`.env.example`에
   `WORKMATE_SERVICE_TOKEN`/`APP_BASE_URL`만 있다고 명시). "별도로 사용자의 최신 workmate-agent를
   pull해온 뒤 다시 추가하라"는 TODO 주석을 남겼다.
   `MainUiPanels.tsx`는 3-way 병합이 깨끗하게 됐고, 자동 병합이 만든 `useEffect` import 중복 1건만
   손으로 고쳤다.

검증 결과로 남긴 수치: Backend 79/79 관련 테스트 통과(무관한 2건 실패는 다른 팀원 로컬 경로
하드코딩 문제), Frontend `tsc -b` 클린, vitest 76/76 통과(그중 10개가 사용자의
`workmate/api.test.ts` 등 신규분), `docker compose config` 통과.

## 지금 시점에 실제로 문제가 되는 항목

### 1. (신규 발견, 가장 심각) `main_agent/docker-compose.yml`의 workmate-agent 빌드 경로가 옛 스텁을 가리킴

`AI-agent_game_platform`의 `docker-compose.yml`은 원래 저장소 루트에 있었고, 19번 문서 "결정 2"가
이때 `build: ../workmate-agent`를 검증해 "`AI-agent_game_platform` 기준 상위 경로라 정확히
`c:\dev\workmate\workmate-agent`(우리 저장소)와 같다"고 확정했다. 그런데 `8e3400e`(모노레포 통합)가
이 파일을 **한 단계 더 안쪽인 `main_agent/docker-compose.yml`로 옮겼다** — `video_agent`/
`dev_agent`/`qna_agent`는 같이 `AI-agent_game_platform/` 아래로 이동해 들어와서 `../video_agent`
등은 여전히 맞게 가리키지만(확인함, 아래 표), **`workmate-agent`만 원래대로 외부(팀 경계 밖) 저장소로
남아 있어 `../workmate-agent`가 이제 한 단계 덜 올라간다**:

| 서비스 | `build:` 값 | `main_agent/docker-compose.yml` 기준 실제로 가리키는 곳 | 맞는지 |
| --- | --- | --- | --- |
| video-agent | `../video_agent` | `AI-agent_game_platform/video_agent`(모노레포 통합으로 들어온 내부 디렉터리) | ✅ 맞음 |
| dev-agent | `../dev_agent` | `AI-agent_game_platform/dev_agent` | ✅ 맞음 |
| game-qa-agent | `../qna_agent` | `AI-agent_game_platform/qna_agent` | ✅ 맞음 |
| **workmate-agent** | `../workmate-agent` | `AI-agent_game_platform/workmate-agent` | ❌ **틀림** — 실제로 필요한 건 `c:\dev\workmate\workmate-agent` |

직접 확인한 사실: `AI-agent_game_platform/workmate-agent/`가 실제로 존재하고 git에 커밋돼 있다
(`app.py`, `compose.yaml`, `README.md`, `requirements.txt`, `smoke_test.py` 등 **9개 파일뿐인 초기
스텁** — `proposal_api.py`, `google_credentials.py` 같은 지금 쓰는 코드가 전혀 없다). 이 디렉터리가
모노레포 통합 훨씬 이전 시점(19번 문서 "결정 2"가 "실제 파일시스템에 존재하지 않는다"고 확인했던
`workmate-agent-main`류 죽은 참조와 비슷한 성격)에 커밋된 채 남아 있다가, 이번 경로 이동으로
`../workmate-agent`가 우연히 이 스텁과 다시 맞아떨어지게 된 것으로 보인다 — **즉 참조 오류가 나는 게
아니라 조용히 "빌드는 되지만 완전히 다른(구식) 코드"가 뜬다**는 점이 더 위험하다(에러였다면 바로
드러났을 텐데, 지금은 `docker compose build`가 성공한다).

`env_file: "../workmate-agent/.env"`도 같은 이유로 잘못된 경로다(존재하지도 않는
`AI-agent_game_platform/workmate-agent/.env`를 가리킴 — 확인 결과 미존재, 파일 없으면 Compose가
조용히 빈 env로 넘어간다).

**더 중요한 사실**: 이 스텁(`workmate-agent/app.py`)은 `/a2a/message:send`·`/health/ready`를
실제로 구현하고 있어서 main-agent의 healthcheck·A2A 호출이 전부 "성공"한다 — 다만 스킬 실행
결과가 전부 하드코딩된 Mock이다(`daily_briefing`/`weekly_report`/`analyze_meeting`/
`search_meetings`/`rank_priorities` 5개 skill_id만 알고, 어떤 요청이 와도 항상
`"Mock 호출에 성공했습니다"` 텍스트와 `"mock": true` 데이터를 즉시 `TASK_STATE_COMPLETED`로
반환). 즉 **`docker compose`로 오케스트레이터 전체를 띄워 쓰는 한, "Workmate AI" A2A
스킬챗(main-agent가 라우팅하는 채팅)은 지금까지 한 번도 실제 workmate-agent 로직을 탄 적이
없다** — 실제 코드는 `../workmate-agent/.runtime`에 쌓인 진짜 Task/Meeting 데이터를 근거로
LLM이 응답을 생성하지만(`workmate-agent/app/a2a/runtime.py`, `TaskState.TASK_STATE_SUBMITTED`로
시작하는 비동기 실행), Mock은 그 어느 것도 하지 않는다. 계획 1을 적용하면 이 부분이 통째로
바뀐다 — 아래 "다른 에이전트에 미치는 영향" 참고.

### 2. (신규 발견) REST 화면은 A2A 컨테이너와 완전히 다른 경로 — 포트가 호스트에 게시돼 있지 않았다

`a8ec0a7`(계획 4로 받은 커밋)의 새 README가 정확히 이 문제를 이미 문서화해뒀다:

> 업무지원(Workmate AI) — `workmate-agent` 서비스, 내부 Port 8001, 호스트 노출 **미노출**,
> 상태: "A2A Mock(`app.py`, 고정 5개 스킬만 흉내) — 실제 백엔드는 별도"
> "**workmate-agent 실제 백엔드(포트 8100) 미구현**: 프론트엔드의 `main_agent/frontend/src/
> workmate/` 모듈(오늘 브리핑, 주간 업무보고, 할 일 관리, 회의 녹음/분석, 제안함)은 Docker의
> `workmate-agent` 컨테이너(포트 8001, A2A 프로토콜용 Mock)가 아니라 **완전히 별도의 REST
> API**(`http://127.0.0.1:8100`)를 호출합니다 ... 그 전까지는 해당 화면들이 'Failed to fetch'
> 에러를 띄웁니다."

코드로 직접 확인한 실제 구조는 README의 "미구현"이라는 표현보다 조금 더 좋은 소식이다:

- `workmate-agent/app/main.py`(실제 저장소)는 **A2A 라우트와 REST 라우트를 전부 같은 FastAPI
  앱(`app.main:app`) 하나에 `include_router`로 합쳐둔다** — `task_router`, `proposal_router`,
  `meeting_router`, `transcript_router`, `action_item_router`, `dev_gmail_sync_router`,
  `dev_calendar_sync_router`, `google_oauth_web_router` 등 전부. 즉 REST API가 "미구현"인 게
  아니라 **이미 구현돼 있고, A2A와 같은 프로세스·같은 포트(컨테이너 기준 8001)에서 같이
  떠 있다** — 별도 프로세스가 필요한 게 아니다.
- 진짜 원인은 `main_agent/frontend/src/workmate/api.ts`가 `WORKMATE_API_BASE_URL =
  "http://127.0.0.1:8100"`을 **하드코딩**하고 있는데(19번 문서 결정 3 — Windows 예약 포트
  범위 `7962-8061` 때문에 로컬에서 `python -m app.server`를 직접 띄울 때 8001→8100으로
  옮긴 이력에서 비롯된 값), `docker-compose.yml`의 `workmate-agent` 서비스는 지금
  `expose: ["8001"]`만 쓴다는 데 있다. Compose의 `expose:`는 **같은 네트워크의 다른 컨테이너**
  (main-agent가 `WORKMATE_AGENT_URL=http://workmate-agent:8001/a2a`로 부르는 용도)에만 열리고
  **호스트(브라우저)에는 열리지 않는다** — `ports:`로 게시해야 호스트에서 접근 가능하다. 지금
  설정엔 `ports:`가 아예 없다.
- 즉 계획 1(빌드 경로 수정)만으로는 REST 화면(Task/Meeting/제안함/오늘 브리핑/주간 업무보고/
  검색 — 19~24번 문서가 실제로 이식한 화면 전부)의 "Failed to fetch"가 안 고쳐진다 — 포트
  게시가 별도로 필요하다. 아래 "계획 5"에서 다룬다.

### 3. docker-compose의 Gmail/Calendar 설정 누락 — 병합 당시 판단이 지금은 틀렸다

병합 커밋의 전제("`../workmate-agent`에 Gmail/Calendar 기능 코드가 없다")를 지금 코드로 직접
재확인했다:

- `workmate-agent/app/workflows/daily_briefing.py`, `assistant_skills.py`,
  `dev_gmail_sync_api.py`, `dev_calendar_sync_api.py` 전부 `GOOGLE_TOKEN_FILE` env var를 읽는다
  (공유 계정 폴백 경로).
- `workmate-agent/app/repositories/google_credentials.py`(사용자별 OAuth 자격 증명 DB 저장소,
  19번 문서 "결정 5" 채택안의 "Google 계정 연결" PKCE 흐름이 쓰는 실제 코드)도 이미 존재한다.
- 즉 **이 기능은 이제 실제로 존재한다** — 병합 당시엔 맞았던 판단이 지금은 stale하다.

그런데 `main_agent/docker-compose.yml`의 `workmate-agent` 서비스 블록은 여전히 그 TODO 주석과
함께 `GOOGLE_TOKEN_FILE`도, `.runtime/` 볼륨 마운트도 없는 상태 그대로다(`build: ../workmate-agent`,
`env_file: ../workmate-agent/.env`, `environment:`는 `WORKMATE_SERVICE_TOKEN`/`APP_BASE_URL`
둘뿐). **`docker compose`로 오케스트레이터 전체를 띄우는 경로로 제안함(Gmail/Calendar 동기화)을
쓰려는 사람은 지금 이 설정으로는 `GOOGLE_TOKEN_FILE` 폴백이 동작하지 않는다.** (다만 19~24번
문서가 실제로 검증한 방식은 `docker compose`가 아니라 `uv run python -m app.server`로 띄운
로컬 backend였기 때문에, 그 검증 결과 자체는 이 갭의 영향을 받지 않는다 — 지금까지의 증빙은
유효하다.)

또한 `.runtime/`(SQLite 상태 파일들: `tasks.sqlite3`, `google_credentials.sqlite3`,
`ignored_proposals.sqlite3` 등) 자체에 대한 볼륨 마운트도 이 서비스 블록엔 없다 — `docker
compose`로 띄우면 컨테이너 재시작마다 이 데이터가 통째로 사라진다는 뜻인데, 이건 이번 pull과
무관하게 원래도 없던 설정이라 "새로 생긴 충돌"은 아니다(참고용으로만 기록).

### 4. 19~24번 문서의 경로 표기가 지금은 틀렸다

19~21, 23~24번 문서는 전부 `AI-agent_game_platform/frontend/...`,
`AI-agent_game_platform/backend/...` 형태로 경로를 적었다(예: "`AI-agent_game_platform/frontend/
src/assignee.ts`", "`MainUiPanels.tsx`"). 이건 `8e3400e`(모노레포 통합, 2026-08-18) **이전** 구조
기준이다. 지금 실제 파일 위치는:

| 문서가 적은 경로 | 실제 현재 경로 |
| --- | --- |
| `AI-agent_game_platform/frontend/src/MainUiPanels.tsx` | `AI-agent_game_platform/main_agent/frontend/src/MainUiPanels.tsx` |
| `AI-agent_game_platform/frontend/src/App.tsx` | `AI-agent_game_platform/main_agent/frontend/src/App.tsx` |
| `AI-agent_game_platform/frontend/src/assignee.ts` | `AI-agent_game_platform/main_agent/frontend/src/assignee.ts` |
| `AI-agent_game_platform/frontend/src/workmate/*` | `AI-agent_game_platform/main_agent/frontend/src/workmate/*` |
| `AI-agent_game_platform/backend/...` | `AI-agent_game_platform/main_agent/backend/...` |

참고로 저장소 루트에 지금도 `frontend/`, `backend/` 디렉터리가 존재하지만(git status상 미추적),
내용을 확인해보니 소스 코드가 아니라 로컬 개발 중 남은 로그·런타임 파일(`.runtime-dev.log`,
`.pytest_cache` 등)뿐이다 — 실제 코드가 아니므로 혼동하지 말 것. 19~24번 문서를 실제 코드
확인용으로 다시 열어볼 사람은 이 표를 참고해 `main_agent/` 아래에서 찾아야 한다. (이 문서
자체는 경로를 고치지 않는다 — 기록 목적)

### 5. 로컬 clone이 origin보다 1커밋 뒤처져 있음(fetch만 됨, merge 안 함)

이 문서 작성 중 `git fetch origin`을 실행해 확인:

```
f9db8ca..a8ec0a7  feat/unified-multi-agent-platform -> origin/feat/unified-multi-agent-platform
```

`a8ec0a7`("docs+fix: root README covering all .env keys, warn on router/qna_agent model
collision", `Gudą`, 2026-08-19 16:39)는 `README.md`와 `main_agent/backend/app/router.py` 2개
파일만 건드려 **workmate 통합 파일과는 겹치지 않는다** — 병합 시 실제 conflict가 날 여지는
없다. 다만 이 커밋이 명시적으로 문서화한 내용 하나는 실사용에 바로 관련된다:

> `WORKMATE_SERVICE_TOKEN`은 두 서비스(`main_agent`, `workmate-agent`)가 **서로 다른 `.env`
> 파일**을 읽기 때문에 자동으로 동기화되지 않는 유일한 토큰이다 — `main_agent/.env`와
> `workmate-agent/.env` 양쪽에 **같은 값**을 직접 맞춰 넣어야 한다.

로컬 clone은 아직 이 커밋을 받지 않은 상태(`test/unified-latest`가 `f9db8ca`에 머물러 있음) —
이 문서는 조사 목적으로 fetch만 했고 merge/pull은 하지 않았다.

## 검증한 항목 — 19~24번 문서가 이식한 기능이 병합 후에도 살아있는지

`main_agent/frontend/src/MainUiPanels.tsx`, `App.tsx`, `workmate/*.ts(x)`,
`main_agent/backend/app/conversation_store.py`를 직접 열어 대조:

- `unseenCount` 배지(19번 문서 "완료 보고" 5번, 24번 문서 5번) — `MainUiPanels.tsx`에 그대로
  렌더링됨, 관련 주석("24번 문서 5번 — ...")도 남아있음.
- 카드 snippet/reason(19번 문서 "완료 보고" 6번, 24번 문서 6번) — 그대로 렌더링됨.
- `X-Workmate-Assignee` 헤더 인증(19번 문서 결정 5, "2026-08-19 후속") — `workmate/api.ts`의
  `apiFetch`/`streamSse`에 `auth: "assignee" | "oidc"` 분기와 `encodeURIComponent` 처리 그대로
  존재.
- `ProposalNotificationsProvider`가 여전히 "제안함" 탭(`ProposalsInner`) 안에만 마운트됨(23번
  문서 2번이 지적한 스코프 제약 — 이번 병합으로 바뀌지 않았음, 여전히 남는 과제).
- `conversation_store.py`의 `owner`+`pending_action` 동시 지원 — 병합 커밋 설명대로 두 값이
  같은 함수 시그니처·같은 테이블에 공존.
- `App.tsx`의 `confirmLeaveRecording`(19번 문서 결정 4) — 그대로 존재, `assigneeName` 변경 시에도
  호출됨(`changeAssignee`).
- `assignee.ts`의 4명 기본값(서선정/배동우/이승현/변해훈, "Workmate 담당자"→서선정) — 19번 문서
  결정 5가 전제한 값과 동일.
- Git 추적 파일 전체에 병합 conflict marker(`<<<<<<<`) 없음.

## 해결 방법 및 계획

다섯 항목을 아래 순서로 처리한다 — 계획 1→2/5가 서로 의존(경로부터 맞아야 볼륨·포트도 맞다),
계획 3·4는 나머지와 독립적으로 아무 때나 처리 가능하다. 전부 **로컬 clone에만 적용** —
`AI-agent_game_platform`은 팀원 소유 저장소라 19번 문서 "원칙"과 동일하게 실제 반영은 담당자에게
요청 목록으로 전달해야 한다(아래 각 항목에 "담당자 전달용 요약" 포함). **이 문서 작성 세션
안에서 계획 1·2·3·4·5를 전부 실제로 적용하고 검증까지 마쳤다 — 실행 결과는 맨 아래 "완료 보고"
절 참고, 아래 각 계획 설명은 실행 당시 세운 원안을 그대로 남겨둔다.**

### 계획 1 — `workmate-agent` 빌드 경로를 실제 저장소로 고정

**수정 대상**: `AI-agent_game_platform/main_agent/docker-compose.yml`

```diff
   workmate-agent:
-    build: ../workmate-agent
+    build: ../../workmate-agent
     expose: ["8001"]
     # OPENAI_API_KEY 등 실 Provider 자격 증명은 workmate-agent 자체 .env를
     # 그대로 재사용한다 - 이 Compose의 .env는 Main Agent 설정만 갖고 있다.
     env_file:
-      - "../workmate-agent/.env"
+      - "../../workmate-agent/.env"
```

- `main_agent/docker-compose.yml` 위치 기준 `../../workmate-agent`가
  `c:\dev\workmate\workmate-agent`로 정확히 해석됨을 경로 계산으로 확인했다(`main_agent/` →
  `AI-agent_game_platform/` → `c:\dev\workmate\` → `workmate-agent`).
- **부작용 없음 확인**: `video-agent`/`dev-agent`/`game-qa-agent`는 이제 내부 디렉터리를
  가리키므로 건드리지 않는다(건드리면 오히려 깨짐).
- `AI-agent_game_platform/workmate-agent/`(9개 파일짜리 옛 스텁)는 이 수정 후에는 어디서도
  참조되지 않는 죽은 디렉터리가 된다 — 지우는 건 팀원 저장소 정리 영역이라 이 계획에는 포함하지
  않고, 존재만 기록해둔다(계속 헷갈릴 여지가 있으니 담당자 전달 시 같이 언급할 것).
- **검증**: `cd main_agent && docker compose build workmate-agent` 실행 후 이미지 안에
  `proposal_api.py`가 실제로 들어갔는지 확인(`docker compose run --rm workmate-agent python -c
  "import app.proposal_api"`가 에러 없이 끝나면 됨 — 옛 스텁에는 이 모듈 자체가 없으므로
  `ModuleNotFoundError`가 나면 아직 옛 경로를 빌드 중이라는 뜻).

**다른 에이전트에 미치는 영향** — 이 계획은 workmate-agent 자신의 빌드 소스만 바꾸지만, 실제로는
"Mock 셸 → 진짜 backend" 전환이라 파급 범위가 workmate-agent 밖으로 나간다:

- **main-agent(오케스트레이터 backend) — 직접 영향, 위험도 높음**:
  - `docker-compose.yml`의 `main-agent`가 `depends_on: workmate-agent: condition:
    service_healthy`로 묶여 있다 — 지금까지는 Mock의 `/health/ready`가 즉시 200을 반환해 기동이
    빨랐지만, 진짜 backend는 LLM Provider 초기화 등으로 더 오래 걸리거나 필요한 env(`LLM_API_KEY`
    등)가 비어 있으면 아예 `unhealthy`로 멈출 수 있다. 지금 healthcheck 설정(`interval: 5s,
    retries: 10, start_period: 5s` — 최대 약 55초)이 충분한지 실제로 띄워서 재확인 필요.
  - main-agent의 `a2a_client.py`(59줄 병합 변경분)가 지금까지 상대한 건 **항상 동기적으로 즉시
    `TASK_STATE_COMPLETED`를 반환하는 Mock**뿐이었다. 진짜 backend는
    `TaskState.TASK_STATE_SUBMITTED`로 시작해 비동기로 진행되는 실제 Task 생명주기를 쓴다
    (`app/a2a/runtime.py`) — `GET /a2a/tasks/{task_id}` 폴링 경로가 `docker compose` 환경에서
    **한 번도 실제로 실행된 적이 없다.** 폴링 타임아웃·재시도 로직에 잠재 버그가 있어도 지금까지는
    드러날 기회 자체가 없었다는 뜻 — 계획 1 적용 직후 "Workmate AI" 탭에서 각 스킬(오늘 브리핑,
    주간 업무보고 등)을 실제로 눌러보는 회귀 테스트가 필요하다.
  - Mock의 `SKILLS` 카탈로그(5개: `daily_briefing`/`weekly_report`/`analyze_meeting`/
    `search_meetings`/`rank_priorities`)와 진짜 backend가 실제로 승인해주는 skill_id 목록
    (`workmate-agent/app/a2a/runtime.py`의 `approved_skill_definitions`)이 정확히 같은 집합인지
    대조 필요 — 다르면 main-agent가 여태 몰랐던 400 에러를 새로 마주치거나, 반대로 그동안 몰랐던
    스킬을 쓸 수 있게 된다.
  - `WORKMATE_SERVICE_TOKEN`이 `main_agent/.env`와 `workmate-agent/.env` 양쪽에 같은 값이어야
    한다(계획 4에서 다시 다룸) — Mock은 토큰 형식만 맞으면(둘 다 같은 파일에서 읽으니 항상
    일치) 통과했지만, 진짜 backend로 바뀌면 두 `.env`가 실제로 어긋나 있을 경우 즉시 401로
    드러난다.
- **video-agent / dev-agent / game-qa-agent — 간접 영향만, 위험도 낮음**: 이 세 에이전트는
  workmate-agent와 직접 통신하지 않으므로 코드·데이터 경로엔 영향이 없다. 다만 전부 main-agent를
  경유해 라우팅되므로(`AGENT_REGISTRY`), main-agent의 기동이 workmate-agent healthcheck
  때문에 지연되거나 실패하면 이 세 에이전트로 가는 요청도 함께 막힌다 — 위 healthcheck 재확인이
  간접적으로 이들의 가용성과도 연결된다.

- **담당자 전달용 요약**: "`main_agent/docker-compose.yml`의 `workmate-agent` 빌드 경로가
  `../workmate-agent`로 돼 있는데, 이 파일이 `main_agent/` 안으로 이동하면서 실제 저장소
  (`workmate-agent` 팀 저장소, 이 컴포즈 파일 기준 두 단계 위)가 아니라 리포 안에 남아있던 옛
  스텁(`AI-agent_game_platform/workmate-agent/`, 9개 파일)을 대신 가리키게 됐습니다.
  `../../workmate-agent`로 고쳐야 합니다. **주의**: 이 스텁은 겉으로는 정상 동작하는 것처럼
  보이는 Mock이라(모든 스킬 호출에 즉시 `Mock 호출에 성공했습니다`로 응답) 지금까지 `docker
  compose`로 띄운 'Workmate AI' 채팅이 실은 진짜 데이터를 한 번도 안 탔을 가능성이 큽니다 —
  경로를 고친 뒤엔 실제 backend의 비동기 Task 폴링을 처음 타게 되니 회귀 테스트를 꼭 해주세요."

### 계획 2 — Gmail/Calendar env·volume 복구 (계획 1 이후 적용)

**수정 대상**: 같은 파일, 계획 1 적용 후 `workmate-agent` 서비스 블록에 추가.
`57be15b`(사용자의 원래 이식 커밋)에 있던 원본 설정을, `main_agent/` 한 단계 안쪽으로 이동한
만큼 `../` 하나씩 더 붙여 복원한다:

```diff
     environment:
       WORKMATE_SERVICE_TOKEN: "${WORKMATE_SERVICE_TOKEN:?WORKMATE_SERVICE_TOKEN must be set}"
       APP_BASE_URL: "http://workmate-agent:8001/a2a"
+      # 컨테이너 안에서는 `Path(__file__).resolve().parents[3]` 기반 기본 토큰 경로 추정
+      # (`app/workflows/daily_briefing.py`)이 리포 레이아웃과 안 맞아 항상 빗나간다 — 아래
+      # 볼륨 마운트 경로를 명시적으로 지정한다.
+      GOOGLE_TOKEN_FILE: "/app/google-oauth-test/token.json"
+    # 컨테이너를 새로 띄울 때마다 비어 있는 SQLite가 새로 생겨 daily_briefing 등이 항상 빈
+    # 결과만 반환하는 문제를 막기 위해, 로컬에서 `python -m app.server`로 직접 실행 중인
+    # workmate-agent와 같은 `.runtime/` SQLite 파일을 그대로 공유한다. Google Calendar/Gmail
+    # 라이브 신호도 같은 이유로 로컬 `google-oauth-test/` OAuth 토큰을 그대로 공유한다.
+    volumes:
+      - "../../workmate-agent/.runtime:/app/.runtime"
+      - "../../google-oauth-test/token.json:/app/google-oauth-test/token.json"
     healthcheck:
```

- 원본 diff(`git show 57be15b`)를 그대로 옮기되 경로 깊이만 `main_agent/` 이동분(한 단계)만큼
  보정했다 — `google-oauth-test/`도 `c:\dev\workmate\google-oauth-test`로 `workmate-agent`와
  같은 깊이의 형제 디렉터리라 동일하게 `../`를 하나 더 붙인다.
- **선행 조건**: 계획 1을 먼저 적용해야 한다 — `build:` 경로가 옛 스텁을 가리키는 채로 이
  env var만 추가하면, 옛 스텁(`app.py` 하나짜리)에S는 애초 `GOOGLE_TOKEN_FILE`을 읽는 코드 자체가
  없어 아무 효과가 없다.
- **검증**: `docker compose up workmate-agent` 후 컨테이너 로그에서 `daily_briefing` 호출 시
  "일정 0건, 메일 신호 0건"이 아니라 실제 로컬 `.runtime/`에 있는 데이터가 나오는지 확인(19번
  문서 3단계가 로컬 직접 실행으로 확인했던 것과 같은 방식, 이번엔 컨테이너 기준).

**다른 에이전트에 미치는 영향**:

- **main-agent — 간접 영향만, 낮음**: 새 env·volume은 workmate-agent 서비스 블록 안에만어
  추가되므로 main-agent 쪽 설정은 그대로다. 다만 계획 1로 이미 진짜 backend를 타고 있는 상태라,
  이 계획을 적용하면 `daily_briefing`/`rank_priorities` 등 응답 **내용**이 "일정 0건"류 빈
  응답에서 실제 `.runtime/`의 Task·Meeting·Google 신호로 바뀐다 — main-agent 자체엔 코드 영향이
  없지만 화면에 보이는 결과가 달라지므로, 계획 1 회귀 테스트를 이 계획까지 적용한 뒤에 다시
  한번 하는 게 안전하다.
- **video-agent / dev-agent / game-qa-agent — 영향 없음**: 이 서비스들과 무관한 볼륨·env다.
- **workmate-agent 자기 자신(다른 인스턴스)과의 충돌 — 참고**: `../../workmate-agent/.runtime`을
  그대로 마운트하므로, 로컬에서 `uv run python -m app.server`로 직접 띄운 workmate-agent
  프로세스가 동시에 떠 있으면 같은 SQLite 파일에 두 프로세스가 동시에 쓸 수 있다(원본
  `57be15b` diff 주석이 이미 경고한 내용, 그대로 승계됨) — "다른 에이전트"는 아니지만 같은
  workmate-agent의 이중 실행이라 실사용 시 유의.
- **담당자 전달용 요약**: "워크메이트 병합 시 뺐던 `GOOGLE_TOKEN_FILE` env var와 `.runtime/`
  볼륨 마운트를 다시 추가해야 합니다 — 그 기능(Gmail/Calendar 실시간 신호) 코드가
  `workmate-agent` 쪽에 이제 들어와 있습니다. 원래 diff는 `57be15b` 커밋에 그대로 남아 있고,
  경로만 한 단계씩 더 올려주면 됩니다(계획 1 참고)."

### 계획 5 — workmate-agent 포트를 호스트에 게시(REST 화면용, 계획 1 이후 적용)

**수정 대상**: 같은 파일, `workmate-agent` 서비스 블록.

```diff
   workmate-agent:
     build: ../../workmate-agent
+    ports:
+      - "8100:8001"
     expose: ["8001"]
```

- 컨테이너 내부 8001(REST+A2A 겸용 `app.main:app`)을 호스트 8100으로 매핑 — 프론트엔드가
  하드코딩한 `WORKMATE_API_BASE_URL = "http://127.0.0.1:8100"`(19번 문서 결정 3)과 정확히
  맞춘다. 기존 `expose: ["8001"]`은 그대로 남겨 main-agent의 컨테이너 간 A2A 호출
  (`workmate-agent:8001/a2a`)도 계속 되게 한다 — 둘은 서로 다른 접근 경로라 공존 가능.
- **선행 조건**: 계획 1(빌드 경로 수정) — 옛 스텁도 우연히 `/health/ready`·`/a2a/*`는
  구현하고 있어 포트만 게시해도 겉보기엔 응답하지만, REST 라우터(`task_router` 등) 자체가
  옛 스텁엔 없으므로 실제 화면은 여전히 깨진다.
- **검증**: `docker compose up -d workmate-agent` 후 호스트에서
  `curl -H "X-Workmate-Assignee: %EC%84%9C%EC%84%A0%EC%A0%95" http://127.0.0.1:8100/api/v1/tasks`가
  200을 반환하는지, 헤더 없이는 401인지 확인. 브라우저 CORS까지 확인하려면
  `curl -X OPTIONS -H "Origin: http://localhost:5173" -H "Access-Control-Request-Headers:
  x-workmate-assignee" http://127.0.0.1:8100/api/v1/tasks`가 200을 반환하는지 확인.

**다른 에이전트에 미치는 영향**:

- **main-agent — 영향 없음**: `expose: ["8001"]`을 그대로 유지하므로 main-agent가 쓰는
  `WORKMATE_AGENT_URL=http://workmate-agent:8001/a2a`(컨테이너 간 통신)는 이 변경으로 전혀
  바뀌지 않는다.
- **video-agent / dev-agent / game-qa-agent — 영향 없음**: 포트 매핑은 workmate-agent
  서비스에만 해당.
- **호스트 환경 — 참고**: 호스트 8100 포트가 이미 다른 프로세스(예: 로컬에서 직접 띄운
  `python -m app.server`)에 점유돼 있으면 `docker compose up`이 포트 바인딩 실패로 죽는다 —
  로컬 workmate-agent를 직접 띄운 채로 `docker compose up`을 같이 쓰지 않도록 주의(둘 중
  하나만 8100을 쓸 수 있음).
- **담당자 전달용 요약**: "`docker-compose.yml`의 `workmate-agent`에 `ports: - \"8100:8001\"`을
  추가해야 합니다 — 프론트엔드(`workmate/api.ts`)가 `127.0.0.1:8100`을 하드코딩해서 호출하는데,
  지금은 `expose`만 있어서 호스트(브라우저)에서 컨테이너에 닿지 않습니다. 컨테이너 안엔 A2A와
  REST가 이미 같은 앱(`app.main:app`)에 같이 떠 있으니 백엔드 쪽 추가 구현은 필요 없고, 이
  한 줄이면 됩니다."

### 계획 3 — 19~24번 문서 경로 표기 갱신

**대상 문서**: 19, 20, 21, 23, 24번(그리고 이번에 새로 만든 25번 자신도 최신 경로 기준으로
이미 작성함 — 대상 아님).

- 치환 규칙: `AI-agent_game_platform/frontend` → `AI-agent_game_platform/main_agent/frontend`,
  `AI-agent_game_platform/backend` → `AI-agent_game_platform/main_agent/backend`(백틱 안 코드
  경로만 대상 — 문장 설명 텍스트는 건드리지 않음).
- 기계적 치환이 아니라 **문서별로 직접 열어 확인하며 고친다** — 일부 문단은 "그 당시엔
  `frontend/`가 맞았다"는 시제 설명이라 단순 치환하면 오히려 역사적 기록이 틀어진다(예: 19번
  문서의 "결정 2"는 재구성 이전 시점 서술이라 원문 그대로 두는 게 맞고, 그 아래 "구현 완료"
  절들만 지금 경로로 갱신 대상).
- **검증**: 갱신 후 각 문서에서 언급한 파일 경로를 실제로 `Read`해서 파일이 그 경로에 있는지
  하나씩 확인.
- **담당자 전달 불필요** — 이 저장소(`c:\dev\workmate`) 소유 문서라 우리가 직접 고치면 된다.

**다른 에이전트에 미치는 영향**: 없음 — 문서 텍스트만 바꾸는 작업이라 어떤 서비스의 런타임
동작에도 영향을 주지 않는다.

### 계획 4 — origin 최신 커밋 반영 + 토큰 동기화 재확인

- `cd AI-agent_game_platform && git merge origin/feat/unified-multi-agent-platform`(또는
  `git pull`)로 `a8ec0a7`을 로컬 `test/unified-latest`에 받는다 — 이미 fetch까지는 끝났고,
  workmate 관련 파일과 겹치지 않아 conflict 위험이 없음을 확인했다(위 "3." 참고).
- 병합 후 `main_agent/.env`와 `workmate-agent/.env`(둘 다 gitignore 대상이라 각자 로컬에
  존재해야 함) 양쪽에 `WORKMATE_SERVICE_TOKEN`이 **같은 값**으로 들어있는지 직접 열어 대조 —
  a8ec0a7의 README가 이 두 파일이 자동 동기화되지 않는다고 명시했다.
- **검증**: `git status`가 clean하고, `docker compose config`(계획 1·2까지 적용된 상태라면)가
  에러 없이 통과하는지 확인.

**다른 에이전트에 미치는 영향**:

- **main-agent — 낮음, 정보성**: `a8ec0a7`이 고친 `router.py`는 `RouterLLM`이
  `ROUTER_MODEL_NAME`/`ROUTER_BASE_URL`/`ROUTER_API_KEY`가 안 채워졌을 때 `MODEL_NAME`/
  `MODEL_BASE_URL`/`MODEL_API_KEY`로 폴백하던 기존 동작은 그대로 두고 **경고 로그 한 줄만**
  추가한다 — 라우팅 판단 자체(어느 에이전트로 보낼지)는 바뀌지 않는다. 병합해도 회귀 테스트가
  필요 없는 수준.
- **game-qa-agent(qna_agent) — 직접 영향 없음, 단 기존 결합을 재확인시켜줌**: 이 경고가 실제로
  드러내는 건 **이미 존재했던** 결합이다 — `main_agent/.env`를 `main-agent`와 `game-qa-agent`가
  같이 읽다 보니, `ROUTER_LLM_ENABLED=true`인데 `ROUTER_*` 3종을 안 채우면 라우터가
  game-qa-agent 자신의 LLM 설정(`MODEL_NAME` 등)을 그대로 빌려 쓴다. 즉 **game-qa-agent 담당자가
  자기 모델을 바꾸면(`MODEL_NAME` 등) 그 값이 그대로 main-agent의 라우팅 판단에도 쓰인다** —
  이번 커밋은 이 상황을 막지 않고 경고만 하므로, game-qa-agent 쪽에서 모델을 바꿀 때는 라우터가
  영향받지 않는지(= `ROUTER_*` 3종이 각자 명시돼 있는지) 같이 확인해야 한다는 점을 담당자에게
  알려줄 필요가 있다.
- **workmate-agent — 이 계획의 "토큰 동기화 재확인" 항목과 직결**: 계획 1로 진짜 backend를
  타기 시작하면 `main_agent/.env`와 `workmate-agent/.env`의 `WORKMATE_SERVICE_TOKEN`이 어긋나 있을
  경우 즉시 401로 드러난다(위 계획 1 "다른 에이전트에 미치는 영향" 참고) — a8ec0a7의 README가
  "자동 동기화 안 됨"을 명시했으니, 계획 1을 적용하기 전에 이 대조를 먼저 해두는 게 순서상
  안전하다(아래 "실행 순서 요약"에도 반영).
- **video-agent / dev-agent — 영향 없음**: 이번 커밋이 건드린 두 파일(`README.md`,
  `main_agent/backend/app/router.py`) 어디에도 이 두 에이전트 관련 코드가 없다.

### 실행 순서 요약

```
계획 4의 "WORKMATE_SERVICE_TOKEN 두 .env 대조"만 먼저 — Mock 시절엔 안 드러났던 401이
  계획 1 적용 즉시 터질 수 있으니 순서상 가장 먼저 확인
  ↓
계획 1(빌드 경로 수정) → 계획 5(포트 게시) → 계획 2(env·volume 복구) → 검증(docker compose
  build/up, curl로 REST·A2A·CORS 확인, "Workmate AI" 탭 전체 스킬 회귀 테스트)
  ↓
계획 4의 나머지(origin 커밋 실제 merge) — 위와 독립적으로 아무 때나
계획 3(문서 경로 갱신) — 위와 완전히 독립적으로 아무 때나
```

**실제로는 이 순서대로 전부 실행·검증했다** — 결과는 바로 아래 "완료 보고" 절 참고.

## 완료 보고 (2026-08-19)

이 문서를 쓴 같은 세션 안에서 계획 1~5를 전부 로컬 clone에 반영하고 직접 검증했다. 원래
"실행 순서 요약"과 한 가지만 다르게 했다 — 계획 4의 origin merge를 토큰 대조보다 먼저 했다
(README·router.py 변화가 뒤이은 검증에 참고가 됐고, workmate 파일과 안 겹쳐 순서를 바꿔도
안전했다).

### 계획 4 — origin 커밋 반영

`git merge origin/feat/unified-multi-agent-platform --no-edit` 실행 →
`Fast-forward, f9db8ca..a8ec0a7`, conflict 없음. 새로 생긴 루트 `README.md`가 계획 2("REST가
미구현"이 아니라 이미 구현돼 있다는 사실)와 계획 5(포트 미게시)를 정확히 예견하고 있어 이후
계획 수립에 그대로 활용했다(위 "2. (신규 발견)" 절 인용).
`WORKMATE_SERVICE_TOKEN` 대조는 `main_agent/.env`를 아래에서 새로 만들며 같이 처리했다(값을
`workmate-agent/.env`에서 그대로 복사 — 아래 참고).

### 계획 1·5·2 — docker-compose.yml 수정

`main_agent/docker-compose.yml`의 `workmate-agent` 서비스를 계획대로 수정했다:

- `build: ../workmate-agent` → `../../workmate-agent`(계획 1)
- `env_file: ../workmate-agent/.env` → `../../workmate-agent/.env`(계획 1)
- `ports: ["8100:8001"]` 추가, 기존 `expose: ["8001"]`은 유지(계획 5)
- `environment.GOOGLE_TOKEN_FILE` 추가, `volumes: ["../../workmate-agent/.runtime:/app/.runtime"]`
  추가(계획 2) — **`google-oauth-test/token.json` 볼륨은 추가하지 않았다.** 확인해보니 로컬에
  그 경로에 활성 파일이 없고(`token.json.disabled-for-test`라는 이름의 파일만 존재 — 의도적으로
  비활성화해둔 것으로 보여 임의로 되살리지 않았다) 없는 파일을 bind mount하면 Docker가 그
  자리에 빈 디렉터리를 만들어 컨테이너 쪽에서 오히려 에러가 난다. 이 부분은 계획에서 갈라진
  지점이라 명시해둔다 — `google-oauth-test/token.json`이 실제로 준비되면 그때 한 줄만 추가하면
  된다(compose 파일에 이 내용을 주석으로 남겨뒀다).

각 변경 지점에는 "25번 문서 계획 N" 형태로 주석을 남겨 나중에 이 문서와 코드를 오가며 대조할
수 있게 했다.

### 검증 — 실제로 docker compose build/up/curl까지 실행

로컬에 Docker Desktop이 꺼져 있어 먼저 띄운 뒤(`Start-Process`) 데몬이 준비될 때까지 기다려
진행했다. `main_agent/.env`가 로컬에 없어(README가 요구하는 필수 키 목록 확인) 검증 전용으로
새로 만들었다(gitignore 대상, 커밋 안 됨) — `WORKMATE_SERVICE_TOKEN`은 `workmate-agent/.env`의
값을 파일 간 직접 복사해 두 파일이 같은 값을 갖게 했다(값 자체는 어디에도 출력하지 않았다).

1. **`docker compose config --quiet`** → 통과(YAML·변수 치환 에러 없음).
2. **`docker compose build workmate-agent`** → 성공, 실제 `c:\dev\workmate\workmate-agent`
   소스로 이미지가 빌드됨(fastapi/google-auth 등 실제 의존성 설치 로그로 확인).
3. **`docker compose run --rm --no-deps workmate-agent python -c "import app.proposal_api,
   app.repositories.google_credentials"`** → `REAL_BACKEND_OK`. 옛 스텁이었다면
   `ModuleNotFoundError`가 났어야 할 두 모듈이 정상 import됨 — **계획 1이 실제로 옛 스텁을
   벗어났음을 코드 레벨로 확인.**
4. **`docker compose up -d workmate-agent`** 후 `/health/ready`가 호스트 8100에서 응답할 때까지
   대기 → 정상 기동.
5. **REST 엔드포인트(계획 5 검증)**: 호스트에서
   `curl -H "X-Workmate-Assignee: %EC%84%9C%EC%84%A0%EC%A0%95" http://127.0.0.1:8100/api/v1/tasks`
   → **200**. 같은 요청을 헤더 없이 보내면 **401**(인증이 실제로 걸려 있음도 같이 확인).
6. **CORS(계획 5 검증)**: `Origin: http://localhost:5173` + `Access-Control-Request-Headers:
   x-workmate-assignee`로 `OPTIONS /api/v1/tasks` → **200**(오케스트레이터 프론트 실제 개발
   포트 기준 브라우저 Preflight를 그대로 흉내낸 것).
7. **A2A 엔드포인트**: 컨테이너 안에서 `http://localhost:8001/.well-known/agent-card.json` →
   **200**(main-agent가 쓰는 컨테이너 간 경로도 살아있음을 확인).
8. **`.runtime` 볼륨 공유(계획 2 검증)**: `docker compose exec workmate-agent ls -la
   /app/.runtime`의 파일 크기(`a2a.sqlite3` 10825728바이트, `meetings.sqlite3` 1114112바이트 등)가
   호스트 `c:\dev\workmate\workmate-agent\.runtime`과 **정확히 일치** — 컨테이너가 로컬 실제
   데이터를 그대로 보고 있음을 확인(1번의 REST 200 응답이 빈 Mock이 아니라 이 실데이터 기준
   응답이라는 뜻).
9. 검증 후 컨테이너는 정리했다(`docker compose stop && rm -f workmate-agent`) — 로컬에 다른
   workmate-agent 프로세스가 함께 떠 있을 때의 SQLite 잠금 경합(계획 2 "다른 에이전트에 미치는
   영향" 참고)을 피하기 위해 검증용으로만 잠깐 띄웠다가 내렸다.

**검증하지 않은 것**: main-agent(main_agent/backend) 자체를 포함한 전체 스택
기동(`docker compose up --build`)과 실제 브라우저로 "Workmate AI" 탭 전체 스킬(오늘 브리핑 등)
회귀 테스트는 이번엔 하지 않았다 — `GEMINI_API_KEY`/`GITHUB_TOKEN` 등 다른 서비스의 실 자격
증명이 로컬에 없어 전체 스택을 검증용으로 채우는 건 범위 밖으로 판단했다(workmate-agent
단독 검증만으로 계획 1·2·5가 실제로 옛 문제를 해결했다는 근거는 위 1~8번으로 충분하다고
봄). main-agent를 포함한 전체 회귀는 담당자 전달 후 실제 반영 시점에 필요하다.

### 계획 3 — 19~24번 문서 경로 표기 갱신

원래 계획한 "본문 전체 치환" 대신 더 안전한 방식으로 갈렸다 — 실행하며 판단이 바뀐 지점이라
명시해둔다. 19번 문서의 "구현 완료" 절들은 그 시점(모노레포 재구성 이전)에 사용자가 실제로
작업한 디렉터리(`frontend/`)를 정확하게 서술한 **역사적 기록**이라, 본문을 지금 경로로
고치면 오히려 "그때 실제로 어디를 고쳤는지"를 왜곡하게 된다는 걸 확인했다. 그래서:

- 19, 20, 21, 22, 23번 문서 머리말(상태/경로 참고 줄)에 "이 문서의 `AI-agent_game_platform/
  frontend`·`backend` 표기는 모노레포 재구성 이전 기준이며, 지금 실제 위치는
  `main_agent/frontend`·`main_agent/backend`(25번 문서 참고)"라는 한 줄짜리 경로 참고 주석만
  추가했다 — 본문 서술은 건드리지 않았다(24번 문서는 해당 경로 언급이 없어 대상에서 뺐다).
- 예외적으로 19번 문서의 "메뉴 확장(1단계) 변경 지점" 절에 있던 **클릭 가능한 상대 마크다운
  링크 3개**(`[ui-variant.ts](../AI-agent_game_platform/frontend/...)` 등)는 역사적 서술이
  아니라 지금 눌러서 파일로 이동하는 실사용 내비게이션이라 실제로 깨져 있었다 — 이 3개는
  `main_agent/frontend/...`로 직접 고쳤다.
- **검증**: 고친 3개 링크가 가리키는 파일(`ui-variant.ts`, `MainUiPanels.tsx`, `App.tsx`)이
  전부 그 경로에 실제로 존재함을 확인.

### 계획 6(추가 발견, 2026-08-19) — `docs/schemas` 미마운트로 오늘 브리핑·주간 업무보고 503

위 "검증하지 않은 것"에서 미뤘던 전체 스택 브라우저 회귀를 사용자 요청으로 실제로 띄워서 확인하다
발견했다. `docker compose up -d main-agent workmate-agent`(video/dev/game-qa-agent는 API 키가
없어 생략) + `npm run dev`로 프론트를 띄우고 브라우저(Playwright)로 "오늘 브리핑" 화면을 열자
**`HTTP 503: approved skill schema is unavailable`**이 떴다.

- **원인**: `workmate-agent/app/internal_chat.py`의 `_schema_validator()`가
  `WORKMATE_SCHEMA_ROOT`가 안 잡혀 있으면 `Path(__file__).resolve().parents[2]/docs/schemas`를
  기본값으로 쓴다. 로컬에서 `c:\dev\workmate\workmate-agent`를 직접 실행할 때는 이 계산이
  `c:\dev\workmate\docs\schemas`(진짜 저장소 루트)를 정확히 가리켜서 우연히 맞았을 뿐이다.
  컨테이너 안에서는 같은 계산이 `/docs/schemas`가 되는데, `Dockerfile`이 `app`/`migrations`/
  `tools`만 `COPY`하므로 이 경로엔 아무것도 없다 — 파일이 없으면 503을 던진다
  (`/api/v1/internal/skill-chat/messages`가 실패해 오늘 브리핑·주간 업무보고가 전부 이 화면을
  보게 된다).
- **수정**: `main_agent/docker-compose.yml`의 `workmate-agent` 서비스 `volumes:`에
  `- "../../docs/schemas:/docs/schemas:ro"` 한 줄을 추가 — 컨테이너의 기본 계산 경로에 그대로
  꽂아 넣어 코드·env 변경 없이 해결.
- **검증**: `docker compose up -d workmate-agent`로 재기동 후 컨테이너 안에서 스키마 파일이
  보임을 확인, 브라우저(Playwright)로 "오늘 브리핑"을 다시 열어 **503 사라짐 + 실제 데이터
  렌더링**까지 확인했다 — "8월 19일, 좋은 아침이에요, 서선정님. 오늘 일정 1건, 메일 신호 2건,
  우선순위 3건입니다", 우선순위 Top 3(점수 breakdown 포함), 실제 오늘 일정, 실제 Gmail 제목까지
  전부 실데이터. `HAS_503: false`.
- **다른 에이전트에 미치는 영향**: 없음 — workmate-agent 서비스에만 해당하는 읽기 전용 볼륨.
- **담당자 전달용 요약**: "`docker-compose.yml`의 `workmate-agent`에
  `- \"../../docs/schemas:/docs/schemas:ro\"` 볼륨을 추가해야 합니다 — 안 그러면 오늘 브리핑·
  주간 업무보고가 컨테이너에서 전부 503(approved skill schema is unavailable)이 납니다. 로컬
  직접 실행에서는 우연히 안 걸리던 문제라 지금까지 못 봤을 수 있습니다."
- **부수 확인**: 같은 세션에서 "Main Chatbot"(우측 패널, `owner=서선정`으로 세션 재조회 시)에
  `sqlite3.InterfaceError: bad parameter or other API misuse`로 인한 500도 관찰됐다
  (`main_agent/backend/app/conversation_store.py:116`) — 이번 조사 범위 밖이라 원인까지는
  안 팠고, 재현 조건("owner=default"로 만든 세션을 "owner=서선정"으로 다시 부를 때로 보임)만
  기록해둔다. 별도로 다뤄야 한다.

### 남는 것 — 이 문서가 대신 못 하는 일

- 위 모든 변경은 **로컬 clone(`c:\dev\workmate\AI-agent_game_platform`)에만** 있다 — 팀원
  저장소로 push하지 않았다. 각 계획의 "담당자 전달용 요약"을 실제로 전달해야 팀원 저장소에
  반영된다.
- main-agent를 포함한 전체 스택 기동·"Workmate AI" 탭 브라우저 회귀 테스트는 하지 않았다(위
  "검증하지 않은 것" 참고) — 담당자가 실제 반영할 때 필요.
- `google-oauth-test/token.json` 볼륨 마운트는 그 파일이 준비될 때까지 보류 상태로 남아있다.

## 관련 문서

- [19-workmate-ui-orchestrator-port-plan.md](19-workmate-ui-orchestrator-port-plan.md) — 이식
  작업 원본 계획·구현 기록(결정 1~5, 1~8단계).
- [23-proposals-orchestrator-vs-workmate-ui-diff.md](23-proposals-orchestrator-vs-workmate-ui-diff.md),
  [24-proposals-orchestrator-vs-workmate-ui-ui-diff.md](24-proposals-orchestrator-vs-workmate-ui-ui-diff.md)
  — 이 문서가 "여전히 유효한지" 검증한 대상(제안함 로직·UI 차이).
