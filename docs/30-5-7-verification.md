# W5-7 — 검증 설계

> [30-5-w5-entrypoint-swap.md](30-5-w5-entrypoint-swap.md) §7의 상세 문서.

## 1. 검증 목록

| ID | 검증 항목 | 대상 요구사항 | 방법 | 판정 기준 |
| --- | --- | --- | --- | --- |
| W5-V1 | A2A 경로 | W5-R1 | `message:send` 요청 | Graph 실행, Artifact 반환 |
| W5-V2 | 이벤트 순서 | W5-R4 | 이벤트 큐 관찰 | 4종 순서 + Part 내용 |
| W5-V3 | UI 동기 경로 | W5-R2 | `POST /messages` | 동일 응답 구조 |
| W5-V4 | UI 비동기 경로 | W5-R3, R9 | async Skill + 폴링 | `submitted`→`completed`, 실패 시 `FAILED` |
| W5-V5 | 오류 매핑 | W5-R6 | 예외 유발 | 422 / 503 + CORS 헤더 |
| W5-V6 | Route allowlist | W5-R5 | 제외 Route 호출 | 404 / 405 |
| W5-V7 | 운영 경로 스냅샷 | W5-R7 | 케이스 27건 대조 | 전건 PASS |
| W5-V8 | `thread_id` 규칙 | W5-R8 | Checkpoint 조회 | `thread_id == task_id` |
| W5-V9 | Checkpointer 수명 | W5-R10 | 앱 기동·종료 | 연결 누수 없음 |
| W5-V10 | 전체 테스트 | 전체 | 회귀 실행 | 실패 0 |

## 2. 검증 케이스 상세

### W5-V1 — A2A 경로

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V1-1 | `message:send`로 `rank_priorities` 호출 | Graph 실행, Artifact 반환 |
| V1-2 | 11개 Skill 각각 | 정상 응답 |
| V1-3 | `grep -rn "workflow_registry" app/` | **출력 없음** |
| V1-4 | 같은 `message_id` 재전송 | **재실행되지 않음**(W4-D1) |

V1-4가 W4-D1의 실전 검증이다. W4에서는 Graph 단위로 확인했고, 여기서는 진입점을 통해 확인한다.

### W5-V2 — 이벤트 순서

| 케이스 | 확인 | 기대 |
| --- | --- | --- |
| V2-1 | 이벤트 타입 순서 | `submitted → working → artifact → completed` |
| V2-2 | `artifact` 이벤트 | `last_chunk=True` |
| V2-3 | **Artifact Part 구성** | 구조화 `data`만 있어도 `text/plain` Part 포함 |
| V2-4 | `markdown` 있는 결과 | `markdown`이 우선 Part |
| V2-5 | 실패 시 | `completed` 대신 실패 상태 |

**V2-3이 2026-08-14 회귀의 방지선이다.** 그때 Orchestrator가 `COMPLETED`인데도 빈 결과를 읽었다.
이벤트 순서만 보고 내용을 안 보면 같은 문제를 놓친다.

### W5-V3 — UI 동기 경로

| 케이스 | 확인 | 기대 |
| --- | --- | --- |
| V3-1 | 응답 최상위 필드 | `skill_id`·`input_type`·`input`·`task_id`·`state`·`artifact`·`warnings` |
| V3-2 | `artifact` dict 키 | `name`·`description`·`text`·`data`·`markdown`·`mock`·`business_result` |
| V3-3 | `warnings` 전달 | 부분 실패 케이스에서 경고가 응답에 포함 |
| V3-4 | `business_result` | `not mock`과 일치 |

### W5-V4 — UI 비동기 경로

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V4-1 | `analyze_meeting` 요청 | 즉시 `state="submitted"` |
| V4-2 | 폴링 | `WORKING` → `COMPLETED` |
| V4-3 | 완료 후 Task 조회 | Artifact + **metadata에 `warnings`** |
| V4-4 | `ValueError` 유발 | `FAILED` + `status.message`에 원인 |
| V4-5 | `RuntimeError` 유발 | 동상 |
| V4-6 | **예상치 못한 예외 유발** | `FAILED` + "unexpected error" — **`WORKING`에 남지 않음** |
| V4-7 | 멱등성 Key | `record_message()`가 최종 저장 시 **한 번만** 호출됨 |

**V4-3이 W5-D1의 검증이다.** 비동기 Skill은 결과를 폴링으로만 받으므로, Artifact metadata에
`warnings`가 없으면 부분 실패 경고가 조용히 사라진다.

**V4-6이 방어선 검증이다.** Task가 `WORKING`에 영원히 남으면 UI는 5분 타임아웃까지 기다린다.

**V4-7 주의:** `_save_task_status()`는 `record_message()`를 부르지 않는다. 두 번 부르면 멱등성 Key
충돌로 `ValueError`가 난다.

### W5-V5 — 오류 매핑

| 케이스 | 유발 | 기대 |
| --- | --- | --- |
| V5-1 | `analyze_meeting`에 `meeting_id` 누락 | 422, `detail`에 원인 |
| V5-2 | `search_meetings`에 빈 `query` | 422 |
| V5-3 | `DATABASE_URL` 미설정 상태로 `search_meetings` | 503 |
| V5-4 | 위 모든 응답 | **CORS 헤더 존재** |
| V5-5 | 위 모든 응답 | 500이 아님 |
| V5-6 | Graph 노드에서 발생한 `ValueError` | 그대로 전파되어 422 |

**V5-4·V5-6이 핵심이다.** 2026-08-15 사고에서 브라우저는 `TypeError: Failed to fetch`만 봤다 —
CORS 헤더 없는 500이었기 때문이다.

**V5-6은 Graph가 예외를 감싸지 않는지 확인한다.** 단위 테스트로도 가능하다.

```python
with self.assertRaises(ValueError):
    asyncio.run(graph.ainvoke(invalid_state, config))
```

### W5-V6 — Route allowlist

| 케이스 | 호출 | 기대 |
| --- | --- | --- |
| V6-1 | 허용 Route 5개 | 정상 |
| V6-2 | Push notification Route | 404 또는 405 |
| V6-3 | Task list Route | 동상 |
| V6-4 | Extended card Route | 동상 |
| V6-5 | Agent Card Skill 목록 | 11개 불변 |

기존 [test_contract.py](../workmate-agent/tests/test_contract.py)가 이미 검증한다면 그대로 통과하는지
확인한다.

### W5-V7 — 운영 경로 스냅샷

케이스 27건을 **실제 진입점을 통해** 실행.

| 케이스 | 기대 |
| --- | --- |
| V7-1 | 전건 PASS |
| V7-2 | W4 대조 결과와 동일 | 진입점 계층이 값을 바꾸지 않았다 |

**차이 발견 시 원인 후보**

| 후보 | 확인 |
| --- | --- |
| payload 가공 | `{**payload, "user_id": user_id}` 같은 처리 |
| 입력 Schema 검증 | 검증만 하고 변형하지 않는지 |
| 어댑터 변환 | `result_from_state()` 필드 매핑 |
| 멱등성 경로 | 케이스 간 `message_id` 격리 |

### W5-V8 — `thread_id` 규칙

| 케이스 | 확인 | 기대 |
| --- | --- | --- |
| V8-1 | A2A 실행 후 Checkpoint 조회 | `thread_id == task_id` |
| V8-2 | UI 동기 실행 후 | 동상 |
| V8-3 | UI 비동기 실행 후 | 동상 |

### W5-V9 — Checkpointer 수명

| 케이스 | 방법 | 기대 |
| --- | --- | --- |
| V9-1 | 앱 기동 | Checkpointer 생성 1회 |
| V9-2 | 요청 여러 번 | 연결이 누적되지 않음 |
| V9-3 | 앱 종료 | 연결 정리 |
| V9-4 | Windows 환경 | Selector Event Loop와 충돌 없음 |

### W5-V10 — 전체 테스트

```
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

**주의:** W5부터는 운영 경로가 바뀌므로 **기존 테스트가 깨질 수 있다.**

| 깨지는 유형 | 처리 |
| --- | --- |
| Registry를 직접 참조하는 테스트 | 경로 교체 반영(정당) |
| 멱등성 관련 테스트 | W4-D1 동작 변경 반영(정당, 기록) |
| 그 외 | **회귀.** 원인 조사 |

세 번째가 나오면 W5의 교체에 문제가 있는 것이다.

## 3. 로컬 HTTP 확인 (W5-T9)

단위 테스트로 잡히지 않는 항목이다. 실제 서버를 띄워 확인한다.

```
[ ] 정상 요청 → 200, 응답 구조
[ ] 422 응답 + CORS 헤더
[ ] 503 응답 + CORS 헤더
[ ] 비동기 Skill 전체 흐름(submitted → 폴링 → completed)
[ ] 비동기 실패(폴링 → FAILED + 메시지)
[ ] 제외 Route 404/405
[ ] 같은 message_id 재전송 → 재실행 없음
```

## 4. 검증 실행 순서

```
W5-T0에서 먼저:
  1. 기준선 테스트로 현재 동작 고정

교체 중:
  2. W5-V5-6  Graph 예외 전파 (단위)
  3. W5-V1    A2A 경로
  4. W5-V2    이벤트 순서
  5. W5-V3    UI 동기
  6. W5-V4    UI 비동기

교체 후:
  7. W5-V6, V8, V9
  8. W5-V7    운영 경로 스냅샷
  9. W5-V10   전체 회귀
  10. 로컬 HTTP 확인
```

## 5. 판정 규칙

- **W5-V2(이벤트 순서)·W5-V5(오류 매핑)가 PASS하지 않으면 W6으로 진행하지 않는다.** 둘 다 실사용
  중 발견돼 고친 회귀의 재발 방지선이다
- W5-V7 차이는 진입점 계층의 문제다. W4로 돌아가지 않는다
- W5-V10에서 기존 테스트가 깨지면 §2의 세 유형으로 분류한다

## 6. 검증 결과의 소비

| 결과 | 소비처 |
| --- | --- |
| W5-V2, V5 PASS | [W6](30-6-w6-interrupt-resume.md) — 같은 경로에 `INPUT_REQUIRED`가 추가된다 |
| W5-V7 | W6의 변경 전 기준선 |
| W5-V4 | W6의 UI 폴링 분기 추가 지점 |
| `message_id` 비대칭 | [W9](30-9-w9-docs-evidence.md) 후속 백로그 |

## 7. 참조

- [30-5-4](30-5-4-requirements.md) — 검증 대상 요구사항
- [30-5-5](30-5-5-design.md) — 설계 결정
- [30-5-9](30-5-9-exit-criteria.md) — 승인 처리
