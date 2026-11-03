# W2-1 — 문서 정보와 문서 체계

> [30-2-w2-graph-foundation.md](30-2-w2-graph-foundation.md) §1의 상세 문서.

## 1. 단계 식별

| 항목 | 값 |
| --- | --- |
| 단계 코드 | W2 |
| 단계명 | State·어댑터·Checkpointer·LLM 골격 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W1 계약 스냅샷](30-1-w1-contract-snapshot.md) |
| 후행 단계 | [W3 Skill Subgraph](30-3-w3-skill-subgraphs.md) |
| 상태 | 대기 |
| 관련 확정 결정 | D3=B(`langchain-openai` 도입), D6=B(Checkpointer 도입 + 옛 테이블 DROP) |

## 2. 단계 성격

W2는 **기반 공사(foundation) 단계**다. 사용자에게 보이는 동작은 하나도 바뀌지 않고, 운영 경로도 여전히
`WorkflowRegistry`다. 그런데도 이 단계가 전환 전체에서 위험도가 높은 이유는 두 가지다.

1. **후행 단계 전부가 여기 산출물 위에 쌓인다.** State 스키마나 어댑터 경계를 잘못 잡으면 W3에서
   Skill 11개를 만든 뒤에야 문제가 드러나고, 그때 고치면 11개를 모두 손봐야 한다.
2. **D3=B의 위험이 여기에 집중된다.** `langchain-openai` 도입은 의존성·구조화 출력·재시도 정책
   세 가지를 동시에 바꾼다. W2에서 막지 못하면 W3 이후 모든 LLM Skill이 영향을 받는다.

## 3. 문서 체계

W2 상세 계획은 상위 문서 [30-2](30-2-w2-graph-foundation.md)의 절 번호에 대응하는 12개 문서로 분해한다.

| 문서 | 대응 절 | 내용 |
| --- | --- | --- |
| [30-2-1](30-2-1-document-info.md) | §1 | 문서 정보·체계·용어·ID 규칙 (이 문서) |
| [30-2-2](30-2-2-scope.md) | §2 | 목적과 범위, 경계 근거, 범위 변경 절차 |
| [30-2-3](30-2-3-entry-criteria.md) | §3 | 선행 조건과 확인 절차 |
| [30-2-4](30-2-4-requirements.md) | §4 | 요구사항 명세 W2-R1~R11 |
| [30-2-5](30-2-5-design.md) | §5 | 설계 — 모듈 4종, LLM 호출 지점 전수 조사 |
| [30-2-6](30-2-6-wbs.md) | §6 | 작업 분해 W2-T1~T11 |
| [30-2-7](30-2-7-verification.md) | §7 | 검증 설계 W2-V1~V9 |
| [30-2-8](30-2-8-traceability.md) | §8 | 추적성 매트릭스 |
| [30-2-9](30-2-9-exit-criteria.md) | §9 | 완료 정의와 승인 절차 |
| [30-2-10](30-2-10-risks.md) | §10 | 위험 등록부 |
| [30-2-11](30-2-11-rollback.md) | §11 | 롤백·중단·재개 기준 |
| [30-2-12](30-2-12-references.md) | §12 | 참조 자료와 읽을 지점 |

상위 문서 [30-2](30-2-w2-graph-foundation.md)는 **요약과 색인** 역할을 유지한다. 두 문서가 충돌하면
상세 문서(30-2-x)를 기준으로 하고, 상위 문서를 맞춘다.

## 4. 식별자 규칙

| 접두 | 의미 | 예 | 정의 위치 |
| --- | --- | --- | --- |
| `W2-E` | 선행 조건 (Entry criteria) | `W2-E1` | [30-2-3](30-2-3-entry-criteria.md) |
| `W2-R` | 요구사항 (Requirement) | `W2-R9` | [30-2-4](30-2-4-requirements.md) |
| `W2-T` | 작업 (Task) | `W2-T8` | [30-2-6](30-2-6-wbs.md) |
| `W2-V` | 검증 (Verification) | `W2-V7` | [30-2-7](30-2-7-verification.md) |
| `W2-K` | 위험 (risK) | `W2-K3` | [30-2-10](30-2-10-risks.md) |

식별자는 **한 번 부여하면 재사용하지 않는다.** 항목이 삭제돼도 번호를 비워 두고 다음 번호를 쓴다.
증빙과 커밋 메시지가 번호로 이 문서를 참조하기 때문이다.

## 5. 용어

| 용어 | 정의 | 혼동 대상 |
| --- | --- | --- |
| **State** | Graph 실행 중 노드들이 공유하는 자료구조(`WorkmateState`) | A2A Task 상태(`TaskState`)와 다르다. 후자는 외부에 노출되는 Task 진행 상태다 |
| **Reducer** | 채널별 갱신 병합 함수 | 단순 덮어쓰기와 다르다. `warnings`는 누적 Reducer를 쓴다 |
| **Checkpoint** | 노드 실행 직후 State의 영속 스냅샷 | 기존 `a2a_checkpoints` 테이블의 행과 이름만 같다. 그쪽은 `submitted` 마커 한 줄뿐이었다 |
| **Checkpointer** | Checkpoint를 저장·복원하는 구성요소 | A2A Task Store와 책임이 다르다([30-2-5](30-2-5-design.md) §4) |
| **thread_id** | Checkpoint 묶음의 식별자 | 현재 구현은 `thread_id = task_id`로 둔다 |
| **어댑터(adapter)** | 전송 payload ↔ State ↔ 공개 응답 변환 경계 | `tools/m51_legacy_adapter.py`(오케스트레이터 어댑터)와 무관하다 |
| **구조화 출력** | JSON Schema를 강제해 LLM 응답을 고정 형태로 받는 방식 | 현재는 `response_format: json_schema` strict, 이후 `with_structured_output` |
| **노드 RetryPolicy** | LangGraph가 노드 단위로 재시도를 관리하는 설정 | 함수 내부 `for attempt in range(...)` 루프와 다르다. W2에서 후자를 전자로 옮긴다 |

## 6. 이해관계자와 역할

| 역할 | 책임 | 이 단계에서 |
| --- | --- | --- |
| 구현자 | 설계·구현·검증 실행 | W2-T1~T11 수행 |
| 사용자(승인자) | 결정 확정, 범위 변경 승인 | D3 재검토가 필요할 때만 관여([30-2-11](30-2-11-rollback.md) §3) |
| 후행 단계 | W2 산출물의 소비자 | W3가 State·어댑터·LLM 경계를 그대로 사용 |

W2는 UI 육안 검수·외부 OAuth·공개 Schema 변경을 포함하지 않으므로, 검증이 전부 PASS면
`AGENTS.md`의 자동 승인 대상이다([30-2-9](30-2-9-exit-criteria.md) §3).

## 7. 산출물 위치

```
workmate-agent/
  app/graph/
    __init__.py       (W4에서 채워짐 — W2에서는 빈 공개면만)
    state.py          W2-T2
    adapter.py        W2-T4
    checkpointer.py   W2-T6
    llm.py            W2-T8
  tests/
    test_graph_state.py        W2-T3
    test_graph_adapter.py      W2-T5
    test_graph_checkpointer.py W2-T7
    test_graph_llm.py          W2-T9, T10
  pyproject.toml / uv.lock     W2-T1
docs/evidence/langgraph/W2/runs/{run_id}/result.md   W2-T11
```

## 8. 변경 이력

| 일자 | 변경 | 사유 |
| --- | --- | --- |
| 2026-09-23 | 초판 (상위 문서 §1) | 단계별 상세 계획 수립 |
| 2026-09-28 | 12개 문서로 분해, LLM 호출 지점 전수 조사 결과 반영 | 절별 상세화 요청 |
