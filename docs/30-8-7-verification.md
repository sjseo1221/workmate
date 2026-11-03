# W8-7 — 검증 설계

> [30-8-w8-retry-observability.md](30-8-w8-retry-observability.md) §7의 상세 문서.

## 1. 검증 목록

| ID | 검증 항목 | 대상 요구사항 | 방법 | 판정 기준 |
| --- | --- | --- | --- | --- |
| W8-V1 | 네트워크 오류 재시도 | W8-R1, R10 | 오류 주입 | 정책별 시도 횟수 |
| W8-V2 | **HTTP 오류 비재시도** | W8-R1 | 5xx·429 주입 | **1회 후 즉시 실패** |
| W8-V3 | 중복 재시도 부재 | W8-R2, R8 | 호출 계측 | 정책과 정확히 일치 |
| W8-V4 | 부분 실패 보존 | W8-R3, R4 | 보조 소스 장애 | 부분 결과 + `warnings` |
| W8-V5 | 핵심 실패 전파 | W8-R4 | 핵심 소스 장애 | `FAILED` |
| W8-V6 | 인증 오류 분류 | W8-R5 | 401 주입 | 재시도 안 함, 분류됨 |
| W8-V7 | **부작용 노드 재시도 금지** | W8-R9 | 적용표 + 쓰기 계측 | 재시도 미적용 |
| W8-V8 | 로그 민감정보 | W8-R7 | 전수 검사 | 미검출 |
| W8-V9 | 스냅샷 | 전체 | 27건 대조 | 전건 PASS |
| W8-V10 | 전체 테스트 | 전체 | 회귀 실행 | 실패 0 |

## 2. 검증 케이스 상세

### W8-V1 — 네트워크 오류 재시도

**`NETWORK_ONLY_RETRY` (assistant_router 계열)**

| 케이스 | 주입 | 기대 시도 횟수 |
| --- | --- | --- |
| V1-1 | DNS 실패(`socket.gaierror`) | 3 |
| V1-2 | 연결 오류(`URLError`) | 3 |
| V1-3 | `TimeoutError` | 3 |
| V1-4 | `JSONDecodeError`(응답 파싱 실패) | 3 |
| V1-5 | 정상 응답 | 1 |
| V1-6 | 2번째 시도에서 성공 | 2 |

**`PROVIDER_ERROR_RETRY` (weekly_report 계열)**

| 케이스 | 주입 | 기대 시도 횟수 |
| --- | --- | --- |
| V1-7 | `LLMProviderError`(timeout) | 2 |
| V1-8 | `LLMProviderError`(429) | 2 |
| V1-9 | `LLMProviderError`(5xx) | 2 |
| V1-10 | Schema 오류 | 2 |
| V1-11 | 두 번째도 실패 | 예외 전파 → 부분 결과 |

**V1-8·V1-9가 두 정책의 차이를 보여준다.** 같은 429·5xx를 `assistant_router`는 재시도하지 않고
`weekly_report`는 재시도한다.

### W8-V2 — HTTP 오류 비재시도 (완료 기준)

**`NETWORK_ONLY_RETRY` 대상이다.**

| 케이스 | 주입 | 기대 시도 횟수 |
| --- | --- | --- |
| V2-1 | **HTTP 500** | **1** |
| V2-2 | **HTTP 502** | **1** |
| V2-3 | **HTTP 503** | **1** |
| V2-4 | **HTTP 429** | **1** |
| V2-5 | HTTP 400 | 1 |
| V2-6 | HTTP 401 | 1 |
| V2-7 | HTTP 404 | 1 |

**이 검증이 [계획서 §9-6](30-langgraph-migration-plan.md)의 완료 기준이다.**

2026-08-19 대응의 재발 방지선이기도 하다 — HTTP 오류를 재시도하면 장애 시 지연이 3배가 된다.

### W8-V3 — 중복 재시도 부재

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V3-1 | 네트워크 오류 주입 후 **실제 HTTP 호출 횟수 계측** | 정확히 3 |
| V3-2 | `PROVIDER_ERROR_RETRY` 노드 | 정확히 2 |
| V3-3 | 노드 함수 안에 재시도 루프 검사 | 없음 |
| V3-4 | Provider Client 내부 재시도 검사 | 없음 |
| V3-5 | 라이브러리(`ChatOpenAI`) `max_retries` | 0 |

**V3-1이 핵심이다.** "정책은 3회인데 실제로는 9회 호출"이 가장 흔한 실패다 — 라이브러리 재시도가
살아 있으면 곱해진다.

계측 방법:

```python
mock_http.call_count == 3     # 정책과 정확히 일치
```

### W8-V4 — 부분 실패 보존

[30-3-5](30-3-5-design.md) §7의 규칙표를 검증한다.

| 케이스 | 주입 | 기대 |
| --- | --- | --- |
| V4-1 | `daily_briefing` + Gmail 장애(재시도 소진) | 일정·우선순위 정상 + 경고 |
| V4-2 | `daily_briefing` + Calendar 장애 | 메일·우선순위 정상 + 경고 |
| V4-3 | `daily_briefing` + 둘 다 장애 | 우선순위만 + **경고 2건** |
| V4-4 | `daily_briefing` + 본문 보강 실패 | **경고 없음**, 자리표시자 |
| V4-5 | `daily_briefing` + LLM 관련성 판정 실패 | **경고 없음**, 전부 통과 |
| V4-6 | `weekly_report` + LLM 2회 실패 | 원장 기반 부분 결과 + `LLM_PROVIDER_UNAVAILABLE` |
| V4-7 | `analyze_meeting` + 색인 실패 | 분석 유지 + 재시도 가능 경고 |
| V4-8 | `search_meetings` + LLM 실패 | 근거 나열 + 경고 |

**V4-4·V4-5의 "경고 없음"이 중요하다.** 현재 동작이며, W8에서 경고를 추가하면 스냅샷이 깨진다.

### W8-V5 — 핵심 실패 전파

| 케이스 | 주입 | 기대 |
| --- | --- | --- |
| V5-1 | `daily_briefing` + Task 저장소 장애 | **전체 실패** |
| V5-2 | `weekly_report` + Task 조회 장애 | 전체 실패 |
| V5-3 | `analyze_meeting` + STT 실패 | 전체 실패 |
| V5-4 | `analyze_meeting` + 근거 검증 실패 | **전체 실패, 저장 안 됨** |
| V5-5 | `search_meetings` + 검색 실패 | 전체 실패 |
| V5-6 | `search_meetings` + 회의 날짜 누락 | 전체 실패(`ValueError`) |
| V5-7 | 위 모든 경우의 예외 타입 | **W5의 매핑과 동일**(422/503) |

**V5-7이 W8-K7(재시도 후 예외 타입 변화)의 검증이다.**

### W8-V6 — 인증 오류 분류

| 케이스 | 주입 | 기대 |
| --- | --- | --- |
| V6-1 | HTTP 401 | 재시도 안 함 |
| V6-2 | HTTP 403 | 동상 |
| V6-3 | 분류 결과 | 인증 오류로 구분됨 |
| V6-4 | `AUTH_REQUIRED` 상태 | **W8-D2 결정에 따름** |

V6-4는 W8-T1에서 미도입으로 결정하면 검증 대상이 아니다.

### W8-V7 — 부작용 노드 재시도 금지 (최우선 제약)

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V7-1 | 적용표 검토 | 부작용 노드 전부 "제외" |
| V7-2 | `manage_tasks.create` 노드에 오류 주입 | **재시도 없음** |
| V7-3 | V7-2 후 Task 수 | **1개**(중복 생성 없음) |
| V7-4 | `review_proposal` 노드 | 동상 |
| V7-5 | `rank_priorities.save_snapshot` | Snapshot 1건 |
| V7-6 | `analyze_meeting`의 4개 쓰기 노드 | 각각 1회 |
| V7-7 | 코드 검사 | 부작용 노드에 `retry=` 인자 없음 |

**V7-3이 이 제약의 의미를 보여준다.** 재시도가 붙어 있으면 Task가 3개 생긴다.

### W8-V8 — 로그 민감정보

| 케이스 | 패턴 | 기대 |
| --- | --- | --- |
| V8-1 | `sk-`, `Bearer `, `ya29.`, `AIza` | 미검출 |
| V8-2 | `X-Amz-Signature`, `Expires=` | 미검출 |
| V8-3 | Fixture의 메일 본문 문자열 | 미검출 |
| V8-4 | Fixture의 회의 녹취 문자열 | 미검출 |
| V8-5 | LLM 프롬프트·응답 전문 | 미검출 |
| V8-6 | `user_id` | **검출됨(허용)** |

**V8-6이 허용 항목이다.** OIDC subject이며 장애 조사에 필요하다.

**검사 방법:** 테스트 실행 중 로그를 캡처해 패턴 검사. 테스트로 구현한다.

### W8-V9 — 스냅샷

```
uv run python -m unittest tests.contracts.test_contract_snapshots -v
```

| 케이스 | 기대 |
| --- | --- |
| V9-1 | 27건 전건 PASS |
| V9-2 | 특히 **부분 실패 케이스 6건** | 재시도 적용이 결과를 바꾸지 않았다 |

**부분 실패 케이스가 W8에서 가장 위험하다.** 재시도 정책이 바뀌면 실패 시점과 경고 내용이 달라질 수
있다.

### W8-V10 — 전체 테스트

```
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

## 3. 검증 실행 순서

```
W8-T2 (적용표) 완료:
  1. W8-V7-1  적용표 검토 — 부작용 노드 제외 확인

W8-T3 (정책 적용) 완료:
  2. W8-V1    네트워크 재시도
  3. W8-V2    HTTP 비재시도  ← 완료 기준
  4. W8-V7    부작용 노드 (실제 주입)

W8-T4 (루프 제거) 완료:
  5. W8-V3    중복 재시도 부재  ← 호출 계측

W8-T5 완료:
  6. W8-V4, V5  실패 파급
  7. W8-V6      인증 오류

W8-T6, T7 완료:
  8. W8-V8    로그 민감정보

최종:
  9. W8-V9    스냅샷
  10. W8-V10  전체 회귀
```

## 4. 판정 규칙

- **W8-V2(HTTP 비재시도) FAIL이면 W9로 진행하지 않는다.** [계획서 §9-6](30-langgraph-migration-plan.md)의
  완료 기준이다
- **W8-V7(부작용 노드) FAIL은 즉시 수정.** 중복 실행은 데이터 손상을 낳는다
- W8-V3에서 호출 횟수가 정책보다 많으면 라이브러리 재시도가 살아 있는 것이다
- W8-V9의 부분 실패 케이스 차이는 재시도 적용이 동작을 바꾼 것이다

## 5. 계측 도구

| 검증 | 방법 |
| --- | --- |
| 시도 횟수 | `Mock.call_count` |
| 오류 주입 | `Mock.side_effect`에 예외 리스트 |
| 로그 캡처 | `unittest`의 `assertLogs` 또는 핸들러 주입 |
| 쓰기 계측 | Repository Mock의 호출 횟수 |

**실제 외부 API는 호출하지 않는다.**

## 6. 검증 결과의 소비

| 결과 | 소비처 |
| --- | --- |
| **W8-V2 PASS** | [계획서 §9-6](30-langgraph-migration-plan.md) 완료 기준 |
| 재시도 적용표 | [W9](30-9-w9-docs-evidence.md) 증빙 |
| 두 정책 보존 기록 | W9 후속 백로그(통일) |
| W8-D2 판단 | W9 후속 백로그(`AUTH_REQUIRED`) |
| W8-V9 | W9 diff 분류 |

## 7. 참조

- [30-8-4](30-8-4-requirements.md) — 검증 대상 요구사항
- [30-8-5](30-8-5-design.md) — 설계
- [30-3-5](30-3-5-design.md) §7 — 실패 파급 규칙표
