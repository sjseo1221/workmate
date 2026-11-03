# W7-5 — 설계

> [30-7-w7-legacy-removal.md](30-7-w7-legacy-removal.md) §5의 상세 문서.

## 1. 삭제 대상과 대체처

| 삭제 | 줄 | 대체 |
| --- | --- | --- |
| `app/workflows/registry.py` | ~100 | `app/graph/state.py` + `adapter.py` + Root 라우팅 |
| `app/workflows/priority.py` | 161 | `app/graph/skills/rank_priorities.py` |
| `app/workflows/daily_briefing.py` | 368 | `app/graph/skills/daily_briefing.py` |
| `app/workflows/weekly_report.py` | 368 | `app/graph/skills/weekly_report.py` |
| `app/workflows/meetings.py` | 467 | `app/graph/skills/{analyze,search}_meeting*.py` |
| `app/workflows/assistant_skills.py` | 387 | `app/graph/skills/assistant_skills/` |
| `app/workflows/assistant_router.py` | 937 | `app/graph/skills/assistant_router.py` |
| `app/workflows/__init__.py` | ~15 | — |

## 2. 이동 대상 (D4=A)

### 2.1 `weekly_classification.py` → `app/domain/`

I/O 없는 순수 함수다.

| 함수 | 역할 |
| --- | --- |
| `link_approved_tasks()` | 승인된 Task와 출처 연결 |
| `link_action_item_tasks()` | Action Item 연결 |
| `build_weekly_report_data()` | 분류(`completed`/`in_progress`/`delayed`/`unresolved_issues`) |
| `extract_next_week_plans()` | 다음 주 계획 추출 |

[96번 §10](96-workmate-langgraph-target-architecture.md)의 Domain 계층 정의에 부합한다.

**호출자** `app/graph/skills/weekly_report.py`(W3 산출물). import 경로만 갱신한다.

### 2.2 `external_sync.py` → `app/sync/`

Skill이 아니고 HTTP Route·스케줄러에 연결돼 있지 않다.

```
# dev_gmail_sync_api.py:3
운영 자동 동기화 Job은 아직 없다(`ExternalSyncWorkflow.sync_gmail`는 있지만
어떤 HTTP Route·스케줄러에도 연결되지 않았다).
```

**그러나 삭제하지 않는다.** 승인 증빙이 참조하기 때문이다(§4).

**새 패키지** `app/sync/__init__.py`를 만든다. 나중에 운영 동기화 Job이 생기면 여기에 붙는다.

## 3. 삭제 순서 (W7-D1)

**역의존 순서로 지운다.** 참조가 남은 채 파일을 지우면 import 오류가 연쇄해 원인 파악이 어려워진다.

```
1. 잔여 참조 전수 조사          (W7-T1)
2. 모듈 이동 + app/ import 갱신  (W7-T2, T3)
3. 테스트 import 갱신            (W7-T4)
4. app/workflows/ 삭제           (W7-T5)
5. save_checkpoint 코드 제거     (W7-T6)
6. Migration 추가·적용           (W7-T7, T8)
7. 증빙 링크 정정                (W7-T9)
```

### 3.1 3번이 4번보다 먼저인 이유

테스트가 `app.workflows`를 import한 채로 패키지를 지우면 **테스트 수집 단계에서 전부 실패**한다.
어떤 테스트가 왜 실패했는지 구분할 수 없다.

### 3.2 6번이 마지막에 가까운 이유

Migration은 비가역이다. 코드 정리가 끝나고 전체 검증이 통과한 뒤에 적용한다(§5.4).

## 4. 증빙 링크 처리 (W7-D2)

### 4.1 규칙 충돌

`AGENTS.md`가 두 가지를 동시에 요구한다.

| # | 규칙 |
| --- | --- |
| 1 | "기존 승인 증빙을 덮어쓰거나 삭제하지 않는다" |
| 2 | "`result.md`의 구현·Schema·Migration·UI·테스트 경로는 저장소 내 파일로 이동하는 Markdown 링크를 사용한다" |

파일을 옮기면 2번이 깨지고, 증빙을 고치면 1번에 저촉되는 것처럼 보인다.

### 4.2 해결 — 링크 경로만 정정

**설계 결정 W7-D2:** 증빙 본문의 서술은 그대로 두고 **링크 경로만** 새 위치로 정정한다.

| 바꾼다 | 바꾸지 않는다 |
| --- | --- |
| Markdown 링크의 경로 문자열 | 서술, 검수 항목, 판정 |
| | `latest_approved_run_id`, `approved_at`, `reviewer` |
| | 실행 결과, 테스트 수 |

**근거** 1번 규칙의 취지는 "승인 사실과 근거를 보존하라"이지 "파일을 영원히 고정하라"가 아니다.
경로 정정은 증빙이 가리키는 대상을 **유효하게 유지**하는 행위이므로 2번을 지키는 것이다.

### 4.3 정정 사실의 기록

정정했다는 사실은 **W7 증빙**에 기록한다. 원 증빙에 "수정함" 같은 문구를 덧붙이지 않는다.

```
## 8. 문제와 수정 이력
### 8.x 승인 증빙 링크 정정
- 대상: 06-delivery-plan.md 2줄, docs/evidence/ 2건
- 변경: app/workflows/external_sync.py → app/sync/external_sync.py
- 변경하지 않은 것: 서술, 판정, 승인 정보
```

### 4.4 정정 대상 목록

W7-T1에서 확정한다. W0 조사 기준 예상 목록.

| 문서 | 참조 | 정정 |
| --- | --- | --- |
| [06-delivery-plan.md:91](06-delivery-plan.md#L91) | M1.2-04 구현 경로 | `app/sync/` |
| [06-delivery-plan.md:769](06-delivery-plan.md#L769) | M1.4-01 구현 경로 | 동상 |
| `docs/evidence/` 2건 | 동상 | 동상 |

`weekly_classification`을 참조하는 증빙도 함께 조사한다.

## 5. Migration 설계

### 5.1 파일

```sql
-- migrations/007_drop_a2a_checkpoints.sql
-- W7(D6=B): LangGraph Checkpointer가 대체했으므로 자체 Checkpoint 테이블을 폐기한다.
-- 이 테이블은 001에서 만들어졌고 {task_id}:submitted 마커만 기록했으며 읽는 코드가 없었다.
DROP TABLE IF EXISTS a2a_checkpoints;
```

**`IF EXISTS`가 멱등성을 준다.** 여러 번 적용해도 오류가 나지 않는다(W7-V6).

### 5.2 `001`을 고치지 않는 이유

| 선택지 | 평가 |
| --- | --- |
| a | `001`에서 `a2a_checkpoints` 생성 구문 삭제 |
| **b** | **`001` 유지 + `007`에서 DROP** |

**채택: b.** Migration은 **이력**이다. 과거에 만들었다가 나중에 지운 것이 사실이고, `001`을 고치면
이미 적용된 환경과 새 환경의 이력이 달라진다.

### 5.3 계약 테스트 처리 (W7-R10)

[test_migration.py:16-24](../workmate-agent/tests/test_migration.py#L16)가 `001`에
`a2a_checkpoints` 선언을 요구한다.

```python
for table in ("a2a_tasks", "a2a_messages", "a2a_artifacts", "a2a_checkpoints"):
    self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", sql)
```

**`001`을 안 고치므로 이 테스트는 그대로 통과한다.** 다만 의미가 흐려지므로 주석을 단다.

```python
# a2a_checkpoints는 001에서 생성했고 007에서 DROP했다(W7, D6=B).
# 이 검증은 Migration 이력의 사실을 확인하는 것이지 현재 스키마를 주장하지 않는다.
```

그리고 **새 검증을 추가**한다.

```python
def test_drop_migration_removes_checkpoint_table(self) -> None:
    migration = Path(__file__).parents[1] / "migrations" / "007_drop_a2a_checkpoints.sql"
    sql = migration.read_text(encoding="utf-8")
    self.assertIn("DROP TABLE IF EXISTS a2a_checkpoints", sql)
```

### 5.4 적용 순서와 커밋 분리 (W7-D3)

```
커밋 1~5: 코드 정리 (삭제·이동·import 갱신)
   ↓
전체 검증 (W7-V1~V4, V9, V10)
   ↓
커밋 6: Migration 파일 추가 + 계약 테스트
   ↓
Migration 적용 + 검증 (W7-V5, V6)
   ↓
커밋 7: 증빙 링크 정정
```

**Migration을 마지막에 두는 이유:** 코드 정리 중 문제가 생기면 revert로 되돌릴 수 있지만, Migration은
되돌릴 수 없다.

### 5.5 SQLite 경로

[PersistentTaskStore](../workmate-agent/app/a2a/persistence.py#L98)는 코드에서
`CREATE TABLE IF NOT EXISTS`를 실행한다. Migration 파일과 별개다.

| 백엔드 | 테이블 생성 | W7에서 |
| --- | --- | --- |
| Postgres | `migrations/*.sql` | `007`로 DROP |
| SQLite | 코드의 `CREATE TABLE IF NOT EXISTS` | **코드에서 구문 제거**(W7-R5) |

즉 SQLite는 Migration이 아니라 코드 수정으로 처리된다. 기존 SQLite 파일에 테이블이 남아 있어도 아무도
쓰지 않으므로 무해하다. 필요하면 `.runtime/` 파일을 지운다.

## 6. 잔여 참조 조사 (W7-T1)

```bash
# 운영 코드
grep -rn "from app.workflows\|import app.workflows" app/
grep -rn "workflow_registry\|WorkflowRegistry\|WorkflowRequest\|WorkflowResult" app/
grep -rn "save_checkpoint" app/

# 테스트
grep -rln "app.workflows" tests/
grep -rln "external_sync\|weekly_classification" tests/

# 문서
grep -rn "app/workflows" ../docs/ | grep -v "docs/30-"
```

### 6.1 예상 결과

| 대상 | 예상 |
| --- | --- |
| `app/` | **출력 없음**(W5에서 교체 완료) |
| `tests/` | 18개 파일(W3에서 재작성됐으면 줄어들 수 있다) |
| `docs/` | 20여 개(evidence 포함) |

`docs/30-*`는 제외한다 — 전환 계획 문서가 옛 경로를 언급하는 것은 정상이다(역사적 서술).

## 7. 설계 결정 요약

| ID | 결정 | 근거 |
| --- | --- | --- |
| W7-D1 | 역의존 순서로 삭제(테스트 import 갱신이 패키지 삭제보다 먼저) | §3 |
| W7-D2 | 증빙은 링크 경로만 정정, 본문 불변 | §4.2 |
| W7-D3 | Migration을 마지막 커밋으로 분리 | §5.4 |
| W7-D4 | `001` Migration을 고치지 않고 `007`에서 DROP | §5.2 |
| W7-D5 | `001` 계약 테스트는 유지하되 주석으로 이력 명시 + `007` 검증 추가 | §5.3 |

## 8. 참조

- [`AGENTS.md`](../AGENTS.md) — 증빙 규칙, 금지 사항
- [30-7-4](30-7-4-requirements.md) — 이 설계가 만족하는 요구사항
- [30-0](30-0-w0-baseline.md) §10.2 — `save_checkpoint` 조사 결과
