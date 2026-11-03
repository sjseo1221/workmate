# W2-2 — 목적과 범위

> [30-2-w2-graph-foundation.md](30-2-w2-graph-foundation.md) §2의 상세 문서.

## 1. 목적

이후 모든 단계가 딛고 설 **공통 기반 4종**을 만든다. 이 단계에서 만드는 것은 Skill 로직이 아니라
Skill이 공유할 타입·경계·인프라다.

| # | 기반 | 없으면 생기는 일 |
| --- | --- | --- |
| 1 | **State** — Graph가 주고받는 자료구조와 병합 규칙 | 노드마다 제각각 dict를 주고받아 병렬 분기에서 값이 유실된다 |
| 2 | **어댑터** — 전송 ↔ State ↔ 공개 응답 경계 | 공개 응답 모양이 Skill 구현에 직접 묶여 계약이 조용히 바뀐다 |
| 3 | **Checkpointer** — 실행 중 State의 영속화 | `interrupt`가 성립하지 않는다. W6이 통째로 불가능해진다 |
| 4 | **LLM 경계** — 모델 객체와 재시도 정책 | D3=B의 위험이 Skill 11개에 분산돼 W3에서 원인 분리가 어려워진다 |

### 1.1 "골격"의 의미

W2 산출물은 **동작하지만 아무 데도 연결되지 않은 상태**로 끝난다. 운영 경로는 여전히
`WorkflowRegistry`이고, 사용자에게 보이는 동작은 전환 전과 동일하다.

이는 의도된 것이다. 기반을 먼저 완성하고 그 위에 Skill을 쌓으면, W3에서 실패했을 때 원인이 "기반"인지
"Skill 이식"인지 구분된다. 반대 순서(Skill 먼저, 기반 나중)는 두 원인이 섞인다.

## 2. 범위 내 (In scope)

| ID | 항목 | 산출물 | 근거 |
| --- | --- | --- | --- |
| S1 | `app/graph/` 패키지 신설 | 디렉터리·`__init__.py` | 계획서 §3 |
| S2 | State·Reducer 정의 | `state.py` | 96번 §3 |
| S3 | 경계 어댑터 구현 | `adapter.py` | 계획서 §5 W2 |
| S4 | Checkpointer 생성·수명 관리 | `checkpointer.py` | D6=B |
| S5 | LLM 모델 객체와 재시도 정책 | `llm.py` | D3=B |
| S6 | 의존성 추가와 lockfile 갱신 | `pyproject.toml`, `uv.lock` | `AGENTS.md` lockfile 규칙 |
| S7 | 기존 `_chat_completion()`과의 동등성 검증 | `test_graph_llm.py` | D3=B 위험 통제 |
| S8 | 각 모듈의 단위 테스트 | 테스트 4종 | `AGENTS.md` 완료 규칙 |

## 3. 범위 외 (Out of scope)

| 항목 | 담당 단계 | 이번에 하지 않는 이유 |
| --- | --- | --- |
| Skill 로직 이식 | [W3](30-3-w3-skill-subgraphs.md) | 기반이 확정되기 전에 시작하면 재작업이 11배로 늘어난다 |
| Root Graph 조립·라우팅 | [W4](30-4-w4-root-graph.md) | Subgraph가 없으면 합성 대상이 없다 |
| 진입점 교체 | [W5](30-5-w5-entrypoint-swap.md) | 운영 경로 변경은 Graph가 완성된 뒤 |
| `interrupt`/`resume` 흐름 | [W6](30-6-w6-interrupt-resume.md) | Checkpointer는 만들되 쓰는 쪽은 W6 |
| `app/workflows/` 수정·삭제 | [W7](30-7-w7-legacy-removal.md) | W2~W6 동안 비교 대상으로 살아 있어야 한다 |
| `a2a_checkpoints` DROP Migration | [W7](30-7-w7-legacy-removal.md) | 비가역 작업은 새 경로가 검증된 뒤 |
| 노드 단위 RetryPolicy **적용** | [W8](30-8-w8-retry-observability.md) | W2는 정책 **정의**까지, 전 노드 적용은 노드가 생긴 뒤 |
| 범위 밖 LLM 호출 지점 통일 | 별건 | [30-2-5](30-2-5-design.md) §5.3 참조 |

### 3.1 경계가 헷갈리는 항목

**"LLM 재시도"는 W2와 W8에 걸쳐 있다.**

| 단계 | 하는 일 |
| --- | --- |
| W2 | 오류 분류 함수와 `RetryPolicy` 객체를 **정의**하고, 모델 객체의 라이브러리 기본 재시도를 끈다 |
| W8 | 정의된 정책을 **전 노드에 적용**하고, 노드 내부 재시도 루프를 제거하며, 부작용 노드를 제외한다 |

W2에서 정책을 정의하지 않으면 W3의 LLM Skill들이 각자 재시도를 구현하게 되고, W8에서 11곳을 되돌려야
한다.

**"Checkpointer"는 W2에서 만들지만 쓰는 곳은 W4·W6이다.** W2는 생성·저장·복원·이력 조회가 되는지까지
확인하고, Graph에 결합하는 것은 W4(`build_workmate_graph(checkpointer=...)`)다.

## 4. 범위 밖 LLM 호출 지점 문제

코드 전수 조사 결과 OpenAI 호환 `/chat/completions` 호출은 **6곳**이며, 이 중 일부는 W3 범위 밖
모듈에 있다.

| 모듈 | 호출 수 | 환경변수 | W3 Skill 범위 |
| --- | --- | --- | --- |
| [assistant_router.py:281](../workmate-agent/app/workflows/assistant_router.py#L281) | 1 | `OPENAI_*` | 범위 내 (`assistant_ask`) |
| [weekly_report.py:169](../workmate-agent/app/workflows/weekly_report.py#L169) | 1 | `LLM_*` | 범위 내 (`weekly_report`) |
| [meeting_analysis.py:54](../workmate-agent/app/meeting_analysis.py#L54) | 1 | `OPENAI_*` | 범위 내 (`analyze_meeting`이 호출) |
| [meeting_answer.py:73](../workmate-agent/app/meeting_answer.py#L73) | 1 | `LLM_*` | 범위 내 (`search_meetings`가 호출) |
| [email_action_items.py:96, 209](../workmate-agent/app/email_action_items.py#L96) | 2 | `OPENAI_*` | **부분** — `daily_briefing`(범위 내)과 `dev_gmail_sync_api`·`proposal_api`(범위 밖)가 공유 |

**W2의 범위 결정:** `llm.py`는 **공통 경계로 설계하되, 이번에 교체하는 호출 지점은 W3 Skill이 실제로
사용하는 경로로 한정**한다. `email_action_items.py`처럼 범위 밖 호출자와 공유되는 모듈은
[30-2-5](30-2-5-design.md) §5.3의 처리 방침을 따른다.

환경변수 계열이 `OPENAI_*`와 `LLM_*`로 갈려 있는 것은 이번 전환이 만든 문제가 아니라 기존 상태다.
**통일은 이번 범위가 아니다** — 통일하려면 배포 환경변수 설정까지 함께 바꿔야 하고, 이는 전환 검증과
무관한 변수를 하나 더 늘린다. W9에서 후속 백로그로 기록한다.

## 5. 범위 변경 절차

W2 진행 중 범위 변경이 필요해지면 다음을 따른다.

| 상황 | 처리 |
| --- | --- |
| 범위 내 항목의 세부 설계 변경 | 구현자 판단으로 진행, 상세 문서 갱신 |
| 범위 외 항목을 끌어와야 함 | 그 항목이 없으면 W2가 완료 불가한지 먼저 판정. 가능하면 후행 단계로 미룬다 |
| **확정 결정(D3·D6)에 영향** | 사용자 승인 없이 변경하지 않는다([30-2-11](30-2-11-rollback.md) §3) |
| 의존성 버전 변경 | `AGENTS.md`에 따라 M0.1 Contract Test 재실행 |

특히 **D3을 임의로 A안(urllib 유지)으로 되돌리지 않는다.** 의존성 충돌이나 동등성 실패가 발생하면
사실을 보고하고 사용자 판단을 기다린다.

## 6. 참조

- [30-2-4](30-2-4-requirements.md) — 범위 내 항목이 요구사항으로 구체화된 형태
- [30-2-5](30-2-5-design.md) §5.3 — LLM 호출 지점 처리 방침
- [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §2 — 전환 전체의 범위 정의
