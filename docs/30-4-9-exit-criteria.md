# W4-9 — 완료 정의

> [30-4-w4-root-graph.md](30-4-w4-root-graph.md) §9의 상세 문서.

## 1. 완료 조건 (Exit criteria)

| # | 조건 | 판정 근거 |
| --- | --- | --- |
| E-1 | `build_workmate_graph()`로 컴파일된 Graph가 Skill 11개를 전부 실행할 수 있다 | W4-V1 |
| E-2 | **W4-V6(Root 경유 스냅샷 대조)이 전건 PASS** | W4-V6 |
| E-3 | W4-V3(멱등성)·V7(Checkpoint) PASS | 각 검증 |
| E-4 | 운영 경로는 **아직 기존 Registry**이고 전체 테스트가 통과한다 | W4-V9 |
| E-5 | 동작 변경 3건(W4-D1·D3·D5)이 내역과 함께 기록됐다 | 증빙 |

### 1.1 E-5를 따로 세운 이유

W4는 **스냅샷으로 검출되지 않는 동작 변경을 세 건 도입하는 단계**다.

| 변경 | 내용 |
| --- | --- |
| W4-D1 | 중복 `message_id` 요청이 재실행되지 않는다 |
| W4-D3 | `runtime_bootstrap`이 미등록 Skill로 처리된다 |
| W4-D5 | 진행 중 중복 요청의 동작이 정의된다 |

기록하지 않으면 W9에서 "설명 불가 차이"로 분류할 근거가 없고, 나중에 이 동작을 보고 "언제 왜
바뀌었나"를 알 수 없다.

### 1.2 E-4의 의미

W4까지는 **사용자에게 보이는 동작이 하나도 바뀌지 않는다.** 위 세 변경도 Graph 내부에만 존재하고,
운영 경로가 Graph를 부르는 것은 W5다.

기존 440건이 통과한다는 것이 이를 증명한다.

## 2. 산출물 체크리스트

### 2.1 코드

```
[ ] app/graph/nodes/initialize.py     initialize_state
[ ] app/graph/nodes/idempotency.py    idempotency_check, restore_result
[ ] app/graph/nodes/routing.py        route_skill
[ ] app/graph/nodes/contract.py       validate_contract
[ ] app/graph/nodes/artifact.py       build_artifact
[ ] app/graph/nodes/persist.py        persist_result
[ ] app/graph/root.py                 Root StateGraph 조립
[ ] app/graph/__init__.py             build_workmate_graph() 공개
```

### 2.2 테스트

```
[ ] tests/test_graph_root.py          V1~V5, V7, V8
[ ] 스냅샷 하네스의 Root 경유 모드    V6
```

### 2.3 문서·증빙

```
[ ] docs/evidence/langgraph/W4/runs/{run_id}/result.md
[ ] docs/evidence/langgraph/README.md   W4 행 갱신
[ ] HANDOFF.md
[ ] W4-T0의 Schema 사전 검증 결과
[ ] 동작 변경 3건의 내역 (W9 전달용)
[ ] 진행 중 중복 정책(W4-D5) 확정 내용
```

## 3. 승인 절차

### 3.1 자동 승인 대상 여부

| 조건 | W4 해당 여부 |
| --- | --- |
| 외부 OAuth·실제 Provider 호출 | 없음 |
| **공개 Schema·데이터 모델 변경** | **없음** — 단 §3.2 참조 |
| UI 육안 검수 | 없음 |
| 모델 평가 | 없음 |
| 원격 Push | 없음 |

→ 원칙적으로 **자동 승인 대상**이다.

### 3.2 다만 판단이 필요한 경계

W4-D1(멱등성)은 공개 **Schema**를 바꾸지 않지만 공개 **동작**을 바꾼다. 같은 요청을 두 번 보냈을 때
외부가 관찰하는 결과가 달라진다.

| 관점 | 판정 |
| --- | --- |
| Schema 변경인가 | 아니다 — 필드·타입 불변 |
| 계약 변경인가 | **02번 문서의 멱등성 계약을 처음으로 실제 구현하는 것**이다 |
| 사용자 승인이 필요한가 | [계획서 §0.1](30-langgraph-migration-plan.md)의 "운영 중 아님 + 설계 정합성 우선" 전제에 부합하므로 **자동 승인 가능** |

**단, 증빙에 명시하고 W9에서 다시 보고한다.** 자동 승인이 "조용히 넘어감"을 뜻하지 않는다.

만약 W4-T0 시점에 이 판단이 부담스러우면 사용자에게 확인을 받는다 — 되돌리기보다 미리 묻는 편이 싸다.

### 3.3 자동 승인 시 기록

```
latest_run_id:          {run_id}
latest_run_status:      PASS
latest_approved_run_id: {run_id}
approved_at:            {날짜} Asia/Seoul
reviewer:               자동 승인(검증 명령)
자동 재작업 착수:        예/아니오
자동 진행 판정:          진행 — W5 자동 착수
동작 변경:              3건 (W4-D1 멱등성, W4-D3 runtime_bootstrap, W4-D5 진행 중 중복)
```

### 3.4 자동 승인이 불가한 경우

| 상황 | 처리 |
| --- | --- |
| **W4-V3(멱등성) FAIL** | W5 진행 금지. 공개 계약이 깨진 채 진입점을 바꿀 수 없다 |
| W4-V5-1에서 스냅샷 케이스가 Schema 위반 | **보고 대상.** 현재 존재하는 계약 위반을 발견한 것 |
| W4-V6 차이가 "의도적"으로 보임 | W4에서 의도적 변경은 §1.1의 3건뿐. 그 외는 회귀 |
| Task Store 구조 변경이 필요해짐 | 범위 이탈. 보고 |

## 4. 완료 후 상태

| 항목 | W4 완료 시점 |
| --- | --- |
| 운영 경로 | **여전히 `WorkflowRegistry`** |
| `app/graph/` | Root + Subgraph 11개, 테스트에서만 실행 |
| `app/workflows/` | 그대로 존재 |
| 공개 응답 모양 | 변경 없음 |
| 공개 동작 | 변경 없음(Graph 내부에만 존재) |
| DB | Checkpointer 테이블이 생성됨 |
| 롤백 비용 | 낮음 — 커밋 revert |

## 5. 완료 판정 체크리스트

```
[ ] 1. W4-V5-1 스냅샷 27건의 Schema 사전 검증 (W4-T0에서 수행)
[ ] 2. W4-V1 라우팅 11개 각각 + path map 일치 + user_id 전달
[ ] 3. W4-V2 미등록 Skill 3종
[ ] 4. W4-V3 멱등성 7케이스 — 특히 V3-3(부작용 Skill 중복 실행 방지)
[ ] 5. W4-V4 식별자 보존 (복원 경로 포함)
[ ] 6. W4-V5 Schema 검증 (로딩 실패 시 명시적 오류 포함)
[ ] 7. W4-V7 Checkpoint 양 백엔드
[ ] 8. W4-V8 저장소 책임 분리
[ ] 9. W4-V6 Root 경유 스냅샷 전건 PASS
[ ] 10. W4-V9 전체 회귀 (Postgres 포함, SKIP 0)
[ ] 11. 동작 변경 3건 내역 기록
[ ] 12. git diff --check, Secret 검사, Docstring 한글 검토
[ ] 13. result.md, evidence README, HANDOFF 갱신
[ ] 14. 자동 승인 판정 후 W5 착수
```

## 6. 다음 단계 전달 사항

| 전달 항목 | 받는 단계 | 용도 |
| --- | --- | --- |
| `build_workmate_graph()` | [W5](30-5-w5-entrypoint-swap.md) | 진입점이 호출할 대상 |
| W4-V3 PASS | W5-E2 | 진입점 교체의 전제 |
| W4-V7 PASS | W5-E3, W6 | `interrupt`의 전제 |
| W4-V6 결과 | W5-V7 | 운영 경로 대조의 기준선 |
| 멱등성 구현 내용 | W5 | A2A·UI REST 경로의 `message_id` 생성 방식을 어떻게 맞출지 |
| 동작 변경 3건 | [W9](30-9-w9-docs-evidence.md) | 의도적 변경 분류 |

### 6.1 W5에 특별히 넘기는 것

W4에서 멱등성을 제대로 구현하면, **UI REST 경로의 `message_id` 생성 방식이 문제가 된다.**

현재 [internal_chat.py:267](../workmate-agent/app/internal_chat.py#L267)은
`message_id = f"internal-{task_id}"`이고 `task_id`가 매 요청 새 `uuid4()`다. 즉 멱등성이 영원히
발동하지 않는다.

W5에서 이를 그대로 둘지, 클라이언트가 보낸 식별자를 쓰도록 바꿀지 결정해야 한다. **W5의 설계
항목으로 넘긴다.**

## 7. 참조

- [30-4-7](30-4-7-verification.md) — 검증 항목
- [30-4-11](30-4-11-rollback.md) — 완료하지 못했을 때
- [`AGENTS.md`](../AGENTS.md) — 완료 규칙
