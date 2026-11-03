# W2-12 — 참조 자료

> [30-2-w2-graph-foundation.md](30-2-w2-graph-foundation.md) §12의 상세 문서.

"무엇을 참조하는가"가 아니라 **"어디를 왜 읽는가"** 를 기록한다.

## 1. 설계 근거 문서

### 96-workmate-langgraph-target-architecture.md

W2 설계의 1차 출처다. 다음 절을 읽는다.

| 절 | 읽는 이유 | 대응 |
| --- | --- | --- |
| §3 공통 State | `WorkmateState` 필드 정의와 Reducer 규칙의 원본 | W2-R1, R2, R3, R4 |
| §7 Task 상태와 Checkpoint | `thread_id`·Checkpoint·Task Store의 관계도 | W2-R7 |
| §10 구현 경계 | Checkpointer와 Task Store의 책임 표 | W2-R11 |
| §11 불변식 | 식별자 보존(11-2), `user_id` 범위(11-3), 부분 실패 보존(11-6) | W2-R3, 후행 단계 |
| §8 오류·재시도 Graph | 재시도 계층 구분(HTTP는 Orchestrator, 노드는 Provider 호출) | W2-R9, W8 |

**주의** 96번은 "가정형 목표 아키텍처"다. 구현과 다르면 W9에서 **구현에 맞춰 문서를 고친다**. W2
시점에는 96번을 기준으로 삼되, 구현 불가한 부분이 나오면 기록하고 W9로 넘긴다.

### 30-langgraph-migration-plan.md

| 절 | 읽는 이유 |
| --- | --- |
| §0.1 전제 | "운영 중이 아니다", "호환보다 설계 정합성 우선" — 설계 선택의 기준 |
| §4 D3, D6 | W2가 구현하는 확정 결정 |
| §5 | 전체 단계 중 W2의 위치와 선후 관계 |
| §9-6 | W2-V7이 증명해야 하는 완료 조건. **W2에서 서술 정밀화 필요**([30-2-9](30-2-9-exit-criteria.md) §2.5) |

### 02-a2a-interface.md

W2는 공개 계약을 바꾸지 않지만, 어댑터가 산출하는 필드가 이 계약을 따른다. Artifact 구조와 Task
상태 값을 확인한다.

## 2. 코드 참조

### 2.1 State·어댑터 설계에 필요한 코드

| 파일·위치 | 읽는 이유 |
| --- | --- |
| [registry.py:20-54](../workmate-agent/app/workflows/registry.py#L20-L54) | `WorkflowRequest`·`WorkflowResult`의 필드 — 어댑터가 산출해야 할 8개 필드의 원본 |
| [daily_briefing.py:118](../workmate-agent/app/workflows/daily_briefing.py#L118) | `_warning()`이 만드는 경고 구조 — `WarningState` 필드의 근거 |
| [test_priority_workflow.py:45-49](../workmate-agent/tests/test_priority_workflow.py#L45-L49) | `data`가 비면 프론트가 빈 결과를 읽는 실사용 버그 — 어댑터 설계 제약 |

### 2.2 Checkpointer 설계에 필요한 코드

| 파일·위치 | 읽는 이유 |
| --- | --- |
| [runtime.py:402-414](../workmate-agent/app/a2a/runtime.py#L402-L414) | `build_task_store()`의 백엔드 선택 규칙 — Checkpointer가 따라야 할 규칙 |
| [runtime.py:228-233](../workmate-agent/app/a2a/runtime.py#L228-L233) | 기존 `save_checkpoint()` 호출 — 무엇을 대체하는지 |
| [persistence.py:63-70](../workmate-agent/app/a2a/persistence.py#L63-L70) | `a2a_checkpoints` 스키마 — W7 DROP 대상 |
| [runtime.py:240-241](../workmate-agent/app/a2a/runtime.py#L240-L241) | `thread_id = task_id` 규칙 |
| [main.py](../workmate-agent/app/main.py) | Selector Event Loop·IPv4 설정 — 비동기 Saver와의 충돌 확인용 |

### 2.3 LLM 경계 설계에 필요한 코드

**반드시 읽어야 할 6개 호출 지점** — 하나라도 빠뜨리면 [30-2-5](30-2-5-design.md) §5.2의 정책 불일치를
놓친다.

| 파일·위치 | 환경변수 | 재시도 | 읽는 이유 |
| --- | --- | --- | --- |
| [assistant_router.py:255-330](../workmate-agent/app/workflows/assistant_router.py#L255) | `OPENAI_*` | 3회, 네트워크만 | W2-R9의 원본. 주석에 2026-08-19 대응 배경이 있다 |
| [assistant_router.py:198](../workmate-agent/app/workflows/assistant_router.py#L198) | — | — | `_CHAT_COMPLETION_MAX_ATTEMPTS = 3` |
| [assistant_router.py:276-283](../workmate-agent/app/workflows/assistant_router.py#L276-L283) | — | — | `temperature=0` + strict json_schema — W2-R10의 원본 |
| [assistant_router.py:267-268](../workmate-agent/app/workflows/assistant_router.py#L267-L268) | — | — | 모델 식별자 변환(`openai/gpt-4.1-mini` → `gpt-4.1-mini`) |
| [weekly_report.py:55-80](../workmate-agent/app/workflows/weekly_report.py#L55-L80) | `LLM_*` | 2회, Provider 오류 포함 | **다른 정책.** W2-K6의 근거 |
| [weekly_report.py:141-193](../workmate-agent/app/workflows/weekly_report.py#L141) | `LLM_*` | — | 두 번째 호출 지점 |
| [meeting_analysis.py:46-60](../workmate-agent/app/meeting_analysis.py#L46) | `OPENAI_*` | 조사 필요 | `analyze_meeting`이 경유 |
| [meeting_answer.py:40-90](../workmate-agent/app/meeting_answer.py#L40) | `LLM_*` | 없음(폴백) | `search_meetings`가 경유 |
| [email_action_items.py:60-110, 200-220](../workmate-agent/app/email_action_items.py#L60) | `OPENAI_*` | 조사 필요 | **범위 밖 호출자와 공유** — [30-2-5](30-2-5-design.md) §5.3 |

## 3. 개발 규칙

### AGENTS.md

| 규칙 | W2에서의 적용 |
| --- | --- |
| 의존성 원장은 `pyproject.toml`·`uv.lock` | W2-T1 |
| SDK 버전 변경 시 M0.1 Contract Test 재실행 | 전이 의존성이 A2A SDK를 밀어 올린 경우 |
| 공개 함수·핵심 업무 규칙 함수에 Docstring | `app/graph/` 전 공개 함수 |
| Docstring은 한글 기본, 식별자는 원문 유지 | 동상 |
| 이벤트 순서·멱등성·재시도·취소 불변식 명시 | `llm.py`의 재시도 정책, `checkpointer.py`의 thread 규칙 |
| Secret·Token·개인정보를 주석·Docstring·Fixture에 기록 금지 | W2-V9 |
| 실패한 테스트 삭제·우회 금지, 기대값 완화 금지 | [30-2-11](30-2-11-rollback.md) §3.2 |
| 자동 승인·자동 진행 보류 사유 기록 | [30-2-9](30-2-9-exit-criteria.md) §3 |

## 4. 선후 단계 문서

| 문서 | W2와의 관계 |
| --- | --- |
| [30-0](30-0-w0-baseline.md) | 기준선·기준 Commit·테스트 환경의 출처 |
| [30-1](30-1-w1-contract-snapshot.md) | W2-E1의 선행 조건. §5.5의 LLM Fake 한계가 W2-V6의 배경 |
| [30-3](30-3-w3-skill-subgraphs.md) | W2 산출물의 첫 소비자. W3-E3이 W2-V6에 의존 |
| [30-4](30-4-w4-root-graph.md) | Checkpointer를 Graph에 결합 |
| [30-6](30-6-w6-interrupt-resume.md) | Checkpointer 위에서 `interrupt` 성립 |
| [30-7](30-7-w7-legacy-removal.md) | `a2a_checkpoints` DROP, `save_checkpoint` 제거 |
| [30-8](30-8-w8-retry-observability.md) | W2가 정의한 RetryPolicy를 전 노드에 적용 |
| [30-9](30-9-w9-docs-evidence.md) | W2에서 발견한 정책 불일치를 후속 백로그로 기록 |

## 5. 외부 문서

| 자료 | 확인할 내용 |
| --- | --- |
| LangGraph — StateGraph·Reducer | `Annotated[list, add]` 사용법, superstep 내 동시 갱신 규칙 |
| LangGraph — Checkpointer | `AsyncSqliteSaver`·`AsyncPostgresSaver` 초기화·수명, `get_state_history()` |
| LangGraph — RetryPolicy | `retry_on` 판정 함수 시그니처, 노드 단위 적용 방법 |
| langchain-openai — ChatOpenAI | `max_retries`, `temperature`, timeout 전달 방식 |
| langchain-core — structured output | `with_structured_output()`의 `method` 선택과 strict 지원 범위 |

**검증 우선 원칙:** 외부 문서의 서술과 실제 동작이 다를 수 있다. W2-V7(호출 횟수 계측)과
W2-V6(결과 구조 비교)은 문서가 아니라 **실행 결과**로 판정한다.

## 6. 이 문서 묶음

| 문서 | 대응 절 |
| --- | --- |
| [30-2-1](30-2-1-document-info.md) | §1 문서 정보·용어·ID 규칙 |
| [30-2-2](30-2-2-scope.md) | §2 목적과 범위 |
| [30-2-3](30-2-3-entry-criteria.md) | §3 선행 조건 |
| [30-2-4](30-2-4-requirements.md) | §4 요구사항 |
| [30-2-5](30-2-5-design.md) | §5 설계 |
| [30-2-6](30-2-6-wbs.md) | §6 작업 분해 |
| [30-2-7](30-2-7-verification.md) | §7 검증 설계 |
| [30-2-8](30-2-8-traceability.md) | §8 추적성 매트릭스 |
| [30-2-9](30-2-9-exit-criteria.md) | §9 완료 정의 |
| [30-2-10](30-2-10-risks.md) | §10 위험 등록부 |
| [30-2-11](30-2-11-rollback.md) | §11 롤백·중단·재개 |
| [30-2-12](30-2-12-references.md) | §12 참조 (이 문서) |
