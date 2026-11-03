# W0-10 — 실행 결과

> [30-0-w0-baseline.md](30-0-w0-baseline.md) §10의 상세 문서.
>
> **이 절은 W0 고유다.** 다른 단계에는 없다. W0는 이미 수행된 단계이므로 결과를 기록한다.

## 1. 확정 기준선

| 항목 | 값 |
| --- | --- |
| 실행일 | 2026-09-23 |
| 실행 ID | `20260923-065508` |
| 기준 Commit | `workmate-agent@8043c1e` |
| 기준 브랜치 | `feat/M0.1-01-sdk-runtime` |
| **테스트** | **440 passed / 0 failed / 0 skipped** (20.211s) |
| 실행 환경 | CPython 3.12.13, `uv.lock` 그대로, PostgreSQL 16 + pgvector |

### 1.1 검증 명령

```bash
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

### 1.2 결과

```
Ran 440 tests in 20.211s

OK
```

## 2. 1차 실행 (SQLite 경로만)

확정 기준선 이전의 측정이다. **SKIP 해소 과정의 기록**으로 남긴다.

```bash
uv run python -m unittest discover -s tests -v
```

```
Ran 440 tests in 5.450s

OK (skipped=12)
```

### 2.1 SKIP 12건

전부 `skipped 'WORKMATE_TEST_DATABASE_URL is not configured'`.

| 테스트 | 수 | 전환 범위 |
| --- | --- | --- |
| `test_hybrid_search_postgres_integration` | 1 | 밖 |
| `test_m1_1_integration` | 1 | 밖 |
| **`test_m1_5_integration`** | **2** | **안** — `daily_briefing`·`rank_priorities` |
| `test_meeting_answer_postgres_integration` | 1 | 밖 |
| `test_meeting_chunk_postgres_integration` | 2 | 밖 |
| `test_postgres_ignored_proposal_integration` | 1 | 밖 |
| **`test_postgres_integration`** | **1** | **안** — Task Snapshot·Message 멱등성 |
| `test_postgres_sync_state_integration` | 1 | 밖 |
| `test_search_data_postgres_integration` | 1 | 밖 |
| `test_trigram_search_postgres_integration` | 1 | 밖 |

**3건이 전환 범위 안이었다.**

### 2.2 소요 시간 비교

| 차수 | 시간 | 차이 |
| --- | --- | --- |
| 1차 (SQLite) | 5.450s | — |
| 2차 (Postgres 포함) | 20.211s | +14.8s |

Postgres 통합 테스트 12건이 추가된 만큼이다.

---

## 3. 발견과 조치

### 3.1 실행 환경 복구 (자동 재작업, 해결됨)

**발견** `uv run`이 실패해 테스트를 실행할 수 없었다.

```
error: Querying Python at `C:\dev\workmate\workmate-agent\.venv\Scripts\python.exe`
failed with exit status exit code: 103
[stderr] No Python at '"C:\Python312\python.exe'
```

**원인** `.venv/pyvenv.cfg`

```
home = C:\Python312
version_info = 3.12.4
```

이 인터프리터가 PC에서 사라졌다. 로컬에는 3.13만 있고 프로젝트는 `>=3.12,<3.13`이다.

**조치**

```bash
uv python install 3.12        # cpython-3.12.13 (20.9MiB) 다운로드
uv venv --clear --python 3.12 # 첫 시도는 --clear 없이 실패
uv sync                       # uv.lock 그대로
```

**판정** `AGENTS.md`의 자동 재시도 범위 — "일시적인 실행 환경처럼 결과 계약을 바꾸지 않는 수정".
`uv.lock`을 그대로 썼고 의존성 버전을 바꾸지 않았다.

---

### 3.2 미커밋 변경 5개 파일 (해결됨)

**발견** 측정 시점에 작업 트리에 변경이 남아 있었다.

```
 M app/meeting_answer.py
 M app/workflows/assistant_router.py
 M app/workflows/meetings.py
 M tests/test_assistant_router.py
 M tests/test_meeting_answer.py
```

5 files changed, 97 insertions(+), 13 deletions(-)

**성격** 모두 전환 계획 §7.2의 동결 구역에 속하며, **공개 응답 값에 영향을 준다** — 즉 W1 계약
스냅샷의 기준선을 바꾼다.

**판단** 제가 쓴 변경이 아니므로 임의로 커밋하지 않고 사용자에게 질문했다.

**사용자 결정** "로컬 커밋으로 고정"

**조치** 논리적 변경 단위로 나눠 2개 커밋으로 남겼다(`AGENTS.md`: 하나의 커밋에 하나의 논리적 변경).

| Commit | 범위 | 내용 |
| --- | --- | --- |
| `274c204` | `assistant_router.py`, `test_assistant_router.py` | `AssistantAskContextProposal` Schema의 required 필드 `proposal_id`를 `_default_proposals_context()` 폴백 경로에서만 누락하던 것 수정(99번 문서 32번 항목) |
| `8043c1e` | `meeting_answer.py`, `workflows/meetings.py`, `test_meeting_answer.py` | `MeetingAnswerService`가 검색 근거만 나열하던 것을 `_summarize_with_llm()`으로 질문에 직접 답하도록 변경. LLM 실패 시 기존 근거 나열 + 경고 폴백. `search_meetings`가 이 경고를 `grounded` 여부에 따라 `INSUFFICIENT_EVIDENCE`와 재시도 가능한 `LLM_PROVIDER_UNAVAILABLE`로 구분 |

**원격 Push는 하지 않았다.**

**주의할 점** 두 번째 커밋은 warning 분류 수정만이 아니라 **실제 LLM 답변 생성**이라는 기능 변경을
포함한다. 커밋 메시지에 명시했다.

---

### 3.3 PostgreSQL 경로 미검증 (해결됨)

**발견** 1차 실행에서 12건이 SKIP됐다. 그중 `test_m1_5_integration`은 `daily_briefing`·
`rank_priorities`의 Postgres 동작을 검증하는 테스트로 **전환 범위 안**이다. D6=B의 DROP Migration도
Postgres 경로에 영향을 준다.

**환경 조사**

```bash
docker --version    # 29.4.3
docker ps           # 엔진 정지
psql --version      # 없음
```

로컬 PostgreSQL이 없고 Docker Desktop은 설치됐으나 엔진이 꺼져 있었다.

**확장 요구사항 확인 (W0-F3)**

```bash
grep -n "CREATE EXTENSION" migrations/*.sql
# 004_search_data.sql:4:  CREATE EXTENSION IF NOT EXISTS vector;
# 004_search_data.sql:5:  CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

표준 `postgres` 이미지에는 `vector`가 없다.

**사용자 결정** "지금 구성해서 기준선에 포함"

**조치**

```bash
docker run -d --name workmate-test-pg \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=workmate_test \
  -p 55432:5432 pgvector/pgvector:pg16
```

**결과** 12건 전부 실행·통과. SKIP 0.

---

## 4. 후행 단계에 넘기는 사실 (W0-F)

### W0-F1 — `save_checkpoint`는 사실상 미사용

**조사**

```bash
grep -rn "save_checkpoint\|load_checkpoint" app tests | grep -v "a2a/persistence.py"
# app/a2a/runtime.py:228:        await self.task_store.save_checkpoint(
# tests/test_persistence.py:55:                first.save_checkpoint(
```

**사실**
- 운영 코드에서 **호출 1곳**([runtime.py:228](../workmate-agent/app/a2a/runtime.py#L228))
- 쓰는 내용: `{"skill_id": ..., "task_id": ...}` + `{"phase": "submitted"}` 마커
- **읽는 코드가 저장소 어디에도 없다**

**영향**

| 단계 | 영향 |
| --- | --- |
| W2 | Checkpointer로 대체해도 기능 손실이 없다 |
| W5 | `save_checkpoint` 호출 제거(W5-T3) |
| W7 | **`a2a_checkpoints` DROP의 근거** |
| D6 | **B안(DROP) 선택의 뒷받침** |

---

### W0-F2 — `external_sync`는 호출자가 없지만 증빙이 참조

**조사**

```bash
grep -rln "external_sync" app tests --include=*.py
# tests/test_google_adapters.py
# tests/test_proposals.py
```

`app/` 안에 호출자가 없다. [dev_gmail_sync_api.py:3](../workmate-agent/app/dev_gmail_sync_api.py#L3)
주석이 확인해 준다.

> 운영 자동 동기화 Job은 아직 없다(`ExternalSyncWorkflow.sync_gmail`는 있지만 어떤 HTTP Route·
> 스케줄러에도 연결되지 않았다).

**그런데 승인 증빙이 참조한다**

```bash
grep -n "external_sync" ../docs/06-delivery-plan.md
# 91:  | M1.2-04 | Cursor·Watch 동기화 | `workmate-agent/app/workflows/external_sync.py` | ... | 완료 |
# 769: | M1.4-01 | 제안 Hub·SSE 발행 | ... `app/workflows/external_sync.py` ... | 완료 |
```

`docs/evidence/`에도 2건이 참조한다.

**영향** W7에서 **삭제가 아닌 이동**(D4=A). 증빙 링크 정정 작업이 필요하다.

---

### W0-F3 — 테스트 DB는 pgvector 이미지가 필요

`migrations/004_search_data.sql`이 `vector`·`pg_trgm` 확장을 요구한다. 표준 `postgres` 이미지로는
부족하다.

**영향** 전 단계의 환경 구성 방법.

---

## 5. 과정에서 있었던 사고

기록으로 남긴다. 같은 실수를 반복하지 않기 위해서다.

### 5.1 파이프가 exit code를 가렸다

첫 테스트 실행에서 `| tail -60`을 썼더니 exit code 0이 나왔다. 실제로는 venv 오류였다.

```
[exited with code 0]     ← 파이프라인의 마지막 명령(tail)의 코드
```

**이후 조치** 출력을 파일로 리디렉션하고 `echo "exit=$?"`로 실제 코드를 확인.

### 5.2 `sed` 구분자를 잘못 써서 파일을 망가뜨렸다

`evidence/langgraph/README.md`의 상태를 갱신하려고 `sed`를 썼는데, 구분자로 `|`를 쓰면서 패턴에도
`|`가 있어 모든 줄 앞에 텍스트가 붙었다.

**조치** 즉시 발견해 파일을 다시 작성했다.

**교훈** 구조화된 문서 편집에 `sed`를 쓰지 않는다. 파일 단위로 다시 쓰거나 전용 편집 도구를 쓴다.

### 5.3 `uv venv`가 기존 venv를 거부했다

```
error: Failed to create virtual environment
  Caused by: A virtual environment already exists at: .venv
hint: Use the `--clear` flag
```

**조치** `--clear` 추가. 기존 venv가 동작하지 않는 상태였으므로 안전했다.

---

## 6. 증빙

| 항목 | 위치 |
| --- | --- |
| 실행 결과 | [`evidence/langgraph/W0/runs/20260923-065508/result.md`](evidence/langgraph/W0/runs/20260923-065508/result.md) |
| 전환 증빙 인덱스 | [`evidence/langgraph/README.md`](evidence/langgraph/README.md) |
| 작업 기록 | [`HANDOFF.md`](../HANDOFF.md) |

## 7. 참조

- [30-0-6](30-0-6-wbs.md) — 작업별 수행 내용
- [30-0-7](30-0-7-verification.md) — 검증 결과
- [30-0-11](30-0-11-risks.md) — 예상 위험과 실제
