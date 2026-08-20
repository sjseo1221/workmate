# M1.5-04 검수 결과

## 1. 기본 정보

- 마일스톤: M1.5
- 제목: 오늘 브리핑 Workflow
- 담당자: Codex
- 검수자: 미승인 — 실제 OAuth Provider 실행 필요
- 상태: 검수 중
- 실행일: 2026-08-13
- 실행 ID: 20260813-222752

## 2. 최신 실행과 승인

- latest_run_id: 20260813-222752
- latest_run_status: PASS (Adapter Fixture 기준)
- latest_approved_run_id: 20260813-222105
- approved_at: 2026-08-13 22:21 Asia/Seoul (M1.5-03)

## 3. 목표와 완료 기준

- 목표: 오늘 일정, Gmail 신호, 결정적 Task Top 3를 하나의 `daily_briefing` Artifact로 반환한다.
- 완료 기준: Calendar/Gmail 부분 실패 시 `warnings`와 부분 결과를 반환하고, 승인 Skill Schema를 통과하며, 실제 OAuth Provider에서도 재현한다.
- 미완료·보류: 실제 OAuth Provider 실행. 현재 `WORKMATE_GOOGLE_ACCESS_TOKEN` 미설정.

## 4. 구현 경로

- 구현 코드: [`app/workflows/daily_briefing.py`](../../../../../../workmate-agent/app/workflows/daily_briefing.py), [`app/a2a/runtime.py`](../../../../../../workmate-agent/app/a2a/runtime.py)
- Schema: [`docs/schemas/workmate-skill-schemas.schema.json`](../../../../../schemas/workmate-skill-schemas.schema.json)
- UI 코드: 해당 없음

## 5. 테스트 파일 경로

- 단위·Workflow 테스트: [`tests/test_daily_briefing.py`](../../../../../../workmate-agent/tests/test_daily_briefing.py)
- Adapter 회귀 테스트: [`tests/test_google_adapters.py`](../../../../../../workmate-agent/tests/test_google_adapters.py)
- Contract 테스트: [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py)
- Fixture/입력: Fake Gmail·Calendar Adapter와 SQLite Task Fixture
- 모델 평가·UI 테스트: 해당 없음

## 6. 실행 명령과 결과

```text
.\.venv\Scripts\python.exe -m unittest tests.test_daily_briefing tests.test_priority_workflow tests.test_priority_repository tests.test_priority_domain tests.test_google_adapters tests.test_contract -q
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

- 결과: 30개 테스트 PASS, compileall PASS, diff check PASS
- 검증된 동작: 일정·메일 신호·Top 3 통합, `mock=false`, Provider 부분 실패 `warnings`, 승인 Schema Envelope
- 실제 Provider: 미실행. 토큰·Secret은 증빙에 기록하지 않음

## 7. 검수 항목

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| 오늘 범위 Calendar 이벤트 정규화 | PASS | `tests/test_daily_briefing.py` |
| Gmail 신호 정규화 | PASS | `tests/test_daily_briefing.py` |
| Top 3 통합 및 사용자 범위 | PASS | `app/workflows/priority.py`, Workflow 테스트 |
| Provider 부분 실패·`warnings` | PASS | `tests/test_daily_briefing.py` |
| 승인 Schema·Contract 회귀 | PASS | `tests/test_daily_briefing.py`, `tests/test_contract.py` |
| 실제 OAuth Provider 실행 | 보류 | `WORKMATE_GOOGLE_ACCESS_TOKEN` 미설정 |

## 8. 문제와 수정 이력

- 발견된 문제: 현재 환경에 Workmate용 Google access token이 설정되어 있지 않아 실시간 Provider 호출을 실행할 수 없다.
- 원인: 운영 Secret을 저장소나 증빙에 기록하지 않는 정책과 런타임 토큰 미주입.
- 수정 내용: `AuthorizedSession` 기반 런타임 자격 증명 주입 경로와 Provider 장애 부분 결과를 구현하고, Fake Adapter로 계약을 검증했다.
- 재검수 조건: 토큰을 환경 변수로 주입한 뒤 Gmail unread 조회·Calendar 오늘 범위 조회·부분 실패 응답을 실제 Provider로 재실행.

## 9. 최종 판단

- 승인 여부: 보류
- 검수 의견: 구현 및 자동화된 검증은 PASS지만, 외부 OAuth Provider 실행은 사람의 권한·Secret 설정이 필요한 예외 항목이므로 자동 승인하지 않는다.
- 다음 조치: 실제 OAuth Provider 검수 승인 후 M1.5-04를 재실행하고, 통과하면 M1.5-05 통합 검수로 이동한다.
