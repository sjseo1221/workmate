# workmate-ui 백엔드 연동 갭 분석 및 구현 계획

작성일: 2026-08-15
상태: 초안 — 항목별로 계속 구체화하며 수정 예정

## 배경

[15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md)가 02·03·04·07·09 문서를
종합해 정의한 화면별 **목표 기능·조회값**을 1차 기준(Source of Truth)으로 삼아, `workmate-ui`(별도
저장소, `../workmate-ui`) 실제 구현과 대조해 찾은 갭 목록이다. 15번 문서가 아직 다루지 않은 화면은
[02-a2a-interface.md](02-a2a-interface.md), [04-scenarios.md](04-scenarios.md), [03-data-priority-rules.md](03-data-priority-rules.md),
[07-technical-specification.md](07-technical-specification.md), [09-ui-design.md](09-ui-design.md)를 직접
대조한다. 각 항목은 `workmate-agent` 백엔드 코드까지 확인해 "프론트만 고치면 되는지 / 백엔드도
필요한지"를 구분해뒀다.

이 문서는 살아있는 작업 문서다. 항목을 구체화하거나 진행 상태가 바뀌면 이 파일을 직접 수정한다.

`workmate-ui`의 실제 메뉴 7개(오늘 브리핑·주간 업무보고·할 일 관리·회의 녹음·회의 관리·회의록 검색·
제안함) + 여러 화면이 공유하는 공통 영역 기준으로 항목을 묶었다.

## ⚠️ 결정 번복: `workmate-ui`를 다시 사용하기로 함 (2026-08-15)

[09-ui-design.md:5](09-ui-design.md)와 [07-technical-specification.md §5.4](07-technical-specification.md#54-내부-skill-검증-챗봇)는
`workmate-ui`를 "폐기된 샘플"로 명시하고 있었다.

> 기존 `workmate-ui`는 폐기된 샘플이며 구현·검수에 사용하지 않는다. 제품 사용자가 쓰는 최종 화면은
> M5에서 팀 공통 Orchestrator UI에 통합한다.

**이 결정을 번복하고 `workmate-ui`를 다시 사용하기로 함. 2단계 계획으로 진행:**

1. **1차**: `workmate-ui`를 이 문서의 갭 목록대로 완성한다. 완성본은 이후 **개인용으로 계속 보관
   (keep)** — 즉 이 저장소 자체가 최종 제품 코드가 되는 것은 아니지만 버리지도 않는다.
2. **2차**: 완성된 화면·로직을 **팀 공통 Orchestrator UI 양식에 맞게 조정**해서 그쪽에 반영한다. 원래
   07·09 문서가 말하던 "M5에서 팀 공통 Orchestrator UI에 통합"은 이 2차 단계로 여전히 유효하다 — 다만
   `workmate-ui`를 처음부터 버리고 새로 짜는 게 아니라, 여기서 완성한 것을 이식하는 방식으로 바뀐 것.

이에 따라:

- 이 문서의 갭 목록(1~18번)은 **1차(완성) 단계의 작업 목록**으로 다시 유효함
- ✅ **후속 조치 완료**: `01-overview-architecture.md`, `06-delivery-plan.md`, `07-technical-specification.md`,
  `09-ui-design.md`, `AGENTS.md`, `HANDOFF.md`, `workmate-ui/README.md`의 "폐기된 샘플" 문구를 위
  2단계 계획에 맞게 갱신함. `workmate-ui`와 별도로 존재하던 독립 정적 HTML/JS UI `workmate-ui`는
  두 UI 간 혼동을 피하기 위해 폐기·삭제함
- 2차(Orchestrator UI 이식) 단계는 아직 이 문서의 범위 밖 — Orchestrator UI 쪽 화면 양식·컴포넌트 체계가
  정해지면 별도 이식 계획 문서로 분리하는 것을 권장

## 상태 범례

- ⬜ 미착수
- 🟨 진행 중
- ✅ 완료
- ⏸️ 보류 (결정 대기 또는 후순위)
- 📄 코드 작업 아님 (문서만 수정)

## 전체 우선순위 (화면 무관, 규모·의존성 기준)

| 순서 | 항목 | 화면 | 규모 | 상태 |
| --- | --- | --- | --- | --- |
| 1 | #13 실시간 녹음 오디오 포맷 불일치 | 회의 녹음 | 중형 | ✅ 완료 (PCM16 24kHz 200ms로 재작성) |
| 2 | #21 실시간 녹음 STT 완전 미연결 | 회의 녹음 | 대형 | ✅ 완료 (파일 기반 최종 STT + 실시간 Partial 자막 모두 실 E2E 검증) |
| 3 | #20 녹음 파일 미저장(R2 미연동) + #14 업로드 방식 결정 | 회의 녹음 | 중형 | ✅ 완료 (파일 업로드·실시간 녹음 두 경로 모두 실 R2 E2E 검증) |
| 4 | #22 analyze_meeting 실사용 불가 (표시용) | 회의 녹음 | 없음(#20·#21 해소 시 자동) | ✅ 완료 (실 R2→STT→LLM E2E로 직접 확인) |
| 5 | #23 meeting_chunks/embedding 저장 없음 | 회의 녹음 | 중형 | ✅ 완료 (실 Postgres/pgvector E2E 검증, search_meetings 근거 조회까지 확인) |
| 6 | #24 분석 시작 전용 엔드포인트 부재 | 회의 녹음 | 결정 대기 | 📄 결정 완료 (내부 스킬챗 경유 유지, 02번 문서 각주 반영) |
| 7 | #25 분석 결과 조회 전용 엔드포인트 부재 | 회의 관리 | 결정 대기 | 📄 결정 완료 (#24와 같은 각주로 반영, 코드 변경 없음) |
| 8 | #7 회의 생성 Idempotency-Key | 회의 녹음 | 초소형 | ✅ 완료 (Header 대신 클라이언트 `meeting_id` + 서버 `INSERT OR IGNORE`로 해결, 02번 문서 정정) |
| 9 | #5 장기 Task Polling | 공통/전역 | 소형 | ⬜ |
| 10 | #6 할 일 담당자 필드 | 할 일 관리 | 결정 대기 | ✅ 결정 완료(본인 전용 유지, 02·09·15번 문서 정정) |
| 11 | #2 전체 회의록 화면 → #3 Task 상세/회의 근거 | 회의 관리 → 할 일 관리 | 중형 | ⬜ |
| 12 | #4 Action Item 편집/거절 | 회의 관리 | 중형 | ⬜ (검토할 결과 자체가 #21·#22로 안 생기는 상태) |
| 13 | #8 recording-sessions 문서 정리 | 회의 녹음 | 초소형 | 📄 완료 |
| 14 | #1 Google Calendar 연동 | 제안함 | 소형~중형 (2026-08-15 재산정, 기존 "대형"에서 축소) | ✅ 코드 완료, 실환경 E2E 검증 남음 |
| 15 | #9 우선순위 변경 사유 텍스트 미사용 | 오늘 브리핑 | 소형 | ✅ 완료 |
| 16 | #10 score_breakdown 미표시 | 오늘 브리핑 | 소형 | ✅ 완료 |
| 17 | #15 녹음 일시정지 버튼 없음 | 회의 녹음 | 소형 | ✅ 완료 (AudioContext suspend/resume) |
| 18 | #17 할 일 필터 마감일 없음 (담당자 필터는 #6 결정으로 범위 제외) | 할 일 관리 | 소형(백엔드 반나절+프론트 반나절) | ✅ 완료 |
| 19 | #18 삭제 확인창에 제목 미포함 | 할 일 관리 | 초소형 | ✅ 완료 |
| 20 | #11 회의 참석자 미표시 | 회의 관리 | 소형~중형 | ⬜ |
| 21 | #19 Gmail 수동 동기화 중복 재노출 | 제안함 | 소형 (무시 메일 처리는 결정 대기) | 🟨 승인된 메일 필터링 완료, 무시 메일 처리는 결정 대기 |
| 22 | #12 `RecordingSession.status` 세분화 미표시 (2026-08-15 추가) | 회의 녹음 | 반나절 | ✅ 완료 (WebSocket `close` 이벤트로 처리 중 상태 표시, 프론트만으로 해결) |
| 23 | #26 등록된 Task 수정 UI 자체가 없음 (2026-08-15 신규 발견) | 할 일 관리 | 소형(프론트 반나절~1일) | ✅ 완료 |
| 24 | #27 회의록 검색 필터 UI 부재 (2026-08-15 신규 발견) | 회의록 검색 | 소형(프론트 반나절) | ✅ 완료 |
| 25 | #30 회의록 검색 전용 REST 엔드포인트 미사용 (2026-08-15 신규 발견) | 회의록 검색 | 문서 정정만 | ✅ 결정 완료 |
| 26 | #28 회의록 검색 참여자 필터 미지원 (2026-08-15 신규 발견) | 회의록 검색 | 결정 대기(#11에 종속) | ⏸️ |
| 27 | #29 Reranker 미구현 (2026-08-15 확인) | 회의록 검색 | 표시용(07 §8.2.1이 M4.4로 지정) | 📄 |
| 28 | #31 검색 결과 → 전체 회의록 이동 불가 (2026-08-15 신규 발견) | 회의록 검색 | 소형(회의 관리 #2 완료 후) | ⬜ |
| 29 | #32 `related_task_ids` 미계산(Calendar·Gmail) (2026-08-15 신규 발견) | 오늘 브리핑 | 소형(백엔드 반나절+프론트 반나절) | ✅ 완료 |
| 30 | #33 Calendar 미등록 일정이 중요 신호에 안 들어감 (2026-08-15 신규 발견) | 오늘 브리핑 | 결정 대기(중형 예상) | ⏸️ |
| 31 | #34 `data_freshness` 응답 미포함 (2026-08-15 확인) | 오늘 브리핑 | 낮은 우선순위(대체 표시 있음) | 📄 |
| 32 | #35 주간 업무보고 주차 선택 UI 부재 (2026-08-15 신규 발견) | 주간 업무보고 | 소형(프론트 반나절) | ✅ 완료 |
| 33 | #36 다음 주 계획 kind 구분 표시 없음 (2026-08-15 신규 발견) | 주간 업무보고 | 초소형(프론트 1시간) | ✅ 완료 |
| 34 | #37 미해결 이슈 개념 미구현 (2026-08-15 신규 발견) | 주간 업무보고 | 결정 대기(중형 예상) | ⏸️ |
| 35 | #38 "주요 회의 내용" 통합 부재 (2026-08-15 신규 발견) | 주간 업무보고 | 결정 대기(중형~대형 예상) | ⏸️ |

---

## 🏠 오늘 브리핑 (`Briefing.tsx`)

[15-workmate-ui-screens-reference.md의 🏠 오늘 브리핑](15-workmate-ui-screens-reference.md#-오늘-브리핑-briefingtsx)
(2026-08-15 신규 작성)을 기준으로 `Briefing.tsx`·`lib/workmate-types.ts`·`lib/workmate-format.ts`·
`app/workflows/daily_briefing.py`를 다시 대조했다. 이 화면은 `daily_briefing`+`rank_priorities` 두
Skill을 함께 호출하는 화면이다. 기존 #9·#10은 재확인 결과 그대로 유효했고, 15번 문서가 Schema까지
확인해 훨씬 구체적으로 정의되면서 이전에 못 찾았던 항목 2개(#32·#33)와 우선순위 낮은 참고 항목(#34)을
추가로 찾았다.

### 🗺️ 작업계획 (2026-08-15)

| Phase | 항목 | 내용 | 처리 |
| --- | --- | --- | --- |
| **1. 즉시 가능** (병렬) | #9, #10 | 순위 변경 사유 텍스트 표시, `score_breakdown` 타입 추가·표시 | 이번에 구현 |
| **2. 핵심 구현** | #32 | `related_task_ids`(이미 Task로 등록됐는지) 실제 계산 — Calendar·Gmail 둘 다 | 이번에 구현 |
| **3. 범위 제외** | #33, #34 | 아래 사유로 이번 작업에서 제외 | 결정/표시만 |

**#32 구현 방향**: `daily_briefing.py`가 이미 갖고 있는 `task_repository`로 `list(user_id)`를 한 번
호출해 `(source_type, source_id) → task_id` 매핑을 만들고, Calendar 이벤트의 `event.source_id`
(`{calendar_id}:{event_id}`)와 Gmail 메일의 `message.message_id`를 각각 대조해 `related_task_ids`를
채운다. 이미 제안함 승인 로직이 쓰는 것과 같은 식별자 형식이라 새 매칭 규칙을 만들 필요는 없다.

### #9. 우선순위 변경 사유가 백엔드 실제 텍스트를 안 씀

**범위**: 프론트엔드만

**현재 상태**: [03-data-priority-rules.md](03-data-priority-rules.md) §7 예시는 백엔드가 `마감이 내일로
가까워져 deadline 점수가 20에서 30으로 상승하여 4위에서 2위로 변경됨`처럼 점수 근거가 담긴 구체적 문장
(`PriorityChange.reason`)을 만든다고 정의한다. 그런데 `lib/workmate-format.ts`의 `movementLabel()`은 이
`reason` 필드를 아예 쓰지 않고 `change_type`과 순위 차이만으로 `↑ 2단계 상승` 같은 일반 라벨을 자체
생성한다. 백엔드가 계산한 실제 근거 텍스트가 화면에 전혀 노출되지 않는다. 재확인 결과 여전히 미수정
상태.

**작업**: `Briefing.tsx`의 우선순위 카드에 `change.reason`을 그대로(또는 `movementLabel()` 라벨과 함께)
표시.

**공수**: 1시간 이내

### #10. `score_breakdown` 필드가 타입에서 누락

**범위**: 프론트엔드만

**현재 상태**: `02-a2a-interface.md`·[15번 문서](15-workmate-ui-screens-reference.md#5-priorities-공통-필드-schema-priorityitem)가
정의하는 `score_breakdown`(deadline/importance/blocked_or_overdue/meeting_commitment/calendar_relevance
5개 요소, [03-data-priority-rules.md](03-data-priority-rules.md) §6의 배점 공식과 대응)이 있지만
`lib/workmate-types.ts`의 `PriorityItem` 타입에는 이 필드가 없다. `Briefing.tsx`도 `score`와
`reasons`만 쓴다. 재확인 결과 여전히 미수정 상태 — Schema상 이 필드는 선택(optional)이라 백엔드가
안 보내는 요청·회의에서는 빈 상태로 둬야 한다.

**작업**: 타입에 `score_breakdown` 추가 후 우선순위 카드에 점수 구성 요소를 펼쳐보기 형태로 표시(예:
"마감임박도 30 · 중요도 15 · 지연/차단 0 · 회의 약속 10 · 일정 연관 5").

**공수**: 반나절

### #32. `related_task_ids`가 항상 비어 있거나 필드 자체가 없음 (신규 발견)

**범위**: 백엔드 + 프론트

**현재 상태**: 15번 문서는 `calendar_events[]`·`important_signals[]` 모두 `related_task_ids`로 이미
Task 등록 여부를 표시해야 한다고 정의한다(04 §1, Schema). 실제로 `app/workflows/daily_briefing.py`를
보면:
- `calendar_events`는 `related_task_ids`를 **항상 빈 배열 `[]`로 하드코딩**한다 — 실제 Task와 대조하는
  로직 자체가 없다.
- `important_signals`(Gmail 메일)는 **`related_task_ids` 필드 자체를 안 만든다**(`type`/`source_id`/
  `summary`만 있음). `lib/workmate-types.ts`의 `CalendarItem`·`ImportantSignal` 타입에도 이 필드가
  없어 프론트가 받아도 쓸 방법이 없다.

결과적으로 사용자는 이미 등록한 회의·메일이 브리핑에 매번 "아직 안 한 일"처럼 다시 보인다 — 04 §1이
명시한 "related_task_ids가 비어 있으면 미등록, 값이 있으면 이미 등록된 Task" 판단을 화면에서 전혀
할 수 없다.

**작업**: `daily_briefing.py`에서 `task_repository.list(user_id)`로 `(source_type, source_id) →
task_id` 매핑을 만들고, Calendar 이벤트는 `event.source_id`로, Gmail 메일은 `message.message_id`로
대조해 `related_task_ids`를 채운다. 프론트 타입에 `related_task_ids?: string[]` 추가, 목록에 "등록됨"
배지 표시.

**공수**: 백엔드 반나절, 프론트 반나절

### #33. `important_signals`에 Calendar 미등록 일정이 빠짐 — 결정 필요

**범위**: 백엔드(새 판정 로직 필요) — 결정 대기

**현재 상태**: 04 §1은 "Calendar의 미등록 할 일 후보도 기존 `important_signals`에 포함한다"고
정의하지만, `daily_briefing.py`의 `important_signals`는 Gmail 메일만으로 만들어진다
(`for message in messages`) — Calendar 이벤트는 전혀 순회하지 않는다.

이건 #32처럼 "이미 있는 값을 못 쓰는" 문제가 아니라, **"이 Calendar 일정이 할 일 후보로 볼 만한가"를
새로 판정하는 로직 자체가 없는** 더 큰 문제다 — 제안함의 Calendar 동기화(`dev_calendar_sync_api.py`)가
쓰는 "확정·미래 일정" 필터와 개념이 겹치는데, 브리핑에도 같은 판정을 새로 넣을지 제안함 판정 결과를
재사용할지 결정이 필요하다.

**다음 액션**: 착수 전 제품 결정 필요. 이번 작업 범위에서는 제외.

**공수**: 결정 후 별도 산정(중형 예상)

### #34. `data_freshness`가 계산은 되지만 응답에 실리지 않음 — 우선순위 낮음, 참고용

**범위**: 백엔드(참고용, 당장 급하지 않음)

**현재 상태**: `daily_briefing.py`는 `provider_freshness`(email/calendar 마지막 조회 시각) 딕셔너리를
계산하지만, `WorkflowResult`엔 이 값을 담을 필드가 아예 없어 그대로 버려진다 — Schema가 정의하는
`WorkmateResultEnvelope.data_freshness`가 스킬챗 응답까지 전혀 도달하지 못한다.

**다만 실사용에 당장 문제는 없다** — `Briefing.tsx`의 소스별 "최신/지연" 배지는 정확한 타임스탬프
대신 이미 **`warnings[].source` 존재 여부**로 대체 판단하고 있다(경고가 있으면 "지연", 없으면
"최신"). 사용자가 실제로 필요로 하는 신호(지금 이 소스가 정상인가)는 이미 다른 방식으로 충족되고
있어, `data_freshness` 배선 자체의 긴급도는 낮다.

**다음 액션**: 없음. 정확한 시각까지 보여줘야 할 필요가 생기면 그때 `WorkflowResult`에 필드를 추가한다.

---

## ✅ 오늘 브리핑(#9·#10·#32) 구현완료보고서 (2026-08-15)

작업계획대로 진행했다. #33(Calendar 미등록 일정을 신호에 포함)은 새 판정 로직이 필요해 결정 대기로,
#34(`data_freshness` 배선)는 이미 `warnings` 기반 대체 표시가 있어 우선순위 낮음으로 계획대로 이번
범위에서 제외했다.

### #9. 순위 변경 사유 텍스트 표시 — 완료

우선순위 카드에 `movementLabel()` 배지는 그대로 두고, 그 아래에 `change.reason`(서버가 계산한 실제
근거 문장)을 작은 회색 텍스트로 추가했다 — 기존 라벨("↑ 2단계 상승")과 실제 근거를 둘 다 볼 수 있다.

### #10. `score_breakdown` 표시 — 완료

`lib/workmate-types.ts`에 `PriorityScoreBreakdown` 타입과 `PriorityItem.score_breakdown?`(선택 필드,
Schema와 동일)을 추가했다. 값이 있을 때만 "마감임박도 30 · 중요도 15 · 지연/차단 0 · 회의 약속 10 ·
일정 연관 5" 형태로 카드에 펼쳐 보여준다.

### #32. `related_task_ids` 실제 계산 — 완료

- **백엔드**(`app/workflows/daily_briefing.py`): `task_repository.list(user_id)`로
  `(source_type, source_id) → task_id` 매핑을 한 번 만들고, Calendar 이벤트는 `event.source_id`
  (`{calendar_id}:{event_id}`)로, Gmail 메일은 `message.message_id`로 대조해 `related_task_ids`를
  채운다. 새 매칭 규칙을 만들 필요 없이 제안함 승인 때 저장하는 `Task.source_id`와 형식이 이미
  같았다.
- **프론트**: `CalendarItem`·`ImportantSignal` 타입에 `related_task_ids?: string[]` 추가, 값이 있는
  항목에 "등록됨" 표시를 붙였다.

### 검증

- **백엔드 회귀**: `uv run pytest tests/` — **213 passed, 10 skipped, 0 failed**(#32 회귀 테스트
  포함 — 등록 전엔 `related_task_ids`가 빈 배열, Task를 만든 뒤엔 정확한 `task_id`가 채워지는 것을
  실제 `daily_briefing` Workflow 실행으로 확인).
- **프론트엔드**: `eslint` clean, `npm run build` 성공, `npm test` — **29 passed**.
- 두 서버 모두 최신 코드로 재시작 완료(이번엔 백엔드 프로세스가 예기치 않게 내려가 있던 것도 함께
  발견해 재기동함).

### 변경/신규 파일 목록

| 파일 | 종류 |
| --- | --- |
| `workmate-agent/app/workflows/daily_briefing.py` | 수정 (`related_task_ids` 실제 계산) |
| `workmate-agent/tests/test_daily_briefing.py` | 수정 (#32 회귀 테스트 추가) |
| `workmate-ui/lib/workmate-types.ts` | 수정 (`PriorityScoreBreakdown`, `related_task_ids?` 필드 추가) |
| `workmate-ui/app/views/Briefing.tsx` | 수정 (순위 변경 사유·점수 구성·등록됨 배지 표시) |
| `workmate-agent/app/internal_chat.py` | 수정 (`PyJWKClient` `jwks_url`별 캐시, 네트워크 예외 → 503 CORS 응답 변환) |
| `workmate-agent/tests/test_internal_chat.py` | 수정 (JWKS 네트워크 실패 회귀 테스트 추가) |
| `workmate-agent/app/workflows/daily_briefing.py` | 수정 (`WorkflowResult.data` 채움 — HTTP 응답에서 항상 `null`이던 버그 수정) |
| `workmate-agent/app/workflows/priority.py` | 수정 (`WorkflowResult.data` 채움, 같은 버그) |
| `workmate-agent/tests/test_daily_briefing.py` | 수정 (`result.data` 채움 회귀 테스트 추가) |
| `workmate-agent/tests/test_priority_workflow.py` | 수정 (`result.data` 채움 회귀 테스트 추가) |

### ⚠️ 실사용 중 추가로 발견·수정한 버그(아홉 번째): OIDC JWKS 검증이 요청마다 Google에 실시간 네트워크 호출을 하다 그대로 크래시

한참 뒤(2026-08-16) 실사용 중 오늘 브리핑 화면이 로딩도 오류도 없이 그냥 "브리핑을 아직 실행하지
않았습니다"에 멈춰 있는 것을 발견했다. 서버 로그에 정확히 그 시점 근처로 같은 예외가 연달아 두 번
찍혀 있었다(오늘 브리핑은 `daily_briefing`·`rank_priorities` 두 Skill을 동시에 호출한다):

```
File "app/internal_chat.py", line 69, in _authenticated_user
    signing_key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token)
  ...
http.client.RemoteDisconnected: Remote end closed connection without response
```

**원인**: `_authenticated_user()`가 인증되는 **모든** 요청마다 `PyJWKClient(jwks_url)`을 새로
만들고 있었다 — PyJWT의 내장 Key 캐시는 Client 인스턴스에 딸려 있는데, 매번 새 인스턴스를 쓰면
그 캐시가 전혀 재사용되지 못해 인증된 요청 하나하나가 실제로 Google의 JWKS 엔드포인트에 네트워크
호출을 내보내고 있었다. 트래픽이 늘거나 네트워크가 한순간이라도 끊기면(이번처럼
`RemoteDisconnected`) 실패할 확률이 그만큼 계속 쌓이는 구조였다. 그런데 이 네트워크 예외는
`jwt.PyJWTError`가 아니라서 바로 아래 `except jwt.PyJWTError` 절이 잡지 못했고, `_authenticated_user`는
Route 본문이 아니라 **Dependency 단계**에서 실행돼 `internal_chat.py`의 `validate_message()`가
가진 `ValueError`/`RuntimeError` 처리(다섯·여섯 번째 버그에서 추가)와도 완전히 다른, 아직 방어되지
않은 경로였다. 결국 CORS 없는 500이 됐고, 오늘 브리핑이 동시에 보낸 두 요청이 나란히 이 순간을
맞으면서 화면은 로딩도 오류도 아닌 "아직 실행 안 함" 상태에 그대로 멈춰 있었다(두 `useSkillRunner`
상태가 둘 다 `loading:false / data:null / error:null`인 최초 상태에서 벗어나지 못함).

**수정**: (1) `PyJWKClient`를 `jwks_url`별로 `@lru_cache`해 재사용 — PyJWT의 Key 캐시가 실제로
동작해 대부분의 요청이 더 이상 네트워크를 타지 않는다(신뢰성과 성능 둘 다 개선). (2)
`_authenticated_user()`에 `except (URLError, OSError, TimeoutError)`를 추가해 남은 네트워크
실패도 CORS 헤더가 붙는 503으로 변환(재시도 가능한 일시적 문제이므로 401이 아니라 503).
`tests/test_internal_chat.py`에 회귀 테스트 추가(`_jwks_client`를 Mock해 `URLError` 발생시켜
503 + CORS 헤더 확인). 백엔드 회귀 최종 **229 tests(218 passed, 11 skipped)**.

### 🔴 실사용 중 추가로 발견·수정한 버그(열 번째, 진짜 원인): `daily_briefing`·`rank_priorities`가 HTTP 응답에 `data`를 아예 채우지 않음

아홉 번째 버그를 고치고 재기동했는데도 화면은 여전히 "브리핑을 아직 실행하지 않았습니다"에
멈춰 있었다. 이번엔 서버 로그부터 다시 봤는데 — 놀랍게도 `daily_briefing`·`rank_priorities`
요청 둘 다 **200으로 정상 완료**되고 있었다. 즉 아홉 번째 수정은 실제로 효과가 있었고(서버가
더 이상 크래시하지 않음), 화면이 멈춘 진짜 원인은 처음부터 따로 있었다.

**원인**: `internal_chat.py`가 HTTP 응답을 만들 때 `"data": result.data`로 `Workflow`가 준
`WorkflowResult.data` 필드를 그대로 내보내는데, `daily_briefing.py`·`app/workflows/priority.py`
(`rank_priorities`)의 `WorkflowResult(...)` 생성 코드에 `data=`가 **아예 빠져 있었다** — `text=`
(JSON 문자열)만 채우고 있었다. `analyze_meeting`·`search_meetings`(`app/workflows/meetings.py`)와
`weekly_report`는 전부 `data=typed_result`를 정확히 채우고 있어서 문제가 없었는데, 오늘 브리핑이
쓰는 이 두 Skill만 빠져 있었던 것. 프론트(`lib/use-skill.ts`)는
`response.artifact.data && "data" in response.artifact.data ? response.artifact.data.data : null`로
읽는데, `artifact.data`가 애초에 `null`이니 요청이 아무리 성공해도 `briefing.data`/`priorities.data`는
항상 `null`이었다 — `loading:false`, `error:null`, `data:null`인 채로 영원히 멈춰, 화면엔 로딩도
오류도 아닌 "아직 실행 안 함" 초기 문구만 보였다. 기존 테스트들은 이 버그를 잡지 못했는데,
`json.loads(result.text)`만 검증하고 `result.data` 자체는 한 번도 assert하지 않고 있었다
(이 세션의 여러 직접 검증 스크립트도 같은 이유로 `result.text`를 파싱해 우회했을 뿐, `data`
필드 자체가 비어 있다는 걸 알아채지 못했다) — HTTP 계층에서만 드러나는 결함이었다.

**수정**: `daily_briefing.py`·`priority.py` 두 곳의 `WorkflowResult(...)`에 `data=result_payload`를
추가(다른 3개 Skill과 동일한 관례로 통일). `tests/test_daily_briefing.py`·`tests/test_priority_workflow.py`에
`result.data`가 `text`와 같은 내용을 담고 있는지 확인하는 회귀 테스트 추가. 실제 사용자 데이터로
두 Workflow를 직접 호출해 `result.data is not None`과 `text` 파싱 결과와 일치하는 것 확인. 백엔드
재기동. 백엔드 회귀 최종 **229 tests(218 passed, 11 skipped)**, 변화 없이 그대로 통과(신규
Assertion만 추가돼 기존 테스트 수는 동일, 항목 2개 강화).

### 📝 실사용 중 추가로 개선한 항목: 중요 업무 신호가 전부 같은 자리표시자 문구로만 보임

화면이 정상 동작하기 시작한 뒤, `중요 업무 신호` 카드 100개가 전부 "읽지 않은 메일 신호"라는
똑같은 문구로만 보인다는 걸 확인했다(버그 리포트라기보단 "문구가 별로다"는 사용성 피드백으로
시작했지만, 실제로는 데이터 결함이었다). 원인: `daily_briefing.py`가 Gmail
`users.messages.list`(`GmailAdapter.list_messages`)만 호출하는데, 이 API는 `id`·`threadId`만
주고 **제목·Snippet은 절대 채워주지 않는다**(코드 자체에도 이미 이 사실이 주석으로 남아 있었다) —
그래서 `message.snippet`이 항상 `None`이라 자리표시자만 나온 것이었다. 실제 제목·Snippet은
메시지별로 `GmailAdapter.get_message()`를 따로 호출해야 얻을 수 있다.

**수정**: 목록 조회 후 각 메시지의 실제 제목·Snippet을 `asyncio.gather` + `asyncio.to_thread`로
**병렬** 조회해 보강했다(순차 호출이면 메일이 많을 때 브리핑 로딩이 메일 수만큼 느려진다). 이
보강은 부가 기능일 뿐이라 별도 `try`로 감싸 실패해도 이메일 조회 자체의 성공/실패 신호(경고)를
더럽히지 않고 조용히 기존 자리표시자로 되돌아간다. 프론트(`Briefing.tsx`)는 이제 최대 500자까지
올 수 있는 실제 메일 본문 미리보기를 받으므로, 카드가 본문 길이만큼 늘어나 보이지 않게 새
`truncateText()` 유틸(단어 경계에서 자르고 말줄임표)로 140자까지 줄이고, 이미 제안함 화면이
쓰던 `decodeHtmlEntities()`도 같이 적용해 `&#39;` 같은 HTML Entity가 그대로 노출되던 것도
고쳤다. 회귀 테스트 추가(백엔드: 개별 조회 결과가 실제로 쓰이는지, 실패해도 경고가 안 남는지;
프론트: `truncateText` 단위 테스트 3개). 실제 Gmail 계정으로 재검증 — 100건 중 83건이 서로 다른
실제 제목+본문 미리보기로 나오는 것 확인(나머지는 실제로 내용이 겹치는 뉴스레터류). 백엔드 회귀
**230 tests(219 passed, 11 skipped)**, 프론트 `eslint` clean·`npm run build` 성공·`npm test`
**33 passed**. 두 서버 모두 최신 코드로 재기동, 배포된 번들에 반영 확인.

**후속(같은 날, 실사용 중 확인)**: 신호 문구가 실제 메일 내용으로 보이기 시작하자, 이번엔 "최근
검색에 표시됨" 같은 구글 마케팅 알림 메일까지 그대로 "중요 업무 신호"에 섞여 나오는 게 눈에 띄었다
— `is:unread`만으로는 사람이 보낸 업무 메일과 자동 발송 알림을 구분하지 못하는 게 원인이었다(애초에
"중요도" 판단 자체가 없고 "안 읽음" 전부를 그대로 노출하는 구조). 사용자 확인 후 Gmail 검색어에
`category:primary`를 추가해 Gmail이 스스로 분류하는 프로모션·소셜·업데이트 탭 메일을 제외했다.
회귀 테스트 추가(쿼리 문자열 자체를 검증), 실제 계정으로 재검증 — 마케팅 메일이 결과 상위에서
사라지고 실제 업무 메일 위주로 나오는 것 확인. 백엔드 회귀 **231 tests(220 passed, 11 skipped)**.
백엔드 재기동.

**추가 후속(같은 날, 실사용 중 요청)**: 100건은 여전히 너무 많다는 요청으로 `max_results`를
10으로 낮췄다. `messages.list`는 정렬 조건을 따로 받지 않지만 Gmail 검색 결과의 기본 순서 자체가
최신 수신순이라, 개수만 줄이면 자연히 "최신 10건"이 된다 — 별도 정렬 로직은 필요 없었다. 회귀
테스트에 `max_results` Assertion 추가, 실제 계정으로 `total signals: 10` 확인. 백엔드 재기동.

### 변경/신규 파일 목록 (아홉·열 번째 버그, 신호 문구 개선 공통)

| 파일 | 종류 |
| --- | --- |
| `workmate-agent/app/internal_chat.py` | 수정 (`PyJWKClient` `jwks_url`별 캐시, 네트워크 예외 → 503 CORS 응답 변환) |
| `workmate-agent/tests/test_internal_chat.py` | 수정 (JWKS 네트워크 실패 회귀 테스트 추가) |
| `workmate-agent/app/workflows/daily_briefing.py` | 수정 (`WorkflowResult.data` 채움, Gmail 제목·Snippet 병렬 보강, `category:primary`로 프로모션·소셜·업데이트 메일 제외) |
| `workmate-agent/app/workflows/priority.py` | 수정 (`WorkflowResult.data` 채움) |
| `workmate-agent/tests/test_daily_briefing.py` | 수정 (`result.data` 채움 + 신호 문구 보강 회귀 테스트 추가) |
| `workmate-agent/tests/test_priority_workflow.py` | 수정 (`result.data` 채움 회귀 테스트 추가) |
| `workmate-ui/lib/workmate-format.ts` | 수정 (`truncateText()` 신규) |
| `workmate-ui/tests/workmate-format.test.mts` | 수정 (`truncateText` 단위 테스트 추가) |
| `workmate-ui/app/views/Briefing.tsx` | 수정 (신호 요약에 `decodeHtmlEntities`·`truncateText` 적용) |
| `google-oauth-test/auth_flow.py` | 수정 (저장된 Token의 실제 동의 범위를 원본 JSON에서 직접 확인 — 부족한 Scope인데도 조용히 Refresh만 하고 새 동의 화면을 안 띄우던 버그 수정, `open_browser=False`로 URL을 항상 콘솔에 출력) |
| `google-oauth-test/print_auth_url.py` | 신규 (`run_local_server()`의 자동 브라우저 실행이 원인 불명으로 실패하는 환경을 위한 수동 인증 URL 출력 스크립트, PKCE `code_verifier`를 `.pkce_verifier`에 저장) |
| `google-oauth-test/exchange_code.py` | 신규 (수동 흐름 2/2 — 브라우저 리다이렉트 주소의 `code`와 저장된 `code_verifier`로 토큰 교환) |
| `google-oauth-test/.gitignore` | 수정 (`.pkce_verifier` 추가) |

---

## 📊 주간 업무보고 (`Report.tsx`)

[15-workmate-ui-screens-reference.md의 📊 주간 업무보고](15-workmate-ui-screens-reference.md#-주간-업무보고-reporttsx)
(2026-08-15 신규 작성)를 기준으로 `Report.tsx`·`lib/workmate-format.ts`·`app/workflows/weekly_report.py`·
`app/workflows/weekly_classification.py`를 다시 대조했다. 기존엔 "이 화면 고유의 갭은 없음"이라고
적혀 있었는데, 실제로는 갭이 4개 있었다. [공통/전역 #5 Task Polling](#-공통전역-여러-화면이-공유하는-hook·api-클라이언트)도
여전히 적용된다.

### 🗺️ 작업계획 (2026-08-15)

| Phase | 항목 | 내용 | 처리 |
| --- | --- | --- | --- |
| **1. 즉시 가능** (병렬) | #35, #36 | 주차 선택 UI 추가, `next_week_plans`의 `kind` 구분 표시 | 이번에 구현 |
| **2. 범위 제외** | #37, #38 | 아래 사유로 이번 작업에서 제외 | 결정 대기 |

**#35·#36이 이번에 구현 가능한 항목이다.** 둘 다 백엔드는 이미 올바르게 동작하는데(`week_of` 필터
전체 지원, `next_week_plans`의 `kind` 분류도 `extract_next_week_plans`/`validate_next_week_plans`가
이미 정확히 계산해둠) 프론트가 그 값을 안 쓰고 있던 경우라 저위험·저비용이다. #37·#38은 백엔드에
**개념 자체가 없는** 더 큰 항목이라 결정 없이 코드부터 짜면 잘못된 설계로 갈 위험이 있어 제외한다.

### #35. 주차 선택 UI 부재

**범위**: 프론트엔드만

**현재 상태**: 09 §1이 요구하는 "기간별 보고서 조회"에 대응하는 백엔드 `week_of` 입력(02 §2.3,
`app/workflows/weekly_report.py`의 `normalize_week_scope`)은 이미 완전히 동작하지만, `Report.tsx`는
`weeklyReportInput()`을 인자 없이 호출해 **항상 이번 주만** 조회한다. 지난주 보고서를 다시 보거나
다른 주를 확인할 방법이 없다.

**작업**: `weeklyReportInput()`에 `week_of` 선택 인자 추가, `Report.tsx`에 주차 선택 UI(날짜 입력 1개
또는 이전/다음 주 이동 버튼) 추가.

**공수**: 프론트 반나절

### #36. 다음 주 계획의 `kind`(확정/이월/제안) 구분 표시 없음

**범위**: 프론트엔드만

**현재 상태**: [03-data-priority-rules.md](03-data-priority-rules.md) §5는 "근거 없는 LLM 생성 계획은
넣지 않고 별도 `제안`으로 표시한다"고 요구하고, 백엔드 `extract_next_week_plans`/
`validate_next_week_plans`(`app/workflows/weekly_classification.py`)가 이미 각 계획을
`planned`(확정 마감)/`carry_over`(이월된 미완료 Action Item)/`suggestion`(근거는 있지만 확정 일정은
아님)으로 정확히 분류해 보낸다. `lib/workmate-types.ts`의 `PlanItem` 타입에도 `kind` 필드가 이미
있다. 그런데 `Report.tsx`의 `PlanBlock`은 `item.kind`를 전혀 읽지 않고 모든 계획을 똑같이
"✓ 제목"으로만 보여준다 — 확정된 일정과 근거가 약한 제안이 화면에서 구분되지 않는다.

**작업**: `PlanBlock`에서 `kind`별로 다른 배지·스타일(예: `planned`="확정", `carry_over`="이월",
`suggestion`="제안")을 표시.

**공수**: 프론트 1시간 이내

### #37. 미해결 이슈(`unresolved_issues`)가 항상 빈 배열 — "이슈" 개념 자체가 없음, 결정 필요

**범위**: 백엔드(새 개념 정의 먼저 필요) — 결정 대기

**확인된 사실**: `app/workflows/weekly_classification.py`의 `build_weekly_report_data()`는
`"unresolved_issues": []`를 **하드코딩**하고, `weekly_report.py`의 `execute()`도 이 값을 이후 절대
덮어쓰지 않는다 — 채우는 로직이 코드베이스 어디에도 없다. `Report.tsx`의 통계 카드가 "미해결 이슈 0"을
보여주는 건 실제로 이슈가 없어서가 아니라 **애초에 셀 방법이 없기 때문**이다.

더 근본적으로, `app/domain/weekly.py`의 `WeeklyBucket`(`completed`/`in_progress`/`delayed`/
`excluded`)엔 "이슈"에 대응하는 분류 자체가 없다. `blocked` 상태 Task는 이미 `delayed`로 분류되고
있어, "이슈"가 `delayed`와 다른 무엇을 의미해야 하는지(예: 마감을 크게 넘긴 것, 여러 번 재조정된
것, 별도로 플래그를 단 것)부터 정의해야 한다.

**다음 액션**: "미해결 이슈"의 판정 기준을 먼저 결정. 이번 작업 범위에서는 제외.

**공수**: 결정 후 별도 산정(백엔드 신규 분류 로직 필요, 중형 예상)

### #38. "주요 회의 내용" 통합이 전혀 구현되지 않음

**범위**: 백엔드(설계 필요) — 결정 대기

**확인된 사실**: 04 §2는 "회의와 맥락 연결", "회의 주요 내용 통합"을 처리 흐름에 명시하고, 출력
Markdown 예시에도 `## 주요 회의 내용` 절이 있다. 그런데 `app/workflows/weekly_report.py`·
`weekly_classification.py`는 Task Repository만 조회할 뿐 **Meeting·MeetingChunk를 어디서도 조회하지
않는다** — LLM 프롬프트에도 회의 데이터가 전달되지 않고, `_render_weekly_report_markdown()`의 고정
섹션 목록(완료/진행/지연/미해결 이슈/다음 주 계획)에도 "주요 회의 내용" 자체가 없다. 15번 문서가
이미 정리했듯 이 내용은 `WeeklyReportResult` Schema에 구조화 필드로도 없어 프론트가 만들 수 있는
UI 자체가 없다 — 순수 백엔드 설계 공백이다.

**다음 액션**: 이번 주 회의를 어떻게 선정("주요"의 기준)하고 요약을 LLM 입력에 어떻게 넣을지(전체
Transcript 전달은 Context 초과 위험이 있어 `Meeting.summary`만 쓸지 등) 설계 결정이 먼저 필요하다.
이번 작업 범위에서는 제외.

**공수**: 결정 후 별도 산정(신규 조회·LLM 입력 설계 필요, 중형~대형 예상)

---

## ✅ 주간 업무보고(#35·#36) 구현완료보고서 (2026-08-15)

작업계획대로 진행했다. #37(미해결 이슈 개념 부재)·#38("주요 회의 내용" 통합 부재)은 계획대로 이번
범위에서 제외했다 — 둘 다 코드를 먼저 짜기보다 개념·설계 결정이 선행돼야 하는 항목이다.

### #35. 주차 선택 UI — 완료

`lib/workmate-format.ts`의 `weeklyReportInput()`에 선택적 `weekOf` 인자를 추가했다(생략하면 기존과
동일하게 서버 기본값 사용). `Report.tsx`에 "◀ 이전 주"/"다음 주 ▶" 버튼과, 현재 주가 아닐 때만 보이는
"이번 주로" 버튼을 추가했다 — 현재 로드된 `period.start`(그 주의 월요일)를 기준으로 ±7일씩 옮겨
`week_of`를 다시 계산하는 방식이라 반복 이동에도 항상 같은 요일의 인접 주로 정확히 이동한다.

### #36. 다음 주 계획 `kind` 구분 표시 — 완료

`PlanBlock`이 이제 `item.kind`를 읽어 "확정"(`planned`)/"이월"(`carry_over`)/"제안"(`suggestion`)
배지를 붙인다. `suggestion`만 다른 색(기존 `.analysis.pending` 스타일 재사용)으로 구분해, 근거가
약한 LLM 제안이 확정된 일정처럼 보이지 않게 했다 — 03 §5가 요구하는 원칙을 그대로 반영했다.

### 검증

- **프론트엔드**: `eslint` clean, `npm run build` 성공, `npm test` — **30 passed**(신규 `weekOf`
  조립 테스트 포함).
- **백엔드**: 이번 항목은 코드 변경이 없어 회귀만 재확인 — `uv run pytest tests/` **213 passed, 10
  skipped**(변화 없음).
- 프론트 서버 최신 코드로 재시작 완료(백엔드는 변경이 없어 재시작 불필요, 헬스체크로 정상 확인만).

### 변경/신규 파일 목록

| 파일 | 종류 |
| --- | --- |
| `workmate-ui/lib/workmate-format.ts` | 수정 (`weeklyReportInput()`에 `weekOf` 인자 추가) |
| `workmate-ui/tests/workmate-format.test.mts` | 수정 (`weekOf` 조립 회귀 테스트 추가) |
| `workmate-ui/app/views/Report.tsx` | 수정 (주차 이동 버튼, 계획 `kind` 배지 추가) |
| `workmate-agent/.env` | 수정 (`LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL` 추가, 기존 `OPENAI_*` 값 재사용, gitignored) |
| `workmate-agent/migrations/002_work_domain.sql` | 수정 (`tasks.task_id` `uuid → text`) |
| `workmate-agent/migrations/003_priority_snapshots.sql` | 수정 (`ranked_task_id` `uuid → text`) |
| `workmate-agent/tests/test_work_domain_migration.py` | 수정 (`task_id`가 `uuid`가 아니어야 하는 이유를 명시하는 회귀 테스트 추가) |

### 📝 실사용 중 확인한 로컬 개발 환경 설정 공백(코드 버그 아님)

`search_meetings`용 `DATABASE_URL`과 마찬가지로, `weekly_report`의 요약 문장은 이 세션의 다른
모든 기능(`meeting_analysis.py`의 `OPENAI_API_KEY`, `EMBEDDING_*`, `STT_*`)과는 **다른 이름의**
환경변수 `LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL`(`app/workflows/weekly_report.py`)을 요구한다.
`.env`에 이 셋이 없어 실사용 중 화면에 `llm: LLM_BASE_URL and LLM_API_KEY are required (재시도
가능)` 경고가 떴다 — **이건 코드 버그가 아니라 우아한 성능 저하가 정확히 설계대로 동작한 것**이다
(`LLMProviderError`를 workflow 내부에서 잡아 `warnings`로만 붙이고 원장 기반 부분 결과는 그대로
반환, CORS 없는 500으로 새지 않음). 이미 발급돼 있는 `OPENAI_API_KEY`/`OPENAI_MODEL`을 재사용해
`.env`에 `LLM_BASE_URL=https://api.openai.com/v1`·`LLM_API_KEY=<OPENAI_API_KEY와 동일>`·
`LLM_MODEL=<OPENAI_MODEL과 동일>`을 추가하고 백엔드를 재기동해 실제 LLM 요약이 정상 생성되는 것
확인(경고 사라짐, 실제 한국어 요약 문장 확인). **주의**: 이 이름 불일치(`LLM_*` vs `OPENAI_*`) 자체는
정리할 만한 기술 부채이지만 이번엔 건드리지 않았고, 앞으로 백엔드를 재기동할 때는 `DATABASE_URL`뿐
아니라 이 `LLM_*` 3종도 `.env`에 있는지 확인해야 한다.

### 🔴 실사용 중 추가로 발견·수정한 버그(자체 유발): `DATABASE_URL` 도입이 실제 Task 데이터를 화면에서 사라지게 함

LLM 경고를 고쳤는데도 화면엔 여전히 완료 0·진행 0·지연 0·미해결 0, "이번 주는 별도 보고할 업무
항목이 없습니다"만 떴다 — "이전 주"를 눌러도 마찬가지였다. 데이터 자체가 없다고 판단하기 전에
`app/task_api.py`·`app/workflows/daily_briefing.py`(`weekly_report`가 재사용)의 저장소 선택
주석을 다시 보니:

```python
def _repositories() -> tuple[TaskRepository, SyncStateRepository]:
    """운영 PostgreSQL 또는 로컬 SQLite의 업무·동기화 Repository를 선택한다."""
    dsn = os.getenv(DATABASE_URL_ENV)
    if dsn:
        return PostgresTaskRepository(dsn), PostgresSyncStateRepository(dsn)
    path = os.getenv(TASK_DB_PATH_ENV, ".runtime/tasks.sqlite3")
    return SQLiteTaskRepository(path), SQLiteSyncStateRepository(path)
```

**원인**: `search_meetings`를 고치려고 이전 항목(다섯 번째 버그)에서 백엔드 재기동 절차에
`DATABASE_URL`을 추가했는데, `task_api.py`의 `/api/v1/tasks`(할 일 관리 REST)와
`daily_briefing.py`의 `_repositories()`(오늘 브리핑·주간 업무보고가 공유)가 **정확히 같은 규칙**을
쓴다 — `DATABASE_URL`이 있으면 무조건 Postgres로 전환하고, 그 안에 실제 사용자 데이터가 있는지는
따지지 않는다. `search_meetings`만 고치려던 환경변수가 할 일 관리·오늘 브리핑·주간 업무보고
**세 화면 전부**의 Task 데이터 원본을 실사용자의 12건이 쌓여 있는 SQLite(`.runtime/tasks.sqlite3`)에서,
비어 있던(정확히는 이번 세션 통합 테스트가 남긴 무관한 테스트 fixture 10건만 있던) 로컬 개발용
Postgres 컨테이너로 조용히 바꿔버린 것 — 크래시도, 경고도 없이 그냥 "0건"으로 보였다. 이건 지금까지의
"CORS 없는 500" 계열과 다른 **완전히 새로운 종류의 실사용 버그**로, 내가 다섯 번째 버그를 고치며
직접 유발한 회귀다.

Task 데이터를 옮기려다 **여덟 번째 버그**를 하나 더 발견했다: `migrations/002_work_domain.sql`의
`tasks.task_id`가 `uuid`로 선언돼 있었는데, 제안함에서 승인한 Task는 `app/proposal_api.py`가
`f"proposal-{source_type}-{source_id}"` 형태의 **결정적 문자열 ID**를 쓴다(같은 제안을 다시
승인해도 같은 Task가 되도록). `user_id`와 정확히 같은 유형의 버그였다 — SQLite는 처음부터
`task_id TEXT`였는데 이 Postgres Migration만 어긋나 있었다.

**수정**: (1) `migrations/002_work_domain.sql`의 `task_id`와 `migrations/003_priority_snapshots.sql`의
`ranked_task_id`를 `uuid → text`로 정정, 계약 테스트 추가. (2) 로컬 `workmate-pg-dev`의 `tasks`·
`priority_snapshots` 테이블을 새 스키마로 재생성. (3) SQLite의 실제 Task 12건을 `id`·`상태`·
`마감일`·`생성/수정 시각`을 그대로 보존한 채 Postgres로 일회성 이전(`PostgresTaskRepository.create()`
재사용, `COALESCE(%s, now())`가 명시적 timestamp를 그대로 보존함을 확인). (4) `weekly_report`·
`daily_briefing`·`task_api.task_repository()` 세 경로 모두 실제 Workflow를 직접 호출해 12건 중
11건(완료 3·진행 4·지연 4, 오늘 브리핑 우선순위 3건)이 정상적으로 보이는 것 확인(1건은 기존
분류 규칙상 `excluded`로 정상 제외). 백엔드 회귀 최종 **228 tests** — `DATABASE_URL` 없이
217 passed/11 skipped, `WORKMATE_TEST_DATABASE_URL` 포함 228 passed/0 skipped 둘 다 확인.
테스트 fixture로 남아 있던 무관한 10건은 실제 사용자 데이터와 겹치지 않아 무해하지만, 삭제
시도는 Bash 안전장치에 막혀 남겨 뒀다(필요하면 사용자 승인 하에 직접 정리 가능).

> ⚠️ **재발 방지 메모**: `DATABASE_URL`이 설정되면 `search_meetings`뿐 아니라 Task·동기화 상태·
> 우선순위 저장소 전체가 Postgres로 전환된다 — 이 넷은 "따로 켜고 끌 수 있는" 설정이 아니라
> 하나로 묶여 있다. 로컬 개발에서 `DATABASE_URL`을 켤 때는 Task 데이터도 함께 Postgres에 있는지
> 반드시 확인해야 하며, SQLite에만 있는 최신 Task를 만든 직후라면 이번처럼 재이전이 필요할 수 있다.

---

## 📋 할 일 관리 (`Tasks.tsx`)

[15-workmate-ui-screens-reference.md의 📋 할 일 관리](15-workmate-ui-screens-reference.md#-할-일-관리-taskstsx)
(2026-08-15 신규 작성)를 기준으로 `app/task_api.py`·`Tasks.tsx`·`lib/workmate-api.ts`를 다시 대조했다.
기존 #3·#6·#17·#18은 여전히 유효해 그대로 남기고, 다시 보며 새로 찾은 것과 기존 항목의 수정 사항을
아래에 반영했다.

> ⚠️ **가장 큰 발견**: 이 화면엔 **기존 Task를 수정하는 UI 자체가 없다**(#26). 제목·마감일·중요도·
> 상태(완료/되돌리기 토글 제외) 전부 등록 이후엔 못 고친다. 15번 문서가 "등록과 수정은 같은 폼을
> 쓴다"(09 §2.2)를 기준으로 정의했는데, 실제로는 등록 폼만 있고 수정 폼 자체가 없다.

### 🗺️ 작업계획 (2026-08-15)

**범위**: #26·#18·#17·#6. **#3은 이번 범위에서 제외** — "회의록에서 보기"가 이동할 전체 회의록 화면
([회의 관리 #2](#-회의-관리-archivetsx--신규-전체-회의록-화면))이 아직 없어서 링크를 만들어도 갈 곳이
없다. 그 화면이 생긴 뒤 별도로 진행한다.

| Phase | 항목 | 내용 | 공수 |
| --- | --- | --- | --- |
| **0. 결정** | #6 | 담당자 필드 — **본인 전용 유지로 결정**(아래 근거) → 02·09·15번 문서 정정 | 즉시 |
| **1. 즉시 가능** | #18 | 삭제 확인창에 Task 제목 포함 | 5분 |
| **2. 핵심** | #26 | 수정 폼 신설(제목·마감일·중요도·상태) | 프론트 반나절~1일 |
| **3. 필터** | #17 | 마감일 필터(백엔드 Query 파라미터 추가 + 프론트), 상태 필터를 서버사이드로 전환 | 백엔드 반나절 + 프론트 반나절 |

**#6 결정 근거**: 이 프로젝트 전체에 팀원 목록·초대·권한 관리 기능이 어디에도 없다 — 모든 API가
`_authenticated_user` 하나로만 범위를 잡고, `assignee_user_id`는 서버가 항상 로그인한 본인으로 강제
설정해왔다(코드 작성 시점부터 계속 이래왔음, 이번에 새로 바꾸는 게 아님). "담당자에게 배정" 기능은
Workmate MVP 어디에도 없는 개념을 이 화면에만 새로 만드는 것과 같다 — 02 §5.2·09 §2.1·§2.2가 요구하는
"담당자 필수 입력·필터"가 실제로는 애초부터 문서 쪽 오류였다고 판단한다. **따라서 코드는 그대로 두고
문서 3곳을 실제 구현에 맞게 정정한다**: 02 §5.2("assignee_user_id를 필수로 받고" 삭제), 09 §2.1·§2.2
(담당자 필터·필수 입력 필드 삭제), 15번 문서(같은 내용 반영). 이 결정에 따라 #17의 "담당자 필터"도
목표에서 빠진다 — 모든 Task가 이미 요청 사용자 범위로만 조회돼 항상 값이 하나뿐인 필터는 의미가 없다.
실사용에서 팀 배정이 실제로 필요해지면 그때 새 기능으로 다시 설계한다.

### #3. Task 상세 화면 / `meeting_evidence` 부재

**범위**: 백엔드 + 프론트

**현재 상태**: `Tasks.tsx`는 목록만 있고 상세 보기가 없다. `source_type=action_item` Task에서
`meeting_evidence`(evidence_text + 회의록 링크)를 보여주는 [15번 문서](15-workmate-ui-screens-reference.md#4-task-상세의-회의-근거--meeting_evidence-02-53)
(02 §5.3 기준) 스펙이 전혀 구현 안 됨. `lib/workmate-api.ts`의 `tasksApi`에는 `GET /api/v1/tasks/{id}`를
부르는 `get()` 메서드조차 없다 — 백엔드 Route는 있는데 프론트가 아예 호출하지 않는다.

**백엔드 작업**: `Task → ActionItem → Meeting` 조인해서 `meeting_evidence` 반환하는 로직이 현재
`GET /api/v1/tasks/{id}`에 없음(`TaskResponse`에 `meeting_evidence` 필드 자체가 없음). 조인 쿼리 추가 필요.

**프론트 작업**: `tasksApi.get()` 신규 추가, `Tasks.tsx`에 상세 보기(행 클릭 → 패널/모달) 신규 추가,
`source_type=action_item`일 때만 `meeting_evidence.evidence_text` + "회의록에서 보기" 링크. 09 §5.4가 이동
경로를 `/meetings/{meeting_id}?highlight_meeting_chunk_id={meeting_chunk_id}` URL 패턴으로 명확히
정의함 — [회의 관리 #2](#-회의-관리-archivetsx--신규-전체-회의록-화면)에서 만들 전체 회의록 화면과
연결됨.

**의존성**: [회의 관리 #2](#-회의-관리-archivetsx--신규-전체-회의록-화면) 완료 후 진행

**공수**: 백엔드 조인 로직 반나절, 프론트 반나절~1일

### #26. 등록된 Task를 수정하는 UI 자체가 없음 (신규 발견)

**범위**: 프론트엔드만(백엔드 `PATCH /api/v1/tasks/{id}`는 이미 `title`·`status`·`priority_hint`·`due_at`
전부 지원 — 막혀 있는 건 프론트뿐)

**현재 상태**: `Tasks.tsx`엔 등록 폼(`showForm`)만 있고 별도의 수정 폼이 없다. 목록 행의 동작 버튼은
"완료/되돌리기"(상태를 `done`↔`todo`로만 토글)와 "삭제" 둘뿐이다. 이 토글 외에는:
- **제목·마감일을 등록 후 절대 못 고친다** — 오타를 냈거나 마감이 바뀌어도 삭제 후 재등록해야 함
- **상태를 `in_progress`/`blocked`/`cancelled`로 바꿀 방법이 없다** — 목록 상단 필터 버튼엔 "진행 중"·
  "지연" 탭이 있지만, 정작 Task를 그 상태로 만들 수단이 없어 **이 두 필터는 항상 0건으로 죽어 있는 UI다**
  (Action Item·메일·Calendar 제안 승인으로 생성되는 Task도 전부 기본값 `todo`로만 만들어짐, `TaskCreateRequest.status`
  기본값 확인)
- **중요도(`priority_hint`) 입력 UI가 등록 폼에도 없다** — API는 받지만 화면에 입력창 자체가 없어 항상
  `null`로만 등록됨

15번 문서는 09 §2.2 "등록과 수정은 같은 폼을 사용한다"를 그대로 목표로 정의했는데, 실제 구현은 등록
폼만 있고 이 원칙이 전혀 지켜지지 않고 있다.

**작업**: 목록 행에 "수정" 버튼(또는 행 클릭) 추가 → 기존 등록 폼을 재사용해 `title`/`due_at`/
`priority_hint`/`status`(select: `todo`/`in_progress`/`blocked`/`done`/`cancelled`)를 채운 채 열고,
제출 시 `tasksApi.update()` 호출. 중요도 입력(숫자 0~10 또는 드롭다운)도 이 폼에 함께 추가. 담당자
필드는 [#6](#6-할-일-등록에-담당자-필드-없음--먼저-결정-필요) 결정에 따라 같이 넣을지 결정.

**공수**: 폼 재사용이라 프론트 반나절~1일

### #6. 할 일 등록에 담당자 필드 없음 — 먼저 결정 필요

**범위**: 결정에 따라 다름

**확인된 사실**: 백엔드 `TaskCreateRequest`(`app/task_api.py`)에는 애초에 `assignee_user_id` 입력 필드가
없다. 서버가 항상 `assignee_user_id=user_id`(로그인한 본인)로 강제 설정한다 — `TaskUpdateRequest`에도
없어 수정으로도 못 바꾼다. 즉 지금 API는 본인 앞으로만 등록 가능하고, `02-a2a-interface.md` §5.2
("assignee_user_id를 필수로 받고")·[15번 문서](15-workmate-ui-screens-reference.md#-할-일-관리-taskstsx)가
정의한 09 §2.2 목표(담당자 필수 입력)가 실제 구현과 다르다.

**결정 필요**:
- (A) 본인 전용이 맞는 설계이고 문서가 틀렸다 → **문서만 수정**, 코드 작업 없음
- (B) 팀원에게 할당하는 기능이 실제로 필요하다 → 백엔드 `TaskCreateRequest`/`TaskUpdateRequest`에 필드
  추가 + 팀원 목록/권한 검증 + [#26](#26-등록된-task를-수정하는-ui-자체가-없음-신규-발견)에서 만들 등록·
  수정 폼에 담당자 선택 UI 추가. 훨씬 큰 작업

**다음 액션**: 착수 전 제품 결정 확인

### #17. 할 일 필터에 담당자·마감일 필터 없음 (백엔드도 미지원으로 정정)

**범위**: 프론트엔드 + **백엔드**(재확인 결과 프론트만의 문제가 아니었음) — #6 결정에 종속

**현재 상태**: 09 §2.1(15번 문서에 그대로 반영)은 상태·담당자·마감일 3개를 최소 필터로 요구하지만
`Tasks.tsx`는 상태(전체/진행 중/지연, 그나마도 위 #26 문제로 진행 중·지연은 항상 0건) + 텍스트 검색만
있다. **다시 보니 이건 프론트만의 문제가 아니다** — 백엔드 `GET /api/v1/tasks`(`app/task_api.py`)도
`status`·`include_deleted` 두 Query 파라미터만 받고 `assignee_user_id`·`due_at` 범위 필터는 서버
자체에 없다. 게다가 `Tasks.tsx`는 있는 `status` Query 파라미터조차 안 쓰고 매번 전체 목록을 받아 클라
이언트에서만 걸러낸다.

**의존성**: 담당자 필터는 [#6](#6-할-일-등록에-담당자-필드-없음--먼저-결정-필요) 결정(담당자 지정 기능
자체를 만들지)에 종속됨. 마감일 필터는 독립적으로 먼저 진행 가능하나 **백엔드에 Query 파라미터 추가가
먼저 필요**.

**공수**: 마감일 필터만이면 백엔드 반나절 + 프론트 반나절

### #18. 삭제 확인창에 Task 제목 미포함

**범위**: 프론트엔드만, 사소함

**현재 상태**: 09 §2.3(15번 문서에 그대로 반영)은 "Task 제목이 포함된 확인창"을 요구하지만 실제 코드는
`window.confirm("이 Task를 삭제할까요?")`로 어떤 Task인지 특정하지 않는다. 재확인 결과 여전히 미수정
상태.

**작업**: `` window.confirm(`"${task.title}"을(를) 삭제할까요?`) ``로 변경

**공수**: 5분

---

## ✅ 할 일 관리(#6·#17·#18·#26) 구현완료보고서 (2026-08-15)

위 🗺️ 작업계획대로 4개 항목을 전부 처리했다. #3(Task 상세/`meeting_evidence`)은 계획대로 이번 범위에서
제외했다 — 의존 대상인 전체 회의록 화면이 아직 없다.

### #6. 담당자 필드 — 본인 전용으로 결정, 문서 3곳 정정 완료

코드는 원래부터 그랬던 대로(항상 `assignee_user_id=요청 사용자 본인`) 그대로 두고, 문서 쪽을 실제
구현에 맞게 고쳤다:
- `02-a2a-interface.md` §5.2: "assignee_user_id를 필수로 받고" 삭제, 근거를 설명하는 각주
  `[^task-assignee]` 추가
- `09-ui-design.md` §2.1·§2.2: 목록의 담당자 표시·필터, 등록 폼의 담당자 필수 입력을 모두 삭제하고
  정정 안내 박스 추가
- `15-workmate-ui-screens-reference.md`: 위 두 문서와 같은 내용으로 목표 기능·조회값 정의를 정정

이 결정에 따라 #17의 "담당자 필터"도 목표에서 제외했다 — 모든 Task가 이미 요청 사용자 범위로만
조회되는데 필터 값이 항상 하나뿐이면 필터 자체가 무의미하기 때문이다.

### #18. 삭제 확인창에 Task 제목 포함 — 완료

`Tasks.tsx`의 `removeTask()`가 이제 `Task` 객체를 통째로 받아 `` `"${task.title}"을(를) 삭제할까요?` ``
형태로 확인창을 띄운다.

### #26. Task 수정 폼 신설 — 완료

`Tasks.tsx`에 등록 폼과 같은 자리에서 재사용하는 수정 모드를 추가했다:
- 목록 각 행에 "수정" 버튼 신설 → 클릭하면 그 Task의 제목·마감일·중요도·상태를 채운 채 폼이 열림
- 폼은 `editingTaskId` 상태로 등록/수정 모드를 구분 — 등록 모드에선 기존과 동일하게 동작하고, 수정
  모드일 때만 상태(`todo`/`in_progress`/`blocked`/`done`/`cancelled`) 선택 `<select>`가 추가로 나타남
  (등록 시 상태는 항상 `todo`로 시작하는 09 §2.2 규칙 유지)
- 중요도(`priority_hint`, 0~10) 입력을 등록·수정 폼 모두에 추가 — 이전엔 API가 받는데도 입력 UI
  자체가 없어 항상 `null`로만 등록됐음
- 기존 "완료/되돌리기" 빠른 토글 버튼은 그대로 남겨 자주 쓰는 동작은 계속 한 번에 처리되게 함
- 백엔드 `PATCH /api/v1/tasks/{id}`는 이미 이 모든 필드를 지원하고 있어 프론트 변경만으로 충분했다
  (계획대로)

### #17. 마감일 필터 — 완료(백엔드+프론트), 담당자 필터는 #6 결정으로 범위 제외

- **백엔드**: `GET /api/v1/tasks`에 `due_before` Query 파라미터 신규 추가(`app/task_api.py`) — 마감일이
  있고 그 값이 `due_before` 이하인 Task만 반환. 기존 `status` 파라미터와 같은 방식(Repository가 전체를
  반환하면 Route 레이어에서 필터링)으로 구현해 SQLite·PostgreSQL Adapter를 건드리지 않았다.
- **프론트**: 목록 상단에 "마감일까지" 날짜 선택 필터 추가(`type="date"`, 선택한 날짜의 23:59:59까지
  포함). 기존 상태 필터 탭(전체/진행 중/지연)도 이번에 서버로 실제로 보내도록 고쳤다 — 이전엔 있는
  `status` Query 파라미터를 안 쓰고 매번 전체 목록을 받아 클라이언트에서만 걸렀었다. 텍스트 검색만
  그대로 클라이언트 필터로 남겼다(09 문서가 요구하는 필터가 아니라 편의 기능이라 서버 왕복 없이 즉시
  반응하는 게 나음).

### 검증

- **백엔드 회귀**: `uv run pytest tests/` — **212 passed, 10 skipped, 0 failed**(`due_before` 필터
  회귀 테스트 포함). ~~`test_task_repository.py::test_list_order_is_deterministic` 1건은 이번 작업과
  무관하게 간헐적으로 실패하는 기존 Flaky 테스트다~~ → 아래 후속 작업에서 원인을 찾아 함께 고쳤다.
- **프론트엔드**: `eslint` clean, `npm run build` 성공, `npm test`(28개) 전부 통과.
- 백엔드·프론트 서버 모두 최신 코드로 재시작 완료.

### 추가 UI 정리 — 버튼 정렬·열 너비·정렬 순서 (2026-08-15 후속 요청)

구현 완료 직후 실제 화면을 보고 사용자가 요청한 3가지 다듬기 작업이다.

1. **우측 동작 버튼 정렬**: "수정"/"완료"(또는 "되돌리기")/"삭제" 버튼이 좁은 열 폭 때문에 "수 정",
   "되돌리 기"처럼 버튼 안에서 줄바꿈되고 있었다. 각 버튼에 `whiteSpace: "nowrap"`을 추가하고 버튼 그룹을
   `justifyContent: "flex-end"`로 우측 정렬해 항상 한 줄로, 열 오른쪽 끝에 가지런히 나오게 했다.
2. **목록 정렬 순서를 등록일시 최신순으로 정정**: `SQLiteTaskRepository`·`PostgresTaskRepository`
   둘 다 `list()`가 `updated_at DESC`로 정렬하고 있었다 — "최근 수정한 것"과 "최근 등록한 것"은 다른
   개념인데 문서·사용자 기대는 후자였다. `ORDER BY created_at DESC, task_id ASC`로 변경. **이 과정에서
   기존 `test_list_order_is_deterministic`가 왜 간헐적으로 실패했는지 원인을 찾았다** — 연속 생성한 두
   Task의 `updated_at`(당시 정렬 기준)이 우연히 같을 때만 성립하는 `task_id` 오름차순 가정으로 작성돼
   있었다. `test_list_order_is_most_recently_created_first`로 이름과 내용을 바꿔 서로 다른 `created_at`을
   명시적으로 주입해 "최신 생성이 먼저 나온다"는 실제 요구사항을 검증하도록 고쳤다 — 5회 연속 재실행해
   더 이상 Flaky하지 않음을 확인했다.
3. **열 너비 조정**: `.table-row`의 `grid-template-columns`를 `2fr .8fr .8fr 1fr .7fr`에서
   `2.8fr .9fr .8fr .5fr 1.4fr`로 변경 — 할 일(제목) 열을 넓히고, 중요도 열을 좁히고(숫자 하나만
   표시하므로), 동작 버튼 열은 위 1번 때문에 넓혔다. 열 사이 간격이 전혀 없어 제목이 길면 마감 열과
   붙어 보이던 문제도 `column-gap:20px`을 추가해 해결했다(할 일↔마감 사이만 골라 넓힐 수는 없어 전체
   열 간격을 넓히는 방식을 택함).

**검증**: 백엔드 회귀 재확인 **212 passed, 10 skipped**(Flaky 테스트 포함 전부 안정적으로 통과, 5회
연속 재실행으로 별도 확인). 프론트 `eslint`·`npm run build`·`npm test`(28개) 전부 통과.

### 변경/신규 파일 목록

| 파일 | 종류 |
| --- | --- |
| `workmate-agent/app/task_api.py` | 수정 (`due_before` Query 파라미터 추가) |
| `workmate-agent/app/repositories/tasks.py` | 수정 (`list()` 정렬 기준을 `updated_at`→`created_at` DESC로 변경) |
| `workmate-agent/tests/test_task_api.py` | 수정 (`due_before` 필터 회귀 테스트 추가) |
| `workmate-agent/tests/test_task_repository.py` | 수정 (Flaky했던 정렬 테스트를 결정적 검증으로 재작성) |
| `workmate-ui/app/views/Tasks.tsx` | 수정 (수정 폼 신설, 중요도 입력 추가, 마감일 필터 추가, 상태 필터 서버 전송, 삭제 확인창 제목 포함, 동작 버튼 정렬) |
| `workmate-ui/lib/workmate-api.ts` | 수정 (`tasksApi.list()`에 `due_before` 파라미터 추가) |
| `workmate-ui/app/globals.css` | 수정 (`.table-row` 열 너비·간격 조정) |
| `docs/02-a2a-interface.md` | 수정 (§5.2 담당자 필수 입력 서술 삭제 + 각주 추가) |
| `docs/09-ui-design.md` | 수정 (§2.1·§2.2 담당자 필터·입력 삭제 + 정정 안내) |
| `docs/15-workmate-ui-screens-reference.md` | 수정 (담당자 필드 관련 목표 기능·조회값 정의 정정) |

---

## 🎙️ 회의 녹음 (`Meeting.tsx`)

[15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md)의 "🎙️ 회의 녹음" 절(04 §3의
1~6단계 — 회의 생성부터 LLM이 Action Item을 자동 추출하는 데까지)을 기준으로 재검토했다. 2026-08-15
백엔드 코드를 끝까지 추적한 결과, **녹음/업로드 → STT → 분석 파이프라인이 중간에 완전히 끊겨 있어 실제
사용자 경로로는 `analyze_meeting`까지 절대 도달할 수 없다**는 게 새로 확인됐다 — #7·#8·#12·#13·#14·#15는
"녹음 입력" 범위의 기존 항목이고, #20~#24가 이번에 새로 찾은 파이프라인 단절이다. 이 단절은
[📁 회의 관리](#-회의-관리-archivetsx-신규-전체-회의록-화면)가 다루는 Action Item 검토·Task 등록 단계도
함께 막는다 — 분석이 시작조차 안 되니 검토할 것 자체가 안 생긴다.

> ✅ **업데이트(2026-08-15)**: 아래 계획의 11개 항목을 모두 착수했다. 파이프라인 단절은 실제로 해소돼
> 녹음/업로드 → R2 저장 → STT → LLM 분석 → Embedding 저장까지 실 계정으로 end-to-end 확인했다. 실시간
> Partial 자막(OpenAI Realtime WebSocket 중계)도 추가로 구현·실 E2E 검증했다. 상세 결과는
> [✅ 회의 녹음 구현완료보고서](#-회의-녹음7·8·12·13·14·15·20·21·22·23·24-구현완료보고서-2026-08-15) 참고.

### 🗺️ 작업계획 (2026-08-15)

11개 항목(#7·#8·#12·#13·#14·#15·#20·#21·#22·#23·#24)을 의존관계 기준으로 5단계로 묶었다. **Phase 2·3이
핵심** — 이 둘을 끝내야 실제 녹음이 할 일까지 이어지는 원래 목적이 달성된다. 나머지는 병렬 진행 가능한
주변 작업이다.

| Phase | 항목 | 의존관계 | 공수 |
| --- | --- | --- | --- |
| **0. 결정** | #14 업로드 방식 확정, #24 분석 엔드포인트 신설 여부 | 착수 전 필수 | 각 30분 논의 |
| **1. 즉시 가능** (병렬) | #7 Idempotency-Key, #8 문서 정리 | 없음 | 합계 1일 이내 |
| **2. STT 선행 조건** | #13 오디오 포맷을 PCM16 24kHz 200ms로 수정 | 없음, **#21·#15보다 먼저** | 1일 |
| **2.5. #13 완료 후** | #15 일시정지 버튼 | **#13 완료 후** — MediaRecorder 기준으로 먼저 만들면 #13이 캡처 방식을 AudioWorklet으로 바꾸면서 재작업 필요. AudioWorklet 오디오 노드 그래프를 멈추는 방식으로 구현 | 반나절~1일 |
| **3. 핵심 파이프라인 복구** (순차) | #20 R2 저장 연동(**파일 업로드 + 실시간 녹음 Chunk 누적·병합 둘 다**) → #21 STT Provider 연동 → #22 검증(자동 해소) | #20은 #14 결정 후, #21은 #13·#20 완료 후 | #20 2~3일(실시간 Chunk 누적·병합 추가로 하루 늘어남) + #21 2~3일 |
| **4. 분석 후처리** | #23 meeting_chunks/embedding 저장, #12 RecordingSession.status 세분화 | #23은 #21 완료 후 검증 가능(코드 자체는 병행 가능) | #23 1일, #12 반나절(#5와 결합) |

**총 예상 공수**: 순차 의존이 있는 Phase 2·2.5·3만 최소 5~7일, 병렬 가능한 Phase 0·1·4를 겹쳐 진행하면
전체 **1.5~2주** 내외 (기존 추정과 큰 차이 없음 — #15 이동은 총량보다 순서 문제였음).

**세부 실행 메모**:

1. **Phase 0 (#14) 결정 기준**: 07번 문서의 Presigned 직접 업로드는 브라우저가 R2 자격 증명 없이 짧은
   시간만 유효한 URL로 직접 올리는 방식이라 서버 부하는 적지만 구현이 더 복잡함(Presigned URL 발급
   API·CORS 설정 추가 필요). 02번 문서의 multipart 경유는 지금 프론트가 이미 이 모양으로 파일을 보내고
   있어(`meetingsApi.uploadRecording`) **재작업이 가장 적다** — 서버가 받은 파일을 그대로 R2에
   PutObject하면 됨. **02번(multipart 유지) 방향을 권장**하며, 07번 문서 §13.1을 이에 맞게 고친다.

2. **Phase 3 (#20) 구현 위치 — 두 경로 다 필요**:
   - 공통: 새 R2 Provider Client를 `app/providers/r2.py`에 신설(기존 `app/providers/google.py`와 같은
     위치). S3 호환 REST API이므로 `boto3` 또는 경량 커스텀 클라이언트 중 선택. 환경변수는 이미 07번
     문서 §12에 정의됨(`R2_ENDPOINT`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`,
     `R2_REGION`).
   - **파일 업로드**: `upload_recording()`이 파일을 받은 뒤 Object
     Key(`users/{user_id}/meetings/{meeting_id}/source/{file_id}.{ext}`)로 PutObject하고 그 Key를
     `Meeting.source_audio_uri`에 저장하도록 수정.
   - **실시간 녹음 (별도 작업, 계획에 처음엔 빠져 있었음)**: 지금 `recording_stream.py`는 수신한 오디오
     바이트(`raw = base64.b64decode(...)`)를 SHA256 해시만 계산하고 **그 자리에서 버린다** — Chunk를
     누적하는 버퍼도, 세션 종료 시 병합·저장하는 로직도 전혀 없다. 세션 동안 받은 Chunk 원본을
     메모리(또는 임시 파일)에 누적해두고, `WebSocketDisconnect` 시점에 하나의 음성 파일로 병합해 같은
     R2 Provider Client로 업로드하는 로직을 추가해야 한다(07 §13.1: "Chunk마다 개별 객체로 저장하지
     않고 세션 종료 후 하나의 음성 파일로 병합해 업로드"). 이게 없으면 #21(STT)을 다 구현해도 실시간
     녹음에는 최종 STT를 돌릴 원본 음성이 애초에 존재하지 않는다.
   - **주의 — WAV 헤더 필요**: #13 이후 브라우저가 보내는 건 raw PCM16 샘플이라(컨테이너·헤더 없음),
     Chunk를 단순히 이어붙이기만 하면 재생·STT 둘 다 못 하는 깨진 파일이 된다. 병합 시 mono·24kHz·16bit
     **WAV 헤더를 씌워서** 저장해야 한다.

3. **Phase 3 (#21) 구현 위치**: 새 STT Provider Client를 `app/stt.py`에 신설 — `app/embeddings.py`의
   `OpenAICompatibleEmbeddingClient` 패턴(이미 검증된 OpenAI 호환 클라이언트 구조)을 그대로 따르면 된다.
   환경변수도 이미 정의됨(`STT_BASE_URL`, `STT_API_KEY`, `STT_MODEL=gpt-4o-transcribe`). 두 개의 별도
   경로가 필요: (a) `recording_stream.py`의 WebSocket 핸들러가 실시간 Partial 자막용으로 호출(위 Chunk
   누적과 별개로, 들어오는 Chunk를 스트리밍으로 STT에 흘려보내기만 하면 됨 — 자막용은 누적 버퍼 필요
   없음), (b) 원본 음성이 R2에 확정된 뒤(파일 업로드든 실시간 병합 후든) 파일 기반 최종 STT. **(b)는
   `analyze_meeting`이 항상 사용자가 "분석 실행" 버튼을 눌러야 도는 구조**이므로, 별도 자동 트리거를
   새로 만들 필요 없이 `build_analyze_meeting_workflow` 진입 시 첫 단계로 "최종 Transcript가 없으면
   R2에서 원본 음성을 가져와 STT부터 수행" 로직을 추가하면 기존 버튼 클릭에 자연스럽게 맞물린다.
   **주의**: STT Provider(OpenAI 호환 API)는 URL이 아니라 실제 파일 바이트를 받아야 하므로, "R2에서
   가져와"는 정확히는 R2 `GetObject`로 바이트를 먼저 내려받은 뒤 STT Provider에 파일로 전달하는
   절차다 — Presigned URL을 STT Provider에 그대로 넘기는 방식은 안 된다.

4. **Phase 4 (#23) 구현 위치**: `app/workflows/meetings.py`의 `build_analyze_meeting_workflow` 안,
   Action Item 추출 이후에 Chunking(문단/주제 단위) + `EmbeddingProvider.embed()`(이미 있음) +
   `MeetingChunkRepository.create()`(이미 있음, 호출부만 없음) 호출 추가.

### #20. 녹음 파일이 실제로 저장되지 않음 (R2 미연동)

**범위**: 백엔드. 심각도 높음 — 아래 #21·#22 문제의 절반을 차지한다.

**현재 상태**: `app/meeting_api.py`의 `upload_recording()`은 함수 Docstring부터 "MIME·크기·checksum을
검증하고 **원본 없이 업로드 메타데이터만 저장**한다"고 명시한다. 실제로 파일명·MIME·크기·checksum만
DB(`RecordingRecord`)에 저장하고 **음성 바이트 자체는 어디에도 저장하지 않는다**. `app/` 전체를
`r2|boto3|s3|presign`으로 검색해도 0건 — R2 업로드 호출이 코드베이스 어디에도 없다. 15번 문서가 정의한
목표(07 §13.1: R2에 원본 저장, `Meeting.source_audio_uri`에 Object Key 확정)와 정면으로 다르다.

**작업**: R2 Provider Client 신규 구현 + 업로드 흐름에 실제 저장 로직 연결, `object_key`를 실제 R2 경로로
채우기. 문서 간 불일치(#14)에서 어느 업로드 방식을 택할지부터 먼저 결정해야 함.

**공수**: 백엔드 1~2일 (R2 자격증명·버킷 설정 별도 필요)

### #21. 실시간 녹음이 최종 Transcript를 절대 만들지 못함 (STT 완전 미연결)

**범위**: 백엔드. 심각도 높음.

**현재 상태**: `app/recording_stream.py`는 수신하는 모든 Chunk에 대해 무조건
`repository.save_transcript(meeting_id, user_id, chunk_no, "", False)`를 호출한다 — 텍스트는 항상 빈
문자열, `is_final`은 항상 `False`. 저장소 계층(`save_transcript`)은 `is_final=True` 저장을 지원하지만,
**실제 애플리케이션 코드 전체에서 이 값을 `True`로 호출하는 곳이 테스트 코드 말고 단 한 군데도 없다**
(`grep`으로 전수 확인). 즉 실시간 녹음이든 파일 업로드든, 실제 사용자 경로로는 "최종 확정된 Transcript"가
생기는 경로 자체가 없다.

**작업**: 실제 STT Provider(`gpt-4o-transcribe`) 연동 — 실시간 Partial 자막과 녹음 종료 후 파일 기반
최종 STT 둘 다 필요 (04 §3, 07 §9.3). #13(오디오 포맷 불일치)이 이 작업의 선행 조건이다.

**공수**: 대형 — STT Provider Client 신규 구현, WebSocket 자막 배선, 파일 기반 최종 STT 배선까지
포함하면 2~3일

### #22. `analyze_meeting`이 실제 사용자 경로로는 절대 성공할 수 없음

**범위**: #20·#21의 직접적 결과. 별도 코드 작업 없음 — 원인이 해소되면 자동으로 풀림.

**현재 상태**: `app/workflows/meetings.py`의 `build_analyze_meeting_workflow`는 `is_final=True`인
Transcript가 하나도 없으면 `ValueError("final transcript is required")`를 던진다. #20·#21 때문에 지금은
실제로 녹음하거나 파일을 올려서 이 조건을 만족시킬 방법이 없다. `tests/test_meeting_workflows.py`가
API를 거치지 않고 `repository.save_transcript(..., True, ...)`로 **DB에 직접 주입**해서만 이 이후
단계(LLM 분석, evidence 추출)를 검증해왔다 — 그 부분 자체는 로직이 맞고 테스트도 통과하지만, 실사용자가
도달해본 적은 없다.

**작업 없음** — 이 항목은 "지금 전체 파이프라인이 처음부터 끊겨 있다"를 명시적으로 기록해두기 위한
표시용 항목이다. #20·#21이 끝나면 저절로 해소된다.

### #23. `meeting_chunks`/embedding 저장이 `analyze_meeting`에 없음

**범위**: 백엔드

**현재 상태**: 15번 문서 목표 6단계("회의록을 문단/주제 단위로 나눠 `meeting_chunks`에 embedding과 함께
저장")가 `build_analyze_meeting_workflow`에 전혀 구현돼 있지 않다. `search_meetings`
Workflow(`build_search_meetings_workflow`)는 `meeting_chunks`를 **읽기만** 하고 쓰지 않는다.
`MeetingChunkRepository.create()`는 존재하지만 실제 앱 코드에서 호출하는 곳이 없다(테스트만 직접 호출).
즉 분석이 끝나도 이후 회의록 검색(`search_meetings`)이 찾을 데이터가 애초에 안 만들어진다.

**작업**: `analyze_meeting` Workflow에 문단/주제 단위 Chunking + Embedding 생성 + `meeting_chunks` 저장
단계 추가.

**공수**: 백엔드 1일 (Chunking 전략을 새로 설계해야 하면 더 걸릴 수 있음)

### #24. `POST /api/v1/meetings/{id}/analysis` 분석 시작 엔드포인트 부재 (내부 스킬챗으로 우회 중)

**범위**: 문서 정합성 확인 우선, 코드 변경은 결정 이후

**현재 상태**: `02-a2a-interface.md` §5.2가 정의하는 분석 시작 전용 엔드포인트가 코드에 없다
(`meeting_api.py`·`main.py` 검색 0건). 대신 `Archive.tsx`가 `/api/v1/internal/skill-chat/messages`
(`useSkillRunner("analyze_meeting")`)로 우회 호출한다 — 같은 공용 Workflow를 호출하므로 **기능적으로는
동작**하지만, 문서가 정의한 전용 REST 경로와는 다른 길이다. 결과 **조회** 엔드포인트(`GET .../analysis`)
부재는 [📁 회의 관리 #25](#25-get-apiv1meetingsidanalysis-분석-결과-조회-엔드포인트-부재)에서 별도로 다룬다
— 15번 문서가 분석 시작(회의 녹음 화면 책임)과 결과 조회(회의 관리 화면 책임)를 서로 다른 화면으로
나눴기 때문이다.

**작업**: 전용 엔드포인트를 새로 만들지, 문서를 실제 구현(내부 스킬챗 경유)에 맞게 고칠지 결정 필요 —
#14와 같은 성격의 문서-구현 불일치.

**공수**: 결정 필요, 코드로 만들기로 하면 반나절

### #7. 회의 생성에 Idempotency-Key 누락

**범위**: 프론트엔드 (백엔드 지원 여부 확인 필요)

**현재 상태**: `lib/workmate-api.ts`의 `meetingsApi.create()`가 `Idempotency-Key` 헤더를 보내지 않음.
`02-a2a-interface.md` §6.5는 회의 생성에 `Idempotency-Key` Header로 중복 생성을 막아야 한다고 명시.

**작업**:
1. `meetingsApi.create()`가 매 호출마다 `Idempotency-Key`를 생성해 헤더로 전송 (`proposalsApi.reviewEmail/reviewCalendar`의 `${id}-${decision}-${Date.now()}` 패턴 재사용 가능)
2. **선행 확인 필요**: `workmate-agent`의 회의 생성 라우트(`meeting_api.py`)가 이 헤더를 실제로 검사/멱등 처리하는지 확인. 서버가 무시하면 헤더만 보내는 건 의미 없으므로 백엔드 작업으로 승격

**공수**: 프론트만이면 1시간 이내, 백엔드까지면 반나절

### #8. recording-sessions REST 엔드포인트 미사용

**범위**: 코드 작업 아님 — 문서만 수정

**결론**: WebSocket(`app/recording_stream.py`)이 연결 시점에 세션을 열고 `save_session()`으로 저장하며,
연결 종료가 곧 세션 종료로 처리된다. 문서가 말하는 별도 REST `recording-sessions`/`:complete` 엔드포인트는
실질적으로 불필요 — 이미 WebSocket 하나로 같은 일을 하고 있다.

**작업**: `02-a2a-interface.md` §5.2 표에서 해당 두 줄을 제거하거나 "WebSocket 연결/종료로 대체 구현됨"
각주 추가.

**예외**: "녹음 중간에 끊겼다가 이어서 재개" 같은 요구사항이 생기면 그때는 명시적 세션 재개 REST가 실제로
필요해짐 — 지금 범위에서는 불필요.

**공수**: 30분

### #12. `RecordingSession.status` 세분화 미표시

**범위**: 프론트엔드만

**현재 상태**: [03-data-priority-rules.md](03-data-priority-rules.md) §1.1은 `RecordingSession.status`를
`recording`/`processing`/`completed`/`failed` 4단계로 정의하지만, `Meeting.tsx`는 `recording: boolean`
하나로만 상태를 다룬다. 녹음 종료 후 "processing"(최종 STT 대기 중) 상태를 사용자에게 보여줄 방법이 없다.

**공수**: [공통/전역 #5](#-공통전역-여러-화면이-공유하는-hook·api-클라이언트)(Task Polling)와 함께 처리하면
자연스럽게 붙는 작업 — 별도로는 반나절

### #13. 실시간 녹음 오디오 포맷이 STT Provider 계약과 안 맞음

**범위**: 프론트엔드 (#21 STT 연동의 선행 조건)

**중요도가 높은 발견이다.** `07-technical-specification.md` §9.3은 Realtime STT 입력을 다음으로 고정한다.

> Realtime 입력: mono PCM16, 24kHz, 기본 200ms Chunk

그런데 실제 `Meeting.tsx`는 `new MediaRecorder(stream)`(mimeType 미지정 → 브라우저 기본값, 보통
`audio/webm;codecs=opus`)로 녹음해 **2000ms(2초)** 간격으로 Blob을 만들고, 이를 base64로 인코딩해 그대로
WebSocket에 보낸다. 즉 코덱(Opus 압축 vs 비압축 PCM16), 샘플레이트, Chunk 길이가 전부 문서 계약과 다르다.

지금은 STT Provider가 아예 연결돼 있지 않아(#21) 이 불일치가 겉으로 드러나지 않는다. STT Provider를
실제로 연결하면 지금 방식대로 보낸 Opus 압축 Blob은 Provider가 기대하는 raw PCM16 스트림이 아니므로
그대로는 동작하지 않을 가능성이 높다 — #21 작업에 들어가기 전에 반드시 같이 해결해야 한다.

**작업**: STT Provider 연결 작업에 들어가기 전에 다음 중 하나를 결정해야 함
1. 브라우저에서 `AudioWorklet`/`ScriptProcessor`로 PCM16 24kHz 200ms Chunk를 직접 만들어 전송하도록
   `Meeting.tsx` 녹음 캡처 로직을 다시 작성 (문서 계약을 따르는 방향)
2. 백엔드가 Opus/WebM Blob을 받아 서버에서 PCM16으로 변환 후 STT Provider에 전달 (문서 갱신 필요, 서버
   부하 증가)

**공수**: 방향 결정 후 프론트 1일 내외 (옵션 1 기준) — #21과 통합 진행 권장

### #14. 회의 파일 업로드 방식이 문서끼리 서로 다름

**범위**: 코드 작업 아님(방식 결정) — 단 #20과 묶어서 실제 구현 필요

**현재 상태**: 2개 문서가 서로 다른 방식을 말하고, 실제 구현은 **둘 다 완전히는 아니다**.

| 출처 | 방식 |
| --- | --- |
| `07-technical-specification.md` §13.1 | 브라우저가 Workmate가 발급한 단기 Presigned URL로 **R2에 직접 업로드** |
| `02-a2a-interface.md` §5.2 | 브라우저가 **`multipart/form-data`로 백엔드에 직접 업로드**, 백엔드가 R2 저장을 대행 |

실제 구현(`meetingsApi.uploadRecording` + `upload_recording()`)은 02번 방식(multipart)으로 파일을
**받기는** 하지만, 받은 뒤 R2에 저장하는 절차가 없다(#20) — 이전 판단("기능은 동작")은 R2 저장 여부를
확인하지 않고 내린 **잘못된 결론이었다.** 지금은 업로드된 음성 바이트가 그냥 유실된다.

**작업**: #20과 함께 R2 저장을 실제로 붙이면서, 그 김에 02번 방식(multipart 유지)과 07번 방식(Presigned
직접 업로드로 전환) 중 하나로 확정하고 나머지 문서를 갱신 — R2 자격 증명 노출 범위가 달라지는 보안 관련
결정이라 신중히 판단.

**공수**: #20 작업에 포함, 별도 문서 정리는 30분

### #15. 실시간 녹음에 "일시정지" 버튼 없음

**범위**: 프론트엔드 (+ 백엔드가 일시정지를 실제로 지원하는지 확인)

**현재 상태**: [09-ui-design.md](09-ui-design.md) §5.1은 "시작·일시정지·종료 버튼"을 요구하지만
`Meeting.tsx`는 "녹음 시작"/"녹음 종료" 두 버튼만 있다.

**공수**: MediaRecorder의 `pause()`/`resume()`으로 프론트만으로 구현 가능해 보이나, 일시정지 중 서버 쪽
`RecordingSession` 상태 처리가 필요한지 확인 필요. 반나절~1일

---

## ✅ 회의 녹음(#7·#8·#12·#13·#14·#15·#20·#21·#22·#23·#24) 구현완료보고서 (2026-08-15)

[🗺️ 작업계획](#-작업계획-2026-08-15)의 11개 항목을 전부 착수했다. Phase 2·3(핵심 파이프라인)과 Phase 4(#23)는
**실제 R2·OpenAI STT·OpenAI Embedding·PostgreSQL/pgvector 계정으로 진짜 네트워크 호출까지 실행해 확인**했다
— DB에 값만 직접 주입해 통과하는 Mock 검증이 아니라, 회의 생성 → 실시간/파일 녹음 → R2 저장 → STT →
LLM 분석 → Embedding → 검색까지 실제 파이프라인이 사용자가 밟는 경로 그대로 끝까지 이어지는지 각
Phase마다 별도 검증 스크립트로 직접 실행해 확인했다. 유일하게 계획과 다르게 처리한 항목은 #21의 **실시간
Partial 자막**(아래 참고) — 의도적으로 범위를 좁혔다.

### Phase 1 — #7, #8: 즉시 가능 항목

**#7 회의 생성 Idempotency-Key**: 계획에 적은 `Idempotency-Key` Header 방식 대신, 이미 코드에 있던 더
단순한 메커니즘으로 해결했다 — `Meeting.tsx`가 `crypto.randomUUID()`로 `meeting_id`를 미리 만들어
`POST /api/v1/meetings` 요청에 실어 보내고(`meetingsApi.create()`), 서버는 `INSERT OR IGNORE`로 같은
`meeting_id` 재시도를 멱등 처리한다. Meeting은 PK 자체가 자연스러운 멱등 Key라 별도 Header 계층은 만들지
않았다. **다만 이 방식은 문서가 원래 약속한 "동일 Key·다른 Payload → `409 Conflict`" 계약까지는 만족하지
않는다** — 같은 `meeting_id`에 다른 제목이 들어와도 최초 값을 그대로 유지할 뿐 오류를 반환하지 않는다.
`02-a2a-interface.md` §6.5를 실제 구현에 맞게 정정하고 이 제약을 각주로 명시했다. 실사용에서 문제가 되면
그때 Header 계층을 추가한다.

**#8 recording-sessions REST 엔드포인트 미사용**: 문서만 정리하는 항목으로, 앞선 세션에서 이미
`02-a2a-interface.md`에서 별도 REST 표 행을 제거하고 WebSocket 연결/종료가 세션 시작/종료를 대체한다는
각주를 추가해 완료돼 있었다.

### Phase 2·2.5 — #13, #15: STT 선행 조건

**#13 실시간 녹음 오디오 포맷**: `Meeting.tsx`의 오디오 캡처를 `MediaRecorder`(Opus, 2초 Blob)에서
`AudioContext` + `ScriptProcessorNode` 기반으로 다시 작성해 07번 문서 §9.3의 mono PCM16·24kHz·200ms
Chunk 계약을 맞췄다. 리샘플링·PCM16 변환·200ms 단위 자르기·WAV 헤더 생성은 `lib/audio-pcm16.ts`의 순수
함수로 분리해 Node 테스트 10개로 검증했다.

**#15 일시정지 버튼**: 계획대로 #13 완료 후 착수 — `AudioContext.suspend()`/`resume()`으로 오디오 그래프
전체(ScriptProcessorNode 콜백 포함)를 멈추는 방식으로 구현했다. WebSocket·세션은 그대로 유지한 채 Chunk
생성만 멈춘다.

### Phase 3 — #20, #21, #22: 핵심 파이프라인 복구

**#14 업로드 방식 결정**: 계획대로 02번 문서(multipart 경유) 방향으로 확정하고 07번 문서 §13.1의
Presigned 직접 업로드 서술을 실제 구현에 맞게 정정했다.

**#20 R2 저장 연동 — 완료, 두 경로 모두 실제 R2로 검증**:
- 기존 `app/storage/r2.py`(`R2StorageAdapter`)를 사용하려다 **실제 버그를 발견했다** —
  `R2Config.from_env()`가 환경변수 이름(`R2_ENDPOINT`)을 그대로 Dataclass 생성자 키워드 인자로 넘겨
  `TypeError`가 나는 상태였다. 기존 테스트는 "설정 없음" 실패 경로만 확인했지 성공 경로를 확인한 적이
  없어 발견되지 못했던 버그다. 환경변수명→필드명 매핑을 명시적으로 고치고 회귀 테스트를 추가했다.
- `put_object`/`get_object` 메서드를 추가하고, **파일 업로드**(`upload_recording()`)와 **실시간 녹음**
  (`recording_stream.py`) 두 경로 모두에 실제로 연결했다.
- 실시간 녹음 경로는 계획에서 새로 찾은 대로 원래 Chunk를 해시만 계산하고 버리고 있었다 — 세션 동안 받은
  원본 PCM16을 임시 파일에 누적하고, `WebSocketDisconnect` 또는 정상 종료 시 WAV 헤더를 씌워 병합한 뒤
  R2에 업로드하고 `Meeting.source_audio_uri`를 확정하는 로직을 추가했다.
- **실 E2E 검증**: `r2-storage-test/.env`의 실제 R2 자격증명으로 PUT/HEAD/GET/DELETE 전부 확인. 실제
  WebSocket 라운드트립으로 실시간 녹음 → R2 업로드까지도 별도로 확인.

**#21 STT Provider 연동 — 파일 기반 최종 STT, 실시간 Partial 자막 모두 완료**:
- `app/stt.py`에 `OpenAICompatibleSttClient` 신규 구현 — `app/embeddings.py`의 기존 OpenAI 호환 Client
  패턴을 따라 `urllib.request`로 `multipart/form-data`를 직접 구성한다(새 SDK 의존성 추가 없음).
- `stt-evaluation/.env`의 실제 자격증명으로 실제 회의 음성 파일을 STT에 보내 정확한 한국어 Transcript를
  받는 것까지 확인했다.
- `build_analyze_meeting_workflow`(`app/workflows/meetings.py`)에 자동 트리거를 배선했다 — 최종
  Transcript가 없을 때, 회의에 `source_audio_uri`가 있으면 R2에서 원본 음성을 `GetObject`로 내려받아
  STT부터 자동 수행하고 결과를 `is_final=True`로 저장한 뒤 이어서 분석한다. 계획대로 사용자가 이미 누르는
  "분석 실행" 버튼 클릭에 자연스럽게 맞물려, 별도 자동 트리거를 새로 만들 필요가 없었다.
- **실시간 Partial 자막(OpenAI Realtime WebSocket) 스트리밍도 이후 별도 요청으로 추가 구현했다**(원래
  1차 계획에서는 파일 기반 최종 STT를 먼저 완성하는 쪽을 택하고 이 부분만 남겨뒀었다). `app/stt.py`에
  `RealtimeSttSession`을 신규 구현해 `stt-evaluation/run_streaming_eval.py`가 검증해둔 프로토콜
  (`session.update` → `input_audio_buffer.append`(base64 PCM16) → `*.delta`/`conversation.item
  .input_audio_transcription.completed` 이벤트 수신)을 그대로 따른다. **실 계정으로 직접 확인한 결과
  Provider가 자체 Turn 검출(서버 VAD)로 문장이 끝날 때마다 자동으로 `completed`를 보내, 처음 우려했던
  주기적 수동 `commit`이 필요 없었다** — 애초에 설계를 단순하게 만든 근거다. `recording_stream.py`는
  브라우저→서버 WebSocket 메인 루프와, 서버→OpenAI 이벤트를 받아 그대로 중계하는 별도 백그라운드
  `asyncio.Task`를 `asyncio.Lock`으로 직렬화된 같은 소켓에 함께 돌린다 — 우려했던 "두 WebSocket을 동시에
  비동기로 중계"가 실제로는 Provider 연결 실패를 조용히 자막 없음으로 흡수하는 방어 코드(R2 미설정 시
  조용히 넘어가는 기존 #20 방침과 동일)만 있으면 충분히 안전하게 구현 가능했다. `Meeting.tsx`는
  `chunk_no`(자막 한 줄 번호, 오디오 Chunk 번호와 무관)가 같은 자막을 새로 추가하지 않고 갱신하도록
  고쳐 Delta가 쌓일수록 중복 행이 늘어나던 문제도 같이 잡았다. 이 결과는 순수 화면 표시용이라 어디에도
  최종 Transcript로 저장하지 않는다(07 §9.3) — 근거로 쓰는 최종 Transcript는 여전히 녹음 종료 후 확정된
  원본 음성으로 다시 수행하는 파일 기반 STT뿐이다.

**#22 analyze_meeting 실사용 불가 — 표시용 항목이었지만 실제로 직접 검증까지 수행**:
계획은 "#20·#21이 끝나면 자동 해소, 별도 작업 없음"이라고 적었지만, 표시만으로 남기지 않고 **실제로
확인했다**. 검증 스크립트로 (1) 실제 회의 음성 파일을 실 R2에 업로드 → (2) `source_audio_uri`만 설정한
상태에서 `build_analyze_meeting_workflow`를 그대로 실행 → (3) 워크플로우가 R2에서 음성을 내려받아 실 STT
호출 → (4) 실 LLM으로 요약·Action Item 추출까지 **한 번의 호출로 전부 이어지는 것을 직접 확인**했다.
사람이 만든 회의(스프린트 진행 상황 공유)에서 "QA 빌드 확인 결과 공유"라는 Action Item이 정확한 근거
문장과 함께 추출됐다.

### Phase 4 — #23, #12: 분석 후처리

**#23 meeting_chunks/embedding 저장 — 완료, 실 Postgres/pgvector로 검증**:
- `build_analyze_meeting_workflow`에 최종 Transcript를 검색용 Chunk로 나누는 단계를 추가했다. 발화
  단위로 저장된 Row가 여럿이면 그 Row(이미 `start_ms`/`end_ms` 근거가 있음)를 그대로 Chunk로 쓰고, 지금
  처럼 파일 기반 STT가 회의 전체를 Row 하나로 합쳐 반환하면 문장 경계로 400자 단위로 나눈다(이 경우
  문장 단위 timestamp는 복원할 수 없어 `None`으로 남김).
  각 Chunk를 `EmbeddingProvider.embed()`로 Embedding하고 `MeetingChunkRepository.create()`로 저장한다.
- **`search_meetings`은 별도 Skill이라 이 색인이 실패해도 이미 계산된 요약·Action Item은 그대로 반환**
  하도록 설계했다 — Postgres·Embedding Provider가 없는 환경(지금 로컬 개발 환경의 기본 상태)에서도
  핵심 분석 흐름을 막지 않기 위해서다. 실패하면 `warnings`에 재시도 가능한 경고(`MEETING_CHUNK_INDEXING_
  UNAVAILABLE`)만 덧붙인다.
- **실 E2E 검증**: 로컬에 `pgvector/pgvector:pg16` Docker 컨테이너를 띄우고 Migration을 그대로 적용한 뒤,
  실 R2 음성 → 실 STT → 실 LLM 분석 → 실 Embedding → 실 Postgres 저장까지 실행하고, 이어서
  `search_meetings` Workflow로 실제로 그 회의를 검색해 방금 저장한 Chunk가 근거로 돌아오는 것까지
  확인했다(`insufficient_evidence=False`, 인용문이 실제 회의 내용과 일치). 기존
  `test_hybrid_search_postgres_integration.py`(`WORKMATE_TEST_DATABASE_URL` 설정 시 실행)도 같은
  컨테이너로 통과 확인. 검증 후 컨테이너는 정리했다.

**#12 RecordingSession.status 세분화 — 계획보다 가볍게, 프론트엔드만으로 완료**:
계획은 "#5(Task Polling)와 묶으면 자연스럽게 붙는 작업"이라고 적었지만, #5 없이도 정확히 표시할 수 있는
신호가 이미 있었다 — 서버(`recording_stream.py`)는 세션 종료 시 누적 PCM16을 WAV로 병합해 R2에 업로드하고
`source_audio_uri`를 확정한 **뒤에야** WebSocket 핸들러가 반환돼 Close Handshake가 끝난다. 즉 사용자가
"녹음 종료"를 누른 시점과 브라우저의 `close` 이벤트가 실제로 도착하는 시점 사이가 정확히
`processing`(최종 원본 저장 대기 중) 구간이다. `Meeting.tsx`에 이 구간을 위한 상태를 추가해 "처리 중" UI로
표시하고, 그 사이 재녹음 버튼도 비활성화했다. 별도 Task Polling·백엔드 변경 없이 프론트엔드만으로 문서가
요구하는 4단계 중 `processing`을 정확히 보여준다.

### #24 (참고 — 이번 Phase 이전에 이미 결정 완료)

계획에서는 Phase 0(착수 전 결정)에 포함했지만, 실제로는 이번 구현 착수 이전 세션에서 이미 "전용 엔드포인트를
새로 만들지 않고 기존 내부 스킬챗 경로(`analyze_meeting`)를 유지, 문서만 실제 구현에 맞게 정정"으로 결정하고
`02-a2a-interface.md`에 각주로 반영해뒀다. 이번 Phase에서 별도로 다시 할 작업은 없었다.

### 검증 요약

- **백엔드 회귀**: `uv run pytest tests/` — 최종 **211 passed, 10 skipped, 0 failed**(아래 CORS·Subprotocol·
  실시간 자막·Action Item PK 관련 회귀 테스트 포함, 10개 skip은 전부 `WORKMATE_TEST_DATABASE_URL` 등
  선택적 실 인프라 환경변수가 없을 때의 기존 skip이며 이번 세션에 새로 생긴 실패는 없음).
- **프론트엔드**: `npx tsc --noEmit`(해당 파일 기준)·`eslint app/views/Meeting.tsx` clean, `npm test`
  (build + 28개 Node 테스트) 전부 통과.
- **실 네트워크 E2E** (Mock이 아닌 진짜 계정으로 실행, 확인 후 생성한 자원은 정리함):
  - R2: PUT/HEAD/GET/DELETE, 실시간 녹음 WebSocket 라운드트립 → R2 업로드
  - STT: 실제 회의 음성 파일 → 정확한 한국어 Transcript
  - 파이프라인 전체: 실 R2 업로드 → `analyze_meeting` 실행(STT 자동 트리거 → LLM 분석) → 정확한 요약·
    Action Item 추출
  - Embedding + Postgres/pgvector: 실 Docker pgvector 컨테이너 → 실 Embedding → 저장 → `search_meetings`로
    실제 검색·근거 인용 확인

### ⚠️ 실사용 중 추가로 발견·수정한 버그: `Failed to fetch`(CORS 없는 500)

위 실 E2E 검증은 `build_analyze_meeting_workflow`를 Python에서 직접 호출해 확인한 것이라, 실제 사용자가
타는 HTTP 경로(`POST /api/v1/internal/skill-chat/messages`)는 거치지 않았다. 구현 완료 후 실제로
`workmate-ui`에서 회의 분석을 눌러보니 화면에 `예상치 못한 오류: Failed to fetch`만 뜨고 실제 원인이 전혀
보이지 않는 문제가 발견됐다.

**원인**: `app/workflows/*.py`는 잘못된 입력·상태(예: `analyze_meeting`의 "final transcript is required")를
관례적으로 `ValueError`로 표시한다(15곳). 그런데 `app/internal_chat.py`의 `validate_message()`는 이
예외를 잡지 않았다 — `verify_a2a_headers` 미들웨어가 `CORSMiddleware` 바깥에 있는 구조라, 잡히지 않은
예외는 Starlette의 최상위 `ServerErrorMiddleware`까지 그대로 올라가 **CORS 헤더가 없는 500**을 반환한다.
브라우저는 CORS 헤더 없는 응답을 읽을 수 없어 실제 오류 메시지(`final transcript is required` 등) 대신
`TypeError: Failed to fetch`만 던진다 — 5개 Skill 전부가 걸리는 문제였고, 녹음 없이 분석을 누르는 것 같은
정상적인 사용자 실수 시나리오에서 특히 자주 재현된다.

**수정**: `validate_message()`에서 `workflow_registry().execute(...)` 호출을 `try/except ValueError`로
감싸 `HTTPException(422, detail=str(exc))`로 변환 — 정상적인 CORS 응답 경로를 타게 된다.
`tests/test_internal_chat.py`에 회귀 테스트 추가(Mock으로 `ValueError` 발생시켜 `422` + CORS 헤더 확인).
백엔드 회귀 **202 passed, 10 skipped**로 갱신.

### ⚠️ 실사용 중 추가로 발견·수정한 버그: 실시간 녹음 `WebSocket 연결 오류`

위 버그를 고친 뒤에도 "회의 녹음" 화면에서 실시간 녹음을 시작하면 곧바로 "WebSocket 연결 오류가
발생했습니다"가 떴다. 서버 로그(`.err.log`)에 원인이 그대로 남아 있었다:

```
WARNING:  Unsupported upgrade request.
WARNING:  No supported WebSocket library detected. Please use "pip install 'uvicorn[standard]'",
          or install 'websockets' or 'wsproto' manually.
```

**원인**: `pyproject.toml`이 `uvicorn==0.35.0`을 `[standard]` extra 없이 선언하고 있었고, `websockets`·
`wsproto` 둘 다 프로젝트 의존성에 없었다. Uvicorn은 WebSocket Upgrade 요청을 처리할 실제 Protocol
구현체가 없으면 무조건 `404 Not Found`로 떨어뜨린다 — `app/recording_stream.py`의 인증·세션 로직 자체는
전혀 실행되지 않고, ASGI 서버 레벨에서 막혀 있었다. `tests/test_recording_stream.py`가 계속 통과했던
이유는 `TestClient`의 WebSocket 테스트 Helper가 실제 네트워크·Uvicorn Protocol 계층을 거치지 않고
인프로세스로 직접 ASGI를 호출하기 때문 — 이 계층의 결함을 테스트로는 잡을 수 없었다.

**수정**: `uv add websockets`로 `websockets>=17.0.1`을 명시적 의존성으로 추가(`pyproject.toml`).
"직접 import하는 패키지만 의존성으로 선언한다"는 기존 방침(07 §2.2)의 예외다 — `app/` 코드가 이
패키지를 직접 import하지는 않지만, Uvicorn이 WebSocket을 처리하는 데 필수인 런타임 요구사항이라
없으면 실시간 녹음 기능 자체가 ASGI 서버 단계에서 항상 실패한다. 백엔드 회귀 재확인(202 passed,
10 skipped, 변화 없음), 실제 기동 후 `websockets` 라이브러리로 직접 Upgrade 요청을 보내 uvicorn이
더 이상 위 경고 없이 정상적으로 WebSocket Protocol을 처리하는 것(`recording_stream.py`의 인증 로직까지
도달해 정상적으로 거부하는 것)을 확인했다.

### ⚠️ 실사용 중 추가로 발견·수정한 버그: Subprotocol Handshake가 실제 브라우저에서 실패

위 두 버그를 고친 뒤에도 실시간 녹음이 여전히 "WebSocket 연결 오류"로 실패했다. 이번엔 서버 로그가
`"WebSocket .../recording-stream" [accepted]` → `connection open` → `connection closed`로, 겉보기엔
**정상 성공**처럼 보였다 — 그런데 Chunk ACK 등 어떤 메시지 교환도 없이 곧바로 닫혔다.

**원인**: `recording_stream.py`의 `_credentials()`는 브라우저가 `Sec-WebSocket-Protocol`로 보낸
`bearer.<token>`/`user.<user_id>` 값을 읽어 인증하면서도, `websocket.accept()`를 Subprotocol 인자 없이
호출해 그중 어떤 것도 응답에서 선택(echo)하지 않았다. 기존 코드 주석은 "WS 표준상 Subprotocol을
선택하지 않아도 Handshake는 성공한다"고 판단했는데, 이는 RFC 6455 자체로는 맞지만 **실제 브라우저
(Chrome 등)는 클라이언트가 Subprotocol을 제시했는데 서버가 그중 하나를 선택하지 않으면 Handshake
자체를 실패로 처리한다**(WHATWG WebSocket 표준의 더 엄격한 규칙). 서버 쪽에서는 TCP/HTTP Upgrade가
끝까지 성공한 것으로 보이지만, 브라우저는 이 시점에 연결을 그대로 끊고 `error`/`close` 이벤트만
던진다 — 원인을 전혀 알 수 없는 "WebSocket 연결 오류가 발생했습니다"로만 보이는 이유다. 기존
`tests/test_recording_stream.py`는 Starlette `TestClient`로, 위에서 직접 검증에 썼던 순수 Python
`websockets` Client 둘 다 이 브라우저 전용 규칙을 강제하지 않아 실제 브라우저로 테스트하기 전까지는
드러나지 않았다.

**수정**: `_credentials()`가 인증에 쓴 Subprotocol 중 하나(`offered[0]`)를 함께 반환하도록 고치고,
`websocket.accept(subprotocol=...)`에 그대로 전달해 Handshake 응답에 echo되게 했다. 값 자체는 의미가
없고(자격 증명은 이미 파싱 완료) 협상 규칙만 만족시키면 된다. 헤더 인증 경로(Subprotocol 자체를 안 씀)는
`subprotocol=None`으로 기존과 동일하게 유지된다. `tests/test_recording_stream.py`에 두 회귀 테스트 추가
— 브라우저 경로는 `ws.accepted_subprotocol`이 제시한 값 중 하나인지, 헤더 경로는 여전히 `None`인지
확인. 백엔드 회귀 **203 passed, 10 skipped**로 갱신. 실제 기동 후 순수 Python `websockets` Client로
브라우저와 동일한 Subprotocol 목록을 제시해 서버가 그중 하나를 실제로 선택해 돌려주는 것, 그 뒤 정상적으로
Chunk ACK를 주고받는 것까지 확인했다.

### ✅ 추가 구현: #21 실시간 Partial 자막 Streaming (2026-08-15, 후속 요청)

위 세 버그를 고쳐 실시간 녹음 자체는 정상 동작하는 상태에서, 사용자가 실시간 자막 기능을 요청해 당초
의도적으로 미루기로 했던 부분을 마저 구현했다.

**구현**: `app/stt.py`에 `RealtimeSttSession` 신규 — `stt-evaluation/run_streaming_eval.py`가 실 계정으로
이미 검증해둔 프로토콜(`session.update`로 Transcription 세션 열기 → `input_audio_buffer.append`로
브라우저가 보낸 PCM16 Chunk를 재인코딩 없이 그대로 전달 → `*.delta`/`conversation.item.input_audio
_transcription.completed` 이벤트 수신)을 그대로 따른다. `recording_stream.py`는 WebSocket 접속 시
`RealtimeSttSession`을 열고(실패하면 조용히 자막 없음으로 진행 — R2 미설정 시와 같은 방침), 브라우저
Chunk 수신 메인 루프와 별도로 Provider 이벤트를 받아 그대로 중계하는 `asyncio.Task`를 하나 더 돌린다.
두 흐름이 같은 WebSocket에 동시에 쓰지 않도록 `asyncio.Lock`으로 직렬화했다. 실시간 결과는 화면 표시
전용이라 최종 Transcript로는 저장하지 않는다(07 §9.3) — 근거로 쓰는 최종 Transcript는 여전히 녹음
종료 후 확정된 원본 음성으로 다시 수행하는 파일 기반 STT뿐이다.

**설계가 단순해진 이유**: 원래 우려는 "두 WebSocket을 동시에 비동기로 중계하고 오류·종료 전파까지
검증"하는 작업이 컸다는 점이었다. 실제로 구현하며 실 계정으로 확인해보니 (1) OpenAI가 자체 Turn
검출(서버 VAD)로 문장이 끝날 때마다 자동으로 `completed`를 보내 주기적인 수동 `commit`이 필요 없었고,
(2) Provider 연결 실패는 자막 기능만 끄면 되고 녹음·저장 경로와는 원래도 독립적이라 별도의 정교한 오류
전파 설계가 필요 없었다 — 기존에 이미 확립된 "Provider 미가용 시 조용히 진행" 방침을 그대로 재사용하는
것으로 충분했다.

**프론트엔드에서 추가로 발견한 버그**: 서버가 보내는 `chunk_no`는 원래 오디오 Chunk 번호였는데, 실시간
자막에서는 "자막 한 줄" 번호(문장이 끝나기 전까지 여러 Delta가 같은 번호로 옴)로 의미가 바뀌었다.
`Meeting.tsx`가 이 값을 그대로 React 목록 Key로 쓰면서 매번 새 줄을 추가하고 있었는데, 이러면 한 줄이
길어질 때마다("오", "오늘", "오늘 스", ...) 중복 행이 쌓이는 UI 버그가 생긴다. 같은 `chunk_no`는 새로
추가하지 않고 갱신하도록 고쳤다.

**검증**: `tests/fixtures/fake_realtime_stt.py` 신규(Provider Double), `tests/test_stt.py`에
`RealtimeSttSession` 단위 테스트 5개(세션 생성 메시지 모양, 오디오 전송, 이벤트 파싱, 종료 — 전부
`websockets.connect` Mock, 실 네트워크 없음), `tests/test_recording_stream.py`에 자막 중계·Provider
연결 실패 시 자막만 없이 녹음은 정상 진행하는지 회귀 테스트 2개 추가. **실 E2E**: (1) `RealtimeSttSession`
단독으로 실제 회의 음성 파일을 실 OpenAI Realtime API에 스트리밍해 Delta·Final 이벤트가 정확한 한국어로
오는 것 확인, (2) 브라우저와 완전히 같은 방식(Subprotocol 인증, PCM16 24kHz 200ms Chunk)으로 실제
서버의 `/recording-stream` 전체 경로에 접속해 145개 Chunk를 보내며 87개의 실시간 자막 메시지가 정확한
누적 문장으로 돌아오는 것과 Chunk ACK가 전부 정상 처리되는 것(자막 기능이 기존 버퍼링·R2 저장 경로를
방해하지 않음)을 함께 확인 — 이 과정에서 실제로 R2에 업로드된 테스트 음성 객체는 확인 후 삭제했다.
백엔드 회귀 최종 **210 passed, 10 skipped**.

### ⚠️ 실사용 중 추가로 발견·수정한 버그: 같은 회의를 반복 분석하면 다른 회의의 Action Item과 충돌

실시간 자막까지 붙인 뒤 실제로 "회의 분석 실행"을 여러 번 눌러보다가, 어떤 회의에서는 매번
`예상치 못한 오류: Failed to fetch`가 났다(§ 위 CORS 버그는 이미 고친 뒤라 이번엔 다른 원인). 서버
로그에 이번엔 진짜 처리되지 않은 예외가 남아 있었다:

```
File "app/repositories/meetings.py", line 165, in upsert_action
    assert row is not None
AssertionError
```

**원인**: `action_item_id`는 서버가 만드는 값이 아니라 **LLM이 구조화 출력에서 스스로 매기는 값**이다
(`app/meeting_analysis.py`의 응답 Schema 필드). 시스템 프롬프트 어디에도 이 값을 전역에서 유일하게
만들라는 지시가 없고 `temperature=0`으로 고정돼 있어서, 비슷한 내용의 회의록을 반복 분석하면 서로
**다른 회의인데도 같은 `action_item_id`**(`"action-1"` 류)를 매기기 쉽다. 그런데
`action_items` 테이블은 `action_item_id` 한 컬럼만 `PRIMARY KEY`였다 — 다른 회의의 같은 ID로
`INSERT OR IGNORE`를 하면 조용히 무시되고, 뒤이어 `(action_item_id, meeting_id, user_id)`로 다시
조회하면 아무 것도 안 나와 `assert row is not None`이 깨졌다. 이 예외도 `app/internal_chat.py`가
잡는 대상은 `ValueError`뿐이라 그대로 CORS 없는 500으로 새 나가 다시 "Failed to fetch"로 보였다.

**수정**: `action_items`의 Primary Key를 `(action_item_id, meeting_id)` 복합 키로 바꿨다 —
`approve_action`/`upsert_action`을 포함해 이 테이블을 쓰는 모든 코드가 이미 항상
`action_item_id`와 `meeting_id`를 함께 조건으로 쓰고 있어(전수 확인) 다른 코드 변경 없이 안전했다.
기존 DB 파일은 SQLite가 `ALTER TABLE`로 Primary Key를 못 바꿔서, `_initialize()`가 예전 단일 컬럼
PK를 감지하면 테이블을 새 스키마로 다시 만들어 데이터를 그대로 옮기는 1회성 마이그레이션을 추가했다
(로컬 개발 DB라 데이터 유실 위험 낮음, 실제로 기존 행 4개 보존 확인). `tests/test_action_item_api.py`에
회귀 테스트 추가 — 같은 `action_item_id`를 서로 다른 두 회의에 승인해도 서로 다른 Task로 독립적으로
처리되는지 확인. 백엔드 회귀 **211 passed, 10 skipped**.

### 아직 안 된 것

- #5(장기 Task Polling), #6/#17(할 일 담당자·필터 결정 대기), #2/#3/#4/#11(회의 관리·할 일 관리 화면 갭)은
  이번 11개 항목 범위 밖으로 착수하지 않았다.
- **Phase 5. LLM 엔지니어링(계획, 미착수)** — 파이프라인이 전부 실제로 이어지는 지금이 회의 분석
  프롬프트를 다듬을 수 있는 시점이다(그 전에는 `analyze_meeting`에 실 데이터가 도달한 적이 없어 튜닝할
  근거 자체가 없었다). "지금 정확히 뭘 시키고 있는지"는 [16-llm-prompts.md](16-llm-prompts.md)에 원문이
  있고, 실제로 프롬프트를 바꾸는 절차·평가 기준·변경 이력 기록 방식은
  [11-llm-evaluation-plan.md](11-llm-evaluation-plan.md) §9("평가 및 수정 이력", `Prompt` 변경 유형)를
  따른다 — 새 평가 실행 없이 프롬프트만 바꾸는 것은 금지(§7 모델 선정과 교체 규칙과 같은 원칙). 이번
  세션 범위 밖으로 남겨둔다.

### 변경/신규 파일 목록

| 파일 | 종류 |
| --- | --- |
| `workmate-agent/app/storage/r2.py` | 수정 (`from_env` 버그 수정, `put_object`/`get_object` 추가) |
| `workmate-agent/app/audio.py` | 신규 (`wrap_pcm16_as_wav`) |
| `workmate-agent/app/stt.py` | 신규 (`OpenAICompatibleSttClient`, `RealtimeSttSession`) |
| `workmate-agent/app/domain/meeting.py` | 수정 (`source_audio_uri` 필드) |
| `workmate-agent/app/repositories/meetings.py` | 수정 (`source_audio_uri` 컬럼, `set_source_audio_uri`, `action_items` 복합 PK 마이그레이션) |
| `workmate-agent/app/meeting_api.py` | 수정 (`r2_storage()`, `upload_recording()` R2 연동) |
| `workmate-agent/app/recording_stream.py` | 수정 (Chunk 버퍼링, 세션 종료 시 WAV 병합·R2 업로드, Subprotocol echo로 브라우저 Handshake 수정, 실시간 자막 중계) |
| `workmate-agent/tests/fixtures/fake_realtime_stt.py` | 신규 |
| `workmate-agent/app/workflows/meetings.py` | 수정 (STT 자동 트리거, `meeting_chunks` 색인) |
| `workmate-agent/.env` | 수정 (R2·STT·Embedding·LLM 자격증명 추가, gitignored) |
| `workmate-agent/tests/fixtures/fake_r2.py` | 신규 |
| `workmate-agent/tests/test_r2_storage.py` | 수정 |
| `workmate-agent/tests/test_audio.py` | 신규 |
| `workmate-agent/tests/test_stt.py` | 신규 |
| `workmate-agent/tests/test_meeting_api.py` | 수정 |
| `workmate-agent/tests/test_action_item_api.py` | 수정 (Action Item PK 충돌 회귀 테스트 추가) |
| `workmate-agent/tests/test_recording_stream.py` | 수정 |
| `workmate-agent/tests/test_meeting_workflows.py` | 수정 |
| `workmate-agent/app/internal_chat.py` | 수정 (Workflow `ValueError` → 422 CORS 응답 변환) |
| `workmate-agent/pyproject.toml`, `uv.lock` | 수정 (`websockets>=17.0.1` 의존성 추가 — 실시간 녹음 WebSocket이 Uvicorn에서 완전히 동작 불가였던 문제 수정) |
| `workmate-agent/tests/test_internal_chat.py` | 수정 (CORS/422 회귀 테스트 추가) |
| `workmate-ui/lib/workmate-api.ts` | 수정 (`meetingsApi.create()`에 `meeting_id` 추가) |
| `workmate-ui/lib/audio-pcm16.ts` | 신규 |
| `workmate-ui/tests/audio-pcm16.test.mts` | 신규 |
| `workmate-ui/package.json` | 수정 (`test` 스크립트) |
| `workmate-ui/app/views/Meeting.tsx` | 수정 (PCM16 캡처, 일시정지, 처리 중 상태, 실시간 자막 렌더링 중복 방지) |
| `docs/02-a2a-interface.md` | 수정 (#7 Idempotency 계약 정정, 각주 추가) |

---

## 📁 회의 관리 (`Archive.tsx` + 신규 전체 회의록 화면)

[15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md)의 "📁 회의 관리" 절(04 §3의
7~8단계 — 분석 결과 표시 → Action Item 검토 → Task 등록)을 기준으로 한다.

> ✅ **업데이트(2026-08-15)**: 아래 경고는 작성 당시(STT 완전 미연결) 기준이었다. [🎙️ 회의 녹음 #21·#22](#-회의-녹음-meetingtsx)가
> 해소돼 `analyze_meeting`이 실제 사용자 경로로 완료되고 검토할 분석 결과가 정상적으로 생긴다 —
> 상세는 [✅ 회의 녹음 구현완료보고서](#-회의-녹음7·8·12·13·14·15·20·21·22·23·24-구현완료보고서-2026-08-15) 참고.
> 아래 #25·#2·#4·#11 항목 자체는 여전히 미해결이다(이번 11개 항목 범위 밖).

아래 항목들은 그 전제(분석이 정상적으로 끝난다면)하에서의 갭이며, 이제 실제로 그 전제가 성립한다.

### #25. `GET /api/v1/meetings/{id}/analysis` 분석 결과 조회 엔드포인트 부재

**범위**: 백엔드. [🎙️ 회의 녹음 #24](#-회의-녹음-meetingtsx)의 짝(분석 시작 vs 결과 조회)이다.

**현재 상태**: `02-a2a-interface.md` §5.2가 정의하는 분석 결과 조회 전용 엔드포인트가 없다
(`meeting_api.py`·`main.py` 검색 0건). `Archive.tsx`는 `useSkillRunner("analyze_meeting")`가 반환하는
동기 응답을 그대로 화면에 쓴다 — 별도로 "다시 조회"할 방법이 없다는 뜻이라, 페이지를 새로고침하면
방금 본 분석 결과(요약·Action Item 목록)를 다시 볼 수 없다.

**작업**: 전용 조회 엔드포인트 신설 여부를 #24와 함께 결정. 신설한다면 `meeting_id`로 마지막 분석 결과를
다시 가져올 수 있어야 함(현재는 결과가 어디에도 영속 저장되지 않는 것으로 보임 — 이 부분도 확인 필요).

**공수**: 결정 필요, 코드로 만들기로 하면 반나절~1일(결과 영속 저장까지 포함 시)

### #2. 전체 회의록 화면 부재

**범위**: 백엔드 일부 + 프론트 신규

**현재 상태**: `GET /api/v1/meetings/{id}/transcript`는 이미 있고 동작함(`app/transcript_api.py`). 단,
`workmate-ui`에서 `meetingsApi.transcript()`가 정의만 되어 있고 어디서도 호출되지 않아 화면 자체가
없다. [04-scenarios.md](04-scenarios.md) 시나리오 3: "근거 문장을 누르면 전체 회의록 화면으로 이동해
`evidence_span.meeting_chunk_ids`에 해당하는 라인을 강조."

[09-ui-design.md](09-ui-design.md) §5.3이 요구사항을 더 구체화한다: 회의록 **내 검색** 기능,
`/meetings/{meeting_id}?highlight_meeting_chunk_id={id}` URL 패턴으로 진입, "할 일로 돌아가기" 버튼.

**백엔드 갭**: 문서가 요구하는 Cursor Pagination과 `around_meeting_chunk_id` 파라미터가 백엔드에도 없음
(현재는 전체를 flat list로 반환). 회의가 길어지면 문제되므로 백엔드 작업 목록에 포함.

**프론트 작업**:
1. 신규 화면/컴포넌트 (예: `app/views/Transcript.tsx`) — `meetingsApi.transcript()`는 이미 있으므로 바로 호출 가능
2. Chunk 목록 렌더링, 특정 `meeting_chunk_id`로 스크롤 + 하이라이트
3. 회의록 내 검색 기능
4. 위 URL 패턴(`?highlight_meeting_chunk_id=`)으로 진입 처리, "할 일로 돌아가기" 버튼

**의존성**: [할 일 관리 #3](#-할-일-관리-taskstsx)의 "회의록에서 보기" 링크가 이 화면을 필요로 함 → #2를
먼저 완료

**공수**: 백엔드 Pagination 포함 1~2일, 프론트만이면 반나절~1일

### #4. Action Item 편집/거절 불가

**범위**: 백엔드 + 프론트

**현재 상태**: 백엔드도 승인 단일 처리만 지원한다 (`app/action_item_api.py`의
`POST /{meeting_id}/actions/{action_item_id}/approve` 하나뿐). `02-a2a-interface.md` §5.3이 정의하는
배치 엔드포인트 `POST /api/v1/meetings/{id}/actions:review`(`decisions[]` 배열, `approve`/`edit`/`reject`)는
프론트·백엔드 모두 없음. 프론트 `Archive.tsx`는 승인 버튼만 있고 거절·수정 UI가 없음.

**백엔드 작업**:
1. `POST /api/v1/meetings/{id}/actions:review` 신설, `decisions[]` 배열로 `approve`/`edit`/`reject` 한 번에 처리
2. `edit`일 때만 `changes`(assignee_user_id, due_at 등) 반영
3. 기존 단일 `.../approve` 라우트를 유지하며 내부적으로 재사용할지, 완전히 교체할지 결정 (프론트가 이미
   쓰고 있어 하위호환 고려)
4. `reject` 시 Task 미생성, `approval_status=rejected` 기록

**프론트 작업**: `Archive.tsx`의 `MeetingDetail`에 Action Item별 "거절" 버튼, "수정"(담당자/마감일 인라인
편집) 추가, 배치 승인(여러 개 체크 후 한 번에)도 고려.

**공수**: 백엔드 1일, 프론트 반나절~1일

### #11. 회의 참석자(`MeetingParticipant`) 미표시

**범위**: 프론트엔드 + 백엔드 확인 필요

**현재 상태**: [03-data-priority-rules.md](03-data-priority-rules.md) §1에 `MeetingParticipant` 엔터티가
정의돼 있고, [09-ui-design.md](09-ui-design.md) §5.2 회의 목록 요구사항도 "제목, 일시, **참석자**, 분석
상태와 요약 일부"라고 명시한다. 실제 `Archive.tsx`(회의 관리 화면)는 참석자를 전혀 표시하지 않고,
`Meeting` 타입(`lib/workmate-types.ts`)에도 참석자 필드가 없다.

**선행 확인 필요**: 회의 생성 시 참여자를 등록하는 UI/API 자체가 있는지 (`meetingsApi.create()`는 `title`,
`started_at`만 받음 — 참여자 입력 경로가 아예 없음). 없다면 참여자 관리 자체가 새 기능.

**공수**: 참여자 등록 API가 이미 있으면 반나절, 없으면 백엔드 포함 1일 이상

---

## 🔍 회의록 검색 (`Search.tsx`)

[15-workmate-ui-screens-reference.md의 🔍 회의록 검색](15-workmate-ui-screens-reference.md#-회의록-검색-searchtsx)
(2026-08-15 신규 작성)을 기준으로 `Search.tsx`·`lib/workmate-format.ts`·`app/workflows/meetings.py`를
다시 대조했다. 기존엔 "이 화면 고유의 갭은 없음"이라고 적혀 있었는데, 15번 문서가 훨씬 구체적으로
정의되면서 실제로는 갭이 여러 개 있는 게 확인됐다. [공통/전역 #5 Task Polling](#-공통전역-여러-화면이-공유하는-hook·api-클라이언트)도
여전히 이 화면에 적용된다.

### 🗺️ 작업계획 (2026-08-15)

| Phase | 항목 | 내용 | 처리 |
| --- | --- | --- | --- |
| **0. 결정** | #30 | 전용 REST 엔드포인트 신설 여부 — **스킬챗 경로 유지로 결정**(#24·#25와 같은 판단) | 즉시(문서만) |
| **1. 핵심 구현** | #27 | 날짜(`date_from`/`date_to`)·회의 선택(`meeting_ids`) 필터 UI 추가 | 이번에 구현 |
| **2. 범위 제외** | #28·#29·#31 | 아래 사유로 이번 작업에서 제외 | 결정/표시만 |

**#27이 유일하게 코드로 구현 가능한 항목이다.** 백엔드 `build_search_meetings_workflow`가 이미
`filters.date_from`/`date_to`/`meeting_ids`를 전부 지원하고 있는데(실 검증 완료 기능, #23 완료보고서
참고) `Search.tsx`엔 자유 질문 입력창 하나뿐이라 이 필터들을 쓸 방법이 없었다 — 백엔드는 준비됐는데
프론트만 안 만든, 가장 명확하고 저위험한 항목이라 이번에 바로 구현한다.

### #27. 검색 필터 UI 부재(날짜·회의 선택) — 백엔드는 이미 지원

**범위**: 프론트엔드만

**현재 상태**: `lib/workmate-format.ts`의 `searchMeetingsInput(query, limit)`은 `query`·`limit`만
보내고 `filters`를 아예 만들지 않는다. `Search.tsx`도 자유 질문 입력창 하나뿐이라 날짜·회의를 좁혀
검색할 방법이 없다. 반면 백엔드 `build_search_meetings_workflow`(`app/workflows/meetings.py`)는
`filters.date_from`/`date_to`(지역 날짜 → UTC 경계 변환)와 `filters.meeting_ids`(특정 회의로 범위
제한, 여러 회의 조회 후 병합)를 이미 완전히 구현·검증해뒀다(2026-08-15, #23 완료보고서의 실 E2E
검증이 이 경로를 그대로 통과함).

**작업**: `searchMeetingsInput()`에 `filters` 선택 인자 추가, `Search.tsx`에 날짜 범위 입력 2개(`date_from`/
`date_to`)와 회의 선택 `<select>`(`meetingsApi.list()`로 채움, 기본값 "전체 회의") 추가.

**공수**: 프론트 반나절

### #28. 참여자(`participants`) 검색 필터 미지원 — `MeetingParticipant` 모델 자체가 없어 결정 대기

**범위**: 결정 필요(구현하려면 백엔드 새 모델부터 필요)

**확인된 사실**: `build_search_meetings_workflow`는 `filters.participants`가 오면
`raise ValueError("participant filtering is not supported by the current meeting schema")`로
아예 거부한다. 코드베이스 전체에 `MeetingParticipant` 도메인·Repository·Migration이 **하나도 없다** —
03번 문서가 정의한 엔터티가 처음부터 구현되지 않은 상태다. 이건 [회의 관리 #11 회의 참석자
미표시](#-회의-관리-archivetsx-신규-전체-회의록-화면)와 **같은 원인**(MeetingParticipant 부재)이다.

**다음 액션**: #11을 먼저 구현할지 결정 → 구현하면 이 필터도 자연스럽게 붙일 수 있음. 이번 작업
범위에서는 제외.

### #29. Reranker 미구현 — 07번 문서가 이미 M4.4로 미뤄둔 항목, 표시용

**범위**: 없음(표시용) — 코드 작업 아님

**현재 상태**: 07-technical-specification.md §8.2.1은 "Top-1/Top-2 점수 차이가 작거나 다중 Chunk·
Metadata 질문이면 조건부 Reranker를 호출한다"고 정의하지만, "이 정책의 실제 구현과 Contract Test는
M4.4에서 수행한다"고 **07번 문서 스스로 명시**해뒀다. 코드베이스에 Reranker 관련 코드가 없는 건
맞지만, 이건 이번에 새로 찾은 갭이 아니라 애초에 계획된 대로 아직 안 온 마일스톤일 뿐이다.

**다음 액션**: 없음. M4.4 착수 시점에 다시 참고.

### #31. 검색 결과 출처 카드 클릭 → 전체 회의록 이동 불가

**범위**: 프론트엔드(의존성 있음)

**현재 상태**: 15번 문서는 출처 카드를 누르면 `highlight_meeting_chunk_id`로 전체 회의록의 근거
Chunk가 강조되는 것을 목표로 정의하지만, `Search.tsx`의 citation 카드는 클릭 동작이 전혀 없고(단순
`<div>`), 애초에 이동할 `/meetings/{meeting_id}` 전체 회의록 화면 자체가 없다.

**의존성**: [회의 관리 #2 전체 회의록 화면](#-회의-관리-archivetsx-신규-전체-회의록-화면) 완료 후 진행 —
[할 일 관리 #3](#3-task-상세-화면--meeting_evidence-부재)과 정확히 같은 의존 관계다.

**공수**: 전체 회의록 화면이 생긴 뒤 프론트 1시간 이내(단순 링크 추가)

### #30. 전용 REST 엔드포인트(`POST /api/v1/meetings/search`) 미사용 — 결정 완료

**범위**: 문서 정정만

**현재 상태**: 02-a2a-interface.md §5.2는 `POST /api/v1/meetings/search`를 정의하지만 실제 구현은
`Search.tsx`가 `useSkillRunner("search_meetings")`로 `/api/v1/internal/skill-chat/messages`를 호출한다
— [#24(분석 시작)](#24-post-apiv1meetingsidanalysis-분석-시작-엔드포인트-부재-내부-스킬챗으로-우회-중)·
[#25(분석 조회)](#-회의-관리-archivetsx-신규-전체-회의록-화면)와 완전히 같은 모양의 우회다.

**결정**: 같은 근거로 **전용 엔드포인트를 새로 만들지 않고 스킬챗 경로를 유지**한다 — 같은 공용
Workflow를 호출해 기능적으로 동일하고, 회의 화면 전용 UX가 더 필요해지기 전까지는 REST 경로를
분리할 이유가 없다. 02번 문서에 `[^analysis-route]`와 같은 방식의 각주를 추가해 실제 구현을 반영한다.

**공수**: 문서 정정 30분

---

## ✅ 회의록 검색(#27·#30) 구현완료보고서 (2026-08-15)

작업계획대로 진행했다. #28(participants 필터)·#29(Reranker)·#31(근거 카드 클릭 이동)은 계획대로 이번
범위에서 제외했다 — 각각 #11(MeetingParticipant 모델 부재), 07번 문서가 이미 M4.4로 미룬 항목, 회의
관리 #2(전체 회의록 화면 부재)에 막혀 있다.

### #30. 전용 REST 엔드포인트 — 스킬챗 경로 유지로 결정, 문서 정정 완료

`02-a2a-interface.md` §5.2의 `POST /api/v1/meetings/search` 행에 `[^search-route]` 각주를 추가해 실제
구현(`/api/v1/internal/skill-chat/messages` 경유)과 그 이유를 `[^analysis-route]`와 같은 방식으로
기록했다.

### #27. 검색 필터 UI — 완료

- `lib/workmate-format.ts`의 `searchMeetingsInput(query, limit, filters?)`에 세 번째 선택 인자를
  추가했다. 빈 문자열·빈 배열은 걸러내고 실제로 값이 있는 필드만 `filters`에 담아 보낸다(빈
  `filters: {}` 자체를 아예 안 보냄).
- `Search.tsx`에 시작일·종료일(`<input type="date">` 2개)과 회의 선택(`<select>`, `meetingsApi.list()`로
  채움, 기본값 "전체 회의") 필터를 추가하고 "필터 초기화" 버튼을 붙였다. 회의 목록을 못 불러와도(예:
  네트워크 실패) 검색 기능 자체는 막지 않고 "전체 회의"로만 조용히 좁아진다.
- 백엔드는 이미 이 필터들을 지원하고 있어(오늘 #23 완료보고서의 실 E2E 검증이 이 경로를 그대로
  통과함) 프론트 변경만으로 충분했다 — 계획대로 별도 백엔드 작업이 필요 없었다.

### 검증

- **프론트엔드**: `eslint` clean, `npm run build` 성공, `npm test` — **29 passed**(신규 필터 테스트
  2개 포함).
- **백엔드**: 이번 항목은 코드 변경이 없어 회귀만 재확인 — `uv run pytest tests/` **212 passed, 10
  skipped**(변화 없음).
- 두 서버 모두 최신 코드로 재시작 완료.

### 변경/신규 파일 목록

| 파일 | 종류 |
| --- | --- |
| `workmate-ui/lib/workmate-format.ts` | 수정 (`searchMeetingsInput()`에 `filters` 인자 추가) |
| `workmate-ui/tests/workmate-format.test.mts` | 수정 (필터 조립 회귀 테스트 추가) |
| `workmate-ui/app/views/Search.tsx` | 수정 (날짜·회의 선택 필터 UI 추가) |
| `docs/02-a2a-interface.md` | 수정 (`POST /api/v1/meetings/search`에 `[^search-route]` 각주 추가) |
| `workmate-agent/app/internal_chat.py` | 수정 (Workflow `RuntimeError` → 503 CORS 응답 변환) |
| `workmate-agent/tests/test_internal_chat.py` | 수정 (`RuntimeError`/503 회귀 테스트 추가) |
| `workmate-agent/migrations/002_work_domain.sql` | 수정 (`user_id` 계열 컬럼 `uuid → text`) |
| `workmate-agent/migrations/003_priority_snapshots.sql` | 수정 (`recipient_user_id` `uuid → text`) |
| `workmate-agent/migrations/004_search_data.sql` | 수정 (`meetings.user_id`·`meeting_chunks.user_id` `uuid → text`) |
| `workmate-agent/tests/test_work_domain_migration.py` | 수정 (기존 계약 테스트 2개를 `text`로 갱신, `user_id`가 `uuid`가 아니어야 하는 이유를 명시하는 회귀 테스트 추가) |
| `workmate-agent/app/domain/meeting_chunk.py` | 수정 (`MeetingChunkRecord`에 `meeting_title`·`meeting_started_at`·`meeting_ended_at` 필드 추가) |
| `workmate-agent/app/repositories/meeting_chunks.py` | 수정 (`PostgresMeetingChunkRepository.create()`가 실제 회의 메타데이터로 `meetings` 행을 `ON CONFLICT DO UPDATE`로 자체 치유하며 저장) |
| `workmate-agent/app/workflows/meetings.py` | 수정 (`_index_meeting_chunks()`가 실제 `meeting.title`/`started_at`(없으면 `created_at`)/`ended_at`을 Chunk에 배선) |
| `workmate-agent/tests/test_meeting_workflows.py` | 수정 (Chunk 저장 호출 인자를 가로채는 Spy로 메타데이터 배선 회귀 테스트 추가) |
| `workmate-agent/tests/test_meeting_chunk_postgres_integration.py` | 수정 (실제 Postgres에 제목·시각이 쓰이고 이전 자리표시자 행도 자체 치유되는지 확인하는 통합 테스트 추가) |

### ⚠️ 실사용 중 추가로 발견·수정한 버그: `RuntimeError`도 CORS 없는 500으로 샌다

#27로 필터를 붙여 실제로 회의록 검색을 써보니 `예상치 못한 오류: Failed to fetch`가 다시 났다(§ 위
CORS 버그·Action Item PK 충돌은 이미 고친 뒤라 이번엔 또 다른 원인). 서버 로그:

```
File "app/workflows/meetings.py", line 361, in execute
    default_repo, default_provider = _search_dependencies()
File "app/workflows/meetings.py", line 112, in _search_dependencies
    raise RuntimeError("DATABASE_URL is required for search_meetings")
RuntimeError: DATABASE_URL is required for search_meetings
```

**원인**: `search_meetings`는 SQLite가 아니라 별도의 PostgreSQL+pgvector(`DATABASE_URL`)를 쓰는
유일한 Skill인데(07 §8.2, 이 세션의 다른 모든 기능은 SQLite만으로 동작), 지금까지 로컬 개발 서버를
띄울 때 쓰던 재기동 절차(`.env` + 4개 OIDC 환경변수)에 `DATABASE_URL`이 포함된 적이 한 번도 없었다
— #23 검증 때 쓴 Postgres는 1회성 Docker 컨테이너로 이미 삭제됨. `_search_dependencies()`는 이
누락을 관례대로 `RuntimeError`로 표시하는데, `app/internal_chat.py`가 그동안 잡던 예외는
`ValueError`뿐이라(위 CORS 버그 수정 때 추가) `RuntimeError`는 그대로 통과해 잡히지 않은 예외가
`verify_a2a_headers`(CORSMiddleware 바깥) 너머로 새 나가 다시 CORS 헤더 없는 500 → "Failed to
fetch"로 보였다. 코드베이스 전체를 보면 "인프라/설정 미비"는 `RuntimeError`가 이미 일관된
관례다(`app/storage/r2.py`의 R2 설정 누락, `app/repositories/*.py`의 `psycopg` 미설치 등 8곳) —
`meeting_api.py`가 R2 쪽 `RuntimeError`는 503으로 이미 변환하고 있었는데 스킬챗 경로만 빠져 있었다.

**수정**: `app/internal_chat.py`의 `validate_message()`에 `except RuntimeError`를 추가해 `503`으로
변환(422가 아니라 503을 쓴 이유: 요청 자체는 유효하고 서버 설정이 문제이므로, `meeting_api.py`
R2·`main.py` service token과 같은 기존 규칙을 따름). 그리고 이번 세션의 로컬 개발 서버용으로
Docker `pgvector/pgvector:pg16` 컨테이너(`workmate-pg-dev`, `55432` 포트, 4개 마이그레이션 적용)를
새로 띄워 `DATABASE_URL`을 재기동 절차에 포함시켰다 — 이제 껍데기 오류 메시지가 아니라 실제 검색이
동작한다(Python으로 `search_meetings` Workflow를 직접 호출해 필터 포함 `state: completed` 확인).
`tests/test_internal_chat.py`에 회귀 테스트 추가(Mock으로 `RuntimeError` 발생시켜 `503` + CORS
헤더 확인). 백엔드 회귀 최종 **224 tests (214 passed, 10 skipped)**.

### ⚠️ 실사용 중 추가로 발견·수정한 버그: `user_id`가 `uuid`가 아니라서 실제 로그인 사용자로는 검색이 항상 실패

위 수정을 배포하고 실제 로그인 계정으로 다시 검색해보니 이번엔 503도 아니고 여전히 "Failed to
fetch"가 났다 — 새로 잡은 `RuntimeError`가 아니라 **또 다른, 세 번째 예외 타입**이 새 나가고
있었다. 서버 로그:

```
File "app/repositories/meeting_chunks.py", line 374, in search_dense
    cursor.execute(sql, [vector_literal, *filter_params, limit])
psycopg.errors.InvalidTextRepresentation: invalid input syntax for type uuid: "104645315427066509691"
```

**원인**: `migrations/002_work_domain.sql`·`003_priority_snapshots.sql`·`004_search_data.sql`이
`users.user_id`와 이를 참조하는 모든 FK 컬럼(`tasks.assignee_user_id`,
`source_sync_states.sync_user_id`, `priority_snapshots.recipient_user_id`, `meetings.user_id`,
`meeting_chunks.user_id`)을 전부 `uuid` 타입으로 선언하고 있었다. 그런데 이 시스템의 `user_id`는
내부에서 발급하는 UUID가 아니라 **Google OIDC의 `sub` Claim을 그대로 쓴다** — 화면 좌측 하단에
보이는 `104645315427066509691` 같은 큰 10진수 문자열이라 uuid 형식이 전혀 아니다. `app/repositories/tasks.py`의
SQLite 스키마는 처음부터 `user_id TEXT`로 맞게 만들어져 있었는데, 유일하게 이 Postgres Migration만
잘못 선언돼 있었다. 이번 세션 내내 Task·회의·브리핑·주간보고 전부 SQLite로만 동작해서 이 버그가
드러날 길이 없었고, `search_meetings`가 실제 로그인 사용자로 실행된 것도 이번이 이 세션 처음이라
지금에서야 발견됐다. `psycopg.errors.InvalidTextRepresentation`은 `ValueError`도 `RuntimeError`도
아니라서 위에서 막 넓힌 `app/internal_chat.py`의 예외 처리도 통과하지 못하고 그대로 CORS 없는
500으로 샜다.

**수정**: 4개 Migration 파일 모두에서 `user_id` 계열 컬럼을 `uuid → text`로 정정(아직 실사용
Postgres 배포가 없어 새 `005_*.sql`을 추가하는 대신 원본 파일을 직접 고쳤다 — `psycopg` Repository들의
`_initialize()`가 매번 이 SQL 그대로 `CREATE TABLE IF NOT EXISTS`를 재실행하는 구조라 새 배포부터
바로 올바른 스키마로 만들어진다). 로컬 개발용 `workmate-pg-dev` 컨테이너는 기존 테이블을 지우고
재생성해 반영. `tests/test_work_domain_migration.py`의 기존 계약 테스트 2개가 이전 `uuid` 문자열을
검증하고 있어 `text`로 갱신하고, "왜 `uuid`가 아니라 `text`인지"를 명시하는 회귀 테스트를 새로
추가. 실제 화면에서 쓴 것과 동일한 `user_id`(`104645315427066509691`)로 Workflow를 직접 호출해
`state: completed`로 정상 동작하는 것 확인. **주의**: 이 과정에서 전체 테스트를 `DATABASE_URL`을
켠 채로 돌리면 무관한 테스트 12개가 무더기로 실패하는 것도 함께 발견 — 일부 테스트가 `DATABASE_URL`
존재 여부로 Postgres 경로를 타면서 격리된 SQLite 상태 대신 이 로컬 컨테이너의 공유 상태를 건드리기
때문이다(회귀 테스트는 항상 `DATABASE_URL` 없이 돌려야 함, 서버 기동 시에만 켬). 백엔드 회귀 최종
**225 tests (215 passed, 10 skipped)**, `DATABASE_URL` 없이 실행해 확인.

### ⚠️ 실사용 중 추가로 발견·수정한 버그: 색인된 회의에 실제 제목·날짜가 저장되지 않음

위 수정 후 다시 검색해보니 이번엔 CORS 응답은 정상으로 왔지만(422·503 수정이 둘 다 제대로
동작한다는 뜻) 내용이 `HTTP 422: meeting date is required for a cited source`였다 — 껍데기
오류가 아니라 실제 검증 실패다. 서버 로그:

```
File "app/workflows/meetings.py", line 390, in execute
    raise ValueError("meeting date is required for a cited source")
```

**원인**: `PostgresMeetingChunkRepository.create()`가 Chunk를 저장하면서 부모 `meetings` 행을
`INSERT INTO meetings(meeting_id,user_id,title) VALUES (%s,%s,'회의') ON CONFLICT DO NOTHING`으로
항상 **제목은 "회의" 자리표시자, `started_at`은 NULL 고정**으로 만들고 있었다 —
`_index_meeting_chunks()`가 애초에 실제 회의 제목·시각을 받지도, 넘기지도 않았기 때문이다.
`search_meetings`가 인용 출처를 만들 때(`meetings.py:389`) `source.meeting_started_at is None`이면
근거 날짜를 표시할 수 없다고 보고 `ValueError`를 낸다 — 이번엔 CORS 응답은 정상이라 422로 잘
보였을 뿐, 실제로 회의 날짜 데이터 자체가 없는 진짜 결함이었다. 확인해보니
`meeting.started_at`은 애초에 프론트(`Meeting.tsx`)가 회의 생성 시 아예 보내지 않는 선택
필드라 실사용 회의는 전부 `None`이었다.

**수정**: `MeetingChunkRecord`에 `meeting_title`/`meeting_started_at`/`meeting_ended_at`
필드를 추가하고, `build_analyze_meeting_workflow`가 이미 갖고 있는 실제 `meeting`(SQLite에서
조회한 원본)의 `title`·`started_at`·`ended_at`을 `_index_meeting_chunks()`를 거쳐 매 Chunk에
실어 보내도록 배선했다 — `started_at`이 없으면(실사용 회의 전부 해당) 항상 채워지는
`created_at`으로 대신한다. `PostgresMeetingChunkRepository.create()`의 `meetings` UPSERT도
`ON CONFLICT (meeting_id) DO UPDATE SET title=EXCLUDED.title, started_at=EXCLUDED.started_at,
ended_at=EXCLUDED.ended_at`으로 바꿔 재색인할 때마다 최신 값으로 자체 치유되게 했다. 로컬
`workmate-pg-dev`에 이미 잘못 저장돼 있던 실사용자의 두 회의 행은 SQLite 원본의 `created_at`으로
직접 백필해 화면 재시도 없이 바로 풀리게 했다. `tests/test_meeting_workflows.py`에 Chunk
Repository의 `create()` 호출 인자를 가로채는 Spy로 회귀 테스트 추가(SQLite Chunk 저장소는
계약 테스트 전용이라 이 필드를 되돌려주지 않아 Spy가 필요했다), `tests/test_meeting_chunk_postgres_integration.py`에
Postgres에 실제로 제목·시각이 쓰이고 이전 자리표시자 행도 재색인 시 고쳐 쓰이는지 확인하는
통합 테스트 추가. 실제 화면에서 쓴 질문("로그인 오류 언제까지 조치 가능하니")으로 Workflow를
직접 재현해 `meeting_date: "2026-08-15"`가 포함된 정상 응답을 확인. 백엔드 회귀 최종
**227 tests** — `DATABASE_URL` 없이 **216 passed, 11 skipped**,
`WORKMATE_TEST_DATABASE_URL`로 이전에 건너뛰던 Postgres 통합 테스트까지 포함해 **227 passed,
0 skipped** 둘 다 확인.

---

## 📬 제안함 (`Proposals.tsx`)

### #1. Google Calendar 일정 제안 — HTTP 진입점만 없음 (2026-08-15 정정)

**범위**: 백엔드 일부(신규 route 3개 + Webhook 1개) + 프론트 아주 조금. Gmail보다 훨씬 작은 작업.

> ⚠️ **정정**: 처음엔 "백엔드 `app/`에 `calendar` 관련 파일이 0개 — 완전 미착수"라고 판단했는데, 이건
> 파일명에 "calendar"가 없어서 못 찾은 것뿐이었다. 실제로는 Gmail과 같은 파일들 안에 Calendar용 Adapter·
> 도메인·저장·발행 계층이 이미 상당 부분 구현돼 있었다. 아래는 실제 코드를 다시 확인한 결과다.

**이미 있는 것**:

| 구성요소 | 위치 | 상태 |
| --- | --- | --- |
| `GoogleCalendarAdapter` (`list_events(sync_token=...)`, `watch(channel_id, address, token)`) | `app/providers/google.py` | ✅ 완성 |
| `CalendarEvent` 도메인 타입 (`source_id` 프로퍼티 = `{calendar_id}:{event_id}`) | `app/providers/google.py` | ✅ 완성 |
| `SyncStateRecord` — `source_type="google_calendar"`, `channel_id`/`channel_token`/`resource_id`/`watch_expiration` 필드 | `app/domain/sync_state.py` | ✅ 완성 (Gmail 전용이 아니라 처음부터 공용 설계) |
| `ExternalSyncWorkflow.sync_calendar()`(syncToken 증분 동기화 + `SyncStateRepository` 저장) | `app/workflows/external_sync.py` | ✅ 완성 |
| `publish_calendar_proposal()` — metadata에 `calendar_id`/`event_id`/`html_link`까지 채움, 프론트(`lib/proposal-review.ts`의 `reviewCalendar`)가 기대하는 형태와 정확히 일치 | `app/proposal_api.py` | ✅ 완성 |

**진짜 갭 (3개뿐)**:
1. HTTP 진입점이 없음 — 위 부품들을 실제로 호출해줄 route가 하나도 없음 (`dev_gmail_sync_api.py`에
   대응하는 파일 자체가 없음)
2. `POST /webhooks/google-calendar` 웹훅 수신 라우트 없음 (repo 전체 검색 0건)
3. 로컬 ngrok 노출 + watch 등록 절차 없음 (Gmail 때 만든 걸 재사용 가능)

**백엔드 작업**:

1. **`app/dev_calendar_sync_api.py` 신규** — `dev_gmail_sync_api.py` 미러링
   - `WORKMATE_DEV_CALENDAR_SYNC_ENABLED` 플래그(기본 false)
   - `_load_authorized_session()`: Gmail과 같은 `google-oauth-test/token.json` 재사용, scope만
     `calendar.readonly` — Gmail 쪽 함수를 거의 그대로 복붙하거나 공용 모듈로 뽑아도 됨(지금 Gmail
     파일에만 있어서 중복 예정)
   - `POST /api/v1/dev/calendar-sync`: `GoogleCalendarAdapter.list_events()` 호출 → [04-scenarios.md](04-scenarios.md)
     §8 규칙대로 "신규·확정·미래 일정"만 필터(`status=="confirmed"` AND 시작이 미래) → 각각
     `publish_calendar_proposal()` 호출. 중복 검사는 승인 시점에 이미 `proposal_api.py`가 하므로 여기선
     필터링만 하면 됨
   - `POST /api/v1/dev/calendar-watch/register`: `channel_id`/`channel_token`을 `uuid4`로 생성,
     `GOOGLE_CALENDAR_WATCH_ADDRESS`(ngrok URL, `07-technical-specification.md`에 이미 환경변수로 정의됨)로
     `adapter.watch()` 호출 → 결과 저장. **결정 포인트**: Gmail은 재기동하면 날아가는 인메모리 딕셔너리를
     쓰는데, Calendar는 `SyncStateRepository`가 이미 준비돼 있으니 처음부터 영속 저장하는 걸 권장 (Gmail도
     나중에 이렇게 고쳐야 하는 이미 알려진 이슈)
   - `GET /api/v1/dev/calendar-watch/status`: 등록 상태 확인
2. **웹훅 수신 라우트** `POST /webhooks/google-calendar`
   - `X-Goog-Channel-ID`/`X-Goog-Channel-Token`/`X-Goog-Resource-ID` 헤더를 저장된 값과 대조
   - 검증되면 바로 `204` 반환(Google이 빠른 응답을 기대함), 실제 동기화는 백그라운드 태스크로
   - Calendar 웹훅은 본문에 데이터가 없어서(그냥 "뭔가 바뀜" 신호) 무조건 `events.list(syncToken=...)`로
     다시 조회 — Gmail의 historyId 비교보다 오히려 단순함
3. `SSE /api/v1/notifications/stream`은 이미 공용 채널이라 Calendar 이벤트 추가 배선은 불필요

**프론트 작업**: `devCalendarSyncApi.trigger()` 하나 추가(Gmail의 `devGmailSyncApi` 패턴 그대로),
`Proposals.tsx`에 "Calendar 동기화 실행" 버튼 하나(Gmail 버튼 옆에). 카드 렌더링·승인/무시는 이미 다 돼 있음.

**로컬 테스트**: Gmail과 동일한 절차 — ngrok 노출 → watch 등록 → 실제 캘린더에 일정 추가해서 웹훅 도착 확인.

**공수**: 반나절~1일 (기존 2~3일 추정에서 축소 — Adapter/도메인/저장/발행 계층이 이미 있어서 사실상
HTTP 껍데기 배선 작업. 가장 큰 리스크는 코드가 아니라 ngrok/Google Cloud 프로젝트 설정 같은 인프라 쪽 —
Gmail 때도 그 부분이 제일 오래 걸렸음)

### #19. Gmail 수동 동기화가 이미 처리한 메일을 다시 제안으로 노출함

**범위**: 백엔드 (`app/dev_gmail_sync_api.py`)

**현재 상태**: `POST /api/v1/dev/gmail-sync`는 매번 최근 메일 N건을 무조건 다시 LLM으로 분석해 제안으로
발행한다. 그 메일이 이미 승인돼 Task가 만들어졌는지, 이미 무시됐었는지 확인하는 로직이 전혀 없다. 그래서
버튼을 여러 번 누르면 이미 처리한 메일도 다시 카드로 뜬다. (승인 버튼을 다시 눌러도 `proposal_api.py`의
`(source_type, source_id)` 중복 검사 덕분에 Task가 중복 생성되지는 않지만, 카드 자체는 매번 다시 나타나
사용자가 "이미 봤던 건데 또 뜨네"라고 느끼게 된다.)

**주의 — 두 경우가 다르다**:
- **이미 승인한 메일**: `source_type=email`, `source_id=message_id`(또는 `message_id:index`)로 Task가
  이미 존재하는지 `task_repository()`에서 조회해 필터링하면 됨 — 구현이 명확함.
- **이미 무시한 메일**: 이건 더 조심해야 한다. [04-scenarios.md](04-scenarios.md) §7이 이미 "무시한 후보는
  `[직전 영업일 00:00, as_of)` 범위에 포함되면 **다음 브리핑에 다시 표시될 수 있다**"고 명시한다 — 즉
  `daily_briefing`의 자동 재노출은 의도된 설계다. 게다가 "무시" 결정 자체는 어디에도 저장하지 않는다는
  것도 문서 원칙이다("메일과 제안 결과는 DB에 저장하지 않는다"). 수동 동기화 버튼이 이 원칙과 다르게
  동작해야 하는지(예: 이번 세션 안에서만 프론트가 기억해서 숨기기)는 **제품 결정이 필요**하다.

**작업 (승인된 메일 필터링만, 결정 없이 바로 가능한 부분)**:
1. `/gmail-sync`에서 메일 목록을 가져온 뒤, 각 `message_id`에 대해 `source_type=email`이고
   `source_id`가 해당 메일에서 파생된 Task가 이미 있는지 확인
2. 있으면 `_publish_action_items_for_message` 호출(LLM 추출)을 건너뛰고 `skipped`에
   `{"message_id": ..., "reason": "already_approved"}`로 기록해 프론트에 알림

**작업 (무시한 메일 처리, 결정 필요)**:
- (A) 문서 원칙대로 무시 결정은 저장하지 않고 계속 재노출 → 코드 변경 없음, 프론트에서 "이미 무시했던
  항목입니다" 안내만 추가하는 정도로 타협
- (B) 수동 동기화 버튼만 예외적으로 세션 내 무시 목록을 프론트 `localStorage`나 백엔드 인메모리에 잠깐
  기억해 재노출 안 함 → 문서 원칙과 다르게 동작하므로 별도로 문서화 필요

**공수**: 승인된 메일 필터링만 반나절, 무시 메일 처리는 결정 이후 반나절 추가

---

## ✅ 제안함(#1, #19) 구현완료보고서 (2026-08-15)

### #1. Google Calendar 일정 제안 — 구현 완료

계획대로 백엔드 신규 route 3개 + Webhook 1개 + 프론트 버튼 1개를 구현했다.

**백엔드 — `workmate-agent/app/dev_calendar_sync_api.py` 신규**:
- `POST /api/v1/dev/calendar-sync`: `GoogleCalendarAdapter.list_events(time_min=now)` 호출 → `status=="confirmed"` AND 시작이 미래인 일정만 필터 → 이미 승인된 `(calendar_id, event_id)`는 건너뛰고 나머지만 `publish_calendar_proposal()`
- `POST /api/v1/dev/calendar-watch/register`: `channel_id`/`channel_token`을 `uuid4`로 생성해 `adapter.watch()` 호출, 결과를 **`SyncStateRepository`에 영속 저장**(계획대로 Gmail의 인메모리 방식 대신 처음부터 DB 저장 사용). Webhook이 `channel_id`로 사용자를 빠르게 찾도록 인메모리 역인덱스(`_channel_index`)도 같이 둠 — 재기동하면 이 역인덱스만 비워지고(재등록 필요), `sync_cursor`·Watch 메타데이터는 DB에 남아 있음
- `GET /api/v1/dev/calendar-watch/status`: 등록 상태 조회
- `POST /webhooks/google-calendar`(`webhook_router`, 별도 등록): `X-Goog-Channel-ID`/`-Token`/`-Resource-Id` 헤더를 저장된 값과 `hmac.compare_digest`로 대조, 검증 여부와 무관하게 항상 `204`를 즉시 반환하고 실제 동기화(`events.list(syncToken=...)` 재조회 → 필터 → 발행 → 새 `syncToken` 저장)는 `BackgroundTasks`로 분리
- `app/main.py`에 두 Router 등록

**프론트 — `workmate-ui`**:
- `lib/workmate-types.ts`: `CalendarSyncResponse` 타입 추가
- `lib/workmate-api.ts`: `devCalendarSyncApi.trigger()` 추가
- `app/views/Proposals.tsx`: "Calendar 동기화 실행" 버튼을 Gmail 버튼 패널 바로 아래에 추가(같은 패턴), 빈 상태 안내 문구도 Calendar 언급하도록 수정

**검증**:
- 신규 `tests/test_dev_calendar_sync_api.py` 12개 작성 — 비활성화 시 404, 확정·미래 일정만 발행(미확정/과거/취소 제외), 이미 승인된 일정 건너뜀, Watch 등록·영속 저장·상태 조회, Webhook의 알 수 없는 Channel 무시(204), 정상 Channel의 백그라운드 동기화 실행과 `syncToken` 갱신 확인, 잘못된 Channel Token 거부(204, 미발행)까지 확인
- 백엔드 전체 회귀 `183 passed, 10 skipped, 0 failed` (기존 테스트 깨짐 없음)
- 프론트 `npx tsc --noEmit`·`eslint` clean, `npm test`(build + 18개 테스트) 전부 통과

**아직 안 된 것 (코드가 아니라 실제 인프라 확인 필요)**:
- 실제 Google Calendar 계정으로 `/api/v1/dev/calendar-watch/register` → ngrok 노출 → 실제 일정 추가 →
  Webhook 도착까지의 End-to-End 확인은 **하지 않았다** (Gmail 때처럼 로컬 ngrok 실행과 실제 Google Cloud
  프로젝트의 Calendar Push 채널 설정이 필요해 이번 세션 범위 밖). 코드 계약과 단위 테스트는 확인됐지만
  실환경 검증은 별도로 필요
- `WORKMATE_DEV_CALENDAR_SYNC_ENABLED=true`, `GOOGLE_CALENDAR_WATCH_ADDRESS=<ngrok URL>/webhooks/google-calendar`
  환경변수를 실행 전에 설정해야 함 (Gmail의 `WORKMATE_DEV_GMAIL_SYNC_ENABLED`/`WORKMATE_DEV_GMAIL_PUSH_TOPIC`과
  같은 위치에 추가하면 됨)

### #19. Gmail 수동 동기화 중복 재노출 — "승인된 메일" 필터링만 구현 완료

계획에서 결정 없이 바로 가능하다고 표시했던 부분만 구현했다.

**백엔드 — `workmate-agent/app/dev_gmail_sync_api.py`**:
- `_already_approved(user_id, message_id)` 추가: `task_repository().list(user_id)`에서
  `source_type=="email"`이고 `source_id`가 해당 `message_id` 정확히 일치하거나 `message_id:`로 시작하는
  Task가 있으면 `True`. 정확한 index까지는 비교하지 않고 "이 메일에서 나온 Task가 하나라도 있으면 메일
  전체를 처리 완료로 본다"는 방침으로 구현(재동기화 시 LLM 추출 순서가 바뀔 수 있어 index 단위 비교는
  신뢰할 수 없다고 판단)
- `trigger_gmail_sync`에서 각 메일마다 LLM 호출(`extract_action_items`) 전에 이 함수로 먼저 걸러 `skipped`에
  `{"message_id": ..., "reason": "already_approved"}`로 기록

**검증**: `tests/test_dev_gmail_sync_api.py`에 `test_already_approved_message_is_skipped_without_llm_call`
추가 — 이미 Task가 있는 메일은 `extract_action_items`가 아예 호출되지 않음(LLM 비용도 아낌)을
`mock_extract.assert_not_called()`로 확인. 기존 테스트에 Task DB 격리(임시 SQLite 파일)도 새로 추가.

**구현하지 않은 것**: "이미 무시한 메일" 필터링은 계획대로 **제품 결정 대기 상태로 남겨둠**. 04-scenarios.md
§7의 "무시한 후보는 다음 브리핑에 다시 표시될 수 있다"는 문서 원칙과 충돌할 수 있어 (A)/(B) 중 결정이
먼저 필요하다.

### 변경/신규 파일 목록

| 파일 | 종류 |
| --- | --- |
| `workmate-agent/app/dev_calendar_sync_api.py` | 신규 |
| `workmate-agent/app/dev_gmail_sync_api.py` | 수정 (`_already_approved` 추가) |
| `workmate-agent/app/main.py` | 수정 (Router 2개 등록) |
| `workmate-agent/tests/test_dev_calendar_sync_api.py` | 신규 |
| `workmate-agent/tests/test_dev_gmail_sync_api.py` | 수정 (DB 격리 + #19 테스트 추가) |
| `workmate-ui/lib/workmate-types.ts` | 수정 (`CalendarSyncResponse`) |
| `workmate-ui/lib/workmate-api.ts` | 수정 (`devCalendarSyncApi`) |
| `workmate-ui/app/views/Proposals.tsx` | 수정 (Calendar 동기화 버튼) |

---

## 🌐 공통/전역 (여러 화면이 공유하는 Hook·API 클라이언트)

### #5. 장기 Task Polling 부재

**범위**: 프론트엔드만 (백엔드는 이미 준비됨)

**영향 화면**: 오늘 브리핑 · 주간 업무보고 · 회의록 검색 · 회의 관리 (4개 화면이 `use-skill.ts` 공유)

**현재 상태**: `lib/use-skill.ts`의 `useSkillRunner`가 `/api/v1/internal/skill-chat/messages` 응답을 그대로
최종 결과로 취급. `TASK_STATE_SUBMITTED/WORKING` 상태 확인이나 Polling 로직이 없음.

**백엔드 확인 결과**: `app/internal_chat.py`에 `GET /api/v1/internal/skill-chat/tasks/{id}`,
`POST /api/v1/internal/skill-chat/tasks/{id}:cancel`, Terminal 상태 판정까지 이미 구현돼 있음. 참고 구현도
존재: `app/internal_chat_ui.py`의 디버그 JS `refreshTask()`가 정확히 이 Polling 패턴을 사용.

다만 현재 백엔드는 `analyze_meeting`을 포함해 모든 Skill을 **동기적으로 끝까지 실행한 뒤에만** 응답하고
(`_persist_task`가 결과를 무조건 `TASK_STATE_COMPLETED`로 저장), 그래서 지금 당장은 화면이 깨지는 증상이
보이지 않는다. 문서가 정의한 `SUBMITTED → WORKING → COMPLETED` 장기 Task 구조와는 어긋나 있고, 백엔드가
나중에 실제 비동기 실행으로 바뀌면 프론트가 미완성 결과를 최종 결과처럼 보여주는 문제가 생긴다. 선제적으로
고치는 것을 권장.

`07-technical-specification.md` §5.4, §9.3에서도 동일하게 "analyze_meeting처럼 오래 걸리는 작업은 내부
Task ID를 표시하고 Polling으로 상태를 갱신한다"를 요구함 — 02·07·09 세 문서가 모두 일치해서 요구하는
항목이라 우선순위를 올릴 근거가 확실하다.

**작업**:
1. `run()`이 첫 응답의 `state` 확인
2. Terminal 상태(`COMPLETED/FAILED/CANCELED/REJECTED`)가 아니면 `GET .../tasks/{task_id}`를 지수 backoff로
   Polling (`02-a2a-interface.md` §6.6: 2초 시작, 최대 10초)
3. Terminal 도달까지 loading 유지, `INPUT_REQUIRED`/`AUTH_REQUIRED` 상태를 별도로 노출할지 결정 (현재는
   이런 상태 자체를 모델링하지 않음)
4. 취소 버튼을 붙일지 결정 (`analyze_meeting` 실행 중 사용자 취소)

**영향 파일**: `lib/use-skill.ts` (Briefing/Report/Search/Archive 4개 화면이 공유하므로 한 번에 적용됨)

**공수**: 반나절

---

## 변경 이력

- 2026-08-15: 초안 작성 (docs 대조 분석 + 백엔드 코드 확인 기반)
- 2026-08-15: docs 03·07·09 대조 결과 추가 (#9~#18), `workmate-ui` "폐기된 샘플" 명시 발견을 문서
  상단에 반영
- 2026-08-15: `workmate-ui`를 다시 사용하기로 결정 번복. 상단 경고를 "결정 번복" 안내로 교체하고,
  07·09·`workmate-ui/README.md`의 "폐기된 샘플" 문구 갱신이 후속 작업으로 필요함을 기록
- 2026-08-15: 2단계 계획 확정 — 1차 `workmate-ui` 완성(완성본은 개인용 keep) → 2차 Orchestrator UI
  양식으로 이식. 상단 안내를 이 계획으로 구체화
- 2026-08-15: `07-technical-specification.md`, `09-ui-design.md`, `workmate-ui/README.md`의 "폐기된
  샘플" 문구를 2단계 계획에 맞게 수정 완료
- 2026-08-15: `workmate-ui`와 별도로 존재하던 독립 정적 HTML/JS UI `workmate-ui`(오케스트레이터를
  거치지 않고 `workmate-agent`를 직접 호출, 미추적 로컬 디렉터리)를 혼동 방지를 위해 폐기·삭제.
  `01-overview-architecture.md`, `06-delivery-plan.md`, `AGENTS.md`, `HANDOFF.md`에 남아있던 나머지
  "폐기된 샘플" 문구도 2단계 계획에 맞게 갱신 완료
- 2026-08-15: 문서 전체 구조를 `workmate-ui` 실제 메뉴(오늘 브리핑·주간 업무보고·할 일 관리·회의
  녹음·회의 관리·회의록 검색·제안함) + 공통/전역 기준으로 재구성. 기존에 발견 순서(#1~#18)로 나열하고
  별도 요약표로만 화면을 안내하던 방식을, 화면별 섹션 안에 전체 상세 내용을 담는 방식으로 바꿈. "기존 항목
  보강" 각주였던 09-ui-design.md 세부 요구사항(URL 패턴 등)도 해당 항목 본문에 합침
- 2026-08-15: **#1 Google Calendar 연동 정정** — 백엔드 코드를 다시 확인해보니 "calendar 관련 파일 0개"는
  파일명 검색의 오류였음. `GoogleCalendarAdapter`, `CalendarEvent`, `SyncStateRecord`의 Calendar 지원,
  `ExternalSyncWorkflow.sync_calendar()`, `publish_calendar_proposal()`이 이미 Gmail 파일들 안에 구현돼
  있었음. 실제 갭은 HTTP 진입점(`dev_calendar_sync_api.py`)과 웹훅 라우트 부재뿐이라 공수를 "대형(2~3일)"
  에서 "소형~중형(반나절~1일)"으로 재산정
- 2026-08-15: **#19 신규 추가** — Gmail 수동 동기화(`/api/v1/dev/gmail-sync`)가 이미 승인·무시한 메일을
  구분 없이 다시 제안으로 재노출하는 문제 발견. 승인된 메일 필터링은 바로 구현 가능하지만, 무시한 메일
  필터링은 04-scenarios.md §7("무시한 후보는 다음 브리핑에 다시 표시될 수 있다")과 "제안은 DB에 저장하지
  않는다" 원칙에 저촉될 수 있어 제품 결정 필요로 표시
- 2026-08-15: 문서 번호 부여(`workmate-ui-integration-gaps.md` → `14-workmate-ui-integration-gaps.md`),
  `docs/README.md` 정식 목차에 등재. 제안함 기능·데이터를 정리한 [15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md)
  신규 작성
- 2026-08-15: **#1·#19 구현 완료** — `dev_calendar_sync_api.py` 신규(route 3개 + Webhook), `dev_gmail_sync_api.py`에
  승인된 메일 필터링 추가, 프론트 Calendar 동기화 버튼 추가. 백엔드 회귀 183 passed/10 skipped, 신규
  테스트 24개 전부 통과, 프론트 tsc/eslint/npm test 전부 clean. 구현완료보고서를 제안함 섹션 말미에 추가.
  실제 Google Calendar 계정 ngrok E2E 검증은 아직 안 함(별도 인프라 작업 필요). #19의 "무시한 메일" 처리는
  여전히 제품 결정 대기
- 2026-08-15: [15-workmate-ui-screens-reference.md](15-workmate-ui-screens-reference.md)의 목적이 "as-built
  기록"에서 "02·03·04·07·09를 종합한 화면별 목표 기능·조회값 정의"로 바뀜에 따라, 이 문서(14번)의 배경도
  15번을 1차 기준으로 참고하도록 갱신
- 2026-08-15: **"🎙️ 회의 녹음" 섹션을 "🎙️ 회의 녹음 및 분석"으로 전면 재작성** — 15번 문서가 확장한 8단계
  전체 흐름 기준으로 백엔드를 다시 추적한 결과, 녹음/업로드 → STT → 분석 파이프라인이 완전히 끊겨 있어
  실사용자 경로로는 `analyze_meeting`에 절대 도달할 수 없다는 것을 새로 확인함. 신규 항목 #20(녹음 파일
  미저장, R2 미연동)·#21(실시간 녹음이 최종 Transcript를 절대 못 만듦, STT 완전 미연결)·#22(analyze_meeting
  실사용 불가, 표시용)·#23(meeting_chunks/embedding 저장 없음)·#24(분석 전용 엔드포인트 부재) 추가.
  기존 #14의 "기능은 동작한다"는 판단이 R2 저장 여부를 확인 안 하고 내린 잘못된 결론이었음을 정정.
  전체 우선순위 표에서 이 5개 항목을 최상단(1~6번)으로 재배치
- 2026-08-15: 15번 문서가 "🎙️ 회의 녹음 및 분석"을 화면 경계로 다시 나눈 것에 맞춰 이 문서도 재분리 —
  "🎙️ 회의 녹음"은 04 §3 1~6단계(회의 생성~Action Item 자동 추출)만 담당하도록 헤더·설명 정정. #24를
  "분석 시작"(회의 녹음 책임)으로 좁히고, 결과 "조회" 부분을 새 항목 **#25**로 분리해 📁 회의 관리
  섹션으로 이동. 회의 관리 섹션 서두에 "이 화면 전체가 #21·#22 때문에 지금 검토할 결과 자체가 안
  생긴다"는 경고 추가, #4에도 같은 취지 상태 갱신. 전체 우선순위 표에 #25 반영(21개 항목으로 증가)
- 2026-08-15: **🎙️ 회의 녹음 작업계획 추가** — 11개 항목(#7·#8·#12·#13·#14·#15·#20·#21·#22·#23·#24)을
  의존관계 기준 5단계(Phase 0 결정 → Phase 1 즉시 가능 → Phase 2 STT 선행조건(#13) → Phase 3 핵심
  파이프라인 복구(#20 R2 → #21 STT, 순차) → Phase 4 분석 후처리(#23·#12))로 정리. R2 Provider는
  `app/providers/r2.py` 신설, STT Provider는 `app/embeddings.py`의 `OpenAICompatibleEmbeddingClient`
  패턴을 따라 `app/stt.py` 신설을 구체적 실행 메모로 남김. 총 예상 공수 1.5~2주(Phase 2·3 순차 최소
  4~6일 + 병렬 가능한 나머지)
- 2026-08-15: **작업계획 1차 검증** — 계획대로 해도 실시간 녹음 경로가 여전히 막힌다는 것을 발견. 지금
  `recording_stream.py`는 수신한 오디오 바이트를 SHA256 해시 계산에만 쓰고 그 자리에서 버려서, Chunk를
  누적·병합·R2 업로드하는 로직이 원래 계획(#20, 파일 업로드만 다룸)에 아예 빠져 있었음. Phase 3 #20에
  "실시간 녹음 Chunk 누적·병합" 작업을 추가하고 공수를 1~2일→2~3일로 재산정.
- 2026-08-15: **작업계획 2차 검증** — 두 가지 추가 보완: (1) #13 이후 브라우저가 raw PCM16을 보내므로
  Chunk 병합 시 WAV 헤더(mono·24kHz·16bit)를 씌워야 함, STT Provider는 URL이 아니라 실제 파일 바이트가
  필요해 R2 `GetObject`로 먼저 내려받는 절차가 필요함을 명시. (2) #15(일시정지 버튼)가 원래 Phase
  1(MediaRecorder 기준, #13 이전)에 있어 #13이 MediaRecorder를 걷어내면 재작업이 생기는 순서 문제를
  발견 — Phase 2.5로 옮겨 #13 완료 후 AudioWorklet 기준으로 구현하도록 수정. Chunk 병합 시 순서 보장은
  기존 `recording_stream.py`의 Gap 거부·중복 무시 로직이 이미 처리하고 있어 별도 조치 불필요함을 확인.
  이 두 항목 반영 후 11개 항목을 모두 커버하는 것으로 재확인됨
- 2026-08-15: **🎙️ 회의 녹음 11개 항목(#7·#8·#12·#13·#14·#15·#20·#21·#22·#23·#24) 구현 완료** —
  파이프라인 단절을 실제로 해소. #20(R2, 파일 업로드·실시간 녹음 두 경로), #21(파일 기반 최종 STT,
  `analyze_meeting` 자동 트리거로 배선), #23(meeting_chunks/embedding 저장)은 Mock이 아니라 실 R2·실
  OpenAI STT·실 OpenAI Embedding·실 PostgreSQL/pgvector(Docker) 계정으로 직접 실행해 검증. #22는 "자동
  해소" 표시용 항목이었지만 실제로 전체 파이프라인을 한 번에 실행해 정확한 요약·Action Item 추출을 확인.
  R2 Provider Client는 계획과 달리 신규 작성하지 않고 기존 `app/storage/r2.py`를 사용했는데, 이 과정에서
  `R2Config.from_env()`의 실제 버그(환경변수명을 그대로 Dataclass 키워드 인자로 전달)를 발견해 수정. #7은
  계획한 `Idempotency-Key` Header 대신 이미 있던 client-supplied `meeting_id` + 서버 `INSERT OR IGNORE`로
  해결(`02-a2a-interface.md` §6.5 정정, 동일 Key·다른 Payload → 409 계약은 미충족 상태로 명시). #12는
  #5(Task Polling) 없이도 WebSocket `close` 이벤트만으로 프론트엔드에서 해결. #21의 실시간 Partial 자막
  Streaming(OpenAI Realtime WebSocket)은 의도적으로 범위에서 제외 — 프로토콜은 확인했지만 브라우저·
  OpenAI 두 WebSocket을 동시에 중계하는 별도 작업이 필요해 핵심 파이프라인(파일 기반 최종 STT)을 먼저
  완성하는 쪽을 택함. 프론트 tsc/eslint/npm test(28개) 전부 통과. 실사용 검증 중 세 가지 버그를 추가로
  발견·수정: (1) `analyze_meeting` 등 Workflow의 `ValueError`가 CORS 헤더 없는 500으로 새 나가 브라우저에
  `Failed to fetch`만 보이던 문제 — `app/internal_chat.py`에서 422로 변환(5개 Skill 전부 영향), (2)
  `websockets` 패키지가 의존성에 없어 Uvicorn이 WebSocket Upgrade 자체를 처리 못 하고 무조건 404를
  반환하던 문제 — `websockets>=17.0.1` 의존성 추가, (3) 브라우저가 제시한 WebSocket Subprotocol을 서버가
  응답에서 선택(echo)하지 않아 실제 브라우저(Chrome 등)에서만 Handshake가 실패하던 문제 —
  `recording_stream.py`가 `accept(subprotocol=...)`로 하나를 echo하도록 수정. 셋 다 Starlette
  `TestClient`나 순수 Python `websockets` Client로는 재현되지 않고 실제 브라우저로만 드러나는 종류의
  결함이었다. 백엔드 회귀 최종 203 passed/10 skipped.
  상세 내용과 실 E2E 검증 결과는 [✅ 회의 녹음 구현완료보고서](#-회의-녹음7·8·12·13·14·15·20·21·22·23·24-구현완료보고서-2026-08-15)
  참고. 전체 우선순위 표 갱신, #12 신규 행 추가(22번)
- 2026-08-15: **#21 실시간 Partial 자막 Streaming 추가 구현(후속 요청)** — 위 완료보고서에서 의도적으로
  범위 밖으로 뺐던 부분을 사용자 요청으로 마저 구현. `app/stt.py`에 `RealtimeSttSession` 신규(OpenAI
  Realtime WebSocket Client), `recording_stream.py`가 브라우저 Chunk 수신 루프와 별도 `asyncio.Task`로
  Provider 이벤트를 중계(`asyncio.Lock`으로 같은 WebSocket 쓰기 직렬화). 실 계정으로 확인해보니 Provider가
  자체 Turn 검출로 자동 `completed`를 보내 우려했던 주기적 수동 `commit`이 불필요해 설계가 단순해짐 —
  Provider 연결 실패도 기존 "조용히 자막 없이 진행" 방침을 그대로 재사용해 별도 오류 전파 설계가
  필요 없었음. `Meeting.tsx`의 `chunk_no`(자막 한 줄 번호로 의미가 바뀜) 처리가 매번 새 줄을 추가해
  Delta가 쌓일수록 중복 행이 늘어나던 프론트 버그도 같이 발견·수정. 단위 테스트(`RealtimeSttSession` 5개,
  `recording_stream.py` 자막 중계·Provider 실패 시 자막 없이 진행 회귀 테스트 2개) 전부 Mock/Fake 기반,
  실 네트워크는 별도 실 E2E로 검증: (1) `RealtimeSttSession` 단독으로 실 OpenAI Realtime API에 실제 회의
  음성을 스트리밍해 정확한 한국어 Delta·Final 이벤트 확인, (2) 브라우저와 동일한 방식(Subprotocol 인증,
  PCM16 24kHz 200ms Chunk)으로 실제 서버 `/recording-stream`에 접속해 145개 Chunk 전부 정상 ACK되면서
  87개의 정확한 누적 자막이 함께 오는 것 확인(자막 기능이 기존 버퍼링·R2 저장 경로를 방해하지 않음).
  테스트로 만든 R2 객체는 확인 후 삭제. 백엔드 회귀 최종 **210 passed, 10 skipped**. 전체 우선순위 표
  #21 상태를 ✅ 완료로 갱신.
- 2026-08-15: **실사용 중 네 번째 버그 발견·수정** — `action_item_id`는 서버가 아니라 LLM이 구조화
  출력에서 스스로 매기는 값인데(`app/meeting_analysis.py`), 전역 유일성을 지시하지 않고
  `temperature=0`으로 고정돼 있어 비슷한 회의를 반복 분석하면 서로 다른 회의가 같은 ID를 매길 수 있었다.
  `action_items` 테이블이 `action_item_id` 단일 컬럼만 PK라 이 경우 `INSERT OR IGNORE`가 조용히
  무시되고 뒤이은 조회가 실패해 `AssertionError` → CORS 없는 500 → 브라우저에 다시 "Failed to fetch"로
  보였다. PK를 `(action_item_id, meeting_id)` 복합 키로 바꾸고, 기존 DB 파일을 위한 1회성 마이그레이션
  (`_initialize()`가 예전 스키마를 감지하면 테이블을 새로 만들어 데이터를 옮김)을 추가. 회귀 테스트
  추가, 백엔드 회귀 최종 **211 passed, 10 skipped**.
- 2026-08-15: **📋 할 일 관리 섹션 재분석·대체** — 새로 작성된
  [15번 문서의 할 일 관리 절](15-workmate-ui-screens-reference.md#-할-일-관리-taskstsx)을 기준으로
  `app/task_api.py`·`Tasks.tsx`·`lib/workmate-api.ts`를 다시 대조. 가장 큰 발견: **기존 Task를 수정하는
  UI 자체가 없음**(신규 #26) — 제목·마감일·중요도는 등록 후 절대 못 고치고, 상태도 완료/되돌리기
  토글 외엔 바꿀 방법이 없어 목록 상단의 "진행 중"·"지연" 필터 탭이 항상 0건으로 죽어 있는 것도 이번에
  확인함. #17(필터 없음)도 재확인 결과 프론트만이 아니라 **백엔드 `GET /api/v1/tasks`도 애초에
  `assignee_user_id`·`due_at` Query 파라미터를 안 받는다**는 것을 발견해 범위를 "프론트+백엔드"로 정정.
  #3(`tasksApi`에 `get()` 메서드조차 없음 확인)·#6·#18은 재확인 결과 그대로 유효해 유지. 전체 우선순위
  표에 #26 추가(23번), #17 공수 재산정.
- 2026-08-15: **📋 할 일 관리 #6·#17·#18·#26 구현 완료** — 작업계획 세우고 그대로 진행. #6은 "본인
  전용 유지"로 결정해 02·09·15번 문서 3곳을 실제 구현(항상 `assignee_user_id=본인`)에 맞게 정정하고
  각주 추가, 이 결정에 따라 #17의 담당자 필터도 목표에서 제외(값이 항상 하나뿐이라 무의미). #26(가장
  큰 항목)은 `Tasks.tsx`에 수정 폼을 신설해 제목·마감일·중요도·상태를 등록 후에도 고칠 수 있게 하고
  중요도 입력 UI도 새로 추가 — 백엔드는 이미 다 지원하고 있어 프론트만 고치면 됐음. #17의 마감일
  필터는 백엔드에 `due_before` Query 파라미터를 새로 추가하고 프론트에 날짜 필터 UI를 붙였으며, 기존
  상태 필터 탭이 있는 `status` 파라미터를 안 쓰고 있던 것도 같이 고침. #18은 삭제 확인창에 제목 포함.
  #3은 계획대로 이번 범위 제외(의존 대상인 전체 회의록 화면 미존재). 백엔드 회귀 212 passed/10
  skipped(무관한 기존 Flaky 테스트 1건 별도 확인), 프론트 eslint·build·npm test(28개) 전부 통과. 구현
  완료보고서를 할 일 관리 섹션 말미에 추가, 우선순위 표 갱신(#6·#17·#18·#26 전부 ✅).
- 2026-08-15: **할 일 관리 UI 후속 정리(사용자 화면 확인 후 요청)** — (1) 동작 버튼("수정"/"완료"/
  "삭제")이 좁은 열 폭 때문에 버튼 안에서 줄바꿈되던 것을 `whiteSpace:nowrap`+우측 정렬로 수정, (2)
  목록 정렬 기준을 `updated_at DESC`에서 **등록일시(`created_at`) 최신순**으로 변경 — 이 과정에서
  기존 `test_list_order_is_deterministic`가 간헐적으로 실패하던 원인(동시 생성 Task의 `updated_at`
  우연 일치에 의존한 약한 검증)을 찾아 `test_list_order_is_most_recently_created_first`로 재작성해
  Flaky 문제 자체를 해결, (3) `.table-row` 열 너비 조정(할 일 넓힘, 중요도 좁힘, 열 간격 20px 추가).
  15번 문서에도 응답 정렬 순서 명시. 백엔드 회귀 212 passed/10 skipped(Flaky 테스트 5회 재실행으로
  안정성 확인), 프론트 eslint·build·npm test 전부 통과.
- 2026-08-15: **🔍 회의록 검색 섹션 재분석·대체 및 구현** — 기존엔 "이 화면 고유의 갭은 없음"이라고
  적혀 있었는데, 새로 작성된 [15번 문서의 회의록 검색 절](15-workmate-ui-screens-reference.md#-회의록-검색-searchtsx)을
  기준으로 다시 보니 실제로는 5개 항목(#27~#31)이 있었다. **#27(날짜·회의 선택 필터 UI 부재)**을
  바로 구현 — 백엔드 `build_search_meetings_workflow`가 이미 `date_from`/`date_to`/`meeting_ids`를
  전부 지원하는데(오늘 #23에서 실 E2E 검증 완료) `Search.tsx`엔 질문 입력창 하나뿐이라 쓸 방법이
  없었다. `searchMeetingsInput()`에 `filters` 인자 추가, `Search.tsx`에 날짜 2개·회의 선택
  드롭다운·필터 초기화 버튼 추가. **#30(전용 REST 엔드포인트 미사용)**은 #24·#25와 완전히 같은
  모양이라 같은 판단으로 스킬챗 경로 유지 결정, 02번 문서에 각주 추가. **#28(참여자 필터)**은
  `MeetingParticipant` 모델 자체가 코드베이스에 아예 없다는 걸 확인해 #11에 종속된 결정 대기로 남김.
  **#29(Reranker)**는 07번 문서 §8.2.1이 스스로 "실제 구현은 M4.4에서 수행한다"고 이미 정해둔
  것이라 이번에 새로 찾은 갭이 아님을 확인 — 표시만. **#31(검색 결과→전체 회의록 이동)**은 회의
  관리 #2(전체 회의록 화면 부재)에 종속돼 있어 대기. 프론트 eslint·build·npm test(29개, 신규 필터
  테스트 2개 포함) 전부 통과, 백엔드 코드 변경 없어 회귀만 재확인(212 passed/10 skipped, 변화 없음).
  전체 우선순위 표에 #27~#31 반영(24~28번), 구현완료보고서를 회의록 검색 섹션 말미에 추가.
- 2026-08-15: **🏠 오늘 브리핑 섹션 재분석·대체 및 구현** — 새로 작성된
  [15번 문서의 오늘 브리핑 절](15-workmate-ui-screens-reference.md#-오늘-브리핑-briefingtsx)을
  기준으로 재확인. 기존 #9·#10은 그대로 유효했고, Schema까지 직접 대조하며 새로 3개(#32·#33·#34)를
  찾았다. **#9(구현)**: 우선순위 카드에 `movementLabel()` 배지와 함께 `change.reason` 실제 근거
  문장을 표시. **#10(구현)**: `PriorityScoreBreakdown` 타입 추가, 값이 있을 때 점수 구성을 펼쳐
  표시. **#32(구현, 이번에 새로 발견)**: `daily_briefing.py`의 `related_task_ids`가 Calendar는 항상
  빈 배열로 고정, Gmail은 필드 자체가 없어서 이미 등록한 회의·메일도 매번 새 항목처럼 보이던 문제를
  발견 — `task_repository.list()`로 실제 대조하도록 고치고 "등록됨" 배지 추가. **#33(제외)**: Calendar
  미등록 일정을 중요 신호에 포함하려면 "할 일 후보로 볼 만한가"를 새로 판정하는 로직이 필요해(제안함의
  Calendar 판정과 개념이 겹침) 결정 대기로 남김. **#34(제외)**: `data_freshness`가 계산은 되지만
  `WorkflowResult`에 담기지 않아 응답에 안 실리는 것을 확인했지만, `Briefing.tsx`가 이미 `warnings`
  기반으로 "최신/지연"을 대체 표시하고 있어 긴급도가 낮음을 확인 — 표시만. 백엔드 회귀
  **213 passed/10 skipped**(#32 회귀 테스트 포함), 프론트 eslint·build·npm test(29개) 전부 통과. 이
  과정에서 백엔드 서버 프로세스가 예기치 않게 내려가 있던 것도 발견해 재기동. 전체 우선순위 표에
  #32~#34 반영(29~31번), 구현완료보고서를 오늘 브리핑 섹션 말미에 추가.
- 2026-08-15: **📊 주간 업무보고 섹션 재분석·대체 및 구현** — 새로 작성된
  [15번 문서의 주간 업무보고 절](15-workmate-ui-screens-reference.md#-주간-업무보고-reporttsx)을
  기준으로 재확인, 기존 "이 화면 고유의 갭은 없음"이 틀렸음을 확인하고 4개(#35~#38) 발견. **#35(구현,
  신규 발견)**: `weeklyReportInput()`이 항상 이번 주만 조회해 지난주 보고서를 다시 볼 방법이 없었던
  것을 확인 — `week_of` 인자 추가, 이전/다음 주 이동 버튼 추가. **#36(구현, 신규 발견)**: 백엔드
  `extract_next_week_plans`/`validate_next_week_plans`가 계획을 `planned`/`carry_over`/`suggestion`
  으로 이미 정확히 분류해 보내는데(코드 확인 결과 03 §5 요구사항을 실제로 만족하고 있었음) 프론트가
  이 값을 안 읽고 있던 것을 발견 — `kind`별 배지 추가. **#37(제외, 신규 발견)**: `unresolved_issues`가
  `build_weekly_report_data()`에서 항상 빈 배열로 하드코딩돼 있고, 채우는 로직도 `app/domain/weekly.py`의
  `WeeklyBucket`에 "이슈"에 대응하는 분류 자체도 없다는 걸 확인 — "이슈"가 `delayed`(지연)와 뭐가
  다른지부터 결정 필요해 제외. **#38(제외, 신규 발견)**: `weekly_report.py`·`weekly_classification.py`가
  Task Repository만 조회하고 Meeting·MeetingChunk를 전혀 안 쓴다는 것을 확인 — 04 §2가 요구하는
  "주요 회의 내용 통합"이 코드에 전혀 없는 순수 설계 공백임을 확인, "주요"의 기준과 LLM 입력 설계가
  선행돼야 해 제외. 프론트 eslint·build·npm test(30개, 신규 `weekOf` 테스트 포함) 전부 통과, 백엔드
  코드 변경 없어 회귀만 재확인(213 passed/10 skipped, 변화 없음). 전체 우선순위 표에 #35~#38
  반영(32~35번), 구현완료보고서를 주간 업무보고 섹션 말미에 추가.
- 2026-08-16: **실사용 중 다섯 번째 버그 발견·수정** — #27 필터를 실제로 붙여 회의록 검색을 써보니
  `search_meetings`의 유일한 PostgreSQL 의존(`DATABASE_URL` 미설정 시 `_search_dependencies()`가
  `RuntimeError` 발생)이 `app/internal_chat.py`가 그때까지 잡던 `ValueError`와는 다른 예외 타입이라
  그대로 새 나가 다시 CORS 없는 500 → "Failed to fetch"로 보였다. `except RuntimeError`를 추가해
  코드베이스 전체의 "설정 미비" 관례(R2·psycopg 등)에 맞춰 503으로 변환. 이 화면이 SQLite가 아닌
  별도 PostgreSQL+pgvector를 요구한다는 사실 자체가 로컬 재기동 절차에서 계속 누락돼 있었다는 것도
  함께 확인 — 이번 세션용 Docker `pgvector/pgvector:pg16` 컨테이너를 새로 띄우고 마이그레이션 4개를
  적용해 `DATABASE_URL`을 재기동 절차에 포함, 실제 검색이 껍데기 오류 없이 동작하는 것까지 확인.
  회귀 테스트 추가, 백엔드 회귀 최종 **224 tests(214 passed, 10 skipped)**. 회의록 검색
  구현완료보고서 말미에 상세 기록.
- 2026-08-16: **실사용 중 여섯 번째 버그 발견·수정** — 위 다섯 번째 버그를 고치고 실제 로그인
  계정으로 다시 검색해보니 이번엔 `psycopg.errors.InvalidTextRepresentation: invalid input syntax
  for type uuid`가 또 다른 CORS 없는 500으로 샜다. 원인은 Postgres Migration 4개
  (`002`~`004`)가 `users.user_id`와 이를 참조하는 모든 FK 컬럼을 `uuid`로 잘못 선언해둔 것 — 실제
  `user_id`는 내부 발급 UUID가 아니라 Google OIDC `sub` Claim(큰 10진수 문자열)을 그대로 쓴다.
  SQLite 스키마는 처음부터 `TEXT`로 맞았지만 이 Postgres Migration만 어긋나 있었고, 이번 세션
  내내 모든 기능이 SQLite로만 동작해 `search_meetings`가 처음으로 Postgres를 실사용자로 두드릴
  때까지 드러나지 않았다. 4개 Migration 파일의 `user_id` 계열 컬럼을 전부 `uuid → text`로 정정(원본
  파일 직접 수정 — `_initialize()`가 매 기동 시 이 SQL을 그대로 재실행하는 구조라 안전),
  기존 계약 테스트 2개 갱신 + 신규 회귀 테스트 추가. 실제 로그인 `user_id`로 Workflow를 직접
  호출해 `state: completed` 확인. 부수적으로 "전체 테스트를 `DATABASE_URL` 켠 채로 돌리면 무관한
  테스트 12개가 함께 깨진다"는 것도 발견(공유 Postgres 상태 오염) — 회귀는 항상 `DATABASE_URL` 없이
  실행. 백엔드 회귀 최종 **225 tests(215 passed, 10 skipped)**. 회의록 검색 구현완료보고서 말미에
  상세 기록.
- 2026-08-16: **실사용 중 일곱 번째 버그 발견·수정** — 위 여섯 번째 버그를 고치고 나니 이번엔
  CORS도 정상, "Failed to fetch"도 아닌 진짜 검증 실패(`HTTP 422: meeting date is required for a
  cited source`)가 화면에 그대로 보였다(CORS·예외 처리 수정 두 개가 제대로 동작한다는 뜻이기도
  함). 원인은 `PostgresMeetingChunkRepository.create()`가 Chunk 저장 시 부모 `meetings` 행을
  항상 `title="회의"`·`started_at=NULL` 자리표시자로만 만들고 실제 회의 제목·시각을 받지도
  넘기지도 않았던 것 — `search_meetings`가 인용 출처에 날짜를 요구하는데, 실사용 회의는
  프론트(`Meeting.tsx`)가 `started_at`을 아예 안 보내 전부 `None`이었다. `MeetingChunkRecord`에
  `meeting_title`/`meeting_started_at`/`meeting_ended_at`을 추가하고 `_index_meeting_chunks()`가
  실제 `meeting`의 값(`started_at` 없으면 `created_at`)을 배선하도록 고쳤으며, `meetings` UPSERT를
  `ON CONFLICT DO UPDATE`로 바꿔 이전에 잘못 저장된 행도 재색인 시 자체 치유되게 했다. 로컬
  컨테이너의 기존 실사용자 행 2개는 SQLite 원본 `created_at`으로 직접 백필. 회귀 테스트
  추가(Spy 기반 배선 테스트 + Postgres 통합 테스트), 실제 질문으로 재현·확인. 백엔드 회귀 최종
  **227 tests** — `DATABASE_URL` 없이 216 passed/11 skipped, `WORKMATE_TEST_DATABASE_URL`로
  이전에 건너뛰던 Postgres 통합 테스트까지 포함해 227 passed/0 skipped 둘 다 확인. 회의록 검색
  구현완료보고서 말미에 상세 기록.
- 2026-08-16: **실사용 중 여덟 번째 버그 발견·수정(자체 유발 회귀)** — 주간 업무보고에서 LLM
  경고를 고쳤는데도 완료·진행·지연·미해결이 전부 0으로 뜨는 걸 보고, 데이터가 진짜 없는 게
  아니라 다섯 번째 버그를 고치며 재기동 절차에 넣은 `DATABASE_URL`이 원인일 가능성을 먼저
  의심했다 — 확인해보니 정확히 그랬다. `task_api.py`의 `/api/v1/tasks`와
  `daily_briefing.py`의 `_repositories()`(`weekly_report`가 재사용)가 `search_meetings`와
  똑같이 "`DATABASE_URL`이 있으면 무조건 Postgres" 규칙을 쓰고 있어서, `search_meetings`만
  고치려던 환경변수가 할 일 관리·오늘 브리핑·주간 업무보고 세 화면 전부의 Task 데이터 원본을
  실사용자 12건이 쌓인 SQLite에서 (테스트 fixture 10건만 있던) 로컬 Postgres로 조용히 바꿔버렸다
  — 크래시도 경고도 없이 그냥 0건으로 보였다. 이전 7건과 다른 완전히 새로운 종류의 버그이자, 내가
  직접 유발한 회귀였다. 데이터를 옮기는 과정에서 **여덟 번째의 일부로** `tasks.task_id`도 `uuid`로
  잘못 선언돼 있던 걸 추가로 발견(제안함 승인 Task는 `proposal-{source_type}-{source_id}` 형태의
  결정적 문자열 ID를 씀 — `user_id`와 같은 유형의 버그) — `002`·`003` Migration을 `text`로 정정하고
  나서야 실제 12건을 이전할 수 있었다. SQLite의 실제 Task 12건을 ID·상태·시각 그대로 보존해
  Postgres로 이전, `weekly_report`·`daily_briefing`·`task_api` 세 경로 모두 직접 호출해 11건이
  정상적으로 보이는 것(1건은 규칙상 정상 제외) 확인. 백엔드 회귀 최종 **228 tests** —
  `DATABASE_URL` 없이 217 passed/11 skipped, `WORKMATE_TEST_DATABASE_URL` 포함 228 passed/0
  skipped 둘 다 확인. "`DATABASE_URL`은 네 저장소(검색·Task·동기화·우선순위)를 한 번에 묶어
  전환한다"는 재발 방지 메모를 남김. 주간 업무보고 구현완료보고서 말미에 상세 기록.
- 2026-08-16: **실사용 중 아홉 번째 버그 발견·수정** — 오늘 브리핑 화면이 로딩도 오류도 없이
  "브리핑을 아직 실행하지 않았습니다"에 멈춰 있는 것을 발견, 서버 로그에서 정확히 그 시점 근처로
  같은 예외가 연달아 두 번(오늘 브리핑이 동시에 부르는 `daily_briefing`·`rank_priorities` 각각)
  찍힌 것을 확인했다: `app/internal_chat.py`의 `_authenticated_user()`가 인증되는 **모든**
  요청마다 `PyJWKClient(jwks_url)`을 새로 만들고 있어서, PyJWT의 내장 Key 캐시가 전혀 재사용되지
  못하고 요청마다 실제로 Google JWKS 엔드포인트에 네트워크 호출이 나가고 있었다 — 이번처럼
  `RemoteDisconnected` 한 번이면 바로 크래시하는 구조. 이 네트워크 예외는 `jwt.PyJWTError`가
  아니라 `except jwt.PyJWTError`가 못 잡았고, `_authenticated_user`는 Route 본문이 아니라
  Dependency 단계라 기존 `ValueError`/`RuntimeError` 처리(다섯·여섯 번째 버그)와도 다른, 아직
  방어되지 않은 새 경로였다 — CORS 없는 500이 됐고, 두 요청이 동시에 이 순간을 맞으면서 화면은
  로딩도 오류도 아닌 "아직 실행 안 함" 초기 상태에 그대로 멈춰 있었다. `PyJWKClient`를
  `jwks_url`별로 `@lru_cache`해 재사용(신뢰성·성능 동시 개선)하고, 남은 네트워크 실패도
  `except (URLError, OSError, TimeoutError)`로 잡아 CORS 헤더가 붙는 503으로 변환. 회귀 테스트
  추가. 백엔드 회귀 최종 **229 tests(218 passed, 11 skipped)**. 오늘 브리핑 구현완료보고서 말미에
  상세 기록.
- 2026-08-16: **실사용 중 열 번째 버그 발견·수정(진짜 원인)** — 아홉 번째 버그를 고치고
  재기동했는데도 오늘 브리핑이 여전히 "아직 실행 안 함"에 멈춰 있어 로그를 다시 보니, 이번엔
  `daily_briefing`·`rank_priorities` 요청 둘 다 **200으로 정상 완료**되고 있었다 — 아홉 번째
  수정은 실제로 효과가 있었지만, 화면이 멈춘 진짜 원인은 따로 있었던 것. `internal_chat.py`가
  HTTP 응답의 `artifact.data`로 그대로 내보내는 `WorkflowResult.data` 필드가
  `daily_briefing.py`·`priority.py`(`rank_priorities`) 두 Workflow에만 채워지지 않고
  있었다(`text=`만 채우고 `data=`가 빠짐) — `analyze_meeting`·`search_meetings`·`weekly_report`는
  전부 정상이었다. 프론트가 읽는 `response.artifact.data.data`가 항상 `null`이 되어, 요청이
  성공해도 화면은 `loading:false / error:null / data:null`인 초기 상태를 벗어나지 못했다. 기존
  테스트들이 `result.data`는 한 번도 assert하지 않고 `json.loads(result.text)`만 검증하고
  있었던 것이 이 버그가 오래 숨어 있었던 이유 — 이 세션의 여러 직접 검증 스크립트도 같은 이유로
  `text`를 파싱해 우회했을 뿐 `data` 필드가 비어 있다는 걸 알아채지 못했다(HTTP 계층에서만
  드러나는 결함). 두 곳에 `data=result_payload`를 추가해 다른 3개 Skill과 통일하고, 회귀 테스트
  추가, 실제 사용자 데이터로 재검증. 백엔드 재기동, 회귀 최종 **229 tests(218 passed, 11
  skipped, 변화 없이 통과)**. 오늘 브리핑 구현완료보고서 말미에 상세 기록.
