# W3-9 — 완료 정의와 Skill별 판정

> [30-3-w3-skill-subgraphs.md](30-3-w3-skill-subgraphs.md) §9의 상세 문서.

## 1. 완료 조건 (Exit criteria)

| # | 조건 | 판정 근거 |
| --- | --- | --- |
| E-1 | 공개 Skill 11개 전부가 `app/graph/skills/` 아래 Subgraph로 존재 | W3-V2 |
| E-2 | **W3-V1(스냅샷 대조)이 전건 PASS** — `assistant_ask`의 확인 흐름 포함 | W3-V1 |
| E-3 | W3-V3(사용자 범위)·V5(부분 실패)·V7(LLM 경계)·V11(숨은 부작용) PASS | 각 검증 |
| E-4 | 기존 `app/workflows/`가 **여전히 존재**하고 기존 테스트가 통과 | W3-V10 |
| E-5 | 부작용 노드 목록과 실패 파급 규칙표가 W8 전달용으로 확정 | 증빙 |

E-4가 완료 조건에 들어가는 것이 W3의 특징이다. **W3은 무언가를 지우는 단계가 아니다.** 옛 구현이
사라졌다면 범위를 벗어난 것이고, 비교 대상이 없어져 W4 이후를 검증할 수 없다.

## 2. Skill별 판정

W3은 Skill 단위로 완료를 판정한다. 11개가 모두 PASS여야 단계가 완료된다.

| Skill | 필수 검증 | 추가 검증 |
| --- | --- | --- |
| `rank_priorities` | V1, V2, V3, V4 | **V7**(LLM 노드 없음), V11(Snapshot 저장) |
| `get_meeting_analysis` | V1, V2, V3, V4 | — |
| `review_action_items` | V1, V2, V3, V4 | V11(승인 상태 변경) |
| `review_proposal` | V1, V2, V3, V4 | V11(제안 상태·Task 생성) |
| `manage_tasks` | V1, V2, V3, V4 | V11(CRUD), 4분기 Edge |
| `read_email` | V1, V2, V3, V4 | — |
| `daily_briefing` | V1, V2, V3, V4 | **V5, V6, V11** — 가장 많은 검증 |
| `weekly_report` | V1, V2, V3, V4 | V5, **V7** |
| `search_meetings` | V1, V2, V3, V4 | V5, V7 |
| `analyze_meeting` | V1, V2, V3, V4 | V5, V11 |
| `assistant_ask` | V1, V2, V3, V4 | **V9**(독립성), V11-4(확인 대기 중 상태 불변) |

### 2.1 Skill 단위 부분 완료

한 Skill이 FAIL이어도 다른 Skill은 계속 진행한다. 단 다음 의존을 지킨다.

```
rank_priorities FAIL     → daily_briefing 착수 불가
하위 Skill 하나라도 FAIL → assistant_ask 착수 불가
```

부분 완료 상태로 W4에 넘어갈 수 없다. Root Graph는 11개 전부를 라우팅 대상으로 갖는다.

### 2.2 전체 미완료로 판정하는 경우

Skill 하나의 문제라도 다음은 **W3 전체를 미완료**로 본다.

| 검증 | 이유 |
| --- | --- |
| W3-V3 (`user_id` 범위) | 보안 문제. 한 Skill의 누락이 다른 Skill의 같은 패턴을 의심하게 만든다 |
| W3-V11 (숨은 부작용) | 스냅샷으로 잡히지 않으므로, 하나가 틀렸다면 전수 재점검이 필요하다 |

## 3. 산출물 체크리스트

### 3.1 코드

```
[ ] app/graph/skills/rank_priorities.py
[ ] app/graph/skills/daily_briefing.py
[ ] app/graph/skills/weekly_report.py
[ ] app/graph/skills/search_meetings.py
[ ] app/graph/skills/analyze_meeting.py
[ ] app/graph/skills/assistant_router.py
[ ] app/graph/skills/assistant_skills/get_meeting_analysis.py
[ ] app/graph/skills/assistant_skills/review_action_items.py
[ ] app/graph/skills/assistant_skills/review_proposal.py
[ ] app/graph/skills/assistant_skills/manage_tasks.py
[ ] app/graph/skills/assistant_skills/read_email.py
```

### 3.2 테스트

```
[ ] tests/test_graph_skill_rank_priorities.py
[ ] tests/test_graph_skill_daily_briefing.py
[ ] tests/test_graph_skill_weekly_report.py
[ ] tests/test_graph_skill_search_meetings.py
[ ] tests/test_graph_skill_analyze_meeting.py
[ ] tests/test_graph_skill_assistant_router.py
[ ] tests/test_graph_skill_assistant_skills.py
[ ] tests/test_graph_side_effects.py          W3-V11 전용
```

### 3.3 후행 단계 전달 문서

```
[ ] 부작용 노드 목록          → W8 재시도 제외 대상
[ ] 실패 파급 규칙표(확정본)   → W8 정책 기준
[ ] Subgraph 입출력 인터페이스 → W4 합성
[ ] assistant_ask 노드 목록    → W6 교체 지점
```

### 3.4 문서·증빙

```
[ ] docs/evidence/langgraph/W3/runs/{run_id}/result.md
[ ] docs/evidence/langgraph/README.md   W3 행 갱신
[ ] HANDOFF.md
[ ] W3-R10(숨은 부작용)을 상위 계획서에 반영
```

## 4. 승인 절차

### 4.1 자동 승인 대상 여부

| 조건 | W3 해당 여부 |
| --- | --- |
| 외부 OAuth·실제 Provider 호출 | **없음** — Fake·고정 응답만 |
| 공개 Schema·데이터 모델 변경 | **없음** — W3은 응답 모양을 바꾸지 않는다 |
| UI 육안 검수 | **없음** |
| 모델 평가 | **없음** |
| 원격 Push | **없음** |

→ **W3은 자동 승인 대상이다.** 검증이 전부 PASS면 승인 후 W4를 착수한다.

### 4.2 자동 승인이 불가한 경우

| 상황 | 처리 |
| --- | --- |
| 스냅샷 차이가 "의도적 변경"으로 판정됨 | **자동 승인 불가.** W3에서 의도적 변경은 원칙적으로 없어야 한다. 사용자에게 보고하고 판단을 받는다 |
| W3-V3(보안) FAIL | 자동 재작업 후 재검수. 해소 전 W4 착수 금지 |
| W3-V11 FAIL | 부작용 방침(W3-D1) 재확인 필요 시 사용자 보고 |
| 범위 밖 모듈 수정이 필요해짐 | 범위 확대. 사용자 확인 |

### 4.3 자동 승인 시 기록

```
latest_run_id:          {run_id}
latest_run_status:      PASS
latest_approved_run_id: {run_id}
approved_at:            {날짜} Asia/Seoul
reviewer:               자동 승인(검증 명령)
자동 재작업 착수:        예/아니오
자동 진행 판정:          진행 — W4 자동 착수
Skill별 판정:            11개 전부 PASS
```

## 5. 완료 후 상태

| 항목 | W3 완료 시점 |
| --- | --- |
| 운영 경로 | **여전히 `WorkflowRegistry`** |
| `app/graph/skills/` | Subgraph 11개, 테스트에서만 실행 |
| `app/workflows/` | **그대로 존재** |
| 공개 계약 | 변경 없음 |
| 확인 흐름 | 현재 방식(`pending_action`) 유지 |
| 롤백 비용 | 낮음 — 신규 파일 삭제 |

## 6. 완료 판정 체크리스트

```
[ ] 1. Skill 11개 각각 W3-V1~V4 결과 기록
[ ] 2. daily_briefing의 V5·V6·V11 결과 기록
[ ] 3. W3-V7 LLM 경계 (rank_priorities·weekly_report·search_meetings)
[ ] 4. W3-V9 Subgraph 독립성 grep 결과
[ ] 5. W3-V8 Mock 부재
[ ] 6. W3-V10 전체 회귀 (Postgres 포함, SKIP 0)
[ ] 7. 부작용 노드 목록 확정
[ ] 8. 실패 파급 규칙표 확정
[ ] 9. git diff --check, Secret 검사
[ ] 10. Docstring 한글 여부 검토
[ ] 11. result.md 작성, 스냅샷 차이 내역 기록
[ ] 12. 자동 승인 판정 후 W4 착수
```

## 7. 참조

- [30-3-7](30-3-7-verification.md) — 검증 항목 정의
- [30-3-11](30-3-11-rollback.md) — 완료하지 못했을 때
- [`AGENTS.md`](../AGENTS.md) — 완료 규칙, 자동 승인 규칙
