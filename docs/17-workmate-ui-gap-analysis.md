# workmate-ui 갭 분석 v2 (15번 문서 기준 재분석)

작성일: 2026-08-16
상태: 초안

## 배경

[14-workmate-ui-integration-gaps.md](14-workmate-ui-integration-gaps.md)는 2026-08-15부터 이어진 매우
긴 단일 세션 동안 갭 목록·작업계획·구현완료보고서·실사용 중 발견한 버그 기록이 한 문서에 계속
누적되며 커졌다(2,000줄 이상). 이 문서는 그 누적된 서술을 배제하고, **[15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md)가
현재 정의하고 있는 내용만**을 기준으로 실제 코드(`workmate-agent`, `workmate-ui`)를 처음부터 다시
대조해 작성한 별도의 갭 분석이다.

**범위 원칙**: 15번 문서가 아직 작성하지 않은 부분(예: 📁 회의 관리의 회의 목록·참석자·전체 회의록
화면)은 이 문서의 갭 목록에도 포함하지 않는다 — "정의되지 않은 것"과 "정의됐는데 안 만든 것"은
다른 문제이고, 이 문서는 후자만 다룬다. 15번 문서 자체가 이미 "알려진 한계"·"결정 대기"로 명시한
항목도, 15번이 정의한 기능인 이상 갭 목록에 포함해 한곳에서 볼 수 있게 했다.

**검증 방법**: 각 항목은 15번 문서의 정확한 문구(목표 기능·조회값 정의)와 2026-08-16 시점의 실제
코드(라우트 존재 여부, 프론트 호출 여부, 필드 채움 여부)를 직접 대조해 확인했다 — 14번 문서의 과거
기록을 인용하지 않고 코드를 다시 읽었다.

## 상태 범례

- ⬜ 미구현
- 🟨 부분 구현
- ⏸️ 15번 문서 자체가 결정 대기로 명시(제품 판단 필요)
- 📄 코드 문제 아님 — 15번 문서와 다른 문서(02 등) 간 서술 동기화만 필요

## 전체 요약

| 번호 | 항목 | 화면 | 상태 |
| --- | --- | --- | --- |
| 1 | SSE 자동 재연결 없음 | 제안함 | ✅ 완료(2026-08-16, 지수 백오프 재연결) |
| 2 | Gmail 무시(ignore) 메일 재노출 처리 미결정 | 제안함 | ✅ 완료(2026-08-16, 영구 제외로 결정) |
| 3 | Calendar Webhook 실환경 E2E 미검증 | 제안함 | ✅ 완료(2026-08-16, 실 Google Webhook 수신 확인) |
| 4 | 파일 업로드 방식 — 07 Presigned 직접 업로드 미구현 | 회의 녹음 | ✅ 완료(2026-08-16, 02 방식 확정 — 애초에 07도 이미 그렇게 정정돼 있었음) |
| 5 | `recording-sessions` 전용 REST 엔드포인트 부재 | 회의 녹음 | ✅ 완료(2026-08-16, 15번 문서 정정) |
| 6 | `POST .../analysis` 분석 시작 전용 엔드포인트 부재 | 회의 녹음 | ✅ 완료(2026-08-16, 15번 문서 정정) |
| 7 | `analyze_meeting`이 장기 Task 상태 전이를 안 씀 | 회의 녹음 | ✅ 완료(2026-08-16, 진짜 비동기 Polling 재설계) |
| 8 | Action Item "수정"·"거절" 기능 없음(승인만 있음) | 회의 관리 | ✅ 완료(2026-08-16) |
| 9 | 배치 검토(`decisions[]`) 엔드포인트 없음 | 회의 관리 | ✅ 완료(2026-08-16) |
| 10 | `GET .../analysis` 조회 전용 엔드포인트 없음 | 회의 관리 | ✅ 완료(2026-08-16, 재평가 후 실제 구현) |
| 11 | `meeting_evidence`(근거 연결) 자체가 없음 | 회의 관리 / 할 일 관리 | ✅ 완료(2026-08-16, 부분 — 근거 라인 강조는 #13 참고) |
| 12 | 참여자(`participants`) 검색 필터 미지원 | 회의록 검색 | ⏸️ 결정 보류(2026-08-16, 문서만 정리) |
| 13 | 검색 결과 → 전체 회의록 이동 불가 | 회의록 검색 | ✅ 완료(2026-08-16, 간이형 회의 상세로 연결) |
| 14 | Calendar 미등록 일정이 중요 신호에 안 들어감 | 오늘 브리핑 | ⬜ |
| 15 | `data_freshness` Envelope 필드 미반영 | 오늘 브리핑 | 🟨(대체 표시로 우회) |
| 16 | `unresolved_issues[]`가 항상 빈 배열 | 주간 업무보고 | ✅ 완료(2026-08-17, `blocked`=이슈로 결정) |
| 17 | "주요 회의 내용" 통합 미구현 | 주간 업무보고 | ✅ 완료(2026-08-17, 저장된 Meeting.summary 재사용) |
| 18 | 장기 Task 상태 Polling 메커니즘 부재 | 공통 | ✅ 완료(2026-08-16, #7과 같은 구현) |
| 19 | 녹음 전 참석자 동의 UI 없음 | 회의 녹음 | ⬜(2026-08-24, 99번 문서 정합성 검증 22번 항목에서 발견) |

---

## 📬 제안함 (`Proposals.tsx`)

실시간 SSE 수신·Toast·데스크톱 알림·제안 카드·승인 전 수정·중복 처리·Gmail/Calendar 수동 동기화·
2분 백그라운드 Polling·미확인 배지까지, 15번 문서가 서술한 기능 대부분이 코드에 그대로 있는 것을
확인했다(`app/proposal_api.py`, `app/dev_gmail_sync_api.py`, `app/dev_calendar_sync_api.py`,
`lib/proposal-notifications.tsx`, `app/views/Proposals.tsx`). 남은 갭은 15번 문서 스스로 이미
한계·결정 대기로 밝혀둔 세 가지뿐이다.

### #1. SSE 연결이 끊기면 자동 재연결을 하지 않음 — ✅ 완료(2026-08-16)

**범위**: 프론트 — 소형

15번 문서 "알려진 한계": "구독 Effect가 `apiBase`/`token` 값이 바뀔 때만 다시 실행되므로, 네트워크가
잠깐 끊겼다 돌아와도 사용자가 새로고침하거나 Token을 다시 입력하기 전까지는 'SSE 연결 안 됨' 상태로
남아 있음." 코드(`lib/proposal-notifications.tsx`)에도 재연결 로직이 없는 것을 확인했다.

**수정**: `lib/workmate-api.ts`의 `streamSse()`에 선택적 `onOpen` 콜백을 추가해, 연결이 실제로 한 번
열렸는지(즉시 실패한 인증 오류 등과 구분)를 호출자가 알 수 있게 했다. `proposal-notifications.tsx`의
SSE 구독 Effect를 재귀적인 `connect()` 함수로 바꿔, 연결이 끊기면(에러든 정상 종료든) 1초에서
시작해 두 배씩 늘어나 30초에서 멈추는 지수 백오프로 스스로 재연결하도록 했다. `onOpen`이 불리면
(연결이 실제로 열렸었다는 뜻) 다음 재시도부터는 백오프를 다시 1초로 초기화한다 — 네트워크가 잠깐
끊긴 경우와 서버가 아예 응답하지 않는 경우를 같은 속도로 재시도하지 않기 위해서다. Effect Cleanup
(언마운트, `apiBase`/`token` 변경)에서는 `AbortController`로 진행 중인 연결을 끊고 대기 중인 재시도
타이머도 정리한다. `tests/workmate-api.test.mts`에 `streamSse`의 `onOpen` 계약 회귀 테스트 3개 추가
(연결 성공 시 첫 블록 전에 호출, 인증 실패 시 미호출, 콜백 생략 시에도 정상 동작). 프론트
`eslint` clean·`npm run build` 성공·`npm test` **36 passed**(신규 3개 포함). 두 서버 재기동, 배포된
번들에 반영 확인.

> 이 작업 도중 별개로 발견한 문제: 로컬 백엔드가 포트 8001에 바인딩하지 못했다 —
> `netsh interface ipv4 show excludedportrange`로 확인한 결과 Windows/WSL2가 `7962-8061`을 예약
> 포트 범위로 잡고 있어(Docker Desktop의 WSL2 네트워킹 관련으로 추정) 권한 오류가 났다. 코드 문제가
> 아니라 이 개발 환경의 OS 네트워킹 상태라서, `WORKMATE_PORT=8100`으로 백엔드를 옮기고
> `workmate-ui/lib/workmate-auth.tsx`의 `DEFAULT_API_BASE`도 `http://127.0.0.1:8100`으로 갱신했다.
> **이미 브라우저 `localStorage`에 8001이 저장돼 있던 세션은 자동으로 안 바뀐다** — 프로필 메뉴의
> "•••"에서 API Base URL을 `http://127.0.0.1:8100`으로 직접 갱신해야 한다.

**검증**:
- 프론트: `eslint` clean, `npm run build` 성공, `npm test` — **36 passed**(신규 `streamSse` `onOpen`
  회귀 테스트 3개 포함, 기존 33개 그대로 통과).
- 배포된 번들(`dist/client/assets/*.js`)에 새 로직·새 포트(8100) 둘 다 실제로 반영된 것을 문자열
  검색으로 확인.
- 백엔드(`http://127.0.0.1:8100/health/ready`)·프론트(`http://localhost:3000`) 둘 다 재기동 후
  정상 응답 확인.

**변경/신규 파일 목록**:

| 파일 | 종류 |
| --- | --- |
| `workmate-ui/lib/workmate-api.ts` | 수정 (`streamSse()`에 선택적 `onOpen` 콜백 매개변수 추가) |
| `workmate-ui/lib/proposal-notifications.tsx` | 수정 (SSE 구독을 재귀적 `connect()`로 바꿔 지수 백오프 재연결 추가) |
| `workmate-ui/tests/workmate-api.test.mts` | 신규 (`streamSse`의 `onOpen` 계약 회귀 테스트 3개) |
| `workmate-ui/package.json` | 수정 (`test` 스크립트에 `tests/workmate-api.test.mts` 추가) |
| `workmate-ui/lib/workmate-auth.tsx` | 수정 (`DEFAULT_API_BASE`를 포트 충돌 회피로 8100으로 변경, 무관한 별개 수정) |

### #2. Gmail "무시"한 메일이 수동 동기화 때마다 다시 노출됨 — ✅ 완료(2026-08-16)

**범위**: 제품 결정 필요(구현은 결정 이후) — ⏸️ → 결정 완료

15번 문서: "무시한 메일은 여전히 구분하지 않고 매번 다시 노출한다 — 04-scenarios.md §7과 '제안은
DB에 저장하지 않는다' 원칙에 저촉될 수 있어 제품 결정이 아직 필요하다." (승인한 메일은 이미
`_already_approved`로 걸러짐 — 이 부분만 남음.)

**결정**: 사용자 확인 결과 "영구 제외"로 결정 — 승인과 같은 수준으로 취급해, 무시한 후보는 이후
Gmail 수동 동기화(버튼)·2분 백그라운드 Polling·Calendar Webhook 증분 동기화 어디에서도 다시 제안
후보로 노출하지 않는다. "제안은 DB에 저장하지 않는다" 원칙은 제안 **본문**(제목·스니펫·LLM 근거)을
저장하지 않는다는 뜻으로 해석해, 그 원칙을 지키면서도 "이미 봤다"는 사실(ID·시각)만 남기는
가벼운 전용 테이블을 새로 뒀다.

**수정**: 새 저장소 `app/repositories/ignored_proposals.py`(`SQLiteIgnoredProposalRepository`·
`PostgresIgnoredProposalRepository`, `task_repository()`와 동일하게 `DATABASE_URL` 유무로 선택)와
Postgres용 `migrations/005_ignored_proposals.sql`(`user_id`/`source_type`/`source_id`만 저장,
`user_id`는 다섯·여섯 번째 버그와 같은 이유로 `uuid`가 아니라 `text`) 추가. `proposal_api.py`의
`_review()`가 `decision == "ignore"`일 때 이 저장소에 기록하도록 배선. `dev_gmail_sync_api.py`에
`_already_ignored()`를 추가해 `_already_approved()`와 같은 메시지 단위 판단(후보 중 하나라도
무시됐으면 그 메일 전체를 재추출 대상에서 제외 — LLM 재호출 비용까지 아낌)으로 수동 동기화를
건너뛰게 했다. `dev_calendar_sync_api.py`에도 같은 방식으로 추가해 수동 동기화·Webhook 증분
동기화 두 경로 모두에 적용(Calendar Webhook은 이미 무시한 일정도 나중에 다른 사람이 편집하면
"변경됨" 목록에 다시 잡혀 Gmail 수동 동기화보다도 더 자주 재노출될 수 있었다). `skipped[].reason`에
`already_ignored` 값이 새로 추가됨 — 15번 문서의 "Gmail 동기화 실행 버튼 응답" 조회값 정의는 이
값을 아직 반영하지 않아 별도 갱신이 필요하다.

**검증**: 새 Repository 계약 테스트 5개(`tests/test_ignored_proposal_repository.py`) + Postgres
통합 테스트 1개(`tests/test_postgres_ignored_proposal_integration.py`, 실 OIDC subject 모양의
`user_id`로 검증) + Gmail/Calendar Sync API 회귀 테스트 4개(무시 후 재동기화 시 건너뜀 2개, Review
엔드포인트로 실제 기록되는지 2개). 백엔드 회귀 최종 **241 tests** — `DATABASE_URL` 없이 229
passed/12 skipped, `WORKMATE_TEST_DATABASE_URL` 포함 241 passed/0 skipped 둘 다 확인. 실제
운영과 같은 `DATABASE_URL` 설정으로 `ignored_proposal_repository()`를 직접 호출해 기록·조회가
실제로 동작하는 것도 확인. 백엔드 재기동.

**변경/신규 파일 목록**:

| 파일 | 종류 |
| --- | --- |
| `workmate-agent/migrations/005_ignored_proposals.sql` | 신규 |
| `workmate-agent/app/repositories/ignored_proposals.py` | 신규 |
| `workmate-agent/app/proposal_api.py` | 수정 (`ignored_proposal_repository()` 추가, `_review()`의 ignore 분기가 기록하도록 배선) |
| `workmate-agent/app/dev_gmail_sync_api.py` | 수정 (`_already_ignored()` 추가, 수동 동기화가 무시된 메일도 건너뜀) |
| `workmate-agent/app/dev_calendar_sync_api.py` | 수정 (`_already_ignored()` 추가, 수동 동기화·Webhook 증분 동기화 둘 다 무시된 일정을 건너뜀) |
| `workmate-agent/tests/test_ignored_proposal_repository.py` | 신규 |
| `workmate-agent/tests/test_postgres_ignored_proposal_integration.py` | 신규 |
| `workmate-agent/tests/test_dev_gmail_sync_api.py` | 수정 (무시 회귀 테스트 2개 추가) |
| `workmate-agent/tests/test_dev_calendar_sync_api.py` | 수정 (무시 회귀 테스트 2개 추가) |

### #3. Calendar Webhook 실환경 E2E 미검증 — ✅ 완료(2026-08-16)

**범위**: 인프라 작업(코드 아님)

15번 문서: "실제 Google Calendar 일정 변경 시 자동으로 제안 도착 — 코드·단위 테스트는 완료됐지만
실제 Google 계정으로 ngrok 노출 후 Webhook이 정말 도착하는지의 실환경 E2E 검증은 아직 안 함."

**검증 방법**: `ngrok http 8100`으로 로컬 백엔드를 공개 HTTPS로 노출(`https://mutilator-cardinal-lettuce.ngrok-free.dev`,
`google-oauth-test/.env`에 이미 예약돼 있던 고정 서브도메인 재사용). 이 환경에는 OIDC **로그인**용
Client Secret·Refresh Token이 없어(Gmail·Calendar API용 자격증명과는 별개 OAuth Client) 실제 HTTP
경로로 `_authenticated_user`를 통과시킬 수 없었다 — 이 저장소의 테스트 스위트가 이미 쓰는 것과
동일한 기법(`app.dependency_overrides[_authenticated_user] = lambda: <실제 user_id>`)으로 인증
계층만 오버라이드하고, 나머지는 전부 실제 경로(실제 Google Calendar API, 실제 ngrok 터널, 실제
Webhook 수신, 실제 백그라운드 증분 동기화, 실제 `proposal_hub` 발행)를 그대로 쓰는 임시 서버로
`POST /api/v1/dev/calendar-watch/register`를 호출해 진짜 Google Calendar Watch를 등록했다
(`channel_id`·`resource_id`·`expiration: 2026-08-23` 전부 Google이 실제로 발급).

**결과**: Google이 Watch 등록 직후 보내는 자동 "sync" 확인 핑이 실제로 ngrok을 거쳐 백엔드에
도착했다 — ngrok 요청 로그(`http://127.0.0.1:4040/api/requests/http`)에서 발신 IP
`192.178.15.36`(Google 소유 대역), `X-Goog-Channel-Id`·`X-Goog-Resource-Id`가 방금 등록한 값과
정확히 일치하는 것 확인. 서버 로그에도 `calendar_webhook_sync_done user_id=... new_events=76
published=74`가 찍혀, Webhook 수신 → Channel/Token 검증 통과 → `BackgroundTasks`로 위임된
`_run_calendar_incremental_sync` 실행 → 실제 `events.list` 재조회 → `proposal_hub.publish()`까지
전체 경로가 실제로 동작하는 것을 확인했다(최초 등록이라 `sync_cursor`가 없어 첫 Push는 증분이
아니라 전체 목록을 다시 받아왔다 — Google Calendar API의 표준 동작이며, 코드가 `X-Goog-Resource-State`
값으로 분기하지 않아 실제 "일정 변경" Push와 동일한 경로를 탄다). 검증 목적의 채널이라 확인 직후
`channels.stop`으로 Google 쪽 구독을 정리했다.

**정리**: 검증용 임시 서버·ngrok 프로세스 종료, 정상 백엔드(실제 OIDC 인증)로 재기동. `proposal_hub`는
메모리 전용이라 검증 중 발행된 74건은 재기동과 함께 자연히 사라짐(DB에 남지 않음, "제안은 DB에
저장하지 않는다" 원칙과 일관). `_channel_index`도 프로세스 메모리 전용이라 정상 서버는 이 Channel을
모른다 — 어차피 위에서 `channels.stop`으로 이미 정지시켜 재전송도 없다. 실제 운영에서 Watch를 쓰려면
사용자가 제안함 화면(또는 앞으로 만들 설정 화면)에서 `POST /api/v1/dev/calendar-watch/register`를
다시 호출해야 한다 — 이건 이번 검증의 범위가 아니라 원래 알려진 별도 운영 절차다.

---

## 🎙️ 회의 녹음 (`Meeting.tsx`)

회의 생성, 실시간 녹음(PCM16/WS/재연결/일시정지), 파일 업로드, R2 저장, STT, LLM Action Item 추출,
`meeting_chunks` embedding 저장까지 실제로 동작하는 것을 코드로 확인했다(`app/meeting_api.py`,
`app/recording_stream.py`, `app/workflows/meetings.py`). 남은 갭은 API 계약 형태에 관한 것들이다.

### #4. 파일 업로드 방식 — 07의 Presigned 직접 업로드가 구현돼 있지 않음 — ✅ 완료(2026-08-16)

**범위**: 문서 간 불일치, 코드는 02 방식으로 일치 — 표시용

15번 문서가 스스로 병기한 불일치: 07-technical-specification.md §13.1은 "브라우저가 Presigned
URL로 R2에 직접 업로드"라고 정의하지만, 실제 구현(`POST /api/v1/meetings/{id}/recordings`,
`app/meeting_api.py:92`)은 02-a2a-interface.md §5.2가 정의한 대로 `multipart/form-data`를
**백엔드가 받아 R2에 대신 올리는** 방식이다. 15번 문서는 "실제로 어느 쪽을 구현 기준으로 삼을지는
14번 갭 문서에서 판단한다"고 남겨뒀는데, 지금 코드는 이미 명확히 02 방식 하나만 구현돼 있다 — 07
쪽을 갭으로 볼지, 07 문서를 정정할지 결정이 필요하다.

**조사 결과 — 사실은 이미 결정돼 있었다**: 07번 문서 §13.1을 다시 읽어보니 "브라우저는 R2 자격
증명이나 Presigned URL을 받지 않는다... Presigned URL 직접 업로드는 채택하지 않는다"고 **이미
2026-08-15에** 정정돼 있었다(`workmate-ui-integration-gaps.md` #14 참고 각주 포함) — 15번 문서가
그 정정 *이전* 서술을 그대로 갖고 있다가, 이번 문서(17번)를 처음 쓸 때 오래된 15번 문서 텍스트만
보고 "07이 Presigned를 정의한다"고 잘못 옮겨 적은 것이었다. 즉 07 vs 02는 애초에 진짜 불일치가
아니라 15번 문서가 07의 옛 판을 인용한 채 갱신을 놓친 것.

**결정**: 그래도 "정말 02 방식으로 확정할지"는 사용자에게 직접 확인 — 02 방식(백엔드 경유, 이미
구현·실 R2 E2E 검증 완료)으로 최종 확정, Presigned 직접 업로드는 채택하지 않음(07번 문서와 동일
결론에 재확인 도장을 찍은 셈). **수정**: 15번 문서의 "녹음 파일 업로드" 목표 기능 서술과 조회값
정의 #2 제목을 02 방식으로 고치고, "⚠️ 문서 간 불일치" 콜아웃을 "정정(2026-08-16)" 콜아웃으로
교체해 이 경위를 기록했다. 코드 변경 없음(이미 맞게 구현돼 있었음).

### #5. `recording-sessions` 전용 REST 엔드포인트가 없음 — ✅ 완료(2026-08-16)

**범위**: 백엔드 — 소형(문서 정정으로 대체 가능)

15번 문서 조회값 정의 #3·#5는 `POST /api/v1/meetings/{id}/recording-sessions`(세션 시작,
`recording_session_id`/`status`/`started_at` 응답)과
`POST /api/v1/meetings/{id}/recording-sessions/{session_id}:complete`(세션 종료) 두 개를 별도
REST 계약으로 정의한다. 실제 코드(`app/recording_stream.py`)를 확인한 결과 이런 REST 엔드포인트는
존재하지 않는다 — `WS /api/v1/meetings/{id}/recording-stream`(`recording_stream.py:135`)에 WebSocket으로
**연결하는 것 자체가 세션 시작**이고, 연결이 끊기면 `_finalize_recording_session()`이 자동으로 호출돼
**연결 종료가 곧 세션 완료**다. 클라이언트는 15번 문서가 정의한 `recording_session_id`/`status` 응답을
별도로 받지 못한다. 실사용에는 문제가 없었던 것으로 보이나(이 세션 내내 실 R2 E2E로 검증됨), 15번
문서 계약과는 다른 형태다.

**수정**: "문서 정정으로 대체 가능"이라는 범위 표시대로, 새 REST 엔드포인트를 만드는 대신 15번
문서를 실제 계약에 맞게 고쳤다 — 02번 문서에는 이미 이 결정이 각주(`[^recording-session]`,
2026-08-15 결정)로 반영돼 있었는데 15번 문서만 갱신되지 않고 있었다. "실시간 녹음 세션 시작"(#3)과
"실시간 녹음 종료"(#5) 두 항목을 없애고, "실시간 음성 Chunk"(#4였던 항목)에 세션 시작=WebSocket
연결·세션 종료=연결 해제라는 실제 동작을 합쳐 하나의 항목(새 #3)으로 재정리했다. 코드 변경 없음.

### #6. `POST /api/v1/meetings/{id}/analysis` 분석 시작 전용 엔드포인트 부재 — ✅ 완료(2026-08-16)

**범위**: 문서 동기화 — 📄

15번 문서 조회값 정의 #6은 `POST /api/v1/meetings/{id}/analysis`를 분석 시작 계약으로 정의하지만,
실제로는 `analyze_meeting`이 내부 스킬챗(`/api/v1/internal/skill-chat/messages`) 경로로만 시작된다
(`app/views/Archive.tsx`의 `useSkillRunner("analyze_meeting")`). 02번 문서에는 이미 이 결정을
반영한 각주가 있지만(14번 갭 문서 #24, "결정 완료: 내부 스킬챗 경유 유지"), **15번 문서 본문은 아직
이 결정을 반영하지 않고 REST 엔드포인트를 그대로 계약으로 적고 있다** — 코드를 고칠 문제가 아니라
15번 문서 쪽을 갱신해야 하는 문제다.

**수정**: 02번 문서의 `[^analysis-route]` 각주(2026-08-15 결정)에 맞춰 15번 문서의 "회의 분석
시작" 항목(새 #4)을 `POST /api/v1/meetings/{id}/analysis` 전용 REST 계약에서 `analyze_meeting`
내부 스킬챗 요청(시작과 결과 수신을 같은 응답에서 겸함)으로 고쳤다. 코드 변경 없음.

**#4·#5·#6 공통 검증**: 셋 다 코드 변경이 없는 문서 정정이라 백엔드·프론트 테스트에는 영향이 없다
— 직전 항목(#1~#3)에서 이미 확인한 회귀(백엔드 241 tests, 프론트 36 tests)가 그대로 유효하다.
`docs/15-workmate-ui-screens-reference.md`에 세 건의 변경 이력 항목을 추가해 기록했다.

### #7. `analyze_meeting`이 실제로는 장기 Task 상태 전이를 쓰지 않음 — ✅ 완료(2026-08-16)

**범위**: 백엔드 — 중형(설계 필요)

15번 문서: "`analyze_meeting`은 장기 Task로 분류된다(02 §2.1, §6.2: `SUBMITTED → WORKING(STT) →
WORKING(LLM 분석) → ...`)." 실제로는 프론트가 스킬챗 요청을 보내고 STT+LLM 분석이 전부 끝날 때까지
**하나의 동기적 HTTP 응답**을 기다리는 구조다(`build_analyze_meeting_workflow`가 `execute()` 안에서
STT·LLM을 순서대로 다 처리한 뒤에야 반환). 클라이언트가 중간에 `SUBMITTED`/`WORKING` 상태를 폴링할
방법이 없다 — 회의가 길어 분석이 오래 걸리면 그 시간 내내 요청이 열려 있어야 한다.

**결정(2026-08-16)**: 사용자에게 확인한 결과 "동기 유지 + 문서 정정"이 아니라 "진짜 비동기 Polling으로
재설계"를 선택했다.

**수정**: `app/internal_chat.py`에 `_ASYNC_SKILLS = {"analyze_meeting"}`을 두고, `validate_message`가
이 Skill이면 즉시 `TASK_STATE_SUBMITTED`로 Task를 저장하고 `state: "submitted"`로 응답한 뒤
`BackgroundTasks`로 실제 STT+LLM 실행(`_run_skill_in_background`)을 넘긴다. 백그라운드 실행은 시작
시 `TASK_STATE_WORKING`으로 갱신하고, 끝나면 `_persist_task`로 `TASK_STATE_COMPLETED` + Artifact를
저장하며, `ValueError`/`RuntimeError`(동기 경로였다면 422/503으로 변환됐을 오류)는
`TASK_STATE_FAILED` + `status.message`에 오류 문구를 담아 저장한다 — 동기 경로의 오류 변환 규칙을
비동기 Task 상태로 그대로 옮긴 것이다. `WorkflowResult.warnings`(부분 실패 경고)도 Artifact
`metadata`에 함께 실어 Polling 응답에서 드러나게 했다(예전엔 Task Store Snapshot에 저장되지 않던 값).

프론트는 `lib/use-skill.ts`에 `usePollingSkillRunner` Hook을 새로 추가했다 — `POST .../messages`로
제출하고 `GET .../tasks/{task_id}`를 1.5초 간격(5분 상한)으로 Poll하다가 종료 상태가 되면 결과를
반환한다. `analyze_meeting`의 Task Artifact는 요약 원문 텍스트만 담고 구조화된 결과
(`MeetingAnalysisResult`)는 안 담아서, 완료 시점에 `GET /api/v1/meetings/{id}/analysis`([#10](#10-get-apiv1meetingsidanalysis-조회-전용-엔드포인트-없음))를
다시 불러 구조화된 값을 얻는다. `Archive.tsx`의 `MeetingDetail`이 이 Hook을 쓰도록 바꾸고, 컴포넌트
마운트 시 이미 저장된 분석 결과가 있으면 재실행 없이 그 값을 먼저 보여주도록 했다.

**검증**: 백엔드 회귀 테스트에 `test_analyze_meeting_returns_submitted_immediately_then_polls_to_completed`,
`test_analyze_meeting_value_error_surfaces_as_a_failed_task`를 추가(`tests/test_internal_chat.py`) —
`TestClient`가 `BackgroundTasks`를 응답 직후 같은 호출 안에서 실행하는 걸 확인하고 이를 이용해
실시간 대기 없이도 결정적으로 검증했다. 기존 `test_workflow_value_error_becomes_a_cors_visible_422`는
`analyze_meeting`이 더 이상 동기 422 계약을 따르지 않으므로, 여전히 동기인 `search_meetings`로
바꿔 같은 오류 변환 규칙을 계속 검증하게 했다. 백엔드 전체 회귀 **262 tests**(`DATABASE_URL` 없이
250 passed/12 skipped, `WORKMATE_TEST_DATABASE_URL` 포함 262 passed/0 skipped 둘 다 확인). 프론트는
`npx tsc --noEmit`·`npm run lint`·`npm test`(36 tests) 모두 통과, `vinext build`도 성공.

**변경/신규 파일 목록**:
- `app/internal_chat.py` — `_ASYNC_SKILLS`·`_save_task_status`·`_run_skill_in_background` 추가,
  `_persist_task`가 Artifact `metadata`에 `warnings`도 저장하도록 수정, `validate_message`에
  비동기 분기 추가.
- `tests/test_internal_chat.py` — 비동기 제출→완료/실패 Polling 테스트 2건 추가, 기존 422 테스트를
  동기 Skill(`search_meetings`) 기준으로 수정.
- `lib/use-skill.ts` — `usePollingSkillRunner` Hook 신규.
- `lib/workmate-api.ts` — `skillChatApi.getTask` 추가.
- `lib/workmate-types.ts` — `SkillChatTaskSnapshot`/`SkillChatTaskState` 타입 추가.
- `app/views/Archive.tsx` — `MeetingDetail`이 `usePollingSkillRunner` + 마운트 시 기존 분석 결과
  재조회를 쓰도록 재작성(아래 [#8](#8-action-item-수정거절-기능-자체가-없음--승인만-구현됨)·
  [#9](#9-배치-검토decisions-엔드포인트가-없음--개별-승인만-가능)·
  [#10](#10-get-apiv1meetingsidanalysis-조회-전용-엔드포인트-없음)과 같은 커밋에서 함께 바뀜).
- `docs/02-a2a-interface.md` — `[^analysis-route]` 각주를 실제 비동기 계약에 맞춰 갱신.
- `docs/15-workmate-ui-screens-reference.md` — 회의 녹음 조회값 정의 #4 정정.

### #19. 녹음 전 참석자 동의 UI가 없음 — ⬜(2026-08-24, 99번 문서 정합성 검증 22번 항목에서 발견)

**범위**: 프론트 — 소형~중형(참석자 개념이 아직 없어 UI만으로는 완결 안 됨)

> **출처가 다른 항목**: 이 문서의 다른 갭 항목은 전부 "15번 문서가 정의했는데 아직 안 만든 것"이지만,
> 이 항목은 **15번 문서가 아직 정의하지 않은** 요구사항이다(이 문서 서두의 범위 원칙상 원래는
> 다루지 않는 종류) — 근거는 05번 문서("LLM, 보안, 오류 처리") §2 "녹음 전 참석자 동의 UI를
> 제공한다"이며, 99번 문서(정합성 검증) 22번 항목에서 사용자 확인을 거쳐 예외적으로 이 목록에
> 추가했다.

`workmate-ui` 전체를 검색해도 "동의"·"consent" 관련 UI 코드가 없다 — 녹음 시작 전에 참석자 동의를
받는 화면·확인 절차가 구현되지 않았다. `MeetingParticipant` 모델·테이블 자체가 없다는 것도
[#12](#12-참여자-filtersparticipants-검색-필터-미지원--결정-보류2026-08-16-문서만-정리)에서 이미
확인했다 — 참석자 개념 자체가 없어 "누구에게 동의를 받을지" 목록을 만들 수 없는 상태다. 회의
참석자 화면(15번 문서 미정의)이 먼저 설계돼야 완결되는 항목이라 #12와 선행 관계가 있다.

**결정 필요**: 참석자 개념·화면이 아직 없는 상태에서 어떤 형태의 동의 확인(예: 참석자 목록 없이
"녹음을 시작하기 전 참석자 전원의 동의를 받았는지" 체크박스 하나로 최소 구현할지, 참석자 화면
설계까지 기다릴지)으로 갈지는 제품 판단이 필요하다.

---

## 📁 회의 관리 (`Archive.tsx`)

15번 문서가 정의한 범위는 "분석 결과 표시 → Action Item 검토 → Task 등록"까지다(회의 목록·참석자·
전체 회의록 화면은 15번 문서가 아직 정의하지 않아 이 갭 목록 범위 밖). 이 범위 안에서 실제 코드
(`app/action_item_api.py`, `app/views/Archive.tsx`)를 확인한 결과, **승인(approve) 외의 경로가
전혀 구현돼 있지 않다**는 걸 새로 확인했다.

### #8. Action Item "수정"·"거절" 기능 자체가 없음 — 승인만 구현됨 — ✅ 완료(2026-08-16)

**범위**: 백엔드 + 프론트 — 중형

15번 문서 목표 기능: "사용자는 각 후보를 **승인(approve)·수정(edit)·거절(reject)** 할 수 있다."
`app/action_item_api.py`를 확인한 결과 `POST /{meeting_id}/actions/{action_item_id}/approve`
하나만 존재한다. `Archive.tsx`도 `approve()` 함수 하나만 있고 거절·수정 버튼·입력창이 없다 — 후보를
한번 잘못 추출하면 승인하거나 그냥 무시하는 것 외에 고칠 방법이 없다.

**수정**: `app/repositories/meetings.py`에 `edit_action`(제목·설명·마감일·담당자만 수정,
`evidence_text`는 서버가 원문에서 뽑은 값이라 절대 수정 불가 — 02 §5.3)과 `reject_action`(이미
Task가 생긴 항목은 `approve_action`과 같은 멱등 규칙으로 되돌리지 않음)을 추가하고, `action_items`
테이블에 `description`·`due_at`·`assignee_user_id`·`start_ms`·`end_ms`·`meeting_chunk_id` 컬럼을
더했다(전엔 `upsert_action`이 제목·근거만 받았음). [#9](#9-배치-검토decisions-엔드포인트가-없음--개별-승인만-가능)의
배치 엔드포인트가 `decision: "edit"`/`"reject"`로 이 둘을 호출한다. `Archive.tsx`는 대기 중 항목마다
"수정"(인라인 폼: 제목·설명·마감일·담당자)·"거절" 버튼을 추가하고, 서버 응답으로 로컬 `overrides`
상태만 갱신해 매 조작마다 전체를 재조회하지 않는다.

**검증**: `tests/test_meeting_repository.py`(신규, 9 tests) — `edit_action`이 안 넘긴 필드는 그대로
두고 `evidence_text`는 절대 못 바꾸는지, `reject_action`이 이미 승인된 항목을 안 건드리는지 검증.
아래 #9와 같은 커밋·같은 회귀에서 함께 확인했다.

**변경/신규 파일 목록**: 아래 #9와 공유(같은 커밋).

### #9. 배치 검토(`decisions[]`) 엔드포인트가 없음 — 개별 승인만 가능 — ✅ 완료(2026-08-16)

**범위**: 백엔드 — 소형~중형(#8과 함께 다루는 게 자연스러움)

15번 문서 조회값 정의 #3: `POST /api/v1/meetings/{id}/actions:review`가 `decisions[]` 배열로
여러 Action Item을 한 번에 처리하는 계약이다. 실제로는 `POST .../actions/{action_item_id}/approve`
하나씩만 있어 후보가 여러 개면 그만큼 여러 번 클릭·요청해야 한다.

**수정**: `app/action_item_api.py`에 `POST /api/v1/meetings/{id}/actions:review`를 추가했다 —
`decisions: [{action_item_id, decision, changes?}]` 배열을 받아 항목마다 승인·수정·거절을 한 번의
요청으로 처리한다(02 §5.3 계약대로 `changes`는 `decision: "edit"`에서만 허용 — 다른 값과 같이 오면
422). `approve`는 클라이언트가 다시 보낸 값이 아니라 분석 시점에 이미 저장된 `title`/`evidence_text`를
그대로 쓴다(기존 단건 승인 엔드포인트와의 차이). `Archive.tsx`는 대기 항목이 2건 이상이면 "대기 N건
일괄 승인" 버튼을 보여줘 `decisions[]`에 여러 항목을 한 번에 담아 보낸다 — 개별 승인·수정·거절
버튼도 내부적으로 이 배치 엔드포인트를 1건짜리 배열로 호출해 두 경로가 갈라지지 않는다.

**#8·#9 공통 검증**: `tests/test_action_item_api.py`에 `ActionsReviewBatchApiTests`(4 tests) —
배치 승인·수정·거절 동시 처리, `changes` + 비-`edit` 조합 422, 존재하지 않는 `action_item_id`/회의
404를 검증. 백엔드 전체 회귀 **262 tests**(`DATABASE_URL` 없이 250 passed/12 skipped,
`WORKMATE_TEST_DATABASE_URL` 포함 262 passed/0 skipped 둘 다 확인). 프론트 `npx tsc --noEmit`·
`npm run lint`·`npm test`(36 tests) 모두 통과, `vinext build` 성공.

**변경/신규 파일 목록**:
- `app/domain/meeting.py` — `MeetingRecord.summary` 필드 추가([#10](#10-get-apiv1meetingsidanalysis-조회-전용-엔드포인트-없음)과 공유).
- `app/repositories/meetings.py` — `edit_action`·`reject_action`·`list_actions`·`set_summary` 추가,
  `action_items` 스키마 확장, `upsert_action` 시그니처 확장.
- `app/action_item_api.py` — `POST .../actions:review` 배치 엔드포인트 신규.
- `app/workflows/meetings.py` — 분석 완료 시 확장 필드까지 `upsert_action`에 넘기고 `set_summary` 호출.
- `tests/test_meeting_repository.py` — 신규.
- `tests/test_action_item_api.py` — 배치 검토 테스트 클래스 추가.
- `app/views/Archive.tsx` — 수정·거절·일괄 승인 UI 추가.
- `lib/workmate-api.ts` — `meetingsApi.reviewActions` 추가.
- `docs/15-workmate-ui-screens-reference.md` — 회의 관리 조회값 정의 #1·#2 정정(아래 #10과 함께).

### #10. `GET /api/v1/meetings/{id}/analysis` 조회 전용 엔드포인트 없음 — ✅ 완료(2026-08-16)

**범위**: 백엔드 — 중형(원래 "문서 동기화 — 📄"로 분류했으나 재평가, 아래 정정 참고)

15번 문서 조회값 정의 #1은 분석 결과(요약·Action Item 목록)를 조회하는 별도 GET 계약을 정의한다.
실제로는 `analyze_meeting` 스킬챗 요청의 응답을 그 화면에서 딱 한 번만 보여주고 별도로 저장하지
않는다 — 페이지를 벗어나거나 새로고침하면 결과를 다시 보려면 **분석을 처음부터 다시 실행**해야
한다(LLM 재호출 비용 발생). #6과 같은 이유로 02번 문서엔 이미 "결정 완료" 각주가 있지만(14번 갭
문서 #25), 15번 문서 본문은 아직 갱신되지 않았다.

**정정(2026-08-16)**: 처음엔 #6과 같은 "02에 이미 결정 각주가 있으니 15번 문서만 고치면 된다"는
문서 동기화(📄)로 분류했지만, #6("분석 시작")과 달리 이건 "조회"라 성격이 다르다는 걸 다시 보며
발견했다 — 스킬챗 응답은 그 자리에서 한 번만 오고 저장되지 않으므로, 문서만 고치면 "결과를 다시
보려면 분석을 처음부터 재실행해야 한다"는 실제 동작을 그대로 인정하는 셈이었다. 그래서 문서만
고치는 게 아니라 실제로 결과를 저장하고 재조회하는 엔드포인트를 코드로 구현했다.

**수정**: `app/domain/meeting.py`의 `MeetingRecord`에 `summary` 필드를 추가하고, `meetings` 테이블에
`summary` 컬럼을, `analyze_meeting`의 `execute()`가 분석 직후 `repo.set_summary(...)`로 저장하게
했다. `app/action_item_api.py`에 `GET /api/v1/meetings/{id}/analysis`를 추가해 저장된 `summary` +
`list_actions()` 결과를 `analyze_meeting`이 돌려주는 구조화 결과와 같은 키(`assignee_user_id` 등)로
반환한다. 한 번도 분석하지 않은 회의는 404. A2A Task 조회가 아니라 "이 회의의 가장 최근 저장된
결과"를 돌려주는 계약이라 `task_id`/`state`는 응답에 없다([#7](#7-analyze_meeting이-실제로는-장기-task-상태-전이를-쓰지-않음)의
Task Polling과는 별개 경로). `Archive.tsx`가 회의를 펼칠 때마다 먼저 이 엔드포인트로 재조회하고,
저장된 값이 있으면 `analyze_meeting`을 다시 실행하지 않는다.

**검증**: `tests/test_action_item_api.py`의 `MeetingAnalysisApiTests`(3 tests) — 미분석 회의 404,
존재하지 않는 회의 404, 저장된 요약·Action Item이 `analyze_meeting`과 같은 키로 반환되는지 검증.
`tests/test_meeting_repository.py`의 `set_summary` 관련 2 tests. 백엔드 전체 회귀 262 tests(위 #9와
같은 실행에 포함).

**변경/신규 파일 목록**:
- `app/domain/meeting.py`, `app/repositories/meetings.py`, `app/workflows/meetings.py` — #8·#9와 공유.
- `app/action_item_api.py` — `GET .../analysis` 엔드포인트 신규.
- `app/views/Archive.tsx` — 마운트 시 재조회 로직.
- `docs/15-workmate-ui-screens-reference.md` — 회의 관리 조회값 정의 #1(`task_id`/`state` 없음
  정정)·#2(`assignee` → `assignee_user_id` 정정).

### #11. `meeting_evidence`(Task ↔ ActionItem ↔ Meeting 근거 연결) 자체가 없음 — ✅ 완료(2026-08-16, 부분)

**범위**: 백엔드 + 프론트 — 중형(회의 관리·할 일 관리 공통)

15번 문서가 회의 관리 #4와 할 일 관리 두 곳에서 정의하는 기능: 승인된 Task 상세에 읽기 전용
`evidence_text`와 "회의록에서 보기" 버튼을 표시하고, 누르면
`/meetings/{meeting_id}?highlight_meeting_chunk_id={id}`로 이동해 근거 라인을 강조한다. 코드
전체에서 `meeting_evidence`·`highlight_meeting_chunk_id`를 검색한 결과 백엔드(`task_api.py`)에도
프론트(`Tasks.tsx`/`Archive.tsx`)에도 전혀 없다. 승인된 Action Item의 근거를 나중에 다시 확인할
방법이 없다(애초에 이동할 "전체 회의록" 화면 자체도 15번 문서 미정의 상태라, 이 기능은 그 화면이
생기기 전까지는 부분적으로만 구현 가능 — "회의록에서 보기" 버튼 없이 `evidence_text`만 Task
상세에 노출하는 정도는 지금도 할 수 있다).

**수정**: `app/action_item_api.py`의 `_source_id`가 Task `source_id`를 `{meeting_id}:{action_item_id}`
형태로 만들도록 바꿨다(기존엔 `action_item_id` 하나뿐이라 어느 회의 근거인지 되짚을 방법이 없었음
— Calendar 제안의 `{calendar_id}:{event_id}`와 같은 패턴). `app/task_api.py`에 `TaskResponse.meeting_evidence`
필드를 추가해, `source_type="action_item"` Task는 `source_id`를 파싱해 회의 Repository에서
`evidence_text`·`meeting_chunk_id`·회의 제목을 되짚어 붙인다(옛 형식 `source_id`는 조용히 `null`).
`proposal_api.py`의 유사 Task 충돌 응답도 같은 직렬화 경로(`_task_response`)를 쓰도록 통일했다.
`Tasks.tsx`는 `meeting_evidence`가 있는 Task 아래에 근거 문장(읽기 전용)과 "회의록에서 보기" 버튼을
보여준다 — 누르면 [#13](#13-검색-결과-출처-카드--전체-회의록-이동-불가)에서 만든 간이형 회의 상세
화면으로 이동한다. `Search.tsx`의 출처 카드에도 같은 버튼을 추가했다.

**부분 구현 안내**: 15번 문서가 정의하는 `/meetings/{meeting_id}?highlight_meeting_chunk_id={id}`
근거 라인 강조 이동은 아직 못 만든다 — 이동할 "전체 회의록"(Transcript 원문 화면) 자체가 15번
문서에 아직 없고, `page.tsx`에 URL Query Parameter 라우팅도 없다(순수 `useState<View>`). #13에서
만든 간이형 화면은 요약·Action Item만 보여주고 원문 강조는 하지 않는다 — 문서가 스스로 이미
"버튼 없이 `evidence_text`만 노출하는 정도는 지금도 가능"이라고 적어둔 범위까지 구현했다.

**검증**: `tests/test_action_item_api.py`에 `test_approve_source_id_embeds_meeting_id_for_evidence_lookup`,
`test_approved_task_exposes_read_only_meeting_evidence`, `test_manual_task_has_no_meeting_evidence`
추가(3 tests) — `source_id` 형식, 근거 노출, 수동 Task는 `null`인지 확인. 백엔드 전체 회귀 262
tests. 프론트 `npx tsc --noEmit`·`npm run lint`·`npm test`(36 tests) 모두 통과.

**변경/신규 파일 목록**:
- `app/action_item_api.py` — `_source_id`에 `meeting_id` 포함.
- `app/task_api.py` — `TaskMeetingEvidence`, `_meeting_evidence`, `TaskResponse.meeting_evidence`.
- `app/proposal_api.py` — 유사 Task 응답도 `_task_response`로 통일.
- `tests/test_action_item_api.py` — 근거 노출 테스트 3개 추가.
- `lib/workmate-types.ts` — `TaskMeetingEvidence`, `Task.meeting_evidence`.
- `app/views/Tasks.tsx`, `app/views/Search.tsx` — "회의록에서 보기" 버튼.
- `app/views/MeetingDetailView.tsx`, `app/page.tsx` — [#13](#13-검색-결과-출처-카드--전체-회의록-이동-불가)과 공유.
- `docs/15-workmate-ui-screens-reference.md` — 회의 관리 조회값 정의 #4 정정·`action_item_id` 필드 추가.

---

## 📋 할 일 관리 (`Tasks.tsx`)

목록 조회·직접 등록·수정·삭제·중복 생성 방지까지 15번 문서 정의와 코드가 일치하는 것을 확인했다
(`app/task_api.py`, `app/views/Tasks.tsx`) — 정렬 순서(등록일시 최신순), 담당자 필드 없음(본인
전용으로 이미 정정 완료), 상태·마감일 필터, 삭제 확인창 제목 포함까지 전부 일치한다. 유일한 갭은
위 [#11 `meeting_evidence`](#11-meeting_evidence-task--actionitem--meeting-근거-연결-자체가-없음)와
같은 항목이라 별도 번호를 매기지 않고 교차 참조만 남긴다.

---

## 🔍 회의록 검색 (`Search.tsx`)

질문 입력·날짜/회의 필터·Hybrid(Dense+Trigram, RRF) 검색·근거 충분성 판정·답변과 출처 표시가 코드와
일치하는 것을 확인했다(`app/repositories/meeting_chunks.py`의 `search_hybrid`가 실제로 `search_dense`+
`search_keyword`를 RRF로 결합, `app/workflows/meetings.py`의 `build_search_meetings_workflow`).

### #12. 참여자(`filters.participants[]`) 검색 필터 미지원 — ⏸️ 결정 보류(2026-08-16, 문서만 정리)

**범위**: 백엔드(모델 설계부터 필요) — 중형

15번 문서 조회값 정의 #1은 `filters.participants[]`를 검색 필터 중 하나로 정의한다. 코드 전체에서
`MeetingParticipant` 관련 모델·테이블이 전혀 없는 것을 확인했다 — 참석자 개념 자체가 없어 필터를
구현할 방법이 없다. `build_search_meetings_workflow`도 `participants` 필터가 오면
`ValueError("participant filtering is not supported by the current meeting schema")`로 명시적으로
거절한다.

**결정(2026-08-16)**: 사용자에게 확인한 결과 "결정 보류 — 문서만 정리"(권장안)로 확정했다.
`MeetingParticipant` 모델·테이블을 지금 새로 설계하는 대신, 이 필터의 실제 사용성은 회의 참석자
개념 자체(회의 관리의 회의 목록·참석자 화면 — 15번 문서가 아직 정의하지 않은 영역, 최초 작성
변경 이력 참고)가 먼저 설계된 뒤 함께 판단하는 게 자연스럽다는 이유다. 코드 변경은 없다 —
`build_search_meetings_workflow`가 이미 `participants` 필터에 명시적 `ValueError`로 거절하는
동작을 그대로 유지한다(조용히 무시되는 대신 분명한 오류로 드러나는 게 안전한 기본값). 이 결정을
15번 문서에도 반영했다.

**변경/신규 파일 목록**:
- `docs/15-workmate-ui-screens-reference.md` — 회의록 검색 조회값 정의 #1에 결정 보류 안내 추가.

### #13. 검색 결과 출처 카드 → 전체 회의록 이동 불가 — ✅ 완료(2026-08-16, 간이형)

**범위**: 프론트(대상 화면이 먼저 필요) — 소형(선행 조건 있음)

15번 문서: "출처 카드를 누르면 전체 회의록 화면으로 이동해 해당 근거 Chunk가 강조된다 —
`highlight_meeting_chunk_id` 메커니즘을 Task 근거와 동일하게 재사용한다." `Search.tsx`에 출처
카드 클릭 시 이동 로직이 없는 것을 확인했다. 이동할 "전체 회의록" 화면 자체가 15번 문서에 아직
정의되지 않아, 이 항목은 그 화면이 먼저 정의·구현돼야 만들 수 있다([#11](#11-meeting_evidence-task--actionitem--meeting-근거-연결-자체가-없음)과
같은 선행 조건).

**결정(2026-08-16)**: 사용자에게 확인한 결과 "전체 회의록 화면이 생길 때까지 보류"(권장안) 대신
"지금 간이형으로도 만들어주세요"를 선택했다. 15번 문서가 정의하는 "전체 회의록"(Transcript 원문 +
`highlight_meeting_chunk_id` 강조 이동)은 여전히 미정의 상태라 그대로 만들 수 없지만, 그 전 단계로
요약·Action Item만 보여주는 간이형 회의 상세 화면을 새로 만들어 지금 붙일 수 있는 진입점(`Search.tsx`
출처 카드, `Tasks.tsx`의 #11 근거 링크)을 전부 연결했다.

**수정**: `app/views/MeetingDetailView.tsx`(신규) — `GET /api/v1/meetings/{id}`로 제목을,
`GET .../analysis`([#10](#10-get-apiv1meetingsidanalysis-조회-전용-엔드포인트-없음))로 요약·Action Item을
가져와 읽기 전용으로 보여준다(원문 Transcript 강조는 없음). `page.tsx`의 `Shell`에 URL 라우팅이
없어(`useState<View>`뿐) `View`에 `"meetingDetail"`을 추가하고 `selectedMeetingId`·`previousView`를
lift해 "← 목록으로"를 누르면 원래 화면으로 돌아가게 했다. `Tasks.tsx`(#11)와 `Search.tsx`의
"회의록에서 보기" 버튼이 이 화면을 연다.

**검증**: 프론트 `npx tsc --noEmit`(타입 오류 없음), `npm run lint`(0 errors), `npm test`(36 tests
그대로 통과), `vinext build` 성공. 이 화면 자체는 자동화 테스트가 없는 다른 화면들(Briefing.tsx
등)과 같은 수준이라 회귀 스위트에 케이스를 추가하지 않았다 — 실 서버 재기동 뒤 실제로 회의를
분석하고 "회의록에서 보기" 클릭 → 요약·Action Item이 뜨는지 수동 확인 예정(다음 섹션 참고).

**변경/신규 파일 목록**:
- `app/views/MeetingDetailView.tsx` — 신규.
- `app/page.tsx` — `View`에 `meetingDetail` 추가, `Shell`에 `selectedMeetingId`/`previousView`/
  `openMeetingDetail` 추가.
- `lib/workmate-api.ts` — `meetingsApi.get` 추가.

*(Reranker 조건부 호출은 15번 문서 스스로 "07 §8.2.1이 M4.4 범위로 지정한 것이라 지금 갭이 아님"이라고
표시만 해둔 항목이라 이 목록에 포함하지 않는다.)*

---

## 🏠 오늘 브리핑 (`Briefing.tsx`)

`daily_briefing`·`rank_priorities` 병렬 호출, 오늘 일정, 우선순위 Top 3(점수 구성·변경 사유 포함),
새로고침이 코드와 일치하는 것을 확인했다(`app/workflows/daily_briefing.py`,
`app/views/Briefing.tsx`). `related_task_ids` 계산도 이 세션 중 구현 완료된 상태를 그대로 재확인했다.

### #14. Calendar 미등록 일정이 중요 업무 신호에 포함되지 않음

**범위**: 백엔드 — 중형(판정 로직 새로 필요)

15번 문서: "중요 업무 신호(`important_signals`)는 읽지 않은 Gmail 메일**과** Calendar의 미등록
일정 후보를 모아 보여준다." `daily_briefing.py`의 `important_signals` 리스트는 `messages`(Gmail)에서만
만들어지고, `calendar_events`는 전혀 참조하지 않는다 — Calendar 쪽 "미등록 일정 후보"를 신호로
승격할지 판단하는 로직 자체가 없다.

### #15. `data_freshness` Envelope 필드가 응답에 실리지 않음

**범위**: 백엔드 — 소형(우선순위 낮음, 대체 표시 있음)

15번 문서 조회값 정의 #7: `WorkmateResultEnvelope`의 `data_freshness`(소스별 마지막 갱신 시각)로
"최신/지연" 상태를 표시해야 한다. 실제로는 `daily_briefing.py`가 내부적으로 `provider_freshness`를
계산하지만 `WorkflowResult`에 담아 응답으로 내보내지 않는다. `Briefing.tsx`는 대신 `warnings` 배열
유무로 소스 상태("최신"/"지연")를 대체 표시하고 있어 화면상 기능은 있지만, 15번 문서가 정의한
정확한 필드 계약과는 다르다.

---

## 📊 주간 업무보고 (`Report.tsx`)

ISO 주간 지정(`week_of`), 완료/진행/지연 분류, 다음 주 계획(`kind` 구분), LLM 요약(이 화면만 실제로
LLM을 씀), Markdown 복사가 코드와 일치하는 것을 확인했다(`app/workflows/weekly_report.py`,
`app/workflows/weekly_classification.py`).

### #16. `unresolved_issues[]`가 항상 빈 배열 — "이슈" 개념 자체가 없음 — ✅ 완료(2026-08-17)

**범위**: 백엔드 — 중형(개념 정의부터 필요)

15번 문서 조회값 정의 #1은 `unresolved_issues[]`를 완료/진행/지연과 나란한 필드로 정의한다.
`build_weekly_report_data()`를 확인한 결과 `"unresolved_issues": []`로 하드코딩돼 있고, 채우는
로직도 없다. `WeeklyBucket`(`app/domain/weekly.py`)에도 "이슈"에 대응하는 분류 자체가 없다 — "이슈"가
`delayed`(지연 업무)와 무엇이 다른지부터 결정해야 한다.

**결정**: "이슈"는 `blocked` 상태 Task, "지연"은 (차단되지 않았지만) 기한을 넘긴 Task로 나눴다.
사용자에게 새로 물어보지 않고 기존 문서에서 근거를 찾아 확정했다 — `06-delivery-plan.md`가 M2.1
범위를 "완료·진행·지연·**이슈** 집계"로 이미 명시하고 있었고(`unresolved_issues`도 다른 세
Bucket과 같은 M2.1 결정론적 결과라고 못 박음), `11-llm-evaluation-plan.md`의 2026-08-10 LLM
평가 이력이 "blocked Task가 `unresolved_issues`에서 누락됐다"는 문제를 System Prompt 수정으로
고친 기록을 그대로 남기고 있었다 — 즉 "blocked → 이슈"는 이미 이전에 내려진 결정이었고, 이번
구현이 그 결정을 현재 아키텍처(LLM이 아니라 Python이 결정론적으로 분류)에 반영한 것뿐이다.
`blocked`이면서 기한도 지났으면 `이슈`를 우선한다(막힌 원인 해소가 기한 초과 표시보다 먼저).

**수정**: `app/domain/weekly.py`의 `WeeklyBucket`에 `"issue"`를 추가하고, `classify_task_status()`가
`blocked`을 `"delayed"` 대신 `"issue"`로 반환하도록 고쳤다. `app/workflows/weekly_classification.py`의
`_BUCKET_ORDER`·`build_weekly_report_data()`가 `"issue"` Bucket을 인식하고, 응답 필드 이름(`unresolved_issues`)으로
옮겨 담도록 했다(Bucket 이름과 필드 이름이 다르다). 폴백 요약 문장(LLM 실패 시 노출되는 결정론적
문장)에도 이슈 건수를 추가했다. `Report.tsx`는 이미 `unresolved_issues.length`를 통계 카드에서
읽고 있었지만 실제 목록을 보여주는 `ReportBlock`이 없었다 — 다른 상태(완료/진행/지연)와 같은
형태로 하나 추가했다.

**검증**: `tests/test_weekly_classification.py`에 `blocked` → `issue` 분류(기존 테스트 값 갱신),
`blocked`+기한 초과가 여전히 `issue`로 남는지 검증하는 신규 테스트 추가. `tests/test_weekly_source_link.py`에
`build_weekly_report_data`가 `blocked` Task를 `unresolved_issues`로, 기한 초과만 있는 Task를
`delayed`로 정확히 나누는지 검증하는 신규 테스트 추가. 백엔드 전체 회귀 **265 tests**(`DATABASE_URL`
없이 253 passed/12 skipped, `WORKMATE_TEST_DATABASE_URL` 포함 265 passed/0 skipped 둘 다 확인).
프론트 `npx tsc --noEmit`·`npm run lint`·`npm test`(36 tests) 모두 통과.

**변경/신규 파일 목록**:
- `app/domain/weekly.py` — `WeeklyBucket`에 `"issue"` 추가, `classify_task_status()` 분류 규칙 변경.
- `app/workflows/weekly_classification.py` — `_BUCKET_ORDER`·`build_weekly_report_data()` 갱신.
- `tests/test_weekly_classification.py`, `tests/test_weekly_source_link.py` — 신규·갱신 테스트.
- `app/views/Report.tsx` — "미해결 이슈" `ReportBlock` 추가.
- `docs/15-workmate-ui-screens-reference.md` — 업무 분류 기준에 "미해결 이슈" 정의 추가.

### #17. "주요 회의 내용" 통합이 전혀 구현되지 않음 — ✅ 완료(2026-08-17)

**범위**: 백엔드 — 중형~대형(LLM 입력 설계 필요)

15번 문서 목표 기능: "조회 주간의 `Meeting.summary`와 근거 `MeetingChunk`를 사용해 [Markdown
본문에] 작성한다." `weekly_report.py`·`weekly_classification.py` 전체에서 Meeting·MeetingChunk
Repository를 전혀 조회하지 않는 것을 확인했다 — Task 저장소만 쓴다. "주요"의 판단 기준(어떤 회의를
포함할지)과 LLM 입력 설계가 선행돼야 착수 가능하다.

**설계 결정**: "LLM 입력 설계"가 새 LLM 호출을 뜻하지 않게 범위를 줄였다 — `analyze_meeting`이
회의 분석 시점에 이미 만들어 저장해 둔 `Meeting.summary`([#10](#10-get-apiv1meetingsidanalysis-조회-전용-엔드포인트-없음)로
영속화됨)를 그대로 재사용한다. 15번 문서가 요구하는 "회의 원문에 확정이 명시된 경우에만 확정으로
표현" 제약은 `analyze_meeting`이 그 `summary`를 만들 때 이미 책임지는 부분이라, 주간 보고서가 같은
내용을 다시 LLM에 태워 재작성할 이유가 없다고 판단했다 — 이 판단으로 새 Prompt 설계·LLM 비용·실패
Surface를 모두 피했다. "주요"의 판단 기준은 "조회 주간에 열렸고 이미 분석된(요약이 있는) 회의
전부"로 정했다(15번 문서가 별도 우선순위 기준을 요구하지 않음).

**수정**: `app/workflows/weekly_report.py`에 `_weekly_meeting_highlights()`를 추가했다 — 사용자의
전체 회의를 조회해 `scope.period`(조회 주간) 안에 `started_at`(또는 `created_at`)이 있고
`summary`가 있는 것만 `{title, summary, source_refs: [meeting_id]}`로 모은다. `SQLiteMeetingRepository`는
`DATABASE_URL` 유무와 무관하게 항상 SQLite라(`app/meeting_api.py`) 주간 보고서에 새 Postgres
의존성을 추가하지 않는다. `_render_weekly_report_markdown()`이 `meeting_highlights` 인자를 받아
`## 지연`/`## 미해결 이슈` 절과 `## 다음 주 계획` 절 사이에 `## 주요 회의 내용`을 렌더링한다
(04 §2 예시 순서와 동일) — 구조화 `data`엔 이 절이 없다(15번 문서가 이미 명시). 순환 import를
피하려고 `meeting_repository`는 함수 실행 시점에 지연 import한다(`app.a2a.runtime` → `weekly_report`
→ `meeting_api` → `internal_chat` → `app.a2a.runtime`으로 되돌아오는 경로가 있었음).

**검증**: `tests/test_weekly_report_generation.py`에 `test_meeting_highlights_reuse_stored_summary_without_a_second_llm_call`
추가 — 주간 범위 안·분석 완료된 회의만 Markdown에 포함되고, 범위 밖 회의와 아직 분석하지 않은
회의(summary 없음)는 제외되는지, 구조화 `data`엔 이 내용이 없는지 검증. 백엔드 전체 회귀 265
tests(위 #16과 같은 실행에 포함).

**변경/신규 파일 목록**:
- `app/workflows/weekly_report.py` — `_weekly_meeting_highlights()`, `_render_work_items()` 추출,
  `_render_weekly_report_markdown()`에 `meeting_highlights` 인자 추가, `build_weekly_report_workflow()`에
  `meeting_repository` 주입 지원.
- `tests/test_weekly_report_generation.py` — 신규 테스트.
- `docs/15-workmate-ui-screens-reference.md` — 주요 회의 내용 통합 절에 구현 방식(새 LLM 호출 없이
  저장된 `Meeting.summary` 재사용) 명시.

---

## 공통/전역

### #18. 장기 Task 상태 Polling 메커니즘이 없음 — ✅ 완료(2026-08-16)

**범위**: 공통 — 소형~중형

02-a2a-interface.md의 A2A Task 모델은 `SUBMITTED → WORKING → INPUT_REQUIRED → COMPLETED` 같은
비동기 상태 전이와 클라이언트의 상태 Polling을 전제하고, 15번 문서도 회의 녹음·회의 관리 두
화면에서 이 전이 모델을 인용해 화면 책임을 나눈다([#7](#7-analyze_meeting이-실제로는-장기-task-상태-전이를-쓰지-않음),
[#10](#10-get-apiv1meetingsidanalysis-조회-전용-엔드포인트-없음) 참고). 실제로는 스킬챗 경로가 요청-응답
하나로 끝나는 동기 모델이라, 오래 걸리는 작업(회의 분석 등)에서 상태를 폴링하며 진행률을 보여줄
방법이 없다. 개별 화면 갭이라기보다 여러 화면이 공유하는 구조적 갭이라 여기 따로 뒀다.

**완료 안내**: [#7](#7-analyze_meeting이-실제로는-장기-task-상태-전이를-쓰지-않음)에서 구현한
`_ASYNC_SKILLS`(`SUBMITTED → WORKING → COMPLETED/FAILED`) + `usePollingSkillRunner`가 이 구조적
갭을 메운 실제 메커니즘이다 — 별도 구현이 아니라 #7과 같은 커밋. 지금은 `analyze_meeting` 하나에만
적용돼 있지만(다른 4개 Skill은 실측상 오래 안 걸려 동기로 남겨둠, `app/internal_chat.py`의
`_ASYNC_SKILLS` 주석 참고), 앞으로 오래 걸리는 Skill이 추가되면 `_ASYNC_SKILLS`에 추가하는 것만으로
같은 메커니즘을 재사용할 수 있다. 별도 검증·파일 목록은 #7 참고.

## 변경 이력

- 2026-08-16: 최초 작성 — 14번 문서의 누적 서술을 배제하고 15번 문서 현재 상태만 기준으로 코드를
  처음부터 다시 대조. 18개 항목 확인(제안함 3, 회의 녹음 4, 회의 관리 4, 회의록 검색 2, 오늘 브리핑
  2, 주간 업무보고 2, 공통 1). 15번 문서가 아직 정의하지 않은 회의 관리의 회의 목록·참석자·전체
  회의록 화면은 범위 밖으로 명시적으로 제외.
- 2026-08-16: **#1(SSE 자동 재연결 없음) 구현 완료** — `streamSse()`에 `onOpen` 콜백을 추가하고,
  `proposal-notifications.tsx`의 SSE 구독 Effect를 재귀적 `connect()`로 바꿔 1초→30초 상한 지수
  백오프로 자동 재연결하게 했다. 연결이 실제로 열렸던 적이 있으면 다음 재시도부터 백오프를
  초기화(네트워크 순간 끊김과 서버 완전 다운을 구분). 회귀 테스트 3개 추가, 프론트 회귀 **36
  passed**. 작업 도중 별개로 로컬 백엔드가 Windows/WSL2의 예약 포트 범위(`7962-8061`)에 걸려 8001
  바인딩이 안 되는 것을 발견 — 코드 문제가 아니라 이 개발 환경의 OS 네트워킹 문제라 백엔드 포트를
  8100으로 옮기고 프론트 기본 API Base URL도 갱신(기존에 8001을 `localStorage`에 저장해둔 세션은
  프로필 메뉴에서 수동 갱신 필요). 전체 요약 표의 #1 상태를 ✅ 완료로 갱신.
- 2026-08-16: **#2(Gmail "무시" 메일 재노출) 구현 완료** — 제품 결정이 필요한 항목이라 먼저
  사용자에게 확인, "영구 제외"(승인과 같은 수준)로 결정. "제안은 DB에 저장하지 않는다" 원칙은
  제안 본문(제목·스니펫·근거)을 저장하지 않는다는 뜻으로 해석해, ID·시각만 담는 가벼운 전용
  저장소(`app/repositories/ignored_proposals.py`, `migrations/005_ignored_proposals.sql`)를
  새로 두고 원칙을 지켰다. `proposal_api.py`의 무시 처리·`dev_gmail_sync_api.py`·
  `dev_calendar_sync_api.py`(수동 동기화 + Calendar Webhook 증분 동기화)에 배선해, 이미 무시한
  후보가 어떤 경로로도 다시 노출되지 않게 했다 — `_already_approved`와 같은 메시지/이벤트 단위
  판단이라 불필요한 LLM 재호출도 함께 아낀다. 회귀 테스트 10개 추가(Repository 계약 5, Postgres
  통합 1, Sync API 4), 백엔드 회귀 최종 **241 tests** — `DATABASE_URL` 없이 229 passed/12
  skipped, `WORKMATE_TEST_DATABASE_URL` 포함 241 passed/0 skipped 둘 다 확인. 실 운영 설정으로
  Repository를 직접 호출해 기록·조회 확인, 백엔드 재기동. 전체 요약 표의 #2 상태를 ✅ 완료로 갱신.
- 2026-08-16: **#3(Calendar Webhook 실환경 E2E) 검증 완료** — `ngrok http 8100`으로 로컬 백엔드를
  공개 HTTPS로 노출하고, 실제 Google Calendar Watch를 등록(`POST /api/v1/dev/calendar-watch/register`,
  실제 `channel_id`·`resource_id`·`expiration` 발급 확인). 이 환경엔 로그인용 OIDC 자격증명이 없어
  `_authenticated_user`만 테스트 스위트와 같은 방식으로 오버라이드하고 나머지는 전부 실제 경로를
  그대로 썼다. Google이 등록 직후 보내는 자동 확인 Push가 ngrok을 거쳐 실제로 도착 —
  발신 IP(Google 소유 대역)·`X-Goog-Channel-Id` 등 헤더가 등록값과 정확히 일치하는 것을 ngrok
  요청 로그로 확인, 서버 로그에서 `calendar_webhook_sync_done ... published=74`까지 확인해
  Webhook 수신→검증→백그라운드 증분 동기화→제안 발행 전체 경로가 실제로 동작하는 것을 검증했다.
  검증 후 `channels.stop`으로 Google 쪽 구독 정리, 임시 서버·ngrok 종료, 정상 백엔드(실 OIDC 인증)로
  재기동 — 검증 중 발행된 제안은 메모리 전용이라 재기동과 함께 자연히 사라짐. 전체 요약 표의 #3
  상태를 ✅ 완료로 갱신.
- 2026-08-16: **#4·#5·#6(회의 녹음 API 계약 정정) 완료** — 셋 다 코드가 아니라 15번 문서를 실제
  구현에 맞게 고치는 작업이었다. #5(`recording-sessions` REST)·#6(`analysis` REST)는 02번 문서에
  이미 있던 각주(`[^recording-session]`, `[^analysis-route]`, 둘 다 2026-08-15 결정)를 15번
  문서에 반영만 하면 되는 것으로 확인 — 세션 시작/종료는 WebSocket 연결/해제가 암묵적으로 겸하고,
  분석 시작은 `analyze_meeting` 내부 스킬챗 요청 하나가 시작·결과 수신을 겸한다는 실제 계약대로
  두 항목을 정정. #4(파일 업로드 방식)는 조사 결과 07번 문서가 **이미 2026-08-15에** 02 방식(백엔드
  경유)으로 정정돼 있었던 것을 발견 — "07 vs 02 불일치"는 애초에 15번 문서가 07의 옛 판을 인용한
  채 갱신을 놓쳐서 생긴 착시였다. 그래도 사용자에게 최종 확인해 02 방식으로 확정하고 15번 문서를
  고쳤다. 셋 다 코드 변경 없음 — `docs/15-workmate-ui-screens-reference.md`에 변경 이력 3건 추가.
  전체 요약 표의 #4~#6 상태를 ✅ 완료로 갱신.
- 2026-08-16: **#7~#13·#18 반영 완료** — 세 항목(#7·#12·#13)은 진행 전 사용자에게 방향을 확인했다:
  #7은 "동기 유지 + 문서 정정" 대신 **"진짜 비동기 Polling으로 재설계"**, #12는 권장안대로 **"결정
  보류 — 문서만 정리"**, #13은 "전체 회의록 화면이 생길 때까지 보류"(권장안) 대신 **"지금 간이형으로도
  만들어주세요"**를 선택했다.
  - **#7(`analyze_meeting` 진짜 비동기 재설계)**: `app/internal_chat.py`에 `_ASYNC_SKILLS`를 두고
    `analyze_meeting`만 즉시 `SUBMITTED`로 응답한 뒤 `BackgroundTasks`로 실행, `WORKING`을 거쳐
    `COMPLETED`/`FAILED`(오류 메시지 포함)로 끝나게 했다. `lib/use-skill.ts`에 `usePollingSkillRunner`
    Hook 신규.
  - **#8·#9(Action Item 수정·거절, 배치 검토)**: `edit_action`·`reject_action` Repository 메서드와
    `POST .../actions:review` 배치 엔드포인트를 새로 만들고, `Archive.tsx`에 인라인 수정 폼·거절
    버튼·"대기 N건 일괄 승인" 버튼을 추가했다.
  - **#10(`GET .../analysis` 재조회)**: 원래 "문서 동기화(📄)"로 분류했으나, #6("시작")과 달리
    "조회"는 실제로 결과를 저장해야 하는 별개 문제라는 걸 재검토 중 발견 — `MeetingRecord.summary`
    저장 + `GET /api/v1/meetings/{id}/analysis`를 실제로 구현했다(A2A Task 조회가 아니라 저장된
    최신 결과 재조회 계약이라 `task_id`/`state`는 없음).
  - **#11(`meeting_evidence`)**: Task `source_id`를 `{meeting_id}:{action_item_id}` 형태로 바꿔
    회의 근거를 되짚을 수 있게 하고, `TaskResponse.meeting_evidence`로 노출. `Tasks.tsx`·`Search.tsx`에
    "회의록에서 보기" 버튼 추가 — 근거 라인 강조 이동은 #13의 간이형 화면으로 부분 구현.
  - **#12(참여자 검색 필터, 결정 보류)**: 코드 변경 없음 — `MeetingParticipant` 모델 자체가
    회의 참석자 화면(15번 문서 미정의)과 함께 설계돼야 한다는 이유로 보류를 15번 문서에 기록만 했다.
  - **#13(간이형 회의 상세, 신규)**: `app/views/MeetingDetailView.tsx` 신규 — 요약·Action Item만
    읽기 전용으로 보여준다(원문 Transcript 강조 없음). `page.tsx`의 `Shell`에 URL 라우팅이 없어
    `View`에 `"meetingDetail"`을 추가하고 `selectedMeetingId`/`previousView`를 lift했다.
  - **#18(공통 Task Polling)**: #7의 `_ASYNC_SKILLS` 메커니즘이 그대로 이 구조적 갭의 답이라 별도
    구현 없이 완료 처리.
  - **문서 동기화**: `docs/02-a2a-interface.md`의 `[^analysis-route]` 각주를 실제 비동기 계약에
    맞게 갱신, `docs/15-workmate-ui-screens-reference.md`의 회의 녹음 #4·회의 관리 #1·#2·#4·
    회의록 검색 #1에 변경 이력 4건 추가(정정·완료·결정 보류 안내).
  - **검증**: 신규 백엔드 테스트 `tests/test_internal_chat.py`(비동기 제출/완료/실패 2건),
    `tests/test_meeting_repository.py`(신규, 9건), `tests/test_action_item_api.py`(배치 검토·근거
    노출 등 7건 추가) — 백엔드 전체 회귀 **262 tests**(`DATABASE_URL` 없이 250 passed/12 skipped,
    `WORKMATE_TEST_DATABASE_URL` 포함 262 passed/0 skipped 둘 다 확인). 프론트 `npx tsc --noEmit`
    (오류 없음)·`npm run lint`(0 errors)·`npm test`(36 tests 그대로 통과)·`vinext build` 성공.
  - 전체 요약 표의 #7~#13·#18 상태를 갱신(#12만 ⏸️ 결정 보류, 나머지 전부 ✅ 완료).
- 2026-08-17: **#16·#17(주간 업무보고 미해결 이슈·주요 회의 내용) 반영 완료** — 둘 다 "결정이
  필요"하다고 표시했던 항목이라, 사용자에게 다시 묻지 않고 기존 문서 근거로 결정을 확정했다.
  - **#16**: "이슈"를 `blocked` 상태로, "지연"을 (차단 안 됐지만) 기한 초과로 나눴다 —
    `06-delivery-plan.md`의 M2.1 범위 서술과 `11-llm-evaluation-plan.md`의 2026-08-10 LLM 평가
    이력("blocked Task가 unresolved_issues에서 누락됐다")이 이미 이 구분을 전제하고 있었다.
    `app/domain/weekly.py`의 `WeeklyBucket`에 `"issue"`를 추가하고 `classify_task_status()`가
    `blocked`을 `issue`로 분류하게 했다. `Report.tsx`에 "미해결 이슈" 목록 카드도 추가(통계 숫자는
    이미 있었지만 목록이 없었음).
  - **#17**: "주요 회의 내용"을 새 LLM 호출 없이 구현했다 — `analyze_meeting`이 이미 저장한
    `Meeting.summary`(#10)를 조회 주간에 열린, 분석 완료된 회의만 골라 그대로 재사용한다. 새
    Prompt 설계·LLM 비용·실패 지점을 늘리지 않았다. `app/workflows/weekly_report.py`에
    `_weekly_meeting_highlights()`를 추가하고 `_render_weekly_report_markdown()`이 `## 주요
    회의 내용` 절을 렌더링하게 했다(구조화 `data`가 아니라 Markdown 본문에만 — 15번 문서 계약대로).
  - **검증**: 신규 테스트 3개(`test_weekly_classification.py` 1개, `test_weekly_source_link.py`
    1개, `test_weekly_report_generation.py` 1개) — 백엔드 전체 회귀 **265 tests**(`DATABASE_URL`
    없이 253 passed/12 skipped, `WORKMATE_TEST_DATABASE_URL` 포함 265 passed/0 skipped 둘 다
    확인). 프론트 `npx tsc --noEmit`·`npm run lint`·`npm test`(36 tests) 모두 통과.
  - `docs/15-workmate-ui-screens-reference.md`의 업무 분류 기준·주요 회의 내용 통합 절에 이 결정과
    구현 방식을 반영. 전체 요약 표의 #16·#17 상태를 ✅ 완료로 갱신.
