# W1-3 — 선행 조건

> [30-1-w1-contract-snapshot.md](30-1-w1-contract-snapshot.md) §3의 상세 문서.

## 1. 선행 조건 목록

| ID | 조건 | 출처 | 확인 방법 | 미충족 시 |
| --- | --- | --- | --- | --- |
| W1-E1 | W0 완료, 기준 Commit 고정 | [30-0](30-0-w0-baseline.md) §10 | `git rev-parse --short HEAD` = `8043c1e`, 트리 clean | 착수 금지 |
| W1-E2 | 전체 테스트 440 passed / 0 skipped | 동상 | 스위트 실행 | 착수 금지 |
| W1-E3 | 테스트 DB 기동 | 동상 | `docker ps` | 컨테이너 재기동 |
| W1-E4 | 전환 브랜치 준비 | 계획서 §7.1 | `git branch --show-current` | 브랜치 생성 |
| W1-E5 | **옛 구현이 온전함** | — | `ls app/workflows/` 9개 파일 | **착수 불가(복구 필요)** |

## 2. 각 조건의 근거

### 2.1 W1-E1 — 기준 Commit 고정

스냅샷은 "이 Commit의 구현이 이 값을 냈다"는 기록이다. 어느 Commit인지 특정되지 않으면 기록의 의미가
약해진다.

W0에서 미커밋 변경 5개 파일을 2개 커밋으로 고정해 기준을 `8043c1e`로 확정했다. 그중 두 변경은
**스냅샷 값에 직접 영향을 준다.**

| Commit | 영향 |
| --- | --- |
| `274c204` | `_default_proposals_context()`에 `proposal_id` 추가 → `assistant_ask` 컨텍스트 값 변경 |
| `8043c1e` | 검색 warning이 `grounded`에 따라 `INSUFFICIENT_EVIDENCE`/`LLM_PROVIDER_UNAVAILABLE`로 갈림 → `search_meetings` 케이스 값 변경 |

이 커밋 이전 상태로 스냅샷을 뜨면 W3에서 전부 불일치가 난다.

### 2.2 W1-E2 — 기준선 유지

W0 측정 이후 W1 착수까지 시간이 지났다면 다시 확인한다. 특히 의존성이나 로컬 환경이 바뀌지 않았는지
본다.

기대값: **440 passed / 0 failed / 0 skipped**.

### 2.3 W1-E3 — 테스트 DB

`search_meetings`·`analyze_meeting` 케이스는 pgvector 하이브리드 검색과 색인을 거친다. SQLite만으로는
이 두 Skill의 스냅샷을 만들 수 없다.

```
docker run -d --name workmate-test-pg \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=workmate_test \
  -p 55432:5432 pgvector/pgvector:pg16
```

### 2.4 W1-E4 — 전환 브랜치

`feat/lg-rewrite`에서 작업한다. W1 산출물은 `tests/` 신규 파일뿐이라 `main`에 영향이 없지만, 전환
관련 커밋을 한 브랜치에 모아야 W9에서 전체 diff를 볼 수 있다.

### 2.5 W1-E5 — 옛 구현의 온전함 (W1 고유 조건)

다른 단계에는 없는 조건이다. W1은 **옛 구현을 실행해 그 출력을 기록**하므로, 옛 구현이 온전해야 한다.

| 확인 | 기대 |
| --- | --- |
| `app/workflows/` 파일 수 | 9개(`__init__`·`registry`·`priority`·`daily_briefing`·`weekly_report`·`meetings`·`assistant_skills`·`assistant_router`·`external_sync`·`weekly_classification`) |
| `WorkflowRegistry` 등록 | 12개(공개 11 + `runtime_bootstrap`) |
| 기존 테스트 | 전부 통과 |

W7에서 이 코드가 삭제되므로, 그 이후에는 W1을 재실행할 수 없다.

## 3. 착수 전 확인 명령

```bash
cd workmate-agent

# W1-E1
git rev-parse --short HEAD        # 8043c1e
git status --porcelain            # 출력 없음

# W1-E4
git branch --show-current         # feat/lg-rewrite

# W1-E5
ls app/workflows/                 # 파일 목록 확인
grep -c "registry.register" app/a2a/runtime.py   # 12

# W1-E3
docker ps --filter name=workmate-test-pg --format "{{.Status}}"

# W1-E2
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

## 4. Skill별 추가 선행 조건

케이스를 만들려면 Skill마다 필요한 준비가 다르다.

| Skill | 필요한 것 | 기존 자산 |
| --- | --- | --- |
| `rank_priorities` | 임시 SQLite + Task Fixture | [`work_domain.py`](../workmate-agent/tests/fixtures/work_domain.py)의 `task_fixture()` |
| `daily_briefing` | Fake Gmail·Calendar Adapter, LLM patch | `provider_factory` 주입 지점이 이미 있음 |
| `weekly_report` | LLM Fake(`LLMClient` 주입) | `build_weekly_report_workflow`의 주입 파라미터 |
| `analyze_meeting` | Fake STT·R2, 테스트 Postgres | [`fake_realtime_stt.py`](../workmate-agent/tests/fixtures/fake_realtime_stt.py), [`fake_r2.py`](../workmate-agent/tests/fixtures/fake_r2.py) |
| `search_meetings` | 테스트 Postgres + pgvector, Fake Embedding | `embedding_provider` 주입 |
| 보조 5종 | 임시 SQLite + 각 도메인 Fixture | |
| `assistant_ask` | LLM patch(라우팅·문장화) + 하위 Skill 준비 | [test_assistant_router.py](../workmate-agent/tests/test_assistant_router.py)의 Fake들 |

**주입 지점이 이미 있다는 점이 중요하다.** 대부분의 Workflow 빌더가 `provider_factory`·`repositories`·
`analyzer` 같은 테스트 주입 파라미터를 갖고 있어, 스냅샷 하네스가 운영 코드를 고치지 않고도 Fake를
넣을 수 있다.

## 5. 미충족 시 처리

| 조건 | 미충족 상황 | 처리 |
| --- | --- | --- |
| W1-E1 | 미커밋 변경 존재 | 주체 확인 후 커밋 또는 보류. 임의 폐기 금지 |
| W1-E2 | 테스트 실패 | **착수 금지.** 깨진 상태의 출력을 기록하면 안 된다 |
| W1-E3 | 컨테이너 미기동 | 재기동(자동 재작업 범위) |
| W1-E4 | 브랜치 없음 | 기준 Commit에서 생성 |
| W1-E5 | 옛 구현 손상 | 기준 Commit으로 복구. 복구 불가면 전환 중단 |

## 6. 후행 단계의 선행 조건에 미치는 영향

| W1 결과 | 후행 조건 | 관계 |
| --- | --- | --- |
| W1-V1 전건 PASS | [W2-E1](30-2-3-entry-criteria.md) | W2 착수 조건 |
| 동상 | [W3-E1](30-3-3-entry-criteria.md) | **W3의 가장 강한 제약** |
| 스냅샷 불가 Skill 목록 | W3-E1 예외 처리 | 기록이 있으면 진행 가능 |
| 정규화 규칙 | W3-V4 | 결정성 검증의 기준 |

## 7. 참조

- [30-0](30-0-w0-baseline.md) §10 — 기준선 확정값과 기준 Commit
- [30-1-5](30-1-5-design.md) §5 — 외부 의존 처리
- [30-3-3](30-3-3-entry-criteria.md) — W3이 W1에 거는 조건
