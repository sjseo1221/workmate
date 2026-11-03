# W7-12 — 참조 자료

> [30-7-w7-legacy-removal.md](30-7-w7-legacy-removal.md) §12의 상세 문서.

"무엇을 참조하는가"가 아니라 **"어디를 왜 읽는가"** 를 기록한다.

## 1. 개발 규칙 — W7에서 가장 중요

### AGENTS.md

W7은 **삭제하는 단계**이므로 "무엇을 지우면 안 되는가"가 핵심이다.

| 규칙 | W7에서의 적용 |
| --- | --- |
| **"기존 승인 증빙을 덮어쓰거나 삭제하지 않는다"** | W7-R7, W7-V8 |
| **"`result.md`의 구현·Schema·Migration·UI·테스트 경로는 저장소 내 파일로 이동하는 Markdown 링크를 사용한다"** | W7-R6, W7-V7 |
| "삭제된 파일은 링크를 만들지 않고 삭제 사실과 대체 검증 경로를 기록한다" | `external_sync`를 **이동**으로 처리하는 근거의 반대편 |
| **"관련 없는 파일을 함께 정리하거나 대규모 포맷 변경을 하지 않는다"** | W7-R8 |
| "사용자 승인 없이 데이터 모델과 공개 A2A Schema를 변경하지 않는다" | DROP은 D6=B로 승인됨 |
| "실패한 테스트를 삭제하거나 우회하지 않는다" | [30-7-11](30-7-11-rollback.md) §4.2 |
| "하나의 커밋에는 하나의 논리적 변경만" | 커밋 분할 |
| "M0.1은 A2A Task·Message 멱등성·Artifact·`task_id ↔ thread_id`·Checkpoint의 최소 인프라 Migration을 소유" | `001`의 소유 범위 — `007`이 그 일부를 폐기한다 |

**마지막 항목이 미묘하다.** `AGENTS.md`는 M0.1이 Checkpoint Migration을 소유한다고 적었다. W7의 DROP은
그 소유 범위를 줄이는 것이므로, W9에서 이 서술도 갱신 대상인지 검토한다.

## 2. 설계 근거 문서

### 30-langgraph-migration-plan.md

| 절 | 읽는 이유 |
| --- | --- |
| §1-1 | "전환이 끝나면 저장소에 `WorkflowRegistry`도 (…) 남지 않는다. 실행 경로는 하나다" — W7의 목적 |
| §2.3 | 자리를 옮기는 것 2건 |
| §4 D4, D6 | 확정 결정 |
| §9-1, §9-5 | W7이 달성하는 완료 기준 |
| §0.1 | "운영 중이 아니다" — DROP의 근거 |

### 96-workmate-langgraph-target-architecture.md

| 절 | 읽는 이유 |
| --- | --- |
| §10 구현 경계 | Domain 계층의 정의 — `weekly_classification` 이동의 근거 |
| §10 | Checkpointer와 Task Store의 책임 — `save_checkpoint` 제거의 근거 |

## 3. 코드 참조

### 3.1 삭제 대상

| 위치 | 읽는 이유 |
| --- | --- |
| [app/workflows/](../workmate-agent/app/workflows/) | 삭제 대상 전체 — 파일 목록과 줄 수 확인 |
| [registry.py:57-100](../workmate-agent/app/workflows/registry.py#L57) | `WorkflowRegistry` — 대체처 확인 |
| [assistant_router.py](../workmate-agent/app/workflows/assistant_router.py) | 937줄. 가장 큰 삭제 대상 |

**삭제 전에 각 파일의 주석을 훑는다.** 실사용 배경이 담긴 주석이 새 구현(W3 산출물)에 옮겨졌는지
확인하는 마지막 기회다.

### 3.2 이동 대상

| 위치 | 읽는 이유 |
| --- | --- |
| [weekly_classification.py](../workmate-agent/app/workflows/weekly_classification.py) | 239줄, 순수 함수 4개 |
| [external_sync.py](../workmate-agent/app/workflows/external_sync.py) | `ExternalSyncWorkflow` |
| [dev_gmail_sync_api.py:3](../workmate-agent/app/dev_gmail_sync_api.py#L3) | **"운영 자동 동기화 Job은 아직 없다"** — 호출자 부재의 근거 |
| [app/domain/](../workmate-agent/app/domain/) | 이동처. 기존 파일 구조 확인 |

### 3.3 Checkpoint 코드

| 위치 | 읽는 이유 |
| --- | --- |
| [persistence.py:63-70](../workmate-agent/app/a2a/persistence.py#L63) | **SQLite의 `CREATE TABLE`** — Migration과 별개 경로(W7-K6) |
| [persistence.py:281-307](../workmate-agent/app/a2a/persistence.py#L281) | `save_checkpoint()`, `_save_checkpoint_sync()` |
| [persistence.py:504-520](../workmate-agent/app/a2a/persistence.py#L504) | Postgres 구현 |
| [test_persistence.py:55](../workmate-agent/tests/test_persistence.py#L55) | 제거할 테스트 |
| [ui_working_fixture.py:75](../workmate-agent/tests/ui_working_fixture.py#L75) | Fake Store의 메서드 |

### 3.4 Migration

| 위치 | 읽는 이유 |
| --- | --- |
| [migrations/001_a2a_infrastructure.sql](../workmate-agent/migrations/001_a2a_infrastructure.sql) | `a2a_checkpoints` 생성 구문 — **고치지 않는다**(W7-D4) |
| [test_migration.py:11-24](../workmate-agent/tests/test_migration.py#L11) | **`001`에 `a2a_checkpoints` 선언을 요구하는 계약 테스트** — W7-R10의 근거 |
| `migrations/` 전체 | 파일명 규칙(`00N_slug.sql`), 다음 번호 확인 |

**`test_migration.py`의 검증 방식이 중요하다.** 파일을 읽어 문자열을 확인하는 방식이므로, `001`을
안 고치면 그대로 통과한다.

## 4. 증빙 참조 — 정정 대상

| 위치 | 참조 | 정정 |
| --- | --- | --- |
| [06-delivery-plan.md:91](06-delivery-plan.md#L91) | M1.2-04의 `external_sync.py` | `app/sync/` |
| [06-delivery-plan.md:769](06-delivery-plan.md#L769) | M1.4-01의 `external_sync.py` | 동상 |
| `docs/evidence/` 2건 | 동상 | 동상 |
| (weekly_classification 참조) | W7-T1에서 확정 | `app/domain/` |

**W7-T1의 조사가 이 목록을 완성한다.** W0 조사 기준으로 `docs/evidence/`에 `app/workflows/`를
참조하는 문서가 20개, 그중 `external_sync`가 2개다.

## 5. 이전 단계 문서

| 문서 | W7과의 관계 |
| --- | --- |
| [30-0](30-0-w0-baseline.md) §10.2 | **`save_checkpoint` 조사 결과** — "읽는 코드가 없다" |
| [30-1-11](30-1-11-rollback.md) §1.1 | **스냅샷 재작성 기한** — W7이 그 끝 |
| [30-3-5](30-3-5-design.md) §3.4 | **부작용 노드 목록** — W8 전달 대상 |
| [30-3-5](30-3-5-design.md) §7 | 실패 파급 규칙표 — W8 전달 |
| [30-5-6](30-5-6-wbs.md) W5-T3 | `save_checkpoint` 호출 제거 — W7의 전제 |
| [30-5-9](30-5-9-exit-criteria.md) §6 | "아무도 안 쓰는 상태"가 삭제의 전제 |
| [30-6-9](30-6-9-exit-criteria.md) | **W6 승인** — W7-E2 |
| [30-6-12](30-6-12-rollback.md) §8.3 | "W7 전의 마지막 롤백 기회" |

## 6. 후행 단계 문서

| 문서 | 전달 내용 |
| --- | --- |
| [30-8](30-8-w8-retry-observability.md) | 부작용 노드 목록(재시도 제외), 실패 파급 규칙표 |
| [30-9](30-9-w9-docs-evidence.md) | 증빙 링크 정정 내역, 발견한 죽은 코드, 코드량 변화 |

## 7. 외부 문서

| 자료 | 확인할 내용 |
| --- | --- |
| Git — `git mv` | 이동을 rename으로 인식시키는 방법(W7-V3-5) |
| Git — `git diff --stat` | 변경 범위 확인(W7-R8) |
| PostgreSQL — `DROP TABLE IF EXISTS` | 멱등성, FK 제약이 있을 때의 동작 |
| Python — `compileall` | 무엇을 검사하고 무엇을 검사하지 않는가(지연 import) |

### 7.1 `DROP TABLE`과 FK

`a2a_checkpoints`를 다른 테이블이 FK로 참조하면 `DROP`이 실패하거나 `CASCADE`가 필요하다.

[001의 스키마](../workmate-agent/migrations/001_a2a_infrastructure.sql)를 읽어 FK 방향을 확인한다.
주석에 따르면 "Message·Checkpoint·Artifact가 FK로 Task Snapshot을 참조"하므로, Checkpoint가
참조하는 쪽이다 — 즉 Checkpoint를 지우는 것은 안전하다. **다만 확인은 한다.**

## 8. 이 문서 묶음

| 문서 | 대응 절 |
| --- | --- |
| [30-7-1](30-7-1-document-info.md) | §1 문서 정보·용어·삭제 대상 목록 |
| [30-7-2](30-7-2-scope.md) | §2 목적, 삭제·이동·DROP 범위 |
| [30-7-3](30-7-3-entry-criteria.md) | §3 선행 조건 — **W6 승인 + 검증 기간** |
| [30-7-4](30-7-4-requirements.md) | §4 요구사항 W7-R1~R10 |
| [30-7-5](30-7-5-design.md) | §5 설계 — 삭제 순서, **증빙 링크 처리**, Migration |
| [30-7-6](30-7-6-wbs.md) | §6 작업 분해 W7-T1~T12, **관문** |
| [30-7-7](30-7-7-verification.md) | §7 검증 설계 W7-V1~V10 |
| [30-7-8](30-7-8-traceability.md) | §8 추적성, 삭제×대체처, **비가역 작업 추적** |
| [30-7-9](30-7-9-exit-criteria.md) | §9 완료 정의 |
| [30-7-10](30-7-10-risks.md) | §10 위험 등록부 W7-K1~K9 |
| [30-7-11](30-7-11-rollback.md) | §11 롤백·중단·재개, **비가역 작업 취급** |
| [30-7-12](30-7-12-references.md) | §12 참조 (이 문서) |
