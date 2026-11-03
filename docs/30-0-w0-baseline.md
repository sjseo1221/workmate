# W0 — 기준선 채증과 출발점 정리

> **이 문서는 요약과 색인이다.** 각 절의 상세는 아래 13개 문서에 있고, 충돌 시 상세 문서를 기준으로
> 한다.
>
> | 절 | 상세 문서 | 내용 |
> | --- | --- | --- |
> | §1 | [30-0-1](30-0-1-document-info.md) | 문서 정보·용어·**발견 사항 W0-F1~F3** |
> | §2 | [30-0-2](30-0-2-scope.md) | 목적과 범위, 측정의 원칙 |
> | §3 | [30-0-3](30-0-3-entry-criteria.md) | 선행 조건과 실제 결과 |
> | §4 | [30-0-4](30-0-4-requirements.md) | 요구사항 W0-R1~R7과 충족 여부 |
> | §5 | [30-0-5](30-0-5-design.md) | 설계 — 측정 대상, 환경 정의, 절차 |
> | §6 | [30-0-6](30-0-6-wbs.md) | 작업 분해와 **실제 수행 결과** |
> | §7 | [30-0-7](30-0-7-verification.md) | 검증 설계와 **실제 결과** |
> | §8 | [30-0-8](30-0-8-traceability.md) | 추적성, 발견 사항 추적 |
> | §9 | [30-0-9](30-0-9-exit-criteria.md) | 완료 정의와 달성 상태 |
> | §10 | [30-0-10](30-0-10-results.md) | **실행 결과** (W0 고유 절) |
> | §11 | [30-0-11](30-0-11-risks.md) | 위험과 **실제 결과** |
> | §12 | [30-0-12](30-0-12-rollback.md) | 롤백·중단 기준 |
> | §13 | [30-0-13](30-0-13-references.md) | 참조 자료와 읽을 지점 |
>
> **W0는 유일하게 완료된 단계다.** 따라서 이 문서 묶음은 계획이 아니라 **기록**이다 — "무엇을 할
> 것인가"가 아니라 "무엇을 했는가".
>
> **조사에서 나온 사실 셋이 이후 단계의 설계를 바꿨다.**
> **W0-F1** `save_checkpoint()`는 마커 한 줄만 쓰고 읽는 코드가 없다 → D6=B(DROP) 결정의 뒷받침,
> W2·W5·W7의 근거.
> **W0-F2** `ExternalSyncWorkflow`는 호출자가 없지만 M1.2-04·M1.4-01 승인 증빙이 경로를 참조 →
> W7에서 삭제가 아닌 이동.
> **W0-F3** 테스트 DB에 `vector`·`pg_trgm` 확장이 필요 → 표준 postgres 이미지로는 부족.
>
> 또한 W0를 "테스트 한 번 돌리는 단계"로 예상했다면 전부 예상 밖이었다 — venv가 깨져 있었고,
> 미커밋 변경 5개 파일이 있었고, Docker 엔진이 꺼져 있었고, 파이프가 exit code를 가렸다
> ([30-0-11](30-0-11-risks.md) §2).

## 1. 문서 정보

| 항목 | 값 |
| --- | --- |
| 단계 | W0 (전환 0단계) |
| 상위 계획 | [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §5 |
| 선행 단계 | 없음 |
| 후행 단계 | [W1 계약 스냅샷 추출](30-1-w1-contract-snapshot.md) |
| 상태 | **완료** (2026-09-23) |
| 승인 실행 | [`docs/evidence/langgraph/W0/runs/20260923-065508/result.md`](evidence/langgraph/W0/runs/20260923-065508/result.md) |

## 2. 목적과 범위

### 2.1 목적

전환 전후를 비교할 수 있도록 **현재 시스템의 검증 가능한 출발점**을 고정한다. 빅뱅 전환은 중간 상태가
동작하지 않으므로, "무엇과 비교해 성공/실패를 판정하는가"를 코드 변경 전에 확정해야 한다.

### 2.2 범위 내 (In scope)

- 전체 테스트 스위트 실행과 결과 기록
- 실행 환경(인터프리터·의존성·테스트 DB) 재현 가능화
- 전환 기준 Git Commit 확정

### 2.3 범위 외 (Out of scope)

- 코드 수정 (W0은 측정 단계다)
- 테스트 추가·수정
- 의존성 버전 변경

## 3. 선행 조건 (Entry criteria)

| ID | 조건 | 확인 방법 |
| --- | --- | --- |
| W0-E1 | 상위 계획 §4의 결정 D1~D6이 확정됨 | 계획서 §4 표 |
| W0-E2 | 작업 대상 저장소에 접근 가능 | `git -C workmate-agent status` |

## 4. 요구사항

| ID | 구분 | 요구사항 | 출처 |
| --- | --- | --- | --- |
| W0-R1 | 기능 | 전체 테스트를 실행하고 통과/실패/건너뜀 수를 기록한다 | 계획서 §5 W0 |
| W0-R2 | 기능 | 실행 환경을 제3자가 재현할 수 있도록 문서화한다 | `AGENTS.md` 완료 규칙 |
| W0-R3 | 기능 | 전환 기준 Commit을 하나의 SHA로 확정한다 | 계획서 §7.1 |
| W0-R4 | 제약 | 건너뛴 테스트가 있으면 사유와 해소 여부를 명시한다 | `AGENTS.md` 작업 시작 순서 |
| W0-R5 | 제약 | Secret·Token·개인정보를 증빙에 기록하지 않는다 | `AGENTS.md` 금지 사항 |

## 5. 설계

### 5.1 측정 대상

```
workmate-agent/tests/   63개 test 파일
  ├ 단위 테스트          Domain·Repository·Provider·Workflow
  ├ 계약 테스트          test_contract.py, test_*_migration.py
  ├ 통합 테스트(SQLite)  test_m1_1 / m1_5 / m2_1 / m2_3_integration.py
  └ 통합 테스트(Postgres) WORKMATE_TEST_DATABASE_URL 필요 — 12건
```

### 5.2 실행 환경 정의

| 요소 | 값 | 근거 |
| --- | --- | --- |
| Python | CPython 3.12.13 | `pyproject.toml`의 `requires-python = ">=3.12,<3.13"` |
| 의존성 | `uv.lock` 고정값 | `AGENTS.md` lockfile 규칙 |
| 테스트 DB | PostgreSQL 16 + pgvector | `migrations/004_search_data.sql`의 `CREATE EXTENSION vector, pg_trgm` |

### 5.3 검증 명령

```
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

## 6. 작업 분해 (WBS)

| ID | 작업 | 선행 | 산출물 |
| --- | --- | --- | --- |
| W0-T1 | 작업 트리 상태 확인 및 미커밋 변경 식별 | — | `git status` 결과 |
| W0-T2 | 실행 환경 점검·복구 | W0-T1 | 동작하는 `.venv` |
| W0-T3 | 1차 테스트 실행 (기본 환경) | W0-T2 | 1차 결과 |
| W0-T4 | 미커밋 변경 처리 결정·반영 | W0-T3 | 기준 Commit |
| W0-T5 | 테스트 DB 구성 | W0-T2 | 실행 중인 컨테이너 |
| W0-T6 | 2차 테스트 실행 (확정 기준선) | W0-T4, W0-T5 | 확정 결과 |
| W0-T7 | 증빙·`HANDOFF.md` 기록 | W0-T6 | `result.md` |

## 7. 검증 설계

| ID | 검증 항목 | 방법 | 판정 기준 |
| --- | --- | --- | --- |
| W0-V1 | 전체 테스트 실행 | §5.3 명령 | 실패 0, 오류 0 |
| W0-V2 | 건너뜀 해소 | 실행 로그의 `skipped` 수 | SKIP 0 |
| W0-V3 | 기준 Commit 확정 | `git log -1`, `git status --porcelain` | 작업 트리 clean |
| W0-V4 | 환경 재현성 | 증빙에 기록된 명령으로 재구성 | 동일 결과 |

## 8. 추적성 매트릭스

| 요구사항 | 작업 | 검증 |
| --- | --- | --- |
| W0-R1 | W0-T3, W0-T6 | W0-V1 |
| W0-R2 | W0-T2, W0-T5, W0-T7 | W0-V4 |
| W0-R3 | W0-T1, W0-T4 | W0-V3 |
| W0-R4 | W0-T5, W0-T6 | W0-V2 |
| W0-R5 | W0-T7 | 증빙 검토 |

## 9. 완료 정의 (Exit criteria)

1. 검증 항목 W0-V1~V4가 모두 PASS.
2. 기준 Commit SHA가 증빙과 `HANDOFF.md`에 기록됨.
3. 후행 단계 W1이 참조할 "비교 대상 동작"이 확정됨.

## 10. 실행 결과 (2026-09-23)

| 항목 | 결과 |
| --- | --- |
| 기준 Commit | `workmate-agent@8043c1e` (브랜치 `feat/M0.1-01-sdk-runtime`) |
| 테스트 | **440 passed / 0 failed / 0 skipped** (20.2s) |
| 실행 환경 | CPython 3.12.13, `uv.lock` 그대로, PostgreSQL 16 + pgvector |

### 10.1 발견과 조치

| 발견 | 조치 |
| --- | --- |
| `.venv`가 사라진 `C:\Python312`(3.12.4)를 가리켜 `uv run` 실패 | `uv python install 3.12` → `uv venv --clear --python 3.12` → `uv sync`. 의존성 버전 불변 |
| 미커밋 변경 5개 파일이 동결 구역에 존재 | 논리 단위로 2개 커밋 분리 — `274c204`(proposal_id Schema 누락), `8043c1e`(회의 검색 LLM 근거 답변) |
| PostgreSQL 통합 테스트 12건 SKIP | `pgvector/pgvector:pg16` 테스트 컨테이너 구성 후 전부 실행·통과 |

### 10.2 후행 단계에 넘기는 사실

- `save_checkpoint()`는 [runtime.py:228](../workmate-agent/app/a2a/runtime.py#L228)에서 한 번 쓰기만 하고
  읽는 코드가 없다 → W2·W7에서 Checkpointer 대체 시 기능 손실이 없다.
- `ExternalSyncWorkflow`는 `app/` 안에 호출자가 없으나 M1.2-04·M1.4-01 승인 증빙이 경로를 참조한다
  → W7에서 삭제가 아닌 이동으로 처리한다.
- 테스트 DB는 표준 `postgres` 이미지로는 부족하다(`vector`·`pg_trgm` 확장 필요).

## 11. 위험과 완화

| 위험 | 완화 | 결과 |
| --- | --- | --- |
| 측정 시점 작업 트리가 불안정해 기준선이 흔들린다 | 미커밋 변경을 커밋해 고정 | 해소 |
| 일부 경로가 미검증인 채로 전환에 들어간다 | Postgres 테스트 DB 구성 | 해소 |
| 환경 복구가 결과 계약을 바꾼다 | `uv.lock` 고정, 버전 변경 금지 | 해소 |

## 12. 롤백·중단 기준

W0은 코드를 수정하지 않으므로 롤백 대상이 없다. 단, W0-V1이 FAIL이면 **전환 자체를 착수하지 않는다** —
기준선이 이미 깨진 상태에서 전환하면 실패 원인을 분리할 수 없다.

## 13. 참조

- [30-langgraph-migration-plan.md](30-langgraph-migration-plan.md) §0 전제, §5 작업 순서, §7 동결
- [`AGENTS.md`](../AGENTS.md) 작업 시작 순서·완료 규칙
- 증빙: [`evidence/langgraph/W0/runs/20260923-065508/result.md`](evidence/langgraph/W0/runs/20260923-065508/result.md)
