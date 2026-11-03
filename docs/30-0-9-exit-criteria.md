# W0-9 — 완료 정의

> [30-0-w0-baseline.md](30-0-w0-baseline.md) §9의 상세 문서.

W0는 완료됐으므로 각 조건에 **충족 여부**를 기록한다.

## 1. 완료 조건 (Exit criteria)

| # | 조건 | 판정 근거 | 결과 |
| --- | --- | --- | --- |
| E-1 | 검증 항목 W0-V1~V4가 모두 PASS | [30-0-7](30-0-7-verification.md) | **충족** |
| E-2 | 기준 Commit SHA가 증빙과 `HANDOFF.md`에 기록됨 | 문서 확인 | **충족** |
| E-3 | 후행 단계 W1이 참조할 "비교 대상 동작"이 확정됨 | 440 passed / 0 skipped | **충족** |

## 2. 실제 달성 상태

```
기준 Commit: workmate-agent@8043c1e (브랜치 feat/M0.1-01-sdk-runtime)
테스트:      440 passed / 0 failed / 0 skipped  (20.211s)
실행 환경:   CPython 3.12.13, uv.lock 그대로, PostgreSQL 16 + pgvector
```

### 2.1 세 요소가 다 있다

| 요소 | 값 | 없으면 |
| --- | --- | --- |
| 테스트 결과 | 440 / 0 / 0 | 회귀를 판정할 수 없다 |
| Commit | `8043c1e` | 어느 코드의 결과인지 모른다 |
| 환경 | 3.12.13 + lockfile + pgvector | 재현할 수 없다 |

## 3. 승인 절차

### 3.1 자동 승인 대상이었다

| 조건 | W0 해당 여부 |
| --- | --- |
| 외부 OAuth·실제 Provider 호출 | 없음 |
| 공개 Schema·데이터 모델 변경 | 없음 |
| UI 육안 검수 | 없음 |
| 모델 평가 | 없음 |
| 원격 Push | 없음 — 로컬 커밋만 |

→ **자동 승인 대상.** 검증 4개 항목 전부 PASS, 미실행·수동 검수·차단 없음.

### 3.2 실제 기록

```
latest_run_id:          20260923-065508
latest_run_status:      PASS
latest_approved_run_id: 20260923-065508
approved_at:            2026-09-23 Asia/Seoul
reviewer:               자동 승인(검증 명령)
자동 재작업 착수:        예 (실행 환경 복구)
자동 진행 판정:          진행 — W1을 자동 착수한다
```

### 3.3 `자동 재작업 착수: 예`

`AGENTS.md`가 요구하는 기록이다.

> 실행 증빙과 `HANDOFF.md`에는 `자동 재작업 착수: 예/아니오`를 기록해 재작업 자동 착수 여부를
> 구분한다.

W0에서는 **환경 복구**가 자동 재작업에 해당한다([30-0-3](30-0-3-entry-criteria.md) §3.2).

### 3.4 두 번의 사용자 질문은 자동 승인과 무관하다

| 질문 | 성격 |
| --- | --- |
| 미커밋 변경 처리 | 다른 작업자의 구현을 이력에 남기는 판단 |
| Postgres 테스트 DB | 외부 환경 준비 |

둘 다 **검증 결과의 판정**이 아니라 **작업 범위의 결정**이었다. 검증이 PASS인 상태에서 물었고,
답변 후 기준선이 더 완전해졌다.

**만약 질문 없이 진행했다면**

| 질문 생략 시 | 결과 |
| --- | --- |
| 미커밋 변경을 임의로 커밋 | 다른 작업자의 의도를 모른 채 이력에 남김 |
| 미커밋 변경을 무시 | 기준 Commit 불명확 |
| SKIP 12건을 방치 | Postgres 경로가 전환 내내 미검증 |

## 4. 산출물 체크리스트 (완료)

### 4.1 코드

```
[x] 코드 수정 없음
[x] 미커밋 변경 2개 커밋으로 고정 (274c204, 8043c1e)
[x] 원격 Push 없음
```

### 4.2 환경

```
[x] .venv 재생성 (CPython 3.12.13)
[x] uv sync (uv.lock 그대로)
[x] 테스트 DB 컨테이너 (pgvector/pgvector:pg16)
```

### 4.3 증빙

```
[x] docs/evidence/langgraph/README.md              전환 증빙 인덱스
[x] docs/evidence/langgraph/W0/runs/20260923-065508/result.md
[x] HANDOFF.md
[x] 발견 사항 3건 (W0-F1~F3)
[x] 1차·2차 실행 결과 병기
[x] 테스트 DB 재현 방법
```

## 5. 완료 후 상태

| 항목 | W0 완료 시점 |
| --- | --- |
| 운영 경로 | `WorkflowRegistry` (변경 없음) |
| 코드 | 변경 없음 |
| git 이력 | 2개 커밋 추가 |
| 환경 | 복구됨 |
| 테스트 DB | 실행 중 |
| **기준선** | **확정** |

### 5.1 전환 준비 완료

```
[x] 결정 D1~D6 확정
[x] 기준선 확정
[ ] W1 계약 스냅샷  ← 다음
```

## 6. 완료 판정 체크리스트 (실제 수행)

```
[x] 1.  git status·log 확인 → 미커밋 5개 파일 발견
[x] 2.  환경 점검 → venv 깨짐 발견 → 복구
[x] 3.  1차 테스트 → 440 passed, 12 skipped
[x] 4.  SKIP 사유 확인 → 전부 WORKMATE_TEST_DATABASE_URL 미설정
[x] 5.  사용자 질문 1: 미커밋 변경 처리
[x] 6.  사용자 질문 2: Postgres 테스트 DB
[x] 7.  커밋 2건 (논리 단위 분리)
[x] 8.  테스트 DB 구성 (pgvector 이미지)
[x] 9.  2차 테스트 → 440 passed, 0 skipped
[x] 10. W0-V1~V4 결과 기록
[x] 11. 발견 사항 3건 기록
[x] 12. result.md, evidence README, HANDOFF
[x] 13. 자동 승인 판정 → W1 착수
```

## 7. 다음 단계 전달 사항

| 전달 항목 | 받는 단계 | 용도 |
| --- | --- | --- |
| 기준 Commit `8043c1e` | [W1](30-1-w1-contract-snapshot.md) 외 전 단계 | 스냅샷의 대상, 비교 기준 |
| 440 passed / 0 skipped | 전 단계 | 회귀 판정 |
| 테스트 DB 구성 | 전 단계 | 환경 |
| 검증 명령 | 전 단계 | 같은 명령 사용 |
| **W0-F1** (`save_checkpoint` 미사용) | W2·W5·W7 | Checkpoint 처리 근거 |
| **W0-F2** (`external_sync` 호출자 부재 + 증빙 참조) | W7 | 이동 결정 |
| **W0-F3** (pgvector 필요) | 전 단계 | 환경 구성 |

### 7.1 W1에 특별히 넘기는 것

W0에서 커밋한 2건이 **스냅샷 값을 직접 바꾼다.**

| Commit | 영향받는 케이스 |
| --- | --- |
| `274c204` | `assistant_ask.*` — 컨텍스트에 `proposal_id` |
| `8043c1e` | `search_meetings.*` — warning 분류 |

**W1은 반드시 `8043c1e` 상태에서 스냅샷을 떠야 한다.**

## 8. 참조

- [30-0-7](30-0-7-verification.md) — 검증 결과
- [30-0-10](30-0-10-results.md) — 실행 결과 상세
- 증빙: [`evidence/langgraph/W0/runs/20260923-065508/result.md`](evidence/langgraph/W0/runs/20260923-065508/result.md)
- [`AGENTS.md`](../AGENTS.md) — 자동 승인 규칙
