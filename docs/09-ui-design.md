# Workmate UI 설계

[← 개발 및 검증 계획](06-delivery-plan.md) · [목차](README.md)

이 문서의 화면 요구사항은 두 구현 표면에 나누어 적용한다. `workmate-agent`의 최소 개발자 페이지는 M0.4에서 5개 Skill·Schema·Workflow만 검증한다. 사용자가 실제로 이용하는 다섯 개 제품 화면은 M5에서 팀 공통 Orchestrator UI에 통합한다. 폐기된 `workmate-ui-demo`와 그 D1·Drizzle 예제는 구현·검수에 사용하지 않으며, Task·Meeting 등 업무 데이터의 원장은 Workmate PostgreSQL이다.

## 1. 화면 구성

| 화면 | 주요 기능 |
| --- | --- |
| 홈/브리핑 | 오늘 일정, 메일 할 일 신호, 중요 신호, 우선순위 Top 3, 새로고침 |
| 할 일 관리 | 목록 조회, 등록, 수정, 상태 변경, 삭제 |
| 주간 보고서 | 기간별 보고서 조회와 Markdown 복사 |
| 회의 관리 | 실시간 녹음·파일 업로드, 회의 목록, 전체 회의록과 선택 근거 강조 |
| 회의 검색 | 질문 입력, 근거 기반 답변과 출처 확인 |
| Skill 검증 챗봇 | `workmate-agent` 최소 개발자 페이지에서 5개 Workmate Skill 직접 실행, Markdown·JSON·Task 상태 확인 |

## 2. 할 일 관리 화면

### 2.1 목록

목록에는 제목, 담당자, 상태, 마감일, 중요도와 수정·삭제 버튼을 표시한다. 기본 조회에서는 삭제된 Task를 제외한다.

최소 필터:

- 상태
- 담당자
- 마감일

### 2.2 등록·수정 폼

등록과 수정은 같은 폼을 사용한다.

| 필드 | 등록 규칙 |
| --- | --- |
| 제목 | 필수 |
| 담당자 | 필수 |
| 마감일 | 선택 |
| 중요도 | 선택 |
| 상태 | 등록 시 `todo`, 수정 시 변경 가능 |

등록 시 서버가 `source_type=manual`, `source_id=null`을 설정하며 UI는 두 필드를 입력받지 않는다.

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
- 무시한 제안은 저장하지 않는다.
- 브라우저가 닫혀 있으면 팝업을 보내지 않으며 다음 브리핑에서 같은 후보가 다시 표시될 수 있다.
- 브리핑에서는 기존 `important_signals`의 `related_task_ids`로 `이미 등록됨` 또는 `미등록`을 표시한다.

## 5. 회의 관리와 할 일 근거

### 5.1 회의 생성과 녹음

- 사용자는 `실시간 녹음` 또는 `녹음 파일 업로드` 중 하나를 선택한다.
- 실시간 녹음에서는 녹음 시간, 연결 상태, 시작·일시정지·종료 버튼과 임시 STT 자막을 표시한다.
- 연결이 끊기면 마지막 전송 Chunk 다음부터 재연결하고, 종료 후에는 최종 STT와 분석 진행 상태를 표시한다.
- 파일 업로드에서는 형식과 크기를 검증하고 Workmate가 발급한 Presigned URL로 R2에 직접 업로드한 뒤 같은 분석 진행 화면으로 이동한다. 브라우저에는 R2 API Key를 전달하지 않는다.

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

Orchestrator 연결 전에 Workmate의 모든 공개 Skill을 화면에서 직접 호출해 결과를 확인한다. 이 화면은 교육용 통합 환경의 검증·시연용이며 `WORKMATE_INTERNAL_CHAT_ENABLED`가 `true`일 때만 노출한다.

### 6.1 입력

- Skill 선택: `daily_briefing`, `weekly_report`, `analyze_meeting`, `search_meetings`, `rank_priorities`
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
