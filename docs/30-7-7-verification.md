# W7-7 — 검증 설계

> [30-7-w7-legacy-removal.md](30-7-w7-legacy-removal.md) §7의 상세 문서.

## 1. 검증 목록

| ID | 검증 항목 | 대상 요구사항 | 방법 | 판정 기준 |
| --- | --- | --- | --- | --- |
| W7-V1 | 레거시 부재 | W7-R1 | grep | 출력 없음 |
| W7-V2 | 패키지 삭제 | W7-R1 | `ls` | 존재하지 않음 |
| W7-V3 | 이동 모듈 동작 | W7-R2, R3 | 관련 테스트 | PASS |
| W7-V4 | import 무결성 | W7-R5 | `compileall` | 오류 없음 |
| W7-V5 | 테이블 DROP | W7-R4, R10 | Migration 적용 후 스키마 | 부재 |
| W7-V6 | Migration 멱등성 | W7-R4 | 2회 적용 | 오류 없음 |
| W7-V7 | 증빙 링크 유효성 | W7-R6 | 링크 대상 확인 | 깨진 링크 0 |
| W7-V8 | 증빙 본문 불변 | W7-R7 | `git diff` 검토 | 경로 외 변경 없음 |
| W7-V9 | 스냅샷 | 전체 | 27건 대조 | 전건 PASS |
| W7-V10 | 전체 테스트 | 전체 | 회귀 실행 | 실패 0, SKIP 0 |

## 2. 검증 케이스 상세

### W7-V1 — 레거시 부재

```bash
grep -rn "WorkflowRegistry" app/
grep -rn "WorkflowRequest\|WorkflowResult" app/
grep -rn "from app.workflows\|import app.workflows" app/
grep -rn "workflow_registry" app/
grep -rn "save_checkpoint" app/
```

**전부 출력 없음**이어야 한다.

| 케이스 | 대상 | 기대 |
| --- | --- | --- |
| V1-1 | `WorkflowRegistry` | 없음 |
| V1-2 | `WorkflowRequest`·`WorkflowResult` | 없음 |
| V1-3 | `app.workflows` import | 없음 |
| V1-4 | `save_checkpoint` | 없음 |
| V1-5 | `tests/`에서 `app.workflows` | 없음(W7-T4 이후) |

### W7-V2 — 패키지 삭제

| 케이스 | 확인 | 기대 |
| --- | --- | --- |
| V2-1 | `ls app/workflows` | 존재하지 않음 |
| V2-2 | `git status` | 8개 파일 삭제, 2개 이동 |

### W7-V3 — 이동 모듈 동작

| 케이스 | 대상 | 기대 |
| --- | --- | --- |
| V3-1 | `app/domain/weekly_classification.py` import | 성공 |
| V3-2 | `app/sync/external_sync.py` import | 성공 |
| V3-3 | `weekly_report` 관련 테스트 | PASS |
| V3-4 | `test_google_adapters.py`·`test_proposals.py` | PASS |
| V3-5 | `git diff`로 이동 파일 내용 확인 | **내용 무수정**(W7-R9) |

**V3-5가 중요하다.** 위치 변경과 내용 변경을 섞으면 회귀 원인 분리가 안 된다. `git`이 rename으로
인식하는지 확인한다.

### W7-V4 — import 무결성

```bash
uv run python -m compileall -q app tests
```

| 케이스 | 기대 |
| --- | --- |
| V4-1 | 오류 없음 |
| V4-2 | 앱 기동 성공 |

**V4-2는 `compileall`이 못 잡는 런타임 import를 확인한다.** 지연 import(`from app.x import y`가
함수 안에 있는 경우)는 컴파일 시점에 검사되지 않는다. 현재 코드에 지연 import가 많으므로 실제 기동이
필요하다.

### W7-V5 — 테이블 DROP

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V5-1 | 깨끗한 DB에 001~006 적용 | `a2a_checkpoints` 존재 |
| V5-2 | 007 적용 | 테이블 부재 |
| V5-3 | 스키마 조회 | `a2a_checkpoints`가 없음 |
| V5-4 | `test_migration.py`의 007 검증 | PASS |
| V5-5 | `001`의 기존 검증 | **여전히 PASS**(이력 사실) |
| V5-6 | SQLite 경로 | 코드에서 `CREATE TABLE` 구문 제거됨 |

**V5-5가 W7-D4의 확인이다.** `001`을 고치지 않았으므로 기존 계약 테스트는 그대로 통과한다.

**V5-6이 SQLite 경로다.** Migration이 아니라 코드 수정으로 처리되므로 별도 확인이 필요하다
([30-7-5](30-7-5-design.md) §5.5).

### W7-V6 — Migration 멱등성

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V6-1 | 007을 2회 적용 | 두 번째도 오류 없음 |
| V6-2 | 테이블이 없는 상태에서 007 적용 | 오류 없음 |

`DROP TABLE IF EXISTS`가 이를 보장한다.

### W7-V7 — 증빙 링크 유효성

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V7-1 | 정정한 링크의 대상 파일 존재 확인 | 전부 존재 |
| V7-2 | `docs/` 전체에서 `app/workflows` 검색 | **`docs/30-*` 외에는 없음** |
| V7-3 | 06-delivery-plan.md의 M1.2-04·M1.4-01 링크 | 새 경로 |
| V7-4 | evidence 2건의 링크 | 새 경로 |

**V7-2의 예외:** `docs/30-*`(전환 계획 문서)가 옛 경로를 언급하는 것은 **정상**이다. 역사적 서술이며
링크가 아니라 설명이다.

### W7-V8 — 증빙 본문 불변

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V8-1 | `git diff docs/evidence/` | 변경이 경로 문자열뿐 |
| V8-2 | 서술·검수 항목 | 불변 |
| V8-3 | `latest_approved_run_id`·`approved_at`·`reviewer` | 불변 |
| V8-4 | 실행 결과·테스트 수 | 불변 |

**이 검증이 `AGENTS.md`의 "승인 증빙을 덮어쓰지 않는다"를 지킨다.**

### W7-V9 — 스냅샷

```
uv run python -m unittest tests.contracts.test_contract_snapshots -v
```

| 케이스 | 기대 |
| --- | --- |
| V9-1 | 27건 전건 PASS |
| V9-2 | W6 대조 결과와 동일 | **삭제가 아무것도 바꾸지 않았다** |

**차이가 나면 삭제한 코드가 여전히 쓰이고 있었다는 뜻이다.** 원인을 찾아 해결한다.

### W7-V10 — 전체 테스트

```
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

| 항목 | 기대 |
| --- | --- |
| 전체 | 실패 0 |
| SKIP | 0 |
| 삭제한 코드의 테스트 | 제거되거나 새 경로로 갱신됨 |

## 3. 검증 실행 순서

```
W7-T6 완료 (코드 정리 끝):
  1. W7-V1, V2   레거시 부재
  2. W7-V3       이동 모듈
  3. W7-V4       import 무결성
  4. W7-V9       스냅샷
  5. W7-V10      전체 회귀
       ↓
  ★ 여기가 Migration 전 관문 (W7-T7)
       ↓
Migration 적용:
  6. W7-V5, V6   DROP·멱등성
  7. W7-V10      전체 회귀 재실행
       ↓
증빙 정정:
  8. W7-V7, V8   링크·본문
```

**5번까지 통과해야 Migration을 적용한다.** 비가역 작업 전의 마지막 확인이다.

## 4. 판정 규칙

- **W7-V9(스냅샷) FAIL이면 Migration을 적용하지 않는다.** 삭제가 동작을 바꿨다는 뜻이므로 원인
  해결이 먼저다
- W7-V8(증빙 본문 불변) FAIL은 `AGENTS.md` 위반이다. 즉시 되돌린다
- W7-V5-6(SQLite 경로)을 잊지 않는다. Migration만 보면 놓친다

## 5. 특별 확인 — 지연 import

현재 코드에는 함수 안에서 import하는 패턴이 많다.

```python
# assistant_skills.py의 예
from app.action_item_api import ActionDecision, ActionsReviewRequest
```

이런 import는 `compileall`이 잡지 못한다. 실제로 그 함수를 호출해야 오류가 드러난다.

**W7-V10(전체 테스트)이 이를 커버한다** — 테스트가 모든 경로를 실행하므로. 다만 테스트가 안 도는
경로가 있으면 남는다. W7-V4-2(앱 기동)를 함께 한다.

## 6. 검증 결과의 소비

| 결과 | 소비처 |
| --- | --- |
| W7-V1 (레거시 부재) | [계획서 §9-1](30-langgraph-migration-plan.md) 완료 기준 |
| W7-V5 (DROP) | 계획서 §9-5 완료 기준 |
| W7-V9 | [W8](30-8-w8-retry-observability.md)의 기준선 |
| 부작용 노드 목록 | W8-T2 재시도 제외 대상 |
| 증빙 링크 정정 내역 | [W9](30-9-w9-docs-evidence.md) |

## 7. 참조

- [30-7-4](30-7-4-requirements.md) — 검증 대상 요구사항
- [30-7-5](30-7-5-design.md) §5 — Migration 설계
- [30-7-9](30-7-9-exit-criteria.md) — 승인 처리
