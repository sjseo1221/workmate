# M0.3-01 검수 결과

## 1. 기본 정보

- 마일스톤: M0.3 내부 챗봇 API
- 제목: Skill·입력 API
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13 14:42 Asia/Seoul
- 실행 ID: 20260813-144226
- 코드 버전: 로컬 작업 브랜치 `feat/M0.1-01-sdk-runtime`
- 입력 데이터 버전: 승인된 5개 Skill 정의와 기존 Agent Card

## 2. 최신 실행과 승인

- latest_run_id: 20260813-144226
- latest_run_status: PASS
- latest_approved_run_id: 20260813-144226
- approved_at: 2026-08-13 14:42 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: 내부 검증 챗봇에서 공개 5개 Skill을 조회하고 자연어 또는 JSON 입력을 검증한다.
- 완료 기준: 5개 Skill 목록이 Agent Card와 일치하고, 유효한 자연어·JSON 입력을 수락하며, 알 수 없는 Skill·빈 입력·불일치 JSON Skill을 거부한다.
- 백로그 범위: M0.3-01
- 미완료·보류 백로그: 없음

## 4. 구현 경로

- 구현 코드: [`app/internal_chat.py`](../../../../../../workmate-agent/app/internal_chat.py), [`app/main.py`](../../../../../../workmate-agent/app/main.py), [`app/a2a/runtime.py`](../../../../../../workmate-agent/app/a2a/runtime.py)
- Schema 또는 Migration: 해당 없음. M0.3-04에서 승인된 Skill Schema 의미 검증을 연결한다.
- UI 코드: 해당 없음. M0.4 범위다.

## 5. 구현 내용

- `WORKMATE_INTERNAL_CHAT_ENABLED=true`일 때만 내부 API Route를 노출한다. 비활성 상태는 `404`다.
- `GET /api/v1/internal/skill-chat/skills`는 Agent Card와 동일한 5개 Skill 정의를 반환한다.
- `POST /api/v1/internal/skill-chat/messages`는 `skill_id`와 자연어 문자열 또는 JSON 객체를 받는다.
- 빈 자연어, 빈 JSON, 존재하지 않는 Skill, JSON 내부 `skill_id` 불일치를 `422`로 거부한다.
- `approved_skill_definitions()`로 공개 Agent Card와 내부 목록의 Skill 원천을 공유한다.
- 실제 업무 Workflow 호출·Artifact 생성·장기 Task·Session/OIDC 인증은 의도적으로 구현하지 않았으며 각각 M0.3-02~04의 범위다.

## 6. 테스트 파일 경로

- 단위·API 테스트: [`tests/test_internal_chat.py`](../../../../../../workmate-agent/tests/test_internal_chat.py)
- 런타임 회귀 테스트: [`tests/test_runtime_boot.py`](../../../../../../workmate-agent/tests/test_runtime_boot.py)
- Fixture/입력: 테스트 코드 내부의 자연어·JSON 경계 Fixture
- 기대 결과: 4개 내부 API 테스트와 3개 런타임 테스트 PASS
- 모델 평가 Case: 해당 없음
- 모델 평가 결과: 해당 없음

## 7. 실행 명령과 결과

```powershell
cd workmate-agent
.\.venv\Scripts\python.exe -m unittest tests/test_internal_chat.py -v
.\.venv\Scripts\python.exe -m unittest tests/test_runtime_boot.py -v
git diff --check
```

- 내부 API 테스트: 4/4 PASS
- 런타임 회귀 테스트: 3/3 PASS
- `git diff --check`: PASS
- 보조 전체 테스트: 23개 실행, 1개 PostgreSQL 테스트 SKIP (`DATABASE_URL` 미설정). M0.3-01 승인 판정 명령에는 포함하지 않았으며, M0.3-02 이후 DB 연결 검수에서 별도 실행한다.
- 실행 결과에는 실패·경고·미실행이 없으므로 자동 승인 조건을 충족한다.

## 8. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Agent Card와 동일한 5개 Skill 목록 | PASS | `tests/test_internal_chat.py` |
| 자연어 입력 수락 | PASS | `tests/test_internal_chat.py` |
| JSON 입력 수락 | PASS | `tests/test_internal_chat.py` |
| 잘못된 Skill·빈 입력·불일치 Skill 거부 | PASS | `tests/test_internal_chat.py` |
| 비활성 API 404 | PASS | `tests/test_internal_chat.py` |
| 기존 A2A 런타임 회귀 | PASS | `tests/test_runtime_boot.py` |

## 9. 문제와 수정 이력

- 발견된 문제: 테스트 중 생성된 로컬 `.runtime/a2a.sqlite3`가 작업 트리에 생성됨.
- 원인: 기존 A2A 런타임의 Contract Test용 SQLite 기본 경로.
- 수정 내용: 검수 후 생성 산출물을 삭제했으며 코드·증빙에는 포함하지 않았다.
- 재검수 실행 ID: 20260813-144226

## 10. 최종 판단

- 승인 여부: 승인 — 자동 승인(검증 명령)
- 검수 의견: 정의된 M0.3-01 검증 명령과 완료 기준이 모두 정확히 PASS다. 전체 Workflow·장기 Task·인증은 후속 백로그에서 연결한다.
- 다음 조치: M0.3-02 공통 Workflow 호출

