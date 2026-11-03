# W3-3 — 선행 조건

> [30-3-w3-skill-subgraphs.md](30-3-w3-skill-subgraphs.md) §3의 상세 문서.

## 1. 선행 조건 목록

| ID | 조건 | 출처 | 확인 방법 | 미충족 시 |
| --- | --- | --- | --- | --- |
| W3-E1 | W1 스냅샷 전건 PASS | [30-1](30-1-w1-contract-snapshot.md) §9 | `uv run python -m unittest tests.contracts.test_contract_snapshots -v` | **착수 금지** |
| W3-E2 | W2 검증 V1~V5, V8, V9 PASS | [30-2-7](30-2-7-verification.md) | W2 증빙 | 착수 금지 |
| W3-E3 | **W2-V6(LLM 구조화 출력 동등성) PASS** | [30-2-7](30-2-7-verification.md) | W2 증빙 | **LLM 의존 Skill만 착수 금지**(§3) |
| W3-E4 | Skill 간 직접 import 처리 방침 확정 | [30-3-5](30-3-5-design.md) §3·§4 | 설계 확정 기록 | W3-T0으로 복귀 |
| W3-E5 | 테스트용 PostgreSQL 기동 | [30-0](30-0-w0-baseline.md) §10.1 | `docker ps` | 컨테이너 재기동 |

## 2. 각 조건의 근거

### 2.1 W3-E1 — 스냅샷이 없으면 W3은 검증 불가

W3의 수용 기준은 "새 Subgraph가 옛 구현과 같은 값을 낸다"이다. 스냅샷이 없으면 비교 대상이 없고,
새로 쓴 테스트는 새로 쓴 구현에 맞춰 작성되므로 둘 다 틀려도 통과한다.

이것이 [계획서 §1-4](30-langgraph-migration-plan.md)의 "W1 없이 W3을 시작하지 않는다"의 이유다.
W3-E1은 전 단계 선행 조건 중 가장 강한 제약이다.

### 2.2 W3-E2 — 기반이 확정돼야 11번 재작업을 피한다

W3에서 State 스키마나 어댑터 계약이 바뀌면 이미 만든 Subgraph를 전부 수정해야 한다. Skill이 11개이므로
손실이 최대 11배가 된다([30-3-10](30-3-10-risks.md) W3-K5).

W2-V6을 제외한 이유는 §3에서 설명한다.

### 2.3 W3-E3 — LLM 동등성은 일부 Skill에만 영향

W2-V6(구조화 출력 동등성)이 실패해도 LLM을 쓰지 않는 Skill은 진행할 수 있다. 전면 차단은 과하다.

| LLM 의존 여부 | Skill | W2-V6 실패 시 |
| --- | --- | --- |
| **의존** | `weekly_report`, `analyze_meeting`, `search_meetings`, `assistant_ask` | 착수 금지 |
| **의존**(간접) | `daily_briefing` — `classify_work_related_emails()` 호출 | 조건부(§3.1) |
| 비의존 | `rank_priorities`, `get_meeting_analysis`, `review_action_items`, `review_proposal`, `manage_tasks`, `read_email` | 진행 가능 |

### 2.4 W3-E4 — Skill 간 직접 호출 방침

현재 코드에는 Skill이 Skill을 부르는 경로가 두 개 있다.

| 호출 | 위치 | 성격 |
| --- | --- | --- |
| `assistant_ask` → 나머지 10개 | [assistant_router.py:881-891](../workmate-agent/app/workflows/assistant_router.py#L881-L891) | Meta Skill의 본질적 동작 |
| `daily_briefing` → `rank_priorities` | [daily_briefing.py:139, 238](../workmate-agent/app/workflows/daily_briefing.py#L139) | **숨은 부작용 포함** |

두 번째는 단순 호출이 아니다. `rank_priorities`는 실행 시 `snapshot_repository.save_all()`로 우선순위
Snapshot을 **저장**한다([priority.py:123](../workmate-agent/app/workflows/priority.py#L123)). 즉
`daily_briefing`을 부르면 우선순위 Snapshot이 기록된다. 이 부작용을 유지할지 말지는 결과 값에 직접
드러나지 않으므로 스냅샷으로 잡히지 않는다.

착수 전에 [30-3-5](30-3-5-design.md) §3의 설계 결정 W3-D1을 확정한다.

### 2.5 W3-E5 — PostgreSQL

`search_meetings`·`analyze_meeting`은 pgvector 하이브리드 검색과 색인을 쓴다. SQLite만으로는 이 경로를
검증할 수 없다.

## 3. 부분 착수 규칙

W2-V6만 미충족인 경우 아래 순서로 진행할 수 있다.

```
1차(진행 가능):  rank_priorities → get_meeting_analysis → review_action_items
                 → review_proposal → manage_tasks → read_email
2차(W2-V6 해소 후): daily_briefing → weekly_report → search_meetings
                    → analyze_meeting → assistant_ask
```

### 3.1 `daily_briefing`의 조건부 판정

`daily_briefing`은 자체 LLM 호출은 없지만 [`classify_work_related_emails()`](../workmate-agent/app/email_action_items.py)를
호출해 업무 무관 메일을 걸러낸다. 이 모듈은 [30-2-5](30-2-5-design.md) §5.3의 결정에 따라 **LLM 경로를
교체하지 않고 기존 함수를 그대로 호출**한다.

따라서 `daily_briefing`은 W2-V6과 무관하게 진행할 수 있다. 다만 `rank_priorities`를 내부 호출하므로
그쪽이 먼저 끝나야 한다.

### 3.2 부분 착수 시 기록 의무

부분 착수한 경우 증빙에 다음을 남긴다.

```
착수 범위:      Skill 6개 (1차)
보류 범위:      Skill 5개 (2차)
보류 사유:      W2-V6 미충족
재개 조건:      W2-V6 PASS
```

## 4. 착수 전 확인 명령

```bash
cd workmate-agent

# W3-E1, W3-E2
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v

# W3-E1 (스냅샷만)
uv run python -m unittest tests.contracts.test_contract_snapshots -v

# W3-E5
docker ps --filter name=workmate-test-pg --format "{{.Status}}"

# W2 산출물 존재 확인
ls app/graph/state.py app/graph/adapter.py app/graph/checkpointer.py app/graph/llm.py
```

## 5. Skill별 선행 조건

일부 Skill은 추가 선행 조건이 있다.

| Skill | 추가 선행 조건 | 이유 |
| --- | --- | --- |
| `daily_briefing` | `rank_priorities` Subgraph 완료 | 내부 호출([30-3-5](30-3-5-design.md) §3) |
| `assistant_ask` | 나머지 10개 Subgraph 완료 | Meta Skill |
| `search_meetings` | 테스트 Postgres + pgvector | 하이브리드 검색 |
| `analyze_meeting` | 테스트 Postgres, Fake STT·R2 | 색인·저장 |
| `weekly_report` | W2-V6 | LLM 요약 |

## 6. 후행 단계에 미치는 영향

| W3 결과 | W4 선행 조건 | 관계 |
| --- | --- | --- |
| Subgraph 11개 존재 | W4-E1 | 합성 대상 |
| W3-V1 스냅샷 PASS | W4-E2 | Root 경유 재대조의 기준선 |
| W3-V9 Skill 간 import 없음 | W4-E3 | 순환 의존 없이 합성 가능 |

## 7. 참조

- [30-1](30-1-w1-contract-snapshot.md) §9 — 스냅샷 완료 정의
- [30-2-7](30-2-7-verification.md) — W2 검증 항목
- [30-3-5](30-3-5-design.md) §3 — Skill 간 호출과 숨은 부작용
