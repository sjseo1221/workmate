# W3-5 — 설계

> [30-3-w3-skill-subgraphs.md](30-3-w3-skill-subgraphs.md) §5의 상세 문서.

## 1. 이식 순서

의존이 적고 결정적인 것부터, 복잡하고 의존이 많은 것을 뒤로 둔다.

| 순서 | Skill | 현재 위치 | 난이도 근거 |
| --- | --- | --- | --- |
| 1 | `rank_priorities` | [priority.py](../workmate-agent/app/workflows/priority.py) 161줄 | LLM 없음, 결정적 계산 |
| 2 | `get_meeting_analysis` | [assistant_skills.py:174](../workmate-agent/app/workflows/assistant_skills.py#L174) | 단순 조회, 얇은 래퍼 |
| 3 | `review_action_items` | [:199](../workmate-agent/app/workflows/assistant_skills.py#L199) | 얇은 래퍼, 확인 대상 |
| 4 | `review_proposal` | [:226](../workmate-agent/app/workflows/assistant_skills.py#L226) | 얇은 래퍼, 확인 대상 |
| 5 | `manage_tasks` | [:293](../workmate-agent/app/workflows/assistant_skills.py#L293) | 4분기 CRUD, 삭제는 확인 대상 |
| 6 | `read_email` | [:63](../workmate-agent/app/workflows/assistant_skills.py#L63) | Gmail 실시간 호출 |
| 7 | `daily_briefing` | [daily_briefing.py](../workmate-agent/app/workflows/daily_briefing.py) 368줄 | 병렬 + 3중 부분 실패 + 숨은 부작용 |
| 8 | `weekly_report` | [weekly_report.py](../workmate-agent/app/workflows/weekly_report.py) 368줄 | LLM + 근거 검증 + 부분 결과 |
| 9 | `search_meetings` | [meetings.py:377](../workmate-agent/app/workflows/meetings.py#L377) | 하이브리드 검색 + 근거 판정 |
| 10 | `analyze_meeting` | [meetings.py:216](../workmate-agent/app/workflows/meetings.py#L216) | STT + LLM + 색인, 실패 격리 |
| 11 | `assistant_ask` | [assistant_router.py:771](../workmate-agent/app/workflows/assistant_router.py#L771) 937줄 | 나머지 10개 호출 |

`daily_briefing`(7)이 `rank_priorities`(1)에 의존하고, `assistant_ask`(11)가 전부에 의존한다.

---

## 2. Skill별 노드 분해

### 2.1 `rank_priorities` — 결정적 계산의 표준

현재 [`execute()`](../workmate-agent/app/workflows/priority.py#L95)는 한 함수에서 조회 → 계산 → 비교 →
저장 → 조립을 수행한다.

```
START → load_previous_snapshot   snapshot_repository.latest(user_id, limit=3)
      → load_user_tasks          task_repository.list(user_id)          [user_id 범위]
      → calculate_scores         rank_tasks() Domain 호출, top_n=3      [LLM 금지]
      → build_snapshots          PrioritySnapshotRecord 생성, calculated_at 확정
      → save_snapshot            snapshot_repository.save_all()         [부작용]
      → explain_rank_changes     _changes(previous, snapshots)
      → build_result             data·text 조립
      → END
```

| 설계 포인트 | 내용 |
| --- | --- |
| `load_previous_snapshot`을 먼저 | 저장 전에 읽어야 변화 비교가 성립한다. 순서를 바꾸면 항상 `unchanged`가 된다 |
| `calculated_at` | `datetime.now(timezone.utc)` — **비결정 값**. W1 정규화 대상 |
| `save_snapshot` 부작용 | W8에서 재시도를 붙이면 안 되는 노드(중복 저장) |
| 점수 계산 | [`rank_tasks()`](../workmate-agent/app/domain/priority.py) 호출만. 재구현 금지(W3-R4) |

### 2.2 보조 Skill 5종 — 얇은 래퍼

**중요한 사실:** 이 5개는 업무 로직을 갖지 않는다. UI REST 모듈의 함수를 그대로 호출하는 어댑터다.

| Skill | 호출 대상 | 모듈 범위 |
| --- | --- | --- |
| `review_action_items` | `app.action_item_api.review_actions()` | **W3 범위 밖** |
| `review_proposal` | `app.proposal_api._review()` | 범위 밖 |
| `manage_tasks` | `app.task_api.{list,create,update,delete}_task()` | 범위 밖 |
| `get_meeting_analysis` | 회의 분석 조회 | 범위 밖 |
| `read_email` | Gmail Adapter | 범위 밖 |

따라서 노드 분해는 **최소**로 한다.

```
START → validate_input      필수 필드 확인, ValueError로 422 매핑
      → call_domain_api     기존 REST 함수 호출 (user_id 전달)
      → build_result        text·data·markdown 조립
      → END
```

**설계 결정 W3-D4 — 얇은 래퍼를 더 쪼개지 않는다.**

쪼갤 만한 로직이 없다. 억지로 4~5개 노드를 만들면 Checkpoint I/O만 늘고 얻는 것이 없다
([30-3-2](30-3-2-scope.md) §1.2의 과분해 경계). 다만 `manage_tasks`는 예외다.

**`manage_tasks`의 분기**

```
START → validate_input → route_action ─┬─(list)→   list_tasks   ─┐
                                       ├─(create)→ create_task  ─┤
                                       ├─(update)→ update_task  ─┼→ build_result → END
                                       └─(delete)→ delete_task  ─┘
```

`action` 값에 따른 조건부 Edge를 쓴다. 네 분기의 결과 모양이 서로 다르므로 `build_result`를 공유할지
분기별로 둘지는 구현 시 결정한다. `delete`는 확인 대상이다(§6).

### 2.3 `daily_briefing` — 3중 부분 실패 구조

현재 구현은 **세 층의 실패 정책**을 갖는다. 노드 분해에서 이 구분을 잃으면 안 된다.

| 층 | 대상 | 실패 시 |
| --- | --- | --- |
| 1 | Gmail `list_messages` | `warnings`에 `GOOGLE_PROVIDER_UNAVAILABLE` 추가, 메일 신호 없이 진행 |
| 2 | 메일 본문 보강(`get_message` 병렬) | **조용히 무시.** `warnings`도 남기지 않고 자리표시자로 폴백 |
| 3 | LLM 관련성 판정 | `relevance = {}` → **모든 메일을 통과**시킴(숨기지 않음) |

근거: [daily_briefing.py:195-235](../workmate-agent/app/workflows/daily_briefing.py#L195)의 주석 3개.
각각 2026-08-16·2026-08-17 실사용 중 발견된 문제의 대응이다.

**목표 구조**

```
START → calculate_date_range   as_of·timezone → local_day, start, end
      ├→ fetch_gmail           ─→ enrich_message_details  ─→ classify_work_related
      ├→ fetch_calendar
      └→ load_user_tasks
                    ↓ (팬인)
      → rank_priorities_subgraph        §3의 W3-D1 결정에 따름
      → match_registered_tasks          source_type/source_id 대조
      → normalize_and_build             event_items·important_signals·source_refs
      → render_markdown
      → build_result → END
```

| 설계 포인트 | 내용 |
| --- | --- |
| 팬아웃 3갈래 | Gmail·Calendar·Task는 서로 의존하지 않는다 |
| 메일 파이프라인은 직렬 | `fetch_gmail → enrich → classify`는 앞 결과에 의존하므로 팬아웃 대상이 아니다 |
| `enrich_message_details` | 내부 병렬(`asyncio.gather`)을 유지. 개별 실패는 조용히 무시 |
| `classify_work_related` | 실패 시 전부 통과. [30-2-5](30-2-5-design.md) §5.3에 따라 기존 함수 그대로 호출 |
| `match_registered_tasks` | `(source_type, source_id)` → `task_id` 매핑. Calendar는 `{calendar_id}:{event_id}`, Gmail은 `message.id` |
| `summary` 문자열 | LLM이 아니라 고정 템플릿 — "오늘 일정 N건, 메일 신호 N건, 우선순위 N건입니다." |
| `markdown` | [`_render_daily_briefing_markdown()`](../workmate-agent/app/workflows/daily_briefing.py#L323) 유지 |

### 2.4 `weekly_report` — LLM 부분 결과

현재 [`build_weekly_report_workflow`](../workmate-agent/app/workflows/weekly_report.py#L223)는 **빌더가
아니라 핸들러 자체**로 등록된다([runtime.py:368](../workmate-agent/app/a2a/runtime.py#L368)). 다른
Skill과 등록 모양이 다르므로 W4 합성 시 주의한다.

```
START → calculate_iso_week
      ├→ load_approved_tasks
      └→ load_meeting_evidence
                    ↓
      → link_source_items          link_approved_tasks / link_action_item_tasks
      → classify_work_items        completed / in_progress / delayed / unresolved_issues
      → extract_next_week_plans
      → validate_plan_grounding    근거 없는 계획은 rejected → warnings
      → generate_summary_llm       실패 시 warnings + 원장 기반 부분 결과
      → build_result → END
```

| 설계 포인트 | 내용 |
| --- | --- |
| 분류 소유권 | 분류와 `source_refs`는 Domain(`weekly_classification`)이 소유. LLM은 문장만(W3-R4) |
| `PLAN_CANDIDATE_REJECTED` | 근거 없는 계획 후보는 경고로 남기고 제외 |
| LLM 실패 | `LLM_PROVIDER_UNAVAILABLE` 경고 + 부분 결과. **전체 실패 아님** |
| 재시도 | [`_call_llm_with_retry`](../workmate-agent/app/workflows/weekly_report.py#L55)는 2회이며 429·5xx도 재시도한다. `assistant_router`와 정책이 다르다([30-2-5](30-2-5-design.md) §5.2) |
| `blocked` Task | `delayed`가 아니라 `unresolved_issues`로 간다([test_weekly_source_link.py](../workmate-agent/tests/test_weekly_source_link.py)) |

### 2.5 `search_meetings` — 검색과 근거 판정

```
START → validate_query           빈 query → ValueError
      → reject_unsupported_filter  participants 필터 → ValueError
      ├→ embed_query               provider.embed([query])
      └→ (동일 노드 내) 하이브리드 검색 준비
      → search_hybrid              repo.search_hybrid(...)  [user_id 범위]
      → dedupe_by_rrf              같은 chunk는 rrf_score 높은 것만
      → generate_grounded_answer   MeetingAnswerService (LLM, 실패 시 근거 나열 폴백)
      → verify_source_metadata     회의 날짜 없으면 ValueError
      → build_result → END
```

| 설계 포인트 | 내용 |
| --- | --- |
| 근거 부족은 정상 종료 | `insufficient_evidence: true`로 완료. 예외 아님([96번 §5.5](96-workmate-langgraph-target-architecture.md)) |
| warning 분류 | `grounded` 여부로 `INSUFFICIENT_EVIDENCE`(재시도 불가) / `LLM_PROVIDER_UNAVAILABLE`(재시도 가능) 구분 |
| 회의 날짜 누락 | **전체 실패**(`ValueError`) — 인용 출처에 날짜가 없으면 근거로 쓸 수 없다 |
| LLM 답변 실패 | 근거 나열 답변으로 폴백 + 경고 |

### 2.6 `analyze_meeting` — 실패 격리의 표준

```
START → authorize_meeting        meeting 조회, 없으면 ValueError  [user_id 범위]
      → load_transcript          final transcript rows
      → (없으면) transcribe_audio  source_audio_uri → STT → save_final_transcript
      → analyze_with_llm         asyncio.to_thread(analyzer, transcript)
      → verify_evidence          evidence_text가 final transcript에 있는지
                                 없으면 ValueError (근거 없는 출력 거부)
      → save_analysis            요약·Action Item 후보 저장
      → heal_meeting_title       기본 제목 패턴이면 실제 제목으로 보정
      → index_chunks             chunk 분할 → embedding → pgvector
                                 실패해도 롤백하지 않고 warnings
      → build_result → END
```

| 설계 포인트 | 내용 |
| --- | --- |
| 분석과 색인 분리 | 색인 실패가 이미 저장된 분석 결과를 롤백하지 않는다([96번 §5.4](96-workmate-langgraph-target-architecture.md)) |
| 근거 검증 | 통과하지 못하면 저장하지 않는다. 순서가 중요 |
| 부작용 노드 | `save_final_transcript`·`save_analysis`·`heal_meeting_title`은 재시도 금지 대상 |
| 확인 대상 | 이 Skill은 `assistant_ask` 경유 시 **항상 확인**이 필요하다(비용) |

### 2.7 `assistant_ask` — Meta Skill

937줄 중 실제 분기는 다음과 같다. **W3에서는 확인 흐름을 현재 방식 그대로 재현한다**(W3-R11).

```
START → load_conversation_context      history·context 기본값 보강
      → resolve_context_references     "그 회의", "2번" 같은 지시 해소
      → route_with_llm                 skill_id·arguments 결정 (구조화 출력)
      ├─(reply)→    build_direct_reply
      ├─(clarify)→  build_clarifying_question
      └─(call_skill)→ validate_skill_and_arguments
                        → requires_confirmation?
                            ├─(예)→ build_pending_action_reply   ← W6에서 interrupt로 교체
                            └─(아니오)→ call_selected_skill
                                          → offer_followup      Action Item → Task 제안
                                          → phrase_answer       결과를 자연어로
      → build_assistant_reply → END
```

| 설계 포인트 | 내용 |
| --- | --- |
| `confirmed_skill_id` 재요청 | `route_with_llm`을 건너뛰고 `validate_skill_and_arguments`부터 시작 |
| LLM 호출 횟수 | 라우팅 1회 + 문장화 1회. 재요청 시 라우팅 생략 |
| 확인 판정 | [`_requires_confirmation()`](../workmate-agent/app/workflows/assistant_router.py#L221) 그대로 |
| Skill 호출 | 직접 import 금지. §4의 주입 핸들 사용 |
| 노드 경계 | `requires_confirmation?`과 `call_selected_skill` 사이를 반드시 분리(W6 대비) |

---

## 3. 숨은 부작용 — 설계 결정 W3-D1

### 3.1 발견

`daily_briefing`은 내부에서 `rank_priorities` **Workflow**를 호출한다.

```python
# daily_briefing.py:139
rank_workflow = build_rank_priorities_workflow()
# daily_briefing.py:238
rank_result = await rank_workflow(WorkflowRequest(skill_id="rank_priorities", ...))
priorities = json.loads(rank_result.text)["data"]["priorities"]
```

`rank_priorities`는 실행 중 `snapshot_repository.save_all()`로 **우선순위 Snapshot을 저장**한다
([priority.py:123](../workmate-agent/app/workflows/priority.py#L123)).

**따라서 `daily_briefing`을 호출하면 우선순위 Snapshot이 기록된다.** 이 부작용은 `daily_briefing`의
응답 어디에도 나타나지 않으므로 **W1 스냅샷으로 검출되지 않는다.**

### 3.2 왜 중요한가

`rank_priorities`의 `changes` 필드는 이전 Snapshot과 비교해 `entered`/`unchanged` 등을 계산한다.
`daily_briefing`이 Snapshot을 쓰면 다음번 `rank_priorities` 호출의 `changes` 값이 달라진다. 즉
**두 Skill이 저장소를 통해 결합돼 있다.**

W3에서 `daily_briefing`이 Domain 함수 `rank_tasks()`만 호출하도록 바꾸면 이 결합이 끊기고, 사용자가
관찰하는 `changes` 값이 달라진다.

### 3.3 선택지

| | 방식 | 부작용 | 평가 |
| --- | --- | --- | --- |
| **A** | `rank_priorities` Subgraph를 노드로 호출 | 유지 | **채택** — 현재 동작 보존 |
| B | Domain `rank_tasks()`만 호출 | 제거 | 동작 변경. `changes` 값이 달라짐 |
| C | Domain 호출 + 별도 저장 노드 | 유지 | A와 같은 결과인데 코드가 중복 |

**채택: A.** 근거는 [30-3-2](30-3-2-scope.md) §3의 범위 원칙 — W3은 구조를 바꾸는 단계이지 동작을
바꾸는 단계가 아니다. 부작용 제거가 바람직하더라도 그것은 별도 백로그다.

**검증:** W3-V11에서 `daily_briefing` 실행 후 Snapshot 테이블에 행이 생겼는지 DB로 직접 확인한다.
스냅샷 대조로는 잡히지 않으므로 전용 검증이 필요하다.

### 3.4 다른 Skill의 부작용 목록

재시도 금지 대상(W8)이기도 하므로 함께 정리한다.

| Skill | 부작용 | 노드 |
| --- | --- | --- |
| `rank_priorities` | 우선순위 Snapshot 저장 | `save_snapshot` |
| `daily_briefing` | (간접) 우선순위 Snapshot 저장 | `rank_priorities_subgraph` |
| `analyze_meeting` | 최종 transcript 저장, 분석·후보 저장, 회의 제목 보정, 색인 | `save_*`, `heal_*`, `index_chunks` |
| `review_action_items` | Action Item 승인 상태 변경 | `call_domain_api` |
| `review_proposal` | 제안 승인/무시, Task 생성 | `call_domain_api` |
| `manage_tasks` | Task 생성·수정·삭제 | `create/update/delete_task` |
| `weekly_report` | 없음 | — |
| `search_meetings` | 없음 | — |
| `get_meeting_analysis`·`read_email` | 없음 | — |

---

## 4. Subgraph 간 호출 규칙 — W3-D2

Subgraph는 다른 Skill 모듈을 import하지 않는다(W3-R7). 대신 **Root가 주입한 핸들**을 쓴다.

```python
def build_assistant_router_graph(*, subgraphs: Mapping[str, CompiledGraph]):
    """Assistant Router Subgraph를 만든다.

    subgraphs는 Root Graph가 컴파일 시점에 주입한다 — Skill 모듈을 직접
    import하면 순환 의존이 되기 때문이다(W3-R7).
    """
```

| 호출 | W3에서의 처리 |
| --- | --- |
| `assistant_ask` → 10개 Skill | 주입된 `subgraphs` 맵 사용. W3에서는 인터페이스만 정의하고 실제 연결은 W4 |
| `daily_briefing` → `rank_priorities` | 동일 방식. 부작용 유지(§3의 A안) |

**W3 단계의 한계:** Root Graph가 없으므로 W3에서는 테스트가 직접 주입한다. 실제 조립은
[W4](30-4-w4-root-graph.md) §5.5.

---

## 5. State 스키마 불일치 처리 — W3-D3

Skill마다 입력 모양이 다르다.

| | 방식 | 평가 |
| --- | --- | --- |
| **A** | 공통 State 유지 + Skill 입력은 `input` 하위 dict | **채택** |
| B | Subgraph 전용 State + 입출력 변환 | 변환 코드가 Skill 수만큼 늘고 `warnings` 누적 경로가 끊긴다 |

**채택: A.** `warnings`·식별자는 공통 채널을 그대로 쓰고, Skill 고유 입력만 `state["input"]`에서 읽는다.
Skill 고유 중간 상태는 `source_data`의 namespace를 쓴다.

---

## 6. 확인 흐름의 노드 경계 (W6 대비)

W3은 확인 동작을 바꾸지 않지만(W3-R11), **경계는 W6을 고려해 나눈다.**

```
validate_skill_and_arguments   ← 검증만. 외부 상태 변경 금지(96번 §11-7)
        ↓
requires_confirmation?         ← 판정 노드
        ↓ (예)
build_pending_action_reply     ← W6에서 interrupt()로 교체되는 노드
        ↓ (아니오)
call_selected_skill            ← 실행
```

`build_pending_action_reply`를 독립 노드로 두면 W6의 변경이 **노드 하나 교체**로 끝난다. 이 경계를
안 나누면 W6에서 `assistant_ask`를 다시 분해해야 한다.

확인 대상 판정 규칙 4종(W3에서 변경 금지):

| Skill | 조건 |
| --- | --- |
| `analyze_meeting` | 항상 (비용이 큰 동작) |
| `review_action_items` | `decisions`에 `reject`가 하나라도 있을 때 |
| `review_proposal` | `decision == "ignore"` |
| `manage_tasks` | `action == "delete"` |

---

## 7. 실패 파급 규칙

| Skill | 핵심 소스 (전체 실패) | 보조 (경고 후 진행) | 조용히 무시 |
| --- | --- | --- | --- |
| `daily_briefing` | Task 저장소 | Gmail, Calendar | 메일 본문 보강, LLM 관련성 판정 |
| `weekly_report` | Task·근거 조회 | LLM 요약, 근거 없는 계획 후보 | — |
| `analyze_meeting` | 회의 조회, STT, 분석, 근거 검증 | embedding·pgvector 색인 | — |
| `search_meetings` | 검색, 회의 날짜 누락 | LLM 답변 생성 | — |
| `rank_priorities` | 전부 | — | — |
| 보조 Skill 5종 | 전부 | — | — |

**"조용히 무시"는 경고도 남기지 않는다.** 현재 동작이며, W3에서 경고를 추가하면 스냅샷이 깨진다.
개선이 바람직하더라도 별도 백로그다.

---

## 8. 설계 결정 요약

| ID | 결정 | 근거 |
| --- | --- | --- |
| W3-D1 | `daily_briefing`은 `rank_priorities` Subgraph를 호출해 부작용을 유지한다 | §3.3 |
| W3-D2 | Skill 간 호출은 주입된 핸들로만 | §4 |
| W3-D3 | 공통 State 유지 + `input` 하위 dict | §5 |
| W3-D4 | 얇은 래퍼 Skill은 3노드로 최소 분해 | §2.2 |
| W3-D5 | 확인 판정과 실행 사이를 노드로 분리 | §6 |

## 9. 참조

- [96번 §5·§6](96-workmate-langgraph-target-architecture.md) — 목표 노드 구성
- [30-3-4](30-3-4-requirements.md) — 이 설계가 만족하는 요구사항
- [30-3-7](30-3-7-verification.md) — 설계 결정의 검증
