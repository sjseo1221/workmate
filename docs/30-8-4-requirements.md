# W8-4 — 요구사항 명세

> [30-8-w8-retry-observability.md](30-8-w8-retry-observability.md) §4의 상세 문서.

## 요약

| ID | 구분 | 한 줄 | 우선순위 | 검증 |
| --- | --- | --- | --- | --- |
| W8-R1 | 제약 | **네트워크 오류만 재시도, HTTP 4xx/5xx 즉시 실패**(`assistant_router` 계열) | **필수(완료 기준)** | W8-V1, V2 |
| W8-R2 | 기능 | 재시도는 노드 `RetryPolicy`가 소유. 내부 루프 금지 | 필수 | W8-V3 |
| W8-R3 | 기능 | Provider 일부 실패 시 부분 결과와 `warnings` 보존 | 필수 | W8-V4 |
| W8-R4 | 기능 | 재시도 소진 시 핵심/보조에 따라 `FAILED`/`warnings` | 필수 | W8-V4, V5 |
| W8-R5 | 기능 | 인증 오류를 `AUTH_REQUIRED`로 분류 | 중요 | W8-V6 |
| W8-R6 | 기능 | 노드 단위 실행 로그 | 필수 | 로그 확인 |
| W8-R7 | 제약 | 로그에 Secret·개인정보 금지 | **필수** | W8-V8 |
| W8-R8 | 제약 | HTTP 계층 재시도는 Orchestrator 담당. Graph 중복 금지 | 필수 | W8-V3 |
| W8-R9 | 제약 | **부작용 노드에 재시도를 붙이지 않는다** | **필수** | W8-V7 |
| W8-R10 | 제약 | 두 재시도 정책을 각각 보존(통일 금지) | 필수 | W8-V1, V9 |

---

## W8-R1 — 재시도 정책 보존 (완료 기준)

**설명** `assistant_router` 계열에서 **네트워크 계층 오류만 재시도하고 HTTP 4xx/5xx는 즉시 실패**한다.

**근거** [assistant_router.py:295-305](../workmate-agent/app/workflows/assistant_router.py#L295-L305)의
원래 구현과 그 주석.

> 2026-08-19 실사용 중 발견 — (…) LLM Provider 호출이 간헐적으로 `socket.gaierror: [Errno 11001]
> getaddrinfo failed`로 실패하는 게 재현됐다 (…) HTTP 오류(4xx/5xx)는 재시도해도 똑같이 실패할
> 뿐이라 그대로 즉시 실패시키고, 네트워크 계층 오류(연결·DNS·Timeout·JSON 파싱)만 재시도 대상으로
> 좁힌다.

**계획서 §9-6의 완료 기준이기도 하다.**

**수용 기준**

| 오류 | 시도 횟수 |
| --- | --- |
| DNS 실패·연결 오류 | 3 |
| Timeout | 3 |
| JSON 파싱 실패 | 3 |
| **HTTP 500** | **1** |
| **HTTP 429** | **1** |
| HTTP 401·403·404 | 1 |

**검증** W8-V1, V2 / **우선순위** **필수(완료 기준)**

---

## W8-R2 — 재시도 소유권

**설명** 재시도는 노드 `RetryPolicy`가 소유하고, 노드 함수 안에 재시도 루프를 두지 않는다.

**근거** [96번 §8](96-workmate-langgraph-target-architecture.md). 노드 계층에 모으면

| 이득 | 설명 |
| --- | --- |
| 일관성 | 모든 노드가 같은 방식 |
| 관측 가능 | 재시도 횟수가 Graph 실행 정보에 남는다 |
| 제어 가능 | 노드별로 켜고 끌 수 있다 |

**수용 기준**
- 노드 함수 안에 `for attempt in range(...)` 형태의 루프가 없다
- 재시도는 `RetryPolicy` 설정으로만
- **호출 횟수가 정책과 정확히 일치**(중복 재시도 없음)

**검증** W8-V3 / **우선순위** 필수

---

## W8-R3 — 부분 실패 보존

**설명** Provider 일부 실패 시 사용 가능한 결과와 `warnings`를 반환한다.

**근거** `AGENTS.md`, [96번 §11-6](96-workmate-langgraph-target-architecture.md).

**수용 기준** — [30-3-5](30-3-5-design.md) §7의 실패 파급 규칙표와 동일해야 한다. W8이 이를 바꾸지
않는다.

**검증** W8-V4 / **우선순위** 필수

---

## W8-R4 — 재시도 소진 후 처리

**설명** 재시도 예산이 소진됐을 때 핵심 결과가 불가능하면 `FAILED`, 부분 결과가 가능하면 `warnings`
후 진행한다.

**근거** [96번 §8](96-workmate-langgraph-target-architecture.md)의 오류 Graph.

**수용 기준**

| Skill | 핵심 소스 소진 | 보조 소스 소진 |
| --- | --- | --- |
| `daily_briefing` | `FAILED` | `warnings` + 부분 결과 |
| `weekly_report` | `FAILED` | 원장 기반 부분 결과 |
| `analyze_meeting` | `FAILED` | 재시도 가능 `warnings` |
| `search_meetings` | `FAILED` | RRF 결과 + `warnings` |

**검증** W8-V4, V5 / **우선순위** 필수

---

## W8-R5 — 인증 오류 분류

**설명** Provider 재인증이 필요한 오류를 `AUTH_REQUIRED`로 분류한다.

**근거** [96번 §8](96-workmate-langgraph-target-architecture.md): "AUTH 오류 → `AUTH_REQUIRED` +
interrupt".

**현재 상태** `AUTH_REQUIRED` 상태가 현재 구현에 있는지 W8-T1에서 확인한다. 없으면 **이번에
도입할지 판단**한다 — `INPUT_REQUIRED`(W6)와 같은 성격의 신규 상태이므로 계약 영향이 있다.

**수용 기준**
- 401·403 응답이 인증 오류로 분류된다
- 재시도 대상이 아니다
- `AUTH_REQUIRED` 상태 도입 여부가 결정되고 기록된다

**검증** W8-V6 / **우선순위** 중요(필수 아님 — 계약 영향 판단 필요)

---

## W8-R6 — 노드 실행 로그

**설명** 노드명·`thread_id`·소요 시간·상태·경고 코드·재시도 횟수를 남긴다.

**수용 기준**

```python
{"node": "fetch_gmail", "thread_id": "...", "user_id": "...",
 "elapsed_ms": 412, "status": "warning",
 "warning_code": "GOOGLE_PROVIDER_UNAVAILABLE", "retry_count": 1}
```

- 모든 노드 실행에 대해 남는다
- 실패·경고 시 코드가 포함된다
- 표준 로깅을 쓴다(외부 서비스 없음)

**검증** 로그 확인 / **우선순위** 필수

---

## W8-R7 — 로그 민감정보 금지

**설명** 로그에 Secret·Token·Presigned URL·메일 본문·회의 녹취를 남기지 않는다.

**근거** `AGENTS.md` 금지 사항.

**수용 기준**
- 로그 전수 검사에서 토큰·키 패턴 미검출
- 메일 본문·회의 내용 미포함
- LLM 프롬프트·응답 전문 미포함
- `user_id`는 허용(OIDC subject, 장애 조사에 필요)

**검증** W8-V8 / **우선순위** **필수**

---

## W8-R8 — 계층 중복 금지

**설명** HTTP 계층 재시도는 Orchestrator가 같은 `message_id`로 담당한다. Graph가 중복 재시도하지
않는다.

**근거** [96번 §8](96-workmate-langgraph-target-architecture.md).

**W4-D1이 이를 성립시켰다.** 멱등성이 구현돼 있으므로 Orchestrator가 재시도해도 중복 실행되지 않는다.

**수용 기준**
- Graph가 요청 전체를 재시도하지 않는다
- 노드 재시도만 존재한다
- Provider Client 내부에 재시도가 없다

**검증** W8-V3 / **우선순위** 필수

---

## W8-R9 — 부작용 노드 제외 (최우선 제약)

**설명** 외부 상태를 바꾸는 노드에 `RetryPolicy`를 붙이지 않는다.

**근거** 노드 재시도의 전제는 **재실행이 안전한 것**이다. 부작용 노드는 재실행 시 중복 처리된다.

**대상**([30-3-5](30-3-5-design.md) §3.4)

| Skill | 제외 노드 |
| --- | --- |
| `rank_priorities` | `save_snapshot` |
| `daily_briefing` | `rank_priorities_subgraph` |
| `analyze_meeting` | `save_final_transcript`, `save_analysis`, `heal_meeting_title`, `index_chunks` |
| `review_action_items` | `call_domain_api` |
| `review_proposal` | `call_domain_api` |
| `manage_tasks` | `create/update/delete_task` |

**수용 기준**
- 위 노드에 `RetryPolicy`가 없다
- 적용표에 명시적으로 기록된다
- 쓰기 노드 계측에서 중복 호출이 없다

**검증** W8-V7 / **우선순위** **필수**

---

## W8-R10 — 두 정책 각각 보존

**설명** `assistant_router` 계열(3회·네트워크만)과 `weekly_report` 계열(2회·Provider 오류 포함)을
각각 보존한다. 통일하지 않는다.

**근거** [30-2-5](30-2-5-design.md) §5.2. 통일은 동작 변경이며 W1 스냅샷의 부분 실패 케이스를
깨뜨린다.

**수용 기준**
- `NETWORK_ONLY_RETRY`가 `assistant_router` 계열 노드에 적용
- `PROVIDER_ERROR_RETRY`가 `weekly_report` 계열 노드에 적용
- 각 정책의 시도 횟수와 대상이 원래와 동일
- 스냅샷의 부분 실패 케이스가 PASS

**검증** W8-V1, V9 / **우선순위** 필수

---

## 요구사항 간 의존

```
W8-R2 (소유권) ─┬→ W8-R1 (정책 보존)  ← 완료 기준
                ├→ W8-R8 (계층 중복 금지)
                ├→ W8-R9 (부작용 제외)  ← 최우선 제약
                └→ W8-R10 (두 정책)

W8-R3, R4 (부분 실패) ← 기존 동작 보존
W8-R6 (로그) ─→ W8-R7 (민감정보)
W8-R5 (인증) ← 계약 영향 판단 필요
```

## 참조

- [96번 §8·§11-6](96-workmate-langgraph-target-architecture.md)
- [30-2-5](30-2-5-design.md) §5.2 — 정책 불일치
- [30-3-5](30-3-5-design.md) §3.4, §7 — 부작용 노드, 실패 파급
