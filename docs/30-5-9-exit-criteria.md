# W5-9 — 완료 정의

> [30-5-w5-entrypoint-swap.md](30-5-w5-entrypoint-swap.md) §9의 상세 문서.

## 1. 완료 조건 (Exit criteria)

| # | 조건 | 판정 근거 |
| --- | --- | --- |
| E-1 | 운영 경로 3곳이 전부 Graph를 호출한다. `grep -rn "workflow_registry" app/`이 비어 있다 | W5-V1-3 |
| E-2 | **W5-V2(이벤트 순서)·V5(오류 매핑)·V6(Route allowlist) PASS** | 각 검증 |
| E-3 | **W5-V7(운영 경로 스냅샷) 전건 PASS** | W5-V7 |
| E-4 | 로컬 실제 HTTP 확인 7항목 완료 | W5-T9 |
| E-5 | W5-V4(비동기 경로) PASS — 특히 V4-6(방어적 예외 처리) | W5-V4 |

### 1.1 E-2를 따로 세운 이유

이벤트 순서와 오류 매핑은 **실사용 중 발견돼 고친 회귀**다([30-5-8](30-5-8-traceability.md) §6).
다른 검증이 전부 통과해도 이 둘이 깨지면 W5는 실패다.

| 검증 | 막는 회귀 |
| --- | --- |
| W5-V2 | 2026-08-14 Orchestrator가 빈 결과를 읽음 |
| W5-V5 | 2026-08-15 브라우저가 `Failed to fetch`만 봄 |
| W5-V6 | 비공개 Route 노출(`AGENTS.md` 규칙) |

### 1.2 E-4가 필수인 이유

단위 테스트는 미들웨어 체인을 거치지 않는다. 2026-08-15 사고가 정확히 그런 경우였다 — 예외가
`CORSMiddleware` **바깥**의 `ServerErrorMiddleware`까지 올라가 CORS 헤더 없는 500이 됐다. 단위
테스트에서는 예외 타입만 보고 "정상"이라 판정한다.

**W5는 실제 HTTP 확인 없이 완료할 수 없다.**

### 1.3 `module` 제거는 W7

E-1은 `app/` 안에 **호출**이 없음을 요구한다. `app/workflows/` 파일 자체는 W7까지 남는다. W5 시점에는
비교 대상으로 존재해야 한다.

## 2. 산출물 체크리스트

### 2.1 코드

```
[ ] app/main.py                Checkpointer lifespan 결합
[ ] app/a2a/runtime.py         Executor 교체, save_checkpoint 호출 제거
[ ] app/internal_chat.py       동기 경로 교체
[ ] app/internal_chat.py       비동기 경로 교체
```

### 2.2 테스트

```
[ ] tests/test_runtime_boot.py     이벤트 순서 (계승·보강)
[ ] tests/test_internal_chat.py    오류 매핑·비동기 (계승·보강)
[ ] 스냅샷 하네스의 운영 경로 모드
```

### 2.3 확인 기록

```
[ ] 로컬 HTTP 확인 7항목 결과
[ ] Graph 예외 전파 확인 결과
[ ] message_id 비대칭 기록 (W5-D3)
```

### 2.4 문서·증빙

```
[ ] docs/evidence/langgraph/W5/runs/{run_id}/result.md
[ ] docs/evidence/langgraph/README.md   W5 행
[ ] HANDOFF.md
```

## 3. 승인 절차

### 3.1 자동 승인 대상 여부

| 조건 | W5 해당 여부 |
| --- | --- |
| 외부 OAuth·실제 Provider 호출 | **없음** — 로컬 HTTP 확인은 Fake 기반 |
| 공개 Schema 변경 | 없음 |
| **공개 동작 변경** | **W4-D1 멱등성이 여기서 실제로 노출된다** |
| UI 육안 검수 | **없음** — UI 응답 형태가 그대로이므로 |
| 원격 Push | 없음 |

→ 원칙적으로 자동 승인 대상이다. 단 §3.2.

### 3.2 W5가 W4와 다른 점

W4에서는 멱등성 변경이 Graph 내부에만 있었다. **W5부터는 외부가 관찰한다.**

| 시점 | 같은 `message_id` 재전송 |
| --- | --- |
| W4까지 | 재실행됨(운영 경로는 Registry) |
| **W5 이후** | **재실행되지 않음** |

이것이 W5에서 처음 발생하는 **사용자 관찰 가능 변경**이다. 자동 승인하더라도 증빙에 명시하고
사용자에게 보고한다.

만약 오케스트레이터가 HTTP 재시도 시 같은 `message_id`를 보낸다면, 이 변경이 그쪽 동작에 영향을
준다. W5-T9의 로컬 확인에서 응답 형태를 기록해 두면 W6의 어댑터 검토에서 쓸 수 있다.

### 3.3 자동 승인 시 기록

```
latest_run_id:          {run_id}
latest_run_status:      PASS
latest_approved_run_id: {run_id}
approved_at:            {날짜} Asia/Seoul
reviewer:               자동 승인(검증 명령)
자동 재작업 착수:        예/아니오
자동 진행 판정:          진행 — W6 자동 착수
운영 경로:              Root Graph (전환 완료 시점)
사용자 관찰 가능 변경:   멱등성(W4-D1)이 이 시점부터 노출
로컬 HTTP 확인:         7항목 완료
```

### 3.4 자동 승인이 불가한 경우

| 상황 | 처리 |
| --- | --- |
| **W5-V2 또는 V5 FAIL** | **W6 진행 금지.** 과거 회귀의 재발 |
| 로컬 HTTP 확인 미수행 | 완료 불가(E-4) |
| 기존 테스트가 §2의 "그 외" 유형으로 깨짐 | 회귀. 원인 조사 |
| 오케스트레이터 동작에 영향이 우려됨 | 보고 후 판단 |

## 4. 완료 후 상태

| 항목 | W5 완료 시점 |
| --- | --- |
| **운영 경로** | **Root Graph** ← 전환의 분기점 |
| `app/workflows/` | 파일은 남아 있으나 **호출되지 않음** |
| `a2a_checkpoints` | **아무도 쓰지 않음** (W7 DROP 대기) |
| 공개 응답 모양 | 변경 없음 |
| 공개 동작 | 멱등성만 변경 |
| 확인 흐름 | 아직 `pending_action` 방식 |
| 롤백 비용 | **중간** — 운영 경로가 바뀌었다 |

### 4.1 이 시점의 의미

전환의 목표("실행 경로는 하나")가 실질적으로 달성된 상태다. 남은 것은

| 단계 | 내용 |
| --- | --- |
| W6 | 확인 흐름 개편(공개 계약) |
| W7 | 죽은 코드 정리 |
| W8 | 운영 품질 |
| W9 | 문서·판정 |

## 5. 완료 판정 체크리스트

```
[ ] 1. W5-V1  A2A 경로 (11개 Skill + 멱등성 재전송)
[ ] 2. W5-V2  이벤트 순서 4종 + Artifact Part 내용
[ ] 3. W5-V3  UI 동기 응답 구조
[ ] 4. W5-V4  UI 비동기 (특히 V4-3 warnings, V4-6 방어)
[ ] 5. W5-V5  오류 매핑 422/503 + CORS 헤더
[ ] 6. W5-V6  Route allowlist
[ ] 7. W5-V7  운영 경로 스냅샷 전건 PASS
[ ] 8. W5-V8  thread_id 규칙 3경로
[ ] 9. W5-V9  Checkpointer 수명
[ ] 10. W5-V10 전체 회귀 (깨진 테스트는 3유형으로 분류)
[ ] 11. 로컬 HTTP 확인 7항목
[ ] 12. grep -rn "workflow_registry" app/ → 출력 없음
[ ] 13. git diff --check, Secret 검사
[ ] 14. result.md, evidence README, HANDOFF
[ ] 15. 자동 승인 판정 후 W6 착수
```

## 6. 다음 단계 전달 사항

| 전달 항목 | 받는 단계 | 용도 |
| --- | --- | --- |
| 운영 경로가 Graph | [W6](30-6-w6-interrupt-resume.md) | `interrupt`를 넣을 대상 |
| 오류 매핑 유지 확인 | W6 | `INPUT_REQUIRED`도 같은 경로 |
| 비동기 폴링 구조 | W6 | 분기 추가 지점 |
| W5-V7 결과 | W6 | 변경 전 기준선 |
| `workflow_registry()` 호출 부재 | [W7](30-7-w7-legacy-removal.md) | 삭제 전제 |
| `save_checkpoint` 미사용 | W7 | DROP 전제 |
| 예외 전파 확인 결과 | [W8](30-8-w8-retry-observability.md) | RetryPolicy 적용 후 재확인 |
| `message_id` 비대칭 | [W9](30-9-w9-docs-evidence.md) | 후속 백로그 |
| 오케스트레이터 영향 기록 | W6 | 어댑터 검토 |

## 7. 참조

- [30-5-7](30-5-7-verification.md) — 검증 항목
- [30-5-8](30-5-8-traceability.md) §6 — 과거 회귀 매핑
- [30-5-11](30-5-11-rollback.md) — 완료하지 못했을 때
