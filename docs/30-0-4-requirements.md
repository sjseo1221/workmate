# W0-4 — 요구사항 명세

> [30-0-w0-baseline.md](30-0-w0-baseline.md) §4의 상세 문서.

W0는 완료된 단계이므로 각 요구사항에 **충족 여부**를 함께 기록한다.

## 요약

| ID | 구분 | 한 줄 | 우선순위 | 검증 | 결과 |
| --- | --- | --- | --- | --- | --- |
| W0-R1 | 기능 | 전체 테스트 실행·기록 | 필수 | W0-V1 | **충족** |
| W0-R2 | 기능 | 실행 환경 재현 가능화 | 필수 | W0-V4 | **충족** |
| W0-R3 | 기능 | 전환 기준 Commit 확정 | 필수 | W0-V3 | **충족** |
| W0-R4 | 제약 | 건너뛴 테스트의 사유·해소 명시 | 필수 | W0-V2 | **충족** |
| W0-R5 | 제약 | Secret·개인정보 비기록 | 필수 | 증빙 검토 | **충족** |
| W0-R6 | 제약 | 코드를 수정하지 않는다 | 필수 | `git diff` | **충족**(§6) |
| W0-R7 | 기능 | 발견 사항을 기록한다 | 필수 | 증빙 | **충족** |

---

## W0-R1 — 전체 테스트 실행

**설명** 전체 테스트를 실행하고 통과/실패/건너뜀 수를 기록한다.

**근거** [계획서 §5 W0](30-langgraph-migration-plan.md).

**수용 기준**
- 63개 테스트 파일 전체 실행
- 통과·실패·건너뜀 수 기록
- 실행 명령이 증빙에 남는다

**결과** **충족**

```
Ran 440 tests in 20.211s
OK
```

실패 0, 오류 0, SKIP 0.

**검증** W0-V1

---

## W0-R2 — 환경 재현 가능화

**설명** 실행 환경을 제3자가 재현할 수 있도록 문서화한다.

**근거** `AGENTS.md` 완료 규칙. 재현 불가한 결과는 증빙 가치가 없다.

**수용 기준**

| 요소 | 기록 |
| --- | --- |
| Python 버전 | CPython 3.12.13 |
| 의존성 | `uv.lock` 고정값 |
| 테스트 DB | 구성 명령 |

**결과** **충족**

```bash
# 환경 복구
uv python install 3.12
uv venv --clear --python 3.12
uv sync

# 테스트 DB
docker run -d --name workmate-test-pg \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=workmate_test \
  -p 55432:5432 pgvector/pgvector:pg16
```

**검증** W0-V4

---

## W0-R3 — 기준 Commit 확정

**설명** 전환 기준 Commit을 하나의 SHA로 확정한다.

**근거** [계획서 §7.1](30-langgraph-migration-plan.md). 롤백과 비교의 기준점.

**수용 기준**
- 작업 트리가 clean
- SHA가 증빙과 `HANDOFF.md`에 기록

**결과** **충족** — `workmate-agent@8043c1e`

측정 시점에는 `6a87c80` + 미커밋 변경 5개 파일이었다. 사용자 결정에 따라 2개 커밋으로 고정했다.

| Commit | 범위 |
| --- | --- |
| `274c204` | `fix: include required proposal_id in assistant context proposal fallback` |
| `8043c1e` | `feat: generate grounded LLM answers for meeting search with source-backed fallback` |

**검증** W0-V3

---

## W0-R4 — 건너뜀 사유·해소

**설명** 건너뛴 테스트가 있으면 사유와 해소 여부를 명시한다.

**근거** `AGENTS.md` 작업 시작 순서.

> 외부 인증이나 Provider Secret이 필요한 테스트는 설정 여부를 먼저 확인하고, **실행하지 못한 경우
> 원인과 재현 조건을 기록한다.**

**수용 기준**
- SKIP된 테스트의 목록과 사유
- 해소 여부

**결과** **충족**

| 단계 | SKIP | 사유 |
| --- | --- | --- |
| 1차 | 12건 | `WORKMATE_TEST_DATABASE_URL is not configured` |
| 2차 | **0건** | 테스트 DB 구성으로 해소 |

**해소한 12건**

```
test_hybrid_search_postgres_integration
test_m1_1_integration
test_m1_5_integration (2건)
test_meeting_answer_postgres_integration
test_meeting_chunk_postgres_integration (2건)
test_postgres_ignored_proposal_integration
test_postgres_integration
test_postgres_sync_state_integration
test_search_data_postgres_integration
test_trigram_search_postgres_integration
```

**검증** W0-V2

---

## W0-R5 — Secret 비기록

**설명** Secret·Token·개인정보를 증빙에 기록하지 않는다.

**근거** `AGENTS.md` 금지 사항.

**수용 기준**
- 증빙에 토큰·키 미포함
- 테스트 DB 접속 정보는 개발용 기본값

**결과** **충족**

증빙에 기록한 접속 정보는 로컬 테스트 컨테이너의 기본값이며 운영 Secret이 아니다. 증빙에 이 사실을
명시했다.

---

## W0-R6 — 코드 무수정

**설명** W0는 측정 단계이므로 코드를 수정하지 않는다.

**근거** 측정을 위해 대상을 바꾸면 무엇을 측정했는지 알 수 없다.

**수용 기준**
- 새 코드 작성 없음
- 기존 코드 수정 없음

**결과** **충족** — 단 해석이 필요하다(§6).

| 구분 | W0에서 |
| --- | --- |
| 새 코드 작성 | 없음 |
| 기존 코드 수정 | 없음 |
| 미커밋 변경 커밋 | **있음** — 이미 있던 변경의 고정 |
| 환경 복구 | 있음 — 코드 아님 |

---

## W0-R7 — 발견 사항 기록

**설명** 조사 중 발견한 사실을 기록한다. 고치지 않는다.

**근거** 측정 단계의 원칙. 발견을 고치면 기준선이 흔들린다.

**수용 기준**
- 발견 사항이 증빙에 기록
- 이후 단계에 전달

**결과** **충족** — 3건 기록

| ID | 발견 | 전달 |
| --- | --- | --- |
| W0-F1 | `save_checkpoint` 미사용 | W2·W5·W7 |
| W0-F2 | `external_sync` 호출자 부재 + 증빙 참조 | W7 |
| W0-F3 | pgvector 필요 | 전 단계 |

---

## 6. W0-R6의 해석

"코드를 수정하지 않는다"와 "미커밋 변경을 커밋했다"가 충돌하는 것처럼 보인다.

### 6.1 무엇이 바뀌었나

| 항목 | 커밋 전 | 커밋 후 |
| --- | --- | --- |
| 작업 트리의 파일 내용 | X | **X**(동일) |
| git 이력 | 변경이 없는 상태 | 2개 커밋 |
| 테스트 결과 | 440 passed | 440 passed |

**파일 내용이 바뀌지 않았으므로 기준선이 흔들리지 않는다.**

### 6.2 왜 커밋했나

기준 Commit을 확정하려면(W0-R3) 작업 트리가 clean해야 한다. 미커밋 변경이 있으면

| 문제 | 설명 |
| --- | --- |
| SHA로 상태를 특정할 수 없다 | "`6a87c80` + 어떤 변경" |
| 롤백 대상이 불명확 | revert 범위를 특정할 수 없다 |
| 나중에 변경이 사라질 수 있다 | 누가 되돌리면 기준선이 달라진다 |

### 6.3 사용자 결정이었다

제가 쓴 변경이 아니므로 임의로 커밋하지 않고 질문했다. 사용자가 "로컬 커밋으로 고정"을 선택했다.

**원격 Push는 하지 않았다**(`AGENTS.md` 커밋 규칙).

## 참조

- [30-0-10](30-0-10-results.md) — 실행 결과 상세
- [30-0-7](30-0-7-verification.md) — 검증
- [`AGENTS.md`](../AGENTS.md) — 작업 시작 순서, 금지 사항
