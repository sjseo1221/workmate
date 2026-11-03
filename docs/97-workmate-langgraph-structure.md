# Workmate LangGraph 구조 도식

작성일: 2026-08-24  
목적: `docs/`의 설계, 시나리오, 구현 계획, 검수 증빙을 종합해 Workmate의 목표 LangGraph 구조와 현재 운영 Workflow Runtime을 한 문서에서 구분해 설명한다.

## 1. 먼저 구분할 것: 목표 Graph와 현재 Runtime

Workmate는 **LangGraph형 State·분기·Checkpoint·Interrupt 구조로 설계**됐다. 다만 현재
`workmate-agent` 운영 코드는 `langgraph` 패키지나 `StateGraph`를 실행하지 않고,
`WorkflowRegistry`가 `skill_id`를 비동기 Python Handler로 연결하는 경량 Runtime이다.

따라서 현재 상태를 정확히 표현하면 다음과 같다.

| 구분 | 현재 구현 | 목표 구조 |
| --- | --- | --- |
| Skill 라우팅 | `WorkflowRegistry`의 `skill_id → handler` 매핑 | `StateGraph` 조건부 Edge |
| Workflow 실행 | Skill별 비동기 Python Workflow | Skill별 Subgraph/Node |
| 공통 State | `WorkflowRequest`·`WorkflowResult` 및 Skill별 모델 | `WorkmateState` TypedDict |
| 장기 Task | A2A Task Store와 Polling/Subscribe | Graph 실행과 Task 상태 연동 |
| Checkpoint | `thread_id`와 Checkpoint JSON 저장 경계 구현 | LangGraph Checkpointer 직접 연결 |
| 사용자 승인 | API/UI의 확인 후 재요청 | `interrupt` 후 동일 `thread_id` 재개 |

> 발표나 문서에서는 “LangGraph로 구현 완료”가 아니라 **“LangGraph형 Workflow 구조로 설계했고,
> 현재는 A2A Registry 기반 경량 Runtime으로 구현했다”**고 표현한다.

## 2. 문서 종합 기준

- 기술 구조와 목표 Graph: [07-technical-specification.md](07-technical-specification.md)
- Skill·A2A Task·멱등성·Polling 계약: [02-a2a-interface.md](02-a2a-interface.md)
- 업무별 데이터 흐름: [04-scenarios.md](04-scenarios.md)
- 날짜·점수·중복·근거 규칙: [03-data-priority-rules.md](03-data-priority-rules.md)
- AI 책임과 실패 처리: [05-ai-security-operations.md](05-ai-security-operations.md)
- 모델·검색·STT 구현 기준: [10-embedding-evaluation-plan.md](10-embedding-evaluation-plan.md), [11-llm-evaluation-plan.md](11-llm-evaluation-plan.md), [12-implementation-verification-guide.md](12-implementation-verification-guide.md)
- Assistant·Human-in-the-loop: [18-workmate-assistant-implementation-plan.md](18-workmate-assistant-implementation-plan.md)
- 현재 구현 정합성 감사: [99-workmate-ppt-content.md](99-workmate-ppt-content.md)
- 완료 여부와 실행 증빙: [06-delivery-plan.md](06-delivery-plan.md), `docs/evidence/`

18번 문서에는 2026-08-17 당시 “공개 5개 + 내부 전용 6개”라는 기록이 남아 있다. 이후 2026-08-24
정합성 검증이 반영된 01·02·07·99번 문서는 현재 Agent Card와 내부 Skill 목록을 모두 **11개**로
정리한다. 이 문서는 더 최신인 2026-08-24 기준을 사용한다.

## 3. 전체 요청·실행 구조

```mermaid
flowchart LR
    U[사용자] --> UI[Workmate UI / Assistant Drawer]
    O[Team Orchestrator] --> A2A[A2A 1.0 HTTP+JSON]
    UI --> REST[UI REST / Internal Skill Chat]

    A2A --> AUTH[인증·Schema·user_id 검증]
    REST --> AUTH
    AUTH --> REG{WorkflowRegistry<br/>skill_id 분기}

    REG --> CORE[핵심 업무 Skill 5개]
    REG --> AUX[보조 Skill 5개]
    REG --> ASK[assistant_ask Meta Skill]

    CORE --> WF[Skill별 Workflow Handler]
    AUX --> WF
    ASK -->|나머지 10개 중 선택| WF

    WF --> DOMAIN[Domain 규칙<br/>날짜·점수·중복·근거 검증]
    WF --> REPO[Repositories]
    WF --> PROVIDER[Provider Clients]

    REPO --> PG[(PostgreSQL + pgvector)]
    PROVIDER --> GOOGLE[Gmail / Calendar]
    PROVIDER --> AI[LLM / Embedding / STT]
    PROVIDER --> R2[Cloudflare R2]

    DOMAIN --> RESULT[WorkflowResult]
    PG --> RESULT
    GOOGLE --> RESULT
    AI --> RESULT
    R2 --> RESULT

    RESULT --> STORE[(A2A Task Store<br/>Task·Artifact·Checkpoint)]
    STORE --> OUT[Typed DataPart + Markdown<br/>warnings + Task state]
    OUT --> UI
    OUT --> O
```

두 진입 경로는 인증 방식만 다르다. Orchestrator는 A2A Service Token을, UI는 Session/OIDC를 사용하지만
같은 Registry·Workflow·Repository·Domain 함수를 호출하며 모든 조회에 `user_id` 범위를 적용한다.

## 4. 현재 Workflow Runtime

현재 실행 경로에는 최상위 `StateGraph`가 없다. 요청을 받은 Runtime이 영속 Task 경계를 연 뒤 Registry를
호출하고, Handler 결과를 공통 Artifact로 변환한다.

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant R as A2A/UI Runtime
    participant T as Persistent Task Store
    participant G as WorkflowRegistry
    participant W as Skill Handler
    participant P as Repository/Provider

    C->>R: skill_id, payload, user_id, message_id
    R->>R: 인증·입력 Schema 검증
    R->>T: message_id 멱등성 확인
    alt 이미 처리한 동일 Message
        T-->>R: 기존 Task Snapshot/Artifact
        R-->>C: 기존 결과 재사용
    else 새 Message
        R->>T: SUBMITTED Task + task_id↔thread_id 저장
        R->>G: WorkflowRequest
        G->>W: skill_id에 등록된 async handler 호출
        W->>P: DB·Provider·Domain 작업
        P-->>W: 데이터 또는 부분 실패
        W-->>G: WorkflowResult(data, markdown, warnings)
        G-->>R: WorkflowResult
        R->>T: 상태·Artifact·Checkpoint JSON 저장
        R-->>C: Task + Artifact
    end
```

### 현재 11개 Skill 분기

```mermaid
flowchart TB
    R{WorkflowRegistry}

    subgraph C[핵심 업무 Skill]
        D[daily_briefing]
        P[rank_priorities]
        W[weekly_report]
        A[analyze_meeting]
        S[search_meetings]
    end

    subgraph X[업무 보조 Skill]
        GM[get_meeting_analysis]
        RA[review_action_items]
        RP[review_proposal]
        MT[manage_tasks]
        RE[read_email]
    end

    AA[assistant_ask<br/>자연어 Meta Skill]

    R --> D
    R --> P
    R --> W
    R --> A
    R --> S
    R --> GM
    R --> RA
    R --> RP
    R --> MT
    R --> RE
    R --> AA
    AA -. route + arguments .-> D
    AA -.-> P
    AA -.-> W
    AA -.-> A
    AA -.-> S
    AA -.-> GM
    AA -.-> RA
    AA -.-> RP
    AA -.-> MT
    AA -.-> RE
```

`assistant_ask`는 요청 전에 실제 하위 Skill을 알 수 없고 `analyze_meeting`으로 분기할 수도 있으므로 항상
비동기 Task/Polling 경로를 사용한다.

## 5. 목표 LangGraph

### 5.1 최상위 Graph

```mermaid
flowchart LR
    START([START]) --> V[Validate Request]
    V --> R{Route skill_id}

    R -->|daily_briefing| D[Daily Briefing Subgraph]
    R -->|rank_priorities| P[Priority Subgraph]
    R -->|weekly_report| W[Weekly Report Subgraph]
    R -->|analyze_meeting| M[Meeting Analysis Subgraph]
    R -->|search_meetings| S[Meeting Search Subgraph]
    R -->|5개 보조 Skill| X[Assistant Skill Subgraph]
    R -->|assistant_ask| A[Assistant Router Subgraph]

    D --> C[Contract·Grounding 검증]
    P --> C
    W --> C
    M --> C
    S --> C
    X --> C
    A --> C
    C --> B[Build Artifact]
    B --> END([END])
```

### 5.2 공통 State

```mermaid
classDiagram
    class WorkmateState {
        +str request_id
        +str task_id
        +str thread_id
        +str message_id
        +str user_id
        +str skill_id
        +dict input
        +datetime now
        +str timezone
        +dict source_data
        +list normalized_items
        +list warnings
        +dict result
        +str markdown
        +dict error
    }

    class WarningState {
        +str source
        +str code
        +str message
        +bool retryable
        +str last_success_at
    }

    WorkmateState "1" *-- "0..*" WarningState
```

State의 핵심 불변식은 다음과 같다.

- `user_id`는 모든 Repository 조회와 Provider 결과 결합에 유지한다.
- 날짜 범위는 사용자 timezone과 `as_of`를 기준으로 코드가 계산한다.
- 우선순위 순위·점수·근거 ID는 LLM이 생성하거나 변경하지 않는다.
- Provider 일부 실패는 사용 가능한 결과를 버리지 않고 `warnings`에 기록한다.
- Secret, Token, Presigned URL, 원본 개인정보는 State나 Artifact에 노출하지 않는다.

## 6. 핵심 Skill Subgraph

### 6.1 `daily_briefing`과 `rank_priorities`

```mermaid
flowchart LR
    DB0([daily_briefing]) --> COL[Task·Calendar·Gmail·Meeting 조회]
    COL --> N[정규화·중복 제거]
    N --> PR[결정적 Priority 계산]
    PR --> SUM[고정 템플릿 Summary 조합]
    SUM --> DBA[DailyBriefing Artifact]

    RP0([rank_priorities]) --> TASK[(미완료 Task 조회)]
    TASK --> SCORE[결정적 점수 계산]
    SCORE --> SNAP[(직전 Priority Snapshot 비교)]
    SNAP --> WHY[변동 이유 생성]
    WHY --> RPA[PriorityRanking Artifact]

    G[Gmail] -. daily_briefing만 호출 .-> COL
    G -.-> NOTE[rank_priorities에서는 미호출]
```

`daily_briefing.summary`는 LLM 요약이 아니라 조회 건수를 이용한 결정적 템플릿 조합이다.
`rank_priorities`는 Gmail을 직접 조회하지 않고 승인되어 Task DB에 저장된 미완료 Task만 순위 후보로 쓴다.

### 6.2 `weekly_report`

```mermaid
flowchart LR
    S([weekly_report]) --> RANGE[ISO 주간 범위 계산]
    RANGE --> LOAD[승인 Task·회의 근거 조회]
    LOAD --> CLASS[완료·진행·지연 분류]
    CLASS --> PLAN[명시된 다음 주 계획 추출]
    PLAN --> LLM[LLM summary 문장화]
    LLM --> KEEP[분류·plan kind·source_refs 보존]
    KEEP --> VALID[Schema·근거 검증]
    VALID --> OUT[JSON DataPart + Markdown]

    LLM -->|Provider 실패| PART[Source-backed 부분 결과 + warning]
    PART --> OUT
```

LLM은 `summary`를 문장화하지만 Workflow가 만든 분류, 계획 종류, `source_refs`를 바꿀 수 없다.

### 6.3 `analyze_meeting`

```mermaid
flowchart LR
    S([analyze_meeting]) --> AUTH[회의 소유권 검증]
    AUTH --> T{최종 Transcript 존재?}
    T -->|아니오| AUDIO{R2 원본 음성 존재?}
    AUDIO -->|아니오| FAIL[FAILED: 분석 입력 없음]
    AUDIO -->|예| STT[STT → 최종 Transcript 저장]
    T -->|예| LLM[LLM 회의 분석]
    STT --> LLM
    LLM --> EX[요약·Action Item 후보 추출]
    EX --> EV{evidence_text가<br/>Transcript 연속 문자열인가?}
    EV -->|아니오| FAIL2[근거 없는 후보 차단]
    EV -->|예| SAVE[분석·후보 저장]
    SAVE --> IDX[Chunk → Embedding → pgvector 색인]
    IDX -->|성공| DONE[MeetingAnalysis Artifact]
    IDX -->|실패| WARN[분석 보존 + retryable warning]
    WARN --> DONE
```

실시간 녹음의 Partial 자막은 UI 표시용이며 분석 원장이 아니다. 녹음 종료 후 확정한 최종 Transcript만
LLM 분석과 근거 검증에 사용한다. Action Item의 Task 등록은 별도의 사용자 승인 뒤에 수행한다.

### 6.4 `search_meetings`

```mermaid
flowchart LR
    Q([search_meetings]) --> AUTH[user_id·날짜·회의 Filter]
    AUTH --> EMB[Query Embedding]
    AUTH --> KEY[pg_trgm Keyword 검색]
    EMB --> D[Dense Cosine / HNSW]
    D --> RRF[RRF 결합 Top-K]
    KEY --> RRF
    RRF --> META[Metadata·직접 근거 검증]
    META --> RR{조건부 Reranker 필요?}
    RR -->|예| RERANK[Reranker / groundedness]
    RR -->|아니오| CTX[근거 Context 구성]
    RERANK -->|성공| CTX
    RERANK -->|실패·Timeout| FALLBACK[RRF 결과 + warning]
    FALLBACK --> CTX
    CTX --> LLM[LLM 근거 기반 답변]
    LLM --> G{근거 충분?}
    G -->|예| YES[답변 + meeting/chunk 출처]
    G -->|아니오| NO[COMPLETED + insufficient_evidence]
```

단일 Cosine 임계값은 답변 거절 조건이 아니다. 근거가 없는 것은 시스템 실패가 아니므로
`COMPLETED`와 `insufficient_evidence: true`를 반환한다.

## 7. Assistant와 Human-in-the-loop

```mermaid
flowchart LR
    U([자연어 질문]) --> CONTEXT[최근 회의·제안·대화 Context]
    CONTEXT --> ROUTE{LLM route}
    ROUTE -->|reply| REPLY[직접 답변/되묻기]
    ROUTE -->|call_skill| CHECK{확인 필요한 동작?}
    CHECK -->|아니오| CALL[선택 Skill 실행]
    CHECK -->|예| INT[pending_action 반환]
    INT --> DECIDE{사용자 확인}
    DECIDE -->|취소| CANCEL[실행하지 않음]
    DECIDE -->|확인| RESUME[confirmed_skill_id로 재요청]
    RESUME --> CALL
    CALL --> PHRASE[Skill JSON·Markdown 기반 자연어 답변]
    PHRASE --> DONE([assistant_reply])
```

확인 대상은 `review_action_items`의 거절, `review_proposal`의 무시, `manage_tasks`의 삭제,
비용이 큰 `analyze_meeting`이다. 현재 Runtime에서는 `pending_action`과 확인 재요청으로 구현하며,
목표 LangGraph에서는 `interrupt`와 동일 `thread_id` 재개로 대응한다. 자연어 경로의
`manage_tasks`는 LLM의 ID 환각을 막기 위해 조회·생성만 허용하고 수정·삭제는 구조화된 직접 경로를 사용한다.

## 8. Task 상태와 Checkpoint

```mermaid
stateDiagram-v2
    [*] --> SUBMITTED
    SUBMITTED --> WORKING
    WORKING --> COMPLETED
    WORKING --> FAILED
    WORKING --> INPUT_REQUIRED
    WORKING --> AUTH_REQUIRED
    INPUT_REQUIRED --> WORKING: 사용자 입력 + 동일 thread_id
    AUTH_REQUIRED --> WORKING: 인증 복구 + 동일 thread_id
    SUBMITTED --> CANCELED
    WORKING --> CANCELED
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELED --> [*]
```

```mermaid
flowchart LR
    MID[message_id] --> IDEMP[Message 멱등성]
    TID[A2A task_id] --> MAP[(task_id ↔ thread_id)]
    TH[thread_id] --> MAP
    MAP --> TS[(Task Store<br/>외부 상태·Artifact)]
    MAP --> CP[(Checkpoint Store<br/>내부 State·재개 지점)]
    IDEMP --> TS
```

Task Store와 Checkpoint Store는 책임이 다르다. Task Store는 외부 A2A 상태와 Artifact의 원장이며,
Checkpoint는 Workflow 내부 State와 재개 지점이다. 현재는 두 저장 경계와 JSON Checkpoint가 있지만
LangGraph Checkpointer가 직접 연결되지는 않았다.

재시작 시 `SUBMITTED`, `WORKING`, `INPUT_REQUIRED`, `AUTH_REQUIRED` Task를 조회한다. 안전하게 재개할 수
있으면 같은 멱등성 Key와 Checkpoint를 사용하고, 재개할 수 없으면 원인을 기록한 뒤 `FAILED`로 전환한다.
취소는 먼저 Task Store에 기록한 후 실행 중인 Workflow·Provider에 전파한다.

## 9. Provider 실패와 재시도 경계

```mermaid
flowchart LR
    O[Orchestrator] -->|timeout·429·502·503·504<br/>같은 message_id| A[A2A 재시도]
    A --> W[Workmate Workflow]
    W -->|Node 내부 제한 재시도| P[Provider]
    P -->|일부 실패| PART[부분 결과 보존]
    PART --> WARN[warnings + data_freshness]
    P -->|핵심 저장소 실패| FAIL[FAILED]
```

Orchestrator와 Workmate가 같은 계층을 중복 재시도하지 않는다. HTTP 재시도는 Orchestrator가 담당하고,
Workmate는 Node/Handler 내부 Provider 호출만 제한적으로 재시도한다. 즉시 Workflow는 전체 15초 예산을
공유하며, 예산 내 완료가 어렵다면 현재 Task를 장기 Task로 전환한다.

## 10. 현재에서 목표 LangGraph로의 연결점

```mermaid
flowchart LR
    A[현재 WorkflowRequest/Result] --> S[WorkmateState Adapter]
    B[WorkflowRegistry handlers] --> N[Skill Subgraph Nodes]
    C[thread_id + Checkpoint JSON] --> CP[LangGraph Checkpointer]
    D[pending_action 재요청] --> I[interrupt / resume]
    E[A2A Task Store] --> T[Graph 상태 이벤트 연동]
```

전환 시 공개 A2A Schema나 업무 데이터 모델을 바꿀 필요는 없다. Registry의 Handler 계약을 Graph 입출력
Adapter로 감싸고 기존 `task_id ↔ thread_id`, 멱등성, Artifact 변환, Provider 부분 실패 규칙을 유지하면
된다. LangGraph 도입의 실질적 이점은 단순 Skill 분기 자체보다 다단계 승인, 중단·재개, Node별 재시도와
복잡한 실패 복구가 늘어날 때 커진다.

## 11. 구조 요약

1. Workmate는 하나의 A2A Agent이며 Skill마다 별도 Agent나 마이크로서비스를 만들지 않는다.
2. 현재 11개 Skill은 하나의 `WorkflowRegistry`와 공통 Runtime을 공유한다.
3. 업무 규칙은 Domain 코드, 외부 I/O는 Repository·Provider, 전송은 A2A/FastAPI 경계가 담당한다.
4. LLM은 요약·추출·라우팅·근거 기반 문장화를 담당하고 날짜·순위·권한·중복·근거 검증은 코드가 통제한다.
5. 현재 구현은 LangGraph형 경량 Workflow이며 실제 `StateGraph`와 Checkpointer 연결은 후속 구조다.
