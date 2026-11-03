# W0-5 — 설계

> [30-0-w0-baseline.md](30-0-w0-baseline.md) §5의 상세 문서.

## 1. 측정 대상

```
workmate-agent/tests/   63개 test 파일
  ├ 단위 테스트          Domain·Repository·Provider·Workflow
  ├ 계약 테스트          test_contract.py, test_*_migration.py
  ├ 통합 테스트(SQLite)  test_m1_1 / m1_5 / m2_1 / m2_3_integration.py
  └ 통합 테스트(Postgres) WORKMATE_TEST_DATABASE_URL 필요 — 12건
```

### 1.1 테스트 분류와 기준선에서의 의미

| 분류 | 수 | 기준선에서의 역할 |
| --- | --- | --- |
| 단위 | 대다수 | 개별 동작 |
| 계약 | 다수 | **공개 인터페이스** — 전환이 깨뜨리면 안 되는 것 |
| 통합(SQLite) | 4 | 기본 경로 |
| 통합(Postgres) | 12 | **운영 백엔드 경로** |

**Postgres 12건이 처음에 SKIP됐다.** 운영 백엔드가 기준선에서 빠지는 문제였다.

### 1.2 전환 범위와의 관계

| 구분 | 수 | W3 이후 |
| --- | --- | --- |
| `app.workflows`·`workflow_registry`·`a2a.runtime` 의존 | 18 | 재작성 대상 |
| 나머지 | 45 | **수정 없이 통과해야 한다**(계획서 §9-3) |

W0 시점에는 구분하지 않고 전체를 측정한다. 구분은 W1·W3에서 쓴다.

## 2. 실행 환경 정의

| 요소 | 값 | 근거 |
| --- | --- | --- |
| Python | CPython 3.12.13 | `pyproject.toml`의 `requires-python = ">=3.12,<3.13"` |
| 의존성 | `uv.lock` 고정값 | `AGENTS.md` lockfile 규칙 |
| 테스트 DB | PostgreSQL 16 + pgvector | `migrations/004_search_data.sql` |

### 2.1 Python 버전 제약

`pyproject.toml`:

```toml
requires-python = ">=3.12,<3.13"
```

상한이 있는 이유는 조사하지 않았다(W0 범위 밖). 그러나 **이 제약을 지켜야 한다** — 3.13으로 돌리면
의존성 호환성이 달라질 수 있고, 그러면 기준선이 다른 환경의 것이 된다.

### 2.2 의존성 고정

`uv.lock`을 그대로 쓴다. 환경 복구 시에도 `uv sync`로 lockfile의 버전을 설치했다.

**버전이 하나라도 달라지면 기준선이 다른 환경의 것이 된다.**

### 2.3 테스트 DB 요구사항 (W0-F3)

표준 `postgres` 이미지로는 부족하다.

```sql
-- migrations/004_search_data.sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

| 확장 | 용도 |
| --- | --- |
| `vector` | pgvector — 회의 검색 임베딩 |
| `pg_trgm` | 트라이그램 — 키워드 검색 |

`pg_trgm`은 contrib이라 표준 이미지에 있지만, `vector`는 없다.

**선택** `pgvector/pgvector:pg16` 이미지.

## 3. 검증 명령

### 3.1 확정 명령

```bash
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

### 3.2 명령 구성 요소

| 요소 | 이유 |
| --- | --- |
| `WORKMATE_TEST_DATABASE_URL` | Postgres 통합 테스트 12건을 활성화 |
| `uv run` | lockfile의 의존성으로 실행 |
| `-m unittest discover -s tests` | 프로젝트가 unittest를 쓴다 |
| `-v` | 테스트별 결과를 남겨 SKIP 사유를 볼 수 있다 |

### 3.3 포트 선택

`55432`를 썼다. 기본 `5432`를 피한 이유는 로컬에 다른 PostgreSQL이 있을 경우 충돌을 피하기 위해서다.

**IPv4 주소(`127.0.0.1`)를 명시했다.** [main.py](../workmate-agent/app/main.py)가 IPv4를 강제하는
환경이므로 `localhost`가 IPv6로 해석되면 연결이 실패할 수 있다.

## 4. 측정 절차 설계

### 4.1 두 번 실행한 이유

| 차수 | 목적 | 결과 |
| --- | --- | --- |
| 1차 | 현재 상태 파악 | 440 passed, **12 skipped** |
| 2차 | 확정 기준선 | 440 passed, **0 skipped** |

1차에서 SKIP을 발견하고, 사용자 결정 후 환경을 보강해 2차를 돌렸다.

**1차 결과도 증빙에 남긴다.** "왜 두 번 돌렸는가"의 기록이다.

### 4.2 미커밋 변경 처리 순서

```
1. 측정 (미커밋 변경 포함 상태)
2. 결과 확인 → 440 passed
3. 사용자에게 질문
4. 커밋
5. 재측정 (Postgres 포함)
```

**커밋 전에 측정한 것이 중요하다.** 커밋이 결과를 바꾸지 않았음을 확인할 수 있다.

## 5. 발견 사항 조사 설계

W0는 측정이 주 목적이지만, 조사도 함께 했다. **이후 단계의 설계에 필요한 사실**을 미리 확보하기
위해서다.

### 5.1 조사한 것

| 대상 | 방법 | 결과 |
| --- | --- | --- |
| `save_checkpoint` 호출자 | `grep -rn "save_checkpoint" app tests` | 호출 1곳, 읽는 코드 0(W0-F1) |
| `external_sync` 호출자 | `grep -rln "external_sync" app tests` | `app/` 0, 테스트 2(W0-F2) |
| 테스트-코드 의존 | `grep -rln "app\.workflows" tests/*.py` | 18개 파일 |
| Skill 목록 | `runtime.py`의 `_SKILLS` | 11개 |

### 5.2 왜 W0에서 조사했나

| 이유 | 설명 |
| --- | --- |
| 계획 정밀화 | 30-x 문서를 사실 기준으로 쓸 수 있다 |
| 결정 지원 | D4·D6 판단에 필요 |
| 시한 | 옛 코드가 살아 있을 때만 가능한 조사도 있다 |

**W0-F1이 D6=B(DROP) 결정을 뒷받침했다.**

## 6. 증빙 설계

### 6.1 형식

기존 마일스톤 증빙(`docs/evidence/Mx/Mx.y/runs/{run_id}/result.md`)의 형식을 따른다.

```
1. 기본 정보          작업·담당자·상태·실행일·실행 ID·코드 버전
2. 최신 실행과 승인    latest_run_id·status·approved_run_id·reviewer
3. 목표와 완료 기준
4. 구현 경로          (W0는 "해당 없음")
5. 테스트 파일 경로
6. 실행 명령과 결과
7. 검수 항목          항목별 PASS/FAIL
8. 문제와 수정 이력    발견·원인·조치
9. 최종 판단          승인 여부·자동 진행 판정·다음 착수
```

### 6.2 W0 고유 항목

| 항목 | 이유 |
| --- | --- |
| §10.2 후행 단계에 넘기는 사실 | 발견 사항 3건 |
| `자동 재작업 착수: 예` | `AGENTS.md` 요구 |
| 1차·2차 실행 결과 병기 | SKIP 해소 과정 |

### 6.3 run_id 형식

`YYYYMMDD-HHMMSS`. 기존 증빙의 규칙을 따랐다 — `20260923-065508`.

## 7. 설계 결정 요약

| ID | 결정 | 근거 |
| --- | --- | --- |
| W0-D1 | 확정 기준선은 Postgres 포함(SKIP 0) | 운영 백엔드가 빠지면 안 된다 |
| W0-D2 | 1차 결과도 증빙에 남긴다 | 해소 과정의 기록 |
| W0-D3 | 커밋 전에 먼저 측정 | 커밋이 결과를 바꾸지 않음을 확인 |
| W0-D4 | 발견 사항을 고치지 않고 기록 | 측정 단계의 원칙 |
| W0-D5 | `pgvector/pgvector:pg16` 이미지 | `vector` 확장 필요(W0-F3) |

## 8. 참조

- [30-0-10](30-0-10-results.md) — 실행 결과
- [30-0-6](30-0-6-wbs.md) — 작업 순서
- `pyproject.toml`, `migrations/004_search_data.sql`
