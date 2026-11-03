# W2-9 — 완료 정의와 승인 절차

> [30-2-w2-graph-foundation.md](30-2-w2-graph-foundation.md) §9의 상세 문서.

## 1. 완료 조건 (Exit criteria)

W2는 다음 네 가지를 모두 충족할 때 완료된다.

| # | 조건 | 판정 근거 |
| --- | --- | --- |
| E-1 | 검증 W2-V1~V9가 전부 PASS | [30-2-7](30-2-7-verification.md) |
| E-2 | `app/graph/`의 4개 모듈이 존재하고 공개 함수에 한글 Docstring이 있다 | 코드 검토 |
| E-3 | `uv.lock`이 갱신되고 기존 440개 테스트가 영향받지 않는다 | W2-V8 |
| E-4 | **W2-V7이 PASS** — 재시도 구분이 보존됐음이 증명됐다 | 계획서 §9-6 |

E-4를 따로 세운 이유는 이것이 D3=B의 최대 위험이자 전환 전체 완료 조건 중 하나이기 때문이다.
다른 검증이 전부 통과해도 E-4가 실패하면 W2는 완료가 아니다.

## 2. 산출물 체크리스트

### 2.1 코드

```
[ ] app/graph/__init__.py         공개면(W2 시점에는 비어 있어도 됨)
[ ] app/graph/state.py            WorkmateState, WarningState, Reducer
[ ] app/graph/adapter.py          state_from_request, result_from_state
[ ] app/graph/checkpointer.py     build_checkpointer
[ ] app/graph/llm.py              build_chat_model, is_network_error, RetryPolicy 2종
```

### 2.2 테스트

```
[ ] tests/test_graph_state.py         V1, V2, V9
[ ] tests/test_graph_adapter.py       V3
[ ] tests/test_graph_checkpointer.py  V4, V5
[ ] tests/test_graph_llm.py           V6, V7
```

### 2.3 의존성

```
[ ] pyproject.toml   langgraph, langgraph-checkpoint-sqlite,
                     langgraph-checkpoint-postgres, langchain-openai
[ ] uv.lock          갱신 + 기존 고정 버전 불변 확인
```

### 2.4 문서·증빙

```
[ ] docs/evidence/langgraph/W2/runs/{run_id}/result.md
[ ] docs/evidence/langgraph/README.md   W2 행 갱신
[ ] HANDOFF.md                          상태·다음 착수 항목
[ ] docs/30-langgraph-migration-plan.md §9-6 서술 정밀화
[ ] docs/30-2-5-design.md §5.2          실제 구현 결과 반영
```

### 2.5 §9-6 서술 정밀화가 필요한 이유

상위 계획서 §9-6은 "LLM 호출이 `langchain-openai` 경로로 바뀐 뒤에도 네트워크 오류만 재시도하고 HTTP
4xx/5xx는 즉시 실패한다"고 적혀 있다. 그러나 [30-2-5](30-2-5-design.md) §5.2 조사 결과 **재시도 정책이
두 종류**이며, `weekly_report` 계열은 429·5xx도 재시도한다.

따라서 §9-6은 "**`assistant_router` 계열은** 네트워크 오류만 재시도하고, **`weekly_report` 계열은 기존
2회 재시도 동작을 유지한다**"로 정밀화해야 한다. W2 완료 시 반영한다.

## 3. 승인 절차

### 3.1 자동 승인 대상 여부

`AGENTS.md`의 자동 승인 조건과 대조한다.

| 조건 | W2 해당 여부 |
| --- | --- |
| 정의된 검증 명령이 모두 정확히 PASS | 판정 대상 |
| 미실행·수동 검수·차단 항목 없음 | 판정 대상 |
| 외부 OAuth·실제 Provider 호출 | **없음** — W2는 고정 응답만 사용 |
| 공개 Schema·데이터 모델 변경 | **없음** — W2는 공개면을 바꾸지 않는다 |
| UI 육안 검수 | **없음** |
| 모델 평가 | **없음** |
| 원격 Push | **없음** — 로컬 커밋만 |

→ **W2는 자동 승인 대상이다.** 검증이 전부 PASS면 사용자 질문 없이 승인하고 W3을 착수한다.

### 3.2 자동 승인 시 기록 항목

```
latest_run_id:          {run_id}
latest_run_status:      PASS
latest_approved_run_id: {run_id}
approved_at:            {날짜} Asia/Seoul
reviewer:               자동 승인(검증 명령)
자동 재작업 착수:        예/아니오
자동 진행 판정:          진행 — W3 자동 착수
```

### 3.3 자동 승인이 불가한 경우

| 상황 | 처리 |
| --- | --- |
| 검증 1건 이상 FAIL | 자동 승인 중단. 현재 범위의 안전한 미실행 해결 방법이 남아 있으면 `재작업`으로 기록 후 자동 수정·재검수 |
| 동일 실패 반복 | 최종 중단, 사유·재현 명령·재개 조건 기록 |
| **의존성 충돌로 D3 재검토 필요** | 사용자 승인 대기. 임의로 A안(urllib 유지)으로 바꾸지 않는다 |
| W2-V6만 FAIL | W2는 미완료. 단 W3의 결정적 Skill은 선행 가능([30-3](30-3-w3-skill-subgraphs.md) W3-E3) |

### 3.4 자동 진행 보류 시 기록 의무

`AGENTS.md`에 따라 "왜 진행하지 않았는지"를 반드시 남긴다. 상태만 `대기`로 두지 않는다.

```
자동 진행 판정:     중단 / 보류 / 사용자 승인 대기
자동 진행 보류 사유: (구체적 사유)
판정을 막은 검증:    W2-Vx
미실행·차단 항목:    (목록)
필요한 조치·승인:    (내용)
재개 조건:          (조건)
다음 구현 백로그:    (ID)
```

## 4. 완료 판정 체크리스트

실행 순서대로 확인한다.

```
[ ] 1. 전체 테스트 실행 (Postgres 포함)
       → 440 + W1 스냅샷 + W2 신규, 실패 0, SKIP 0
[ ] 2. W2-V1~V9 각 항목의 PASS/FAIL 기록
[ ] 3. W2-V7의 호출 횟수 계측 결과를 증빙에 수치로 기록
[ ] 4. uv.lock diff 검토 — 기존 고정 버전 불변
[ ] 5. git diff --check
[ ] 6. Secret 패턴 검사 (코드·테스트·증빙 전체)
[ ] 7. 공개 함수 Docstring 한글 여부 검토
[ ] 8. 산출물 체크리스트(§2) 전항 확인
[ ] 9. result.md 작성
[ ] 10. evidence README·HANDOFF 갱신
[ ] 11. 논리 단위 커밋
[ ] 12. 자동 승인 판정 후 W3 착수
```

## 5. 완료 후 상태

| 항목 | W2 완료 시점의 상태 |
| --- | --- |
| 운영 경로 | **여전히 `WorkflowRegistry`** — 사용자에게 보이는 동작 변화 없음 |
| `app/graph/` | 4개 모듈 존재, 동작하지만 아무 데도 연결되지 않음 |
| `app/workflows/` | 그대로 존재 |
| 공개 계약 | 변경 없음 |
| DB 스키마 | 변경 없음 (Checkpointer 테이블은 첫 사용 시 생성) |
| 롤백 비용 | 낮음 — 커밋 revert로 충분 |

이 상태가 정상이다. W2에서 운영 동작이 바뀌었다면 범위를 벗어난 것이다.

## 6. 다음 단계 전달 사항

W2 완료 시 [W3](30-3-w3-skill-subgraphs.md)에 다음을 전달한다.

| 전달 항목 | 내용 |
| --- | --- |
| State 스키마 | Skill Subgraph가 사용할 공통 타입 |
| 어댑터 계약 | Skill 결과가 갖춰야 할 8개 필드 |
| LLM 경계 | `build_chat_model()`과 RetryPolicy 2종 |
| W2-V6 결과 | LLM 의존 Skill 착수 가부(W3-E3) |
| 정책 불일치 사실 | `weekly_report` 계열의 재시도가 다르다는 점 — W3-T4에서 주의 |
| 교체 대상 확정 결과 | [30-2-5](30-2-5-design.md) §5.3의 모듈별 판정 |

## 7. 참조

- [30-2-7](30-2-7-verification.md) — 검증 항목 정의
- [30-2-11](30-2-11-rollback.md) — 완료하지 못했을 때의 처리
- [`AGENTS.md`](../AGENTS.md) — 완료 규칙, 자동 승인 규칙
