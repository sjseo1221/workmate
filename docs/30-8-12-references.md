# W8-12 — 참조 자료

> [30-8-w8-retry-observability.md](30-8-w8-retry-observability.md) §12의 상세 문서.

"무엇을 참조하는가"가 아니라 **"어디를 왜 읽는가"** 를 기록한다.

## 1. 설계 근거 문서

### 96-workmate-langgraph-target-architecture.md

| 절 | 읽는 이유 | 대응 |
| --- | --- | --- |
| **§8 오류·재시도 Graph** | **W8의 설계도.** 재시도 계층 구분과 실패 파급 | W8-R2, R4, R8 |
| §8 | "HTTP 계층 재시도는 Orchestrator가 같은 `message_id`로 담당하고, Graph는 Node 내부 Provider 호출만 재시도한다" | W8-R8 |
| §8 | `AUTH 오류 → AUTH_REQUIRED + interrupt` | W8-R5 |
| §11-6 | "Provider 일부 실패는 사용 가능한 결과와 `warnings`를 보존한다" | W8-R3 |
| §7 | 상태 전이도에 `AUTH_REQUIRED` 포함 | W8-D2 판단 |

**§8의 flowchart를 읽는다.** 재시도 예산·부분 결과·전체 실패의 분기가 그려져 있다.

### 30-langgraph-migration-plan.md

| 절 | 읽는 이유 |
| --- | --- |
| **§9-6** | **완료 기준** — "네트워크 오류만 재시도하고 HTTP 4xx/5xx는 즉시 실패" |
| §4 D3 | `langchain-openai` 도입 — W8-R1의 배경 |
| §4 D5 | 스트리밍은 범위 밖 |
| §5 W8 | 단계 정의 |

**§9-6의 서술이 정밀화 대상이다**([30-8-9](30-8-9-exit-criteria.md) §1.2). 정책이 하나가 아니라는
사실이 반영돼야 한다.

## 2. 코드 참조 — 재시도의 원본

### 2.1 `assistant_router` 계열 (3회, 네트워크만)

| 위치 | 읽는 이유 |
| --- | --- |
| [assistant_router.py:198](../workmate-agent/app/workflows/assistant_router.py#L198) | `_CHAT_COMPLETION_MAX_ATTEMPTS = 3` |
| [assistant_router.py:282-292](../workmate-agent/app/workflows/assistant_router.py#L282) | **주석 — 2026-08-19 DNS 간헐 실패 대응의 전말** |
| [assistant_router.py:293-310](../workmate-agent/app/workflows/assistant_router.py#L293) | **재시도 루프와 예외 분류** — `HTTPError`는 `break`, `URLError`·`TimeoutError`·`JSONDecodeError`는 `continue` |

**주석 전문을 읽는다.**

> 2026-08-19 실사용 중 발견 — `_ipv4_only_getaddrinfo`(app/main.py)로 IPv4를 강제해도 이 환경에서
> LLM Provider 호출이 간헐적으로 `socket.gaierror: [Errno 11001] getaddrinfo failed`로 실패하는 게
> 재현됐다(재시도 없이 바로 assistant_ask 전체가 500으로 죽었다). 원인이 이 프로세스 밖(환경의
> 일시적 DNS 응답 실패)이라 완전히 없앨 수는 없어, 흔한 일시적 오류에 대응하는 표준 방식대로
> 재시도를 추가한다 — **HTTP 오류(4xx/5xx)는 재시도해도 똑같이 실패할 뿐이라 그대로 즉시
> 실패시키고, 네트워크 계층 오류(연결·DNS·Timeout·JSON 파싱)만 재시도 대상으로 좁힌다.**

### 2.2 `weekly_report` 계열 (2회, Provider 오류 포함)

| 위치 | 읽는 이유 |
| --- | --- |
| [weekly_report.py:55-80](../workmate-agent/app/workflows/weekly_report.py#L55) | **`_call_llm_with_retry`** — 다른 정책 |
| [weekly_report.py:60-66](../workmate-agent/app/workflows/weekly_report.py#L60) | **Docstring — "timeout·429·5xx와 Schema 오류는 Provider Adapter에서 `LLMProviderError`로 정규화된다"** |
| [weekly_report.py:48-53](../workmate-agent/app/workflows/weekly_report.py#L48) | `LLMProviderError` 정의 |

**두 Docstring을 나란히 읽는 것이 W8의 출발점이다.** 같은 시스템의 두 LLM 호출이 정반대 정책을
쓴다.

### 2.3 재시도가 없는 지점

| 위치 | 현재 |
| --- | --- |
| [meeting_answer.py:66-90](../workmate-agent/app/meeting_answer.py#L66) | 재시도 없음. 실패 시 근거 나열 폴백 |
| [meeting_analysis.py:54](../workmate-agent/app/meeting_analysis.py#L54) | W8-T1에서 조사 |
| [providers/google.py](../workmate-agent/app/providers/google.py) | Gmail·Calendar — 재시도 유무 조사 |

**재시도가 없던 곳에 추가하지 않는다**(W8-D3).

### 2.4 실패 파급의 원본

| 위치 | 읽는 이유 |
| --- | --- |
| [daily_briefing.py:181-183](../workmate-agent/app/workflows/daily_briefing.py#L181) | Gmail 실패 → `warnings` |
| [daily_briefing.py:195-208](../workmate-agent/app/workflows/daily_briefing.py#L195) | 본문 보강 실패 → **조용히 무시** |
| [daily_briefing.py:210-235](../workmate-agent/app/workflows/daily_briefing.py#L210) | LLM 관련성 판정 실패 → 전부 통과 |
| [weekly_report.py:59-64](../workmate-agent/app/workflows/weekly_report.py#L59) | LLM 실패 → 부분 결과 + 경고 |
| [meetings.py:159-215](../workmate-agent/app/workflows/meetings.py#L159) | 색인 실패 → 경고, 분석 유지 |

**이 동작들을 W8이 바꾸면 안 된다.**

### 2.5 부작용 노드의 원본

| 위치 | 부작용 |
| --- | --- |
| [priority.py:123](../workmate-agent/app/workflows/priority.py#L123) | `snapshot_repository.save_all()` |
| [assistant_skills.py:214](../workmate-agent/app/workflows/assistant_skills.py#L214) | `_review_actions()` — 승인 상태 변경 |
| [assistant_skills.py:293-387](../workmate-agent/app/workflows/assistant_skills.py#L293) | `manage_tasks`의 CRUD |
| [meetings.py:216-320](../workmate-agent/app/workflows/meetings.py#L216) | `analyze_meeting`의 저장 4곳 |

**W7 이후에는 `app/graph/skills/`의 해당 노드를 본다.** 위 경로는 삭제됐다.

## 3. 개발 규칙

### AGENTS.md

| 규칙 | W8에서의 적용 |
| --- | --- |
| 외부 Provider 장애 시 정의된 부분 결과와 `warnings` 반환 | W8-R3 |
| Secret·Token·API Key·개인정보를 주석·Docstring·Fixture에 기록하지 않음 | W8-R7(로그로 확장) |
| 이벤트 순서·멱등성·**재시도**·취소처럼 코드만 읽어도 놓치기 쉬운 불변식은 명시 | 적용표의 주석 |
| 실패한 테스트 삭제·우회 금지 | [30-8-11](30-8-11-rollback.md) §3.2 |
| 기대값 완화 금지 | 동상 |
| LangSmith 등 API Key가 필요한 도입은 별도 승인 | [30-8-2](30-8-2-scope.md) §3.2 |

## 4. 선후 단계 문서

| 문서 | W8과의 관계 |
| --- | --- |
| [30-2-4](30-2-4-requirements.md) W2-R9 | **재시도 정책 정의** — W8이 적용할 대상 |
| [30-2-5](30-2-5-design.md) §5.2 | **정책 불일치 조사** — W8-R10의 근거 |
| [30-2-7](30-2-7-verification.md) W2-V7 | 정책 정의 검증 — W8-E2 |
| [30-3-5](30-3-5-design.md) §3.4 | **부작용 노드 목록** — W8-R9의 근거 |
| [30-3-5](30-3-5-design.md) §7 | **실패 파급 규칙표** — W8-V4·V5의 기준 |
| [30-4-5](30-4-5-design.md) §3 | 멱등성 — HTTP 계층 재시도의 전제 |
| [30-5-4](30-5-4-requirements.md) W5-R6 | 오류 매핑 — W8-K7의 배경 |
| [30-7-9](30-7-9-exit-criteria.md) §6 | 부작용 노드 목록 전달 |
| [30-9](30-9-w9-docs-evidence.md) | 후속 백로그 3건의 소비처 |

## 5. 외부 문서

| 자료 | 확인할 내용 |
| --- | --- |
| **LangGraph — `RetryPolicy`** | `max_attempts`, `retry_on` 시그니처, 노드별 적용 방법 |
| LangGraph — 재시도와 예외 | **재시도 소진 시 원 예외가 유지되는가**(W8-K7) |
| LangGraph — 콜백·미들웨어 | 노드 실행 전후 훅이 있는가(W8-D5) |
| langchain-openai — `max_retries` | 0으로 끌 수 있는가, 내부 HTTP 클라이언트의 재시도 |
| Python `logging` | 구조화 로그, `assertLogs`로 캡처 |

### 5.1 실행으로 확인할 것

문서만으로 판단하지 않는다.

| 질문 | 확인 방법 |
| --- | --- |
| 실제 호출 횟수가 몇 번인가 | `Mock.call_count` |
| 예외가 감싸지는가 | 재시도 소진 후 예외 타입 확인 |
| 콜백이 모든 노드에 걸리는가 | 로그 출력 확인 |

## 6. 이 문서 묶음

| 문서 | 대응 절 |
| --- | --- |
| [30-8-1](30-8-1-document-info.md) | §1 문서 정보·용어·재시도 3계층 |
| [30-8-2](30-8-2-scope.md) | §2 목적, 범위, **W2와의 분담** |
| [30-8-3](30-8-3-entry-criteria.md) | §3 선행 조건 |
| [30-8-4](30-8-4-requirements.md) | §4 요구사항 W8-R1~R10 |
| [30-8-5](30-8-5-design.md) | §5 설계 — 3계층, 오류 분류, **부작용 제외**, 관측 |
| [30-8-6](30-8-6-wbs.md) | §6 작업 분해 W8-T1~T9, **적용표가 핵심 산출물** |
| [30-8-7](30-8-7-verification.md) | §7 검증 설계 W8-V1~V10 |
| [30-8-8](30-8-8-traceability.md) | §8 추적성, 노드×정책, 조사에서 나온 요구사항 |
| [30-8-9](30-8-9-exit-criteria.md) | §9 완료 정의, **§9-6 서술 정밀화** |
| [30-8-10](30-8-10-risks.md) | §10 위험 등록부 W8-K1~K9 |
| [30-8-11](30-8-11-rollback.md) | §11 롤백·중단·재개 |
| [30-8-12](30-8-12-references.md) | §12 참조 (이 문서) |
