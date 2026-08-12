# A2A 인터페이스

[← 이전](01-overview-architecture.md) · [목차](README.md) · [다음: 데이터 규칙 →](03-data-priority-rules.md)

## 1. 기본 원칙

- A2A Protocol `1.0`과 공식 Python SDK를 사용한다.
- `/.well-known/agent-card.json`에서 Agent Card를 제공한다.
- Binding은 `HTTP+JSON` 하나만 지원한다. 엔드포인트는 일부 REST 스타일을 따른다.
- 브리핑·검색·우선순위는 같은 HTTP 응답에서 `TASK_STATE_COMPLETED` Task와 Artifact를 반환한다.
- STT처럼 오래 걸리는 작업은 `TASK_STATE_SUBMITTED` 또는 `TASK_STATE_WORKING` Task를 먼저 반환하고 Polling으로 조회한다.
- 진행 안내와 추가 입력 요청은 Message, 최종 산출물은 Artifact에 담는다.
- 시스템용 구조화 Data Part는 항상 제공하고, UI용 Markdown Text Part는 클라이언트가 `text/markdown`을 수락할 때 제공한다.
- A2A Protocol 버전, Workmate Agent 버전, Workmate Skill Schema 버전을 별도로 관리한다.
- A2A Protocol 버전은 Orchestrator와 합의한 버전으로 고정하고 한쪽만 변경하지 않는다.

### 1.1 완전한 Agent Card 예시

Interface URL은 배포 환경에서 Orchestrator가 접근 가능한 주소로 설정한다. 아래 예시는 Docker Compose 통합 환경이며, 외부 운영 환경에서는 HTTPS URL로 바꾼다. `securitySchemes`에는 인증 방법만 공개하며 실제 Token은 포함하지 않는다.

```json
{
  "name": "Workmate AI",
  "description": "메일, 캘린더, 회의록과 Task를 통합해 브리핑, 보고서, 회의 분석과 업무 우선순위를 제공하는 업무지원 Agent",
  "supportedInterfaces": [
    {
      "url": "http://workmate-agent:8001/a2a",
      "protocolBinding": "HTTP+JSON",
      "protocolVersion": "1.0"
    }
  ],
  "provider": {
    "organization": "Game Team",
    "url": "https://workmate.example.com"
  },
  "version": "1.0.0",
  "documentationUrl": "https://workmate.example.com/docs",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "extendedAgentCard": false
  },
  "securitySchemes": {
    "serviceBearer": {
      "httpAuthSecurityScheme": {
        "description": "Orchestrator와 Workmate 사이의 Service Token",
        "scheme": "Bearer",
        "bearerFormat": "opaque"
      }
    }
  },
  "securityRequirements": [
    {
      "schemes": {
        "serviceBearer": {
          "list": []
        }
      }
    }
  ],
  "defaultInputModes": ["application/json"],
  "defaultOutputModes": ["application/json", "text/markdown"],
  "skills": [
    {
      "id": "daily_briefing",
      "name": "오늘 업무 브리핑",
      "description": "오늘 일정, 미완료 업무, 중요 메일과 회의 맥락을 통합해 우선순위 Top 3를 포함한 브리핑을 생성한다.",
      "tags": ["briefing", "task", "calendar", "email"],
      "examples": ["오늘 브리핑 해줘"]
    },
    {
      "id": "weekly_report",
      "name": "주간 업무보고",
      "description": "이번 주 완료, 진행, 지연 업무와 회의 주요 내용, 미해결 이슈, 다음 주 계획을 정리한다.",
      "tags": ["weekly-report", "task", "meeting"],
      "examples": ["이번 주 보고서 정리해줘"]
    },
    {
      "id": "analyze_meeting",
      "name": "회의 분석",
      "description": "등록된 회의 녹음 또는 회의록을 분석해 주요 내용을 통합한 요약 Text와 Action Item 후보를 생성한다.",
      "tags": ["meeting", "stt", "action-item"],
      "examples": ["등록한 회의 녹음을 분석해줘"]
    },
    {
      "id": "search_meetings",
      "name": "이전 회의록 검색",
      "description": "과거 회의록에서 근거 문맥을 검색해 회의명, 날짜와 발화자가 포함된 답변을 생성한다.",
      "tags": ["meeting", "search", "rag"],
      "examples": ["빌드 일정은 어느 회의에서 결정됐어?"]
    },
    {
      "id": "rank_priorities",
      "name": "업무 우선순위 계산",
      "description": "최신 업무 신호를 기준으로 우선순위 Top 3와 직전 순위 대비 변경 사유를 계산한다.",
      "tags": ["priority", "task", "ranking"],
      "examples": ["우선순위를 다시 계산해줘"]
    }
  ]
}
```



Agent Card JSON은 구현 시 공식 A2A Python SDK 모델로 생성하고 검증한다. 공식 SDK 런타임 경계는 `workmate-agent/app/a2a/runtime.py`에 두고, 공개 `/a2a` Route는 SDK REST Handler와 `AgentExecutor`를 사용하도록 구현한다. 예시를 손으로 복사해 별도 전송 모델을 만들지 않는다. MVP 응답은 `Cache-Control: public, max-age=3600`을 제공하고 Orchestrator는 캐시 만료 후 다시 조회한다. 조건부 재검증 요구가 생기기 전에는 별도 `ETag` 계약을 추가하지 않는다.

## 2. 공개 Skill

### 2.1 Skill 목록

| Skill ID          | 입력 Schema           | 출력 `result.type` | 처리 방식                |
| ----------------- | --------------------- | ------------------ | ------------------------ |
| `daily_briefing`  | `DailyBriefingInput`  | `daily_briefing`   | 즉시 완료 Task           |
| `weekly_report`   | `WeeklyReportInput`   | `weekly_report`    | 즉시 완료 또는 장기 Task |
| `analyze_meeting` | `AnalyzeMeetingInput` | `meeting_analysis` | 장기 Task                |
| `search_meetings` | `SearchMeetingsInput` | `grounded_answer`  | 즉시 완료 Task           |
| `rank_priorities` | `RankPrioritiesInput` | `priority_ranking` | 즉시 완료 Task           |

“즉시 완료”는 Task를 사용하지 않는다는 뜻이 아니라, 첫 `SendMessage` 응답 안에 최종 Artifact가 포함된 `TASK_STATE_COMPLETED` Task를 반환한다는 뜻이다. `weekly_report`는 예상 처리시간이 HTTP timeout 기준을 넘을 때 장기 Task로 전환할 수 있다.

### 2.2 공통 입력 필드

모든 Skill 입력은 Message의 Data Part에 다음 공통 필드를 포함한다.

| 필드             | 타입   |            필수 | 규칙                                  |
| ---------------- | ------ | --------------: | ------------------------------------- |
| `schema_version` | string |               O | Workmate 요청 Schema 버전, 현재 `1.0` |
| `skill_id`       | string |               O | 공개 Skill ID 중 하나                 |
| `user_id`        | string |               O | 신뢰된 Orchestrator가 검증 후 전달한 사용자 ID |
| `timezone`       | string | 시간 기반 Skill | IANA timezone, 기본 `Asia/Seoul`      |
| `locale`         | string |               X | BCP 47 형식, 기본 `ko-KR`             |

### 2.3 Skill별 입력 Schema

#### `DailyBriefingInput`

```json
{
  "schema_version": "1.0",
  "skill_id": "daily_briefing",
  "user_id": "user-123",
  "timezone": "Asia/Seoul",
  "locale": "ko-KR",
  "as_of": "2026-08-02T09:00:00+09:00"
}
```

`as_of`는 ISO 8601 offset 포함 시각이며 생략하면 서버 수신 시각을 사용한다.

#### `WeeklyReportInput`

```json
{
  "schema_version": "1.0",
  "skill_id": "weekly_report",
  "user_id": "user-123",
  "timezone": "Asia/Seoul",
  "locale": "ko-KR",
  "week_of": "2026-07-29"
}
```

`week_of`는 `YYYY-MM-DD`이며 해당 날짜가 속한 ISO 주간을 조회한다. 생략하면 서버 수신일이 속한 주간을 사용한다.

#### `AnalyzeMeetingInput`

```json
{
  "schema_version": "1.0",
  "skill_id": "analyze_meeting",
  "user_id": "user-123",
  "timezone": "Asia/Seoul",
  "locale": "ko-KR",
  "meeting_id": "meeting-42"
}
```

`meeting_id`는 필수다. 녹음 Binary는 A2A Message에 넣지 않고 UI REST API로 먼저 업로드한다.

#### `SearchMeetingsInput`

```json
{
  "schema_version": "1.0",
  "skill_id": "search_meetings",
  "user_id": "user-123",
  "timezone": "Asia/Seoul",
  "locale": "ko-KR",
  "query": "빌드 일정은 어떻게 결정됐어?",
  "filters": {
    "date_from": "2026-07-01",
    "date_to": "2026-08-02",
    "meeting_ids": [],
    "participants": []
  },
  "limit": 5
}
```

`query`는 공백 제외 1~1000자다. `limit` 기본값은 5, 최대값은 20이다. 날짜는 양쪽 모두 포함하는 지역 날짜이며 내부에서 `[date_from 00:00, date_to 다음 날 00:00)`로 변환한다.

#### `RankPrioritiesInput`

```json
{
  "schema_version": "1.0",
  "skill_id": "rank_priorities",
  "user_id": "user-123",
  "timezone": "Asia/Seoul",
  "as_of": "2026-08-02T09:00:00+09:00",
  "compare_with_previous": true
}
```

`compare_with_previous` 기본값은 `true`다. 비교 가능한 이전 Snapshot이 없으면 변경 유형은 `entered`로 반환한다.

### 2.4 Skill별 출력 Schema

모든 Data Part는 공통 결과 Envelope를 사용하며 `result.type`과 `result.data`만 Skill별로 달라진다.

필드 타입, 필수값, `null`, Enum, 배열 Item과 추가 필드 허용 여부의 정식 계약은 [Workmate Skill JSON Schema](schemas/workmate-skill-schemas.schema.json)를 따른다. 아래 표와 JSON은 읽기 쉬운 요약 예시이며 Schema와 충돌하면 Schema가 우선한다.

| `result.type`      | `result.data` 필수 필드                                                                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `daily_briefing`   | `date`, `summary`, `calendar_events`, `important_signals`, `priorities`, `source_refs`                                         |
| `weekly_report`    | `period`, `summary`, `completed`, `in_progress`, `delayed`, `unresolved_issues`, `next_week_plans`, `source_refs` |
| `meeting_analysis` | `meeting_id`, `summary`, `action_items`, `transcript_ref`, `source_refs`                                         |
| `grounded_answer`  | `answer`, `sources`, `insufficient_evidence`                                                                                   |
| `priority_ranking` | `calculated_at`, `priorities`, `changes`, `source_refs`                                                                        |

우선순위 항목의 공통 형태:

```json
{
  "rank": 1,
  "task_id": "task-101",
  "title": "QA 서버에 신규 빌드 배포",
  "score": 80,
  "score_breakdown": {
    "deadline": 35,
    "importance": 15,
    "blocked_or_overdue": 10,
    "meeting_commitment": 10,
    "calendar_relevance": 10
  },
  "reasons": ["오늘 마감", "확정된 회의 Action Item"]
}
```

회의 검색 출처의 공통 형태:

```json
{
  "meeting_id": "meeting-42",
  "meeting_title": "8월 개발 일정 회의",
  "meeting_date": "2026-08-01",
  "speaker": "김개발",
  "meeting_chunk_id": "chunk-4207",
  "quote": "8월 5일까지 QA 서버에 배포합니다."
}
```

## 3. 공통 요청

공통 요청 JSON은 A2A 최상위 객체가 아니라 `SendMessageRequest.message.parts[].data`에 들어가는 Workmate 전용 Payload다. `skill_id`도 A2A 표준 필드가 아니라 Workmate가 명시적 라우팅에 사용하는 필드다.

### 3.1 A2A SendMessage Envelope

```http
POST /a2a/message:send HTTP/1.1
Authorization: Bearer <service-token>
Content-Type: application/a2a+json
A2A-Version: 1.0
traceparent: 00-<trace-id>-<span-id>-01
```

```json
{
  "message": {
    "messageId": "msg-6bb4e5b8",
    "role": "ROLE_USER",
    "parts": [
      {
        "data": {
          "schema_version": "1.0",
          "skill_id": "daily_briefing",
          "user_id": "user-123",
          "timezone": "Asia/Seoul",
          "as_of": "2026-08-02T09:00:00+09:00",
          "locale": "ko-KR"
        },
        "mediaType": "application/json"
      }
    ]
  },
  "configuration": {
    "acceptedOutputModes": ["application/json", "text/markdown"]
  },
  "metadata": {
    "request_id": "req-8f73c2a1"
  }
}
```

식별자 책임:

| 식별자        | 생성 주체             | 용도                     |
| ------------- | --------------------- | ------------------------ |
| `messageId`   | Message 발신자        | Message 중복 감지        |
| `task.id`     | Workmate              | 작업 상태와 결과 조회    |
| `contextId`   | Workmate              | 관련 Message와 Task 묶기 |
| `request_id`  | 요청 최초 진입 서비스 | 로그 상관관계            |
| `traceparent` | 분산 추적 계층        | 서비스 간 Trace 전파     |

`request_id`가 없으면 Workmate가 생성한다. 커스텀 `trace_id` JSON 필드를 추가하지 않고 W3C `traceparent` 헤더를 사용한다.

### 3.2 기존 Task에 추가 입력

Action Item 승인이나 누락값 보완은 새 Message를 같은 Task와 Context에 연결한다.

```json
{
  "message": {
    "messageId": "msg-approval-001",
    "taskId": "a2a-task-789",
    "contextId": "context-456",
    "role": "ROLE_USER",
    "parts": [
      {
        "data": {
          "action": "approve_action_items",
          "approvals": [
            {
              "action_item_id": "action-1",
              "decision": "approve"
            }
          ]
        },
        "mediaType": "application/json"
      }
    ]
  },
  "metadata": {
    "request_id": "req-approval-001"
  }
}
```

## 4. 공통 결과

### 4.1 완료 Task와 Artifact Envelope

짧은 작업은 첫 응답에서 다음과 같은 완료 Task를 반환한다.

```http
HTTP/1.1 200 OK
Content-Type: application/a2a+json
```

```json
{
  "task": {
    "id": "a2a-task-123",
    "contextId": "context-123",
    "createdAt": "2026-08-02T00:00:00.000Z",
    "lastModified": "2026-08-02T00:00:03.000Z",
    "status": {
      "state": "TASK_STATE_COMPLETED",
      "timestamp": "2026-08-02T00:00:03Z"
    },
    "artifacts": [
      {
        "artifactId": "artifact-daily-briefing-123",
        "name": "오늘의 브리핑",
        "description": "2026-08-02 업무 브리핑과 우선순위 Top 3",
        "parts": [
          {
            "text": "# 오늘의 브리핑\n\n## 중요 우선순위 Top 3\n1. QA 서버 빌드 배포 — 85점\n2. 로그인 오류 수정 — 70점\n3. 전투 밸런스 검토 자료 준비 — 55점",
            "mediaType": "text/markdown"
          },
          {
            "data": {
              "schema_version": "1.0",
              "request_id": "req-8f73c2a1",
              "generated_at": "2026-08-02T09:00:03+09:00",
              "data_freshness": {
                "task": "2026-08-02T08:59:30+09:00",
                "calendar": "2026-08-02T08:58:10+09:00",
                "email": "2026-08-02T08:57:42+09:00",
                "meeting": "2026-08-01T18:10:00+09:00"
              },
              "warnings": [],
              "result": {
                "type": "daily_briefing",
                "data": {
                  "date": "2026-08-02",
                  "summary": "QA 서버 배포와 로그인 오류 대응이 가장 중요합니다.",
                  "calendar_events": [],
                  "important_signals": [],
                  "priorities": [
                    {
                      "rank": 1,
                      "task_id": "task-101",
                      "title": "QA 서버 빌드 배포",
                      "score": 85,
                      "reasons": ["오늘 마감", "QA 점검 회의와 관련"]
                    },
                    {
                      "rank": 2,
                      "task_id": "task-102",
                      "title": "로그인 오류 수정",
                      "score": 70,
                      "reasons": ["QA팀 긴급 요청", "테스트 업무 차단"]
                    },
                    {
                      "rank": 3,
                      "task_id": "task-103",
                      "title": "전투 밸런스 검토 자료 준비",
                      "score": 55,
                      "reasons": ["오늘 리뷰 회의 전에 필요", "승인된 회의 후속업무"]
                    }
                  ],
                  "source_refs": ["task-101", "task-102", "task-103"]
                }
              }
            },
            "mediaType": "application/json"
          }
        ]
      }
    ]
  }
}
```

구조화 Data Part를 원본으로 삼고 같은 결과에서 Markdown Text Part를 생성한다. 서로 다른 LLM 호출로 두 표현을 따로 만들지 않는다. Data Part는 항상 반환하며 Text Part는 `acceptedOutputModes`에 `text/markdown`이 있을 때만 추가한다. `application/json`을 수락하지 않는 요청은 `CONTENT_TYPE_NOT_SUPPORTED`로 거절한다.

### 4.2 장기 Task 최초 응답

```json
{
  "task": {
    "id": "a2a-task-789",
    "contextId": "context-456",
    "createdAt": "2026-08-02T00:10:00.000Z",
    "lastModified": "2026-08-02T00:10:00.000Z",
    "status": {
      "state": "TASK_STATE_SUBMITTED",
      "timestamp": "2026-08-02T00:10:00Z",
      "message": {
        "messageId": "msg-status-001",
        "role": "ROLE_AGENT",
        "parts": [
          {
            "text": "회의 분석 요청을 접수했습니다.",
            "mediaType": "text/plain"
          }
        ]
      }
    }
  }
}
```

Orchestrator는 `GET /a2a/tasks/{id}`로 상태를 Polling하며 완료 시 `artifacts`를 읽는다.

### 4.3 Warning Schema

```json
{
  "source": "calendar",
  "code": "SOURCE_UNAVAILABLE",
  "message": "캘린더 데이터를 조회하지 못했습니다.",
  "retryable": true,
  "last_success_at": "2026-08-02T08:30:00+09:00"
}
```

Warning은 일부 결과를 만들 수 있을 때 사용한다. 결과의 핵심 데이터가 없으면 Warning으로 숨기지 않고 Task를 실패 처리한다.

### 4.4 Error Schema

A2A 요청 형식, 인증, Task 조회 같은 Protocol 오류는 HTTP 오류 응답을 사용한다.

```json
{
  "error": {
    "code": 404,
    "status": "NOT_FOUND",
    "message": "Task를 찾을 수 없거나 접근 권한이 없습니다.",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "TASK_NOT_FOUND",
        "domain": "a2a-protocol.org",
        "metadata": {
          "request_id": "req-8f73c2a1",
          "task_id": "a2a-task-missing",
          "retryable": false
        }
      }
    ]
  }
}
```

실행 도중 업무 오류가 발생하면 Task를 `TASK_STATE_FAILED`로 전환하고 상태 Message의 Data Part에 다음을 담는다.

```json
{
  "code": "STT_PROVIDER_UNAVAILABLE",
  "message": "음성 변환 서비스를 사용할 수 없습니다.",
  "retryable": true,
  "request_id": "req-8f73c2a1"
}
```

내부 Stack Trace, SQL, Provider 원문과 Secret은 외부 오류에 포함하지 않는다.

### 4.5 Artifact Schema 계약

Workmate MVP의 Artifact는 다음 규칙을 고정한다.

- `artifactId`, `name`, `description`, `parts`는 필수다.
- `parts`는 하나 이상의 Text Part 또는 Data Part를 포함한다.
- Text Part는 `text/markdown` 또는 `text/plain`만 사용한다.
- Data Part는 `application/json`만 사용하며 Workmate Skill Result Envelope를 담는다.
- 구조화 Data Part를 원본으로 삼고 Markdown Part는 같은 결과에서 렌더링한다.
- MVP에서는 Artifact 부분 추가(`append`), Chunk 종료 플래그(`lastChunk`), Binary·URL Part를 사용하지 않는다.
- `artifactId`는 Task 안에서 유일해야 하며, 재시도 시 같은 결과를 재사용한다.

정식 JSON Schema는 [a2a-artifact.schema.json](schemas/a2a-artifact.schema.json)이다. Protocol 객체 검증과 Skill Data 검증을 분리하며, Schema 오류는 `SCHEMA_VALIDATION_FAILED`로 처리한다.

### 4.6 버전 규칙

| 버전                   | 위치                                    | 의미                        |
| ---------------------- | --------------------------------------- | --------------------------- |
| A2A Protocol `1.0`     | `supportedInterfaces[].protocolVersion` | 통신 객체와 Operation 규격  |
| A2A Python SDK `1.1.2` | `pyproject.toml`·lockfile                | Workmate HTTP+JSON 서버 구현 |
| Workmate Agent `1.0.0` | Agent Card `version`                    | Workmate 배포 기능 버전     |
| Workmate Skill Schema `1.0` | Data Part `schema_version`         | Skill 입력·출력 데이터 규격 |

Workmate Skill Schema의 호환 필드 추가는 minor, 필드 제거·의미 변경은 major 변경으로 본다. 새로운 major Schema는 Orchestrator 계약 테스트가 준비되기 전까지 기존 major와 병행하거나 배포하지 않는다. 구현 시 `a2a-sdk[http-server]==1.1.2`를 정확히 고정하고 lockfile을 커밋한다. SDK 변경은 Agent Card·REST·Streaming·Task Contract Test 통과 후에만 허용한다.

## 5. 내부 API

### 5.1 A2A HTTP+JSON 경계

Docker Compose 통합 환경에서 Agent Card의 Interface Base URL은 `http://workmate-agent:8001/a2a`이다. 외부 운영 환경에서는 Orchestrator가 접근할 수 있는 HTTPS URL을 사용한다. 실제 Operation은 다음과 같다.

| Method | 전체 Path                      | 용도                                           |
| ------ | ------------------------------ | ---------------------------------------------- |
| GET    | `/.well-known/agent-card.json` | 공개 Agent Card 조회                           |
| POST   | `/a2a/message:send`             | 새 Message 전송, Task 생성 또는 기존 Task 재개 |
| POST   | `/a2a/message:stream`           | SSE Streaming Message 전송                    |
| GET    | `/a2a/tasks/{id}`               | Task 상태와 Artifact 조회                      |
| POST   | `/a2a/tasks/{id}:cancel`        | 실행 중 Task 취소                              |
| POST   | `/a2a/tasks/{id}:subscribe`     | Task 이벤트 SSE 구독                          |

MVP에서는 공식 SDK REST Route가 제공하는 A2A `/message:stream`과 Task Subscribe를 사용한다. Task Subscribe의 정식 계약은 A2A 1.0 HTTP+JSON 표준에 맞춘 `POST`이며, SDK 1.1.2가 호환 목적으로 제공하는 `GET` Route는 공개 계약에 포함하지 않는다. Push Notification, gRPC, JSON-RPC Binding은 제공하지 않는다. 회의 실시간 녹음·임시 자막은 A2A와 별도의 UI WebSocket이며, 회의 분석 결과는 A2A Task로 확인한다.

SDK 1.1.2의 REST Route 생성기는 `GET /tasks`, Push Notification 설정, Extended Agent Card, Tenant Mount도 만들 수 있다. Workmate는 Route 객체를 생성한 뒤 위 표의 MVP 허용 목록만 등록한다. 허용 목록 밖의 SDK Route는 외부에 노출하지 않으며 Contract Test에서 `404` 또는 `405`를 확인한다. Agent Card의 `pushNotifications=false`, `extendedAgentCard=false`와 실제 Route 노출 범위는 항상 일치시킨다.

오케스트레이터와 Workmate 사이의 필드·상태 차이는 Workmate 입구 Adapter에서 변환한다. `workspace_id`는 공개 Workmate Skill Schema에 추가하지 않고 사용자 범위 검증 후 입력에서 제거한다. 외부 상태 `queued/running/succeeded/failed/cancelled`는 각각 `TASK_STATE_SUBMITTED/WORKING/COMPLETED/FAILED/CANCELED`로 매핑하며, 변환 실패는 Task 생성 전 HTTP 400으로 반환한다.

Adapter Contract Test는 다음을 고정한다.

| 검증 항목 | 기대 결과 |
| --- | --- |
| `Authorization: Bearer ...` 누락·불일치 | Task 생성 전 HTTP 401 |
| `A2A-Version: 1.0`과 `application/a2a+json` | 공식 SDK HTTP+JSON Route에서 정상 처리 |
| 필수 `application/json` 출력 미수락 | `CONTENT_TYPE_NOT_SUPPORTED` |
| `text/markdown` 선택 수락 | 동일한 구조화 결과에서 Markdown Part 추가 |
| `workspace_id` | 인증된 사용자 범위 검증 후 내부 Skill 입력에서 제거 |
| `messageId`, `request_id`, `user_id` | 변환 전후 값 보존 |
| `queued/running/succeeded/failed/cancelled` | 정의된 A2A Task 상태로 일대일 매핑 |
| 알 수 없는 상태·필드 변환 실패 | Task 생성 전 HTTP 400 |
| Orchestrator 오류 | `code`, HTTP 상태, 메시지, 요청 식별자 보존 |

### 5.1.1 런타임 구현 범위와 테스트 영향

구현 목표는 공개 `/a2a` 경로에서 공식 SDK REST Handler와 `AgentExecutor`를 직접 사용하는 것이다. A2A 전송 계층은 SDK의 `SendMessageRequest`, `Task`, `Artifact`, SSE Streaming 응답을 사용하고, 업무 도메인·내부 UI API의 Pydantic 모델은 유지한다. SDK 런타임 경계는 `workmate-agent/app/a2a/runtime.py`에 두며, M0.1-01·02에서 이 전송 경계를 구현·검증했다. M0.1-03에서는 `skill_id → Workflow Registry`와 A2A Task·Message 멱등성·Artifact·`task_id ↔ thread_id`·Checkpoint 영속 경계를 연결한다.

- 실제 Workflow 연결 시 `AgentExecutor`는 공통 `skill_id`, `user_id`, `request_id`를 전송 계층과 독립적인 요청 객체로 변환하고 `skill_id → Workflow` Registry를 호출한다. Workflow 결과는 공통 Artifact 변환기에서 SDK `Task`·`Artifact`로 직렬화한다.
- 현재 5개 Skill은 Registry를 통과하는 런타임 준비 Workflow로 연결되어 있으나 업무 결과를 생성하지 않는다. Task·Gmail·Calendar·회의·검색·우선순위 실제 Workflow는 마일스톤 순서에 따라 연결한다.
- 구현 이후에도 A2A Route와 Executor에는 Provider 호출, SQL, 우선순위 계산 같은 업무 규칙을 작성하지 않는다. 실제 Workflow가 Repository·Provider·Domain 함수를 조합한다.
- Contract Test와 Smoke Test는 Agent Card의 `Cache-Control`, SDK REST 요청·응답, Artifact, 인증, Adapter 상태·오류 매핑과 5개 Skill을 검증한다. `/message:stream`은 첫 이벤트가 Task이고 이후 상태·Artifact 순서가 유지되는지 확인한다. 활성 Task의 `POST` Subscribe는 현재 Task 스냅샷부터 신규 이벤트를 전달해야 하고, Terminal Task Subscribe는 정의된 SDK 오류를 반환해야 한다. 비허용 `GET` Subscribe와 나머지 허용 목록 밖 Route는 `404` 또는 `405`여야 한다.
- 구현 후 SDK 표준 응답은 `SendMessageResponse`의 `task` 필드를 사용한다. Task 조회·취소 응답은 SDK REST 규격에 따라 Task 객체를 직접 반환하며, 완료 Task 취소는 `400 Task cannot be canceled`로 처리한다.
- Push Notification은 저장소·발송기가 연결되지 않아 계속 비활성화한다. Agent Card의 `pushNotifications`는 `false`로 유지한다.
- 업무 기능 완료와 SDK 런타임 검증을 분리하지 않고, M0.1은 SDK Route와 계약 테스트가 통과한 상태에서 검수한다. Workflow 경계 구현과 각 Skill의 실제 연결은 해당 백로그·마일스톤에서 검증한다.
- 승인 Schema는 `additionalProperties: false`이므로 공개 Artifact에 `mock`, `received` 같은 Mock 전용 필드를 추가하지 않는다. Mock Shell과 테스트 Fixture도 5개 Skill별 정식 Result Envelope를 생성해 Schema를 통과해야 하며, Mock 여부와 입력 Echo는 테스트 로그·Fixture 이름·증빙 메타데이터에만 기록한다. Schema를 통과하지 않는 기존 Mock 응답은 M0.1 승인 증빙으로 사용할 수 없다.
- M0 완료 후 운영 Profile은 Legacy Mock Handler를 등록하지 않는다. 아직 해당 마일스톤이 완료되지 않은 업무 Workflow는 성공한 고정 결과 대신 명시적인 미구현 오류를 반환하고, Mock·Fake는 테스트 Profile의 Fixture로만 사용한다.

### 5.2 Workmate UI REST API

| Method | Path                                                | 용도                          |
| ------ | --------------------------------------------------- | ----------------------------- |
| POST   | `/api/v1/meetings`                                  | 회의 메타데이터 생성          |
| GET    | `/api/v1/meetings`                                  | 회의 목록 조회                |
| GET    | `/api/v1/meetings/{id}`                             | 회의 기본정보와 요약 조회     |
| GET    | `/api/v1/meetings/{id}/transcript`                  | 전체 회의록 Chunk 조회        |
| POST   | `/api/v1/meetings/{id}/recordings`                  | 녹음 파일 업로드              |
| POST   | `/api/v1/meetings/{id}/recording-sessions`          | 실시간 녹음 세션 시작         |
| WS     | `/api/v1/meetings/{id}/recording-stream`            | 음성 Chunk 전송과 임시 STT 수신 |
| POST   | `/api/v1/meetings/{id}/recording-sessions/{session_id}:complete` | 실시간 녹음 종료와 원본 음성 확정 |
| POST   | `/api/v1/meetings/{id}/analysis`                    | 회의 분석 시작                |
| GET    | `/api/v1/meetings/{id}/analysis`                    | 분석 Task 상태와 결과 조회    |
| POST   | `/api/v1/meetings/{id}/actions:review`              | Action Item 승인·수정·거절 반영 |
| POST   | `/api/v1/meetings/search`                           | Workmate UI의 회의 검색       |
| GET    | `/api/v1/tasks`                                     | 할 일 목록 조회와 조건 검색   |
| POST   | `/api/v1/tasks`                                     | 사용자가 할 일 직접 등록      |
| GET    | `/api/v1/tasks/{id}`                                | 할 일 상세 조회               |
| PATCH  | `/api/v1/tasks/{id}`                                | 할 일 내용 또는 상태 수정     |
| DELETE | `/api/v1/tasks/{id}`                                | 할 일 Soft Delete             |
| GET    | `/api/v1/notifications/stream`                      | Gmail 할 일 제안 SSE 수신     |
| POST   | `/api/v1/email-task-proposals:review`               | 임시 메일 제안 승인·무시      |
| POST   | `/api/v1/calendar-task-proposals:review`            | 임시 일정 제안 승인·무시      |
| GET    | `/api/v1/internal/skill-chat/skills`               | 내부 검증 챗봇의 5개 Skill 목록 |
| POST   | `/api/v1/internal/skill-chat/messages`             | 내부 검증 챗봇 메시지 전송과 Skill 실행 |
| GET    | `/api/v1/internal/skill-chat/tasks/{id}`           | 내부 검증 Task 상태와 Artifact 조회 |
| GET    | `/health/live`                                      | API Process 생존 확인         |
| GET    | `/health/ready`                                     | DB와 Migration 준비 상태 확인 |

회의 생성과 녹음 입력을 분리한다. 사용자는 완성된 파일을 업로드하거나 실시간 녹음 세션을 시작할 수 있으며, 두 방식 모두 원본 음성이 확정된 뒤 같은 `analyze_meeting` Workflow를 호출한다. 파일은 `multipart/form-data`, 실시간 음성 Chunk는 WebSocket, 나머지는 JSON을 사용한다.

내부 검증 챗봇 API는 `WORKMATE_INTERNAL_CHAT_ENABLED=true`일 때만 노출한다. `skills` 조회는 Agent Card의 공개 Skill 목록과 동일한 5개를 반환하며, 메시지 요청은 선택한 `skill_id`와 자연어 또는 Schema JSON 입력을 받아 같은 Workflow를 호출한다. 응답은 Markdown·구조화 JSON·Task 상태를 함께 제공하고, 장기 Task는 전용 조회 경로로 Polling한다. 이 경로는 A2A Service Token을 사용하지 않고 UI Session/OIDC 인증을 사용한다.

할 일 등록은 `title`, `assignee_user_id`를 필수로 받고 `due_at`, `priority_hint`를 선택적으로 받는다. 서버는 `status=todo`, `source_type=manual`, `source_id=null`을 설정한다. 수정은 전달된 필드만 변경하며, 삭제는 `deleted_at`을 기록한다. 삭제된 Task는 기본 목록·브리핑·보고서·우선순위에서 제외한다.

메일 제안은 DB에 저장하지 않는다. SSE Event는 Gmail `message_id`와 LLM이 제안한 Task 필드를 전달한다. 검토 요청은 `message_id`, `decision`, 수정된 `task`를 받으며 `decision`은 `approve`, `ignore` 중 하나다. 승인 시 `source_type=email`, `source_id=message_id`인 Task를 생성하고 무시 시 아무 데이터도 저장하지 않는다.

```json
{
  "message_id": "gmail-message-123",
  "decision": "approve",
  "task": {
    "title": "QA 결과 회신",
    "assignee_user_id": "user-123",
    "due_at": "2026-08-08T18:00:00+09:00"
  }
}
```

일일 브리핑은 별도 배열을 추가하지 않고 기존 `important_signals`를 사용한다. Email 항목의 `source_id`는 Gmail `message.id`이며 `related_task_ids`가 비어 있으면 미등록, 값이 있으면 이미 등록된 Task다. Gmail은 사용자 지역 시각 기준 `[직전 영업일 00:00, as_of)` 범위를 조회한다.

`daily_briefing`은 Gmail을 실시간 조회하지만 `rank_priorities`는 Gmail을 조회하지 않는다. 메일 제안 승인 시 `due_at`, `priority_hint`, `source_type=email`, `source_id=message_id`를 Task에 저장하고 이후 우선순위 계산은 저장된 Task 값을 사용한다.

Calendar 제안은 Google Calendar Event를 DB에 저장하지 않고 SSE 또는 브리핑 응답에서만 제공한다. Calendar 항목의 `source_id`는 `{calendar_id}:{event_id}`이고 `related_task_ids`가 비어 있으면 미등록, 값이 있으면 이미 등록된 Task다. 승인 시 `source_type=calendar`, `source_id={calendar_id}:{event_id}`를 Task에 저장한다.

메일과 Calendar 제안은 같은 중복 검사 함수를 사용한다. 동일 `(source_type, source_id)`가 있으면 기존 Task를 반환한다. 제목·담당자·마감일이 유사한 Task가 있으면 `409 SIMILAR_TASK_EXISTS`와 기존 Task 목록을 반환하고, 사용자가 재확인한 요청의 `allow_similar_duplicate=true`일 때만 별도 Task 생성을 허용한다. 저장 직전에 다시 검사하며 모든 승인 POST는 `Idempotency-Key`를 사용한다.

### 5.2.1 Google Calendar Webhook

| Method | Path | 용도 |
| --- | --- | --- |
| POST | `/webhooks/google-calendar` | Google Calendar 변경 알림 수신 |

Webhook은 `X-Goog-Channel-ID`, `X-Goog-Channel-Token`, `X-Goog-Resource-ID`를 `SourceSyncState`와 대조한다. 검증에 성공하면 즉시 `204 No Content`를 반환하고, 해당 사용자의 Calendar 증분 동기화를 비동기로 시작한다. Webhook 본문에는 일정 내용이 없으므로 Task 제안은 `events.list(syncToken=...)` 조회 후 생성한다.

### 5.3 A2A와 UI API의 책임

```text
A2A Endpoint ─┐
              ├→ 동일한 LangGraph Workflow와 Domain 함수
UI REST API ──┘
```

- A2A와 UI Route에 업무 규칙을 중복 구현하지 않는다.
- A2A Endpoint는 Protocol 객체와 Workmate Skill Schema를 검증하고 Artifact로 변환한다.
- UI API는 파일 업로드, 화면용 조회와 승인 입력을 HTTP 요청으로 변환한다.
- UI API는 실시간 녹음 연결과 임시 STT 자막도 처리하며, 녹음 종료 후 최종 분석은 `analyze_meeting` Workflow에 위임한다.
- A2A API는 Orchestrator의 Bearer Service Token, UI API는 사용자 Session 또는 OIDC로 인증한다.
- 두 경로는 인증수단은 분리하되 동일한 사용자 권한 검사 함수·Repository·Workflow를 사용한다.
- UI 회의 검색도 `search_meetings` Workflow를 호출한다.
- UI 회의 분석도 `analyze_meeting` Workflow를 호출하고 같은 Task 저장소를 사용한다.

Action Item 검토 요청은 후보 여러 개를 한 번에 처리한다.

```json
{
  "decisions": [
    {
      "action_item_id": "action-1",
      "decision": "edit",
      "changes": {
        "assignee_user_id": "user-456",
        "due_at": "2026-08-07T18:00:00+09:00"
      }
    },
    {
      "action_item_id": "action-2",
      "decision": "reject"
    }
  ]
}
```

`decision`은 `approve`, `edit`, `reject` 중 하나다. `edit`일 때만 `changes`를 허용한다. 브라우저에는 Service Token을 전달하지 않는다. `/health/live`와 `/health/ready`는 내부 네트워크 또는 배포 플랫폼에서만 접근하도록 제한한다.

`meeting_analysis.action_items[]`에는 `evidence_span`과 `evidence_text`가 포함된다. `evidence_text`는 서버가 최종 회의록에서 추출한 읽기 전용 원문이므로 Action Item 검토 API의 `changes`에서 변경할 수 없다. UI의 `회의록에서 보기`는 `evidence_span`을 사용한다.

Action Item 전용 조회 화면과 조회 API는 제공하지 않는다. 승인 후에는 Task 상세에서 근거를 조회한다. `source_type=action_item`인 Task의 상세 응답은 DB 컬럼을 추가하지 않고 `Task → ActionItem → Meeting`을 조인해 다음 `meeting_evidence`를 구성한다.

```json
{
  "meeting_evidence": {
    "meeting_id": "meeting-123",
    "meeting_title": "기획 리뷰 회의",
    "evidence_text": "금요일까지 QA 빌드를 배포하겠습니다.",
    "evidence_span": {
      "meeting_chunk_ids": ["chunk-456"],
      "start_ms": 932000,
      "end_ms": 936000
    }
  }
}
```

`GET /api/v1/meetings/{id}/transcript`는 Cursor Pagination을 사용하며 `around_meeting_chunk_id`가 있으면 해당 Chunk와 앞뒤 문맥을 우선 반환한다. 서버는 `end_ms >= start_ms`와 모든 `meeting_chunk_ids`가 같은 Meeting에 속하는지 검증한다.

## 6. 장기 작업 상태

### 6.1 Task 상태 정의

| A2A 상태                    | 의미                               | 다음 상태                                                            |
| --------------------------- | ---------------------------------- | -------------------------------------------------------------------- |
| `TASK_STATE_SUBMITTED`      | 요청 접수 및 실행 대기             | `WORKING`, `CANCELED`, `REJECTED`                                    |
| `TASK_STATE_WORKING`        | STT, LLM 또는 저장 처리 중         | `INPUT_REQUIRED`, `AUTH_REQUIRED`, `COMPLETED`, `FAILED`, `CANCELED` |
| `TASK_STATE_INPUT_REQUIRED` | 사용자 확인·수정·승인 대기         | `WORKING`, `CANCELED`                                                |
| `TASK_STATE_AUTH_REQUIRED`  | 외부 Provider 재인증 필요          | `WORKING`, `FAILED`, `CANCELED`                                      |
| `TASK_STATE_COMPLETED`      | Artifact 생성 완료                 | 없음                                                                 |
| `TASK_STATE_FAILED`         | 복구하지 못한 오류                 | 없음                                                                 |
| `TASK_STATE_CANCELED`       | 사용자 또는 시스템 취소            | 없음                                                                 |
| `TASK_STATE_REJECTED`       | 권한, 지원 범위 또는 정책으로 거절 | 없음                                                                 |

`COMPLETED`, `FAILED`, `CANCELED`, `REJECTED`는 Terminal 상태다. Terminal Task를 재시작하지 않고 새로운 Message로 새 Task를 생성한다.

### 6.1.1 Task Store와 재시작 복구

- 외부 A2A Task 상태·Message 멱등성 Key·Artifact·`task_id ↔ thread_id` 매핑은 M0.1에서 생성하는 A2A 인프라 PostgreSQL Migration과 Task Store가 소유한다. 공개 이벤트 전체 이력은 MVP에서 별도 저장하지 않는다. M1.1의 업무 DB Migration과 책임을 구분한다.
- LangGraph Checkpoint는 Workflow 내부 State와 `thread_id` 재개 지점을 저장한다. Task Store와 Checkpoint는 `task.id ↔ thread_id` 매핑으로 연결하되 같은 저장 책임으로 합치지 않는다.
- SDK의 프로세스 메모리 Active Task는 실행 중 전달에만 사용하고 완료 판정의 원장으로 사용하지 않는다.
- 서버 시작 시 `SUBMITTED`, `WORKING`, `INPUT_REQUIRED`, `AUTH_REQUIRED` Task를 조회한다. 안전하게 재개 가능한 Task는 같은 멱등성 Key와 Checkpoint로 재개하고, 재개할 수 없는 Task는 원인을 기록한 뒤 `FAILED`로 전환한다.
- 취소 요청은 먼저 Task Store에 기록하고 실행 중인 Provider·Workflow에 전파한다. Terminal Task 취소는 거절하며 재시작 후에도 취소 상태가 유지되어야 한다.
- Subscribe는 연결 시 저장된 현재 Task 스냅샷을 먼저 전송하고 그 뒤 연결 이후 발생한 신규 이벤트를 Streaming한다. 연결 종료 자체는 Task 취소로 간주하지 않는다. 과거 이벤트 재생이 필요해질 때에만 이벤트 순번·재생 Cursor·중복 규칙·보존기간을 별도 계약으로 추가한다.
- Task·Message 멱등성·Artifact 기록은 최소 7일 보존하며, 복구·취소·중복 요청과 연결 이후 이벤트 순서 테스트를 M0.1-03과 M0.1-04에서 검증한다.

### 6.2 회의 분석 상태 흐름

```text
SUBMITTED
→ WORKING(STT)
→ WORKING(LLM 분석)
→ INPUT_REQUIRED(Action Item 검토)
→ WORKING(Task 등록)
→ COMPLETED

실패: WORKING → FAILED
취소: SUBMITTED/WORKING/INPUT_REQUIRED → CANCELED
재인증: WORKING → AUTH_REQUIRED → WORKING
```

Task 상태 Message에는 사용자에게 공개 가능한 현재 단계만 기록한다. 세부 진행률을 정확히 계산할 수 없으면 임의의 백분율을 제공하지 않는다.

### 6.3 Retry 계약

| 대상                | 재시도 조건        | 최대 | 비고                                  |
| ------------------- | ------------------ | ---: | ------------------------------------- |
| DB 읽기             | 일시적 연결 오류   |  2회 | 짧은 지수 Backoff                     |
| 메일·캘린더 읽기    | timeout, 429, 5xx  |  2회 | `Retry-After` 우선                    |
| LLM                 | timeout, 429, 5xx  |  2회 | 같은 요청 ID 유지                     |
| LLM Schema 검증     | 구조화 출력 불일치 |  1회 | 수정 프롬프트 사용                    |
| STT                 | timeout, 429, 5xx  |  1회 | Provider Job ID 재사용 가능 시 재사용 |
| 인증·권한·입력 오류 | 재시도 안 함       |  0회 | Task 생성 전 HTTP 400/401/403 반환    |
| DB 쓰기             | 자동 반복하지 않음 |  0회 | 멱등성 Key와 Transaction으로 보호     |

Orchestrator와 Workmate가 중복으로 재시도하지 않도록, A2A HTTP 요청 재시도는 Orchestrator가 담당하고 Workmate는 Node 내부 Provider 호출만 위 표대로 재시도한다. Orchestrator는 timeout, 429, 502, 503, 504만 같은 `messageId`로 재시도하며 `Retry-After`가 있으면 우선한다. 그 밖의 4xx는 재시도하지 않는다.

### 6.4 Timeout 계약

| 작업            | 기준                                               |
| --------------- | -------------------------------------------------- |
| 즉시 A2A 요청   | Workflow 전체 실행 예산 15초, Gateway timeout보다 짧게 설정 |
| DB Query        | 5초                                                |
| 메일·캘린더 API | 요청당 10초                                        |
| LLM             | 요청당 60초                                        |
| STT             | HTTP 연결에서 대기하지 않고 장기 Task로 처리       |
| UI 녹음 파일 업로드 | 별도 업로드 timeout과 파일 크기 제한 적용       |
| 실시간 녹음 WebSocket | 연결 유휴 timeout 적용, 재연결 허용            |

즉시 Workflow는 DB·Provider·LLM 호출을 모두 포함해 15초 예산을 공유한다. 남은 예산 안에 완료할 수 없으면 실행을 계속 기다리지 않고 장기 Task로 전환해 현재 Task를 반환한다. 장기 Task로 전환된 뒤에만 LLM의 요청당 60초 timeout을 전부 사용할 수 있다.

### 6.5 멱등성 계약

| 작업             | 멱등성 Key                        | 동작                                          |
| ---------------- | --------------------------------- | --------------------------------------------- |
| A2A Message 처리 | `messageId`                       | 같은 ID 재수신 시 기존 Message 처리 결과 반환 |
| 회의 생성        | `Idempotency-Key` Header          | 같은 Key로 Meeting 중복 생성 금지             |
| 녹음 업로드      | `meeting_id + file_hash`          | 동일 파일 중복 저장·STT 방지                  |
| 실시간 음성 Chunk | `recording_session_id + chunk_no` | 재연결·재전송 시 동일 Chunk 중복 저장 방지    |
| 회의 분석 시작   | `meeting_id + transcript_version` | 같은 입력의 활성 Task 재사용                  |
| Action Item 승인 | `action_item_id` Unique           | 같은 Task 중복 등록 금지                      |
| LangGraph 재개   | `taskId + messageId`              | 동일 승인 Message 중복 적용 금지              |

UI POST의 `Idempotency-Key` 기록은 최소 24시간, A2A `messageId`는 Task 보존기간 동안 유지한다. Action Item과 생성된 Task의 연결 정보는 업무 데이터 보존기간 동안 유지한다. 동일 Key에 다른 Payload가 들어오면 `409 Conflict`를 반환한다.

### 6.6 Polling 계약

- Orchestrator는 Task를 2초 후 처음 조회하고 최대 10초까지 지수 Backoff한다.
- 응답에 `Retry-After`가 있으면 해당 값을 우선한다.
- `COMPLETED`, `FAILED`, `CANCELED`, `REJECTED`에서 Polling을 종료한다.
- `INPUT_REQUIRED`, `AUTH_REQUIRED`에서는 자동 Polling 빈도를 낮추고 사용자 조치를 기다린다.
- Task 보존기간은 최소 7일이며, 기간이 지난 Task는 `TASK_NOT_FOUND`로 응답할 수 있다.

### 6.7 실패와 부분 성공

- 일부 소스만 실패하고 결과 생성이 가능하면 Task는 완료하고 `warnings`에 기록한다.
- 핵심 입력이 없거나 결과 신뢰성을 보장할 수 없으면 Task를 실패 처리한다.
- `search_meetings`에서 근거가 없는 것은 시스템 장애가 아니므로 `COMPLETED`로 반환하고 `insufficient_evidence: true`로 표시한다.
- 사용자 승인 대기는 실패가 아니라 `INPUT_REQUIRED`다.
- OAuth 만료로 사용자 조치가 필요하면 `AUTH_REQUIRED`다.
- `REJECTED`는 형식과 인증이 정상인 요청을 지원 범위나 Agent 정책 때문에 수행하지 않기로 결정한 경우에만 사용한다.
- 오류 응답과 로그는 `request_id`, Task는 `task.id`, 분산 추적은 `traceparent`로 연결한다.

## 공식 참고자료

- [A2A Protocol 최신 규격](https://a2a-protocol.org/latest/specification)
- [A2A 핵심 개념](https://a2a-protocol.org/latest/topics/key-concepts/)
- [A2A Agent 발견](https://a2a-protocol.org/latest/topics/agent-discovery/)
- [A2A 공식 Python SDK](https://github.com/a2aproject/a2a-python)
