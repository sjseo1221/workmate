# W2-7 — 검증 설계

> [30-2-w2-graph-foundation.md](30-2-w2-graph-foundation.md) §7의 상세 문서.

## 1. 검증 목록

| ID | 검증 항목 | 대상 요구사항 | 방법 | 판정 기준 |
| --- | --- | --- | --- | --- |
| W2-V1 | State Reducer | W2-R1, R2 | 단위 테스트 | 경고 누적, 유실 없음 |
| W2-V2 | 식별자 불변식 | W2-R3 | 단위 테스트 | 변경 시도가 검출됨 |
| W2-V3 | 어댑터 왕복 | W2-R5 | 단위 테스트 | 8개 필드 산출, 식별자 보존 |
| W2-V4 | Checkpoint 저장·복원·이력 | W2-R7, R11 | 통합 테스트 | 이력 누적, 책임 분리 |
| W2-V5 | Checkpointer 백엔드 선택 | W2-R6 | 통합 테스트 | 두 백엔드 정확히 선택·동작 |
| W2-V6 | 구조화 출력 동등성 | W2-R8, R10 | 비교 테스트 | 결과 구조 동일 |
| W2-V7 | 재시도 정책 | W2-R9 | 오류 주입 테스트 | 정책별 시도 횟수 일치 |
| W2-V8 | 기존 테스트 무영향 | 전체 | 회귀 실행 | 440+ 실패 0 |
| W2-V9 | Secret 비저장 | W2-R4 | 패턴 검사 | 미검출 |

## 2. 검증 케이스 상세

### W2-V1 — State Reducer

| 케이스 | 입력 | 기대 |
| --- | --- | --- |
| V1-1 | 두 노드가 각각 `warnings`에 1건씩 추가 | 결과에 2건 모두 존재 |
| V1-2 | 한 노드가 `warnings`에 2건 추가 | 2건 모두 존재 |
| V1-3 | 빈 `warnings` 상태에서 추가 | 1건 |
| V1-4 | 두 노드가 `source_data`의 서로 다른 출처 키에 기록 | 두 키 모두 존재 |
| V1-5 | 두 노드가 `source_data`의 **같은 키**에 기록 | 예외 발생(조용한 덮어쓰기 금지) |

**주의** V1-1은 순서에 의존하지 않는 단언을 쓴다. 같은 superstep 내 노드 실행 순서는 보장되지 않는다.

### W2-V2 — 식별자 불변식

| 케이스 | 입력 | 기대 |
| --- | --- | --- |
| V2-1 | 노드가 `user_id`를 다른 값으로 반환 | 테스트가 검출(실패) |
| V2-2 | 노드가 `thread_id`를 변경 | 검출 |
| V2-3 | 정상 흐름 실행 | 종료 State의 식별자 5종이 초기값과 동일 |

**설계 의도** V2-1·V2-2는 "바꾸려 하면 잡힌다"를 확인한다. 변경을 시도하는 노드를 테스트 안에서
실제로 만들어 실행한다. 정상 노드만으로 "안 바뀌었다"를 확인하는 것은 검증이 아니다.

### W2-V3 — 어댑터 왕복

| 케이스 | 입력 | 기대 |
| --- | --- | --- |
| V3-1 | 전형적 payload | State에 식별자·`input`·`now`·`timezone` 존재 |
| V3-2 | State → 결과 | 8개 필드(`artifact_name`·`artifact_description`·`text`·`data`·`markdown`·`state`·`warnings`·`mock`) 산출 |
| V3-3 | 왕복 | 입력 식별자가 결과까지 보존 |
| V3-4 | `warnings` 있는 State | 결과 `warnings`에 전달 |
| V3-5 | 구조화 결과가 `text`에만 있는 State | `data`도 함께 채워짐(빈 `data` 금지) |
| V3-6 | `markdown` 없는 State | `markdown=None`, 오류 아님 |

**V3-5의 근거** [test_priority_workflow.py:45-49](../workmate-agent/tests/test_priority_workflow.py#L45-L49)에
기록된 실사용 버그 — `data`가 비면 프론트가 항상 빈 결과를 읽는다.

### W2-V4 — Checkpoint 저장·복원·이력

| 케이스 | 입력 | 기대 |
| --- | --- | --- |
| V4-1 | 노드 2개 Graph를 `thread_id=T`로 실행 | Checkpoint가 노드 수만큼 생성 |
| V4-2 | 같은 `thread_id`로 재실행 | 이력이 누적(덮어쓰기 아님) |
| V4-3 | `get_state_history()` 조회 | 노드별 Snapshot 조회 가능 |
| V4-4 | 다른 `thread_id` | 이력이 섞이지 않음 |
| V4-5 | 실행 후 Task Store 조회 | **Checkpointer가 Task 상태·Artifact를 쓰지 않았음** |
| V4-6 | Task Store 저장 후 Checkpoint 조회 | **Task Store가 노드 State를 쓰지 않았음** |

**V4-5·V4-6이 W2-R11(책임 분리)의 실질적 검증이다.** 설계 검토만으로는 경계 침범을 잡을 수 없다.

### W2-V5 — Checkpointer 백엔드 선택

| 케이스 | 환경 | 기대 |
| --- | --- | --- |
| V5-1 | `DATABASE_URL` 설정 | Postgres Saver 반환 + **실제 저장·복원 성공** |
| V5-2 | 미설정 | SQLite Saver 반환 + 실제 저장·복원 성공 |
| V5-3 | 두 경우 | Task Store의 백엔드 선택과 일치 |

**주의** 타입만 확인하고 끝내지 않는다. Postgres 경로가 실제로 동작하는지 확인해야 운영 백엔드가
검증된다. 테스트 컨테이너가 필요하다([30-2-3](30-2-3-entry-criteria.md) W2-E4).

### W2-V6 — 구조화 출력 동등성

| 케이스 | 입력 | 기대 |
| --- | --- | --- |
| V6-1 | Router Schema + 고정 응답 | 기존 경로와 신규 경로의 결과 구조 동일 |
| V6-2 | Weekly Summary Schema + 고정 응답 | 동일 |
| V6-3 | 스키마 위반 응답 주입 | 양쪽 모두 오류 처리(조용한 통과 없음) |
| V6-4 | 모델 호출 파라미터 검사 | `temperature=0` 전달 |
| V6-5 | strict 모드 | 유지 확인. 미유지 시 사실과 대체 검증 수단 기록 |

**방법** 실제 API를 부르지 않는다. HTTP 계층을 고정 응답으로 대체하고 양쪽 경로를 같은 입력으로
실행해 결과를 비교한다.

**중요도** 이 검증이 실패하면 W3의 LLM 의존 Skill(`weekly_report`·`analyze_meeting`·`search_meetings`·
`assistant_ask`)을 착수할 수 없다([30-3](30-3-w3-skill-subgraphs.md) W3-E3).

### W2-V7 — 재시도 정책

정책이 두 종류이므로 각각 검증한다([30-2-5](30-2-5-design.md) §5.2).

**`NETWORK_ONLY_RETRY` (assistant_router 계열)**

| 케이스 | 주입 | 기대 시도 횟수 |
| --- | --- | --- |
| V7-1 | DNS 실패(네트워크 오류) | 3 |
| V7-2 | Timeout | 3 |
| V7-3 | 응답 JSON 파싱 실패 | 3 |
| V7-4 | **HTTP 500** | **1** (즉시 실패) |
| V7-5 | **HTTP 429** | **1** |
| V7-6 | HTTP 401 | 1 |
| V7-7 | 정상 응답 | 1 |

**`PROVIDER_ERROR_RETRY` (weekly_report 계열)**

| 케이스 | 주입 | 기대 시도 횟수 |
| --- | --- | --- |
| V7-8 | Provider 오류(429·5xx·timeout·Schema) | 2 |
| V7-9 | 두 번째도 실패 | 예외 전파(Workflow가 부분 결과로 변환) |

**공통**

| 케이스 | 확인 | 기대 |
| --- | --- | --- |
| V7-10 | 실제 HTTP 호출 횟수 계측 | 정책상 시도 횟수와 정확히 일치 — 라이브러리 재시도로 인한 초과 호출 없음 |

**V7-4·V7-5·V7-10이 계획서 §9-6 완료 조건의 근거다.** V7-10은 `max_retries=0`이 실제로 적용됐는지를
확인하는 유일한 수단이다.

### W2-V8 — 기존 테스트 무영향

```
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

| 항목 | 기대 |
| --- | --- |
| 기존 440건 | 전부 통과 |
| W1 스냅샷 | 전건 PASS |
| W2 신규 테스트 | 전부 통과 |
| SKIP | 0 |

**의존성 추가만으로 기존 테스트가 깨질 수 있다.** W2-T1 직후에도 한 번 실행한다.

### W2-V9 — Secret 비저장

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V9-1 | State 직렬화 결과 패턴 검사 | `sk-`·`Bearer `·`X-Goog-` 등 미검출 |
| V9-2 | Checkpoint 저장 내용 검사 | 동일 |
| V9-3 | Gmail 원문·회의 녹취 원문 | State에 직접 싣지 않고 식별자로 참조 |

**V9-2가 W2에서 새로 생긴 위험이다.** State는 Checkpointer를 통해 DB에 영속화된다. 지금까지 메모리에만
있던 값이 디스크에 남는다.

## 3. 검증 실행 순서

```
1. W2-T1 직후:  W2-V8 (의존성 추가만으로 회귀가 없는지)
2. 모듈 구현 중: V1~V3 (State·어댑터)
                V4, V5 (Checkpointer)
                V6, V7 (LLM)
3. 통합:        V9 (Secret)
4. 최종:        W2-V8 전체 재실행
```

## 4. 검증 도구

| 검증 | 도구·기법 |
| --- | --- |
| V1~V3 | `unittest` 단위 테스트 |
| V4, V5 | `unittest` + 임시 SQLite + 테스트 Postgres |
| V6 | HTTP 계층 고정 응답 주입(`patch`) |
| V7 | 예외·응답 주입 + 호출 횟수 계측(`Mock.call_count`) |
| V8 | 전체 스위트 |
| V9 | 정규식 패턴 검사 |

실제 외부 API는 호출하지 않는다. W2는 비용과 결정성 모두에서 외부 호출을 필요로 하지 않는다.

## 5. 판정 규칙

- 검증 항목은 **PASS / FAIL** 두 값만 갖는다. "대체로 통과"는 FAIL이다.
- W2-V6에서 strict 모드가 유지되지 않는 경우는 FAIL이 아니라 **조건부 PASS**로 기록하되, 대체 검증
  수단(스키마 사후 검증 등)을 함께 구현해야 한다.
- 하나라도 FAIL이면 W2는 미완료이며 W3를 착수하지 않는다. 단 W2-V6만 FAIL인 경우
  [30-3](30-3-w3-skill-subgraphs.md) W3-E3에 따라 결정적 Skill만 선행할 수 있다.

## 6. 참조

- [30-2-4](30-2-4-requirements.md) — 검증 대상 요구사항
- [30-2-8](30-2-8-traceability.md) — 요구사항↔검증 대응 확인
- [30-2-9](30-2-9-exit-criteria.md) — 검증 결과의 승인 처리
