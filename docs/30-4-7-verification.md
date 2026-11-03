# W4-7 — 검증 설계

> [30-4-w4-root-graph.md](30-4-w4-root-graph.md) §7의 상세 문서.

## 1. 검증 목록

| ID | 검증 항목 | 대상 요구사항 | 방법 | 판정 기준 |
| --- | --- | --- | --- | --- |
| W4-V1 | 라우팅 | W4-R1, R6 | 11개 Skill 호출 | 해당 Subgraph 실행 |
| W4-V2 | 미등록 Skill | W4-R7 | 없는 `skill_id` | 정의된 오류 |
| W4-V3 | 멱등성 | W4-R2 | 동일 `message_id` 2회 | 두 번째는 미실행, 동일 결과 |
| W4-V4 | 식별자 보존 | W4-R4 | 종료 State 검사 | 5종 모두 입력과 동일 |
| W4-V5 | Schema 검증 | W4-R3, R10 | 정상·위반 결과 주입 | 위반은 `COMPLETED` 도달 실패 |
| W4-V6 | Root 경유 스냅샷 | 전체 | 케이스 27건 대조 | 전건 PASS |
| W4-V7 | Checkpoint 생성 | W4-R8 | `thread_id` 이력 조회 | 노드별 Snapshot 존재 |
| W4-V8 | 저장소 책임 분리 | W4-R5 | 쓰기 경로 검사 | 겹치지 않음 |
| W4-V9 | 기존 테스트 | 전체 | 회귀 실행 | 실패 0 |
| W4-V11 | **Graph 구조 산출물** | W4-R11 | `draw_mermaid()` | 코드와 일치하는 다이어그램 |

## 2. 검증 케이스 상세

### W4-V1 — 라우팅

**11개 각각을 호출한다.** 몇 개만 확인하면 path map 오타를 놓친다.

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V1-1~V1-11 | 각 `skill_id`로 Root Graph 실행 | 해당 Subgraph가 실행됨 |
| V1-12 | `assistant_ask` 실행 시 하위 Skill 호출 | 주입된 핸들로 실행됨 |
| V1-13 | `assistant_ask` → 하위 Skill의 `user_id` | **입력 `user_id`와 동일** |
| V1-14 | path map 키 집합 | 공개 Skill 11개와 정확히 일치(`runtime_bootstrap` 제외) |

**V1-13이 보안 항목이다.** Meta Skill이 하위 Skill을 호출할 때 `user_id`를 잃으면 권한 범위가
사라진다. [W3-V3-4](30-3-7-verification.md)와 같은 취지지만, 여기서는 **Root가 주입한 핸들**을 통한
경로를 본다.

### W4-V2 — 미등록 Skill

| 케이스 | 입력 | 기대 |
| --- | --- | --- |
| V2-1 | `skill_id="nonexistent"` | 정의된 예외(`WorkflowNotImplementedError` 계열) |
| V2-2 | `skill_id=""` | 동상 |
| V2-3 | `skill_id="runtime_bootstrap"` | **미등록 경로**(W4-D3) |
| V2-4 | 위 모든 경우 | 예외 타입이 500으로 매핑되지 않는다 |

V2-4는 W5에서 HTTP 매핑을 확인할 때 다시 본다. W4에서는 예외 타입만 확인한다.

### W4-V3 — 멱등성 (동작 변경 검증)

**W4-D1로 동작이 바뀌는 항목이므로 가장 꼼꼼히 본다.**

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V3-1 | 같은 `message_id` + 같은 payload 2회 | 두 번째는 **Skill 미실행**, 동일 결과 반환 |
| V3-2 | V3-1에서 Skill 실행 횟수 계측 | 1회 |
| V3-3 | 부작용 있는 Skill(`manage_tasks.create`)로 V3-1 | **Task가 1개만 생성** |
| V3-4 | 같은 `message_id` + **다른** payload | `ValueError`(기존 동작 유지) |
| V3-5 | 다른 `message_id` | 정상 실행 |
| V3-6 | 진행 중 중복 | W4-D5에서 정한 동작 |
| V3-7 | 복원된 결과의 식별자 | 입력과 동일(W4-R4) |

**V3-3이 이 변경의 가치를 보여준다.** 현재는 중복 요청 시 Task가 2개 생성된다. 변경 후에는 1개다.

**V3-4가 기존 동작 보존을 확인한다.** 해시 충돌 감지는 이미 있던 기능이므로 유지돼야 한다.

### W4-V4 — 식별자 보존

| 케이스 | 경로 | 기대 |
| --- | --- | --- |
| V4-1 | 정상 실행 | 종료 State의 5종이 입력과 동일 |
| V4-2 | **멱등성 복원 경로** | 동일 — `restore_result`가 식별자를 덮어쓰지 않는다 |
| V4-3 | Schema 검증 실패 경로 | 동일 |

V4-2가 중요하다. 복원은 저장된 응답을 State에 넣는데, 저장 당시의 식별자로 덮어쓰면 안 된다.

### W4-V5 — Schema 검증

| 케이스 | 입력 | 기대 |
| --- | --- | --- |
| V5-1 | **스냅샷 27건의 `expected`** | 전부 Schema 통과 |
| V5-2 | 필수 필드가 빠진 결과 주입 | `COMPLETED` 도달 실패 |
| V5-3 | 타입이 틀린 결과 주입 | 동상 |
| V5-4 | Schema 파일 로딩 실패 시뮬레이션 | **명시적 오류** — 조용히 통과하지 않음 |
| V5-5 | 배포 환경 경로에서 로딩 | 성공 |

**V5-1을 W4-T0에서 먼저 한다.** 실패하는 케이스가 있으면 현재 존재하는 계약 위반이므로, 구현 전에
알아야 한다.

**V5-4가 중요하다.** Schema 로딩이 실패했는데 검증을 건너뛰고 통과시키면, 검증이 꺼진 줄 모르고
배포된다.

### W4-V6 — Root 경유 스냅샷

```
uv run python -m unittest tests.contracts.test_contract_snapshots -v
```

단 하네스가 **Root Graph를 경유하도록** 설정한 상태로 실행한다.

| 케이스 | 기대 |
| --- | --- |
| V6-1 | 27건 전건 PASS |
| V6-2 | W3 대조 결과와 동일 | 공통 노드가 값을 바꾸지 않았다 |

**차이 발견 시 원인 후보**

| 후보 | 확인 |
| --- | --- |
| `initialize_state`의 `now`·`timezone` 주입 | 케이스의 `as_of`가 전달되는지 |
| `validate_contract` 거부 | V5-1 결과와 대조 |
| `build_artifact`의 Part 구성 | Artifact 이름·설명 비교 |
| 멱등성 경로 진입 | 케이스 간 `message_id` 격리 확인 |

### W4-V7 — Checkpoint

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V7-1 | Root Graph 실행 후 `thread_id`로 이력 조회 | 노드별 Snapshot 존재 |
| V7-2 | `thread_id = task_id` 확인 | 일치 |
| V7-3 | 두 백엔드(SQLite·Postgres) | 양쪽 모두 동작 |
| V7-4 | 멱등성 복원 경로 | Checkpoint도 남는다(짧은 경로) |
| V7-5 | **`get_state_history()` 출력을 증빙에 첨부** | 노드별 State·`next` 노드가 보인다 |

**V7-5는 검증이자 산출물이다.** "중간 상태가 사라지지 않는다"를 문장이 아니라 실물로 보여준다.

```python
for snapshot in graph.get_state_history(config):
    print(snapshot.next, snapshot.values.get("task_state"))
```

### W4-V11 — Graph 구조 산출물

LangGraph로 구현했음을 **코드가 아니라 실행 결과로** 증명하는 항목이다.

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V11-1 | `graph.get_graph().draw_mermaid()` | 컴파일된 Graph에서 생성된 다이어그램 |
| V11-2 | 생성된 다이어그램의 노드 목록 | Root 노드 7종 + Skill 11개와 일치 |
| V11-3 | 조건부 Edge 표현 | `route_skill`의 분기 11개가 보인다 |
| V11-4 | Subgraph 중첩 | Skill Subgraph의 내부 노드가 보인다(`xray` 옵션) |

**왜 검증 항목인가** 손으로 그린 그림은 코드와 어긋날 수 있다. `draw_mermaid()` 출력은 **실행 가능한
Graph 객체에서 나온 것**이므로 구조가 코드와 100% 일치한다. V11-2가 그 일치를 확인한다.

이 산출물은 [W9](30-9-w9-docs-evidence.md)의 97번 문서 개정에 그대로 쓰인다.

### W4-V8 — 저장소 책임 분리

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V8-1 | 실행 후 Checkpointer 저장 내용 검사 | **Task 상태·Artifact 없음** |
| V8-2 | 실행 후 Task Store 저장 내용 검사 | **노드 State 없음** |
| V8-3 | `idempotency_check`의 조회 대상 | Task Store(Checkpointer 아님) |
| V8-4 | 두 저장소의 연결 키 | `task_id ↔ thread_id`뿐 |

V8-3이 W4-K3(멱등성이 Checkpointer로 새어나감)의 검증이다.

### W4-V9 — 기존 테스트

```
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

| 항목 | 기대 |
| --- | --- |
| 기존 440건 | 전부 통과 — **W4 시점에도 운영 경로는 Registry다** |
| W1~W4 신규 | 전부 통과 |
| SKIP | 0 |

## 3. 검증 실행 순서

```
W4-T0에서 먼저:
  1. W4-V5-1  스냅샷 27건의 Schema 사전 검증

노드 구현 중:
  2. W4-V3    멱등성 (동작 변경이므로 가장 먼저 확인)
  3. W4-V5    Schema 검증
  4. W4-V4    식별자 보존

합성 후:
  5. W4-V1, V2  라우팅
  6. W4-V7, V8  Checkpoint·책임 분리

최종:
  7. W4-V6    Root 경유 스냅샷
  8. W4-V9    전체 회귀
```

## 4. 판정 규칙

- 검증은 PASS / FAIL 두 값
- **W4-V3(멱등성) FAIL이면 W5로 진행하지 않는다** — 멱등성은 공개 계약이고, 깨진 채 진입점을 바꾸면
  중복 실행이 외부에 노출된다
- W4-V5-1(사전 검증)에서 실패 케이스가 나오면 FAIL이 아니라 **보고 대상**이다. 현재 존재하는 계약
  위반을 발견한 것이므로 기록하고 판단을 받는다
- W4-V6 FAIL은 공통 노드의 문제다. Subgraph(W3)로 돌아가지 않는다

## 5. 검증 결과의 소비

| 결과 | 소비처 |
| --- | --- |
| W4-V3 PASS | [W5-E2](30-5-w5-entrypoint-swap.md) 선행 조건 |
| W4-V7 PASS | W5-E3, W6의 `interrupt` 전제 |
| W4-V6 | W5-V7의 기준선 |
| 멱등성 동작 변경 내역 | [W9](30-9-w9-docs-evidence.md) "의도적 변경" 분류 |
| Schema 사전 검증 결과 | W9 — 발견한 계약 위반 기록 |

## 6. 참조

- [30-4-4](30-4-4-requirements.md) — 검증 대상 요구사항
- [30-4-5](30-4-5-design.md) §3 — 멱등성 동작 변경의 배경
- [30-4-9](30-4-9-exit-criteria.md) — 승인 처리
