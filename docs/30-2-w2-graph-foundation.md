# W2 — State·어댑터·Checkpointer·LLM 골격

> **이 문서는 요약과 색인이다.** 각 절의 상세는 아래 12개 문서에 있고, 두 문서가 충돌하면 상세
> 문서를 기준으로 한다.
>
> | 절 | 상세 문서 | 내용 |
> | --- | --- | --- |
> | §1 | [30-2-1](30-2-1-document-info.md) | 문서 정보·체계·용어·ID 규칙 |
> | §2 | [30-2-2](30-2-2-scope.md) | 목적과 범위, 경계 근거, 범위 변경 절차 |
> | §3 | [30-2-3](30-2-3-entry-criteria.md) | 선행 조건과 확인 명령 |
> | §4 | [30-2-4](30-2-4-requirements.md) | 요구사항 명세 W2-R1~R11 |
> | §5 | [30-2-5](30-2-5-design.md) | 설계 — 모듈 4종, **LLM 호출 지점 6곳 전수 조사** |
> | §6 | [30-2-6](30-2-6-wbs.md) | 작업 분해 W2-T1~T11, 병렬 실행 |
> | §7 | [30-2-7](30-2-7-verification.md) | 검증 설계 W2-V1~V9, 케이스 상세 |
> | §8 | [30-2-8](30-2-8-traceability.md) | 추적성 매트릭스(전방·후방·출처·소비자) |
> | §9 | [30-2-9](30-2-9-exit-criteria.md) | 완료 정의와 승인 절차 |
> | §10 | [30-2-10](30-2-10-risks.md) | 위험 등록부 W2-K1~K8 |
> | §11 | [30-2-11](30-2-11-rollback.md) | 롤백·중단·재개 기준 |
> | §12 | [30-2-12](30-2-12-references.md) | 참조 자료와 읽을 지점 |

## 1. 문서 정보

| 항목 | 값 |
| --- | --- |
| 단계 | W2 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W1 계약 스냅샷](30-1-w1-contract-snapshot.md) |
| 후행 단계 | [W3 Skill Subgraph](30-3-w3-skill-subgraphs.md) |
| 상태 | 대기 |
| 관련 결정 | D3=B(`langchain-openai` 도입), D6=B(Checkpointer 도입) |

## 2. 목적과 범위

### 2.1 목적

이후 모든 단계가 딛고 설 **공통 기반 4종**을 만든다. 이 단계에서 만드는 것은 Skill 로직이 아니라,
Skill이 공유할 타입·경계·인프라다.

1. **State** — Graph 전체가 주고받는 자료구조와 병합 규칙
2. **어댑터** — 전송 계층 ↔ State ↔ A2A Artifact 경계 변환
3. **Checkpointer** — 실행 중 State의 영속화(=`interrupt` 성립 조건)
4. **LLM 경계** — `langchain-openai` 모델 객체와 재시도 정책

### 2.2 범위 내

- `app/graph/` 패키지 신설과 위 4개 모듈 구현
- 의존성 추가(`langgraph`, `langgraph-checkpoint-*`, `langchain-openai`)와 lockfile 갱신
- 기존 `_chat_completion()`과의 **동등성 검증**

### 2.3 범위 외

- Skill 로직 이식 (W3)
- Root Graph 조립 (W4)
- `interrupt` 흐름 (W6)
- 기존 `app/workflows/` 수정·삭제 (W7)

## 3. 선행 조건

| ID | 조건 | 확인 방법 |
| --- | --- | --- |
| W2-E1 | W1 스냅샷이 전건 PASS | `tests.contracts.test_contract_snapshots` |
| W2-E2 | 기준선 440+ 테스트 유지 | 전체 스위트 실행 |

## 4. 요구사항

| ID | 구분 | 요구사항 | 출처 |
| --- | --- | --- | --- |
| W2-R1 | 기능 | 96번 §3의 `WorkmateState`를 TypedDict로 정의한다 | 96번 §3 |
| W2-R2 | 기능 | `warnings`는 노드별 값을 덮어쓰지 않고 누적한다 | 96번 §3 Reducer 규칙 |
| W2-R3 | 제약 | `user_id`·`request_id`·`message_id`·`task_id`·`thread_id`는 실행 중 변경되지 않는다 | 96번 §11-2 |
| W2-R4 | 제약 | Secret·Token·Presigned URL·원본 개인정보를 State에 담지 않는다 | 96번 §3, `AGENTS.md` |
| W2-R5 | 기능 | 전송 payload → State, State → `WorkflowResult` 상당 출력의 왕복 변환을 제공한다 | 계획서 §5 W2 |
| W2-R6 | 기능 | `DATABASE_URL` 유무에 따라 Postgres/SQLite Checkpointer를 선택한다 | [runtime.py:402](../workmate-agent/app/a2a/runtime.py#L402) 규칙과 일치 |
| W2-R7 | 기능 | `thread_id`로 State를 저장·복원하고 이력을 조회할 수 있다 | 96번 §7 |
| W2-R8 | 기능 | LLM 호출을 `langchain-openai` 모델 객체로 수행한다 | D3=B |
| W2-R9 | 제약 | **네트워크 오류만 재시도하고 HTTP 4xx/5xx는 즉시 실패한다** | [assistant_router.py:295-305](../workmate-agent/app/workflows/assistant_router.py#L295-L305), 2026-08-19 DNS 대응 |
| W2-R10 | 제약 | `temperature=0` + JSON Schema strict 구조화 출력 동작을 유지한다 | [assistant_router.py:276-283](../workmate-agent/app/workflows/assistant_router.py#L276-L283) |
| W2-R11 | 제약 | Checkpointer와 A2A Task Store의 책임을 합치지 않는다 | 96번 §10 |

## 5. 설계

### 5.1 모듈 구성

```
app/graph/
  __init__.py        build_workmate_graph()만 공개 (W4에서 채움)
  state.py           WorkmateState, WarningState, Reducer
  adapter.py         payload ↔ State ↔ Artifact 변환
  checkpointer.py    Checkpointer 생성·수명 관리
  llm.py             ChatOpenAI 생성, 구조화 출력, RetryPolicy
```

### 5.2 State (`state.py`)

96번 §3을 그대로 구현한다. 핵심은 채널별 병합 규칙이다.

```python
class WorkmateState(TypedDict, total=False):
    # 불변 식별자 — 실행 중 변경 금지(W2-R3)
    request_id: str
    message_id: str
    task_id: str
    thread_id: str
    user_id: str
    skill_id: str

    # 입력·실행 문맥
    input: dict[str, Any]
    now: str
    timezone: str

    # 중간 상태
    source_data: Annotated[dict[str, Any], merge_by_source]
    normalized_items: list[dict[str, Any]]
    warnings: Annotated[list[WarningState], add]      # 누적(W2-R2)
    pending_action: dict[str, Any] | None

    # 결과
    task_state: Literal["SUBMITTED", "WORKING", "INPUT_REQUIRED", "AUTH_REQUIRED",
                        "COMPLETED", "FAILED", "CANCELED"]
    result: dict[str, Any]
    markdown: str
    error: dict[str, Any] | None
```

| 채널 | Reducer | 이유 |
| --- | --- | --- |
| `warnings` | `operator.add` | 병렬 노드가 각자 경고를 남기고 모두 보존해야 한다 |
| `source_data` | 출처별 namespace 병합 | Gmail·Calendar·Task가 동시에 쓰므로 충돌 방지 |
| 식별자 5종 | 덮어쓰기 금지(불변식 테스트) | W2-R3 |
| 나머지 | 기본 덮어쓰기 | 단일 노드만 쓴다 |

**설계 근거:** Reducer가 없으면 병렬 분기(W3의 Daily Briefing)에서 동일 채널 동시 갱신이 충돌한다.
이는 LangGraph의 superstep 모델이 요구하는 조건이다.

### 5.3 어댑터 (`adapter.py`)

```python
def state_from_request(*, skill_id, task_id, thread_id, message_id,
                       user_id, payload) -> WorkmateState:
    """전송 계층 입력을 Graph 초기 State로 변환한다."""


def result_from_state(state: WorkmateState) -> WorkflowResultLike:
    """Graph 종료 State를 공개 응답 구조로 변환한다.

    W7에서 WorkflowResult가 사라진 뒤에도 같은 필드 집합
    (artifact_name·artifact_description·text·data·markdown·state·warnings·mock)을
    유지한다 — W1 스냅샷의 비교 대상이기 때문이다.
    """
```

이 어댑터가 **전환 기간 내내 계약을 지키는 단일 지점**이다. 공개 응답 모양이 바뀌는 곳은 W6의
`interrupt` 관련 필드뿐이고, 그 외 변경은 여기서 차단한다.

### 5.4 Checkpointer (`checkpointer.py`)

```python
def build_checkpointer() -> BaseCheckpointSaver:
    """환경에 맞는 Checkpointer를 만든다.

    DATABASE_URL이 있으면 AsyncPostgresSaver, 없으면 AsyncSqliteSaver를 쓴다 —
    build_task_store()와 같은 선택 규칙을 따른다(W2-R6).
    """
```

**책임 경계(W2-R11, 96번 §10)**

| 저장소 | 소유 | 소유하지 않음 |
| --- | --- | --- |
| A2A Task Store | 외부 Task 상태, Artifact, `message_id` 멱등성 | Graph 내부 노드 State |
| LangGraph Checkpointer | 내부 State, 재개 지점, interrupt payload | 외부 Task 상태 원장 |

연결 고리는 `task_id ↔ thread_id`뿐이다. 현재 코드도 이미 `thread_id = task_id`로 쓴다
([runtime.py:236-243](../workmate-agent/app/a2a/runtime.py#L236-L243)).

### 5.5 LLM 경계 (`llm.py`)

D3=B의 위험이 집중되는 모듈이다.

> **전수 조사 결과(2026-09-28):** `/chat/completions` 직접 호출은 **6곳, 5개 모듈**이며 환경변수 계열이
> `OPENAI_*`와 `LLM_*`로 갈려 있다. 더 중요한 것은 **재시도 정책이 하나가 아니라는 점**이다 —
> `assistant_router`는 3회·네트워크 오류만 재시도하지만, `weekly_report`는 2회·429·5xx까지 재시도한다.
> 따라서 아래 정책은 `assistant_router` 계열에 적용되며, 지점별 동작 보존이 기본 방침이다.
> 상세는 [30-2-5](30-2-5-design.md) §5.1~5.3.

```python
def build_chat_model(*, model: str | None = None) -> BaseChatModel:
    """구조화 출력용 ChatOpenAI를 만든다.

    라이브러리 기본 재시도는 끄고(max_retries=0) 재시도 정책은 노드
    RetryPolicy가 소유한다 — HTTP 4xx/5xx 재시도 금지 규칙(W2-R9)을
    지키기 위해서다.
    """


NETWORK_RETRY_POLICY = RetryPolicy(
    max_attempts=3,
    retry_on=_is_network_error,   # URLError/Timeout/ConnectionError/JSONDecodeError 계열만
)
```

**왜 라이브러리 재시도를 끄는가:** 현재 구현은 2026-08-19에 Windows 환경의 간헐적 DNS 실패
(`getaddrinfo failed`)를 잡으려고 재시도를 추가하면서, **HTTP 오류는 재시도해도 같은 결과이므로 즉시
실패**시키도록 범위를 좁혔다. LangChain 기본 재시도는 5xx·429도 재시도하므로 이 구분이 사라진다.

### 5.6 의존성

| 패키지 | 용도 | 확인 사항 |
| --- | --- | --- |
| `langgraph` | StateGraph·interrupt | Python 3.12 호환 |
| `langgraph-checkpoint-sqlite` | 개발·테스트 Checkpointer | |
| `langgraph-checkpoint-postgres` | 운영 Checkpointer | `psycopg[binary]==3.2.10`과 공존 |
| `langchain-openai` | 모델 객체 | `httpx` 등이 `fastapi==0.116.1`·`a2a-sdk==1.1.2`와 충돌하지 않을 것 |

`uv add` 후 `uv.lock`을 갱신하고, `AGENTS.md` 규칙에 따라 버전 변경 시 M0.1 Contract Test를 재실행한다.

## 6. 작업 분해 (WBS)

| ID | 작업 | 선행 | 산출물 |
| --- | --- | --- | --- |
| W2-T1 | 의존성 추가·충돌 확인 | — | `pyproject.toml`, `uv.lock` |
| W2-T2 | `state.py` 구현 | W2-T1 | State·Reducer |
| W2-T3 | 식별자 불변식 테스트 | W2-T2 | `tests/test_graph_state.py` |
| W2-T4 | `adapter.py` 구현 | W2-T2 | 왕복 변환 |
| W2-T5 | 어댑터 왕복 테스트 | W2-T4 | `tests/test_graph_adapter.py` |
| W2-T6 | `checkpointer.py` 구현 | W2-T1 | Saver 생성 |
| W2-T7 | Checkpointer 저장·복원·이력 테스트 | W2-T6 | `tests/test_graph_checkpointer.py` |
| W2-T8 | `llm.py` 구현(모델·재시도 정책) | W2-T1 | LLM 경계 |
| W2-T9 | 구조화 출력 동등성 테스트 | W2-T8 | `tests/test_graph_llm.py` |
| W2-T10 | 재시도 정책 테스트(4xx/5xx 비재시도) | W2-T8 | 위 파일 |
| W2-T11 | 증빙·커밋 | W2-T3~T10 | `result.md` |

## 7. 검증 설계

| ID | 검증 항목 | 방법 | 판정 기준 |
| --- | --- | --- | --- |
| W2-V1 | State Reducer | `warnings`에 두 노드가 각각 추가 | 둘 다 보존 |
| W2-V2 | 식별자 불변식 | 노드가 `user_id` 변경 시도 | 거부 또는 테스트 실패로 검출 |
| W2-V3 | 어댑터 왕복 | payload → State → 결과 구조 | 필드 손실 없음 |
| W2-V4 | Checkpointer 저장·복원 | 같은 `thread_id`로 2회 실행 | State 이력이 누적 |
| W2-V5 | Checkpointer 백엔드 선택 | `DATABASE_URL` 유무 | Postgres/SQLite 정확히 선택 |
| W2-V6 | 구조화 출력 동등성 | 같은 프롬프트·스키마로 기존 `_chat_completion()`과 신규 경로 비교(고정 응답) | 동일 결과 구조 |
| W2-V7 | 재시도 정책 | HTTP 500 주입 / DNS 오류 주입 | 500은 1회 시도 후 실패, 네트워크 오류는 3회 |
| W2-V8 | 기존 테스트 무영향 | 전체 스위트 | 440 + 신규, 실패 0 |
| W2-V9 | Secret 비저장 | State 직렬화 검사 | 토큰·키 패턴 미검출 |

## 8. 추적성 매트릭스

| 요구사항 | 작업 | 검증 |
| --- | --- | --- |
| W2-R1 | W2-T2 | W2-V1 |
| W2-R2 | W2-T2 | W2-V1 |
| W2-R3 | W2-T2, T3 | W2-V2 |
| W2-R4 | W2-T2 | W2-V9 |
| W2-R5 | W2-T4, T5 | W2-V3 |
| W2-R6 | W2-T6 | W2-V5 |
| W2-R7 | W2-T6, T7 | W2-V4 |
| W2-R8 | W2-T8 | W2-V6 |
| W2-R9 | W2-T8, T10 | W2-V7 |
| W2-R10 | W2-T8, T9 | W2-V6 |
| W2-R11 | W2-T6 | W2-V4, 설계 검토 |

## 9. 완료 정의 (Exit criteria)

1. W2-V1~V9 전부 PASS.
2. `app/graph/`의 4개 모듈이 존재하고, 각 공개 함수에 한글 Docstring이 작성됨(`AGENTS.md` 주석 규칙).
3. `uv.lock`이 갱신되고 기존 440개 테스트가 영향받지 않음.
4. **W2-V7(재시도 구분 보존)이 PASS** — D3=B의 최대 위험이 해소됐음을 증명.

## 10. 위험과 완화

| 위험 | 영향 | 완화 |
| --- | --- | --- |
| `langchain-openai` 의존성이 `a2a-sdk`·`fastapi`와 충돌 | W2에서 전환 전체가 막힘 | W2-T1을 가장 먼저 수행. 충돌 시 D3 재검토를 사용자에게 보고 |
| 라이브러리 기본 재시도가 살아 있어 4xx/5xx까지 재시도 | 장애 시 지연 증폭, 2026-08-19 회귀 | `max_retries=0` 명시 + W2-V7로 고정 |
| `with_structured_output`이 strict JSON Schema와 다르게 동작 | LLM 응답 파싱 실패 | W2-V6 동등성 테스트를 W3 착수 전에 통과시킨다 |
| 비동기 Checkpointer가 Windows Selector Event Loop와 충돌 | 로컬 실행 불가 | [main.py](../workmate-agent/app/main.py) 설정 유지한 채 W2-T7에서 확인 |
| Checkpointer와 Task Store 책임 혼재 | 상태 원장이 둘로 갈려 복구 불가 | 96번 §10 경계표를 설계 검토 항목으로 고정 |

## 11. 롤백·중단 기준

- W2 산출물은 신규 파일과 의존성 추가뿐이라 롤백은 커밋 revert로 충분하다.
- **중단 기준:** 의존성 충돌(W2-T1) 또는 구조화 출력 동등성(W2-V6)을 해결하지 못하면 D3 결정을
  사용자에게 되돌려 재확인한다. 임의로 A안(urllib 유지)으로 바꾸지 않는다.

## 12. 참조

- [96-workmate-langgraph-target-architecture.md](96-workmate-langgraph-target-architecture.md) §3, §7, §10, §11
- [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §4 D3·D6, §8
- [`app/a2a/persistence.py`](../workmate-agent/app/a2a/persistence.py), [`app/a2a/runtime.py`](../workmate-agent/app/a2a/runtime.py)
