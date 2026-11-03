# W8-5 — 설계

> [30-8-w8-retry-observability.md](30-8-w8-retry-observability.md) §5의 상세 문서.

## 1. 재시도 경계 — 3계층

[96번 §8](96-workmate-langgraph-target-architecture.md)이 정의하는 계층을 혼동하지 않는 것이 요점이다.

| 계층 | 주체 | 재시도 대상 | 멱등성 근거 | W8에서 |
| --- | --- | --- | --- | --- |
| HTTP 요청 전체 | Orchestrator | 요청 실패 | 같은 `message_id` | **건드리지 않는다** |
| 노드 | LangGraph `RetryPolicy` | 노드 내 Provider 호출 | 노드 재실행이 안전 | **여기를 정리한다** |
| Provider Client | 없음 | — | — | **없음을 확인한다** |

### 1.1 1계층이 성립하는 이유

W4-D1(멱등성 구현)이 이를 가능하게 했다. Orchestrator가 같은 `message_id`로 재시도하면 Graph가
기존 결과를 복원한다.

**W8 이전에는 1계층이 작동하지 않았다** — 중복 요청이 재실행됐다.

### 1.2 3계층에 재시도를 두지 않는 이유

Provider Client(`GmailAdapter` 등)에 재시도를 넣으면

| 문제 | 설명 |
| --- | --- |
| 계층 중복 | 노드 재시도 3회 × 클라이언트 재시도 3회 = 9회 |
| 관측 불가 | Graph가 재시도를 모른다 |
| 정책 분산 | 클라이언트마다 다른 정책 |

**W8-T1에서 Provider Client에 재시도가 있는지 확인**하고, 있으면 제거를 검토한다.

---

## 2. 오류 분류

### 2.1 분류표

| 부류 | 예 | 처리 |
| --- | --- | --- |
| **네트워크** | DNS 실패(`socket.gaierror`), 연결 끊김(`URLError`), Timeout, 응답 파싱 실패(`JSONDecodeError`) | **재시도** |
| **HTTP 4xx** | 400, 404 | 즉시 실패 |
| **HTTP 401·403** | 인증 실패 | 즉시 실패. `AUTH_REQUIRED` 후보(§5) |
| **HTTP 5xx** | 500, 502, 503 | 즉시 실패(`NETWORK_ONLY_RETRY` 기준) |
| **HTTP 429** | rate limit | 즉시 실패(현재 동작 유지) |
| **취소** | 취소 감지 | `CANCELED` |

### 2.2 429에 대한 주의

일반적으로 429는 재시도 대상이다. 그러나 **현재 구현이 재시도하지 않으므로 바꾸지 않는다.**

```python
# assistant_router.py:300-305 — HTTPError를 재시도하지 않는다
except error.HTTPError as exc:
    ...  # 즉시 실패
except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
    ...  # 재시도
```

`429`도 `HTTPError`이므로 즉시 실패한다.

**개선이 바람직하더라도 동작 변경이다.** [30-8-2](30-8-2-scope.md) §3에 따라 W9 후속 백로그로 기록한다.

### 2.3 `weekly_report` 계열은 다르다

[weekly_report.py:55-80](../workmate-agent/app/workflows/weekly_report.py#L55)의
`_call_llm_with_retry`는 `LLMProviderError`를 재시도하는데, Docstring이 그 범위를 설명한다.

> timeout·429·5xx와 Schema 오류는 Provider Adapter에서 `LLMProviderError`로 정규화된다. 첫 실패 뒤
> 짧게 대기하고 한 번만 재호출하며, 두 번째 실패는 Workflow가 원장 기반 부분 결과와 warning으로
> 변환하도록 다시 발생시킨다.

즉 **429·5xx를 재시도한다.** `assistant_router`와 정반대다.

---

## 3. 정책 2종

### 3.1 정의 (W2 산출물)

```python
# app/graph/llm.py

def is_network_error(exc: BaseException) -> bool:
    """재시도 가능한 네트워크 계층 오류인지 판정한다.

    HTTP 응답을 받은 오류(4xx/5xx)는 재시도해도 같은 결과이므로 제외한다 —
    2026-08-19 Windows 환경 DNS 간헐 실패 대응에서 확정한 구분이다.
    """


NETWORK_ONLY_RETRY = RetryPolicy(max_attempts=3, retry_on=is_network_error)
PROVIDER_ERROR_RETRY = RetryPolicy(max_attempts=2, retry_on=is_provider_error)
```

### 3.2 적용 대상

| 정책 | 적용 노드 | 근거 |
| --- | --- | --- |
| `NETWORK_ONLY_RETRY` | `assistant_router`의 LLM 노드(`route_with_llm`, `phrase_answer`) | 원래 `_chat_completion`의 정책 |
| `PROVIDER_ERROR_RETRY` | `weekly_report`의 `generate_summary_llm` | 원래 `_call_llm_with_retry`의 정책 |
| (없음) | 그 외 LLM 노드 | 원래 재시도가 없었다 |
| (없음) | **부작용 노드 전부** | W8-R9 |

### 3.3 원래 재시도가 없던 지점

| 지점 | 현재 | W8에서 |
| --- | --- | --- |
| `meeting_answer._summarize_with_llm` | 재시도 없음. 실패 시 근거 나열 폴백 | **그대로** |
| `meeting_analysis` LLM 호출 | W8-T1에서 조사 | 조사 결과에 따름 |
| Gmail·Calendar 호출 | 재시도 없음 | **그대로** |

**재시도가 없던 곳에 새로 추가하지 않는다.** 그것도 동작 변경이다.

### 3.4 설계 결정 W8-D1 — 정책을 통일하지 않는다

| | 방식 | 평가 |
| --- | --- | --- |
| a | 하나로 통일 | 동작 변경. 스냅샷 부분 실패 케이스가 깨진다 |
| **b** | **지점별 동작 보존** | **채택** |

통일이 바람직하더라도 이번 범위가 아니다. W9 후속 백로그.

---

## 4. 부작용 노드 제외 (W8-R9)

### 4.1 재시도의 전제

노드 재시도가 안전하려면 **재실행해도 결과가 같아야 한다**(멱등).

| 노드 유형 | 재실행 | 재시도 |
| --- | --- | --- |
| 조회 | 안전 | ✓ |
| 계산 | 안전 | ✓ |
| LLM 호출 | 안전(결과가 달라질 수 있지만 부작용 없음) | ✓ |
| **쓰기** | **중복 처리** | **✗** |

### 4.2 제외 목록

[30-3-5](30-3-5-design.md) §3.4에서 작성하고 W7에서 확정.

| Skill | 제외 노드 | 중복 시 일어나는 일 |
| --- | --- | --- |
| `rank_priorities` | `save_snapshot` | Snapshot 중복 저장 |
| `daily_briefing` | `rank_priorities_subgraph` | 동상(간접) |
| `analyze_meeting` | `save_final_transcript` | transcript 중복 |
| | `save_analysis` | 분석·Action Item 후보 중복 |
| | `heal_meeting_title` | 제목 중복 수정(무해하지만 불필요) |
| | `index_chunks` | 색인 중복 |
| `review_action_items` | `call_domain_api` | **승인 중복 처리** |
| `review_proposal` | `call_domain_api` | **제안 중복 처리, Task 중복 생성** |
| `manage_tasks` | `create/update/delete_task` | **Task 중복 생성·삭제** |

### 4.3 적용표를 명시적으로 만든다

```python
# app/graph/skills/rank_priorities.py
graph.add_node("load_user_tasks", load_user_tasks, retry=NETWORK_ONLY_RETRY)
graph.add_node("save_snapshot", save_snapshot)   # 부작용 — 재시도 금지(W8-R9)
```

**주석으로 이유를 남긴다.** 나중에 "왜 여기만 재시도가 없지?"라는 질문에 답한다.

### 4.4 조회 노드는 재시도해도 되나

조회도 Provider 호출이면 네트워크 오류가 날 수 있다. 재시도가 유용하다.

단 **DB 조회에는 재시도를 붙이지 않는다** — DB 오류는 대개 재시도로 해결되지 않고, 연결 문제라면
더 큰 장애다.

---

## 5. 인증 오류와 `AUTH_REQUIRED` (W8-R5)

### 5.1 96번의 설계

[96번 §8](96-workmate-langgraph-target-architecture.md)은 `AUTH 오류 → AUTH_REQUIRED + interrupt`를
그린다. [96번 §7](96-workmate-langgraph-target-architecture.md)의 상태 전이도에도
`WORKING → AUTH_REQUIRED → WORKING`이 있다.

### 5.2 현재 상태 조사 필요

| 확인 | W8-T1에서 |
| --- | --- |
| `AUTH_REQUIRED` 상태가 현재 쓰이는가 | grep |
| Google Provider 재인증이 어떻게 처리되는가 | [google_auth.py](../workmate-agent/app/providers/google_auth.py) 확인 |
| 401·403이 지금 어떻게 되는가 | 조사 |

### 5.3 설계 결정 W8-D2 — 도입 여부를 W8-T1에서 판단

`AUTH_REQUIRED`는 `INPUT_REQUIRED`(W6)와 같은 성격의 **신규 Task 상태**다. 도입하면 계약 영향이
있고 UI도 처리해야 한다.

| 판단 | 처리 |
| --- | --- |
| 현재 인증 오류가 명확히 구분되고 있다 | 분류만 정리. 상태 도입은 후속 |
| 구분이 안 되고 있다 | **W8 범위에서 분류까지만.** 상태 도입은 후속 백로그 |

**W8에서 새 Task 상태를 도입하지 않는 것을 기본으로 한다.** W6에서 이미 계약을 바꿨고, 또 바꾸면
W9의 "의도적 변경" 목록이 커진다.

---

## 6. 실패 파급 규칙

[30-3-5](30-3-5-design.md) §7의 표를 그대로 유지한다. W8이 바꾸지 않는다.

| Skill | 핵심(전체 실패) | 보조(경고 후 진행) | 조용히 무시 |
| --- | --- | --- | --- |
| `daily_briefing` | Task 저장소 | Gmail, Calendar | 메일 본문 보강, LLM 관련성 판정 |
| `weekly_report` | Task·근거 조회 | LLM 요약, 근거 없는 계획 후보 | — |
| `analyze_meeting` | 회의 조회, STT, 분석, 근거 검증 | 색인 | — |
| `search_meetings` | 검색, 회의 날짜 누락 | LLM 답변 | — |

### 6.1 재시도와의 관계

```
Provider 호출 실패
  → RetryPolicy가 재시도 (네트워크 오류인 경우)
  → 소진
  → 실패 파급 규칙 적용
      ├ 핵심 소스 → FAILED
      └ 보조 소스 → warnings + 계속
```

재시도는 **실패 파급 이전 단계**다. 재시도가 성공하면 파급 규칙이 발동하지 않는다.

---

## 7. 관측 설계

### 7.1 로그 항목

```python
{"node": "fetch_gmail",
 "thread_id": "task-abc",
 "task_id": "task-abc",
 "user_id": "00000000-...",
 "skill_id": "daily_briefing",
 "elapsed_ms": 412,
 "status": "warning",            # ok | warning | error
 "warning_code": "GOOGLE_PROVIDER_UNAVAILABLE",
 "retry_count": 1}
```

### 7.2 남기지 않는 것

| 항목 | 이유 |
| --- | --- |
| 메일 본문·Snippet | 개인정보 |
| 회의 녹취·요약 | 동상 |
| LLM 프롬프트·응답 전문 | 개인정보 포함 가능 |
| Token·API Key | `AGENTS.md` 금지 |
| Presigned URL | 동상 |

### 7.3 구현 방식

**표준 `logging`을 쓴다.** 외부 서비스(LangSmith 등)는 범위 밖이다.

```python
# app/graph/observability.py
def log_node_execution(node: str, state: WorkmateState, *,
                       elapsed_ms: int, status: str, ...) -> None:
    """노드 실행 결과를 구조화 로그로 남긴다.

    Secret·개인정보는 남기지 않는다(AGENTS.md). user_id는 OIDC subject이며
    장애 조사에 필요하므로 포함한다.
    """
```

### 7.4 노드마다 수동으로 호출하지 않는다

11개 Skill의 모든 노드에 로그 호출을 넣으면 누락이 생긴다. **래퍼나 콜백**으로 일괄 적용한다.

LangGraph가 제공하는 방법(콜백·미들웨어)을 W8-T1에서 확인한다. 없으면 노드 등록 시 감싸는 함수를
만든다.

---

## 8. 설계 결정 요약

| ID | 결정 | 근거 |
| --- | --- | --- |
| W8-D1 | 두 재시도 정책을 통일하지 않고 각각 보존 | §3.4 |
| W8-D2 | `AUTH_REQUIRED` 상태 도입은 W8-T1에서 판단, 기본은 미도입 | §5.3 |
| W8-D3 | 재시도가 없던 지점에 새로 추가하지 않는다 | §3.3 |
| W8-D4 | 부작용 노드에 재시도 금지, 주석으로 이유 명시 | §4.3 |
| W8-D5 | 로그는 래퍼·콜백으로 일괄 적용 | §7.4 |
| W8-D6 | 429 재시도 정책을 바꾸지 않는다 | §2.2 |

## 9. 참조

- [96번 §8](96-workmate-langgraph-target-architecture.md) — 오류·재시도 Graph
- [30-2-5](30-2-5-design.md) §5.2 — 정책 불일치 조사
- [30-3-5](30-3-5-design.md) §3.4, §7 — 부작용 노드, 실패 파급
