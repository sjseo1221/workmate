# W7-2 — 목적과 범위

> [30-7-w7-legacy-removal.md](30-7-w7-legacy-removal.md) §2의 상세 문서.

## 1. 목적

전환의 완결 조건인 **"실행 경로는 하나"** 를 실제로 만든다.

### 1.1 이중 구조를 남기면 생기는 일

| 문제 | 설명 |
| --- | --- |
| 어느 쪽이 운영인지 모른다 | 다음 작업자가 `app/workflows/`를 고치고 아무 효과가 없어 당황한다 |
| 수정이 두 곳에 필요해 보인다 | 실제로는 한 곳인데 양쪽을 고치게 된다 |
| 테스트가 죽은 코드를 검증한다 | 통과해도 의미가 없다 |
| 검색이 오염된다 | `grep`으로 함수를 찾으면 두 곳이 나온다 |

### 1.2 왜 W7까지 남겨 두었나

| 단계 | `app/workflows/`의 역할 |
| --- | --- |
| W1 | **스냅샷의 대상** — 이 코드를 실행해 기대값을 만든다 |
| W2~W4 | 비교 대상 |
| W5 | **롤백 착지점** — 진입점 교체가 실패하면 여기로 돌아간다 |
| W6 | 동상 |
| **W7** | **더 이상 필요 없다** |

W5 이후 호출되지 않지만, W6까지는 롤백 가능성을 위해 남긴다.

## 2. 범위 내 (In scope)

| ID | 항목 | 대상 |
| --- | --- | --- |
| S1 | 패키지 삭제 | `app/workflows/` (9개 파일 약 2,800줄) |
| S2 | 모듈 이동 | `weekly_classification.py` → `app/domain/`, `external_sync.py` → `app/sync/` |
| S3 | Checkpoint 코드 제거 | `save_checkpoint()`, `_save_checkpoint_sync()` |
| S4 | DROP Migration | `a2a_checkpoints` 테이블 |
| S5 | 테스트 import 경로 갱신 | 영향받는 테스트 |
| S6 | Migration 계약 테스트 갱신 | `test_migration.py` |
| S7 | 승인 증빙 링크 정정 | `06-delivery-plan.md` 2줄 + evidence 2건 |

## 3. 범위 외 (Out of scope)

| 항목 | 이유 |
| --- | --- |
| 새 기능 추가 | W7은 없애는 단계다 |
| Task Store 구조 변경 | 외부 원장은 유지(96번 §10) |
| **관련 없는 파일 정리·포맷 변경** | `AGENTS.md` 금지 사항 |
| 이동 모듈의 내용 수정 | 위치만 바꾼다 |
| 다른 테이블 정리 | `a2a_checkpoints`만 |
| 문서 본문 수정 | 링크 경로만 정정 |

### 3.1 "정리 김에"를 경계한다

`AGENTS.md`: "관련 없는 파일을 함께 정리하거나 대규모 포맷 변경을 하지 않는다."

W7은 대량 삭제를 하는 단계라 "이것도 정리하자"는 유혹이 크다. 그러나 diff가 커지면 리뷰가 불가능해지고,
회귀가 숨는다.

| 유혹 | 판단 |
| --- | --- |
| 안 쓰는 import 정리 | 삭제하는 파일의 것만 |
| 오래된 주석 정리 | 범위 밖 |
| 다른 죽은 코드 발견 | **기록만 하고 후속 백로그** |
| 포맷 통일 | 범위 밖 |

## 4. 삭제와 이동의 구분

### 4.1 왜 `external_sync.py`는 삭제하지 않나

`app/` 안에 호출자가 없다. [dev_gmail_sync_api.py:3](../workmate-agent/app/dev_gmail_sync_api.py#L3)의
Docstring이 명시한다.

> 운영 자동 동기화 Job은 아직 없다(`ExternalSyncWorkflow.sync_gmail`는 있지만 어떤 HTTP Route·
> 스케줄러에도 연결되지 않았다).

**그런데 승인된 증빙이 이 경로를 참조한다.**

| 증빙 | 위치 | 상태 |
| --- | --- | --- |
| M1.2-04 Cursor·Watch 동기화 | [06-delivery-plan.md:91](06-delivery-plan.md#L91) | 완료 |
| M1.4-01 제안 Hub·SSE 발행 | [06-delivery-plan.md:769](06-delivery-plan.md#L769) | 완료 |
| `docs/evidence/` 참조 | 2건 | 승인됨 |

`AGENTS.md`는 두 가지를 동시에 요구한다.

1. "기존 승인 증빙을 덮어쓰거나 삭제하지 않는다"
2. "`result.md`의 구현·Schema·Migration·UI·테스트 경로는 저장소 내 파일로 이동하는 Markdown 링크를
   사용한다"

파일을 지우면 2번이 깨지고, 증빙을 고치면 1번에 저촉된다. **이동이 유일한 해결책이다.**

### 4.2 `weekly_classification.py`

I/O 없는 순수 함수(`link_approved_tasks`·`build_weekly_report_data`·`extract_next_week_plans`)다.
[96번 §10](96-workmate-langgraph-target-architecture.md)의 Domain 계층 정의에 부합한다.

> Domain 함수 — 날짜, 점수, 중복, 권한, 근거 검증 / **외부 I/O는 하지 않는다**

W3의 `weekly_report` Subgraph가 호출하므로 죽은 코드도 아니다. 단지 위치가 틀렸을 뿐이다.

## 5. Migration의 특수성

### 5.1 비가역

```sql
DROP TABLE IF EXISTS a2a_checkpoints;
```

이 한 줄이 W7에서 유일하게 **git으로 되돌릴 수 없는** 변경이다.

### 5.2 근거

| 근거 | 내용 |
| --- | --- |
| D6=B | 사용자 결정(2026-09-23) |
| 운영 중 아님 | [계획서 §0.1](30-langgraph-migration-plan.md) |
| 데이터가 마커뿐 | W0 조사 — `{task_id}:submitted` 한 줄, 읽는 코드 없음 |
| W5에서 쓰기 중단 | `save_checkpoint` 호출 제거 |

### 5.3 커밋 분리

**Migration을 마지막 커밋으로 분리한다.**

```
1. 코드 정리 커밋들   ← revert 가능
2. 검증
3. Migration 커밋     ← 비가역
```

검증이 끝나기 전에 Migration을 적용하지 않는다([30-7-11](30-7-11-rollback.md) §2).

## 6. 범위 변경 절차

| 상황 | 처리 |
| --- | --- |
| 삭제 중 다른 죽은 코드 발견 | **기록만.** 후속 백로그 |
| 이동 모듈에 수정이 필요해 보임 | 범위 밖. 위치만 바꾼다 |
| 증빙 본문 수정이 필요해 보임 | **금지.** 링크 경로만 정정 |
| 다른 테이블도 정리하고 싶음 | 범위 밖 |
| Migration이 다른 테이블에 영향 | 조사 후 보고 |

## 7. 참조

- [`AGENTS.md`](../AGENTS.md) — 증빙 규칙, 금지 사항
- [30-7-5](30-7-5-design.md) — 삭제 순서와 증빙 링크 처리
- [30-3-5](30-3-5-design.md) §3.4 — 부작용 노드 목록(W8 전달)
