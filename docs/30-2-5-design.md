# W2-5 — 설계

> [30-2-w2-graph-foundation.md](30-2-w2-graph-foundation.md) §5의 상세 문서.

## 1. 모듈 구성

```
app/graph/
  __init__.py        build_workmate_graph()만 공개 (W4에서 채움, W2에서는 빈 공개면)
  state.py           WorkmateState, WarningState, Reducer            → W2-R1~R3
  adapter.py         payload ↔ State ↔ 공개 응답 변환                → W2-R5
  checkpointer.py    Checkpointer 생성·수명 관리                      → W2-R6, R7, R11
  llm.py             모델 객체, 구조화 출력, 오류 분류, RetryPolicy    → W2-R8~R10
```

### 1.1 모듈 간 의존 규칙

```
state.py   ← 아무것도 import하지 않는다 (순수 타입 정의)
adapter.py ← state.py
llm.py     ← (독립) 외부 SDK만
checkpointer.py ← (독립) 외부 SDK만
```

`state.py`가 다른 모듈을 import하지 않는 것이 중요하다. W3에서 Skill Subgraph가 State를 import하므로,
State가 Checkpointer나 LLM을 끌고 오면 순환 의존과 테스트 격리 문제가 생긴다.

### 1.2 공개면 최소화

`app/graph/__init__.py`는 최종적으로 `build_workmate_graph()` 하나만 공개한다. 내부 모듈을 패키지
바깥에서 직접 import하는 것은 테스트와 W4의 조립 코드에 한정한다. 운영 코드(`runtime.py`·
`internal_chat.py`)는 W5에서 `build_workmate_graph()`만 부른다.

---

## 2. State (`state.py`)

### 2.1 정의

[96번 §3](96-workmate-langgraph-target-architecture.md)을 그대로 구현한다.

```python
class WarningState(TypedDict):
    source: str            # "gmail" | "calendar" | "task" | "llm" | "meeting" ...
    code: str              # "GMAIL_UNAVAILABLE" | "LLM_PROVIDER_UNAVAILABLE" ...
    message: str
    retryable: bool
    last_success_at: str | None


class WorkmateState(TypedDict, total=False):
    # 불변 식별자 (W2-R3)
    request_id: str
    message_id: str
    task_id: str
    thread_id: str
    user_id: str
    skill_id: str

    # 입력과 실행 문맥
    input: dict[str, Any]
    now: str
    timezone: str
    deadline_at: str

    # 중간 상태
    source_data: Annotated[dict[str, Any], merge_by_source]
    normalized_items: list[dict[str, Any]]
    warnings: Annotated[list[WarningState], operator.add]
    pending_action: dict[str, Any] | None

    # 결과
    task_state: Literal["SUBMITTED", "WORKING", "INPUT_REQUIRED", "AUTH_REQUIRED",
                        "COMPLETED", "FAILED", "CANCELED"]
    result: dict[str, Any]
    markdown: str
    error: dict[str, Any] | None
```

`WarningState`의 필드는 현재 구현이 만들어 내는 경고 구조와 같아야 한다
([daily_briefing.py:118](../workmate-agent/app/workflows/daily_briefing.py#L118)의 `_warning()`이 만드는
`source`·`code`·`message`·`retryable`·`last_success_at`). W1 스냅샷이 이 구조를 기대값으로 갖고 있다.

### 2.2 채널별 병합 규칙

| 채널 | Reducer | 근거 |
| --- | --- | --- |
| `warnings` | `operator.add` (누적) | 병렬 노드가 각자 경고를 남기고 모두 보존(W2-R2) |
| `source_data` | 출처별 namespace 병합 | Gmail·Calendar·Task가 동시에 쓴다. 키 충돌 시 예외로 검출 |
| 식별자 6종 | 덮어쓰기(기본) + 불변식 테스트 | 런타임 강제 대신 테스트 검출([30-2-4](30-2-4-requirements.md) W2-R3) |
| `task_state` | 덮어쓰기 | 상태 전이 검증은 W4 Root 노드의 책임 |
| 나머지 | 덮어쓰기(기본) | 단일 노드만 쓴다 |

### 2.3 `merge_by_source` 설계

```python
def merge_by_source(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """출처별 namespace로 병합한다.

    같은 키를 서로 다른 노드가 동시에 쓰면 병합 결과가 실행 순서에 의존하게
    되므로, 키 충돌은 조용히 덮어쓰지 않고 예외로 드러낸다.
    """
```

**설계 판단:** 충돌 시 "나중 값 우선"이 아니라 예외를 택한 이유는, 병렬 노드가 같은 출처 키를 쓰는
것은 설계 실수이지 정상 상황이 아니기 때문이다. 조용히 덮어쓰면 W3에서 값이 사라져도 알 수 없다.

### 2.4 Reducer가 없으면 생기는 일

LangGraph는 한 superstep 안에서 여러 노드가 같은 채널을 갱신하면, Reducer가 없는 채널에 대해
`InvalidUpdateError`를 낸다. `warnings`에 Reducer를 붙이지 않으면 `daily_briefing`의 병렬 수집 노드
중 둘 이상이 경고를 남기는 순간 실행이 실패한다. 이는 W3-T3에서 드러나며, W2에서 미리 막는다.

---

## 3. 어댑터 (`adapter.py`)

### 3.1 인터페이스

```python
def state_from_request(*, skill_id: str, task_id: str, thread_id: str,
                       message_id: str, user_id: str,
                       payload: dict[str, object]) -> WorkmateState:
    """전송 계층 입력을 Graph 초기 State로 변환한다.

    now·timezone은 payload에 있으면 그것을 쓰고, 없으면 여기서 주입한다 —
    노드가 각자 datetime.now()를 부르면 같은 실행 안에서 시각이 어긋난다.
    """


def result_from_state(state: WorkmateState) -> ResultEnvelope:
    """Graph 종료 State를 공개 응답 구조로 변환한다.

    W7에서 WorkflowResult가 삭제된 뒤에도 같은 필드 집합을 산출한다 —
    W1 계약 스냅샷의 비교 대상이기 때문이다.
    """
```

### 3.2 산출 필드 (W2-R5)

현재 [`WorkflowResult`](../workmate-agent/app/workflows/registry.py#L41)의 8개 필드를 그대로 낸다.

| 필드 | 출처 State 경로 | 비고 |
| --- | --- | --- |
| `artifact_name` | `result.artifact_name` | Skill이 정한다 |
| `artifact_description` | `result.artifact_description` | |
| `text` | `result.text` | 구조화 결과의 JSON 문자열인 경우가 많다 |
| `data` | `result.data` | **`None`이면 안 되는 경우가 있다** — 아래 참조 |
| `markdown` | `state.markdown` | 없으면 `None` |
| `state` | `task_state` 매핑 | `"completed"` 등 소문자 문자열 |
| `warnings` | `warnings` | 누적된 전체 |
| `mock` | 고정 `False` | 운영 경로에 Mock 금지(W3-R8) |

> **`data=None` 주의:** [test_priority_workflow.py:45-49](../workmate-agent/tests/test_priority_workflow.py#L45-L49)에
> 기록된 실사용 버그 — `WorkflowResult.data`가 비면 `internal_chat.py`가 `artifact.data=null`을 반환해
> 요청이 200이어도 프론트는 빈 결과만 읽는다. 어댑터는 `text`에 구조화 결과가 있는데 `data`가 비는
> 조합을 만들지 않아야 한다.

### 3.3 어댑터가 경계인 이유

전환 기간 동안 공개 응답 모양이 바뀌는 지점은 W6의 `interrupt` 관련 필드뿐이다. 나머지 변경은 전부
회귀다. 변환 코드가 한 파일에 모여 있으면 "공개 계약이 바뀌었는가"를 `git diff app/graph/adapter.py`로
확인할 수 있다. Skill마다 흩어져 있으면 불가능하다.

---

## 4. Checkpointer (`checkpointer.py`)

### 4.1 인터페이스

```python
def build_checkpointer() -> BaseCheckpointSaver:
    """환경에 맞는 Checkpointer를 만든다.

    DATABASE_URL이 있으면 AsyncPostgresSaver, 없으면 AsyncSqliteSaver를 쓴다 —
    build_task_store()와 같은 선택 규칙이다(W2-R6).
    """
```

### 4.2 백엔드 선택 규칙

[`build_task_store()`](../workmate-agent/app/a2a/runtime.py#L402)와 동일하게 맞춘다.

| 조건 | Task Store | Checkpointer |
| --- | --- | --- |
| `DATABASE_URL` 있음 | `PostgresTaskStore` | `AsyncPostgresSaver` |
| 없음 | `PersistentTaskStore` (SQLite `.runtime/a2a.sqlite3`) | `AsyncSqliteSaver` (`.runtime/` 하위) |

### 4.3 책임 경계 (W2-R11)

| 저장소 | 소유 | 소유하지 않음 |
| --- | --- | --- |
| A2A Task Store | 외부 Task 상태, Artifact, `message_id` 멱등성 | Graph 내부 노드 State |
| LangGraph Checkpointer | 내부 State, 재개 지점, interrupt payload | 외부 Task 상태 원장 |

연결 고리는 `task_id ↔ thread_id` 하나다. 현재 코드도 이미
[runtime.py:240-241](../workmate-agent/app/a2a/runtime.py#L240-L241)에서 `thread_id = task_id`로 쓴다.

### 4.4 기존 `a2a_checkpoints`와의 관계

| 항목 | 기존 | 신규 |
| --- | --- | --- |
| 쓰기 지점 | [runtime.py:228](../workmate-agent/app/a2a/runtime.py#L228) 1곳 | LangGraph가 노드마다 자동 |
| 쓰는 내용 | `{"skill_id", "task_id"}` + `phase: "submitted"` 마커 | 노드 실행 직후 State 전체 |
| 읽는 코드 | **없음** | `resume`·이력 조회 |
| 처리 | W7에서 DROP(D6=B) | — |

기존 테이블이 사실상 껍데기였으므로 대체에 따른 기능 손실이 없다. W0 §10.2의 조사 결과다.

### 4.5 수명 관리

`AsyncSqliteSaver`·`AsyncPostgresSaver`는 연결을 보유한다. FastAPI 앱 수명과 함께 열고 닫아야 하며,
요청마다 새로 만들면 연결이 누적된다.

**설계:** 프로세스 단위 싱글턴으로 만들고 `app/main.py`의 lifespan에서 정리한다. 단 W2에서는 생성
함수만 제공하고, 앱 수명 결합은 W5(진입점 교체)에서 한다 — W2 시점에는 앱이 Graph를 쓰지 않는다.

---

## 5. LLM 경계 (`llm.py`)

D3=B의 위험이 집중되는 모듈이다.

### 5.1 현재 LLM 호출 지점 전수 조사

`/chat/completions` 직접 호출은 **6곳, 5개 모듈**이다.

| 모듈 | 호출 | 환경변수 | 재시도 | W3 범위 |
| --- | --- | --- | --- | --- |
| [assistant_router.py:281](../workmate-agent/app/workflows/assistant_router.py#L281) | 1 | `OPENAI_*` | **3회, 네트워크만** | 내 (`assistant_ask`) |
| [weekly_report.py:169](../workmate-agent/app/workflows/weekly_report.py#L169) | 1 | `LLM_*` | **2회, 429·5xx 포함** | 내 (`weekly_report`) |
| [meeting_analysis.py:54](../workmate-agent/app/meeting_analysis.py#L54) | 1 | `OPENAI_*` | 조사 필요 | 내 (`analyze_meeting` 경유) |
| [meeting_answer.py:73](../workmate-agent/app/meeting_answer.py#L73) | 1 | `LLM_*` | 없음(실패 시 폴백) | 내 (`search_meetings` 경유) |
| [email_action_items.py:96, 209](../workmate-agent/app/email_action_items.py#L96) | 2 | `OPENAI_*` | 조사 필요 | **부분** |

### 5.2 발견된 정책 불일치

**재시도 정책이 하나가 아니다.**

| 지점 | 시도 | 재시도 대상 | 근거 |
| --- | --- | --- | --- |
| `assistant_router` | 3 | `URLError`·`TimeoutError`·`JSONDecodeError`. **HTTP 4xx/5xx 제외** | [:295-305](../workmate-agent/app/workflows/assistant_router.py#L295-L305), 2026-08-19 DNS 대응 |
| `weekly_report` | 2 | `LLMProviderError` — Docstring상 **timeout·429·5xx·Schema 오류 포함** | [:55-80](../workmate-agent/app/workflows/weekly_report.py#L55-L80) |

즉 "현재 재시도 정책을 보존한다"는 요구는 **정책이 두 개**라는 사실과 충돌한다. W2는 다음과 같이
처리한다.

| 방침 | 내용 |
| --- | --- |
| **지점별 동작 보존이 기본** | W1 스냅샷이 각 Skill의 현재 동작을 기대값으로 갖는다. 정책을 통일하면 스냅샷이 깨지고, 그 차이는 "의도한 변경"으로 설명해야 한다 |
| `RetryPolicy`를 두 종류 정의 | `NETWORK_ONLY_RETRY`(3회)와 `PROVIDER_ERROR_RETRY`(2회)를 `llm.py`에 함께 둔다 |
| 완료 조건의 대상 | 계획서 §9-6의 "네트워크 오류만 재시도"는 **`assistant_router` 계열**에 적용된다. `weekly_report` 계열은 기존 동작 유지가 기준이다 |
| 통일은 별건 | 정책 통일은 동작 변경이므로 전환과 분리한다. W9에서 후속 백로그로 기록 |

이 사실은 상위 계획서 §9-6의 서술을 정밀화한다. W2 착수 시 상위 문서에도 반영한다.

### 5.3 범위 밖 호출자와 공유되는 모듈

`email_action_items.py`는 `daily_briefing`(범위 내)과 `dev_gmail_sync_api`·`proposal_api`(범위 밖)가
함께 쓴다.

| 선택지 | 내용 | 평가 |
| --- | --- | --- |
| A. 모듈 전체를 새 LLM 경계로 교체 | 범위 밖 호출자도 영향 | 전환과 무관한 경로에 위험 전파 |
| **B. 모듈은 그대로 두고 Graph 노드에서 호출** | `daily_briefing` Subgraph가 기존 함수를 그대로 부른다 | **채택** — 범위를 지키고 위험을 줄인다 |
| C. 호출자별로 분기 | 코드 복잡도 증가 | 불필요 |

**채택: B.** W3의 `daily_briefing` 노드는 `extract_action_items()`를 기존 그대로 호출한다. 이 모듈의
LLM 경로 교체는 전환 범위가 아니다. [30-2-2](30-2-2-scope.md) §4의 결정과 일치한다.

같은 판단이 `meeting_analysis.py`에도 적용될 수 있다. W2-T1 착수 시 각 모듈의 호출자를 다시 확인해
"Graph 노드만 쓰는가"를 기준으로 교체 대상을 확정한다.

### 5.4 인터페이스

```python
def build_chat_model(*, model: str | None = None,
                     base_url: str | None = None,
                     api_key: str | None = None) -> BaseChatModel:
    """구조화 출력용 ChatOpenAI를 만든다.

    라이브러리 기본 재시도는 끈다(max_retries=0) — 재시도는 노드 RetryPolicy가
    소유한다. HTTP 4xx/5xx 비재시도 규칙(W2-R9)을 지키기 위해서다.
    temperature=0과 timeout 30초는 기존 동작을 따른다.
    """


def is_network_error(exc: BaseException) -> bool:
    """재시도 가능한 네트워크 계층 오류인지 판정한다."""


NETWORK_ONLY_RETRY: RetryPolicy    # 3회, 네트워크 오류만 (assistant_router 계열)
PROVIDER_ERROR_RETRY: RetryPolicy  # 2회, Provider 오류 포함 (weekly_report 계열)
```

### 5.5 구조화 출력

현재는 `response_format: {"type": "json_schema", "json_schema": {"name": ..., "schema": ...,
"strict": True}}`를 직접 싣는다. `langchain-openai`에서는 `with_structured_output(schema,
method=...)`으로 대응한다.

**검증 우선 원칙:** `method`가 무엇으로 결정되는지(function calling / json_mode / json_schema)에 따라
결과가 달라질 수 있으므로, W2-V6에서 **기존 경로와 신규 경로의 결과 구조를 직접 비교**한 뒤 W3을
착수한다. 비교는 고정 응답을 주입해 수행하며 실제 API를 부르지 않는다.

### 5.6 모델 식별자 처리

현재 [assistant_router.py:267-268](../workmate-agent/app/workflows/assistant_router.py#L267-L268)은
`OPENAI_MODEL` 기본값 `"openai/gpt-4.1-mini"`를 받아 `"gpt-4.1-mini"`로 바꾼다(OpenRouter 형식과
OpenAI 직접 호출 형식의 차이 보정). 이 변환 규칙을 `llm.py`로 옮기고 동작을 유지한다.

---

## 6. 의존성

| 패키지 | 용도 | 확인 사항 |
| --- | --- | --- |
| `langgraph` | StateGraph·interrupt | Python 3.12 호환 |
| `langgraph-checkpoint-sqlite` | 개발·테스트 Checkpointer | |
| `langgraph-checkpoint-postgres` | 운영 Checkpointer | `psycopg[binary]==3.2.10`과 공존 |
| `langchain-openai` | 모델 객체 | `httpx`·`pydantic` 등이 `fastapi==0.116.1`·`a2a-sdk==1.1.2`와 충돌하지 않을 것 |

### 6.1 충돌 위험 지점

현재 고정 버전 중 충돌 가능성이 있는 것:

| 기존 | 버전 | 충돌 가능 지점 |
| --- | --- | --- |
| `a2a-sdk[http-server]` | 1.1.2 | `pydantic`·`httpx` 버전 범위 |
| `fastapi` | 0.116.1 | `pydantic` v2 계열 |
| `psycopg[binary]` | 3.2.10 | `langgraph-checkpoint-postgres`가 요구하는 psycopg 버전 |
| `jsonschema` | 4.26.0 | LangChain의 스키마 처리 |

### 6.2 절차

1. `uv add langgraph langgraph-checkpoint-sqlite langgraph-checkpoint-postgres langchain-openai`
2. `uv.lock` 갱신 확인 — **기존 고정 버전이 변경되지 않았는지** 확인한다
3. 기존 버전이 밀려 올라가면 `AGENTS.md`에 따라 M0.1 Contract Test를 재실행한다
4. 충돌로 설치가 불가하면 [30-2-11](30-2-11-rollback.md) §3의 중단 절차를 따른다

### 6.3 lockfile 규칙

`AGENTS.md`: "공식 A2A SDK는 계획서에 고정된 정확한 버전과 lockfile을 사용하고, 버전 변경 시 M0.1
Contract Test를 다시 실행한다." W2는 A2A SDK를 바꾸지 않지만, 전이 의존성이 SDK의 요구 버전을 밀어
올릴 수 있으므로 같은 규칙을 적용한다.

---

## 7. 참조

- [96번 §3](96-workmate-langgraph-target-architecture.md) — State 정의 원본
- [96번 §10](96-workmate-langgraph-target-architecture.md) — 저장소 책임 경계
- [30-2-4](30-2-4-requirements.md) — 이 설계가 만족하는 요구사항
- [30-2-7](30-2-7-verification.md) — 설계 결정의 검증 방법
