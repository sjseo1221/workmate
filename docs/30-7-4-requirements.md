# W7-4 — 요구사항 명세

> [30-7-w7-legacy-removal.md](30-7-w7-legacy-removal.md) §4의 상세 문서.

## 요약

| ID | 구분 | 한 줄 | 우선순위 | 검증 |
| --- | --- | --- | --- | --- |
| W7-R1 | 기능 | `app/workflows/` 패키지 삭제 | 필수 | W7-V1, V2 |
| W7-R2 | 기능 | `weekly_classification`을 `app/domain/`으로 이동 | 필수 | W7-V3 |
| W7-R3 | 기능 | `external_sync`를 `app/sync/`로 이동(삭제 금지) | 필수 | W7-V3 |
| W7-R4 | 기능 | `a2a_checkpoints` DROP Migration 추가 | 필수 | W7-V5, V6 |
| W7-R5 | 기능 | `save_checkpoint()` 관련 코드 제거 | 필수 | W7-V4 |
| W7-R6 | 제약 | **승인 증빙 링크를 유효하게 유지** | **필수** | W7-V7 |
| W7-R7 | 제약 | **승인 증빙 본문을 수정·삭제하지 않음** | **필수** | W7-V8 |
| W7-R8 | 제약 | 전환과 무관한 파일을 함께 정리하지 않음 | 필수 | `git diff --stat` |
| W7-R9 | 제약 | 이동 모듈의 내용을 수정하지 않음 | 필수 | `git diff` |
| W7-R10 | 기능 | Migration 계약 테스트를 실제와 맞춤 | 필수 | W7-V5 |

---

## W7-R1 — 패키지 삭제

**설명** `app/workflows/` 패키지를 삭제한다(§2.3의 이동분 제외).

**근거** [계획서 §9-1](30-langgraph-migration-plan.md): "`app/workflows/`와 `WorkflowRegistry`가
저장소에 없다."

**수용 기준**
- `ls app/workflows`가 "존재하지 않음"
- `grep -rn "WorkflowRegistry" app/`이 비어 있음
- `python -m compileall -q app tests`가 오류 없음
- 전체 테스트 통과

**삭제 대상 9개 파일**

```
__init__.py  registry.py  priority.py  daily_briefing.py  weekly_report.py
meetings.py  assistant_skills.py  assistant_router.py
(weekly_classification.py, external_sync.py는 이동)
```

**검증** W7-V1, V2 / **우선순위** 필수

---

## W7-R2 — `weekly_classification` 이동

**설명** `app/workflows/weekly_classification.py`를 `app/domain/`으로 옮긴다.

**근거** D4=A. I/O 없는 순수 함수이므로 [96번 §10](96-workmate-langgraph-target-architecture.md)의
Domain 계층에 속한다.

**수용 기준**
- `app/domain/` 아래에 존재
- **내용 무수정**(W7-R9)
- 호출자(`app/graph/skills/weekly_report.py`)의 import 갱신
- 관련 테스트 import 갱신
- 관련 동작이 그대로

**검증** W7-V3 / **우선순위** 필수

---

## W7-R3 — `external_sync` 이동 (삭제 금지)

**설명** `app/workflows/external_sync.py`를 `app/sync/`로 옮긴다. **삭제하지 않는다.**

**근거** 호출자가 없지만 승인된 증빙이 참조한다.

| 증빙 | 위치 |
| --- | --- |
| M1.2-04 | [06-delivery-plan.md:91](06-delivery-plan.md#L91) |
| M1.4-01 | [06-delivery-plan.md:769](06-delivery-plan.md#L769) |
| `docs/evidence/` | 2건 |

**수용 기준**
- `app/sync/` 아래에 존재
- 내용 무수정
- 테스트 import 갱신(`test_google_adapters.py`, `test_proposals.py`)
- 증빙 링크 정정(W7-R6)

**검증** W7-V3 / **우선순위** 필수

---

## W7-R4 — DROP Migration

**설명** `a2a_checkpoints` 테이블을 제거하는 Migration을 추가한다.

**근거** D6=B(사용자 결정 2026-09-23). 운영 중이 아니며 데이터 파기 무방함을 확인했다.

**수용 기준**
- `migrations/007_drop_a2a_checkpoints.sql` 존재
- `DROP TABLE IF EXISTS a2a_checkpoints;`
- Migration 적용 후 테이블 부재
- **재적용 시 오류 없음**(멱등)

**비가역성** 이 Migration이 적용되면 테이블 데이터를 복구할 수 없다. 커밋을 마지막으로 분리하고
검증 완료 후 적용한다([30-7-5](30-7-5-design.md) §5.4).

**검증** W7-V5, V6 / **우선순위** 필수

---

## W7-R5 — Checkpoint 코드 제거

**설명** `save_checkpoint()`·`_save_checkpoint_sync()` 관련 코드를 제거한다.

**대상**

| 위치 | 내용 |
| --- | --- |
| [persistence.py:281-307](../workmate-agent/app/a2a/persistence.py#L281) | `PersistentTaskStore.save_checkpoint()`, `_save_checkpoint_sync()` |
| [persistence.py:504-520](../workmate-agent/app/a2a/persistence.py#L504) | `PostgresTaskStore.save_checkpoint()` |
| [persistence.py:63-70](../workmate-agent/app/a2a/persistence.py#L63) | `CREATE TABLE IF NOT EXISTS a2a_checkpoints` |
| [test_persistence.py:55](../workmate-agent/tests/test_persistence.py#L55) | 해당 테스트 |
| [ui_working_fixture.py](../workmate-agent/tests/ui_working_fixture.py) | Fake Store의 메서드 |

**수용 기준**
- 위 코드가 없다
- `compileall` 오류 없음
- 관련 테스트가 갱신되거나 제거됨

**검증** W7-V4 / **우선순위** 필수

---

## W7-R6 — 증빙 링크 유효성

**설명** 이동한 모듈을 참조하는 승인 증빙의 링크가 실재 파일을 가리킨다.

**근거** `AGENTS.md`: "`result.md`의 구현·Schema·Migration·UI·테스트 경로는 저장소 내 파일로
이동하는 Markdown 링크를 사용한다."

**수용 기준**
- 모든 증빙 링크의 대상 파일이 존재
- 깨진 링크 0

**정정 대상**

| 문서 | 줄 | 현재 | 이후 |
| --- | --- | --- | --- |
| [06-delivery-plan.md](06-delivery-plan.md) | 91 | `workmate-agent/app/workflows/external_sync.py` | `workmate-agent/app/sync/external_sync.py` |
| [06-delivery-plan.md](06-delivery-plan.md) | 769 | 동상 | 동상 |
| `docs/evidence/` | 2건 | 동상 | 동상 |

**검증** W7-V7 / **우선순위** **필수**

---

## W7-R7 — 증빙 본문 불변

**설명** 승인 증빙의 서술·판정·승인 정보를 수정하지 않는다. **링크 경로만** 정정한다.

**근거** `AGENTS.md` 금지 사항: "기존 승인 증빙을 덮어쓰거나 삭제하지 않는다."

**수용 기준**
- `git diff`에서 증빙 파일의 변경이 경로 문자열뿐
- 서술·검수 항목·판정·`latest_approved_run_id`·`approved_at`·`reviewer` 불변

**정정 사실의 기록** 경로를 고쳤다는 사실은 **W7 증빙**에 기록한다. 원 증빙에 "수정함"을 덧붙이지
않는다.

**검증** W7-V8 / **우선순위** **필수**

---

## W7-R8 — 무관한 정리 금지

**설명** 전환과 무관한 파일을 함께 정리하지 않는다.

**근거** `AGENTS.md` 금지 사항.

**수용 기준**
- `git diff --stat`의 변경 파일이 W7 범위 안
- 삭제 파일: `app/workflows/` 8개(이동 2개 제외)
- 수정 파일: 이동 모듈 호출자, 테스트 import, 증빙 링크, Migration

**검증** `git diff --stat` 검토 / **우선순위** 필수

---

## W7-R9 — 이동 모듈 무수정

**설명** 이동하는 두 파일의 내용을 바꾸지 않는다.

**근거** 위치 변경과 내용 변경을 섞으면 회귀 원인 분리가 안 된다.

**수용 기준**
- `git diff`에서 이동으로 인식됨(내용 동일)
- import 문 자체도 변경 없음(모듈 내부 import가 절대 경로라면)

**예외** 모듈 내부에 상대 import가 있으면 경로 수정이 불가피하다. 그 경우 최소 변경만 한다.

**검증** `git diff` 검토 / **우선순위** 필수

---

## W7-R10 — Migration 계약 테스트 정합

**설명** Migration 계약 테스트가 실제 스키마와 맞도록 갱신한다.

**현재 상태** [test_migration.py:16-24](../workmate-agent/tests/test_migration.py#L16)가
`001_a2a_infrastructure.sql`에 `a2a_checkpoints` 선언이 있는지 확인한다.

```python
for table in ("a2a_tasks", "a2a_messages", "a2a_artifacts", "a2a_checkpoints"):
    self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", sql)
```

**문제** `001`은 그대로 두고 `007`에서 DROP하므로 이 테스트는 **계속 통과한다.** 그러나 의미상
"이 테이블이 존재해야 한다"를 주장하는 테스트가 남는다.

**수용 기준**

| 선택지 | 처리 |
| --- | --- |
| a | `001`의 검증 목록에서 `a2a_checkpoints` 제거 + `007`의 DROP 검증 추가 |
| b | `001` 검증은 유지(역사적 사실) + `007` DROP 검증 추가 |

**권장: b.** `001`은 과거에 그 테이블을 만들었다는 역사적 사실이고, 그것을 부정하면 Migration 이력이
왜곡된다. 다만 **주석으로 "007에서 DROP됨"을 명시**한다.

**검증** W7-V5 / **우선순위** 필수

---

## 요구사항 간 의존

```
W7-R4 (DROP) ← W7-R5 (코드 제거) ← W5-T3 (호출 제거)
W7-R1 (삭제) ← W7-R2, R3 (이동) ← W7-E4 (호출자 부재)
W7-R6 (링크) ← W7-R3 (이동)
W7-R7 (본문 불변) ← W7-R6과 긴장 관계 — §W7-R6·R7이 함께 해결
W7-R10 (테스트 정합) ← W7-R4
```

## 참조

- [30-7-5](30-7-5-design.md) — 구현 설계
- [30-7-7](30-7-7-verification.md) — 검증
- [`AGENTS.md`](../AGENTS.md) — 증빙 규칙
