# W8-3 — 선행 조건

> [30-8-w8-retry-observability.md](30-8-w8-retry-observability.md) §3의 상세 문서.

## 1. 선행 조건 목록

| ID | 조건 | 출처 | 확인 방법 | 미충족 시 |
| --- | --- | --- | --- | --- |
| W8-E1 | W7 완료 — 실행 경로가 하나 | [30-7-9](30-7-9-exit-criteria.md) | `grep -rn "WorkflowRegistry" app/` | 착수 금지 |
| W8-E2 | **W2-V7(재시도 정책 정의) PASS** | [30-2-7](30-2-7-verification.md) | W2 증빙 | 적용할 정책이 없음 |
| W8-E3 | **부작용 노드 목록 확보** | [30-3-5](30-3-5-design.md) §3.4, W7-T12 | 목록 확인 | 재시도 제외 대상 불명 |
| W8-E4 | 실패 파급 규칙표 확보 | [30-3-5](30-3-5-design.md) §7 | 동상 | 검증 기준 없음 |
| W8-E5 | 스냅샷 27건 PASS | [30-7-7](30-7-7-verification.md) | 대조 | 기준선 없음 |
| W8-E6 | W5-V5(오류 매핑) PASS | [30-5-7](30-5-7-verification.md) | W5 증빙 | 재시도 후 예외 전파 확인 불가 |

## 2. 각 조건의 근거

### 2.1 W8-E2 — W2가 정의한 것을 적용한다

W8은 **정책을 새로 만들지 않는다.** W2에서 정의한 것을 노드에 붙인다.

| W2 산출물 | W8에서의 쓰임 |
| --- | --- |
| `is_network_error()` | 오류 분류 |
| `NETWORK_ONLY_RETRY` (3회) | `assistant_router` 계열 노드 |
| `PROVIDER_ERROR_RETRY` (2회) | `weekly_report` 계열 노드 |
| `max_retries=0` 설정 | 라이브러리 중복 재시도 방지 |

W2-V7이 FAIL이면 붙일 정책이 없거나 잘못된 정책을 붙이게 된다.

### 2.2 W8-E3 — 부작용 노드 목록이 핵심

**재시도를 붙이면 안 되는 노드 목록**이다. 이것 없이 정책을 적용하면 Task가 중복 생성되거나 승인이
중복 처리된다.

[30-3-5](30-3-5-design.md) §3.4에서 작성하고 W7에서 확정한 목록.

| Skill | 부작용 노드 |
| --- | --- |
| `rank_priorities` | `save_snapshot` |
| `daily_briefing` | (간접) `rank_priorities_subgraph` |
| `analyze_meeting` | `save_final_transcript`, `save_analysis`, `heal_meeting_title`, `index_chunks` |
| `review_action_items` | `call_domain_api` |
| `review_proposal` | `call_domain_api` |
| `manage_tasks` | `create/update/delete_task` |

**목록이 없거나 불완전하면 W8을 시작하지 않는다.**

### 2.3 W8-E4 — 실패 파급 규칙표

재시도 소진 후 어떻게 되는지의 기준이다.

| Skill | 핵심(전체 실패) | 보조(경고 후 진행) |
| --- | --- | --- |
| `daily_briefing` | Task 저장소 | Gmail, Calendar |
| `weekly_report` | Task·근거 조회 | LLM 요약 |
| `analyze_meeting` | 회의 조회, STT, 분석, 근거 검증 | 색인 |
| `search_meetings` | 검색, 회의 날짜 누락 | LLM 답변 |

W8-V4·V5가 이 표를 검증한다.

### 2.4 W8-E6 — 오류 매핑

`RetryPolicy`를 붙이면 **재시도 소진 시 어떤 예외가 나오는지**가 달라질 수 있다. LangGraph가 원
예외를 유지하는지, 자체 예외로 감싸는지 확인해야 한다.

W5에서 매핑이 확인돼 있어야 "W8이 깨뜨렸다"를 판정할 수 있다.

```
W5: ValueError → 422 확인
W8: RetryPolicy 적용 후에도 ValueError → 422인가?
```

## 3. 착수 전 확인 명령

```bash
cd workmate-agent

# W8-E1
grep -rn "WorkflowRegistry\|from app.workflows" app/    # 출력 없음
ls app/workflows/                                        # 존재하지 않음

# W8-E2
grep -n "NETWORK_ONLY_RETRY\|PROVIDER_ERROR_RETRY\|is_network_error" app/graph/llm.py

# 현재 노드 내부 재시도 루프 조사 (W8의 제거 대상)
grep -rn "for attempt in range\|max_attempts\|retry" app/graph/

# W8-E5, E6
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

## 4. 조사 항목 — 노드 내부 재시도 루프

W3에서 Skill을 옮길 때 기존 재시도를 그대로 보존했다. W8에서 이를 `RetryPolicy`로 옮긴다.

**착수 전에 어디에 무엇이 있는지 파악한다.**

| 원래 위치 | 내용 | W3 이후 위치 |
| --- | --- | --- |
| `assistant_router._chat_completion` | 3회, 네트워크만 | `skills/assistant_router.py`의 LLM 노드 |
| `weekly_report._call_llm_with_retry` | 2회, Provider 오류 | `skills/weekly_report.py`의 LLM 노드 |
| (기타) | W8-T1에서 조사 | |

## 5. 환경 전제

| 항목 | 이유 |
| --- | --- |
| 오류 주입 가능 | 재시도 검증에 필수 |
| 호출 횟수 계측 가능 | `Mock.call_count` |
| 테스트 PostgreSQL | 통합 경로 |

### 5.1 오류 주입 설계

W8의 검증은 대부분 오류를 일부러 만들어야 한다.

| 오류 | 주입 방법 |
| --- | --- |
| 네트워크(DNS 실패) | `socket.gaierror` 또는 `URLError` |
| Timeout | `TimeoutError` |
| HTTP 500 | Fake 응답 |
| HTTP 429 | 동상 |
| 인증 오류 | 401 응답 |

**실제 외부 호출은 하지 않는다.** W1·W2와 같은 원칙이다.

## 6. 미충족 시 처리

| 조건 | 미충족 상황 | 처리 |
| --- | --- | --- |
| W8-E1 | 레거시 잔존 | W7로 복귀 |
| W8-E2 | 정책 미정의 | W2로 복귀 |
| W8-E3 | 목록 없음 | **W3·W7의 산출물 확인.** 없으면 재작성 |
| W8-E4 | 규칙표 없음 | 동상 |
| W8-E5 | 스냅샷 차이 | W7에서 해소 |
| W8-E6 | 오류 매핑 미확인 | W5로 복귀 |

## 7. 후행 단계의 선행 조건에 미치는 영향

| W8 결과 | W9 선행 조건 | 관계 |
| --- | --- | --- |
| W8-V2(HTTP 비재시도) PASS | [계획서 §9-6](30-langgraph-migration-plan.md) | **완료 기준 중 하나** |
| 스냅샷 27건 PASS | W9의 diff 분류 | |
| 정책 통일 미실시 기록 | W9 후속 백로그 | |

## 8. 참조

- [30-2-7](30-2-7-verification.md) — W2-V7 재시도 정책 검증
- [30-3-5](30-3-5-design.md) §3.4, §7 — 부작용 노드 목록, 실패 파급 규칙표
- [30-8-5](30-8-5-design.md) — 적용 설계
