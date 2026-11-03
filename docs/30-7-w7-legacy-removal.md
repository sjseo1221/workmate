# W7 — 레거시 삭제·모듈 이동·Migration

> **이 문서는 요약과 색인이다.** 각 절의 상세는 아래 12개 문서에 있고, 충돌 시 상세 문서를 기준으로
> 한다.
>
> | 절 | 상세 문서 | 내용 |
> | --- | --- | --- |
> | §1 | [30-7-1](30-7-1-document-info.md) | 문서 정보·용어·삭제 대상 목록 |
> | §2 | [30-7-2](30-7-2-scope.md) | 목적, 삭제·이동·DROP 범위 |
> | §3 | [30-7-3](30-7-3-entry-criteria.md) | 선행 조건 — **W6 승인 + 검증 기간** |
> | §4 | [30-7-4](30-7-4-requirements.md) | 요구사항 W7-R1~R10 |
> | §5 | [30-7-5](30-7-5-design.md) | 설계 — 삭제 순서, **증빙 링크 처리**, Migration |
> | §6 | [30-7-6](30-7-6-wbs.md) | 작업 분해 W7-T1~T12, **비가역 작업 전 관문** |
> | §7 | [30-7-7](30-7-7-verification.md) | 검증 설계 W7-V1~V10 |
> | §8 | [30-7-8](30-7-8-traceability.md) | 추적성, 삭제×대체처, 비가역 작업 추적 |
> | §9 | [30-7-9](30-7-9-exit-criteria.md) | 완료 정의 |
> | §10 | [30-7-10](30-7-10-risks.md) | 위험 등록부 W7-K1~K9 |
> | §11 | [30-7-11](30-7-11-rollback.md) | 롤백·중단·재개, **비가역 작업 취급** |
> | §12 | [30-7-12](30-7-12-references.md) | 참조 자료와 읽을 지점 |
>
> **W7의 특징 셋.**
> (1) **아무것도 만들지 않는다.** 없애고 옮기는 것이 전부인데 위험 등록부에 9건이 있다 — 전부
> 삭제에 관한 것이다.
> (2) **`AGENTS.md` 의존도가 가장 높다.** 요구사항 10개 중 3개가 증빙 규칙·금지 사항에서 나온다.
> 특히 증빙 링크는 "본문을 고치지 말라"와 "링크가 실재 파일을 가리켜야 한다"가 충돌하는데, **경로만
> 정정**하는 것으로 해결한다([30-7-5](30-7-5-design.md) §4).
> (3) **비가역 작업이 있다.** `a2a_checkpoints` DROP은 되돌릴 수 없고, `app/workflows/` 삭제는
> W5·W6의 롤백 착지점을 없앤다. 그래서 코드 정리 → **전체 검증(관문)** → Migration 순서를 지키고,
> Migration을 마지막 커밋으로 분리한다. 이 시점부터 **W1 스냅샷도 재작성할 수 없다.**

## 1. 문서 정보

| 항목 | 값 |
| --- | --- |
| 단계 | W7 |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W6 interrupt·공개 계약](30-6-w6-interrupt-resume.md) |
| 후행 단계 | [W8 재시도와 관측](30-8-w8-retry-observability.md) |
| 상태 | 대기 |
| 관련 결정 | D4=A(모듈 이동), D6=B(`a2a_checkpoints` DROP) |
| 성격 | **비가역 작업 포함** (DB Migration) |

## 2. 목적과 범위

### 2.1 목적

전환의 완결 조건인 "실행 경로는 하나"를 실제로 만든다. 이중 구조가 남아 있으면 다음 작업자가 어느 쪽이
운영 경로인지 알 수 없다.

### 2.2 범위 내

| 작업 | 대상 |
| --- | --- |
| 삭제 | `app/workflows/` 패키지, `WorkflowRegistry`, `WorkflowRequest`/`WorkflowResult` |
| 이동 | `weekly_classification.py` → `app/domain/`, `external_sync.py` → `app/sync/` |
| Migration | `a2a_checkpoints` 테이블 DROP |
| 정리 | `save_checkpoint()`·`_save_checkpoint_sync()` 제거 |
| 문서 | 이동에 따른 승인 증빙 링크 경로 갱신 |

### 2.3 범위 외

- 새 기능 추가
- Task Store 구조 변경 (외부 원장은 유지)
- 관련 없는 파일 정리·대규모 포맷 변경 (`AGENTS.md` 금지)

## 3. 선행 조건

| ID | 조건 | 확인 방법 |
| --- | --- | --- |
| W7-E1 | W5 완료 — 운영 경로가 Graph | W5-V7 |
| W7-E2 | W6 완료 — 확인·재개가 Graph에서 동작 | W6-V3 |
| W7-E3 | 스냅샷 전건 PASS(의도적 변경 반영 후) | W6-T9 |
| W7-E4 | `app/`에 `WorkflowRegistry` 호출자 없음 | `grep -rn "workflow_registry\|WorkflowRegistry" app` |

## 4. 요구사항

| ID | 구분 | 요구사항 | 출처 |
| --- | --- | --- | --- |
| W7-R1 | 기능 | `app/workflows/` 패키지를 삭제한다 | 계획서 §9-1 |
| W7-R2 | 기능 | `weekly_classification`을 `app/domain/`으로 이동한다 | D4=A |
| W7-R3 | 기능 | `external_sync`를 `app/sync/`로 이동한다(삭제 금지) | D4=A |
| W7-R4 | 기능 | `a2a_checkpoints` 테이블을 DROP하는 Migration을 추가한다 | D6=B |
| W7-R5 | 기능 | `save_checkpoint()` 관련 코드를 제거한다 | D6=B |
| W7-R6 | 제약 | 이동한 모듈을 참조하는 승인 증빙의 링크를 유효하게 유지한다 | `AGENTS.md` 증빙 규칙 |
| W7-R7 | 제약 | 승인 증빙 본문을 수정·삭제하지 않는다(경로만 정정) | `AGENTS.md` 금지 사항 |
| W7-R8 | 제약 | 전환과 무관한 파일을 함께 정리하지 않는다 | `AGENTS.md` 금지 사항 |

## 5. 설계

### 5.1 삭제 대상과 대체처

| 삭제 | 줄 수 | 대체 |
| --- | --- | --- |
| `app/workflows/registry.py` | 약 100 | `app/graph/state.py` + `app/graph/adapter.py` + Root 라우팅 |
| `app/workflows/priority.py` | 161 | `app/graph/skills/rank_priorities.py` |
| `app/workflows/daily_briefing.py` | 368 | `app/graph/skills/daily_briefing.py` |
| `app/workflows/weekly_report.py` | 368 | `app/graph/skills/weekly_report.py` |
| `app/workflows/meetings.py` | 467 | `app/graph/skills/{analyze,search}_meeting*.py` |
| `app/workflows/assistant_skills.py` | 387 | `app/graph/skills/assistant_skills/` |
| `app/workflows/assistant_router.py` | 937 | `app/graph/skills/assistant_router.py` |

### 5.2 이동 대상 (D4=A)

**`weekly_classification.py` → `app/domain/`**

I/O 없는 순수 함수(`link_approved_tasks`·`link_action_item_tasks`·`build_weekly_report_data`·
`extract_next_week_plans`)다. 96번 §10의 Domain 계층 정의에 부합한다.

**`external_sync.py` → `app/sync/`**

Skill이 아니고 HTTP Route·스케줄러에 연결돼 있지 않다([dev_gmail_sync_api.py:3](../workmate-agent/app/dev_gmail_sync_api.py#L3)
주석: "운영 자동 동기화 Job은 아직 없다"). 그러나 **삭제하지 않는다** — 아래 승인 증빙이 이 경로를
참조하기 때문이다.

| 증빙 | 위치 | 상태 |
| --- | --- | --- |
| M1.2-04 Cursor·Watch 동기화 | [06-delivery-plan.md:91](06-delivery-plan.md#L91) | 완료 |
| M1.4-01 제안 Hub·SSE 발행 | [06-delivery-plan.md:769](06-delivery-plan.md#L769) | 완료 |
| `docs/evidence/` 참조 | 2건 | 승인됨 |

### 5.3 증빙 링크 처리 (W7-R6·R7)

`AGENTS.md`는 (1) 승인 증빙을 덮어쓰거나 삭제하지 않을 것, (2) 증빙의 구현 경로는 저장소 내 실재
파일로 연결할 것을 동시에 요구한다. 파일을 옮기면 둘이 충돌한다.

**해결 방식:** 증빙 본문의 서술은 그대로 두고 **링크 경로만** 새 위치로 정정한다. 정정 사실은 W7
증빙에 기록한다. 서술·판정·승인 정보는 건드리지 않는다.

### 5.4 Migration (D6=B)

```sql
-- migrations/0NN_drop_a2a_checkpoints.sql
DROP TABLE IF EXISTS a2a_checkpoints;
```

- 이 테이블은 [runtime.py:228](../workmate-agent/app/a2a/runtime.py#L228)에서 `{task_id}:submitted` 마커를
  쓰기만 했고 읽는 코드가 없었다(W0 §10.2). 기능 손실이 없다.
- 운영 배포 중이 아니고 기존 데이터 파기가 무방함을 사용자가 확인했다(계획서 §0.1, 2026-09-23).
- **비가역.** W7-V6(Migration 재실행 안전성) 확인 후 적용한다.

### 5.5 삭제 순서

역의존 순서로 지운다. 참조가 남은 채 파일을 지우면 import 오류로 원인 파악이 어려워진다.

```
1. app/ 안의 잔여 참조 제거 확인 (W7-E4)
2. 모듈 이동 (weekly_classification, external_sync) + import 경로 갱신
3. 테스트의 import 경로 갱신
4. app/workflows/ 삭제
5. save_checkpoint 관련 코드 제거
6. Migration 추가·적용
7. 증빙 링크 정정
```

## 6. 작업 분해 (WBS)

| ID | 작업 | 선행 | 산출물 |
| --- | --- | --- | --- |
| W7-T1 | 잔여 참조 전수 조사 | — | 참조 목록 |
| W7-T2 | `weekly_classification` 이동 + import 갱신 | W7-T1 | `app/domain/` |
| W7-T3 | `external_sync` 이동 + import 갱신 | W7-T1 | `app/sync/` |
| W7-T4 | 관련 테스트 import 갱신 | W7-T2, T3 | 테스트 3건 |
| W7-T5 | `app/workflows/` 삭제 | W7-T4 | — |
| W7-T6 | `save_checkpoint` 관련 코드 제거 | W7-T5 | `persistence.py`, `runtime.py` |
| W7-T7 | DROP Migration 작성 | W7-T6 | `migrations/0NN_*.sql` |
| W7-T8 | Migration 계약 테스트 추가 | W7-T7 | `tests/test_migration.py` |
| W7-T9 | 증빙 링크 경로 정정 | W7-T3 | `06-delivery-plan.md`, evidence 2건 |
| W7-T10 | 전체 검증 | W7-T8, T9 | 실행 로그 |
| W7-T11 | 증빙·커밋 | W7-T10 | `result.md` |

## 7. 검증 설계

| ID | 검증 항목 | 방법 | 판정 기준 |
| --- | --- | --- | --- |
| W7-V1 | 레거시 부재 | `grep -rn "WorkflowRegistry" app` | 출력 없음 |
| W7-V2 | 패키지 삭제 | `ls app/workflows` | 존재하지 않음 |
| W7-V3 | 이동 모듈 동작 | 관련 테스트 실행 | PASS |
| W7-V4 | import 무결성 | `uv run python -m compileall -q app tests` | 오류 없음 |
| W7-V5 | 테이블 DROP | Migration 적용 후 스키마 조회 | `a2a_checkpoints` 부재 |
| W7-V6 | Migration 재실행 안전성 | 2회 적용 | 오류 없음(멱등) |
| W7-V7 | 증빙 링크 유효성 | 링크 대상 파일 존재 확인 | 깨진 링크 0 |
| W7-V8 | 증빙 본문 불변 | `git diff` 검토 | 경로 외 변경 없음 |
| W7-V9 | 스냅샷 | 전건 대조 | PASS |
| W7-V10 | 전체 테스트 | 스위트 실행 (Postgres 포함) | 실패 0, SKIP 0 |

## 8. 추적성 매트릭스

| 요구사항 | 작업 | 검증 |
| --- | --- | --- |
| W7-R1 | W7-T5 | W7-V1, V2 |
| W7-R2 | W7-T2 | W7-V3, V4 |
| W7-R3 | W7-T3 | W7-V3, V4 |
| W7-R4 | W7-T7, T8 | W7-V5, V6 |
| W7-R5 | W7-T6 | W7-V4 |
| W7-R6 | W7-T9 | W7-V7 |
| W7-R7 | W7-T9 | W7-V8 |
| W7-R8 | 전 작업 | `git diff --stat` 검토 |

## 9. 완료 정의 (Exit criteria)

1. W7-V1~V10 전부 PASS.
2. `app/workflows/`가 저장소에 없고, 이동한 두 모듈이 새 위치에서 동작한다.
3. `a2a_checkpoints`가 DROP되고 Migration이 멱등하다.
4. 승인 증빙의 링크가 전부 유효하며 본문은 변경되지 않았다.

## 10. 위험과 완화

| 위험 | 영향 | 완화 |
| --- | --- | --- |
| **DROP Migration은 비가역** | 되돌리기 불가 | W7-V6 먼저 확인. 운영 중이 아니며 파기 무방함을 사용자가 확인(§5.4) |
| 잔여 참조를 놓쳐 런타임에만 실패 | 특정 경로에서 장애 | W7-T1 전수 조사 + W7-V4 `compileall` |
| 증빙 링크가 깨져 완료 판정 근거가 사라진다 | M1.2-04·M1.4-01 추적 불가 | W7-T9 + W7-V7 |
| 삭제 김에 관련 없는 파일을 정리한다 | 리뷰 불가능한 대형 diff | W7-R8, `git diff --stat` 검토 |
| 이동 모듈의 테스트가 함께 깨진다 | 회귀 | W7-T4를 삭제(W7-T5)보다 먼저 |

## 11. 롤백·중단 기준

- 코드 삭제·이동은 revert로 되돌릴 수 있다. **Migration은 되돌릴 수 없다.**
- 따라서 커밋 순서를 `코드 정리 → 검증 → Migration`으로 두고, Migration을 마지막 커밋으로 분리한다.
- **중단 기준:** W7-V10(전체 테스트, Postgres 포함)이 PASS하기 전에는 Migration을 적용하지 않는다.

## 12. 참조

- [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §2.3, §4 D4·D6, §9
- [`AGENTS.md`](../AGENTS.md) 완료 규칙·금지 사항
- [06-delivery-plan.md](06-delivery-plan.md) — 링크 정정 대상
