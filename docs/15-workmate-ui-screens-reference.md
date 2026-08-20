# workmate-ui 화면별 기능·데이터 참조

작성일: 2026-08-15
상태: 초안 — 화면별로 하나씩 채워나가는 진행 중 문서

## 목적

[02-a2a-interface.md](02-a2a-interface.md), [03-data-priority-rules.md](03-data-priority-rules.md),
[04-scenarios.md](04-scenarios.md), [07-technical-specification.md](07-technical-specification.md),
[09-ui-design.md](09-ui-design.md) 다섯 문서에 흩어져 있는 계약·시나리오·데이터 모델·UI 요구사항을
화면 단위로 종합해, **`workmate-ui`가 궁극적으로 구현해야 할 화면별 기능**과 **화면 조회값(데이터 필드)**을
정의하는 문서다. 즉 지금 코드가 무엇을 하는지가 아니라 **다섯 문서를 기준으로 무엇을 해야 하는지**를
적는다.

`workmate-ui`의 2단계 계획(1차 완성 → 2차 Orchestrator UI 양식으로 이식) 양쪽 모두에서 "이 화면이 뭘
해야 하는가"의 단일 기준(source of truth)으로 쓴다.

[14-workmate-ui-integration-gaps.md](14-workmate-ui-integration-gaps.md)는 이 문서가 정의한 기준과
`workmate-ui` 실제 구현을 대조해 갭을 찾는 문서다 — 즉 14번 갭 분석은 02·03·04·07·09를 직접 다시 훑는
대신 이 문서를 1차 기준으로 참고한다. 두 문서의 역할 구분:

| 문서                                       | 역할                                                                       |
| ------------------------------------------ | -------------------------------------------------------------------------- |
| 이 문서(15번)                              | 02·03·04·07·09를 종합한 화면별 **목표 기능·조회값 정의** (Source of Truth) |
| [14번](14-workmate-ui-integration-gaps.md) | 15번 기준과 `workmate-ui` 실제 구현을 대조한 **갭·구현 계획·진행 상태**    |

## 진행 상태

| 화면                            | 상태                                                                       |
| ------------------------------- | -------------------------------------------------------------------------- |
| 📬 제안함 (`Proposals.tsx`)     | 🟨 구형(as-built) 스타일로 작성됨 — 새 목적 기준 재작성 필요               |
| 🏠 오늘 브리핑 (`Briefing.tsx`) | ✅ 작성 완료                                                               |
| 📊 주간 업무보고 (`Report.tsx`) | ✅ 작성 완료                                                               |
| 📋 할 일 관리 (`Tasks.tsx`)     | ✅ 작성 완료                                                               |
| 🎙️ 회의 녹음 (`Meeting.tsx`)    | ✅ 작성 완료 (회의 생성~Action Item 자동 추출까지)                         |
| 📁 회의 관리 (`Archive.tsx`)    | 🟨 분석 결과 표시~Task 등록만 작성 (회의 목록·참석자·전체 회의록은 미작성) |
| 🔍 회의록 검색 (`Search.tsx`)   | ✅ 작성 완료                                                               |

---

## 📬 제안함 (`Proposals.tsx`)

### 기능 설명

- **실시간 제안 수신**: Gmail·Calendar에서 발행된 임시 Task 제안을 SSE로 실시간 수신. 다른 화면에 있어도
  우측 상단 Toast 팝업 + 상단 종 아이콘 미확인 배지로 알려줌 (`lib/proposal-notifications.tsx`가 앱
  최상단에서 구독을 유지해 화면 전환에도 끊기지 않음)
- **데스크톱 알림**: 브라우저 알림 권한을 켜면 탭이 백그라운드에 있어도 OS 알림 표시
- **제안 카드 목록**: 도착한 제안을 카드 형태로 표시 — 출처(MAIL/CALENDAR) 배지, **날짜**(이메일은
  수신 시각, Calendar는 일정 시작 시각), 원본 요약(메일 스니펫 또는 일정 정보), AI가 판단한 사유(💡)
  표시. **메일 하나에서 여러 개의 제안이 나올 수 있음** — LLM이 메일 본문을 분석해 "할 일로 등록할
  가치가 있다"고 판단한 항목만, 있는 만큼(0개~여러 개) 각각 독립된 카드로 만듦. 메일 1건 = 카드 1개가
  아니라 카드 0개일 수도 3개일 수도 있고, 각 카드는 서로 다른 할 일 후보로 따로 승인/무시함. Calendar는
  (계획상) 일정 하나 = 제안 하나로 이 다중 카드 동작이 없음
  > **정렬 기준(2026-08-17 요청)**: 1순위 — 이메일 카드가 먼저, Calendar 카드가 나중(출처로 두 그룹을
  > 나눔). 2순위 — 이메일은 수신 날짜 **내림차순**(최신 메일이 위), Calendar는 일정 날짜 **오름차순**
  > (임박한 일정이 위). 날짜가 없거나 파싱할 수 없는 항목은 그 출처 그룹 안에서 맨 뒤로 밀린다
  > (`sortProposals`, `lib/workmate-format.ts`). 이 정렬은 프론트에서만 적용된다 — SSE로 오는 순서·
  > `proposals` 원본 배열 자체는 바뀌지 않는다.
- **승인 전 수정**: 제목·담당자·마감일·우선순위를 카드에서 바로 수정한 뒤 승인 가능
- **승인/무시**: 각 제안을 승인(Task로 등록)하거나 무시(제안만 사라짐, Task 미생성) 선택
- **중복 처리**: 비슷한 Task가 이미 있으면 기존 목록을 보여주고 "그래도 추가" 선택 시에만 별도로 생성
- **Google 계정 연결(2026-08-18 신규)**: "Google 계정 연결" 버튼을 누르면 실제 Google 로그인 화면으로
  이동해 사용자 자신의 계정으로 동의하고, 그 Credential이 자기 `user_id` 몫으로 서버에 저장됨
  (`app/google_oauth_web.py`, `GET /api/v1/auth/google/start`가 서명된 인증 URL을 내려주면 프론트가
  `window.location.href`로 직접 이동 — Google로 가는 이동 자체엔 Bearer Token이 필요 없어 이 조회
  단계에서만 인증함). 연결되면 화면 상단에 "연결됨" 표시와 "연결 해제" 버튼이 뜨고, 아래 Gmail·
  Calendar 동기화가 이 개인 계정으로 동작함. **연결하지 않아도 기존처럼 개발 환경 공유 계정
  (`google-oauth-test/token.json`, 고정 데모 계정 1개)이 있으면 그대로 동작함** — 개인 연결이
  없을 때만 공유 계정으로 자동 폴백(`GET /api/v1/auth/google/status`로 연결 여부 조회,
  `POST .../disconnect`로 해제). 이전까지는 서버 프로세스가 대화형 브라우저를 못 열어 `token.json`이
  없으면 그냥 503과 "`auth_flow.py`를 먼저 실행하라"는 안내만 돌려줬다 — 이 흐름이 그 수동 스크립트
  실행을 화면 버튼으로 대체한다. 사용자별 Credential은 `google_credentials` 테이블에 저장하고
  (SQLite: `app/repositories/google_credentials.py`, PostgreSQL: `migrations/006_google_credentials.sql`),
  `state` 위조를 막기 위해 `WORKMATE_OAUTH_STATE_SECRET`(없으면 `WORKMATE_SERVICE_TOKEN`)으로 서명한다.
  `google-oauth-test/client_secret.json`이 "installed"(Desktop App) 타입 OAuth Client라 Google이
  `http://localhost`(포트 무관) Loopback 리디렉션을 사전 등록 없이 허용하므로, 이 웹 흐름도 Google
  Cloud Console 설정을 새로 바꾸지 않고 그대로 재사용한다(실측 확인).
- **Gmail 수동 동기화**: "Gmail 동기화 실행" 버튼으로 최근 메일 5건을 즉시 분석해 제안 생성
  (개발/테스트용)
- **Gmail·Calendar 백그라운드 자동 Polling** (2026-08-15 신규): 실제 Google Push(ngrok+Watch 등록)가
  없는 개발 환경에서도 "다른 화면에 있어도 새 메일이 알아서 뜬다"를 흉내내기 위해, `proposal-notifications.tsx`가
  **2분마다** `/api/v1/dev/gmail-sync`·`/api/v1/dev/calendar-sync`를 자동으로 호출한다. Provider가
  앱 최상단에서 상시 유지되므로 제안함 화면이 아니어도 계속 돈다. 이미 승인된 항목은 걸러지지만(#19),
  아직 승인/무시하지 않은 같은 후보는 주기마다 다시 발행될 수 있다 — 이땐 카드가 갱신될 뿐 이미 알림을
  띄운 `proposal_id`를 기억해 **Toast·데스크톱 알림은 중복으로 안 뜨도록** 걸러낸다(승인/무시로
  카드가 사라지면 이 기억도 같이 지워져 나중에 다시 나오면 새 알림으로 취급). Dev Route가 꺼져 있거나
  Calendar 403(Scope 부족 등) 같은 오류는 화면에 띄우지 않고 콘솔에만 조용히 남긴다.
  > **Toast 표시 기준(2026-08-18 갱신)**: 카드 목록(`proposals`)엔 유효한 제안이 전부 올라오지만, Toast·
  > 데스크톱 알림은 출처별로 별도 기준을 추가로 적용한다(`shouldToastProposal`, `lib/workmate-format.ts`) —
  > **이메일은 "마지막 동기화 이후 새로 온 것만"**: 메일의 수신 시각(`metadata.received_at`)이 직전
  > 백그라운드 동기화가 끝난 시각(`lastSyncAt`)보다 늦은 것만 Toast를 띄운다. `lastSyncAt`은
  > `localStorage`(`workmate-ui:last-gmail-sync-at`)에 남겨 Provider가 재마운트돼도 유지된다 — 이
  > 앱은 로그인 Token을 어떤 storage에도 저장하지 않아(`lib/workmate-auth.tsx`) 새로고침·Google 계정
  > 연결 팝업 왕복마다 `ProposalNotificationsProvider`가 다시 마운트되는데, 예전엔 "마운트 직후 첫
  > 동기화 사이클(적체분 구간)"이라는 재마운트마다 초기화되는 기준을 썼다(2026-08-17) — 그래서 새로고침
  > 직후 도착한 진짜 새 메일도 "적체분"으로 오분류돼 다시는 Toast가 뜨지 않는 문제가 있었다(같은
  > `proposal_id`는 한 번 판정되면 재평가 안 함). `lastSyncAt`이 아직 없으면(이 브라우저에서 첫 실행)
  > 적체분으로 보고 건너뛴다. **Calendar는 "당일 일정만"**(기존과 동일, 변경 없음): `due_at`(일정 시작
  > 시각)이 브라우저 로컬 날짜 기준 오늘이 아니면 Toast를 건너뛴다 — 도착 시점과 무관하게 일정
  > 날짜만 본다. 두 기준 모두 "제안함에는 이미 다 보인다"가 전제라, 카드 자체를 놓치는 일은 없다.
- **연결 상태 표시**: SSE 연결 여부, 데스크톱 알림 허용 여부를 화면 상단에 표시. SSE 연결이 끊기면
  오류 메시지도 함께 표시
- **인증 필요 안내**: Bearer Token이 없으면 제안함 화면 대신 Token 입력 안내 화면(`RequireToken`)을 보여줌
- **미확인 배지 자동 해제**: 제안함 화면에 들어오면(또는 화면을 보는 중 새 제안이 도착하면) 전체를
  "확인함" 처리해 상단 종 아이콘의 미확인 숫자를 0으로 리셋함
- **빈 상태 안내**: 도착한 제안이 하나도 없으면 "위 'Gmail 동기화 실행'을 눌러 실제 메일로 테스트하거나,
  실제 Gmail Watch(Pub/Sub)가 제안을 발행하길 기다리세요" 안내 표시
- **승인/무시 후 카드 자동 제거**: 승인 또는 무시에 성공하면 카드 안에 결과 메시지("Task 생성:
  {task_id}" 또는 "무시했습니다")를 잠깐 보여준 뒤 **1.2초 후 카드가 목록에서 자동으로 사라짐**

**전역 Toast (`ToastStack.tsx`, 제안함 화면이 아니어도 항상 뜸)**:

- 화면 아무 곳에서나 우측 상단에 떠서 어떤 화면을 보고 있어도 새 제안 도착을 알림
- 이메일은 ✉️, Calendar는 📅 아이콘 + "새 제안 도착" 라벨 + 제안 제목 표시
- 버튼 2개만 제공: **"제안함으로 가기"**(제안함 화면으로 이동 + Toast 닫힘) / **"무시"**(Toast만 닫힘,
  제안 자체는 제안함에 그대로 남아 있어 나중에 처리 가능) — Toast에서 바로 승인/무시하지 않음
- **6초 후 자동으로 사라짐**
- 상단 종 아이콘(`page.tsx`): 클릭하면 제안함 화면으로 이동, 미확인 건수가 9건을 넘으면 "9+"로 표시

**브라우저 데스크톱 알림 상세**: 제목은 항상 "Workmate — 새 제안 도착" 고정, 본문은 제안 제목, 클릭하면
브라우저 창에 포커스만 이동(제안함 화면으로 자동 전환은 안 함)

**알려진 한계**: SSE 연결이 끊기면 **자동 재연결을 시도하지 않음** — 구독 Effect가 `apiBase`/`token`
값이 바뀔 때만 다시 실행되므로, 네트워크가 잠깐 끊겼다 돌아와도 사용자가 새로고침하거나 Token을 다시
입력하기 전까지는 "SSE 연결 안 됨" 상태로 남아 있음.

**부분 구현 — [갭 문서 #19](14-workmate-ui-integration-gaps.md#19-gmail-수동-동기화가-이미-처리한-메일을-다시-제안으로-노출함)**
(2026-08-15 구현 완료 상태 반영): Gmail 수동 동기화는 이제 **이미 승인한 메일은 자동으로 건너뛴다**
(`_already_approved` 검사, LLM 호출 자체를 안 함). **무시한 메일**은 여전히 구분하지 않고 매번 다시
노출한다 — [04-scenarios.md](04-scenarios.md) §7("무시한 후보는 다음 브리핑에 다시 표시될 수 있다")과
"제안은 DB에 저장하지 않는다" 원칙에 저촉될 수 있어 제품 결정이 아직 필요하기 때문이다.

**Calendar 동기화 (2026-08-15 구현 완료)** — [갭 문서 #1](14-workmate-ui-integration-gaps.md#1-google-calendar-일정-제안--http-진입점만-없음-2026-08-15-정정):

- "Calendar 동기화 실행" 버튼으로 **오늘부터 한 달 안**의 일정 중 신규·확정 건을 수동으로 즉시 제안
  생성 (Gmail 버튼 바로 아래에 같은 패턴으로 추가됨). 이미 승인된 일정과 어제까지의 일정·한 달 넘게
  남은 일정·미확정·취소된 일정은 자동으로 제외한다.
  > **정정(2026-08-17)**: "다가오는 일정"의 범위를 `now`(정확히 이 순간) 이후 무제한에서 **로컬
  > (Asia/Seoul) 자정 기준 오늘부터 정확히 한 달 뒤(같은 일자, 없으면 그 달 마지막 날)까지**로
  > 바꿨다(사용자 요청 "제안함 Calendar 필터: 오늘 이후 → 오늘부터 한달"). 하한을 `now`에서 오늘
  > 자정으로 낮춘 것은 이미 시작한 오늘 일정을 제외하던 부작용도 함께 고쳤다 — 종일 일정은 UTC
  > 자정으로 파싱돼(`app/dev_calendar_sync_api.py`의 `_parse_event_start`) KST 오후 시간대엔 "오늘의
  > 종일 일정"조차 조용히 걸러지는 시간대 버그가 있었다. 상한을 새로 둔 것은 끝없이 먼 미래 일정까지
  > 제안으로 쌓이지 않게 하기 위해서다.
- 실제 Google Calendar 일정 변경 시 자동으로 제안 도착 (Webhook 기반) — 코드·단위 테스트는 완료됐지만
  실제 Google 계정으로 ngrok 노출 후 Webhook이 정말 도착하는지의 **실환경 E2E 검증은 아직 안 함**
  (별도 인프라 작업)

### 조회값 정의

`app/proposal_api.py`의 `TaskProposal`(SSE 실제 전송 페이로드)과 `lib/workmate-types.ts`를 대조한 결과다.

#### 1. 제안 카드 — SSE `task_proposal` 이벤트 페이로드

`GET /api/v1/notifications/stream`으로 수신, `TaskProposal.as_payload()`가 그대로 JSON化.

| 필드               | 타입                    | 설명                                                                                                                                                                   |
| ------------------ | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `proposal_id`      | string                  | 제안 고유 ID. `email-{source_id}` 또는 `calendar-{calendar_id}:{event_id}` 형태                                                                                        |
| `user_id`          | string                  | 제안 대상 사용자                                                                                                                                                       |
| `source_type`      | `"email" \| "calendar"` | 제안 출처 — 카드의 MAIL/CALENDAR 배지에 사용                                                                                                                           |
| `source_id`        | string                  | 출처 내 원본 식별자. email은 `message_id`(여러 후보면 `message_id:index`), calendar는 `{calendar_id}:{event_id}`                                                       |
| `title`            | string                  | 제안된 Task 제목 — 카드 상단, 수정 입력창 기본값                                                                                                                       |
| `assignee_user_id` | string                  | 제안된 담당자 — 항상 제안 대상 본인                                                                                                                                    |
| `due_at`           | string(ISO) \| null     | 제안된 마감일 — email은 항상 `null`(마감일 개념 없음), calendar는 일정 시작 시각(2026-08-17부터 실제로 채워짐, 이전엔 항상 `null`이었음 — Toast "당일 것만" 판정에 씀) |
| `priority_hint`    | number \| null          | 제안된 중요도(0~10)                                                                                                                                                    |
| `metadata`         | object \| null          | 출처별로 다름 (아래)                                                                                                                                                   |

**`metadata` — `source_type=email`일 때**

| 필드          | 설명                                                                         |
| ------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `thread_id`   | Gmail Thread ID                                                              |
| `snippet`     | 메일 본문 일부(카드에 회색 텍스트로 표시, HTML 엔티티 디코딩 적용)           |
| `reason`      | LLM이 이 항목을 할 일로 판단한 근거(💡 라인) — LLM 추출 실패 시 없을 수 있음 |
| `received_at` | string(ISO) \| 없음                                                          | 메일 수신 시각(Gmail `internalDate`에서 파싱, 2026-08-17 신규) — 카드의 "수신" 날짜 표시와 정렬(수신 최신순)에 쓴다. `messages.list`만으로 온 메시지는 아직 개별 조회 전이라 없을 수 있다 |

**`metadata` — `source_type=calendar`일 때** (`publish_calendar_proposal` 기준)

| 필드          | 설명                    |
| ------------- | ----------------------- |
| `calendar_id` | Google Calendar ID      |
| `event_id`    | Calendar Event ID       |
| `html_link`   | Google Calendar 웹 링크 |

#### 2. 승인/무시 요청 (`ProposalCard`가 보내는 값)

| 필드                      | email 요청                                                            | calendar 요청              |
| ------------------------- | --------------------------------------------------------------------- | -------------------------- |
| 식별자                    | `message_id`                                                          | `calendar_id` + `event_id` |
| `decision`                | `"approve" \| "ignore"`                                               | 동일                       |
| `task`                    | `{title, assignee_user_id, due_at, priority_hint}` — `approve`일 때만 | 동일                       |
| `allow_similar_duplicate` | 기본 `false`, "그래도 추가" 클릭 시 `true`                            | 동일                       |

**HTTP 헤더**: 모든 승인/무시 요청에 `Idempotency-Key: {proposal_id}-{decision}-{timestamp}` 형식의 키를
매번 새로 생성해 붙임 (`lib/proposal-review.ts`). 같은 요청이 중복 전송돼도 서버가 한 번만 처리하도록
하는 멱등성 보장 헤더 — [02-a2a-interface.md](02-a2a-interface.md) §5.2 "모든 승인 POST는
`Idempotency-Key`를 사용한다"에 대응.

#### 3. 승인/무시 응답 (`ProposalReviewResult`)

| 필드                        | 설명                                                                |
| --------------------------- | ------------------------------------------------------------------- |
| `decision`                  | 처리된 결정                                                         |
| `source_type` / `source_id` | 처리된 원본                                                         |
| `created`                   | 새 Task를 만들었으면 `true`, 기존 Task를 재사용했으면 `false`(멱등) |
| `task`                      | 생성/재사용된 Task 전체                                             |

**409 충돌 시** (`SimilarTaskConflict`): `{code: "SIMILAR_TASK_EXISTS", tasks: Task[]}` — 유사 Task 목록이
카드 안 노란 박스에 표시됨.

#### 4. "Gmail 동기화 실행" 버튼 응답 (`GmailSyncResponse`)

| 필드        | 설명                                                                                                                                                                                       |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `fetched`   | 조회한 메일 수                                                                                                                                                                             |
| `published` | 발행된 제안 목록: `{message_id, source_id, title}[]`                                                                                                                                       |
| `skipped`   | 발행 안 된 메일: `{message_id, reason}[]` — `gmail_fetch_failed`/`llm_extraction_failed`(Provider·LLM 실패) 또는 `already_approved`(이미 승인된 메일, 2026-08-15부터 LLM 호출 없이 걸러짐) |
| `note`      | 사용자에게 보여줄 안내 문구                                                                                                                                                                |

#### 5. "Calendar 동기화 실행" 버튼 응답 (`CalendarSyncResponse`, 2026-08-15 신규)

| 필드        | 설명                                                                                                                                                                                                                       |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fetched`   | 조회한 일정 수                                                                                                                                                                                                             |
| `published` | 발행된 제안 목록: `{source_id, title}[]` — `source_id`는 `{calendar_id}:{event_id}`                                                                                                                                        |
| `skipped`   | 발행 안 된 일정: `{source_id, reason}[]` — `not_confirmed_or_out_of_range`(미확정·취소된 일정 또는 범위 밖 일정 — 어제까지, 또는 오늘부터 한 달 넘게 남음, 2026-08-17 기준 갱신) 또는 `already_approved`(이미 승인된 일정) |
| `note`      | 사용자에게 보여줄 안내 문구                                                                                                                                                                                                |

---

## 🎙️ 회의 녹음 (`Meeting.tsx`)

[04-scenarios.md](04-scenarios.md) §3, [09-ui-design.md](09-ui-design.md) §5.1, [02-a2a-interface.md](02-a2a-interface.md) §2·§5.2,
[03-data-priority-rules.md](03-data-priority-rules.md) §1, [07-technical-specification.md](07-technical-specification.md) §9.1·§9.3·§13.1을
종합한 목표 정의다. 이 화면은 **회의 생성부터 LLM이 Action Item 후보를 자동 추출하는 데까지**를 담당한다
— 추출된 결과를 사용자에게 보여주고 Task로 등록하는 부분은 [🎙️ 회의 녹음의 다음 화면인 📁 회의
관리](#-회의-관리-archivetsx)가 담당한다(04 §3의 연속된 시나리오를 화면 경계에 맞춰 나눈 것).

### 전체 흐름 중 이 화면이 담당하는 부분 (04 §3 1~6단계)

```
1. 회의 메타데이터 생성 + 입력 방식 선택 (업로드 or 실시간)
2. 원본 음성 확정 (업로드 완료 또는 실시간 녹음 종료)
3. 원본 음성 준비되면 비동기 analyze_meeting A2A Task 생성
4. 원본 음성 기반 최종 STT 수행 → timestamp 포함 보정 원문 저장
5. LLM이 통합 요약 Text + Action Item 후보 자동 추출        ← 이 화면은 여기까지
──────────────────────────────────────────────────────────
6. (백엔드 자동) 회의록을 meeting_chunks에 embedding과 함께 저장
7. UI에서 Action Item 후보 수정·승인·거절                    ← 여기부터 📁 회의 관리
8. 승인된 Action Item만 Task DB에 등록
```

### 목표 기능

- **회의 생성과 입력 방식 선택**: 사용자는 회의를 만들 때 **실시간 녹음** 또는 **녹음 파일 업로드** 중
  하나를 선택한다. 회의 생성(메타데이터)과 녹음 입력은 서로 분리된 개념이며, 두 입력 방식 모두 원본
  음성이 최종 확정된 뒤에는 동일한 `analyze_meeting` Workflow를 호출한다 (02 §5.2, 04 §3).

- **실시간 녹음**:
  - 녹음 진행 중 **녹음 시간**, **연결 상태**, **시작·일시정지·종료** 버튼, **임시 STT 자막**을 표시한다
    (09 §5.1).
  - 마이크 음성은 WebSocket으로 전송한다. Chunk 형식은 mono PCM16, 24kHz, 기본 200ms 단위다 (07 §9.3).
  - 서버는 각 Chunk에 순번을 매겨 검증하고 `RecordingSession.last_chunk_no`로 마지막 수신 지점을
    기록한다. 연결이 끊기면 **마지막으로 전송된 Chunk 다음부터 재연결**해 이어 보낸다 — 처음부터
    다시 녹음하지 않는다 (09 §5.1, 07 §9.3·§14).
  - 임시 자막은 Partial Delta로 오고, 화면은 이를 누적해서 보여준다. 화자 분리는 MVP 범위에서 제외한다
    (07 §9.3).
  - 녹음 종료 시 지금까지의 Chunk를 **하나의 원본 음성 파일로 병합**해 R2에 업로드한다(Chunk마다
    개별 객체로 저장하지 않음) (07 §13.1). 종료 직후에는 **최종 STT와 분석 진행 상태**를 화면에
    표시한다 (09 §5.1).

- **녹음 파일 업로드**:
  - 업로드 전에 **형식**(WAV·MP3·M4A 등 STT Provider가 지원하는 포맷, 07 §9.3)과 **크기**(500MB 이하,
    07 §14)를 검증한다.
  - 브라우저는 `POST /api/v1/meetings/{id}/recordings`에 `multipart/form-data`로 파일을 **Workmate
    서버에 직접 올리고**, 서버가 그 파일을 R2에 `PutObject`한다(02 §5.2, 07 §13.1). R2 API Key·Access
    Key는 어떤 경우에도 브라우저에 전달하지 않는다 (09 §5.1) — Presigned URL 직접 업로드는 채택하지
    않는다(아래 정정 참고).
  - 업로드가 끝나면 서버가 `HeadObject`로 MIME·크기·checksum을 확인한 뒤에만 `analyze_meeting` Task를
    시작한다 (07 §13.1).
  - 업로드 완료 후 화면은 실시간 녹음과 같은 **분석 진행 화면**으로 이동한다 (09 §5.1).

- **원본 음성 저장**: 파일 업로드·실시간 녹음 모두 최종 원본 음성을 R2에 저장하고, 만료되는 Presigned
  URL이 아니라 **R2 Object Key**를 `Meeting.source_audio_uri`에 확정해 저장한다 (03 §1.2). Object Key
  규칙은 `users/{user_id}/meetings/{meeting_id}/source/{file_id}.{ext}`다 (07 §13.1).

> **정정(2026-08-16)**: 이전 판은 07-technical-specification.md §13.1이 "브라우저가 Presigned URL로
> R2에 직접 업로드"라고 정의한다고 적고, 02-a2a-interface.md §5.2의 `multipart/form-data` 백엔드 경유
> 정의와 서로 다른 두 경로가 병존한다고 기록했었다. 실제로는 07 §13.1이 **이미 2026-08-15에**
> 02 방식(백엔드 경유 `multipart/form-data`)으로 정정돼 있었다(`workmate-ui-integration-gaps.md`
> #14: "이미 프론트가 이 모양으로 파일을 보내고 있어 재작업이 가장 적음", "Presigned URL 직접 업로드는
> 채택하지 않는다"고 명시) — 이 문서만 그 정정을 반영하지 못한 채 예전 서술을 그대로 갖고 있었다.
> 사용자 확인(17번 갭 문서 #4)을 거쳐 이 문서도 실제 구현·07번 문서와 같은 02 방식으로 맞춘다 — 더
> 이상 "결정 대기"가 아니라 확정된 설계다.

- **STT (3~4단계)**: 원본 음성이 확정되면 비동기 `analyze_meeting` A2A Task를 생성한다(02 §2.1 — `analyze_meeting`은
  "장기 Task"로 분류됨). 실시간 녹음 중 나온 임시 자막은 최종본이 아니다 — **원본 음성이 확정된 뒤
  처음부터 다시 최종 STT를 수행**해 timestamp가 포함된 보정 원문을 만든다(04 §3, 07 §9.3). Provider는
  OpenAI `gpt-4o-transcribe`, 언어는 한국어(`ko`), 화자 분리는 MVP 범위에서 제외한다(07 §9.3).

- **LLM 분석 — Action Item 자동 추출 (5단계, 이 화면의 마지막 책임)**: 통합 요약 Text(주요 논의·결정·이슈
  포함)와 Action Item 후보를 **LLM이 자동으로** 추출한다(04 §3). Action Item 필드는 `title`, `assignee`,
  `due_at`, `description`, `evidence_span`, `evidence_text`, `confidence`다(03 §1.1). **LLM은
  `evidence_span`(근거 위치)만 지정**하고, **서버가 최종 회의록의 해당 구간에서 원문을 직접 추출**해
  `evidence_text`로 저장한다 — LLM이 생성한 인용문을 그대로 신뢰하지 않는다(02 §2.3, 07 §9.1). 이 시점의
  Action Item은 전부 `approval_status=pending`이며, **사용자에게 보여주고 승인받는 것은 이 화면의 책임이
  아니다** — [📁 회의 관리](#-회의-관리-archivetsx)로 넘어간다.

- **검색용 저장 (6단계, 백엔드 자동)**: 회의록을 문단/주제 단위 `MeetingChunk`로 나눠
  `embedding`(`text-embedding-3-small`, 1536차원)과 함께 PostgreSQL+pgvector에 저장한다(03 §1.2, 07 §8).
  화면에 노출되는 동작이 아니라 분석이 끝나면 자동으로 일어나며, 이후 회의록 검색(`search_meetings`)의
  근거로 쓰인다.

- **`analyze_meeting`은 장기 Task로 분류된다** (02 §2.1, §6.2: `SUBMITTED → WORKING(STT) →
WORKING(LLM 분석) → ...`). 이 화면은 분석 시작을 요청하고 진행 상태(`WORKING`)까지만 다루며, 검토
  대기(`INPUT_REQUIRED`) 이후 상태 전이는 회의 관리 화면 몫이다.

### 조회값 정의

#### 1. 회의 생성 — `POST /api/v1/meetings`

| 필드         | 방향       | 설명                          |
| ------------ | ---------- | ----------------------------- |
| `title`      | 요청       | 회의 제목                     |
| `started_at` | 요청(선택) | 회의 시작 시각                |
| `meeting_id` | 응답       | 신규 회의 고유 ID             |
| `user_id`    | 응답       | 회의 소유 사용자              |
| `ended_at`   | 응답       | 종료 시각(생성 시점엔 `null`) |
| `created_at` | 응답       | 생성 시각                     |

(필드는 03 §1.1 `Meeting` 엔터티, 응답 형태는 02 §5.2 REST API 표 기준)

#### 2. 녹음 파일 업로드 — `POST /api/v1/meetings/{id}/recordings` (02 §5.2, 07 §13.1 — 위 정정 참고)

| 필드           | 방향 | 설명                                                        |
| -------------- | ---- | ----------------------------------------------------------- |
| `file`         | 요청 | `multipart/form-data`로 전달되는 음성 파일                  |
| `recording_id` | 응답 | 녹음 파일 고유 ID                                           |
| `filename`     | 응답 | 원본 파일명                                                 |
| `content_type` | 응답 | MIME 타입                                                   |
| `size_bytes`   | 응답 | 파일 크기                                                   |
| `sha256`       | 응답 | 파일 checksum                                               |
| `object_key`   | 응답 | R2 Object Key (`Meeting.source_audio_uri`에 대응, 07 §13.1) |

#### 3. 실시간 음성 Chunk와 세션 시작·종료 — `WS /api/v1/meetings/{id}/recording-stream` (02 §5.2 각주 `[^recording-session]`, 07 §9.3)

> **정정(2026-08-16)**: 이전 판은 세션 시작·종료를 `POST .../recording-sessions`와
> `POST .../recording-sessions/{session_id}:complete`라는 별도 REST 엔드포인트로 정의했다.
> 실제로는 이런 REST 엔드포인트가 없다 — 이 WebSocket에 **연결하는 것 자체가 세션 시작**이고,
> **연결이 끊기면**(정상 종료든 접속 끊김이든) 서버가 그 시점까지 받은 Chunk를 자동으로 병합해
> 원본 음성을 확정한다(`_finalize_recording_session()`). 02번 문서도 이미 같은 결정을 각주로
> 반영해 뒀다(`[^recording-session]`, 2026-08-15 결정, 17번 갭 문서 #5·#8) — 이 문서만 아직
> 갱신되지 않았던 것을 실제 코드(`app/recording_stream.py`) 재확인으로 발견해 바로잡는다.
> "녹음 중간에 끊겼다가 이어서 재개" 이상의 명시적 세션 제어(예: 사용자가 직접 일시정지가 아닌
> 완전히 새 세션으로 재시작)가 필요해지면 그때 별도 Route를 추가한다.

| 필드                         | 방향            | 설명                                                           |
| ---------------------------- | --------------- | -------------------------------------------------------------- |
| (WebSocket 연결 자체)        | 클라이언트→서버 | 세션 시작 신호 — 별도 요청 Body 없음                           |
| `chunk_no`                   | 클라이언트→서버 | 순번(재연결 시 이어받기 기준)                                  |
| `audio`                      | 클라이언트→서버 | mono PCM16, 24kHz, 200ms 단위 음성 데이터                      |
| (연결 종료)                  | 클라이언트→서버 | 세션 완료 신호 — 서버가 수신한 Chunk를 병합해 원본 음성을 확정 |
| `type: "chunk_ack"`          | 서버→클라이언트 | Chunk 수신 확인(`chunk_no`, 중복 여부)                         |
| `type: "transcript.partial"` | 서버→클라이언트 | 임시 자막 이벤트                                               |
| `chunk_no`, `text`           | 서버→클라이언트 | 해당 Chunk의 임시 STT 텍스트(Partial Delta 누적)               |

#### 4. 회의 분석 시작 — `analyze_meeting` 내부 스킬챗 요청 (02 §5.2 각주 `[^analysis-route]`)

> **정정(2026-08-16)**: 이전 판은 이걸 `POST /api/v1/meetings/{id}/analysis`라는 전용 REST
> 엔드포인트로 정의했다. 실제로는 이런 엔드포인트가 없다 — `POST /api/v1/internal/skill-chat/messages`에
> `skill_id: "analyze_meeting"`으로 보내는 스킬챗 요청 하나가 분석 시작과 결과 수신을 겸한다
> (`Archive.tsx`의 `useSkillRunner("analyze_meeting")`). 02번 문서도 이미 같은 결정을 각주로
> 반영해 뒀다(`[^analysis-route]`, 2026-08-15 결정, 17번 갭 문서 #6·#24·#25) — 이 문서만 아직
> 갱신되지 않았던 것을 실제 코드 재확인으로 발견해 바로잡는다. 이 요청·응답 형태는 [🔍 회의록
> 검색](#-회의록-검색-searchtsx)이 `search_meetings`를 호출하는 방식과 같은 스킬챗 계약을 그대로
> 쓴다.

| 필드                                                    | 방향         | 설명                                                                                                                                    |
| ------------------------------------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| `skill_id: "analyze_meeting"`, `meeting_id`             | 요청         | 최종 Transcript 기준 분석 시작                                                                                                          |
| `state`                                                 | 응답         | 스킬챗 Task 상태(02 §6.1) — 요청은 즉시 `submitted`로 끝난다(아래 정정 참고)                                                            |
| `task_id`                                               | 응답         | `GET /api/v1/internal/skill-chat/tasks/{task_id}` Polling에 쓸 ID                                                                       |
| `artifact.data.summary`, `artifact.data.action_items[]` | Polling 응답 | 분석 결과 — 완료(`TASK_STATE_COMPLETED`) 뒤 `GET /api/v1/meetings/{id}/analysis`(위 [📁 회의 관리](#-회의-관리-archivetsx) #1)로 재조회 |

> **정정(2026-08-16, 17번 갭 문서 #7·#18 구현 완료)**: 위 표는 이제 실제 동작과 일치한다 —
> `analyze_meeting` 요청은 STT+LLM 분석이 끝날 때까지 기다리지 않고 즉시 `TASK_STATE_SUBMITTED` +
> `task_id`로 응답한다. 실제 분석은 백그라운드에서 `TASK_STATE_WORKING`을 거쳐
> `TASK_STATE_COMPLETED`(또는 실패 시 `TASK_STATE_FAILED` + 오류 메시지)로 끝나며, 클라이언트는
> `GET /api/v1/internal/skill-chat/tasks/{task_id}`를 Polling해 완료를 확인한 뒤
> `GET /api/v1/meetings/{id}/analysis`로 구조화된 결과를 가져온다(Task Artifact 자체엔 요약
> 원문 텍스트만 있고 구조화 JSON은 없음). `Archive.tsx`는 `usePollingSkillRunner` Hook으로 이
> 흐름을 감싼다. 나머지 4개 Skill(`daily_briefing`·`weekly_report`·`rank_priorities`·
> `search_meetings`)은 실측상 오래 안 걸려 여전히 동기 응답이다.

---

## 📁 회의 관리 (`Archive.tsx`)

[04-scenarios.md](04-scenarios.md) §3, [09-ui-design.md](09-ui-design.md) §5.4, [02-a2a-interface.md](02-a2a-interface.md) §5.2·§5.3·§6.2,
[03-data-priority-rules.md](03-data-priority-rules.md) §1을 종합한 목표 정의다. 이 화면은 [🎙️ 회의
녹음](#-회의-녹음-meetingtsx)이 자동 추출한 Action Item 후보를 **사용자에게 보여주고**, 검토(승인·수정·거절)
결과에 따라 **Task로 등록**하는 부분을 담당한다(04 §3의 7~8단계). 아래는 이 흐름만 다루며, 회의
목록·참석자 표시나 전체 회의록 화면(09 §5.2·§5.3) 같은 이 화면의 나머지 책임은 아직 이 문서에 작성하지
않았다.

### 목표 기능

- **분석 결과 표시**: 회의 분석이 끝나면 LLM이 만든 **요약 Text**와 **Action Item 후보 목록**을 보여준다.
  이건 회의 분석 직후의 **임시 검토 UI**이며, 별도의 Action Item 전용 조회 화면은 따로 만들지 않는다
  (04 §3, 09 §5.4).

- **Action Item 검토**: 사용자는 각 후보를 **승인(approve)·수정(edit)·거절(reject)** 할 수 있고, 여러
  후보를 한 번에 처리할 수 있다(02 §5.3). `edit`일 때만 `changes`(담당자·마감일 등)를 허용하며,
  `evidence_text`(서버가 원문에서 추출한 근거)는 읽기 전용이라 수정할 수 없다(02 §5.3).

- **Task 등록**: **승인된 Action Item만** Task로 등록하며 `source_type=action_item`,
  `source_id=action_item_id`로 저장한다(04 §3, 03 §1.2). 거절된 후보는 Task를 만들지 않는다.

- **승인 후 근거 연결**: Task로 등록된 뒤에는 할 일 상세에서 `evidence_text` + "회의록에서 보기"로 근거를
  확인할 수 있다. 클릭하면 `/meetings/{meeting_id}?highlight_meeting_chunk_id={id}`로 이동해 전체
  회의록에서 해당 근거 라인이 강조된다(09 §5.4).

- **A2A Task 상태 전이** (02 §6.2), 이 화면이 담당하는 구간:

  ```
  ... → WORKING(LLM 분석) → INPUT_REQUIRED(Action Item 검토) → WORKING(Task 등록) → COMPLETED
  ```

  검토 대기 중에는 `INPUT_REQUIRED` 상태이며, 사용자가 결정을 마치면 `WORKING`을 거쳐 `COMPLETED`로
  끝난다.

- **회의 삭제**(2026-08-17, 사용자 요청): 회의를 목록에서 Soft Delete한다(`DELETE
/api/v1/meetings/{id}`) — Recording·Transcript·Action Item·검색 색인은 그대로 두고
  `deleted_at`만 찍어, 목록·상세 조회에서 더는 보이지 않게 한다.

- **제목 자동 생성**(2026-08-17, 사용자 요청): 녹음 시점엔 아직 내용이 없어 "회의 M월 D일 HH:MM"
  같은 날짜·시각 자리표시자 제목만 붙는다(`Meeting.tsx`의 `defaultMeetingTitle()`). `analyze_meeting`이
  요약을 만드는 그 LLM 호출에 짧은 제목도 함께 요청하고(`MeetingAnalysis.title`, 추가 호출 없음),
  분석 시점 회의 제목이 그 자리표시자 패턴 그대로일 때만 실제 내용을 요약한 제목으로 바꾼다 —
  사용자가 직접 지은 제목은 건드리지 않는다.

### 조회값 정의

#### 1. 회의 분석 결과 조회 — `GET /api/v1/meetings/{id}/analysis` (02 §5.2)

> **정정(2026-08-16, 17번 갭 문서 #10 구현 완료)**: 실제 구현은 A2A Task를 조회하지 않는다 —
> `analyze_meeting`이 분석 직후 저장해 둔 `summary`·`action_items`를 회의 Repository에서
> 그대로 재조회하는 단순 GET이라 `task_id`/`state` 필드가 없다. 한 회의를 여러 번 분석하면
> Task ID가 매번 새로 생기는데(내부 스킬챗의 `analyze_meeting` 요청마다 새 `task_id`), 이 GET은
> 특정 Task가 아니라 "이 회의의 가장 최근 저장된 결과"를 돌려주는 계약이라 Task 상태 자체를
> 노출할 이유가 없다고 판단했다. 분석 **실행 중** 진행 상태를 보려면(제출됨/실행 중 등)
> `analyze_meeting` 요청이 돌려준 `task_id`로 `GET /api/v1/internal/skill-chat/tasks/{task_id}`를
> Polling한다(17번 갭 문서 #7).

| 필드             | 설명                                         |
| ---------------- | -------------------------------------------- |
| `meeting_id`     | 대상 회의                                    |
| `summary`        | LLM이 만든 통합 요약 Text                    |
| `action_items`   | Action Item 후보 배열(아래 #2 필드)          |
| `transcript_ref` | 근거로 쓰인 최종 Transcript 중 하나의 참조   |
| `source_refs`    | 근거 출처 ID 목록(Transcript·Action Item ID) |

#### 2. Action Item 필드 (03 §1.1 `ActionItem`)

> **정정(2026-08-16, 17번 갭 문서 #10 구현 완료)**: 담당자 필드명은 `assignee`가 아니라
> `assignee_user_id`다 — 승인 Schema(`docs/schemas/workmate-skill-schemas.schema.json`)와
> `analyze_meeting`이 실제로 만드는 구조화 결과가 이미 이 이름을 쓰고 있었다(이 문서만 예전
> 이름이 남아 있었다).

| 필드               | 설명                                                            |
| ------------------ | --------------------------------------------------------------- |
| `action_item_id`   | 후보 고유 ID                                                    |
| `title`            | 수행할 업무                                                     |
| `assignee_user_id` | 담당자, 불명확하면 `null`                                       |
| `due_at`           | 마감 시각, 불명확하면 `null`                                    |
| `description`      | 세부 내용                                                       |
| `evidence_span`    | 근거 `meeting_chunk_ids`, `start_ms`, `end_ms`                  |
| `evidence_text`    | 근거 구간에서 **서버가 추출한** 읽기 전용 원문(LLM 인용문 아님) |
| `confidence`       | AI 추출 신뢰도                                                  |
| `approval_status`  | `pending`/`approved`/`rejected`                                 |

#### 3. Action Item 검토 — `POST /api/v1/meetings/{id}/actions:review` (02 §5.2·§5.3)

| 필드                         | 방향 | 설명                                                              |
| ---------------------------- | ---- | ----------------------------------------------------------------- |
| `decisions[]`                | 요청 | 여러 후보를 한 번에 처리하는 배열                                 |
| `decisions[].action_item_id` | 요청 | 대상 Action Item                                                  |
| `decisions[].decision`       | 요청 | `approve`/`edit`/`reject` 중 하나                                 |
| `decisions[].changes`        | 요청 | `edit`일 때만 허용(담당자·마감일 등). `evidence_text`는 변경 불가 |
| `approval_status`, `task_id` | 응답 | 반영 결과, 승인 시 생성된 Task ID                                 |

#### 4. Task 상세의 회의 근거 — `meeting_evidence` (02 §5.3) — ✅ 완료(2026-08-16, 17번 갭 문서 #11, 부분)

`source_type=action_item`인 Task 상세 응답에 `Task → ActionItem → Meeting` 조인으로 구성해 포함한다
(별도 컬럼 저장 없음 — Task의 `source_id`를 `{meeting_id}:{action_item_id}`로 저장해 두고 조회
시점에 되짚는다). 실제로 표시되는 화면은 할 일 관리 쪽이지만, 값 자체는 이 화면에서 만든 승인
결과에서 비롯되므로 여기 기록한다.

| 필드                          | 설명                                                                                                                             |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `meeting_id`, `meeting_title` | 근거 회의                                                                                                                        |
| `action_item_id`              | 근거가 된 Action Item ID                                                                                                         |
| `evidence_text`               | 승인 당시 확정된 근거 원문                                                                                                       |
| `meeting_chunk_id`            | 근거 Transcript Chunk ID(전체 회의록에서 강조할 위치 — `evidence_span`의 `start_ms`/`end_ms`는 아직 Task 응답에 포함하지 않는다) |

> **부분 구현 안내(2026-08-16)**: "회의록에서 보기"를 누르면 이동하는 화면은 아직 15번 문서가
> 정의하는 `highlight_meeting_chunk_id` 강조 이동이 아니라, 요약·Action Item만 보여주는 간이형
> 회의 상세다(17번 갭 문서 #13) — "전체 회의록"(Transcript 원문 화면) 자체가 이 문서에 아직
> 정의되지 않았고, 프론트에 URL Query Parameter 라우팅도 없다.

---

## 📋 할 일 관리 (`Tasks.tsx`)

[04-scenarios.md](04-scenarios.md) §6, [09-ui-design.md](09-ui-design.md) §2·§5.4, [02-a2a-interface.md](02-a2a-interface.md) §5.2·§6.5,
[03-data-priority-rules.md](03-data-priority-rules.md) §1.1·§1.3·§2를 종합한 목표 정의다. 이 화면은
사용자가 직접 만든 Task와, [📬 제안함](#-제안함-proposalstsx)·[📁 회의 관리](#-회의-관리-archivetsx)에서
승인돼 자동으로 생성된 Task를 **한 곳에서 조회·수정·삭제**하는 화면이다 — Task 생성 경로는 여러 곳이지만
조회·관리는 이 화면 하나로 모인다.

### 목표 기능

- **목록 조회**: 제목·상태·마감일·중요도와 수정·삭제 버튼을 표시한다. 기본 조회에서는 삭제된
  Task를 제외한다(09 §2.1). 최소 필터로 **상태**, **마감일**을 제공한다(09 §2.1).

- **직접 등록**: 제목(필수)·마감일(선택)·중요도(선택)를 입력해 Task를 만든다(09 §2.2). 등록·수정은
  같은 폼을 쓴다(09 §2.2). 서버가 `source_type=manual`, `source_id=null`,
  `assignee_user_id=요청 사용자 본인`을 설정하며, 이 세 필드는 화면에서 입력받지 않는다(04 §6, 09 §2.2).

  > **담당자 필드는 만들지 않는다(2026-08-15 결정)**: Workmate MVP에는 팀원 목록·초대·권한 관리 기능이
  > 없고, `assignee_user_id`는 항상 요청 사용자 본인으로만 강제 설정된다 — "담당자에게 배정"할 대상 자체가
  > 없어 입력·필터 모두 항상 값이 하나뿐인 무의미한 UI가 된다(`14-workmate-ui-integration-gaps.md` #6,
  > 02 §5.2 각주 참고). 팀 배정이 실사용에서 필요해지면 별도 기능으로 다시 설계한다.

- **수정**: 제목·마감일·중요도와 **상태**(`todo`/`in_progress`/`blocked`/`done`/`cancelled`, 03 §1)를
  수정할 수 있다(04 §6). 등록 시 상태는 항상 `todo`로 시작하고, 수정 화면에서만 상태 변경이 가능하다
  (09 §2.2).

- **삭제**: 삭제 버튼을 누르면 **Task 제목이 포함된 확인창**을 표시하고, 확인 후
  `DELETE /api/v1/tasks/{id}`를 호출한다(09 §2.3). Soft Delete로 처리해 DB 행은 남기고 `deleted_at`만
  기록하며(03 §1.3), 삭제된 Task는 목록·브리핑·주간보고·우선순위 계산 전부에서 제외한다(03 §1.3, 04
  §6). MVP는 삭제 복구 기능도 삭제 목록 화면도 제공하지 않는다(03 §1.3, 09 §2.3).

- **회의에서 온 Task의 근거 확인**: `source_type=action_item`인 Task 상세에는 읽기 전용 `evidence_text`와
  "회의록에서 보기" 버튼을 표시한다(09 §5.4). 누르면 `/meetings/{meeting_id}?highlight_meeting_chunk_id=
{meeting_chunk_id}`로 이동해 전체 회의록에서 해당 근거 라인이 강조된다(09 §5.4, 02 §5.3) — 값 정의는
  [📁 회의 관리 #4](#4-task-상세의-회의-근거--meeting_evidence-02-53)를 그대로 따른다. Action Item 전용
  조회 화면은 따로 만들지 않는다(09 §5.4).

- **중복 생성 방지**: 이 화면에서 직접 만드는 Task는 `source_type=manual`이라 중복 검사 대상이 아니다.
  중복 검사는 제안함에서 승인할 때만 적용된다 — 같은 `(source_type, source_id)`면 기존 Task를 재사용하고,
  원본 ID는 다르지만 제목·담당자·마감일이 유사하면 재확인 후 승인해야 별도 Task가 생긴다(03 §2). Action
  Item 승인은 `action_item_id`가 Unique Key라 같은 Action Item으로 두 번 승인해도 Task가 중복 생성되지
  않는다(02 §6.5).

- **UI 상태 처리**: 저장 중에는 중복 제출을 막고, 입력 오류는 해당 필드 가까이에 표시하며, API 실패
  시 기존 입력을 유지해 재시도할 수 있게 한다(09 §3). 삭제 성공 후 목록이 비면 빈 상태 안내를
  표시한다(09 §3).

### 조회값 정의

#### 1. 목록 조회 — `GET /api/v1/tasks` (02 §5.2)

응답 순서는 **등록일시(생성 시각) 최신순**이다(가장 최근에 만든 Task가 맨 위, 2026-08-15 결정).
"최근 수정한 순서"가 아니다 — 수정·완료 처리를 해도 목록에서의 위치는 바뀌지 않는다.

| 필드                    | 방향              | 설명                                                                                                              |
| ----------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------- |
| `status`, `due_at` 범위 | 요청(선택, Query) | 최소 필터 2종(09 §2.1, 담당자 필터는 만들지 않기로 결정 — 위 참고)                                                |
| `task_id`               | 응답              | Task 고유 ID                                                                                                      |
| `title`                 | 응답              | 업무 제목                                                                                                         |
| `assignee_user_id`      | 응답              | 담당 사용자 — 항상 요청 사용자 본인과 같음                                                                        |
| `status`                | 응답              | `todo`/`in_progress`/`blocked`/`done`/`cancelled` 중 하나                                                         |
| `priority_hint`         | 응답              | 사용자가 지정했거나 외부(제안 승인 등)에서 받은 중요도 신호                                                       |
| `due_at`                | 응답              | 마감 시각                                                                                                         |
| `source_type`           | 응답              | `manual`/`action_item`/`email`/`calendar` 중 하나                                                                 |
| `source_id`             | 응답              | `manual`은 `null`, `action_item`은 ActionItem ID, `email`은 Gmail Message ID, `calendar`는 Calendar·Event ID 조합 |
| `deleted_at`            | 응답              | 기본 조회에서는 `null`인 행만 반환                                                                                |

(필드는 03 §1.1 `Task` 엔터티 기준)

#### 2. 직접 등록 — `POST /api/v1/tasks` (02 §5.2)

| 필드                                           | 방향       | 설명                                                                                                 |
| ---------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| `title`                                        | 요청       | 필수(09 §2.2)                                                                                        |
| `due_at`                                       | 요청(선택) | —                                                                                                    |
| `priority_hint`                                | 요청(선택) | —                                                                                                    |
| `task_id`                                      | 응답       | 신규 Task ID                                                                                         |
| `status`                                       | 응답       | 항상 `todo`로 시작(09 §2.2)                                                                          |
| `source_type`, `source_id`, `assignee_user_id` | 응답       | 서버가 각각 `manual`, `null`, 요청 사용자 본인으로 고정 설정 — 요청 값으로 받지 않음(04 §6, 09 §2.2) |

#### 3. 수정 — `PATCH /api/v1/tasks/{id}` (02 §5.2)

| 필드                                         | 방향                   | 설명                                                                             |
| -------------------------------------------- | ---------------------- | -------------------------------------------------------------------------------- |
| `title`, `due_at`, `priority_hint`, `status` | 요청(선택적 부분 수정) | 수정 가능 필드(04 §6) — `source_type`/`source_id`/`assignee_user_id`는 수정 불가 |

#### 4. 삭제 — `DELETE /api/v1/tasks/{id}` (02 §5.2)

| 필드                          | 방향 | 설명                                                     |
| ----------------------------- | ---- | -------------------------------------------------------- |
| (Body 없음, `task_id`는 경로) | 요청 | Soft Delete 요청 — 실제로는 `deleted_at`만 기록(03 §1.3) |

성공하면 목록에서 제거되고, 브리핑·주간보고·우선순위 재조회 시 포함하지 않는다(03 §1.3, 04 §6).
`ActionItem`에서 생성된 Task를 삭제해도 원본 Action Item과 회의 기록은 유지된다(03 §1.3).

---

## 🔍 회의록 검색 (`Search.tsx`)

[04-scenarios.md](04-scenarios.md) §4, [02-a2a-interface.md](02-a2a-interface.md) §2.1·§2.3·§2.4·§5.2·§9(오류),
[07-technical-specification.md](07-technical-specification.md) §8.2·§8.2.1을 종합한 목표 정의다. 이 화면은
과거 회의록에서 질문에 대한 근거를 찾아 **회의명·날짜·발화자가 포함된 답변**을 만드는 화면이다(02 §2.1
`search_meetings` Skill 설명). [🎙️ 회의 녹음](#-회의-녹음-meetingtsx)이 만든 `MeetingChunk`(embedding 포함,
03 §1.2)를 검색 대상으로 한다 — 즉 회의 분석이 끝나 색인된 회의만 검색된다.

### 목표 기능

- **질문 입력과 검색 실행**: 자유 형식 질문 하나를 입력해 검색을 실행한다(04 §4 1단계 "사용자
  접근권한 검증"은 인증된 본인 범위로 이미 보장됨). 질문은 공백 제외 1~1000자, 결과 개수(`limit`)는
  기본 5·최대 20이다(02 §2.3 `SearchMeetingsInput`).

- **필터**: 질문에서 날짜·회의명·참여자 조건을 추출해 검색 범위를 좁힌다(04 §4 2단계). `filters`는
  `date_from`/`date_to`(지역 날짜, 양쪽 끝 포함)·`meeting_ids[]`·`participants[]`로 구성된다(02 §2.3).
  날짜는 내부적으로 `[date_from 00:00, date_to 다음 날 00:00)`로 변환한다(02 §2.3).

- **Hybrid 검색**: Vector(pgvector Cosine) Top-K와 PostgreSQL `pg_trgm` Trigram 유사도 Top-K를 각각
  구하고, 두 순위를 **Reciprocal Rank Fusion(RRF)**으로 결합한다(07 §8.2) — 척도가 다른 두 점수를
  `0.7 × vector + 0.3 × keyword`처럼 원시 점수로 직접 더하지 않는다(04 §4 MVP 하이브리드 점수 서술은
  이 RRF 결합의 초기 설명이며, 정식 계산식은 07 §8.2 기준).

  ```text
  RRF(document) = 1 / (60 + vector_rank) + 1 / (60 + keyword_rank)
  ```

  상위 Chunk는 인접 구간까지 Context로 확장한다(07 §8.2).

- **근거 충분성 판정**: Cosine 점수 단일 임계값(예: `top_dense_score >= 0.45`)만으로 답변 가능 여부를
  정하지 않는다 — 답변 가능·불가 질문의 점수 범위가 겹쳐 정상 질문을 과도하게 거절하기 때문이다(07
  §8.2.1). 서버는 후보 Chunk의 필터 일치·실제 `chunk_id`·직접 근거 문장 존재 여부를 검증하고, Top-1/
  Top-2 점수 차이가 작거나 다중 Chunk·Metadata 질문이면 조건부 Reranker를 호출한다(기존 후보 ID만
  재정렬, 새 근거를 만들지 않음). Reranker 장애·Timeout 시에는 RRF 결과를 그대로 쓰고 `warnings`를
  추가한다(07 §8.2.1).

- **답변 생성과 출처 표시**: 근거가 충분하면 답변과 출처를 반환하고, 부족하면 근거가 없다는 것을
  명시적으로 알린다 — "관련 회의록에서 확인할 수 없습니다" 같은 문구, `insufficient_evidence: true`(04
  §4 결과, 02 §2.4). 화면은 답변 아래에 각 출처를 회의명·날짜·발화자·인용문(`quote`)과 함께 카드로
  나열한다(02 §2.4 "회의 검색 출처의 공통 형태"). **발화자(`speaker`)는 항상 `null`이다** — MVP는 화자
  분리를 지원하지 않는다(07 §9.3, [🎙️ 회의 녹음](#-회의-녹음-meetingtsx)과 같은 제약).

  > **04 §4 5단계 표현과의 차이**: 04 문서는 이 단계를 "LLM이 제공된 문맥 안에서 답변"이라고 적었다.
  > 실제로 지향하는 설계는 검색된 근거를 **그대로 인용해 조립**하는 것이지 LLM이 문장을 새로 생성하는
  > 것이 아니다 — 근거에 없는 표현이 섞여 들어갈 환각 위험을 원천 차단하기 위함이다. 07 §9.1도
  > 이에 맞춰 "검색 답변은 LLM을 거치지 않는다"로 정리돼 있다(2026-08-15 정정,
  > [16-llm-prompts.md](16-llm-prompts.md) 참고). 04 §4의 서술은 이 문서 작성 시점에 아직 정정하지
  > 않았다.

- **근거 없음 상태 처리**: `insufficient_evidence: true`(또는 시스템 오류가 아닌 검색 결과 없음)는
  실패가 아니라 정상 완료로 취급한다 — Task 상태는 `COMPLETED`로 반환하고 답변 문구로만 부족함을
  알린다(02 §9 오류 처리 원칙).

- **근거 회의록으로 이동**: 출처 카드를 누르면 [📁 회의 관리](#-회의-관리-archivetsx)가 만들 전체
  회의록 화면으로 이동해 해당 근거 Chunk가 강조된다 — `highlight_meeting_chunk_id` 메커니즘을 Task
  근거([📋 할 일 관리](#-할-일-관리-taskstsx))와 동일하게 재사용한다(09 §5.3·§5.4).

### 조회값 정의

#### 1. 회의록 검색 — `POST /api/v1/meetings/search` (02 §5.2, `search_meetings` Workflow 동일 호출)

| 필드                                   | 방향       | 설명                                                      |
| -------------------------------------- | ---------- | --------------------------------------------------------- |
| `query`                                | 요청       | 질문(공백 제외 1~1000자, 02 §2.3)                         |
| `filters.date_from`, `filters.date_to` | 요청(선택) | 지역 날짜, 양쪽 끝 포함(02 §2.3)                          |
| `filters.meeting_ids[]`                | 요청(선택) | 특정 회의로 범위 제한                                     |
| `filters.participants[]`               | 요청(선택) | 참여자로 범위 제한 — 아직 지원 안 함(아래 결정 보류 참고) |
| `limit`                                | 요청(선택) | 기본 5, 최대 20(02 §2.3)                                  |
| `answer`                               | 응답       | 근거를 조립해 만든 답변 텍스트(02 §2.4)                   |
| `sources[]`                            | 응답       | 인용 출처 배열(아래 #2 필드, 02 §2.4)                     |
| `insufficient_evidence`                | 응답       | 근거 부족 여부(02 §2.4)                                   |

> **결정 보류(2026-08-16, 17번 갭 문서 #12)**: `filters.participants[]`를 실제로 처리하려면
> `MeetingParticipant` 모델·테이블이 있어야 하는데 코드 전체에 그런 모델이 없다 — 참석자 개념
> 자체가 아직 없다(`build_search_meetings_workflow`는 이 필터가 오면 명시적
> `ValueError("participant filtering is not supported by the current meeting schema")`로
> 거절해, 조용히 무시되는 대신 분명한 오류로 드러난다). 사용자에게 확인한 결과 지금 새로 설계하지
> 않고 보류하기로 했다 — 회의 참석자 개념 자체(회의 관리의 회의 목록·참석자 화면, 이 문서가 아직
> 정의하지 않은 영역)가 먼저 설계된 뒤 함께 판단하는 게 자연스럽다는 이유다.

#### 2. 검색 출처 필드 (02 §2.4 "회의 검색 출처의 공통 형태")

| 필드               | 설명                                              |
| ------------------ | ------------------------------------------------- |
| `meeting_id`       | 근거 회의                                         |
| `meeting_title`    | 회의 제목                                         |
| `meeting_date`     | 회의 날짜                                         |
| `speaker`          | 발화자 — MVP에서는 항상 `null`(화자 분리 미지원)  |
| `meeting_chunk_id` | 인용된 Chunk ID — 전체 회의록 이동·강조에 사용    |
| `quote`            | 인용 원문(`MeetingChunk.content`에서 그대로 발췌) |

---

## 🏠 오늘 브리핑 (`Briefing.tsx`)

[04-scenarios.md](04-scenarios.md) §1, [02-a2a-interface.md](02-a2a-interface.md) §2.1·§2.3·§2.4·§9,
[03-data-priority-rules.md](03-data-priority-rules.md) §4·§6·§7, [Workmate Skill Schema](schemas/workmate-skill-schemas.schema.json)를
종합한 목표 정의다. 이 화면은 **`daily_briefing`과 `rank_priorities` 두 Skill을 함께 호출**해 하나의
화면으로 합성한다 — `daily_briefing` 결과 자체에는 순위 변동(`changes`)이 없고, 그건 `rank_priorities`
결과에만 있기 때문이다.

### 목표 기능

- **처리 흐름**: 요청 인증 → timezone/기준 시각(`as_of`) 확정 → Task·Calendar·Gmail·Meeting **네 데이터
  소스를 병렬 조회** → 정규화·중복 제거 → 우선순위 계산 → 요약 → 출력 검증 → Artifact 반환(04 §1).
  Calendar 일정과 Gmail 메일은 별도 저장 테이블 없이 **매 요청마다 Provider에서 그대로 조회**한다(04 §1).

- **Gmail 조회 범위**: 사용자 지역 시각 기준 `[직전 영업일 00:00, as_of)`(04 §1). `rank_priorities`는
  Gmail을 조회하지 않고 이미 저장된 Task 값만 쓴다(02 §5.2 본문) — 실시간 조회는 `daily_briefing`만
  한다.

- **부분 실패 허용**: 데이터 소스 중 일부 조회가 실패해도 나머지로 결과를 만들고, 실패한 소스는
  `warnings`로 알린다(04 §1). 응답 Envelope의 `data_freshness`(`task`/`calendar`/`email`/`meeting`
  각각의 마지막 갱신 시각)로 화면에 소스별 "최신/지연" 상태를 표시한다(Schema `DataFreshness`).

- **오늘 일정**(`calendar_events`): 오늘 하루의 Calendar 일정을 시간순으로 보여준다. 각 항목은
  `related_task_ids`로 이미 Task로 등록됐는지 표시한다 — 비어 있으면 미등록, 값이 있으면 등록됨(04
  §1, 02 §5.2 본문).

- **중요 업무 신호**(`important_signals`): 읽지 않은 Gmail 메일과 Calendar의 미등록 일정 후보를 모아
  보여준다(04 §1). `type`은 `email`/`calendar`/`meeting_action_item`/`task` 중 하나이며(Schema
  `ImportantSignal`), 이 중 `email`·`calendar` 두 타입이 04 §1이 설명하는 실제 신호 출처다. 각 항목도
  `related_task_ids`로 등록 여부를 표시한다(04 §1).

- **오늘의 우선순위 Top 3**: `rank_priorities` 결과의 `priorities`(최대 3개, Schema
  `maxItems: 3`)를 점수·점수 구성(`score_breakdown`)·근거(`reasons`)와 함께 보여주고(03 §6), 이전
  계산 대비 순위가 바뀐 항목은 `changes`에서 찾아 이동 배지(상승/하락/신규 진입)를 함께 표시한다(03 §7).
  **순위 변경 사유는 서버가 계산한 `PriorityChange.reason` 실제 문장을 그대로 보여준다** — 화면이 임의로
  "↑ 2단계 상승" 같은 일반 라벨만 만들어 보여주고 서버가 만든 구체적 근거 문장을 버려서는 안 된다(03
  §7).

- **새로고침**: 버튼 하나로 두 Skill을 모두 다시 호출해 갱신한다(09 §1 화면 구성 표의 "새로고침").

  > **04 §1 흐름도 표현과의 차이**: 04 문서의 처리 흐름은 "LLM 요약" 단계를 포함하고, 출력 예시의
  > `summary`도 자연어 문장("QA 서버 배포와 로그인 오류 대응이 가장 중요합니다.")이다. 하지만
  > [🔍 회의록 검색](#-회의록-검색-searchtsx)에서 정리한 것과 같은 이유로, 실제 지향 설계는 `summary`를
  > LLM이 새로 쓰지 않고 조회된 값(일정 수·신호 수·우선순위 수 등)을 결정적으로 조합해 만드는 것이다
  > (2026-08-15 정정, 07 §9.1·[16-llm-prompts.md](16-llm-prompts.md) 참고). 04 §1의 흐름도·예시
  > 문구는 이 문서 작성 시점에 아직 정정하지 않았다.

### 조회값 정의

#### 1. 오늘 브리핑 — `daily_briefing` Skill 결과 (Schema `DailyBriefingResult`)

| 필드                  | 설명                                               |
| --------------------- | -------------------------------------------------- |
| `date`                | 브리핑 기준 날짜                                   |
| `summary`             | 브리핑 요약 문장(위 LLM 관련 정정 참고)            |
| `calendar_events[]`   | 오늘 일정 배열(아래 #2 필드)                       |
| `important_signals[]` | 중요 업무 신호 배열(아래 #3 필드)                  |
| `priorities[]`        | 우선순위 Top 3(최대 3개, 아래 #5 필드와 동일 구조) |
| `source_refs[]`       | 이 결과가 근거로 쓴 출처 ID 목록(중복 없음)        |

#### 2. `calendar_events[]` 필드 (Schema `CalendarItem`)

| 필드                   | 설명                                           |
| ---------------------- | ---------------------------------------------- |
| `event_id`             | Calendar Event 식별자                          |
| `title`                | 일정 제목                                      |
| `starts_at`, `ends_at` | 시작·종료 시각                                 |
| `related_task_ids[]`   | 이 일정으로 이미 등록된 Task ID(없으면 미등록) |

#### 3. `important_signals[]` 필드 (Schema `ImportantSignal`)

| 필드                 | 설명                                                                 |
| -------------------- | -------------------------------------------------------------------- |
| `type`               | `email`/`calendar`/`meeting_action_item`/`task` 중 하나              |
| `source_id`          | 출처 원본 식별자(Gmail `message.id` 또는 `{calendar_id}:{event_id}`) |
| `summary`            | 신호 요약 텍스트                                                     |
| `related_task_ids[]` | 이 신호로 이미 등록된 Task ID(없으면 미등록)                         |

#### 4. 우선순위 재계산 — `rank_priorities` Skill 결과 (Schema `PriorityRankingResult`)

| 필드            | 설명                                   |
| --------------- | -------------------------------------- |
| `calculated_at` | 계산 시각                              |
| `priorities[]`  | 우선순위 Top 3(아래 #5 필드)           |
| `changes[]`     | 직전 계산 대비 순위 변동(아래 #6 필드) |
| `source_refs[]` | 근거 출처 ID 목록                      |

#### 5. `priorities[]` 공통 필드 (Schema `PriorityItem`)

| 필드              | 설명                                                                                                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `rank`            | 순위(1~3)                                                                                                                                                           |
| `task_id`         | 대상 Task                                                                                                                                                           |
| `title`           | Task 제목                                                                                                                                                           |
| `score`           | 점수(0~95)                                                                                                                                                          |
| `score_breakdown` | 점수 구성 요소(선택) — `deadline`(0~40)·`importance`(0~20)·`blocked_or_overdue`(0~15)·`meeting_commitment`(0~10)·`calendar_relevance`(0~10), 03 §6 배점 공식과 대응 |
| `reasons[]`       | 이 순위·점수의 근거 문장 1~10개                                                                                                                                     |

#### 6. `changes[]` 필드 (Schema `PriorityChange`)

| 필드                            | 설명                                                                                            |
| ------------------------------- | ----------------------------------------------------------------------------------------------- |
| `task_id`                       | 대상 Task                                                                                       |
| `change_type`                   | `entered`/`moved_up`/`moved_down`/`removed`/`unchanged` 중 하나                                 |
| `previous_rank`, `current_rank` | 이전·현재 순위(없으면 `null`)                                                                   |
| `reason`                        | 순위가 바뀐 실제 근거 문장(03 §7) — 화면이 임의 생성한 라벨이 아니라 이 값을 그대로 보여줘야 함 |

#### 7. 응답 Envelope 공통 필드 (Schema `WorkmateResultEnvelope`, 두 Skill 결과 모두 이 틀로 옴)

| 필드             | 설명                                                                                                 |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| `request_id`     | 요청 식별자                                                                                          |
| `generated_at`   | 응답 생성 시각                                                                                       |
| `data_freshness` | `task`/`calendar`/`email`/`meeting`별 마지막 갱신 시각(없으면 `null`) — 소스별 최신/지연 표시에 사용 |
| `warnings[]`     | 부분 실패 경고 목록                                                                                  |

---

## 📊 주간 업무보고 (`Report.tsx`)

[04-scenarios.md](04-scenarios.md) §2, [02-a2a-interface.md](02-a2a-interface.md) §2.1·§2.3·§2.4,
[03-data-priority-rules.md](03-data-priority-rules.md) §5, [09-ui-design.md](09-ui-design.md) §1,
[Workmate Skill Schema](schemas/workmate-skill-schemas.schema.json)를 종합한 목표 정의다. 이 화면은
지정한 ISO 주간의 업무를 완료·진행·지연·이슈로 분류하고 회의 내용을 통합해 **LLM이 작성한 보고서**를
보여준다 — [🏠 오늘 브리핑](#-오늘-브리핑-briefingtsx)·[🔍 회의록 검색](#-회의록-검색-searchtsx)과
달리 이 화면의 `summary`는 실제로 LLM이 생성한다(07 §9.1, [16-llm-prompts.md](16-llm-prompts.md) 3번
항목).

### 목표 기능

- **처리 흐름**: ISO 주간 경계 계산 → Task·Meeting·Gmail·Calendar 데이터 소스 병렬 조회 → 업무와
  맥락 연결 → 완료/진행/지연/이슈 분류와 회의 주요 내용 통합 → 근거 있는 다음 주 계획 추출 → LLM
  보고서 작성 → 출처 참조·Schema 검증 → Artifact 반환(04 §2). 이번 주·다음 주 일정은 보고서 생성
  시점에 Calendar Provider에서 조회하며 별도 저장 테이블을 두지 않는다(04 §2).

- **조회 기간 지정**: 09 §1이 요구하는 "기간별 보고서 조회"에 대응 — `week_of`(YYYY-MM-DD)로 조회할
  ISO 주간을 지정할 수 있고, 생략하면 서버 수신일이 속한 주간을 쓴다(02 §2.3). ISO 주간은 **월요일
  00:00 이상, 다음 월요일 00:00 미만**이다(03 §5).

- **업무 분류 기준**(03 §5):
  - **완료 업무**: 조회 범위 안에 완료 처리된 Task
  - **진행/지연 업무**: **주간 종료 시점의 상태**를 기준으로 분류(주중에 상태가 바뀌었어도 마지막
    스냅샷 기준)
  - **미해결 이슈**: `blocked` 상태 Task — "그냥 기한을 넘긴" `지연`과 달리 "누가 봐도 막혀서 외부
    조치가 필요한" 상태다(2026-08-16 결정, 17번 갭 문서 #16 — 06번 문서의 M2.1 범위·11번 문서의
    LLM 평가 이력이 이미 이 구분을 전제하고 있었다). `blocked`이면서 기한도 지났으면 `이슈`를
    우선한다.
  - **다음 주 계획**: 다음 주가 마감인 Task, 미완료 Action Item, 회의 등에서 명시적으로 언급된 예정
    문장을 근거로 추출한다. **근거 없이 LLM이 만들어낸 계획은 넣지 않고 별도 `제안`(`kind:
"suggestion"`)으로 구분 표시**한다 — 확정된 일정처럼 보이게 하지 않는다(03 §5).

- **주요 회의 내용 통합**: 조회 주간의 `Meeting.summary`와 근거 `MeetingChunk`를 사용해 작성한다.
  **회의 원문에 확정이 명시된 경우에만 "확정"으로 표현**하고, 논의·제안·검토 단계 내용은 확정된
  결정처럼 작성하지 않는다(04 §2) — 이 부분은 구조화된 `data` 필드가 아니라 Markdown 본문(`# 주간
업무보고` 아래 `## 주요 회의 내용` 절)에만 있다(아래 조회값 정의 참고).

  > **구현(2026-08-16, 17번 갭 문서 #17)**: 새 LLM 호출로 이 절을 다시 쓰지 않는다 — `analyze_meeting`이
  > 이미 만들어 저장해 둔 `Meeting.summary`(17번 갭 문서 #10)를 회의별로 그대로 재사용한다. "확정
  > 표현" 제약은 그 `summary`를 만든 `analyze_meeting` 호출 시점의 책임이지, 주간 보고서가 두 번째
  > LLM 호출로 다시 검증하지 않는다. 아직 분석하지 않은 회의(`summary`가 없음)는 근거가 없어 제외한다.

- **Markdown 복사**: 09 §1이 요구하는 "Markdown 복사" — Artifact의 Markdown Part를 그대로 클립보드에
  복사하는 버튼을 제공한다.

### 조회값 정의

#### 1. 주간 업무보고 — `weekly_report` Skill 결과 (Schema `WeeklyReportResult`)

| 필드                         | 설명                                       |
| ---------------------------- | ------------------------------------------ |
| `period.start`, `period.end` | 조회한 ISO 주간의 시작·끝 날짜             |
| `summary`                    | LLM이 작성한 요약 문장(최대 3000자)        |
| `completed[]`                | 완료 업무 배열(아래 #2 `WorkItem` 구조)    |
| `in_progress[]`              | 진행 중 업무 배열(`WorkItem`)              |
| `delayed[]`                  | 지연 업무 배열(`WorkItem`)                 |
| `unresolved_issues[]`        | 미해결 이슈 배열(`WorkItem`)               |
| `next_week_plans[]`          | 다음 주 계획 배열(아래 #3 `PlanItem` 구조) |
| `source_refs[]`              | 근거 출처 ID 목록                          |

**"주요 회의 내용"은 구조화된 필드가 아니다** — 04 §2의 출력 예시엔 `## 주요 회의 내용` Markdown
절이 있지만, `WeeklyReportResult` Schema에는 이 내용을 담을 배열이 따로 없다. 화면은 이 부분을
Artifact의 Markdown Text Part(`artifact.markdown`)를 그대로 보여주거나 복사하는 방식으로만 다룰 수
있다 — `completed`/`in_progress`/`delayed`/`unresolved_issues`/`next_week_plans`처럼 카드로 나눠
보여줄 수 없다.

#### 2. 업무 항목 공통 필드 (Schema `WorkItem` — `completed`/`in_progress`/`delayed`/`unresolved_issues` 공용)

| 필드            | 설명                                                      |
| --------------- | --------------------------------------------------------- |
| `task_id`       | 대상 Task                                                 |
| `title`         | Task 제목                                                 |
| `status`        | `todo`/`in_progress`/`blocked`/`done`/`cancelled` 중 하나 |
| `summary`       | 이 업무에 대한 부연 설명(없으면 `null`)                   |
| `due_at`        | 마감 시각(없으면 `null`)                                  |
| `source_refs[]` | 근거 출처 ID                                              |

#### 3. `next_week_plans[]` 필드 (Schema `PlanItem`)

| 필드            | 설명                                                                                                    |
| --------------- | ------------------------------------------------------------------------------------------------------- |
| `title`         | 계획 제목                                                                                               |
| `kind`          | `planned`(확정 일정)/`carry_over`(이월된 미완료 항목)/`suggestion`(근거가 약해 제안으로만 표시) 중 하나 |
| `source_refs[]` | 근거 출처 ID                                                                                            |

`kind: "suggestion"`은 03 §5의 "근거 없는 LLM 생성 계획은 별도 제안으로 표시" 규칙에 대응한다 — 화면은
이 값을 `planned`/`carry_over`와 시각적으로 구분해야 한다.

---

## 💬 Workmate 어시스턴트 (Drawer — 전체 화면 공통) — ✅ 구현 완료(2026-08-17)

구현 계획·완료 보고는 [18-workmate-assistant-implementation-plan.md](18-workmate-assistant-implementation-plan.md)에
있다. 아래 목표 정의는 실제 구현과 대체로 일치하지만, `manage_tasks`의 수정(`update`)·삭제(`delete`)는
자연어 Router가 아예 제안하지 않는다(사용자 문장에 없는 `task_id`를 지어낼 위험이 있어서다 — "할 일
관리" 화면을 안내한다) — 자세한 남은 범위는 18번 문서를 참고한다.

**갱신(2026-08-17)**: 아래 "Skill 선택 + 자연어/JSON 입력"·"자동 Skill 판별 여부" 두 절은 이 문서
작성 시점엔 자동 판별을 범위 밖으로 뒀었는데, 이후 사용자가 명시적으로 요청해 구현했다 — Drawer는
이제 Skill 드롭다운이 없고 자연어 채팅 하나뿐이다. 어떤 Skill을 부를지는 신규 Skill
`assistant_ask`(`app/workflows/assistant_router.py`)가 LLM으로 판단한다. 자세한 설계는
18번 문서 "자연어 Router 추가 구현 완료" 절을 참고한다.

**결정(2026-08-17)**: 기존 `app/internal_chat_ui.py`(`GET /internal/skill-chat`, 개발자 전용
검증 페이지, `WORKMATE_INTERNAL_CHAT_ENABLED` 게이팅)와는 별개로, **최종 사용자가 실제로 쓰는
기능**으로 `workmate-ui` 안에 새로 만든다 — 화면 세 가지 시안(대화형 전용 메뉴 / 사이드 패널(Drawer) /
폼+실행 기록 탭) 중 **사이드 패널(Drawer)**로 확정했다. 사이드바에 새 메뉴 항목을 추가하지 않고,
우측 하단 플로팅 버튼(💬)으로 **어느 화면(오늘 브리핑·할 일 관리·회의 관리 등)에 있든 그 화면 위에
겹쳐서 열고 닫는다** — 지금 보던 작업 맥락을 벗어나지 않고 바로 질문·요청할 수 있게 하기 위해서다.
기존 개발자용 검증 페이지는 그대로 유지한다(용도가 다름: 그쪽은 Skill 호출 자체가 계약대로 동작하는지
확인하는 도구, 이 Drawer는 실제 업무를 처리하는 사용자 기능).

### 목표 기능

- **진입**: 화면 우측 하단 플로팅 버튼 — 클릭 시 현재 화면 위에 슬라이드 패널(Drawer)이 열린다.
  배경 화면은 흐리게 처리하되 완전히 가리지 않는다. 다시 누르거나 닫기 버튼으로 접는다.
- **Skill 선택 + 자연어/JSON 입력**: 기존 검증 페이지와 같은 입력 방식(승인된 Skill 목록, 자연어
  또는 Schema JSON) — 다만 최종 사용자에게는 "JSON 모드"가 개발자용 개념이라, 기본은 자연어만 노출하고
  JSON 모드는 고급 옵션으로 접어두는 것을 권장한다(자연어 입력만으로 Skill을 자동 판별하는 게 이상적이나,
  이 문서 시점엔 사용자가 Skill을 직접 고르는 현재 계약을 그대로 쓴다 — 자동 판별은 별도 검토 필요).
- **결과 표시**: Markdown 요약을 우선 보여주고, 구조화 JSON은 펼쳐보기로 둔다. `TASK_STATE_*`·경고는
  배지로, 오류는 사용자가 이해할 수 있는 문구로 보여준다(원본 오류 메시지를 그대로 노출하지 않음).
- **장기 Task Polling**: `analyze_meeting`처럼 오래 걸리는 Skill은 제출 후 Drawer를 닫아도 백그라운드
  Polling이 유지되고, 완료되면 종 아이콘(`ToastStack`)과 같은 방식으로 알려준다 — 제안함의 실시간 알림
  패턴을 재사용한다.
- **대화 이력**: Drawer를 열어둔 세션(페이지 새로고침 전까지) 동안은 이전 질문·답변이 쌓여 보인다.
  새로고침하면 초기화된다(서버에 대화 이력을 영속 저장하지 않음 — 제안과 마찬가지로 "DB에 저장하지
  않는다" 원칙을 따름).
- **경계**: 백엔드는 기존 `/api/v1/internal/skill-chat/*`를 그대로 재사용한다 — 이미 A2A Service
  Token이 아니라 사용자 Session/OIDC로 인증하는 경로라(07 §5.4, 02 §5.2) 최종 사용자 기능으로 전환하는
  데 인증 방식 자체는 바꿀 필요가 없다. 다만 API·모듈 이름의 "internal"이 더는 정확하지 않으므로,
  실제 구현 시점에 이름을 바꿀지(예: `/api/v1/assistant/*`) 판단이 필요하다 — 이 문서는 그 판단을
  강제하지 않고 가능성만 적어둔다.

### Skill 구성 — 15번 문서 전체 기능을 Drawer에서 쓰려면

이 문서가 정의하는 화면 전체 기능(🏠 오늘 브리핑·📊 주간 업무보고·🔍 회의록 검색·🎙️ 회의 녹음의
분석 시작뿐 아니라 📁 회의 관리의 검토, 📬 제안함의 승인·무시, 📋 할 일 관리의 조회·등록까지)을
Drawer 자연어 채팅 하나로 다루려면 각 화면의 동작 하나하나에 대응하는 Skill이 있어야 한다.
`get_meeting_analysis`·`review_action_items`·`review_proposal`·`manage_tasks`·`read_email`·
`assistant_ask` 6개를 이 목적으로 추가해, 기존 5개(`daily_briefing`·`weekly_report`·
`analyze_meeting`·`search_meetings`·`rank_priorities`)와 합쳐 총 11개가 됐다 — 전부
`app/a2a/runtime.py`의 Agent Card에 공개한다(각 Skill의 세부 기능은 아래 "Skill별 기능 설명" 표
참고).

예외는 회의 생성·녹음 파일 업로드·실시간 스트리밍이다 — 파일·마이크 UI가 필요해 텍스트 기반 Skill
인터페이스로 자연스럽게 표현하기 어려워, Drawer가 아니라 기존 🎙️ 회의 녹음 화면을 그대로 쓴다.

**Human-in-the-loop**: Task 삭제·제안 무시·Action Item 거절·회의 재분석처럼 되돌리기 어렵거나
비용이 드는 동작은 Drawer가 바로 실행하지 않는다 — 자연어 Router(`assistant_ask`)가 먼저 확인
문구만 돌려주고, 사용자가 확인 버튼을 눌러 같은 Skill·인자를 `confirmed_skill_id`로 다시 보내야
실제로 실행된다(제안함의 승인/무시 카드가 확인 단계를 거치는 것과 같은 원칙).

### Skill별 기능 설명

이 문서 각 화면 절의 목표 기능과 `app/a2a/runtime.py`(Agent Card에 공개하는 11개 Skill 정의)·
`app/workflows/assistant_skills.py`·`app/workflows/assistant_router.py`의 실제 구현을 근거로
정리했다. 입력·출력 필드의 정확한 계약은 각 화면 절의 "조회값 정의"를 따른다(REST CRUD를 감싼
Skill은 대응하는 REST 엔드포인트를 함께 적었다).

| Skill ID               | 공개 범위         | 기능 설명                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 근거(화면)                  |
| ---------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| `daily_briefing`       | 공개(Agent Card)  | 오늘 일정, 안 읽은 메일 신호(최근 5건), 우선순위 Top 3(`rank_priorities` 결과 재사용)를 하나로 합성해 하루 시작 브리핑을 만든다. Gmail·Calendar를 실시간 조회하고, Provider 실패는 부분 결과 + `warnings`로 표시한다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 🏠 오늘 브리핑              |
| `rank_priorities`      | 공개(Agent Card)  | 사용자 소유 Task를 마감임박도(0~40)·중요도(0~20)·지연/차단(0~15)·회의 약속(0~10)·일정 연관(0~10) 점수로 계산해 Top 3를 뽑고, 직전 계산과 비교한 순위 변동 사유(`entered`/`moved_up`/`moved_down`/`removed`)를 함께 준다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 🏠 오늘 브리핑              |
| `weekly_report`        | 공개(Agent Card)  | 지정한 ISO 주간(생략 시 이번 주)의 완료·진행·지연·미해결 이슈(`blocked` Task)·다음 주 계획을 결정론적으로 분류하고, 그 위에 LLM이 요약 문장을 작성한다. 이미 분석된 회의의 저장된 요약을 "주요 회의 내용"으로 재사용해 통합한다(새 LLM 호출 없음).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 📊 주간 업무보고            |
| `search_meetings`      | 공개(Agent Card)  | 자연어 질문을 Hybrid(Dense+Trigram, RRF 결합) 검색으로 회의록 Chunk에서 근거를 찾아, 그 근거를 그대로 인용해 답변을 조립한다(LLM이 문장을 새로 만들지 않음). 근거가 부족하면 `insufficient_evidence: true`로 명시한다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 🔍 회의록 검색              |
| `analyze_meeting`      | 공개(Agent Card)  | 회의 최종 Transcript(없으면 원본 음성을 STT로 변환)를 LLM으로 분석해 요약과 Action Item 후보(담당자·마감일·근거 원문 포함)를 추출하고, 검색용 Embedding으로 인덱싱한다. 회의 제목이 녹음 시점 날짜·시각 자리표시자 그대로면 같은 LLM 호출로 짧은 제목도 함께 생성해 바꾼다. 처리 시간이 걸려 `SUBMITTED→WORKING→COMPLETED/FAILED`로 비동기 실행되며 Task Polling으로 진행 상태를 확인한다.                                                                                                                                                                                                                                                                                                                                                                                       | 🎙️ 회의 녹음 / 📁 회의 관리 |
| `get_meeting_analysis` | 공개(Agent Card) | 이미 분석한 회의의 저장된 요약·Action Item 목록을 **재분석 없이** 다시 조회하는 얇은 어댑터다(`GET /api/v1/meetings/{id}/analysis`와 같은 로직을 그대로 호출) — `analyze_meeting`을 다시 실행할 때와 달리 LLM을 호출하지 않는다. 대응 REST: `GET /api/v1/meetings/{id}/analysis`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 📁 회의 관리                |
| `review_action_items`  | 공개(Agent Card) | 회의에서 추출된 Action Item 후보 하나 또는 여러 개를 한 번에 승인(Task 생성)·수정(제목·담당자·마감일, `evidence_text`는 읽기 전용이라 수정 불가)·거절 처리한다(`POST /api/v1/meetings/{id}/actions:review`를 그대로 호출). "이 회의 Action Item 다 승인해줘" 같은 일괄 요청에 대응한다. 대응 REST: `POST /api/v1/meetings/{id}/actions:review`.                                                                                                                                                                                                                                                                                                                                                                                                                                  | 📁 회의 관리                |
| `review_proposal`      | 공개(Agent Card) | Gmail·Calendar에서 발행된 임시 Task 제안 하나를 승인(Task 생성) 또는 무시 처리한다(이메일·Calendar 두 REST 엔드포인트가 공유하는 내부 함수를 그대로 호출해 같은 유사 Task 검사·멱등성 규칙을 따른다). 승인 시 제목·담당자·마감일·중요도를 요청 시점에 바꿀 수 있고, 비슷한 Task가 이미 있으면(`SIMILAR_TASK_EXISTS`) 사용자 확인 없이 임의로 "그래도 추가"하지 않는다. 대응 REST: `POST /api/v1/email-task-proposals:review`, `POST /api/v1/calendar-task-proposals:review`.                                                                                                                                                                                                                                                                                                     | 📬 제안함                   |
| `manage_tasks`         | 공개(Agent Card) | Workflow 자체는 조회(`list`)·등록(`create`)·수정(`update`)·삭제(`delete`) 네 동작을 모두 지원한다(`app/task_api.py`의 REST 함수를 그대로 호출). 다만 자연어 Router(`assistant_ask`)는 **조회·등록만** 선택하도록 제한한다 — 존재하지 않는 `task_id`를 LLM이 지어낼 위험이 있어, 사용자가 수정·삭제를 요청하면 "할 일 관리" 화면을 이용하라고 안내하는 답으로 대신한다. 담당자 필드는 항상 요청 사용자 본인 고정(팀 배정 개념 없음). 대응 REST: `GET/POST /api/v1/tasks`, `PATCH/DELETE /api/v1/tasks/{id}`.                                                                                                                                                                                                                                                                      | 📋 할 일 관리               |
| `read_email`           | 공개(Agent Card) | Gmail에서 메일 본문을 그 자리에서 다시 가져온다(저장하지 않음) — 제안(Proposal)에는 짧은 제목만 남고 원문 본문이 남지 않아, "메일 내용 요약해줘" 같은 후속 질문에 답할 근거가 필요할 때 쓴다. `message_id`(Context의 제안 목록에 있을 때) 또는 `query`(제목·본문 키워드로 메일함을 검색, 최근 30일 내로 제한)로 찾는다. 대응하는 REST 엔드포인트는 없다 — Gmail Provider를 직접 호출한다.                                                                                                                                                                                                                                                                                                                                                                                                            | 💬 Workmate 어시스턴트      |
| `assistant_ask`        | 공개(Agent Card) | Drawer의 자연어 채팅 한 턴을 처리하는 Meta Skill. 두 단계 LLM 호출로 동작한다 — ①`route()`가 사용자 문장과 Context(최근 회의·대기 제안 목록, 대화 이력)를 보고 위 10개 Skill 중 무엇을 어떤 인자로 부를지(또는 그냥 답하거나 되물을지) 정하고, ②`phrase_answer()`가 실행 결과 JSON을 근거로 자연어 한국어 답을 만든다. 문장이 어떤 회의·제안을 가리키는지는 별도의 작은 LLM 호출(의미 매칭, 조사·동의어 차이에도 견고)로 한 번 더 확인한다. 되돌리기 어렵거나 파괴적인 동작(`analyze_meeting` 실행, Action Item 거절, 제안 무시, 할 일 삭제)은 먼저 확인 문구만 돌려주고, Drawer의 확인 버튼을 눌러 같은 Skill·인자를 `confirmed_skill_id`로 다시 보내야 실제로 실행된다. 회의 분석 직후 아직 검토 안 한 Action Item이 남아 있으면 "할 일로 추가할까요?" 확인도 이어서 제안한다. | 💬 Workmate 어시스턴트      |

## 변경 이력

- 2026-08-15: 문서 목적을 재정의 — as-built(현재 구현 상태 기록) 문서에서 02·03·04·07·09를 종합한
  화면별 **목표 기능·조회값 정의(Source of Truth)** 문서로 전환. 기존 as-built 성격의 변경 이력은
  새 목적과 맞지 않아 정리하고 이 항목부터 다시 시작함. 14번 문서가 갭 분석 시 이 문서를 1차 기준으로
  참고하도록 역할 분담을 명시함. 제안함 섹션은 구형 스타일로 남겨두고(재작성은 후속 작업), 회의 녹음
  섹션을 새 목적 기준으로 신규 작성 — 07·02 문서 간 파일 업로드 방식 불일치(Presigned 직접 업로드 vs
  multipart 백엔드 경유)를 있는 그대로 병기함
- 2026-08-15: "🎙️ 회의 녹음" 섹션을 "🎙️ 회의 녹음 및 분석"으로 확장 — 04 §3 시나리오의 전체 8단계
  (STT·LLM 분석·embedding 저장·Action Item 검토·Task 등록)를 전부 포함하도록 목표 기능·조회값 정의
  보강. 실제 구현은 이 흐름이 회의 녹음/회의 관리 두 화면에 걸쳐 있지만, 목표 프로세스는 하나로 끊지
  않고 기록함
- 2026-08-15: 위 통합 섹션을 화면 경계에 맞춰 다시 분리 — **🎙️ 회의 녹음**은 회의 생성부터 LLM이
  Action Item 후보를 자동 추출하는 데까지(04 §3 1~6단계, embedding 저장 포함)만 담당하도록 축소하고,
  **📁 회의 관리** 섹션을 신규 작성해 분석 결과 표시·Action Item 검토(승인/수정/거절)·Task 등록(7~8단계)을
  옮김. 회의 관리 화면의 나머지 책임(회의 목록·참석자·전체 회의록)은 아직 미작성으로 남김
- 2026-08-15: **📋 할 일 관리** 섹션 신규 작성 — 04 §6, 09 §2·§5.4, 02 §5.2·§6.5, 03 §1.1·§1.3·§2를
  종합해 목록 조회·직접 등록·수정·삭제·회의 근거 확인·중복 생성 방지까지 정의. 회의 관리에서 이미 정의한
  `meeting_evidence` 값은 새로 만들지 않고 그 절을 그대로 참조하도록 링크만 걸었다. 진행 상태 표를
  ✅ 작성 완료로 갱신
- 2026-08-15: 📋 할 일 관리 구현(14번 갭 문서 #6·#17·#18·#26) 완료에 맞춰 담당자 필드 관련 서술을
  전부 정정(담당자 필터·필수 입력 삭제 — 팀 배정 개념이 없어 항상 값이 하나뿐임) — 02·09번 문서와
  같은 결정을 반영. 목록 조회 응답 순서가 등록일시(생성) 최신순이라는 것도 새로 명시
- 2026-08-15: **🔍 회의록 검색** 섹션 신규 작성 — 04 §4, 02 §2.1·§2.3·§2.4·§5.2·§9, 07 §8.2·§8.2.1을
  종합해 질문 입력·필터·Hybrid 검색(RRF)·근거 충분성 판정·답변과 출처 표시·전체 회의록 이동까지 정의.
  04 §4가 답변 생성을 "LLM이 문맥 안에서 답변"이라고 적은 것과 실제 지향 설계(근거를 그대로 인용
  조립, LLM 미사용 — 16번 문서·07 §9.1 정정과 일치)가 다르다는 것을 발견해 있는 그대로 병기(07·02
  문서 간 업로드 방식 불일치를 병기했던 것과 같은 방식). 진행 상태 표를 ✅ 작성 완료로 갱신
- 2026-08-15: **🏠 오늘 브리핑** 섹션 신규 작성 — 04 §1, 02 §2.1·§2.3·§2.4·§9, 03 §4·§6·§7, Workmate
  Skill Schema(`DailyBriefingResult`/`PriorityRankingResult` 등)를 종합해 정의. 이 화면이
  `daily_briefing`·`rank_priorities` 두 Skill을 함께 호출해 하나로 합성한다는 것(순위 변동은
  `rank_priorities`에만 있음)을 명시. 회의록 검색 때와 같은 이유로 04 §1의 "LLM 요약" 흐름 서술이
  실제 지향 설계(결정적 조합, LLM 미사용)와 다르다는 것도 있는 그대로 병기. `data_freshness` 등
  Envelope 공통 필드도 별도 표로 정리. 진행 상태 표를 ✅ 작성 완료로 갱신
- 2026-08-15: **📊 주간 업무보고** 섹션 신규 작성 — 04 §2, 02 §2.1·§2.3·§2.4, 03 §5, 09 §1, Workmate
  Skill Schema(`WeeklyReportResult`/`WorkItem`/`PlanItem`)를 종합해 정의. 이 화면은 오늘 브리핑·
  회의록 검색과 달리 `summary`를 실제로 LLM이 작성하는 유일한 화면임을 명시(16번 문서 3번 항목과
  일치, 정정 불필요). 03 §5의 업무 분류 기준(완료는 조회 범위 안 완료 처리, 진행/지연은 주간 종료
  시점 상태 기준, 다음 주 계획은 근거 없는 LLM 생성분을 `kind: "suggestion"`으로 구분)을 그대로
  반영. 04 §2 출력 예시의 "주요 회의 내용" 절이 `WeeklyReportResult` Schema엔 구조화 필드로 없고
  Markdown Text Part에만 있다는 것도 확인해 명시. 진행 상태 표를 ✅ 작성 완료로 갱신
- 2026-08-16: **🎙️ 회의 녹음** 조회값 정의 #3·#5·#6 정정(17번 갭 문서 #5·#6) — 이 세 항목은
  2026-08-15에 "실시간 녹음 세션 시작/종료"를 별도 REST 엔드포인트(`POST .../recording-sessions`,
  `POST .../recording-sessions/{id}:complete`)로, "회의 분석 시작"을 `POST .../analysis` 전용
  REST 엔드포인트로 정의했었다. 실제 코드(`app/recording_stream.py`, `app/views/Archive.tsx`)를
  다시 확인한 결과 둘 다 그런 엔드포인트가 없다 — 전자는 WebSocket 연결/해제가 세션 시작/완료를
  암묵적으로 겸하고, 후자는 `analyze_meeting` 내부 스킬챗 요청 하나가 시작과 결과 수신을 겸한다.
  두 결정 모두 02번 문서엔 이미 각주(`[^recording-session]`, `[^analysis-route]`)로 반영돼 있었는데
  이 문서만 갱신되지 않고 있었다 — 세 항목(#3·#5·#6)을 두 항목(#3·#4)으로 합쳐 실제 계약대로
  정정했다.
- 2026-08-16: **🎙️ 회의 녹음** 파일 업로드 방식 서술 정정(17번 갭 문서 #4) — 이 문서는 파일 업로드를
  "브라우저가 Presigned URL로 R2에 직접 업로드"라고 적고 07번 문서와의 불일치를 병기해 뒀었다.
  실제로는 07-technical-specification.md §13.1이 이미 2026-08-15에 02 방식(백엔드 경유
  `multipart/form-data`)으로 정정돼 있었던 것을 재확인 — 이 문서만 그 정정을 반영하지 못하고 있었다.
  사용자에게 확인해 02 방식(실제 구현·실 R2 E2E 검증 완료)으로 확정하고, 목표 기능 서술과 조회값
  정의 #2 제목을 그에 맞게 고쳤다 — 더 이상 "문서 간 불일치"·"결정 대기"가 아니라 확정된 설계다.
- 2026-08-16: **🎙️ 회의 녹음** #4(회의 분석 시작) 정정(17번 갭 문서 #7·#18 구현 완료) —
  `analyze_meeting`이 실제로 진짜 장기 Task Polling 모델(`SUBMITTED → WORKING → COMPLETED/FAILED`)로
  바뀌어, "스킬챗 요청 하나가 시작과 결과 수신을 겸한다"던 이전 정정이 다시 낡았다. 요청은 이제
  즉시 `submitted`로 끝나고, 결과는 `GET .../tasks/{task_id}` Polling 뒤
  `GET /api/v1/meetings/{id}/analysis`(아래)로 재조회한다.
- 2026-08-16: **📁 회의 관리** 조회값 정의 #1·#2·#4 갱신(17번 갭 문서 #7·#8·#9·#10·#11 구현 완료) —
  `GET /api/v1/meetings/{id}/analysis`(저장된 요약·Action Item 재조회, Task 조회가 아님),
  `POST /api/v1/meetings/{id}/actions:review`(배치 승인·수정·거절)를 실제로 구현했다. ActionItem
  필드명을 실제 코드·Schema와 맞춰 `assignee` → `assignee_user_id`로 고쳤고, `meeting_evidence`에
  `action_item_id`를 추가했다. "회의록에서 보기"는 아직 간이형 화면(요약·Action Item만, 원문 강조
  없음)으로만 연결된다 — 전체 회의록 화면 자체가 이 문서에 미정의라는 선행 조건은 그대로다(#13).
- 2026-08-16: **🔍 회의록 검색** #1 `filters.participants[]`에 결정 보류 각주 추가(17번 갭 문서
  #12) — `MeetingParticipant` 모델·테이블이 없어 지원할 수 없다는 사실은 그대로고, 지금 새로
  설계하는 대신 회의 참석자 개념 자체(회의 목록·참석자 화면, 아직 이 문서 미정의)가 먼저 설계된
  뒤 함께 판단하기로 사용자와 확인했다. `search_meetings` Workflow는 여전히 이 필터가 오면
  명시적 `ValueError`로 거절한다(조용히 무시하지 않음).
- 2026-08-17: **📊 주간 업무보고** 업무 분류 기준·주요 회의 내용 통합 절 갱신(17번 갭 문서 #16·#17
  구현 완료) — `unresolved_issues[]`가 실제로 채워지도록 "미해결 이슈 = `blocked` 상태"를 결정해
  분류 기준에 추가했다(`지연`은 단순 기한 초과, `이슈`는 외부 조치가 필요한 차단 상태로 구분).
  "주요 회의 내용"은 새 LLM 호출 없이 `analyze_meeting`이 이미 저장해 둔 `Meeting.summary`를
  그대로 재사용하도록 구현했다는 것을 명시.
- 2026-08-17: **📬 제안함** Calendar 제안 필터·Toast 표시 기준 갱신(사용자 요청) — Calendar 제안
  범위를 "다가오는(지금 이 순간 이후, 무제한 미래)"에서 "오늘부터 한 달 안(로컬 자정 기준 하한·상한
  둘 다)"으로 바꿔, 이미 시작한 오늘 일정도 포함하고(예전엔 종일 일정이 KST 오후엔 조용히 걸러지는
  시간대 버그도 있었음) 끝없이 먼 미래 일정은 제외하게 했다. `TaskProposal.due_at`이 Calendar
  제안에서 항상 `null`이던 것도 고쳐 일정 시작 시각을 실제로 담는다. Toast·데스크톱 알림에 출처별
  기준을 추가했다 — 이메일은 마운트 직후 첫 동기화(적체분 적재)에 도착한 건 Toast를 건너뛰고
  "실시간 수신된 것만" 알리며, Calendar는 `due_at`이 오늘이 아니면 Toast를 건너뛴다("당일 것만").
  카드 목록 자체는 두 경우 다 그대로 보인다 — Toast만 걸러진다.
- 2026-08-17: **📬 제안함** 카드에 날짜 표시 추가·정렬 규칙 신설(사용자 요청) — 이메일 카드는 그동안
  아무 날짜도 없었다(`GmailMessage`에 수신 시각 필드 자체가 없었음). Gmail `internalDate`(수신
  시각, epoch 밀리초)를 파싱해 `GmailMessage.received_at`으로 추가하고, `publish_email_proposal`이
  `TaskProposal.metadata.received_at`에 담도록 했다. 카드는 이메일은 "수신", Calendar는 "일정"
  레이블과 함께 날짜를 보여준다. 목록 정렬 규칙도 새로 만들었다(`sortProposals`,
  `lib/workmate-format.ts`) — 1순위 이메일 먼저·Calendar 나중, 2순위 이메일은 수신 내림차순·
  Calendar는 일정 오름차순. 프론트 정렬만 바뀌었고 SSE 발행 순서·원본 `proposals` 배열은 그대로다.
- 2026-08-17: **💬 Workmate 어시스턴트** 자연어 Router 추가 구현(사용자 요청) — "Skill 선택 + 자연어/
  JSON 입력"·"자동 Skill 판별 여부" 두 절이 범위 밖으로 뒀던 자동 판별을 구현했다. Drawer의 Skill
  드롭다운·Skill별 입력 폼을 전부 걷어내고 채팅 UI로 바꿨고, 신규 10번째 Skill `assistant_ask`(내부
  전용)가 사용자 문장을 LLM으로 보고 기존 9개 Skill 중 무엇을 부를지 판단한다. 자세한 설계·검증은
  18번 문서 "자연어 Router 추가 구현 완료" 절 참고. Skill별 기능 설명 표에 `assistant_ask` 행 추가.
- 2026-08-17: **📁 회의 관리** 회의 삭제(Soft Delete)·제목 자동 생성 구현(사용자 요청) — 목록에
  삭제 버튼 추가(`DELETE /api/v1/meetings/{id}`, Recording·Transcript·Action Item·검색 색인은
  그대로 둠). `analyze_meeting`이 요약을 만드는 LLM 호출에 짧은 제목도 함께 요청하도록
  `MeetingAnalysis`를 확장하고, 회의 제목이 녹음 시점 날짜·시각 자리표시자 패턴("회의 8월 17일
  16:06")일 때만 분석이 끝난 뒤 실제 내용을 요약한 제목으로 바꾼다.
- 2026-08-18: **📬 제안함** 이메일 Toast 표시 기준을 "마지막 동기화 이후 새로 온 것만"으로 변경(사용자
  요청, 위 "Toast 표시 기준" 각주 갱신) — 예전 기준("마운트 직후 첫 동기화 사이클만 적체분 취급")은
  `ProposalNotificationsProvider`가 재마운트될 때마다(이 앱이 로그인 Token을 저장 안 해 새로고침·
  Google 계정 연결 팝업 왕복마다 재마운트됨) 초기화돼, 그 직후 도착한 진짜 새 메일도 적체분으로
  오분류돼 다시는 Toast가 안 뜨는 문제가 있었다. `lastSyncAt`(직전 동기화 완료 시각)을 `localStorage`
  에 남겨 재마운트에도 유지하고, 메일 수신 시각(`metadata.received_at`)이 그보다 늦은 것만 Toast를
  띄우도록 `shouldToastProposal`(`lib/workmate-format.ts`)을 바꿨다. Calendar 기준("당일 일정만")은
  그대로다.
