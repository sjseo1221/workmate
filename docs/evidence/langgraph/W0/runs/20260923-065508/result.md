# W0 기준선 채증 결과

## 1. 기본 정보

- 작업: LangGraph 전면 전환 W0 — 기준선 채증과 출발점 정리
- 계획 문서: [`docs/30-langgraph-migration-plan.md`](../../../../../30-langgraph-migration-plan.md) §5 W0
- 담당자: Claude
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-09-23
- 실행 ID: `20260923-065508`
- 코드 버전: 측정 시점 `workmate-agent@6a87c80` + 미커밋 변경 5개 파일 → 사용자 결정에 따라 커밋해 전환 기준 Commit을 `8043c1e`로 고정(§8.2)
- 기준 브랜치: `feat/M0.1-01-sdk-runtime`

## 2. 최신 실행과 승인

- latest_run_id: `20260923-065508`
- latest_run_status: PASS
- latest_approved_run_id: `20260923-065508`
- approved_at: 2026-09-23 Asia/Seoul
- reviewer: 자동 승인(검증 명령)
- 자동 재작업 착수: 예 (실행 환경 복구, §8)

## 3. 목표와 완료 기준

- 목표: 전환 착수 전 현재 구현의 테스트 기준선을 확보하고, 전환 출발점이 될 코드 상태를 확정한다.
- 완료 기준: 전체 테스트 실행 결과가 기록되고, 미커밋 변경과 미실행 테스트의 처리 방침이 정해진다.
- 범위: W0
- 미완료·보류: 없음 (미커밋 변경 처리와 Postgres 테스트 구성 모두 §8에서 해결)

## 4. 구현 경로

- 구현 코드: 해당 없음 (W0은 측정 단계이며 코드를 수정하지 않았다)
- Schema 또는 Migration: 해당 없음
- UI: 해당 없음

## 5. 테스트 파일 경로

- 대상: `workmate-agent/tests/` 전체 63개 테스트 파일
- Fixture/입력: 각 테스트의 기존 Fixture
- 모델 평가 Case: 해당 없음

## 6. 실행 명령과 결과

### 6.1 1차 실행 (SQLite 경로만)

```
uv run python -m unittest discover -s tests -v
```

```
Ran 440 tests in 5.450s

OK (skipped=12)
```

건너뛴 12개는 전부 `WORKMATE_TEST_DATABASE_URL is not configured` 사유의 PostgreSQL 통합 테스트였다
(§8.3).

### 6.2 2차 실행 — 확정 기준선 (PostgreSQL 포함)

```
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

```
Ran 440 tests in 20.211s

OK
```

- **총 440개 테스트 통과, 실패 0, 오류 0, SKIP 0.** 이 결과를 전환 기준선으로 확정한다.
- 전환 범위 안의 PostgreSQL 테스트도 모두 실행됐다 — `test_m1_5_integration`(daily_briefing·
  rank_priorities의 Postgres 경계 2건), `test_postgres_integration`(Task Snapshot·Message 멱등성),
  `test_hybrid_search_postgres_integration`, `test_meeting_chunk_postgres_integration` 등.
- 테스트 DB는 로컬 전용 컨테이너이며 접속 정보는 개발용 기본값이다. 운영 Secret은 사용하지 않았고
  Token·개인정보는 증빙에 기록하지 않았다.

### 6.3 테스트 DB 재현 방법

```
docker run -d --name workmate-test-pg \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=workmate_test \
  -p 55432:5432 pgvector/pgvector:pg16
```

`migrations/004_search_data.sql`이 `vector`·`pg_trgm` 확장을 요구하므로 표준 `postgres` 이미지가 아닌
`pgvector/pgvector:pg16`을 사용한다. 테스트가 Migration을 직접 적용하므로 별도 초기화는 필요 없다.

## 7. 검수 항목

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| 전체 테스트 실행 | PASS | §6.2 `Ran 440 tests ... OK` (SKIP 0) |
| 실행 환경 복구 | PASS | §8.1 |
| 기준 Commit 확정 | PASS | §8.2 — `workmate-agent@8043c1e` |
| PostgreSQL 경로 기준선 | PASS | §6.2·§6.3 — 통합 테스트 12개 전부 실행·통과 |

## 8. 문제와 수정 이력

### 8.1 실행 환경 복구 (자동 재작업, 해결됨)

- 발견된 문제: `uv run`이 `No Python at '"C:\Python312\python.exe'`로 실패해 테스트를 실행할 수 없었다.
- 원인: `.venv/pyvenv.cfg`의 `home = C:\Python312`(CPython 3.12.4)가 가리키는 인터프리터가 이 PC에서
  사라졌다. 로컬에 설치된 Python은 3.13뿐이었고, 프로젝트는 `requires-python = ">=3.12,<3.13"`이다.
- 수정 내용: `uv python install 3.12`(3.12.13 설치) → `uv venv --clear --python 3.12` → `uv sync`.
  `uv.lock`을 그대로 사용했고 의존성 버전은 변경하지 않았다.
- 판정: 결과 계약을 바꾸지 않는 실행 환경 보정이므로 `AGENTS.md`의 자동 재시도 범위에 해당한다.

### 8.2 미커밋 변경 5개 파일 (해결됨)

측정 시점에 작업 트리에 다음 변경이 커밋되지 않은 상태로 남아 있었다. 모두 전환 계획 §7.2의 동결
구역에 속하며, 공개 응답 값에 영향을 주므로 W1 계약 스냅샷의 기준선을 바꾼다.

| 파일 | 변경 내용 |
| --- | --- |
| `app/workflows/assistant_router.py` | `_default_proposals_context()`가 Schema required 필드 `proposal_id`를 누락하던 것 수정 |
| `app/workflows/meetings.py` | 검색 warning을 `INSUFFICIENT_EVIDENCE` 고정에서 grounded 여부에 따라 `LLM_PROVIDER_UNAVAILABLE`과 구분 |
| `app/meeting_answer.py` | 위 변경에 대응하는 구현 |
| `tests/test_assistant_router.py`, `tests/test_meeting_answer.py` | 위 두 변경의 테스트 |

이 변경을 포함한 상태로 440개 테스트가 통과했다.

**해결(2026-09-23, 사용자 결정 "로컬 커밋으로 고정"):** 논리적 변경 단위로 나눠 2개 로컬 커밋으로
남기고 전환 기준 Commit을 `8043c1e`로 고정했다. 원격 Push는 하지 않았다.

| Commit | 범위 |
| --- | --- |
| `274c204` | `fix: include required proposal_id in assistant context proposal fallback` — `assistant_router.py`, `test_assistant_router.py` |
| `8043c1e` | `feat: generate grounded LLM answers for meeting search with source-backed fallback` — `meeting_answer.py`, `workflows/meetings.py`, `test_meeting_answer.py` |

두 번째 커밋은 warning 분류 수정만이 아니라 `MeetingAnswerService`가 근거 나열 대신
`_summarize_with_llm()`으로 실제 답변을 생성하도록 바꾸는 변경을 포함한다. LLM 호출이 실패하면
기존 근거 나열 답변과 경고를 함께 반환하는 폴백을 유지한다.

### 8.3 PostgreSQL 경로 미검증 (해결됨)

- 발견된 문제: 12개 통합 테스트가 SKIP되어 PostgreSQL 경로의 기준선이 없었다. 이 중
  `test_m1_5_integration`은 `daily_briefing`·`rank_priorities`의 Postgres 동작을 검증하는
  테스트로 전환 범위 안에 있고, D6=B(`a2a_checkpoints` DROP Migration)도 Postgres 경로에 영향을 준다.
- 수정 내용(2026-09-23, 사용자 결정 "지금 구성해서 기준선에 포함"): Docker Desktop 엔진을 기동하고
  `pgvector/pgvector:pg16` 테스트 컨테이너를 띄운 뒤 `WORKMATE_TEST_DATABASE_URL`을 설정해
  전체 테스트를 다시 실행했다(§6.2·§6.3). 12개 전부 실행·통과했다.
- 참고: 이 PC에 로컬 PostgreSQL은 설치돼 있지 않고 `compose.yaml`에도 DB 서비스가 없어, 테스트용
  컨테이너를 별도로 띄우는 방식을 택했다.

## 9. 최종 판단

- 승인 여부: 자동 승인(검증 명령)
- latest_run_status: PASS — 검수 항목 4개 전부 PASS, 미실행·수동 검수·차단 없음
- 자동 진행 판정: 진행 — W1을 자동 착수한다
- 자동 재작업 착수: 예 (§8.1 실행 환경 복구)
- 확정된 전환 기준선
  - 기준 Commit: `workmate-agent@8043c1e` (브랜치 `feat/M0.1-01-sdk-runtime`)
  - 테스트: 440 passed / 0 failed / 0 skipped
  - 실행 환경: CPython 3.12.13, `uv.lock` 그대로, PostgreSQL 16 + pgvector 테스트 컨테이너
- 다음 착수 백로그: W1 계약 스냅샷 추출 — **옛 구현이 살아 있는 동안에만 수행 가능**하므로 W3보다
  반드시 먼저 끝낸다(계획서 §1-4).
