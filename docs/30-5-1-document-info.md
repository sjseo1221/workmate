# W5-1 — 문서 정보와 문서 체계

> [30-5-w5-entrypoint-swap.md](30-5-w5-entrypoint-swap.md) §1의 상세 문서.

## 1. 단계 식별

| 항목 | 값 |
| --- | --- |
| 단계 코드 | W5 |
| 단계명 | 진입점 교체 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W4 Root Graph](30-4-w4-root-graph.md) |
| 후행 단계 | [W6 interrupt·공개 계약](30-6-w6-interrupt-resume.md) |
| 상태 | 대기 |
| 관련 확정 결정 | D5=A(폴링 유지) |

## 2. 단계 성격 — 전환의 실질적 스위치

W5는 **운영 경로가 처음으로 Graph가 되는 단계**다.

```
W1 ─ W2 ─ W3 ─ W4 ──┬── W5 ─ W6 ─ W7 ─ W8 ─ W9
                    │
        운영 경로:  Registry │ Graph
        사용자 영향: 없음    │ 있음
        롤백 비용:  낮음    │ 중간
```

W4까지는 무슨 일이 생겨도 사용자에게 보이는 동작이 변하지 않았다. W5부터는 다르다.

### 2.1 W5가 작은 단계인 이유

교체 지점은 **3곳**이고, 각각 호출 한 덩어리를 바꾸는 일이다. 설계는 이미 W4에 있다.

| # | 위치 | 바꾸는 것 |
| --- | --- | --- |
| 1 | [runtime.py:236-244](../workmate-agent/app/a2a/runtime.py#L236) | `registry.execute(...)` → `graph.ainvoke(...)` |
| 2 | [internal_chat.py:318-327](../workmate-agent/app/internal_chat.py#L318) | 동기 경로 |
| 3 | [internal_chat.py:391-400](../workmate-agent/app/internal_chat.py#L391) | 백그라운드 경로 |

### 2.2 그런데 위험은 크다

코드 변경량과 위험이 비례하지 않는다. W5에서 신경 쓸 것은 Graph가 아니라 **그 주변의 계약**이다.

| 계약 | 왜 깨지기 쉬운가 | 과거 사고 |
| --- | --- | --- |
| A2A 이벤트 순서 | Graph 실행이 끼어들면서 순서가 바뀔 수 있다 | 2026-08-14 Orchestrator가 빈 결과를 읽음 |
| 오류 → HTTP 매핑 | Graph가 예외를 감싸면 422/503이 500이 된다 | 2026-08-15 `Failed to fetch`만 보임 |
| Route allowlist | 변경 대상이 아니지만 확인 필요 | — |
| 비동기 Task 상태 | 백그라운드 예외가 삼켜지면 영원히 `submitted` | — |

세 가지가 전부 **실사용 중 발견된 문제**다. W5는 이것들을 재발시키지 않는 것이 본질이다.

## 3. 문서 체계

| 문서 | 대응 절 | 내용 |
| --- | --- | --- |
| [30-5-1](30-5-1-document-info.md) | §1 | 문서 정보·체계·용어 (이 문서) |
| [30-5-2](30-5-2-scope.md) | §2 | 목적, 교체 지점 3곳, 범위 |
| [30-5-3](30-5-3-entry-criteria.md) | §3 | 선행 조건 |
| [30-5-4](30-5-4-requirements.md) | §4 | 요구사항 W5-R1~R10 |
| [30-5-5](30-5-5-design.md) | §5 | 설계 — 교체 전후, 오류 경계, 비동기 경로, **message_id 문제** |
| [30-5-6](30-5-6-wbs.md) | §6 | 작업 분해 W5-T1~T9 |
| [30-5-7](30-5-7-verification.md) | §7 | 검증 설계 W5-V1~V10 |
| [30-5-8](30-5-8-traceability.md) | §8 | 추적성 매트릭스 |
| [30-5-9](30-5-9-exit-criteria.md) | §9 | 완료 정의 |
| [30-5-10](30-5-10-risks.md) | §10 | 위험 등록부 |
| [30-5-11](30-5-11-rollback.md) | §11 | 롤백·중단 기준 |
| [30-5-12](30-5-12-references.md) | §12 | 참조 자료 |

## 4. 식별자 규칙

| 접두 | 의미 | 예 |
| --- | --- | --- |
| `W5-E` | 선행 조건 | `W5-E2` |
| `W5-R` | 요구사항 | `W5-R4` |
| `W5-T` | 작업 | `W5-T5` |
| `W5-V` | 검증 | `W5-V2` |
| `W5-K` | 위험 | `W5-K1` |
| `W5-D` | 설계 결정 | `W5-D1` |

## 5. 용어

| 용어 | 정의 | 주의 |
| --- | --- | --- |
| **진입점(entrypoint)** | 외부 요청이 업무 로직에 들어오는 지점 | A2A Executor와 UI REST Route 두 종류 |
| **이벤트 순서** | A2A SDK가 발행하는 Task 이벤트의 순서 | `submitted → working → artifact → completed` |
| **오류 매핑** | 예외 타입 → HTTP 상태 코드 변환 | `ValueError`→422, `RuntimeError`→503 |
| **Route allowlist** | 공개하는 SDK Route 목록 | 5개. W5에서 바꾸지 않는다 |
| **`_ASYNC_SKILLS`** | 백그라운드 실행 + 폴링을 쓰는 Skill 집합 | `analyze_meeting`, `assistant_ask` |
| **폴링** | 클라이언트가 주기적으로 Task 상태를 조회 | D5=A로 유지 |

## 6. 교체 대상 파일

| 파일 | 바꾸는 부분 | 안 바꾸는 부분 |
| --- | --- | --- |
| [runtime.py](../workmate-agent/app/a2a/runtime.py) | `execute()`의 Workflow 호출 | Agent Card, Route allowlist, 인증, Task Store 생성 |
| [internal_chat.py](../workmate-agent/app/internal_chat.py) | 동기·비동기 Workflow 호출 | 인증(JWT/JWKS), 입력 Schema 검증, 폴링 Route |
| [main.py](../workmate-agent/app/main.py) | Checkpointer 수명 결합(신규) | Event Loop·IPv4 설정, Router 등록 |

## 7. 산출물 위치

```
workmate-agent/
  app/a2a/runtime.py          교체
  app/internal_chat.py        교체
  app/main.py                 Checkpointer lifespan 결합
  tests/
    test_runtime_boot.py      이벤트 순서 검증 계승
    test_internal_chat.py     오류 매핑·비동기 경로 계승
docs/evidence/langgraph/W5/runs/{run_id}/result.md
```

## 8. 변경 이력

| 일자 | 변경 | 사유 |
| --- | --- | --- |
| 2026-09-23 | 초판 (상위 문서 §1) | 단계별 상세 계획 |
| 2026-09-29 | 12개 문서로 분해, W4에서 넘어온 `message_id` 문제 반영 | 절별 상세화 요청 |
