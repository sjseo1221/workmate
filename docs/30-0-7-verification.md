# W0-7 — 검증 설계

> [30-0-w0-baseline.md](30-0-w0-baseline.md) §7의 상세 문서.

W0는 완료됐으므로 각 검증에 **실제 결과**를 함께 기록한다.

## 1. 검증 목록

| ID | 검증 항목 | 대상 요구사항 | 방법 | 판정 기준 | 결과 |
| --- | --- | --- | --- | --- | --- |
| W0-V1 | 전체 테스트 실행 | W0-R1 | §5.3 명령 | 실패 0, 오류 0 | **PASS** |
| W0-V2 | 건너뜀 해소 | W0-R4 | 로그의 `skipped` 수 | SKIP 0 | **PASS** |
| W0-V3 | 기준 Commit 확정 | W0-R3 | `git log -1`, `git status --porcelain` | 트리 clean | **PASS** |
| W0-V4 | 환경 재현성 | W0-R2 | 증빙 명령으로 재구성 | 동일 결과 | **PASS** |

## 2. 검증 케이스와 실제 결과

### W0-V1 — 전체 테스트 실행

**명령**

```bash
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

**결과**

```
Ran 440 tests in 20.211s
OK
```

| 항목 | 값 |
| --- | --- |
| 실행 | 440 |
| 실패 | 0 |
| 오류 | 0 |
| 건너뜀 | 0 |

**판정 PASS**

#### 2.1.1 exit code 확인의 교훈

1차 시도에서 `| tail -60` 파이프를 썼더니 **exit code 0**이 나왔다. 실제로는 venv 오류로 테스트가
실행되지 않았다.

```
error: Querying Python at ... failed with exit status exit code: 103
[exited with code 0]
```

**파이프라인의 exit code는 마지막 명령의 것이다.** 이후 실행에서는

```bash
... > {log} 2>&1; echo "exit=$?"; tail -25 {log}
```

로 바꿔 실제 종료 코드를 확인했다.

**이 교훈이 이후 단계에도 적용된다** — 검증 명령의 결과를 파이프로 가리지 않는다.

---

### W0-V2 — 건너뜀 해소

**1차 결과**

```
OK (skipped=12)
```

**SKIP 사유 확인**

```bash
grep -n "skipped" {log}
```

12건 전부 `skipped 'WORKMATE_TEST_DATABASE_URL is not configured'`.

| 테스트 | 수 |
| --- | --- |
| `test_hybrid_search_postgres_integration` | 1 |
| `test_m1_1_integration` | 1 |
| `test_m1_5_integration` | 2 |
| `test_meeting_answer_postgres_integration` | 1 |
| `test_meeting_chunk_postgres_integration` | 2 |
| `test_postgres_ignored_proposal_integration` | 1 |
| `test_postgres_integration` | 1 |
| `test_postgres_sync_state_integration` | 1 |
| `test_search_data_postgres_integration` | 1 |
| `test_trigram_search_postgres_integration` | 1 |

**2차 결과** SKIP 0.

**판정 PASS**

#### 2.2.1 왜 해소가 중요했나

SKIP 12건 중 **전환 범위 안의 테스트가 있었다.**

| 테스트 | 전환 범위 |
| --- | --- |
| `test_m1_5_integration` | **범위 내** — `daily_briefing`·`rank_priorities`의 Postgres 경계 |
| `test_postgres_integration` | 범위 내 — Task Snapshot·Message 멱등성 |
| 나머지 | 범위 밖이지만 회귀 감시선 |

또한 D6=B(`a2a_checkpoints` DROP)가 Postgres 경로에 영향을 준다. 기준선에 없으면 W7에서 검증할 수
없다.

---

### W0-V3 — 기준 Commit 확정

**확인**

```bash
git log --oneline -3
# 8043c1e feat: generate grounded LLM answers for meeting search with source-backed fallback
# 274c204 fix: include required proposal_id in assistant context proposal fallback
# 6a87c80 fix: read_email_workflow now reads the logged-in user's own Gmail, ...

git status --porcelain
# (출력 없음)
```

**판정 PASS** — 작업 트리 clean, 기준 Commit `8043c1e`.

#### 2.3.1 커밋 전후의 테스트 결과

| 시점 | 결과 |
| --- | --- |
| 커밋 전(1차) | 440 passed, 12 skipped |
| 커밋 후(2차) | 440 passed, 0 skipped |

**통과 수가 같다.** 커밋은 파일 내용을 바꾸지 않았고, SKIP 변화는 테스트 DB 구성 때문이다.

---

### W0-V4 — 환경 재현성

**기록한 명령**

```bash
# Python
uv python install 3.12
uv venv --clear --python 3.12
uv sync

# 테스트 DB
docker run -d --name workmate-test-pg \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=workmate_test \
  -p 55432:5432 pgvector/pgvector:pg16
```

**판정 PASS** — 증빙 §6.3에 재현 방법을 기록했다.

#### 2.4.1 재현에 필요한 것을 빠뜨리지 않았나

| 요소 | 기록 여부 |
| --- | --- |
| Python 버전 | ✓ CPython 3.12.13 |
| 의존성 | ✓ `uv.lock` 그대로 |
| 테스트 DB 이미지 | ✓ `pgvector/pgvector:pg16` |
| **왜 pgvector인가** | ✓ `migrations/004_search_data.sql`의 확장 요구 |
| 포트 | ✓ 55432 |
| 접속 URL | ✓ 검증 명령에 포함 |
| OS 고유 설정 | Windows Selector Event Loop는 코드에 있음 |

**"왜 pgvector인가"를 기록한 것이 중요하다.** 표준 postgres로 시도하면 실패하는데, 이유를 모르면
시간을 쓴다.

---

## 3. 검증 결과 요약

| 검증 | 결과 | 근거 |
| --- | --- | --- |
| W0-V1 | PASS | 440 passed / 0 failed / 0 errors |
| W0-V2 | PASS | SKIP 0 |
| W0-V3 | PASS | `8043c1e`, 트리 clean |
| W0-V4 | PASS | 재현 명령 기록 |

**4개 항목 전부 PASS. 미실행·수동 검수·차단 없음.**

→ `AGENTS.md`의 자동 승인 조건 충족([30-0-9](30-0-9-exit-criteria.md) §3).

## 4. 검증 설계에서 배운 것

### 4.1 검증 명령이 실패했는지 확인하는 것도 검증이다

exit code를 파이프가 가린 사건(§2.1.1)은 "테스트가 통과했다"고 잘못 판정할 뻔한 경우다.

**검증 명령의 결과를 신뢰하려면 그 명령이 제대로 실행됐는지부터 확인해야 한다.**

### 4.2 SKIP을 PASS로 세지 않는다

`OK (skipped=12)`는 unittest 기준으로 "성공"이다. 그러나 기준선으로는 불완전하다.

**"OK"라는 글자만 보고 넘어가면 12건이 빠진 기준선을 쓰게 된다.**

### 4.3 재현 방법에 "왜"를 적는다

명령만 적으면 나중에 바꿔도 되는지 모른다. `pgvector` 이미지를 쓴 이유를 적었기에, 다른 이미지로
바꾸면 안 된다는 것을 알 수 있다.

## 5. 검증 결과의 소비

| 결과 | 소비처 |
| --- | --- |
| 440 passed / 0 skipped | 전 단계의 기준선 |
| 기준 Commit `8043c1e` | [W1-E1](30-1-3-entry-criteria.md), 전 단계 |
| 테스트 DB 구성 | 전 단계 |
| 검증 명령 | 전 단계가 같은 명령을 쓴다 |

## 6. 참조

- [30-0-10](30-0-10-results.md) — 실행 결과 상세
- [30-0-9](30-0-9-exit-criteria.md) — 완료 판정
- 증빙: [`evidence/langgraph/W0/runs/20260923-065508/result.md`](evidence/langgraph/W0/runs/20260923-065508/result.md)
