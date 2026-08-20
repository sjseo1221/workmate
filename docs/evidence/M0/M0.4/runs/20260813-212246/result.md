# M0.4-03 UI 통합 재검수 결과

## 1. 기본 정보

- 마일스톤: M0.4 내부 검증 UI
- 백로그: M0.4-03 UI 통합 검수
- 실행일: 2026-08-13 21:22 Asia/Seoul
- 실행 ID: `20260813-212246`
- 코드 버전: `workmate-agent@1ae46d8` 및 현재 작업 트리
- 상태: 재작업
- 검수자: Codex

## 2. 검수 목표

- 5개 Skill 결과·Artifact·상태·오류 표시
- 장기 Task Polling
- `WORKING` Task의 취소 버튼 활성화와 취소 후 `TASK_STATE_CANCELED` 표시
- 다른 사용자 Task 접근 차단

## 3. 구현·테스트 경로

- UI: [`app/internal_chat_ui.py`](../../../../../../workmate-agent/app/internal_chat_ui.py)
- 내부 API: [`app/internal_chat.py`](../../../../../../workmate-agent/app/internal_chat.py)
- Workflow Registry: [`app/workflows/registry.py`](../../../../../../workmate-agent/app/workflows/registry.py)
- 테스트: [`tests/test_internal_chat.py`](../../../../../../workmate-agent/tests/test_internal_chat.py), [`tests/test_internal_chat_ui.py`](../../../../../../workmate-agent/tests/test_internal_chat_ui.py)

## 4. 실행 명령과 결과

```text
cd C:\dev\workmate\workmate-agent
.\.venv\Scripts\python.exe -m unittest tests.test_internal_chat tests.test_internal_chat_ui -v
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

- 내부 API·UI 테스트: 11 PASS
- `WORKING` Fixture 취소 상태 전환: PASS
- 사용자 범위 격리: PASS
- Polling·취소 버튼 상태 제어 코드: PASS
- `compileall`: PASS
- `git diff --check`: PASS
- 운영 경로의 실제 `WORKING` A2A Task 육안 검수: BLOCKED

## 5. 문제와 원인

- 발견된 문제: M1.3 완료 후에도 내부 검증 UI에서 취소 가능한 실제 장기 Task를 만들 수 없다.
- 원인: M1.3의 `/api/v1/tasks`는 업무 Task CRUD 동기 API이며 A2A 장기 Task를 생성하지 않는다. 현재 5개 Skill Workflow도 runtime bootstrap 응답을 즉시 완료한다.
- 기존 계획 오류: `M1.3 완료 → 실제 WORKING Task 제공`이라는 의존 관계가 성립하지 않는다.
- 제외 범위: 육안 검수만을 위해 운영 Runtime에 지연 Mock이나 테스트 Route를 추가하지 않는다.

## 6. 최종 판단

- 승인 여부: 미승인
- 판정: `BLOCKED` 항목이 있으므로 자동 승인과 다음 백로그 진행을 중단한다.
- 재개 조건: 운영 Route와 공개 Schema를 변경하지 않는 테스트 전용 실행 환경에서 유효한 로컬 OIDC JWT와 `WORKING` Task Fixture를 제공하고, 사용자가 취소 버튼 활성화·클릭·`TASK_STATE_CANCELED` 표시를 육안 확인한다.
