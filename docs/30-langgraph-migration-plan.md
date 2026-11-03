# Workmate LangGraph 전면 전환 계획

작성일: 2026-09-22
개정일: 2026-09-23 (§4 결정 6건 확정)
문서 성격: **확정된 구현 계획**. §4 결정이 모두 확정되어 W0부터 착수할 수 있다.
목적: `workmate-agent`에서 **LangGraph가 담당할 수 있는 모든 구조를 LangGraph로 전면 재작성**한다.

관련 문서:

- [96-workmate-langgraph-target-architecture.md](96-workmate-langgraph-target-architecture.md) — 목표 `StateGraph` 구조. 이 문서는 그 목표에 **도달하는 실행 계획**이다.
- [97-workmate-langgraph-structure.md](97-workmate-langgraph-structure.md) — 현재 Runtime과 목표 Graph의 차이 표. 전환 완료 시 이 문서의 "현재" 열이 폐기된다.
- [07-technical-specification.md](07-technical-specification.md) — 기술 기준.
- [02-a2a-interface.md](02-a2a-interface.md) — 공개 A2A 계약. **D1=B 결정으로 이번 전환의 개정 대상이다.**

## 0. 전제와 결정 기록

### 0.1 전제

| 전제 | 근거 | 계획에 미치는 영향 |
| --- | --- | --- |
| **운영 배포 중이 아니다.** 지켜야 할 실사용자 데이터·가동률이 없다. | 사용자 확인(2026-09-23) | 데이터 파기·공개 계약 변경·긴 전환 기간을 감수할 수 있다 |
| **목표는 탄탄한 LangGraph 설계이고 학습이 목적이다.** | 사용자 확인(2026-09-23) | 하위 호환을 위한 우회 설계보다 **구조 정합성**을 우선한다 |

### 0.2 결정 기록

| 일자 | 결정 | 출처 |
| --- | --- | --- |
| 2026-09-22 | 초판의 **병행 경로 + `WORKMATE_USE_LANGGRAPH` 플래그 + 단계별 점진 전환** 방식을 폐기한다. | 사용자 지시 |
| 2026-09-22 | 전환 범위는 **LangGraph가 들어갈 수 있는 부분 전부**로 한다. | 사용자 지시 |
| 2026-09-22 | `app/workflows/` 모듈과 그에 붙은 테스트를 **모두 재작성**한다. | 사용자 지시 |
| 2026-09-22 | **빅뱅 전면 재작성**(단일 브랜치, 한 번의 스위치)으로 진행한다. | 사용자 지시 |
| 2026-09-23 | §4의 D1~D6을 **D1=B, D2=A, D3=B, D4=A, D5=A, D6=B**로 확정한다. | 사용자 결정 |
| 2026-09-23 | 전환 기간 중 충돌 구역은 **기본 동결**하고, 불가피한 수정만 전환 브랜치에 직접 반영한다(§7.2). | 운영 중이 아니라는 전제에 따른 기본값 |

초판에서 적용했다가 폐기된 원칙 셋은 이후 작업에 적용하지 않는다.

- "운영 경로를 끊지 않는다"(기존 Handler 존치 + 환경변수 분기)
- "한 단계에 한 개념만 배운다"(학습 단위 분할)
- "기존 테스트를 한 줄도 고치지 않는다"

## 1. 개정 원칙

1. **전면 교체다.** 전환이 끝나면 저장소에 `WorkflowRegistry`도, 레거시 Handler 경로도, 전환용 환경변수도 남지 않는다. 실행 경로는 하나다.
2. **호환보다 구조 정합성을 우선한다.** 운영 중이 아니므로, "옛 모양을 유지하려고 Graph 구조를 비트는" 설계를 선택하지 않는다. LangGraph의 정식 방식(`interrupt`/`resume`, Checkpointer, Reducer, Subgraph)을 먼저 놓고, 그에 맞게 공개 계약과 UI를 고친다. 다만 `AGENTS.md`의 금지 사항(실패 테스트 삭제·우회, 기대값 완화, 결정적 규칙의 LLM 이관)은 예외 없이 지킨다.
3. **범위는 §2 표가 정의한다.** LangGraph 개념이 대응하는 코드는 전부 교체하고, 대응이 없는 계층(전송·인증·Repository·Provider·순수 Domain 함수)은 그대로 둔다. LangGraph는 Workflow 실행 구조를 소유하지 HTTP·SQL·인증을 소유하지 않는다.
4. **계약 스냅샷이 유일한 회귀 안전망이다.** D1=B로 공개 계약이 바뀌므로 `test_contract.py`를 "기대값 무변경 감시선"으로 쓸 수 없다. 따라서 W1에서 뽑는 스냅샷(§5 W1)이 옛 동작과 새 동작을 비교할 **유일한 기준**이다. W1 없이 W3을 시작하지 않는다.
5. **빅뱅이되 스위치는 한 번이다.** `feat/lg-rewrite` 단일 브랜치에서 작업하고, 중간 커밋은 동작하지 않아도 된다. `main`은 전환 기간 내내 현재 구조 그대로 둔다.
6. **결정적 규칙의 소유권은 바뀌지 않는다.** 우선순위 점수·순위·근거 ID·날짜 계산·`user_id` 범위 적용은 Graph로 옮긴 뒤에도 결정적 코드 Node가 소유한다. LLM은 요약·구조화 추출·자연어 라우팅·문장화만 담당한다(`AGENTS.md`, 96번 §11).

## 2. 수정 범위

코드에서 직접 확인한 사실을 기준으로 한다.

### 2.1 전면 교체 대상

| 현재 구현 | 근거 | 목표 |
| --- | --- | --- |
| `WorkflowRegistry`의 `skill_id → async handler` dict 디스패치 | [registry.py:57](../workmate-agent/app/workflows/registry.py#L57), [runtime.py:353-386](../workmate-agent/app/a2a/runtime.py#L353-L386) | Root `StateGraph`의 `add_conditional_edges` + path map |
| Skill별 단일 async 함수 12개(공개 11 + `runtime_bootstrap`) | [app/workflows/](../workmate-agent/app/workflows/) | Skill Subgraph 11개 + Root Graph 내부 노드 |
| frozen dataclass `WorkflowRequest`/`WorkflowResult` | [registry.py:20-54](../workmate-agent/app/workflows/registry.py#L20-L54) | `WorkmateState` TypedDict + Reducer + 경계 어댑터 |
| 직접 만든 `a2a_checkpoints` 테이블과 `save_checkpoint()` — [runtime.py:228](../workmate-agent/app/a2a/runtime.py#L228)에서 `submitted` 마커를 **한 번 쓰기만 하고 읽는 코드가 없다** | [persistence.py:63-70](../workmate-agent/app/a2a/persistence.py#L63-L70), [persistence.py:281-307](../workmate-agent/app/a2a/persistence.py#L281-L307) | LangGraph Checkpointer. **테이블은 DROP Migration으로 폐기(D6=B)** |
| `pending_action` 반환 → 프론트가 `confirmed_skill_id`로 **재요청** | [assistant_router.py:794-876](../workmate-agent/app/workflows/assistant_router.py#L794-L876) | `interrupt()` + `Command(resume=...)`. **공개 계약까지 개편(D1=B, §4.1)** |
| `assistant_ask_workflow()` 937줄 단일 함수(LLM 2~3회 + 분기 + 확인) | [assistant_router.py:771](../workmate-agent/app/workflows/assistant_router.py#L771) | Assistant Router Subgraph(96번 §6 노드 구성) |
| `_chat_completion()`의 `urllib` 직접 호출과 손수 만든 재시도 루프 | [assistant_router.py:255](../workmate-agent/app/workflows/assistant_router.py#L255), [:198](../workmate-agent/app/workflows/assistant_router.py#L198) | `langchain-openai` 모델 객체 + 노드 `RetryPolicy`(D3=B). **재시도 구분 보존은 §9 완료 조건** |
| Daily Briefing의 순차 소스 수집과 `warnings` 수동 누적 | [daily_briefing.py:132-322](../workmate-agent/app/workflows/daily_briefing.py#L132-L322) | 병렬 팬아웃/팬인 노드 + `Annotated[list, add]` 리듀서 |
| Workflow가 Workflow를 직접 호출하는 지연 Import 재귀 | [assistant_router.py:881-891](../workmate-agent/app/workflows/assistant_router.py#L881-L891), [daily_briefing.py:238](../workmate-agent/app/workflows/daily_briefing.py#L238) | Subgraph 합성(상위 Graph가 하위 Graph를 노드로 소유) |
| UI의 Task 폴링 루프가 `INPUT_REQUIRED`를 모른다 | [AssistantDrawer.tsx:151-163](../workmate-ui/app/views/AssistantDrawer.tsx#L151-L163) | 폴링 구조는 유지하고 `INPUT_REQUIRED` 분기와 resume 호출을 추가(D5=A) |

### 2.2 건드리지 않는 것

| 계층 | 파일 | 이유 |
| --- | --- | --- |
| A2A 전송·Route allowlist·Agent Card·인증 | [runtime.py:85-163](../workmate-agent/app/a2a/runtime.py#L85-L163), [internal_chat.py:53-157](../workmate-agent/app/internal_chat.py#L53-L157) | 공식 SDK와 JWT/JWKS 경계. Graph 진입 전에 끝나는 일(96번 §10) |
| A2A Task Store(외부 원장) | [persistence.py:98](../workmate-agent/app/a2a/persistence.py#L98), [persistence.py:323](../workmate-agent/app/a2a/persistence.py#L323) | Task Snapshot·Artifact·멱등성의 원장. Checkpointer와 합치지 않는다 |
| Repository 계층 | [app/repositories/](../workmate-agent/app/repositories/) | Node가 호출하는 `user_id` 범위 SQL I/O |
| Provider Client | [app/providers/](../workmate-agent/app/providers/), [stt.py](../workmate-agent/app/stt.py), [embeddings.py](../workmate-agent/app/embeddings.py), [storage/r2.py](../workmate-agent/app/storage/r2.py) | 외부 SDK 경계 |
| 순수 Domain 규칙 | [app/domain/](../workmate-agent/app/domain/) | 결정적 함수. 노드가 호출할 뿐 Graph 개념이 아님 |
| UI REST API 모듈 | [task_api.py](../workmate-agent/app/task_api.py), [meeting_api.py](../workmate-agent/app/meeting_api.py), [proposal_api.py](../workmate-agent/app/proposal_api.py), [action_item_api.py](../workmate-agent/app/action_item_api.py), [transcript_api.py](../workmate-agent/app/transcript_api.py) 등 | Skill 실행 경로가 아닌 CRUD·조회 API |
| Windows 실행 환경 설정 | [main.py](../workmate-agent/app/main.py)의 Selector Event Loop·IPv4 강제 | Graph 도입과 무관하게 필요 |

### 2.3 자리를 옮기는 것 (D4=A)

| 파일 | 이동처 | 이유 |
| --- | --- | --- |
| [weekly_classification.py](../workmate-agent/app/workflows/weekly_classification.py) | `app/domain/` | I/O 없는 순수 함수(`link_approved_tasks`·`build_weekly_report_data`·`extract_next_week_plans`). 노드가 아니라 Domain |
| [external_sync.py](../workmate-agent/app/workflows/external_sync.py) | `app/sync/` | Skill이 아니고 HTTP Route·스케줄러에 연결돼 있지 않지만([dev_gmail_sync_api.py:3](../workmate-agent/app/dev_gmail_sync_api.py#L3) 주석), **M1.2-04·M1.4-01 승인 증빙이 이 경로를 참조**하므로 삭제하지 않는다 |

이동 시 [06-delivery-plan.md:91](06-delivery-plan.md#L91)·[:769](06-delivery-plan.md#L769)의 구현 경로 링크와 `docs/evidence/` 참조 2건을 함께 갱신한다. 증빙 본문은 수정하지 않고 경로만 정정한다.

## 3. 목표 파일 구조

```
app/graph/
  __init__.py          build_workmate_graph() 하나만 공개
  state.py             WorkmateState, WarningState, Reducer, 상태 전이 규칙
  adapter.py           전송 payload ↔ State ↔ A2A Artifact 경계 변환
  checkpointer.py      SQLite/Postgres Checkpointer 생성과 수명 관리
  llm.py               langchain-openai 모델 객체 생성과 RetryPolicy 정책(D3=B)
  root.py              Root StateGraph 조립(initialize → idempotency → route → validate → artifact → persist)
  nodes/               Root 공통 노드
  skills/
    daily_briefing.py  rank_priorities.py  weekly_report.py
    analyze_meeting.py search_meetings.py  assistant_router.py
    assistant_skills/  get_meeting_analysis · review_action_items · review_proposal · manage_tasks · read_email
app/sync/
  external_sync.py     app/workflows/에서 이동(D4=A)
app/domain/
  weekly_classification.py  app/workflows/에서 이동(D4=A)
```

- `app/workflows/` 패키지는 전환 완료 시 **삭제**한다.
- `app/a2a/runtime.py`와 `app/internal_chat.py`는 Registry 호출부만 `build_workmate_graph()` 호출로 교체한다. 인증·Route·Task Store 코드는 유지한다.

## 4. 확정된 결정

| ID | 결정 | 확정 | 근거 |
| --- | --- | --- | --- |
| **D1** | 사용자 확인·재개 프로토콜 | **B — `interrupt` 기반으로 공개 계약까지 개편** | 호환 우회보다 구조 정합성 우선(§1-2) |
| **D2** | 테스트 재작성 기준 | **A — 계약 스냅샷 선추출 후 재작성** | D1=B로 `test_contract` 감시선이 사라져 스냅샷이 유일 안전망 |
| **D3** | LLM 호출 방식 | **B — `langchain-openai` 모델 객체 도입** | LangGraph 생태계 표준 방식 학습 |
| **D4** | 비-Skill 모듈 처리 | **A — 둘 다 이동(삭제하지 않음)** | 승인 증빙이 `external_sync` 경로를 참조 |
| **D5** | 장기 실행 모델 | **A — 폴링 유지 + `INPUT_REQUIRED` 분기 추가** | 전환 범위 통제. 스트리밍은 별건 |
| **D6** | Checkpointer와 옛 테이블 | **B — `a2a_checkpoints` DROP Migration 포함** | 운영 중이 아니라 기존 데이터 파기 무방 |

### 4.1 D1=B가 바꾸는 공개 계약 (W6 설계 산출물)

현재는 확인이 필요하면 응답에 `pending_action`을 실어 보내고 **서버에 아무 상태도 남기지 않으며**, 프론트가 `confirmed_skill_id`로 **새 요청**을 만든다. 전환 후에는 Graph가 `interrupt()`로 멈춰 Checkpoint에 얼어붙고, 같은 `thread_id`로 **resume**한다.

W6에서 확정해야 할 계약 항목은 다음과 같다. 설계안은 W6 착수 시 별도로 제시하고 승인받는다.

1. **Task 상태 노출** — 확인 대기는 `TASK_STATE_INPUT_REQUIRED`로 표면화한다. 이 상태 문자열은 현재 agent·UI 어디에도 존재하지 않는다.
2. **interrupt payload 전달 위치** — 확인 문구·`skill_id`·`arguments`를 Task Snapshot의 어디에 싣는지(A2A `Task.status.message` vs. Artifact).
3. **resume 요청 형태** — 새 `message:send`가 아니라 같은 Task에 대한 재개 요청임을 어떻게 표현하는지. 새 Task를 만들지 않고 같은 `thread_id`·멱등성 Key를 쓴다(96번 §11-8).
4. **취소 경로** — 사용자가 확인을 거부했을 때의 상태 전이(`CANCELED`).
5. **영향 파일** — [02-a2a-interface.md](02-a2a-interface.md), [AssistantDrawer.tsx](../workmate-ui/app/views/AssistantDrawer.tsx), [tools/m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py).

> **승인 경계:** 오케스트레이터 저장소(`AI-agent_game_platform`) 코드는 `AGENTS.md`상 건드리지 않는다. 어댑터([tools/m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py), 우리 저장소)에서 흡수할 수 있는지 W6에서 먼저 확인하고, 오케스트레이터 수정이 불가피하면 그 시점에 별도 승인을 받는다.

## 5. 작업 순서

브랜치: `feat/lg-rewrite` 하나. 중간 커밋은 동작을 보장하지 않는다. 커밋 메시지는 `<type>(LG-Wn): <change>` 형식을 쓴다.

각 단계는 **별도 상세 계획 문서**를 갖는다. 아래 표는 색인이며, 요구사항 ID·설계·WBS·검증 설계·추적성 매트릭스·DoD는 각 문서에 있다.

| 단계 | 상세 문서 | 내용 | 핵심 검증 | 상태 |
| --- | --- | --- | --- | --- |
| **W0** | [30-0](30-0-w0-baseline.md) | 기준선 채증과 출발점 정리 | 전체 테스트 실행, 기준 Commit 확정 | **완료** |
| **W1** | [30-1](30-1-w1-contract-snapshot.md) | 계약 스냅샷 추출 (**옛 구현이 살아 있을 때만 가능**) | 스냅샷 재현·결정성 | 대기 |
| **W2** | [30-2](30-2-w2-graph-foundation.md) | State·어댑터·Checkpointer·LLM 골격 | 어댑터 왕복, Checkpoint 복원, LLM 동등성·재시도 구분 | 대기 |
| **W3** | [30-3](30-3-w3-skill-subgraphs.md) | Skill Subgraph 11개 재작성 (`assistant_ask`는 마지막) | 스냅샷 대조, `user_id` 범위, 부분 실패 | 대기 |
| **W4** | [30-4](30-4-w4-root-graph.md) | Root Graph 조립 | 라우팅·멱등성·Schema 검증 | 대기 |
| **W5** | [30-5](30-5-w5-entrypoint-swap.md) | 진입점 교체 (운영 경로가 Graph가 되는 지점) | 이벤트 순서, 오류 매핑 | 대기 |
| **W6** | [30-6](30-6-w6-interrupt-resume.md) | 확인·재개를 `interrupt`로 + **공개 계약 개편**(§4.1) | 재개·취소, interrupt 이전 외부 상태 무변경, UI 육안 검수 | 대기 |
| **W7** | [30-7](30-7-w7-legacy-removal.md) | 레거시 삭제·모듈 이동·DROP Migration | 잔여 참조 0, Migration 멱등성, 증빙 링크 유효성 | 대기 |
| **W8** | [30-8](30-8-w8-retry-observability.md) | 재시도와 관측 | HTTP 4xx/5xx 비재시도, 부분 실패 보존 | 대기 |
| **W9** | [30-9](30-9-w9-docs-evidence.md) | 문서·증빙 정리와 완료 판정 | 완료 기준 대조, 스냅샷 diff 분류 | 대기 |
| **W10** | [30-10](30-10-w10-react-agent.md) | **ReAct Agent 전환** (전환 완료 후 별도 작업) | 카탈로그 규칙 회귀, 결정적 규칙 보존 | **계획 수립** |

> **W10은 W0~W9 전환의 일부가 아니다.** `assistant_ask`의 단발 분류 라우팅을 ReAct 루프로 바꾸는
> 후속 작업이며, W9 완료·승인 후 별도로 착수한다. 전환의 완료 기준이 "의도적으로 바꾼 것 외에는
> 아무것도 안 바뀌었다"(§9-7)인데 ReAct를 섞으면 그 판정이 불가능해지기 때문이다. 착수 전
> [05-ai-security-operations.md](05-ai-security-operations.md) §1 개정 승인과 결정 D7-1~D7-7 확정이
> 필요하다([30-10-3](30-10-3-entry-criteria.md) 선행 조건, [30-10-10](30-10-10-approval.md) 승인 경계).
> **D7과 05번 개정은 지금 확정하지 않는다** — W2~W6을 거치면서 판단 근거가 채워지는 결정이고, 문서를
> 미리 고치면 W1~W9 동안 설계 문서가 구현보다 앞서 나간다([30-10-10](30-10-10-approval.md) §1.1).
> W10도 다른 단계와 같이 13개 절별 문서로 분해되어 있다(30-10-1 ~ 30-10-13).

각 단계의 불변식(96번 §11)은 단계마다 다시 확인한다. 특히 **모든 조회에 `user_id` 범위 적용**과 **`interrupt` 이전에 외부 상태를 바꾸지 않는다**는 W3·W6에서 테스트로 고정한다.

## 6. 테스트 재작성 매핑

현재 `app.workflows`·`workflow_registry`·`a2a.runtime`에 의존하는 테스트는 **18개 파일 4,675줄**이다. 나머지 45개 파일(Repository·Domain·Provider·UI API)은 범위 밖이며 수정 없이 통과해야 한다.

| 기존 테스트 | 줄 | 처리 |
| --- | --- | --- |
| [test_assistant_router.py](../workmate-agent/tests/test_assistant_router.py) | 1,019 | Assistant Subgraph 노드 단위 + `interrupt`/`resume` 시나리오로 재작성. 최대 난관 |
| [test_internal_chat.py](../workmate-agent/tests/test_internal_chat.py) | 451 | 진입점 교체 + `INPUT_REQUIRED` 폴링 분기(D5=A) 반영 |
| [test_daily_briefing.py](../workmate-agent/tests/test_daily_briefing.py) | 446 | 병렬 노드 + `warnings` 리듀서 기준으로 재작성 |
| [test_contract.py](../workmate-agent/tests/test_contract.py) | 399 | **D1=B로 기대값 계승 불가.** 새 resume 프로토콜 기준으로 재작성하고, 변경되지 않는 Artifact·Skill Schema 부분은 그대로 유지 |
| [test_assistant_skills.py](../workmate-agent/tests/test_assistant_skills.py) | 314 | 보조 Skill 5종 Subgraph 기준 재작성 |
| [test_meeting_workflows.py](../workmate-agent/tests/test_meeting_workflows.py) | 313 | 분석/검색 Subgraph 분리 반영 |
| [test_proposals.py](../workmate-agent/tests/test_proposals.py) | 255 | `app/sync/` 이동에 따른 import 경로 변경 |
| [test_weekly_source_link.py](../workmate-agent/tests/test_weekly_source_link.py) | 234 | `weekly_classification` → `app/domain/` 이동 반영 |
| [ui_working_fixture.py](../workmate-agent/tests/ui_working_fixture.py) | 212 | Fixture 경로 갱신 |
| [test_google_adapters.py](../workmate-agent/tests/test_google_adapters.py) | 181 | `app/sync/` 이동 반영 |
| [test_runtime_boot.py](../workmate-agent/tests/test_runtime_boot.py) | 169 | Registry 등록 검증 → Graph 노드 등록 검증으로 교체 |
| [test_weekly_report_generation.py](../workmate-agent/tests/test_weekly_report_generation.py) | 152 | Weekly Subgraph + `langchain-openai` 호출 경로 기준 재작성 |
| [test_persistence.py](../workmate-agent/tests/test_persistence.py) | 113 | Checkpointer 테스트로 교체. Task Store 부분은 유지. `save_checkpoint` 테스트는 DROP과 함께 제거 |
| [test_weekly_report_provider_failure.py](../workmate-agent/tests/test_weekly_report_provider_failure.py) | 104 | 부분 실패 Edge 기준 재작성 |
| [test_m2_1_integration.py](../workmate-agent/tests/test_m2_1_integration.py) | 89 | 통합 시나리오 유지, 호출 경로만 교체 |
| [test_priority_workflow.py](../workmate-agent/tests/test_priority_workflow.py) | 88 | Priority Subgraph 기준 재작성 |
| [test_m1_5_integration.py](../workmate-agent/tests/test_m1_5_integration.py) | 86 | 통합 시나리오 유지 |
| [test_weekly_plan_grounding.py](../workmate-agent/tests/test_weekly_plan_grounding.py) | 50 | 근거 검증 노드 기준 재작성 |

추가로 [test_migration.py](../workmate-agent/tests/test_migration.py)에 `a2a_checkpoints` DROP 검증을 더한다(D6=B).

## 7. 스위치오버·롤백·동결

### 7.1 스위치오버와 롤백

- 전환 기간 내내 `main`은 현재 구조로 둔다. 운영 배포가 없으므로 가동률 위험은 없다.
- 스위치는 `feat/lg-rewrite` 머지 한 번이다. 머지 조건은 §9 완료 기준 전부 충족이다.
- 롤백은 머지 전이면 "머지하지 않음", 머지 후면 revert다. 환경변수로 즉시 되돌리는 수단은 **없다**.
- **D6=B의 비가역성:** `a2a_checkpoints` DROP Migration이 실행된 뒤에는 그 테이블의 기존 행을 되살릴 수 없다. 운영 중이 아니고 해당 데이터가 `{task_id}:submitted` 마커뿐이므로 파기해도 무방하다고 확인했다(2026-09-23).
- `AGENTS.md` 커밋 규칙에 따라 작업 단위로 로컬 커밋만 남기고, 전체 완료·승인 시점에 한 번에 Push한다.

### 7.2 전환 기간 동결 구역

기본은 **동결**이다. 아래 경로는 전환 기간 동안 `main`에서 수정하지 않는다. 전환 브랜치에서 삭제·재작성되므로 `main`의 변경은 `modify/delete` 충돌이 되고, git이 자동 해결하지 못한다.

- `app/workflows/` 전체
- [app/a2a/runtime.py](../workmate-agent/app/a2a/runtime.py)
- [app/internal_chat.py](../workmate-agent/app/internal_chat.py)
- [workmate-ui/app/views/AssistantDrawer.tsx](../workmate-ui/app/views/AssistantDrawer.tsx)
- [tools/m51_legacy_adapter.py](../workmate-agent/tools/m51_legacy_adapter.py)

불가피한 수정이 생기면 `main`이 아니라 **전환 브랜치에 새 구조 기준으로** 넣는다. `app/repositories/`·`app/domain/`·`app/providers/`·UI REST API 모듈은 범위 밖이므로 평소대로 작업해도 된다.

## 8. 위험과 대응

| 위험 | 대응 |
| --- | --- |
| 구현·테스트·공개 계약이 동시에 바뀌어 비교 기준이 사라진다 | W1 계약 스냅샷이 유일한 방어선이다. W1 없이 W3을 시작하지 않는다(§1-4) |
| `assistant_router.py`(937줄) + 그 테스트(1,019줄)가 전체 일정의 최대 변수 | W3에서 이 Skill을 마지막에 하고, W6에서 `interrupt`를 다시 다룬다. 노드 경계는 96번 §6을 그대로 쓴다 |
| `langchain-openai` 도입으로 재시도 정책이 조용히 바뀐다 | 현재는 **HTTP 4xx/5xx 비재시도 · 네트워크 오류만 3회 재시도**다([assistant_router.py:295-305](../workmate-agent/app/workflows/assistant_router.py#L295-L305), 2026-08-19 DNS 간헐 실패 대응). 라이브러리 기본 재시도를 끄고 같은 구분을 RetryPolicy로 재현한다. §9-6 완료 조건 |
| `temperature=0` + `json_schema` strict 동작이 래퍼 교체로 달라진다 | W2에서 구조화 출력 동등성 테스트를 먼저 만들고 W3을 시작한다 |
| 공개 계약 개편이 오케스트레이터까지 번진다 | W6에서 어댑터 흡수 가능성을 먼저 확인한다. 불가피하면 그 시점에 별도 승인(§4.1) |
| 동결 구역에 수정이 쌓여 머지 지옥이 된다 | §7.2 동결. 불가피한 수정은 전환 브랜치에 직접 |
| Checkpointer와 Task Store 책임이 섞인다 | 96번 §10 경계표를 W2·W4·W6에서 재확인한다. Task 상태 판정은 계속 Task Store가 소유한다 |
| 의존성 충돌 | `langgraph` + Checkpointer + `langchain-openai`가 Python `>=3.12,<3.13`, `a2a-sdk==1.1.2`, `fastapi==0.116.1`과 공존하는지 W2에서 먼저 확인한다 |
| Windows 로컬 실행 차이 | [main.py](../workmate-agent/app/main.py)의 Selector Event Loop·IPv4 설정을 유지하고, 비동기 Checkpointer와의 상호작용을 W2에서 확인한다 |

## 9. 완료 기준

1. `app/workflows/`와 `WorkflowRegistry`가 저장소에 없다. `grep -r "WorkflowRegistry" app`이 비어 있다.
2. 공개 Skill 11개가 모두 Graph 경로로 실행되고, 운영 경로에 Mock·고정 샘플 응답이 없다(`AGENTS.md` 완료 규칙).
3. 전체 테스트(63개 파일 + 신규) PASS. 범위 밖 45개 파일은 **수정 없이** 통과한다.
4. 확인이 필요한 동작이 `interrupt`로 멈춰 `INPUT_REQUIRED`로 표면화되고, 같은 `thread_id` resume으로 이어서 실행되며, 재개 시 Router LLM을 다시 부르지 않는다. 확인 거부 시 `CANCELED`로 끝난다.
5. `a2a_checkpoints` 테이블이 DROP되고, LangGraph Checkpointer로 State 이력 조회와 재개가 실증된다.
6. LLM 호출이 `langchain-openai` 경로로 바뀐 뒤에도 **네트워크 오류만 재시도하고 HTTP 4xx/5xx는 즉시 실패**한다.
7. W1 계약 스냅샷 대비, 의도적으로 바꾼 항목(§4.1) 외에 결과 값 차이가 없다.
8. 02·96·97번 문서가 실제 구현 기준으로 갱신된다(사용자 승인 후).
9. `docs/evidence/langgraph/`에 W0 기준선과 각 단계 결과가 기록된다.

## 10. 이 문서로 결정하지 않은 것

- §4.1 공개 계약의 구체적 형태 — W6 착수 시 설계안을 따로 제시하고 승인받는다.
- 오케스트레이터 저장소(`AI-agent_game_platform`) 수정 필요 여부 — W6에서 판정 후 별도 승인.
- `astream` 스트리밍 전환(D5의 B안) — 전환 완료 후 별건. **W10과 함께 하는 편이 낫다**([30-10-2](30-10-2-scope.md) §5).
- LangSmith 등 외부 트레이싱 도입 — API Key가 필요하므로 별도 승인. **동상**.
- **ReAct Agent 전환(W10)** — 이 전환의 범위가 아니다. [30-10](30-10-w10-react-agent.md)에서 결정
  D7-1~D7-7과 [05번 문서](05-ai-security-operations.md) §1 개정 승인을 받은 뒤 착수한다.
