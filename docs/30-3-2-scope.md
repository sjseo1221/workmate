# W3-2 — 목적과 범위

> [30-3-w3-skill-subgraphs.md](30-3-w3-skill-subgraphs.md) §2의 상세 문서.

## 1. 목적

Skill별 단일 async 함수를 **노드로 분해한 Subgraph**로 재작성한다.

### 1.1 왜 "옮기기"가 아니라 "분해"인가

현재 Skill은 하나의 함수 안에서 조회·계산·외부 호출·결과 조립을 전부 수행한다. 이 형태 그대로 노드
하나에 넣으면 LangGraph를 쓰되 아무것도 얻지 못한다.

| 분해했을 때 얻는 것 | 분해하지 않으면 |
| --- | --- |
| 중간 상태가 State에 남아 Checkpoint·이력 조회 대상이 됨 | 함수 지역 변수로 사라짐 |
| 노드 단위 실패 격리와 재시도(W8) | 함수 전체가 실패 단위 |
| 병렬 실행(팬아웃/팬인) | 순차 실행 고정 |
| 중단·재개 지점 확보(W6) | 중단 불가 |
| 노드 단위 관측(W8) | 실행 내부가 블랙박스 |

### 1.2 분해의 기준

| 기준 | 노드를 나눈다 | 나누지 않는다 |
| --- | --- | --- |
| I/O 경계 | DB 조회, Provider 호출, LLM 호출은 각각 독립 노드 | |
| 실패 정책 | 실패 시 처리가 다르면 나눈다(전체 실패 vs `warnings`) | |
| 병렬 가능성 | 서로 의존하지 않는 수집은 나눈다 | |
| 재개 지점 | 사용자 확인 전후는 반드시 나눈다(W6 대비) | |
| 순수 계산 | | 같은 입력으로 이어지는 변환은 한 노드에 둔다 |
| 단순 포맷 | | 결과 조립·Markdown 렌더링은 한 노드 |

**과분해를 경계한다.** 노드가 많아질수록 Checkpoint I/O와 State 왕복이 늘어난다. "한 줄짜리 노드"가
생기면 분해 기준을 다시 본다.

## 2. 범위 내 (In scope)

| ID | 항목 | 산출물 |
| --- | --- | --- |
| S1 | 공개 Skill 11개의 Subgraph 구현 | `app/graph/skills/*` |
| S2 | Skill별 노드 단위 테스트 | `tests/test_graph_skill_*.py` |
| S3 | W1 스냅샷 대조 | 대조 로그 |
| S4 | Subgraph 입출력 인터페이스 정의(W4 합성 대비) | 설계 |
| S5 | 숨은 부작용 처리 방침 확정 | [30-3-5](30-3-5-design.md) §3 |

## 3. 범위 외 (Out of scope)

| 항목 | 담당 단계 | 이유 |
| --- | --- | --- |
| Root Graph 조립·라우팅 | [W4](30-4-w4-root-graph.md) | Subgraph가 다 만들어진 뒤 |
| 진입점 교체 | [W5](30-5-w5-entrypoint-swap.md) | W3 시점 운영 경로는 여전히 Registry |
| **`interrupt` 도입** | [W6](30-6-w6-interrupt-resume.md) | **W3은 현재 확인 방식을 그대로 재현한다** |
| `app/workflows/` 삭제 | [W7](30-7-w7-legacy-removal.md) | 비교 대상으로 살아 있어야 함 |
| 노드 `RetryPolicy` 적용 | [W8](30-8-w8-retry-observability.md) | W3은 기존 재시도 동작을 보존만 한다 |
| 공개 계약 변경 | W6 | W3에서 응답 모양이 바뀌면 회귀 |
| Domain 규칙 변경 | — | 점수·날짜·근거 검증은 그대로 호출만 |

### 3.1 특히 주의: 확인 흐름

`assistant_ask`의 확인 흐름은 W3에서 **바꾸지 않는다.**

```
현재:  requires_confirmation? → pending_action을 응답에 실어 반환 → 함수 종료
W3:    같은 동작을 노드로 재현 (build_pending_action_reply 노드)
W6:    interrupt()로 교체
```

W3에서 미리 `interrupt`를 넣으면 W1 스냅샷의 `assistant_ask.requires_confirmation` 케이스와 대조할 수
없다. 그러면 "Subgraph 이식이 틀렸는지 계약이 바뀐 것인지"를 구분하지 못한다.

다만 **노드 경계는 W6을 고려해 미리 나눈다.** `requires_confirmation` 판정과 실행 사이를 노드로
쪼개 두면, W6에서 그 사이에 `interrupt()`를 넣는 것으로 끝난다.

## 4. 설계 원칙 (W3-R 요구사항의 배경)

### 원칙 1 — 노드는 한 가지 일만 한다

I/O 노드와 계산 노드를 섞지 않는다. 섞으면 W8에서 재시도를 붙일 때 계산까지 재실행되고, 계산에
부작용이 있으면 중복 실행된다.

### 원칙 2 — 결정적 규칙은 Domain 함수에 남긴다

점수·순위·날짜 경계·중복 제거·권한·근거 검증은 [app/domain/](../workmate-agent/app/domain/)이 계속
소유한다. 노드는 **호출**할 뿐 재구현하지 않는다.

`AGENTS.md`: "우선순위 점수는 결정적으로 계산한다. LLM이 Task 순위와 근거 ID를 생성하거나 변경하지
않도록 한다." 노드 안에서 점수를 다시 계산하면 이 규칙을 지키는지 확인할 지점이 늘어난다.

### 원칙 3 — 실패는 예외가 아니라 Edge다

부분 실패는 `warnings`를 누적하고 다음 노드로 진행한다. 다만 **모든 실패가 그런 것은 아니다** —
핵심 소스 실패는 전체 실패다. Skill별 구분은 [30-3-5](30-3-5-design.md) §7에 있다.

### 원칙 4 — Subgraph는 자기 입력만 안다

다른 Skill 모듈을 직접 import하지 않는다. 현재 코드는 지연 import로 서로를 부른다.

| 현재 | 위치 |
| --- | --- |
| `assistant_ask` → `workflow_registry()` → 다른 Skill | [assistant_router.py:881-891](../workmate-agent/app/workflows/assistant_router.py#L881-L891) |
| `daily_briefing` → `rank_priorities` Workflow | [daily_briefing.py:139, 238](../workmate-agent/app/workflows/daily_briefing.py#L139) |

이대로 두면 Subgraph 합성(W4) 시 순환 의존이 된다. 처리 방침은 [30-3-5](30-3-5-design.md) §3·§4.

## 5. 범위 변경 절차

| 상황 | 처리 |
| --- | --- |
| 특정 Skill의 노드 분해안 변경 | 구현자 판단. 해당 Skill 문서 절 갱신 |
| State 스키마 변경 필요 | **한 Skill에서 먼저 검증한 뒤 확산.** 이미 만든 Subgraph의 수정 범위를 먼저 산정 |
| 공개 응답 모양 변경 필요 | 회귀일 가능성이 높다. 스냅샷 대조로 먼저 확인하고, 의도적 변경이면 사용자 승인 |
| Domain 규칙 변경 필요 | 범위 밖. 별도 백로그 |
| 숨은 부작용 제거 | [30-3-5](30-3-5-design.md) §3의 W3-D1 결정을 따른다 |

## 6. 참조

- [30-3-4](30-3-4-requirements.md) — 이 원칙들이 요구사항으로 구체화된 형태
- [30-3-5](30-3-5-design.md) — Skill별 노드 분해 설계
- [96번 §5·§6](96-workmate-langgraph-target-architecture.md) — 목표 노드 구성
