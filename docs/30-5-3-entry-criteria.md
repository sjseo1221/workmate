# W5-3 — 선행 조건

> [30-5-w5-entrypoint-swap.md](30-5-w5-entrypoint-swap.md) §3의 상세 문서.

## 1. 선행 조건 목록

| ID | 조건 | 출처 | 확인 방법 | 미충족 시 |
| --- | --- | --- | --- | --- |
| W5-E1 | W4 완료 — `build_workmate_graph()` 동작 | [30-4-9](30-4-9-exit-criteria.md) | 컴파일·실행 | 착수 금지 |
| W5-E2 | **W4-V3(멱등성) PASS** | [30-4-7](30-4-7-verification.md) | W4 증빙 | **착수 금지** |
| W5-E3 | W4-V7(Checkpoint) PASS | 동상 | W4 증빙 | 착수 금지 |
| W5-E4 | W4-V6(Root 경유 스냅샷) 전건 PASS | 동상 | 대조 실행 | 착수 금지 |
| W5-E5 | `message_id` 방침 확정 | [30-4-9](30-4-9-exit-criteria.md) §6.1 | 결정 기록 | W5-T0에서 확정 |
| W5-E6 | 기존 이벤트 순서·오류 매핑 테스트 존재 | — | 테스트 확인 | 기준선 없이 교체 위험 |

## 2. 각 조건의 근거

### 2.1 W5-E2 — 멱등성이 차단 조건인 이유

W4-V3이 FAIL인 채로 진입점을 바꾸면 **중복 실행이 외부에 노출된다.**

| W4까지 | W5 이후 |
| --- | --- |
| Graph는 테스트에서만 실행. 멱등성이 깨져도 사용자 영향 없음 | 실제 요청이 Graph를 탄다 |

중복 실행은 부작용이 있는 Skill에서 실제 피해를 낳는다 — `manage_tasks.create`가 두 번 실행되면 Task가
두 개 생기고, `review_proposal`이 두 번 실행되면 상태가 꼬인다.

**다른 어떤 검증보다 이것이 W5의 전제다.**

### 2.2 W5-E3 — Checkpointer

W5에서 Graph를 실제로 실행하면 Checkpoint가 **운영 DB에 쌓이기 시작**한다. 저장·복원이 검증되지
않았다면 W5에서 문제가 생겨도 원인이 Graph인지 Checkpointer인지 모른다.

또한 W5-T3(Checkpointer 수명 결합)이 앱 lifespan을 건드리므로, 생성·정리 동작이 확인돼 있어야 한다.

### 2.3 W5-E4 — 대조 기준선

W5는 같은 스냅샷을 **운영 경로를 경유해** 다시 대조한다(W5-V7).

```
W3: Subgraph 직접   → PASS
W4: Root Graph 경유 → PASS
W5: 운영 경로 경유  → PASS여야 함
     차이가 나면 원인은 진입점 계층(인증·Schema 검증·Task 저장·이벤트 발행)
```

### 2.4 W5-E5 — `message_id` 방침

W4에서 넘어온 문제다. UI REST는 `message_id = f"internal-{task_id}"`이고 `task_id`가 매번 새
`uuid4()`라 멱등성이 발동하지 않는다.

W4에서 멱등성을 제대로 구현했으므로, UI REST 경로를 그대로 둘지 바꿀지 W5에서 정해야 한다. 방침
선택지는 [30-5-5](30-5-5-design.md) §6에 있다.

**착수 전 확정이 원칙이지만**, W5-T0에서 정해도 된다 — 다만 W5-T3(UI REST 교체) 전에는 확정돼야 한다.

### 2.5 W5-E6 — 기준선 테스트

교체 전에 "지금 어떻게 동작하는가"를 고정하는 테스트가 있어야 한다.

| 계약 | 기존 테스트 |
| --- | --- |
| 이벤트 순서 | [test_runtime_boot.py](../workmate-agent/tests/test_runtime_boot.py) |
| 오류 매핑 | [test_internal_chat.py](../workmate-agent/tests/test_internal_chat.py) |
| Route allowlist | [test_contract.py](../workmate-agent/tests/test_contract.py) |
| 비동기 경로 | [test_internal_chat.py](../workmate-agent/tests/test_internal_chat.py) |

없거나 부족하면 **교체 전에 보강한다.** 교체 후에 만들면 새 동작을 고정하는 것이지 회귀를 잡는 것이
아니다.

## 3. 착수 전 확인 명령

```bash
cd workmate-agent

# W5-E1
uv run python -c "from app.graph import build_workmate_graph; g = build_workmate_graph(); print(type(g))"

# W5-E6
grep -n "submitted\|working\|completed\|artifact" tests/test_runtime_boot.py | head
grep -n "422\|503" tests/test_internal_chat.py | head

# W5-E2, E3, E4
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

## 4. 환경 전제

| 항목 | 이유 |
| --- | --- |
| 테스트 PostgreSQL | Checkpointer·Task Store의 Postgres 경로 |
| Windows Selector Event Loop | [main.py](../workmate-agent/app/main.py) 설정 유지 — 비동기 Checkpointer와의 상호작용 |
| 로컬 서버 기동 가능 | W5-V1·V3에서 실제 HTTP 요청 확인 |

### 4.1 로컬 서버 기동

W5는 **실제 HTTP 요청으로 확인하는 것이 권장**된다. 단위 테스트만으로는 미들웨어 체인(CORS·인증)을
거친 실제 응답을 볼 수 없다.

2026-08-15 사고가 정확히 그런 경우였다 — 예외가 `CORSMiddleware` 바깥의 `ServerErrorMiddleware`까지
올라가 CORS 헤더 없는 500이 되고, 브라우저는 `TypeError: Failed to fetch`만 보였다. 단위 테스트에서는
드러나지 않는다.

## 5. 미충족 시 처리

| 조건 | 미충족 상황 | 처리 |
| --- | --- | --- |
| W5-E1 | Graph 컴파일 실패 | W4로 복귀 |
| W5-E2 | 멱등성 FAIL | **W4로 복귀.** 예외 없음 |
| W5-E3 | Checkpoint FAIL | W4 또는 W2로 복귀 |
| W5-E4 | 스냅샷 차이 | W4에서 해소 |
| W5-E5 | 방침 미정 | W5-T0에서 확정 |
| W5-E6 | 기준선 테스트 부족 | **교체 전에 보강** |

## 6. 후행 단계의 선행 조건에 미치는 영향

| W5 결과 | W6 선행 조건 | 관계 |
| --- | --- | --- |
| 운영 경로가 Graph | [W6-E1](30-6-w6-interrupt-resume.md) | `interrupt`를 넣을 대상 |
| W5-V7(운영 경로 스냅샷) | W6의 변경 전 기준선 | 의도적 변경을 분리하려면 나머지가 PASS여야 |
| 오류 매핑 유지 확인 | W6 | 새 상태(`INPUT_REQUIRED`) 추가 시 같은 경로를 탄다 |

## 7. 참조

- [30-4-9](30-4-9-exit-criteria.md) — W4 완료 정의와 전달 사항
- [30-5-5](30-5-5-design.md) §6 — `message_id` 방침
- [30-5-10](30-5-10-risks.md) — 기준선 없이 교체하는 위험
