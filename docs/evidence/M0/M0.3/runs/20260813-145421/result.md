# M0.3-02 검수 결과

## 1. 기본 정보

- 마일스톤: M0.3 내부 챗봇 API
- 제목: 공통 Workflow 호출
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13 14:54 Asia/Seoul
- 실행 ID: 20260813-145421
- 코드 버전: 로컬 작업 브랜치 `feat/M0.1-01-sdk-runtime`
- 입력 데이터 버전: 승인된 5개 Skill 정의와 기존 A2A Workflow Registry

## 2. 최신 실행과 승인

- latest_run_id: 20260813-145421
- latest_run_status: PASS
- latest_approved_run_id: 20260813-145421
- approved_at: 2026-08-13 14:54 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: 내부 챗봇 API가 A2A와 동일한 `WorkflowRegistry`·`WorkflowRequest` 경계를 호출하도록 연결한다.
- 완료 기준: 내부 자연어·JSON 요청이 공유 Registry를 통해 실행되고, Workflow 결과의 상태·Artifact·warnings를 응답한다.
- 백로그 범위: M0.3-02
- 미완료·보류 백로그: 없음

## 4. 구현 경로

- 구현 코드: [`app/internal_chat.py`](../../../../../../workmate-agent/app/internal_chat.py), [`app/a2a/runtime.py`](../../../../../../workmate-agent/app/a2a/runtime.py)
- Schema 또는 Migration: 해당 없음
- UI 코드: 해당 없음. M0.4 범위다.

## 5. 구현 내용

- `build_runtime_routes()`가 생성한 단일 `WorkflowRegistry`를 런타임 전역 경계로 보관한다.
- 내부 챗봇 메시지 Route는 입력을 `WorkflowRequest`로 변환하고 같은 Registry를 비동기로 호출한다.
- 응답에 `task_id`, Workflow `state`, Artifact 요약, `warnings`를 포함한다.
- `thread_id`와 `task_id`는 요청 단위로 연결했으며, 장기 Task 영속화·Polling·취소는 M0.3-03에서 구현한다.
- 현재 Registry의 런타임 준비 Workflow는 경계 검증용이며, 실제 Gmail·Calendar·업무 DB Workflow 결과를 완료했다고 주장하지 않는다.

## 6. 테스트 파일 경로

- 내부 API 테스트: [`tests/test_internal_chat.py`](../../../../../../workmate-agent/tests/test_internal_chat.py)
- A2A 런타임 회귀: [`tests/test_runtime_boot.py`](../../../../../../workmate-agent/tests/test_runtime_boot.py)
- 공개 A2A Contract Test: [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py)
- Fixture/입력: 내부 자연어·JSON 요청과 기존 5개 A2A Skill Fixture
- 기대 결과: 내부 API 4개, 런타임 3개, 공개 Contract 10개 테스트 PASS

## 7. 실행 명령과 결과

```powershell
cd workmate-agent
.\.venv\Scripts\python.exe -m unittest tests/test_internal_chat.py tests/test_runtime_boot.py tests/test_contract.py -v
git diff --check
```

- 테스트: 17/17 PASS
- `git diff --check`: PASS
- 미실행·경고·보류·차단: 없음
- 실행 후 생성된 Contract Test용 `.runtime/a2a.sqlite3`는 삭제했으며 커밋하지 않았다.

## 8. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| 내부 입력이 공유 Workflow Registry를 호출 | PASS | `tests/test_internal_chat.py` |
| Workflow 상태·Artifact 응답 | PASS | `tests/test_internal_chat.py` |
| A2A 런타임 회귀 | PASS | `tests/test_runtime_boot.py` |
| 공개 A2A Contract 회귀 | PASS | `tests/test_contract.py` |
| 변경 범위 diff 검사 | PASS | 실행 ID `20260813-145421` |

## 9. 문제와 수정 이력

- 발견된 문제: 없음
- 원인: 해당 없음
- 수정 내용: 해당 없음
- 재검수 실행 ID: 해당 없음

## 10. 최종 판단

- 승인 여부: 승인 — 자동 승인(검증 명령)
- 검수 의견: 정의된 검증 명령과 완료 기준이 모두 정확히 PASS하여 M0.3-02를 자동 승인했다. M0.3 전체는 M0.3-03·04와 통합 검수 전까지 `진행`으로 유지한다.
- 다음 조치: M0.3-03 장기 Task API

