# Workmate UI 설계

[← 개발 및 검증 계획](06-delivery-plan.md) · [목차](README.md)

이 문서의 화면 요구사항은 두 구현 표면에 나누어 적용한다. `workmate-agent`의 최소 개발자 페이지는 M0.4에서 5개 Skill·Schema·Workflow만 검증한다. 사용자가 실제로 이용하는 다섯 개 제품 화면은 M5에서 팀 공통 Orchestrator UI에 통합한다.

`workmate-ui`는 1차로 이 문서 기준까지 완성하고, 완성본은 개인용으로 보관한다. 2차로 완성된 화면·로직을 팀 공통 Orchestrator UI 양식에 맞게 조정해 M5 통합에 반영한다 — 처음부터 새로 만드는 대신 완성본을 이식하는 방식이다. `workmate-ui`의 D1·Drizzle 예제는 여전히 선택형 starter 예제일 뿐 구현·검수 대상이 아니며, Task·Meeting 등 업무 데이터의 원장은 Workmate PostgreSQL이다.

## 1. 화면 구성

| 화면 | 주요 기능 |
| --- | --- |
| 홈/브리핑 | 오늘 일정, 메일 할 일 신호, 중요 신호, 우선순위 Top 3, 새로고침 |
| 할 일 관리 | 목록 조회, 등록, 수정, 상태 변경, 삭제 |
| 주간 보고서 | 기간별 보고서 조회와 Markdown 복사 |
| 회의 관리 | 실시간 녹음·파일 업로드, 회의 목록, 전체 회의록과 선택 근거 강조 |
| 회의 검색 | 질문 입력, 근거 기반 답변과 출처 확인 |
| Skill 검증 챗봇 | `workmate-agent` 최소 개발자 페이지에서 Workmate Skill 직접 실행, Markdown·JSON·Task 상태 확인(2026-08-17 이전 5개 / 현재 11개, §6 참고) |

## 2. 할 일 관리 화면

### 2.1 목록

목록에는 제목, 상태, 마감일, 중요도와 수정·삭제 버튼을 표시한다. 기본 조회에서는 삭제된 Task를 제외한다.
담당자는 항상 로그인한 본인이라 별도 표시하지 않는다(아래 담당자 관련 정정 참고).

최소 필터:

- 상태
- 마감일

### 2.2 등록·수정 폼

등록과 수정은 같은 폼을 사용한다.

| 필드 | 등록 규칙 |
| --- | --- |
| 제목 | 필수 |
| 마감일 | 선택 |
| 중요도 | 선택 |
| 상태 | 등록 시 `todo`, 수정 시 변경 가능 |

등록 시 서버가 `source_type=manual`, `source_id=null`, `assignee_user_id=요청 사용자 본인`을 설정하며
UI는 이 세 필드를 입력받지 않는다.

> **정정(2026-08-15)**: 이전 버전은 "담당자" 필터·입력 필드를 요구했다. Workmate MVP에는 팀원 목록·
> 초대·권한 관리 기능이 없고 모든 Task가 이미 요청 사용자 본인 범위로만 조회돼, 담당자는 항상 값이
> 하나뿐이라 입력·필터 둘 다 의미가 없다 — 실제 구현(서버가 항상 본인으로 강제 설정)에 맞춰 문서를
> 고쳤다(`14-workmate-ui-integration-gaps.md` #6). 팀 배정이 실사용에서 필요해지면 별도 기능으로
> 다시 설계한다.

### 2.3 삭제

삭제 버튼을 누르면 Task 제목이 포함된 확인창을 표시한다. 확인 후 `DELETE /api/v1/tasks/{id}`를 호출한다. 성공하면 목록에서 제거하고 브리핑과 우선순위 재조회 시 포함하지 않는다.

DB 행은 Soft Delete로 보존하지만 복구와 삭제 목록 화면은 MVP에서 제공하지 않는다.

## 3. UI 상태

- 저장 중에는 중복 제출을 막는다.
- 입력 오류는 해당 필드 가까이에 표시한다.
- API 실패 시 기존 입력을 유지하고 재시도할 수 있게 한다.
- 삭제 성공 후 목록이 비면 빈 상태 안내를 표시한다.

## 4. Gmail 할 일 제안

- 브라우저는 `GET /api/v1/notifications/stream`으로 SSE 알림을 받는다.
- 팝업에는 메일 제목, 제안된 Task 제목·담당자·마감일과 `할 일 추가`, `무시` 버튼을 표시한다.
- 사용자는 승인 전에 Task 필드를 수정할 수 있다.
- 승인은 `POST /api/v1/email-task-proposals:review`를 호출하고 같은 Gmail `message.id`로 생성된 Task가 있으면 기존 Task를 표시한다.
- 무시한 제안의 본문(제목·스니펫 등)은 저장하지 않지만, "이미 무시했다"는 사실(ID·시각)은 별도
  저장소(`ignored_proposals`)에 남겨 이후 동기화에서 다시 노출되지 않는다 — **영구 제외**된다
  (2026-08-16 결정, 99번 문서 18번 항목 참고. 정정 전에는 이 문서가 "무시한 제안은 저장하지 않는다"
  고만 적어, 다시 노출될 수 있다는 옛 동작을 암시하고 있었다).
- 브라우저가 닫혀 있으면 팝업을 보내지 않는다 — 이건 **아직 검토하지 않은** 제안이 놓치는 경우라
  위의 "무시(ignore)한 제안"과는 다르다. 놓친 제안은 다음 브리핑·제안함에서 다시 표시될 수 있다.
- 브리핑에서는 기존 `important_signals`의 `related_task_ids`로 `이미 등록됨` 또는 `미등록`을 표시한다.

## 5. 회의 관리와 할 일 근거

### 5.1 회의 생성과 녹음

- 사용자는 `실시간 녹음` 또는 `녹음 파일 업로드` 중 하나를 선택한다.
- 실시간 녹음에서는 녹음 시간, 연결 상태, 시작·일시정지·종료 버튼과 임시 STT 자막을 표시한다.
- 연결이 끊기면 마지막 전송 Chunk 다음부터 재연결하고, 종료 후에는 최종 STT와 분석 진행 상태를 표시한다.
- 파일 업로드에서는 형식과 크기를 검증하고 `multipart/form-data`로 Workmate 서버에 파일을 올린다. 서버가 받은 파일을 R2에 저장한 뒤 같은 분석 진행 화면으로 이동한다. 브라우저에는 R2 API Key나 Presigned URL을 전달하지 않는다(2026-08-15 결정, `workmate-ui-integration-gaps.md` #14).

### 5.2 회의 목록

- 제목, 일시, 참석자, 분석 상태와 요약 일부를 표시한다.
- 제목·날짜·분석 상태로 필터링한다.
- 회의를 선택하면 `/meetings/{meeting_id}` 전체 회의록 화면으로 이동한다.

### 5.3 전체 회의록

- 회의 기본정보와 전체 MeetingChunk를 발화 시각·발화자 순서로 표시한다.
- 회의록 내 검색과 Cursor Pagination을 제공한다.
- `highlight_meeting_chunk_id`가 있으면 해당 Chunk로 자동 스크롤하고 근거 라인을 강조한다.

### 5.4 할 일의 회의 근거

- `source_type=action_item`인 할 일 상세에 읽기 전용 `evidence_text`와 `회의록에서 보기`를 표시한다.
- 근거 문장을 누르면 `/meetings/{meeting_id}?highlight_meeting_chunk_id={meeting_chunk_id}`로 이동한다.
- 전체 회의록 화면은 선택된 근거 라인을 강조하고 `할 일로 돌아가기`를 제공한다.
- Action Item 전용 조회 화면은 만들지 않는다. 회의 분석 직후 승인·수정·거절을 위한 임시 검토 UI만 유지한다.

## 6. Workmate 내부 Skill 검증 챗봇

Orchestrator 연결 전에 Workmate의 모든 공개 Skill을 화면에서 직접 호출해 결과를 확인한다. 이 화면은 `WORKMATE_INTERNAL_CHAT_ENABLED`가 `true`일 때만 노출한다.

> **갱신(2026-08-24, 99번 문서 정합성 검증)**: "교육용 통합 환경의 검증·시연용"이라는 원래 성격
> 규정은 2026-08-17 이후 더는 정확하지 않다 — `workmate-ui`의 💬 Workmate 어시스턴트(Drawer,
> 15·18번 문서)가 이 절과 같은 백엔드 API(`/api/v1/internal/skill-chat/*`, 같은
> `WORKMATE_INTERNAL_CHAT_ENABLED` 게이팅)를 최종 사용자 프로덕션 기능으로 재사용한다 — 자세한
> 내용은 07 §5.4 갱신 각주 참고. 아래 §6.1 "Skill 선택"은 여전히 **이 문서가 정의하는 개발자용
> 검증 화면**(`/internal/skill-chat`)만 가리킨다 — Drawer 자체는 2026-08-17 이후 Skill 선택
> 드롭다운을 없애고 순수 채팅 UI로 바뀌었다(15번 문서 "💬 Workmate 어시스턴트" 절 참고). 대상
> Skill 개수도 이 절 작성 시점엔 5개였지만 지금은 11개다(07 §5.4 참고).

### 6.1 입력

- Skill 선택: `daily_briefing`, `weekly_report`, `analyze_meeting`, `search_meetings`, `rank_priorities`
  (+ 2026-08-17 이후 `get_meeting_analysis`, `review_action_items`, `review_proposal`,
  `manage_tasks`, `read_email`, `assistant_ask` — 총 11개, 07 §5.4 참고)
- 자연어 질문 입력
- 필요하면 Schema JSON 입력 모드로 전환해 정확한 Skill Payload를 전송
- 전송 중 중복 제출 방지와 `request_id` 표시

### 6.2 결과

- 채팅 메시지와 함께 Markdown 결과 표시
- 구조화 JSON Artifact 펼쳐보기
- `TASK_STATE_*`, 경고, 오류 코드, 처리 시간과 출처 표시
- 장기 Task는 진행 상태를 Polling하고 완료 Artifact를 같은 대화에 추가
- 회의 분석의 Action Item 승인·거절은 기존 검토 UI와 동일한 Human-in-the-loop를 사용

### 6.3 경계와 보안

- 챗봇은 Orchestrator와 A2A 통신하지 않고 Workmate 내부 Workflow를 직접 호출한다.
- A2A Service Token과 R2 Secret은 브라우저에 전달하지 않는다.
- UI는 사용자 Session/OIDC로 인증하고, 기능 Flag가 꺼져 있으면 API와 화면 모두 `404` 또는 `403`으로 차단한다.
- 챗봇은 별도 업무 규칙을 구현하지 않으며 기존 Repository·Workflow·Artifact Schema를 재사용한다.

## 7. Calendar 할 일 제안

- 실시간 Calendar 제안은 기존 `/api/v1/notifications/stream` SSE 연결로 표시한다.
- 아침 브리핑의 미등록 Calendar `important_signals`에도 `할 일 추가`를 표시한다.
- 추가 요청 전에 제목·담당자·마감일·중요도를 수정할 수 있다.
- 동일 Calendar 원본의 Task가 있으면 `이미 등록됨`과 `기존 할 일 보기`를 표시한다.
- 유사 Task가 있으면 기존 Task 정보를 보여주고 `계속 추가`, `기존 할 일 보기`, `취소`를 제공한다.
- 사용자가 `계속 추가`를 선택한 경우에만 `allow_similar_duplicate=true`로 다시 요청한다.
