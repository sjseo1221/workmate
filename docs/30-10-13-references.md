# W10-13 — 참조 자료

> [30-10-w10-react-agent.md](30-10-w10-react-agent.md) §13의 상세 문서.

## 1. 착수 전 반드시 읽을 것

| 자료 | 읽는 이유 | 읽을 지점 |
| --- | --- | --- |
| [05-ai-security-operations.md](05-ai-security-operations.md) | **LLM과 코드의 책임 표** — 개정 대상 | §1 전체 + 원칙 목록 |
| [`assistant_router.py`](../workmate-agent/app/workflows/assistant_router.py) | **134줄 규칙** — W10-T2의 대상 | `_SKILL_CATALOG` 전문 |
| 동 | 평평한 15필드 — ReAct가 해소하는 문제 | `_ARGUMENTS_SCHEMA` |
| 동 | 현재의 단발 분류 구조 | `route()` |
| 동 | 확인 대상 4종 | `_requires_confirmation()` |
| [16-llm-prompts.md](16-llm-prompts.md) | 프롬프트 원문 — 규칙 대조 | `assistant_ask` 절 |
| [AGENTS.md](../AGENTS.md) | 결정적 규칙·`user_id`·타 저장소 금지 | 구현 규칙, 금지 사항 |

### 1.1 `_SKILL_CATALOG`를 어떻게 읽나

**줄 단위로 읽는다.** 요약해서 읽으면 규칙이 빠진다.

```
1. 파일에서 _SKILL_CATALOG 전문을 꺼낸다
2. 한 줄씩 규칙표에 옮긴다
3. "이건 당연한 설명"이라고 생각되는 줄도 표에 남기고 판정을 적는다
4. 16번 문서와 대조해 누락 확인
```

**3번이 중요하다.** 당연해 보이는 줄이 실사용 오류로 추가된 것일 수 있다.

## 2. 설계 근거 문서

| 자료 | 읽는 이유 |
| --- | --- |
| [30-6-5](30-6-5-design.md) | W6의 interrupt 설계 — W10이 확장한다 |
| [30-6-10](30-6-10-approval.md) | W6의 승인 경계 — W10의 선례 |
| [30-3-5](30-3-5-design.md) §3.4 | 부작용 노드 — 확인 대상과 겹친다 |
| [30-2-5](30-2-5-design.md) | `WorkmateState` 원형 — W10이 확장한다 |
| [30-4-5](30-4-5-design.md) | Root Graph — ReAct Subgraph가 붙는 자리 |
| [30-8-5](30-8-5-design.md) | 노드 `RetryPolicy` — `max_retries=0`의 이유 |
| [30-9-12](30-9-12-backlog.md) | 후속 백로그 — W9-B7·B8과의 관계 |

## 3. 경위 문서

| 자료 | 읽는 이유 |
| --- | --- |
| [18-workmate-assistant-implementation-plan.md](18-workmate-assistant-implementation-plan.md) 설계 결정 2 | **LLM Router 도입 경위(2026-08-17)** — 왜 Agent가 아니라 분류기였는지 |
| [96-workmate-langgraph-target-architecture.md](96-workmate-langgraph-target-architecture.md) §11 | 불변식 — W10 이후에도 유지 |
| [97-workmate-langgraph-structure.md](97-workmate-langgraph-structure.md) | 구조 도식 — ReAct Subgraph 추가 대상 |

### 3.1 18번 설계 결정 2를 왜 읽나

**"Agent를 안 쓴 것이 실수가 아니라 결정이었다"는 기록이다.**

당시 판단은 "Skill 하나 고르기까지는 LLM, 실행 순서는 코드"였고, 그 경계가 05번 문서 §1에 반영됐다.
W10은 그 결정을 뒤집는 것이므로 **왜 그렇게 정했는지를 알고 뒤집어야 한다.**

## 4. 외부 자료

| 자료 | 쓰는 부분 |
| --- | --- |
| LangGraph — `create_react_agent` | **참고만.** 커스텀 구현의 기준 패턴(D7-2=B) |
| LangGraph — `ToolNode` | `tool_node` 구현 |
| LangGraph — `add_messages` | `messages` 채널 Reducer |
| LangGraph — `interrupt` / `Command(resume=...)` | 확인 게이트 |
| LangGraph — 조건 분기 `path_map` | `route_after_agent` |
| LangChain — `BaseTool`, `bind_tools` | 도구 정의 |
| LangChain — `ChatOpenAI` | 모델 래퍼 |

### 4.1 prebuilt를 "참고만" 하는 이유

`create_react_agent`의 소스를 읽어 **표준 루프의 구조**는 따르되, 확인 게이트와 예산 노드를 넣기 위해
직접 짠다([30-10-10](30-10-10-approval.md) §2.2).

**부수 효과** 직접 짜면 Graph 구조가 코드에 드러나 `draw_mermaid()` 출력이 설계 문서와 대조 가능해진다.
prebuilt를 쓰면 내부 구조가 라이브러리에 숨는다.

## 5. 쓰지 않는 것

[W9-R11](30-9-4-requirements.md)의 "안 쓰는 것" 목록에 W10 이후의 변화를 반영한다.

| 항목 | W9까지 | W10 이후 |
| --- | --- | --- |
| LangChain `AgentExecutor` | 안 씀 | **여전히 안 씀** — LangGraph로 직접 구현 |
| LangChain Tool 추상화 | 안 씀 | **씀** (`BaseTool`) |
| LCEL 파이프 | 안 씀 | 안 씀 |
| Retriever / VectorStore | 안 씀 | 안 씀 — 검색은 직접 SQL |
| Memory 추상화 | 안 씀 | 안 씀 — State + Checkpointer |
| `astream` | 안 씀 | W9-B7 (미정) |
| LangSmith | 안 씀 | W9-B8 (미정) |

**`AgentExecutor`를 쓰지 않는 것이 W10 이후에도 유지된다는 점이 중요하다.** "ReAct Agent"라고 해서
LangChain의 Agent 추상화를 쓰는 것이 아니다 — LangGraph StateGraph로 직접 짠다.

## 6. 증빙 경로

| 경로 | 내용 |
| --- | --- |
| `docs/evidence/langgraph/W10/README.md` | 단계 증빙 색인 |
| `docs/evidence/langgraph/W10/runs/{run_id}/result.md` | 실행 결과 |
| 동 `catalog-rules.md` | **규칙표** — 이 단계 증빙의 중심 |
| 동 `rule-regression.log` | W10-V1 |
| 동 `determinism.log` | W10-V5 |
| 동 `stability.md` | W10-V9 측정 |
| 동 `cost-latency.md` | W10-V8 측정 |
| 동 `snapshot-diff.md` | 23건 불변 + 4건 재작성 |

## 7. 문서 갱신 대상

W10 완료 시 아래를 갱신한다([30-10-8](30-10-8-traceability.md) §5).

```
[ ] docs/05-ai-security-operations.md §1    ← 착수 전에 개정
[ ] docs/02-a2a-interface.md                 계약
[ ] docs/16-llm-prompts.md                   프롬프트 원문
[ ] docs/13-manual-verification-guide.md     육안 검수 항목
[ ] docs/96-*.md                             assistant_ask 노드 구성
[ ] docs/97-*.md                             ReAct Subgraph 도식
[ ] docs/18-*.md                             설계 결정 2의 후속 기록
[ ] docs/30-9-12-backlog.md                  W9-B11 완료 표시
[ ] docs/README.md                           30-10 상태
[ ] HANDOFF.md
```

**`AGENTS.md`는 수정하지 않는다** — 충돌 지점을 찾지 못했다([30-10-10](30-10-10-approval.md) §3.4).

## 8. 참조

- [30-10-1](30-10-1-document-info.md) — 문서 체계
- [30-10-10](30-10-10-approval.md) — 승인 경계
- [30-10-8](30-10-8-traceability.md) — 추적성
