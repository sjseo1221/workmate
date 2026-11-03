# W7-1 — 문서 정보와 문서 체계

> [30-7-w7-legacy-removal.md](30-7-w7-legacy-removal.md) §1의 상세 문서.

## 1. 단계 식별

| 항목 | 값 |
| --- | --- |
| 단계 코드 | W7 |
| 단계명 | 레거시 삭제·모듈 이동·Migration |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | [W6 interrupt·공개 계약](30-6-w6-interrupt-resume.md) |
| 후행 단계 | [W8 재시도와 관측](30-8-w8-retry-observability.md) |
| 상태 | 대기 |
| 관련 확정 결정 | D4=A(모듈 이동), **D6=B(`a2a_checkpoints` DROP)** |
| 성격 | **비가역 작업 포함** |

## 2. 단계 성격 — 되돌릴 수 없는 선을 넘는다

W7은 두 가지 비가역 작업을 한다.

| 작업 | 비가역성 |
| --- | --- |
| `app/workflows/` 삭제 | 코드는 git에서 복원 가능하지만, **W5·W6의 롤백 착지점이 사라진다** |
| `a2a_checkpoints` DROP | **DB 데이터는 복원 불가** |

### 2.1 롤백 착지점의 소멸

```
W5 완료: 운영 경로 = Graph,  app/workflows/ 존재 → revert하면 즉시 동작
W6 완료: 확인 = interrupt,   app/workflows/ 존재 → 동상
W7 완료: app/workflows/ 없음 → **revert해도 호출할 대상이 없다**
```

W5·W6을 되돌리려면 `app/workflows/`도 함께 복원해야 한다. 가능하지만 "커밋 하나 revert"로 끝나지
않는다.

**그래서 W7은 W5·W6이 충분히 검증된 뒤에 온다.**

### 2.2 W7이 만드는 것

아무것도 만들지 않는다. **없애고 옮기는 것이 전부다.**

| 동작 | 대상 |
| --- | --- |
| 삭제 | `app/workflows/` 패키지(9개 파일 약 2,600줄), `save_checkpoint()` 관련 코드 |
| 이동 | `weekly_classification.py` → `app/domain/`, `external_sync.py` → `app/sync/` |
| DROP | `a2a_checkpoints` 테이블 |
| 정정 | 승인 증빙의 링크 경로 |

### 2.3 "실행 경로는 하나"의 완성

[계획서 §1-1](30-langgraph-migration-plan.md): "전환이 끝나면 저장소에 `WorkflowRegistry`도, 레거시
Handler 경로도, 전환용 환경변수도 남지 않는다. 실행 경로는 하나다."

W7이 이 원칙을 실제로 달성하는 단계다. 이중 구조가 남아 있으면 다음 작업자가 어느 쪽이 운영 경로인지
알 수 없다.

## 3. 문서 체계

| 문서 | 대응 절 | 내용 |
| --- | --- | --- |
| [30-7-1](30-7-1-document-info.md) | §1 | 문서 정보·체계·용어 (이 문서) |
| [30-7-2](30-7-2-scope.md) | §2 | 목적, 삭제·이동·DROP 범위 |
| [30-7-3](30-7-3-entry-criteria.md) | §3 | 선행 조건 |
| [30-7-4](30-7-4-requirements.md) | §4 | 요구사항 W7-R1~R10 |
| [30-7-5](30-7-5-design.md) | §5 | 설계 — 삭제 순서, 증빙 링크, Migration |
| [30-7-6](30-7-6-wbs.md) | §6 | 작업 분해 W7-T1~T11 |
| [30-7-7](30-7-7-verification.md) | §7 | 검증 설계 W7-V1~V10 |
| [30-7-8](30-7-8-traceability.md) | §8 | 추적성 매트릭스 |
| [30-7-9](30-7-9-exit-criteria.md) | §9 | 완료 정의 |
| [30-7-10](30-7-10-risks.md) | §10 | 위험 등록부 |
| [30-7-11](30-7-11-rollback.md) | §11 | 롤백·중단 기준 |
| [30-7-12](30-7-12-references.md) | §12 | 참조 자료 |

## 4. 식별자 규칙

| 접두 | 의미 | 예 |
| --- | --- | --- |
| `W7-E` | 선행 조건 | `W7-E4` |
| `W7-R` | 요구사항 | `W7-R6` |
| `W7-T` | 작업 | `W7-T7` |
| `W7-V` | 검증 | `W7-V5` |
| `W7-K` | 위험 | `W7-K1` |
| `W7-D` | 설계 결정 | `W7-D1` |

## 5. 용어

| 용어 | 정의 | 주의 |
| --- | --- | --- |
| **레거시** | W3~W6에서 Graph로 대체된 옛 구현 | `app/workflows/`와 그 호출 코드 |
| **죽은 코드** | 호출자가 없는 코드 | W5 이후 `app/workflows/`가 여기 해당 |
| **이동(move)** | 파일 위치만 바꾸고 내용은 유지 | 삭제와 구분 |
| **DROP Migration** | 테이블을 제거하는 SQL | **비가역** |
| **증빙 링크** | 승인된 `result.md`가 참조하는 구현 경로 | `AGENTS.md`상 유효해야 한다 |
| **멱등 Migration** | 여러 번 적용해도 결과가 같은 SQL | `DROP TABLE IF EXISTS` |

## 6. 삭제 대상 목록

| 파일 | 줄 | W3~W6의 대체처 |
| --- | --- | --- |
| `app/workflows/registry.py` | ~100 | `app/graph/state.py`, `adapter.py`, Root 라우팅 |
| `app/workflows/priority.py` | 161 | `app/graph/skills/rank_priorities.py` |
| `app/workflows/daily_briefing.py` | 368 | `app/graph/skills/daily_briefing.py` |
| `app/workflows/weekly_report.py` | 368 | `app/graph/skills/weekly_report.py` |
| `app/workflows/meetings.py` | 467 | `app/graph/skills/{analyze,search}_meeting*.py` |
| `app/workflows/assistant_skills.py` | 387 | `app/graph/skills/assistant_skills/` |
| `app/workflows/assistant_router.py` | 937 | `app/graph/skills/assistant_router.py` |
| `app/workflows/__init__.py` | ~15 | — |
| **계** | **약 2,800** | |

## 7. 이동 대상

| 파일 | 이동처 | 이유 |
| --- | --- | --- |
| `app/workflows/weekly_classification.py` | `app/domain/` | I/O 없는 순수 함수 |
| `app/workflows/external_sync.py` | `app/sync/` | Skill이 아니지만 **승인 증빙이 참조** |

## 8. 산출물 위치

```
workmate-agent/
  app/workflows/                삭제
  app/domain/weekly_classification.py    이동
  app/sync/external_sync.py              이동
  app/a2a/persistence.py                 save_checkpoint 제거
  app/a2a/runtime.py                     잔여 정리
  migrations/007_drop_a2a_checkpoints.sql  신규
  tests/                                 import 경로 갱신, Migration 검증 추가
docs/
  06-delivery-plan.md                    링크 정정
  evidence/**/result.md                  링크 정정 2건
  evidence/langgraph/W7/runs/{run_id}/result.md
```

## 9. 변경 이력

| 일자 | 변경 | 사유 |
| --- | --- | --- |
| 2026-09-23 | 초판 (상위 문서 §1) | 단계별 상세 계획 |
| 2026-09-29 | 12개 문서로 분해, Migration 계약 테스트 조사 반영 | 절별 상세화 요청 |
