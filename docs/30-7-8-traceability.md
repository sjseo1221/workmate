# W7-8 — 추적성 매트릭스

> [30-7-w7-legacy-removal.md](30-7-w7-legacy-removal.md) §8의 상세 문서.

## 1. 전방 추적 (요구사항 → 작업 → 검증)

| 요구사항 | 한 줄 | 작업 | 검증 | 우선순위 |
| --- | --- | --- | --- | --- |
| W7-R1 | 패키지 삭제 | W7-T5 | W7-V1, V2 | 필수 |
| W7-R2 | `weekly_classification` 이동 | W7-T2 | W7-V3 | 필수 |
| W7-R3 | `external_sync` 이동 | W7-T3 | W7-V3 | 필수 |
| W7-R4 | DROP Migration | W7-T8, T10 | W7-V5, V6 | 필수 |
| W7-R5 | Checkpoint 코드 제거 | W7-T6 | W7-V4 | 필수 |
| W7-R6 | 증빙 링크 유효성 | W7-T11 | **W7-V7** | **필수** |
| W7-R7 | 증빙 본문 불변 | W7-T11 | **W7-V8** | **필수** |
| W7-R8 | 무관한 정리 금지 | 전 작업 | `git diff --stat` | 필수 |
| W7-R9 | 이동 모듈 무수정 | W7-T2, T3 | W7-V3-5 | 필수 |
| W7-R10 | Migration 계약 테스트 정합 | W7-T9 | W7-V5-4, V5-5 | 필수 |

**누락 검사:** 없음.

## 2. 후방 추적 (작업 → 요구사항)

| 작업 | 근거 요구사항 | 비고 |
| --- | --- | --- |
| W7-T1 | 전체 (전제) | 조사 |
| W7-T2 | R2, R9 | |
| W7-T3 | R3, R9 | |
| W7-T4 | R1 (전제) | **삭제보다 먼저여야 한다** |
| W7-T5 | R1 | |
| W7-T6 | R5 | |
| W7-T7 | — | **Migration 전 관문** |
| W7-T8 | R4 | |
| W7-T9 | R10 | |
| W7-T10 | R4 | **비가역** |
| W7-T11 | R6, R7 | |
| W7-T12 | — (증빙) | |

**W7-T7만 요구사항 근거가 없다.** 이는 프로세스 안전 장치다 — 비가역 작업 전에 되돌릴 수 있는
상태를 확인한다.

## 3. 후방 추적 (검증 → 요구사항)

| 검증 | 보장 대상 | 실패 시 영향 |
| --- | --- | --- |
| W7-V1 | R1 | 죽은 코드가 남아 혼란 |
| W7-V2 | R1 | 동상 |
| W7-V3 | R2, R3, R9 | 이동 모듈이 동작하지 않음 |
| W7-V4 | R5 | import 오류로 앱 기동 실패 |
| W7-V5 | R4, R10 | 테이블이 남음 |
| W7-V6 | R4 | Migration 재적용 시 오류 |
| W7-V7 | R6 | **승인 증빙의 근거가 사라짐** |
| W7-V8 | R7 | **`AGENTS.md` 위반** |
| W7-V9 | 전체 | 삭제가 동작을 바꿈 |
| W7-V10 | 전체 | 기준선 붕괴 |

## 4. 삭제 대상 × 대체처 추적

무엇이 무엇으로 대체됐는지. 삭제의 정당성을 보여준다.

| 삭제 | 줄 | 대체 | 대체 단계 | 검증 |
| --- | --- | --- | --- | --- |
| `registry.py` | ~100 | `app/graph/state.py`·`adapter.py`·Root 라우팅 | W2, W4 | W4-V1 |
| `priority.py` | 161 | `skills/rank_priorities.py` | W3 | W3-V1 |
| `daily_briefing.py` | 368 | `skills/daily_briefing.py` | W3 | 동상 |
| `weekly_report.py` | 368 | `skills/weekly_report.py` | W3 | 동상 |
| `meetings.py` | 467 | `skills/{analyze,search}_meeting*.py` | W3 | 동상 |
| `assistant_skills.py` | 387 | `skills/assistant_skills/` | W3 | 동상 |
| `assistant_router.py` | 937 | `skills/assistant_router.py` | W3, W6 | W3-V1, W6-V1 |
| `save_checkpoint()` | ~50 | LangGraph Checkpointer | W2, W4 | W2-V4, W4-V7 |
| `a2a_checkpoints` 테이블 | — | Checkpointer 테이블 | W2, W4 | 동상 |

**모든 삭제 대상에 대체처가 있다.** 대체처가 없는 삭제는 기능 제거이므로 W7 범위가 아니다.

## 5. 증빙 참조 추적

이동으로 영향받는 승인 증빙을 전수 추적한다.

| 증빙 | 위치 | 참조 대상 | 정정 |
| --- | --- | --- | --- |
| M1.2-04 Cursor·Watch 동기화 | [06-delivery-plan.md:91](06-delivery-plan.md#L91) | `external_sync.py` | `app/sync/` |
| M1.4-01 제안 Hub·SSE | [06-delivery-plan.md:769](06-delivery-plan.md#L769) | 동상 | 동상 |
| (evidence 2건) | W7-T1에서 확정 | 동상 | 동상 |
| (weekly_classification 참조) | W7-T1에서 확정 | `weekly_classification.py` | `app/domain/` |

**W7-T1의 조사가 이 표를 완성한다.** 누락되면 깨진 링크가 남는다.

## 6. 상위 문서 추적 (요구사항 → 출처)

| 요구사항 | 출처 | 종류 |
| --- | --- | --- |
| W7-R1 | [계획서 §9-1](30-langgraph-migration-plan.md) | 전환 완료 기준 |
| W7-R2, R3 | D4=A(사용자 결정) | 확정 결정 |
| W7-R4 | D6=B(사용자 결정) | 확정 결정 |
| W7-R5 | W5-T3(호출 제거)의 후속 | 선행 단계 |
| W7-R6 | `AGENTS.md` 증빙 규칙 | 개발 규칙 |
| W7-R7 | `AGENTS.md` 금지 사항 | **개발 규칙** |
| W7-R8 | `AGENTS.md` 금지 사항 | 동상 |
| W7-R9 | 회귀 원인 분리 | 방법론 |
| W7-R10 | **코드 조사**([test_migration.py](../workmate-agent/tests/test_migration.py) 확인) | 발견 사항 |

**W7은 `AGENTS.md` 의존도가 가장 높은 단계다.** 요구사항 10개 중 3개가 금지 사항·증빙 규칙에서
나온다. 삭제하는 단계이므로 "무엇을 지우면 안 되는가"가 중요하다.

## 7. 비가역 작업 추적

전환 전체에서 되돌릴 수 없는 것은 W7에 집중돼 있다.

| 작업 | 되돌릴 수 있나 | 조건 |
| --- | --- | --- |
| `app/workflows/` 삭제 | 가능(git) | 단 W5·W6 롤백 시 **함께 복원 필요** |
| 모듈 이동 | 가능 | |
| 코드 제거 | 가능 | |
| **`a2a_checkpoints` DROP** | **불가** | 데이터 복구 불가 |
| 증빙 링크 정정 | 가능 | |

### 7.1 롤백 착지점의 소멸

```
W5 완료: app/workflows/ 존재 → W5 revert로 즉시 복구
W6 완료: 동상
W7 완료: app/workflows/ 없음 → W5·W6 revert 시 복원 작업 추가
```

이것이 [W7-E7](30-7-3-entry-criteria.md)(검증 기간)이 선행 조건인 이유다.

## 8. 후행 단계 추적 (W7 산출물 → 소비자)

| W7 산출물 | 소비 단계 | 사용 방식 |
| --- | --- | --- |
| "실행 경로가 하나" 상태 | [W8](30-8-w8-retry-observability.md) | 재시도 정책을 붙일 대상이 명확 |
| 부작용 노드 목록 | W8-T2 | **재시도 제외 대상** |
| 실패 파급 규칙표 | W8 | 재시도·경고 정책 기준 |
| 스냅샷 27건 PASS | W8 | 기준선 |
| 증빙 링크 정정 내역 | [W9](30-9-w9-docs-evidence.md) | 문서 정합성 |
| 발견한 다른 죽은 코드 | W9 | 후속 백로그 |

### 8.1 W8로 넘기는 부작용 노드 목록

[W3-5](30-3-5-design.md) §3.4에서 작성한 목록이다. W7에서 최종 확정해 W8에 넘긴다.

| Skill | 부작용 노드 |
| --- | --- |
| `rank_priorities` | `save_snapshot` |
| `daily_briefing` | (간접) `rank_priorities_subgraph` |
| `analyze_meeting` | `save_final_transcript`, `save_analysis`, `heal_meeting_title`, `index_chunks` |
| `review_action_items` | `call_domain_api` |
| `review_proposal` | 동상 |
| `manage_tasks` | `create/update/delete_task` |

**W8에서 이 노드들에 `RetryPolicy`를 붙이면 안 된다** — 중복 실행된다.

## 9. 매트릭스 유지 규칙

1. 삭제 대상을 추가하면 §4에 **대체처를 명시**한다. 대체처가 없으면 기능 제거이므로 범위 밖이다.
2. 증빙 참조를 발견하면 §5에 추가한다. W7-T1의 조사가 이 표의 완전성을 결정한다.
3. 비가역 작업을 추가하면 §7에 등록하고 커밋 순서를 조정한다.
4. 식별자는 재사용하지 않는다.

## 10. 참조

- [30-7-4](30-7-4-requirements.md) — 요구사항
- [30-7-5](30-7-5-design.md) — 설계
- [30-7-7](30-7-7-verification.md) — 검증
