# Workmate AI 개발 인수인계

이 문서는 저장소의 현재 작업 상태와 다음 착수 항목을 기록한다. 전체 개발 계획은 [`docs/06-delivery-plan.md`](docs/06-delivery-plan.md), 하위 마일스톤의 검수 결과는 `docs/evidence/Mx/Mx.y/result.md`를 기준으로 한다.

## 1. 현재 상태

- 현재 트랙: LangGraph 전면 전환 (`docs/30-langgraph-migration-plan.md`)
- 진행 중 단계: W0 완료, **다음 착수 항목은 W1 계약 스냅샷 추출**
- 선행 마일스톤: M0~M5 구현 완료 (M2.4 육안 검수는 사용자 보류 상태 유지)
- 상태: 진행 — 구현·문서·증빙을 원격 Push 완료, W1 미착수
- 마지막 갱신: 2026-11-03 Asia/Seoul
- 마지막 작업자: Claude
- 기준 Git Commit: `8043c1e` (`workmate-agent`), `c4ea51d` (`workmate-ui`)
- 기준 브랜치: `feat/M0.1-01-sdk-runtime` (Superproject·`workmate-agent`), `main` (`workmate-ui`)

## 2. 완료된 항목

| 항목 | 상태 | 승인 증빙 |
|---|---|---|
| M0.1-01 SDK HTTP+JSON 런타임 부트스트랩 | 완료 | `docs/evidence/M0/M0.1/runs/20260812-210001/result.md` |
| M0.1-02 공개 A2A 전송 타입 Contract Test | 완료 | `docs/evidence/M0/M0.1/runs/20260812-204500/result.md` |
| M0.1-03 Workflow·영속 Task 경계 구현 | 완료 | `docs/evidence/M0/M0.1/runs/20260812-224743/result.md` |
| M0.1-04 통합 A2A 계약 검수 | 완료 | `docs/evidence/M0/M0.1/runs/20260812-230413/result.md` |
| M0.2-01 LLM 평가 승인 | 완료 | `docs/evidence/M0/M0.2/runs/20260813-093322/result.md` |
| M0.2-02 Embedding 평가 승인 | 완료 | `docs/evidence/M0/M0.2/runs/20260813-134129/result.md` |
| M0.2-03 STT 평가 승인 | 완료 | `docs/evidence/M0/M0.2/runs/20260813-134542/result.md` |
| M0.2-04 Gmail OAuth 승인 | 완료 | `docs/evidence/M0/M0.2/runs/20260813-134915/result.md` |
| M0.2 통합 검수 | 완료 | `docs/evidence/M0/M0.2/runs/20260813-135158/result.md` |
| M0.2-05 Calendar OAuth 승인 | 완료 | `docs/evidence/M0/M0.2/runs/20260813-131903/result.md` |
| M0.3-01 Skill·입력 API | 완료 | `docs/evidence/M0/M0.3/runs/20260813-144226/result.md` |
| M0.3-02 공통 Workflow 호출 | 완료 | `docs/evidence/M0/M0.3/runs/20260813-145421/result.md` |
| M0.3-03 장기 Task API | 완료 | `docs/evidence/M0/M0.3/runs/20260813-150133/result.md` |
| M0.3-04 인증·Schema·부분 실패 | 완료 | `docs/evidence/M0/M0.3/runs/20260813-153001/result.md` |
| M0.4-02 결과·상태 UI | 완료 | `docs/evidence/M0/M0.4/runs/20260813-161223/result.md` |
| M0.4-03 UI 통합 검수 | 완료 | `docs/evidence/M0/M0.4/runs/20260813-213733/result.md` |
| M0.4 내부 검증 UI | 완료 | `docs/evidence/M0/M0.4/README.md` |
| M1.4 Task 제안 | 완료 | `docs/evidence/M1/M1.4/runs/20260813-215728/result.md` |
| M1.5-01 점수 Domain·시간 경계 | 완료 | `docs/evidence/M1/M1.5/runs/20260813-221012/result.md` |
| M1.5-02 PrioritySnapshot 저장 경계 | 완료 | `docs/evidence/M1/M1.5/runs/20260813-221527/result.md` |
| M1.5-03 rank_priorities Workflow/API | 완료 | `docs/evidence/M1/M1.5/runs/20260813-222105/result.md` |
| M1.5-04 실제 Provider daily_briefing | 완료 | `docs/evidence/M1/M1.5/runs/20260813-224808/result.md` |
| M1.5-05 통합·회귀 검수 | 완료 | `docs/evidence/M1/M1.5/runs/20260813-225921/result.md` |

완료 항목은 명시 승인 또는 규칙에 따른 묵시 승인이 기록된 `result.md` 경로만 연결한다. 자동 승인 조건을 충족하지 않은 단순 구현 완료나 일부 테스트 실행만으로 완료 처리하지 않는다.

## 3. 현재 진행 중인 작업

- 백로그 ID: M2.4-03 UI 자동 테스트·육안 검수
- 작업: `/weekly-report` 구현과 집중 테스트 11개 PASS
- 담당자: Codex
- 구현 중인 파일: `workmate-agent/app/weekly_report_ui.py`, `workmate-agent/tests/test_weekly_report_ui.py`
- 완료된 부분: M0.1~M0.4, M1.1~M1.5 데이터·우선순위·브리핑
- 남은 부분: 사용자가 나중에 `docs/13-manual-verification-guide.md`의 M2.4-03 절차를 수행하고 승인
- 현재 테스트 결과: UI·Artifact·내부 API 집중 테스트 11개 PASS·0 SKIP, compileall·git diff --check PASS
- 마지막 실행 명령: `python -m unittest discover -s tests -v`, `python -m compileall -q app tests`, `git diff --check`
- 최신 실행 ID: `20260814-071500` (M2.4 자동 테스트)
- 자동 진행 판정: UI 자동 테스트는 PASS했으나 육안 검수는 사용자 판단이 필요해 승인 보류
- 자동 진행 보류 사유: 사용자가 M2.4 육안 검수를 나중에 수행하기로 결정
- 다음 착수 조건: [`M2.4-03 수동 검수 절차`](docs/13-manual-verification-guide.md#2-m24-03-주간-보고서-ui-육안-검수)에 따른 사용자 PASS/FAIL 판정
- 최신 승인 실행 ID: `20260812-210001` (M0.1-01), `20260812-212244` (M0.1-02), `20260813-093322` (M0.2-01), `20260813-134129` (M0.2-02 재검수), `20260813-134542` (M0.2-03 재검수), `20260813-134915` (M0.2-04 재검수), `20260813-131903` (M0.2-05), `20260813-135158` (M0.2 통합), `20260813-144226` (M0.3-01), `20260813-145421` (M0.3-02), `20260813-150133` (M0.3-03), `20260813-153001` (M0.3-04), `20260813-160540` (M0.4-01), `20260813-161223` (M0.4-02), `20260813-213733` (M0.4-03), `20260813-214548` (M0 통합), `20260813-170714` (M1.1-01), `20260813-192221` (M1.1-02), `20260813-193615` (M1.1-03), `20260813-193901` (M1.1-05), `20260813-194043` (M1.1-04), `20260813-194801` (M1.2), `20260813-215728` (M1.4), `20260813-221012` (M1.5-01), `20260813-221527` (M1.5-02), `20260813-222105` (M1.5-03), `20260813-224808` (M1.5-04), `20260813-225921` (M1.5-05), `20260813-231130` (M2.1-01), `20260813-231401` (M2.1-02), `20260813-231904` (M2.1-03), `20260813-232223` (M2.1-04), `20260813-232437` (M2.1-05), `20260813-232643` (M2.1-06), `20260813-233115` (M2.2-01), `20260813-235246` (M2.2-02)

## 4. 다음 작업

1. M2.3-01 주간 보고 입력 조립·LLM 생성 Workflow 구현

M1.5-05 실행 `20260813-225921`은 PostgreSQL 통합 5개와 기존 M0/M1 회귀 80개가 모두 PASS하여 자동 승인 처리했다. M2.1-01 실행 `20260813-231130`, M2.1-02 실행 `20260813-231401`, M2.1-03 실행 `20260813-231904`, M2.1-04 실행 `20260813-232223`, M2.1-05 실행 `20260813-232437`, M2.1-06 실행 `20260813-232643`, M2.2-01 실행 `20260813-233115`은 정의된 검증 명령이 모두 PASS하여 자동 승인했다. M2.2-02 실제 Provider 평가 `20260813-234838`은 20건 실행·Schema·의미 검증이 모두 PASS했고, 사용자 승인으로 수동 의미 검수 `20260813-235246`도 PASS하여 완료 처리했다. M2.3-01~04의 구현 계획과 완료 조건을 `docs/06-delivery-plan.md`와 `docs/evidence/M2/M2.3/README.md`에 정의했다.

## 5. 차단 사항

| 항목 | 원인 | 필요한 조치 | 해소 상태 |
|---|---|---|---|
| Docker Compose 검증 환경 | Dockerfile의 지원되지 않는 `uv sync --system` 옵션 | `--system` 제거, `.venv` PATH 연결 후 이미지 빌드·기동·Health·Agent Card 재검수 PASS | 해소 |
| 루트 문서 Git 추적 | Superproject·Submodule·원격 기준선 필요 | `origin/main`에 기준 Commit Push 완료 | 해소 |
| PostgreSQL·최종 Docker 재검수 | Docker CLI 응답 지연으로 최초 검증 보류 | 격리 PostgreSQL 연결·최종 이미지 build/Health/Agent Card 재검증 PASS | 해소 |

실제 회의 음성 평가, R2 Lifecycle, 운영 부하·복구, 실제 Orchestrator 종단 간 검증은 현재 M0.1의 차단 사항이 아니다. 각각 M3.3, M3.6, M5.2~M5.4 완료 조건으로 추적한다.

## 6. 중요한 결정

- Task 원장: Workmate PostgreSQL
- 삭제 방식: Task는 Soft Delete
- Gmail 원본 식별자: Gmail `message.id`
- 우선순위 계산 규칙: PostgreSQL에 승인·저장된 Task만 결정적으로 계산하며 계산 중 Gmail API를 호출하지 않음
- LLM 책임: Task 순위와 근거 ID를 생성하거나 변경하지 않음
- Embedding: `openai/text-embedding-3-small`, 1536차원, Cosine, Dense + Trigram RRF + HNSW
- STT: `gpt-4o-transcribe`, 파일 기반·Realtime Streaming MVP
- A2A·Artifact Schema: A2A 1.0 HTTP+JSON, `a2a-sdk[http-server]==1.1.2`, 승인된 `docs/schemas/` 사용
- A2A Route 공개 범위: `POST /a2a/tasks/{task_id}:subscribe`를 정식 Subscribe 계약으로 사용하고 SDK 추가 Route는 MVP allowlist 밖에서 `404` 또는 `405`로 차단
- 장기 Task 저장: PostgreSQL Task Store와 LangGraph Checkpoint를 `task.id ↔ thread_id`로 연결하고 프로세스 메모리를 원장으로 사용하지 않음
- Migration 책임: M0.1은 A2A Task·Message 멱등성·Artifact·`task_id ↔ thread_id`·Checkpoint 인프라, M1.1은 Task·Gmail·Calendar 업무 도메인을 담당. 공개 이벤트 전체 이력은 MVP에서 저장하지 않음
- Python 의존성: `pyproject.toml`과 `uv.lock`을 단일 원장으로 사용하고 `requirements.txt`는 필요할 때만 생성형 호환 산출물로 유지
- UI 책임: M0.4 내부 검증 UI는 `workmate-agent`가 제공하는 최소 개발자 페이지다. `workmate-ui`는 1차로 완성해 개인용으로 보관하고, 2차로 완성된 화면·로직을 팀 공통 Orchestrator UI 양식에 맞게 조정해 M5 통합에 반영한다(2026-08-15 결정 번복, 이전 "폐기된 샘플" 방침 대체).
- Agent Card Cache: MVP는 `Cache-Control: public, max-age=3600`만 계약으로 유지하고 별도 `ETag`는 요구가 생길 때 추가
- Streaming·Subscribe: `/message:stream` 첫 Task와 후속 상태·Artifact 순서, 활성 Task Subscribe의 현재 Snapshot·신규 이벤트, Terminal Task 오류, 비허용 `GET` Route 차단을 검증
- Mock 응답: 운영 실행 경로에는 Mock Handler·고정 샘플 응답·Mock fallback을 두지 않고 Mock 여부는 단위·계약 테스트의 Fixture·로그·증빙에만 기록
- Git 구조: `C:\dev\workmate`는 문서·증빙 Superproject, `workmate-agent`만 기존 이력을 보존한 Submodule로 관리한다. `workmate-ui`는 1차 완성 후 개인용 보관·2차 Orchestrator UI 이식 대상으로 결정이 바뀌어 더 이상 추적 제외 대상이 아니다 — Superproject 편입 방식(Submodule 등록 vs 일반 추적)은 별도 확정 필요. 별도로 존재했던 `workmate-ui`(독립 정적 HTML/JS UI)는 혼란을 피하기 위해 폐기하고 삭제했다.
- Submodule 기준: `workmate-agent` `fdddd221174fce0340a49b068d5fe005ce550b9a`; 기존 README 문서 변경은 `stash@{0}`에 보존
- 마일스톤 진입: 명시된 선행 조건이 있는 후속 백로그는 조건 완료 전 구현·검수를 시작하지 않음. 선행 조건이 없는 M0.2 이력 검수는 M0.1과 병행 가능

결정 변경 시 관련 설계 문서와 `docs/evidence/`의 검수 결과를 함께 갱신한다.

## 7. 실행 방법

- 개발 환경 실행: `cd workmate-agent; uv sync --frozen; uv run uvicorn app.main:app --host 0.0.0.0 --port 8001`
- Migration: M0.1-03에서 A2A 인프라 Migration, M1.1에서 업무 도메인 Migration 도구와 명령을 각각 확정
- 단위 테스트: `cd workmate-agent; uv run python -m unittest discover -s tests -v`
- 통합 테스트: M0.1-04 착수 시 A2A Contract Test 명령 확정
- 전체 Smoke Test: M5.3 착수 시 Docker Compose 명령 확정
- 종료 방법: 실행 방법과 함께 같은 백로그에서 확정

실행 명령은 실제 작업 환경에서 재현 가능한 형태로 기록한다. Secret, API Key, Token, Presigned URL은 기록하지 않는다.

## 8. 검수·증빙 경로

- 구현 코드: [`workmate-agent/app/internal_chat.py`](workmate-agent/app/internal_chat.py), [`workmate-agent/app/main.py`](workmate-agent/app/main.py), [`workmate-agent/app/a2a/runtime.py`](workmate-agent/app/a2a/runtime.py)
- Schema 또는 Migration: `docs/schemas/a2a-artifact.schema.json`, `docs/schemas/workmate-skill-schemas.schema.json`; A2A 인프라 Migration은 M0.1-03에서 생성 예정
- 단위 테스트: [`workmate-agent/tests/test_internal_chat.py`](workmate-agent/tests/test_internal_chat.py), [`workmate-agent/tests/test_runtime_boot.py`](workmate-agent/tests/test_runtime_boot.py)
- 통합 테스트: M0.1-04에서 생성 예정
- UI 테스트: M0.4에서 생성 예정
- Fixture/입력: M0.1-04에서 승인 Schema를 통과하는 5개 Skill Fixture 생성 예정
- 모델 평가 Case: `llm-evaluation/cases/`의 Pilot·Full Case 1·2 연결 완료
- 모델 평가 결과: `docs/evidence/M0/M0.2/runs/20260813-093322/result.md` (M0.2-01 완료), `docs/evidence/M0/M0.2/runs/20260813-114046/result.md` (M0.2-02 완료), `docs/evidence/M0/M0.2/runs/20260813-121052/result.md` (M0.2-03 완료)
- 최신 실행 로그: `docs/evidence/M0/M0.3/runs/20260813-144226/result.md`
- 최신 실행 결과: M0.3-01의 정의 검증 명령과 검수 항목이 모두 정확히 PASS하여 자동 승인·완료 처리. 전체 PostgreSQL 테스트의 1개 SKIP은 M0.3-01 범위 밖이며 M0.3-02 이후 별도 검수한다.
- 최신 결과 문서: `docs/evidence/M0/M0.3/README.md`

## 9. 주의사항

- 실제 Secret을 Git에 저장하지 않는다.
- 승인된 Artifact Schema를 임의로 변경하지 않는다.
- Schema 변경 시 A2A Contract Test를 함께 수정한다.
- 이전 검수 결과를 덮어쓰거나 삭제하지 않는다.
- 실패 실행은 `docs/evidence/Mx/Mx.y/runs/{run_id}/`에 보존한다.
- `latest_run_id`와 `latest_approved_run_id`를 구분해 기록한다.
- 실행 결과의 구현·Schema·Migration·UI·테스트 경로는 저장소 파일로 이동하는 Markdown 링크로 기록하고, 삭제 파일은 삭제 사실과 대체 검증 경로만 남긴다.

## 10. 커밋·Push 인수인계 규칙

- `기준 Git Commit`은 이 인수인계 시점에 테스트와 증빙을 확인한 마지막 커밋을 기록한다.
- 작업 브랜치와 Pull Request 주소 또는 식별자를 기록하고, 기준 브랜치에 직접 Push하지 않는다.
- 구현·테스트·증빙 커밋을 구분해 주요 커밋 ID와 내용을 남긴다.
- 백로그 완료 시에는 로컬 커밋만 남기고, 하위 마일스톤의 모든 백로그와 통합 완료 기준이 승인된 시점에 한 번에 Push한다.
- 인수인계·원격 협업, 장기간 작업의 원격 백업, 사용자 명시 요청이 있을 때만 중간 Push한다. 테스트 PASS·증빙·상태 변경만으로 Push하거나 승인 여부를 묻지 않는다.
- Push 전 `git diff --check`, 변경 범위 테스트, Schema·Contract Test, Secret 검사를 수행한다.
- 검수 전 상태는 `진행` 또는 `검수 중`으로 기록하고, `latest_approved_run_id` 승인 전에는 완료로 표시하지 않는다.
- 자동 승인 대상에서 정의된 검증 명령과 검수 항목이 전부 정확히 PASS이고 미실행·수동 검수·차단 항목이 없으면 `자동 승인(검증 명령)`으로 묵시 승인하고 계획표·증빙·HANDOFF를 완료로 갱신한다. 공개 Schema·데이터 모델 변경과 외부 OAuth·UI·모델 평가처럼 명시 승인이 필요한 항목은 자동 승인하지 않는다.
- PASS가 아닌 결과가 하나라도 나오면 자동 승인과 정규 다음 백로그를 중단하고 `latest_approved_run_id`를 유지한다. 실패 항목·재현 명령·재개 조건·남은 재시도 후보를 기록하며, 원인이 명확하고 안전한 미실행 해결 방법이 남아 있으면 해당 재작업·재검수를 자동 수행한다.
- 자동 승인된 실행은 별도 진행 질문 없이 `다음 작업` 백로그를 즉시 착수한다. 외부 OAuth·실제 Provider·공개 Schema·데이터 모델·UI 육안 검수·모델 평가·원격 Push처럼 명시 승인이 필요한 작업은 예외로 사용자 승인을 기다린다.
- 자동으로 다음 작업을 착수하지 않은 경우에는 `자동 진행 보류 사유`, 관련 검증 결과, 미실행·수동 검수·차단 항목, 필요한 승인 또는 조치, 재개 조건을 이 문서와 실행 `result.md`에 기록하고 사용자에게 보고한다.
- 자동 다음 작업 미실행 사유가 `재작업`이면 정규 후속 백로그가 아니라 기록된 재작업·재검수 백로그를 자동 착수한다. 재검수도 실패하면 서로 다른 미실행 해결 방법을 후보별로 한 번씩 자동 수행하고, 동일 원인 반복·후보 소진·새 사용자 입력 필요 시 중단한다. 이미 승인된 외부 Provider 검수의 동등 범위 명령 수정은 자동 재시도할 수 있지만 새 Scope·계정·Secret·외부 부작용은 다시 승인을 기다린다. 재작업 재검수가 모두 정확히 `PASS`가 된 뒤에만 정규 다음 백로그로 진행한다.
- `다음 작업`에 문제 해결용 재작업·재검수 항목이 지정된 경우에는 정규 후속 백로그보다 먼저 자동 착수한다. 로컬 코드·테스트·환경 보정이고 별도 승인이 필요 없으면 사용자 질문 없이 실행하며, 재작업이 정확히 `PASS`가 된 뒤에만 정규 다음 백로그로 전환한다.
- 자동 착수 허용 경로는 두 가지다: 모든 검수 결과가 정확히 `PASS`인 정상 진행은 정규 다음 백로그를 자동 착수하고, `재작업` 상태는 기록된 로컬 재작업·재검수 백로그를 먼저 자동 착수한다. 재작업 재검수가 모두 `PASS`가 되면 정규 다음 백로그로 자동 전환한다. 외부 OAuth·실제 Provider·공개 Schema·데이터 모델·UI 육안 검수·모델 평가·원격 Push는 항상 사용자 또는 검수자 승인을 기다린다.
- 진행 기록에는 `자동 재작업 착수: 예/아니오`를 함께 남겨 재작업 자동 착수 여부를 구분한다.
- API Key, Token, Presigned URL, 실제 회의 음성은 커밋·Push하지 않는다.

## 11. 갱신 이력

| 2026-08-13 | 사용자 요청 반영 | 모든 검수 결과가 정확히 PASS인 정상 진행과 로컬 재작업 상태의 자동 착수 조건, 재작업 PASS 후 정규 백로그 자동 전환 규칙을 AGENTS·개발계획·HANDOFF에 통일 | 문서 정책 |
| 2026-08-13 | 사용자 요청 반영 | FAIL이어도 현재 범위의 안전한 미실행 해결 방법이 남으면 후보별 자동 수정·재검수하고, 동일 실패 반복·후보 소진·새 승인 필요 시에만 중단하도록 규칙 보완 | 문서 정책 |
| 2026-08-14 | 사용자 요청 반영 | `다음 작업`이 문제 해결용 재작업·재검수이면 정규 후속 백로그보다 우선 자동 착수하도록 규칙 명시 | 문서 정책 |

| 날짜 | 작업자 | 변경 내용 | 기준 Commit |
|---|---|---|---|
| 2026-08-12 | Codex | 권장사항 1~4·6 반영: 입력 Schema, A2A/M1 DB 책임, Package·의존성, Subscribe·Route allowlist, UI 경계와 문서 상태 정합화; 사용자별 Task 권한 결정은 변경하지 않음 | 루트 Git 미구성 |
| 2026-08-12 | Codex | M0.1-04, M0.2~M0.4 백로그, Task 복구·Mock Schema·Adapter·운영 검증 계획 반영 | 루트 Git 미구성 |
| 2026-08-12 | Codex | M0.1 공식 SDK·전송 타입·Workflow 경계 구현 계획 확정, 코드 구현은 원복 | |
| 2026-08-12 | Codex | 구현 전 권장안 반영: Superproject 구조, M0.1 백로그 경계, Streaming·Subscribe 검증, 현재 Task Snapshot 방식, Legacy Smoke 정리와 마일스톤별 Mock 종료 조건 확정 | 루트 Git 미구성 |
| 2026-08-12 | Codex | `workmate-ui`를 폐기된 로컬 샘플로 구현·검수·Submodule 범위에서 제외하고 M0.4를 `workmate-agent` 최소 개발자 검증 페이지로 변경 | 루트 Git 미구성 |
| 2026-08-12 | Codex | 루트 Superproject 초기 Commit과 `workmate-agent` 단일 Submodule 구성, Secret·로컬 산출물 제외 규칙 적용 | `bc22a073a47b25462727bf4a6cde1d7a9f404d52` |
| 2026-08-12 | Codex | `https://github.com/sjseo1221/workmate.git` 원격 등록과 `main` 기준선 Push, Git 추적 차단 해소 | `3b320923cc6684cb40508d8fc7c8978fc49a1496` |
| 2026-08-12 | Codex | M0.1-01 공식 SDK 런타임·Agent Card·Streaming/Subscribe allowlist와 부트스트랩 테스트 구현, 실행 증빙 생성 | `feat/M0.1-01-sdk-runtime` 작업 중 |
| 2026-08-12 | Codex | 주석·Docstring 확장 정책을 AGENTS·기술규격에 반영하고 M0.1 핵심 함수 문서화 보강, 테스트 재실행 | `feat/M0.1-01-sdk-runtime` 작업 중 |
| 2026-08-12 | Codex | M0.1-01 `workmate-agent` 작업 브랜치 원격 Push 완료 | `639f35c`, `origin/feat/M0.1-01-sdk-runtime` |
| 2026-08-12 | Codex | M0.1-02 승인 Schema Contract Test·SDK Message 검증·Legacy Smoke 제거, 7개 테스트 PASS | 로컬 커밋 예정 |
| 2026-08-12 | Codex | M0.1-02 `workmate-agent` 브랜치 원격 Push 완료 | `9ba62fa`, `origin/feat/M0.1-01-sdk-runtime` |
| 2026-08-12 | Codex | Docker daemon 정상 연결 확인, Dockerfile의 `uv sync --system` 오류 수정, Compose·Health·Agent Card 재검수 PASS | `0149b92`, 실행 ID `20260812-210001` |
| 2026-08-12 | 사용자 | 실행 `20260812-210001` 검수 승인, M0.1-01 완료 처리 | M0.1-01 승인 |
| 2026-08-12 | 사용자 | 실행 `20260812-204500` 검수 승인, M0.1-02 완료 처리 및 이후 전 검증 PASS 시 묵시 승인 규칙 확정 | M0.1-02 승인 |
| 2026-08-12 | 사용자 | Push 기본 단위를 백로그에서 하위 마일스톤 완료 체크포인트로 변경하고 중간 Push 예외 조건 확정 | M0.1 완료 시 Push 예정 |
| 2026-08-12 | Codex | M0.1-02 구현 설명을 포함해 7개 테스트 재검증 PASS, 실행 `20260812-212244` 자동 승인 및 result 표준 양식 보강 | M0.1-02 완료 유지 |
| 2026-08-12 | 사용자 | 새로 작성·수정하는 Docstring·JSDoc은 한글을 기본 언어로 사용하고 기술 식별자는 원문을 유지하는 정책 확정 | 문서 정책 반영 |
| 2026-08-12 | Codex | M0.1-03 Registry·SQLite/PostgreSQL Task Store·A2A Migration·Checkpoint 경계 구현, 12개 테스트 PASS; PostgreSQL 실제 연결은 별도 검수 대기 | `82839ac`, 실행 `20260812-215216` |
| 2026-08-12 | Codex | PostgreSQL 통합 테스트 경계 추가, 로컬 12 PASS·1 SKIP; Docker daemon 응답 지연으로 실제 PostgreSQL·최종 Docker 재검증 보류 | `85a4036`, 실행 `20260812-222254` |
| 2026-08-12 | Codex | 실제 PostgreSQL Migration·Task 멱등성·삭제, 최종 Docker build·Migration 파일·Health·Agent Card 검증 PASS; M0.1-03 자동 승인 | `c17d4c2`, 실행 `20260812-224743` |
| 2026-08-12 | Codex | M0.1-04 GET Subscribe 공개 불일치 수정, Cache-Control·활성/Terminal Subscribe·5 Skill·Streaming·Route allowlist Contract Test, 전체 19 PASS·최종 Docker 검증 PASS; M0.1 자동 승인 | `d00a858`, 실행 `20260812-230413` |
| 2026-08-13 | Codex | M0.2-01 기존 LLM 평가 원본·Schema dry-run·평가기 21개 테스트 검수, Full Case 실제 결과와 재평가 Trigger·재현성 보완 위험 기록; 모델 평가는 사용자 승인 대기로 유지 | 실행 `20260813-075806` |
| 2026-08-13 | Codex | M0.2-01 평가기 생성 설정·Prompt/Schema/Case Hash·Retry·비용 상태 메타데이터 보완, 단위 테스트 23개와 Pilot·Full Case dry-run PASS; 실제 Provider 재평가 대기 | 실행 `20260813-082016` |
| 2026-08-13 | Codex | 실제 Provider Pilot·Full Case 1·2 실행 시 메타데이터는 기록됐으나 Windows 소켓 권한과 외부 egress 정책으로 응답 전 차단; M0.2-01 보류 | 실행 `20260813-082520` |
| 2026-08-13 | Codex | 외부 전송 승인 후 실제 Provider 재평가 완료: Pilot 4/4, Full Case 1·2 각 20/20, Schema·의미 44/44 PASS; 비용 미산정·모델 선택 사용자 승인 대기 | 실행 `20260813-093322` |
| 2026-08-13 | 사용자 | `openai/gpt-4.1-mini` 기본 모델과 비용 미산정 사유 승인, M0.2-01 완료; M0.2-02로 진행 | 실행 `20260813-093322` |
| 2026-08-13 | Codex | M0.2-02 Embedding 64 Chunk·60 Case 결과와 평가기 16개 테스트 검수; Hybrid/HNSW 기준 PASS, 답변 가능성 거절률 권장 기준 초과를 운영 판정에서 제외하고 사용자 승인 대기 | 실행 `20260813-114046` |
| 2026-08-13 | Codex | 단일 Cosine 답변 거절을 폐기하고 RRF Top-K·근거 검증·조건부 Reranker·insufficient_evidence·RRF fallback Workflow를 docs/07·10·12와 M0.2-02 증빙에 반영; 실제 구현은 M4.4로 이관 | 실행 `20260813-114046` |
| 2026-08-13 | 사용자 | `openai/text-embedding-3-small`, `vector(1536)`, Cosine, Dense+Trigram RRF+HNSW와 단일 Cosine 운영 거절 제외 방침 승인; M0.2-02 완료 처리 | 실행 `20260813-114046` |
| 2026-08-13 | Codex | M0.2-03 STT 합성 파일·Realtime·Chunk 재연결 E2E 검수; 파일 19/20, Realtime 2/2, E2E 2/2, Provider 오류 0건 PASS, 실제 음성 품질은 M3.3으로 이관하고 사용자 승인 대기 | 실행 `20260813-121052` |
| 2026-08-13 | 사용자 | `gpt-4o-transcribe`, 한국어 `ko`, 파일 기반 STT·Realtime 임시 자막 MVP 승인; 실제 음성 WER/CER·화자 분리·잡음·겹침 발화는 M3.3으로 이관하고 M0.2-03 완료 처리 | 실행 `20260813-121052` |
| 2026-08-13 | Codex | M0.2-04 Gmail OAuth 검수: readonly Scope·dry-run·2개 단위 테스트·구문 검사 PASS, 기존 Gmail Profile·Message·History·Watch 성공 이력 확인; 현재 외부 API 재실행은 네트워크 차단으로 사용자 확인 대기 | 실행 `20260813-122007` |
| 2026-08-13 | Codex | M0.2-05 Calendar OAuth 검수: readonly Scope·dry-run·2개 단위 테스트·구문 검사 PASS, 기존 Calendar Events·Watch 성공 이력 확인; 현재 외부 API 재실행은 네트워크 차단으로 사용자 확인 대기 | 실행 `20260813-122321` |
| 2026-08-13 | 사용자 | 기존 Calendar OAuth·Watch 성공 이력 승인, M0.2-05 완료 처리; 이후 하위 마일스톤은 모든 결과가 정확히 PASS일 때만 자동 승인하고 PASS 이외 결과 발생 시 중단 | 실행 `20260813-122321` |
| 2026-08-13 | Codex | `httplib2` IPv6 fallback 실패를 확인해 `AuthorizedSession` REST 전송으로 교체하고 회귀 테스트 3건 PASS; 실제 OAuth timeout·Watch 미실행으로 M0.2-05 재작업 및 다음 작업 중단 | 실행 `20260813-130230` |
| 2026-08-13 | 사용자 로컬 실행 결과 | Gmail·Calendar 실제 조회와 Watch가 모두 정확히 PASS하여 M0.2-05 자동 승인; 이전 실패 실행은 보존 | 실행 `20260813-131903` |
| 2026-08-13 | Codex | M0.2 통합 검수에서 M0.2-02·03·04의 PASS_WITH_CAVEAT·FAIL·보류를 확인해 자동 승인 중단, M0.2 재작업 전환 | 실행 `20260813-133446` |
| 2026-08-13 | Codex | M0.2-02·03·04 차단 해소 계획 확정: 범위 재정리, 후속 마일스톤 이관, Gmail 결과 전용 증빙 후 정확한 PASS 재검수 | `docs/evidence/M0/M0.2/remediation-plan.md` |
| 2026-08-13 | Codex | M0.2-02 재검수에서 모델·검색·성능·단위 테스트·구문·문서 검사가 모두 PASS하여 자동 승인; 다음은 M0.2-03 재검수 | 실행 `20260813-134129` |
| 2026-08-13 | Codex | M0.2-03 재검수에서 합성·Realtime·E2E 범위와 정의된 검증 명령이 모두 PASS하여 자동 승인; 다음은 M0.2-04 재검수 | 실행 `20260813-134542` |
| 2026-08-13 | Codex | M0.2-04 재검수에서 Gmail 실제 로컬 조회·Watch와 정의된 검증 명령이 모두 PASS하여 자동 승인; 다음은 M0.2 통합 재검수 | 실행 `20260813-134915` |
| 2026-08-13 | Codex | M0.2 통합 재검수에서 M0.2-01~05 최신 승인 실행이 모두 정확히 PASS하여 자동 승인·완료; 다음은 M0.3-01 | 실행 `20260813-135158` |
| 2026-08-13 | 사용자 | 기존 Gmail OAuth·Watch 성공 이력 승인, M0.2-04 완료 처리; 외부 API 재실행 보류는 증빙에 유지 | 실행 `20260813-122007` |
| 2026-08-13 | Codex | 자동 승인 대상 검수의 판정 알고리즘을 문서화: 모든 항목이 정확히 PASS면 자동 승인하고 PASS 이외 결과가 하나라도 있으면 즉시 중단·재개 조건 기록 | `docs/06-delivery-plan.md`, `AGENTS.md` |
| 2026-08-13 | Codex | M0.4-03을 `보류(선행 M1.3 대기)`로 전환하고, M1.1 Task DB 기반 실제 Workflow 착수 계획·증빙 경로를 문서화; M1.3 완료 후 M0.4-03 잔여 UI 육안 검수를 다시 묻도록 명시 | `docs/06-delivery-plan.md`, `docs/evidence/M1/M1.1/README.md` |
| 2026-08-13 | Codex | M1.1-01 업무 도메인 Migration 초안과 5개 계약·회귀 테스트 구현, `compileall`·`git diff --check` PASS; 공개 DDL·PostgreSQL 실제 적용 검수 대기 | 실행 `20260813-170218` |
| 2026-08-13 | 사용자 로컬 실행 결과 | M1.1-01 계약·회귀 테스트 5개, `compileall`, `git diff --check` 모두 PASS; PostgreSQL 실제 적용과 공개 DDL 승인 대기 | 실행 `20260813-170714` |
| 2026-08-13 | 사용자 | M1.1-01 공개 DDL·제약 승인; 승인 실행 `20260813-170714`을 최신 승인으로 연결하고 M1.1-01 완료 처리 | 다음 M1.1-02 |
| 2026-08-13 | Codex | M1.1-02 `TaskRecord`·`TaskRepository`·SQLite/PostgreSQL Adapter와 사용자 범위·멱등·Soft Delete 테스트 구현; 전체 39개 테스트 PASS, PostgreSQL 통합 1개 SKIP으로 실제 DB 검수 대기 | 실행 `20260813-185441` |
| 2026-08-13 | Codex | M1.1-03 동기화 상태 Domain·Repository와 SQLite/PostgreSQL 통합 테스트 구현; SQLite는 PASS했으나 PostgreSQL `users.user_id` 외래키 위반으로 FAIL하여 자동 진행 중단·재작업 전환 | 실행 `20260813-193324` |
| 2026-08-13 | Codex | M1.1-03 사용자 원장 보장 수정 후 PostgreSQL 동기화 통합·전체 44개 테스트·정적 검사가 모두 PASS하여 자동 승인·완료 처리 | 실행 `20260813-193615` |
| 2026-08-13 | Codex | M1.1-05 Migration 재실행·Task·Sync 통합 12개와 전체 45개 테스트가 PASS하여 자동 승인·완료 처리 | 실행 `20260813-193901` |
| 2026-08-13 | Codex | M1.1-04 정상·Soft Delete·중복·사용자 격리·Provider Cursor Fixture 5개와 정적 검사가 PASS하여 자동 승인·완료 처리 | 실행 `20260813-194043` |
| 2026-08-13 | Codex | M1.1-01~05 전체 승인으로 M1.1 완료 처리; M1.2는 외부 OAuth·실제 Provider 연동 예외로 자동 착수 보류 사유와 재개 조건 기록 | 문서 정책 |
| 2026-08-13 | 사용자 | M1.2 외부 Gmail·Google Calendar 연동 착수 승인 | 실행 `20260813-194801` |
| 2026-08-13 | Codex | Gmail·Calendar Adapter·Cursor Workflow 구현, 실제 OAuth 조회·Watch·새 Adapter 정규화와 계약 테스트 PASS; M1.2 자동 승인·완료 처리 | 실행 `20260813-194801` |
## 최신 상태 보정: M1.3 검수 중

- 백로그 ID: M1.3
- 구현 완료: [`workmate-agent/app/task_api.py`](workmate-agent/app/task_api.py)의 Task CRUD API와 [`workmate-agent/tests/test_task_api.py`](workmate-agent/tests/test_task_api.py)의 8개 테스트
- 최신 실행 ID: `20260813-200500`
- 결과: API 단위·Repository 8 PASS, compileall PASS, diff check PASS
- 자동 승인 보류 사유: M1.3-02 UI 미구현 및 전체 테스트의 PostgreSQL 통합 테스트 3건 SKIP (`DATABASE_URL` 미설정)
- 상태: 검수 중
- 다음 착수 조건: M1.3-02 Task 관리 UI 구현 후 PostgreSQL 통합 테스트를 실행하고 모두 PASS일 때 재검수
## 최신 상태 보정: M1.3 UI 육안 검수 대기

- 백로그 ID: M1.3
- 구현 완료: Task CRUD API와 `/tasks` Task 관리 UI
- 최신 실행 ID: `20260813-201500`
- 결과: PostgreSQL 포함 전체 59개 테스트, UI 계약 테스트, compileall, diff check 모두 PASS
- 자동 승인 보류 사유: UI 육안 검수는 사용자 판단이 필요한 수동 검수
- 상태: 검수 중
- 검수 URL: `http://127.0.0.1:8001/tasks`
- 다음 착수 조건: 사용자가 UI를 육안 확인해 PASS 승인한 후 M1.3 완료 처리
## 최신 상태 보정: M1.3 완료

- M1.3 실행 `20260813-201500`의 59개 테스트와 UI 계약 검증이 PASS했고, 사용자가 UI 육안 검수를 `y`로 승인했다.
- `docs/evidence/M1/M1.3/README.md`의 `latest_approved_run_id`를 `20260813-201500`으로 갱신했다.
- 현재 상태: M1.3 완료
- 다음 작업: M0.4-03 UI 통합 검수 재실행
- M0.4-03은 실제 장기 Task의 취소·권한 UI를 다시 확인하기 전까지 완료 처리하지 않는다.
## 최신 상태 보정: M0.4-03 재검수 중단

- 실행 ID: `20260813-212246`
- 자동 검증: 내부 API·UI 11 PASS, `WORKING` Fixture 취소·사용자 격리·compileall·diff check PASS
- 비-PASS 항목: 운영 경로의 실제 `WORKING` A2A Task 육안 검수 BLOCKED
- 원인: M1.3 Task CRUD는 동기 API이며, 현재 5개 Skill은 즉시 완료 runtime bootstrap이라 취소 버튼을 활성화할 실제 장기 Task가 없음
- 상태: M0.4-03 재작업
- 자동 진행 중단 사유: BLOCKED 항목 발생
- 재개 조건: 운영 Route를 변경하지 않는 테스트 전용 로컬 OIDC·`WORKING` Task UI Fixture로 취소 버튼 활성화·취소 상태를 사용자 육안 검수
- 증빙: [`docs/evidence/M0/M0.4/runs/20260813-212246/result.md`](docs/evidence/M0/M0.4/runs/20260813-212246/result.md)

## 최신 상태 보정: M0.4-03 재작업 검수 중

- 실행 ID: `20260813-213733`
- 자동 재작업 착수: 예
- 구현: 테스트 전용 로컬 OIDC·JWKS·`WORKING` Task Fixture 실행기 추가
- 자동 검증: Fixture·내부 API·UI 13 PASS, 실제 HTTP 흐름 PASS, `compileall`·`git diff --check` PASS
- 브라우저 검증: `TASK_STATE_WORKING`과 활성 취소 버튼 표시 후 `TASK_STATE_CANCELED` 전환 PASS
- 운영 Route·공개 Schema·운영 Workflow: 변경 없음
- 상태: M0.4-03 검수 중
- 자동 진행 보류 사유: UI 육안 검수는 사용자 판단 필요
- 재개 조건: 사용자가 현재 브라우저 화면을 확인하고 PASS 승인
- 증빙: [`docs/evidence/M0/M0.4/runs/20260813-213733/result.md`](docs/evidence/M0/M0.4/runs/20260813-213733/result.md)

## 최신 상태 보정: M0.4-03 완료

- 실행 ID: `20260813-213733`
- 자동 재작업 착수: 예
- 자동·HTTP·브라우저 검증: 모두 PASS
- 사용자 UI 육안 승인: `y` 승인
- 상태: M0.4-03 및 M0.4 완료
- 최신 승인 실행: `20260813-213733`
- 다음 작업: M0 통합 검수
- 증빙: [`docs/evidence/M0/M0.4/runs/20260813-213733/result.md`](docs/evidence/M0/M0.4/runs/20260813-213733/result.md)
- M3.1 회의 입력 구현 시작: `docs/evidence/M3/M3.1/runs/20260814-080000/result.md`에서 multipart 의존성 파일 잠금으로 테스트가 BLOCKED되어 재작업 중. 프로세스 종료 후 `\.venv\Scripts\python.exe -m unittest tests/test_meeting_api.py` 재실행 필요.
- M3.1 회의 입력 자동 승인 완료: [실행 결과](docs/evidence/M3/M3.1/runs/20260814-081500/result.md). 회의 메타데이터 API와 multipart MIME·크기·checksum 중복 검증 PASS.
- M3.2 실시간 녹음은 ACK·Gap·중복 WebSocket 테스트 3개가 PASS했으나 RecordingSession이 프로세스 메모리 상태라 재작업 중이다. 영속 Repository와 프로세스 재시작 재연결 검증 후 승인한다: `docs/evidence/M3/M3.2/runs/20260814-083000/result.md`
- M3.2 실시간 녹음 자동 승인 완료: [실행 결과](docs/evidence/M3/M3.2/runs/20260814-084500/result.md). WebSocket ACK·Gap·중복·영속 RecordingSession·재연결 검증 4개 PASS.
- M3.3 STT·Transcript 로컬 계약 구현 완료, 5개 저장·조회·Streaming 회귀 테스트 PASS. 실제 `gpt-4o-transcribe` Provider 호출과 품질 평가는 Secret·평가 음성 검수 대기: `docs/evidence/M3/M3.3/runs/20260814-090000/result.md`
- M3.3 STT·Transcript 자동 승인 완료: 실제 `gpt-4o-transcribe` 2 Case 의미 검증 2/2, Provider 오류 0, Chunk 재연결 PASS. 증빙: `docs/evidence/M3/M3.3/runs/20260814-091500/result.md`
- M3.4 실제 LLM 호출은 연결됐으나 ActionItem 필수 필드와 Transcript 원문 근거 검증에서 실패해 재작업 중이다. 로컬 7개 테스트는 PASS. 증빙: `docs/evidence/M3/M3.4/runs/20260814-093000/result.md`
- M3.4 회의 분석 자동 승인 완료: strict JSON Schema·Action Item 필수 필드·Transcript 원문 근거 검증과 실제 gpt-4.1-mini 호출이 PASS했다. 증빙: `docs/evidence/M3/M3.4/runs/20260814-094500/result.md`
- M3.5 승인·Task 등록 자동 승인 완료: 동일 Action Item 반복 승인 시 동일 Task ID·단일 Task 생성 8개 회귀 테스트 PASS. 증빙: `docs/evidence/M3/M3.5/runs/20260814-100000/result.md`
- M3.6 R2 Adapter 로컬·실제 PUT/HEAD/GET checksum/삭제는 PASS했으나 30일 Lifecycle 조회가 권한 부족(`not_permitted`)으로 검수 중이다. 증빙: `docs/evidence/M3/M3.6/runs/20260814-103000/result.md`
- M3.6 Lifecycle 필수 재검수 `20260814-104500`도 `R2 Lifecycle 정책이 설정되어 있지 않습니다`로 실패했다. 관리 Dashboard 확인 또는 Lifecycle 권한 Token이 필요하다.
- M3.6 Lifecycle 권한 부족이 3회 연속 재현되어 자동 검수를 보류로 전환했다. Dashboard의 30일 규칙 확인 또는 관리 Token 제공 전에는 재실행하지 않는다.
- M3.6 Dashboard에서 `meetings/` Prefix·30일 삭제·Enabled 규칙을 확인했다. API 자동 Lifecycle 조회는 Token 권한 부족으로 별도 보류하며, 화면 검수 사용자 승인 대기: `docs/evidence/M3/M3.6/runs/20260814-110000/result.md`

## 최신 상태 보정: M3.6 완료

- 실행 ID: `20260814-113000`
- 실행 명령: `r2-storage-test\\venv\\Scripts\\python.exe smoke_test.py --require-lifecycle`
- Presigned PUT·HEAD·GET checksum·Lifecycle 조회·삭제: 모두 PASS
- Lifecycle 규칙 2개와 `delete-meeting-audio-after-30-days` 규칙 확인
- 상태: M3.6 완료
- 최신 승인 실행: `20260814-113000` (자동 승인: 검증 명령 전체 PASS)
- 증빙: [`docs/evidence/M3/M3.6/runs/20260814-113000/result.md`](docs/evidence/M3/M3.6/runs/20260814-113000/result.md)
- 다음 작업: M4.1 검색 데이터 구현 계획 및 착수 검토

## 최신 상태 보정: M4.1 착수

- 상태: M4.1 진행
- 착수 검토: `meeting_chunks` Migration·Repository·Embedding Adapter가 아직 구현되지 않았음을 확인
- 계획 증빙: [`docs/evidence/M4/M4.1/README.md`](docs/evidence/M4/M4.1/README.md)
- 현재 백로그: M4.1-01 검색 Chunk Migration
- 선행 조건: M3.3 Transcript 승인 완료
- 다음 작업: M4.1-01 pgvector·`meetings`·`meeting_chunks` Migration 구현
- 자동 승인: 아직 실행 결과가 없어 적용하지 않음

## 최신 상태 보정: M4.1-01 완료

- 실행 ID: `20260814-120000`
- Migration 계약 테스트 1개, `compileall`, `git diff --check`: 모두 PASS
- 자동 승인: M4.1-01 검증 명령 전체 PASS
- 증빙: [`docs/evidence/M4/M4.1/runs/20260814-120000/result.md`](docs/evidence/M4/M4.1/runs/20260814-120000/result.md)
- 다음 작업: M4.1-02 Chunk Repository 구현

## 최신 상태 보정: M4.1-02 검수 중

- 실행 ID: `20260814-123000`
- SQLite 계약·단위 테스트 5개, `compileall`, `git diff --check`: PASS
- 실제 PostgreSQL 통합: 미실행
- 자동 구현 보류 사유: pgvector Migration 적용과 PostgreSQL 사용자 격리·저장·조회·수정 검증 필요
- 재개 조건: `WORKMATE_TEST_DATABASE_URL`이 설정된 PostgreSQL 16+pgvector 통합 테스트 PASS
- 상태: M4.1-02 검수 중, M4.1 진행
- 증빙: [`docs/evidence/M4/M4.1/runs/20260814-123000/result.md`](docs/evidence/M4/M4.1/runs/20260814-123000/result.md)
- 다음 작업: M4.1-02 PostgreSQL 통합 검수

## 최신 상태 보정: M4.1-02 PostgreSQL 검수 보류

- 실행 ID: `20260814-124000`
- `WORKMATE_TEST_DATABASE_URL`: 미설정
- Docker PostgreSQL/pgvector 컨테이너: 없음
- `127.0.0.1:5432`: 포트만 응답하며 검수 DSN·인증 정보 없음
- 자동 구현 보류 사유: 실제 PostgreSQL 통합 검수를 안전하게 실행할 연결 대상이 없음
- 재개 조건: PostgreSQL 16+pgvector 준비 후 `WORKMATE_TEST_DATABASE_URL` 설정
- 상태: M4.1-02 보류, M4.1 진행 중단
- 증빙: [`docs/evidence/M4/M4.1/runs/20260814-124000/result.md`](docs/evidence/M4/M4.1/runs/20260814-124000/result.md)
- 다음 작업: M4.1-02 PostgreSQL 통합 검수 재실행

## 최신 상태 보정: M4.1-02 완료

- 실행 ID: `20260814-125000`
- PostgreSQL 16+pgvector 실제 저장·조회·수정·멱등·사용자 격리: 모두 PASS
- SQLite 계약·Migration 회귀 5개, `compileall`, `git diff --check`: 모두 PASS
- 임시 pgvector 컨테이너 정리 완료
- 상태: M4.1-02 완료, M4.1 진행
- 증빙: [`docs/evidence/M4/M4.1/runs/20260814-125000/result.md`](docs/evidence/M4/M4.1/runs/20260814-125000/result.md)
- 자동 구현 보류 사유: M4.1-03은 실제 Embedding Provider·`EMBEDDING_API_KEY` 사용 승인이 필요
- 재개 조건: 실제 `openai/text-embedding-3-small` 호출 승인과 환경변수 설정
- 다음 작업: M4.1-03 Embedding Adapter·재임베딩 구현 및 실제 Provider 검수

## 최신 상태 보정: M4.1-01 완료

- 실행 ID: `20260814-120000`
- 구현: [`004_search_data.sql`](workmate-agent/migrations/004_search_data.sql), [`test_search_data_migration.py`](workmate-agent/tests/test_search_data_migration.py)
- 검증: Migration 계약 테스트, `compileall`, `git diff --check` PASS
- 실제 PostgreSQL 적용·pgvector Index Scan은 M4.1-04에서 검증
- 상태: M4.1-01 완료, M4.1 진행
- 다음 작업: M4.1-02 Chunk Repository 구현

## 최신 상태 보정: M4.1-03 완료

- 실행 ID: `20260814-131500`
- 구현: [`workmate-agent/app/embeddings.py`](workmate-agent/app/embeddings.py)
- 테스트: [`workmate-agent/tests/test_embedding_adapter.py`](workmate-agent/tests/test_embedding_adapter.py) 포함 회귀 8개 PASS
- 실제 Provider: `openai/text-embedding-3-small` 호출 PASS, 응답 차원 1536
- `compileall`, `git diff --check`: PASS
- 상태: M4.1-03 완료, M4.1 진행
- 증빙: [`docs/evidence/M4/M4.1/runs/20260814-131500/result.md`](docs/evidence/M4/M4.1/runs/20260814-131500/result.md)
- 자동 승인: 검증 명령 전체 PASS 및 미해결 차단 없음
- 다음 작업: M4.1-04 검색 데이터 통합 검수

## 최신 상태 보정: M4.1 완료

- 실행 ID: `20260814-143000`
- 구현: [`workmate-agent/tests/test_search_data_postgres_integration.py`](workmate-agent/tests/test_search_data_postgres_integration.py)
- 실제 PostgreSQL 16 + pgvector 통합·재임베딩·사용자 격리·HNSW Index Scan: PASS
- 통합·회귀 6개, `compileall`, `git diff --check`: PASS
- 초기 HNSW 계획 검증 실패는 [`20260814-140500`](docs/evidence/M4/M4.1/runs/20260814-140500/result.md)에 보존하고 수정 후 재검수했다.
- 임시 PostgreSQL 컨테이너 정리 완료
- 상태: M4.1 완료
- 증빙: [`docs/evidence/M4/M4.1/runs/20260814-143000/result.md`](docs/evidence/M4/M4.1/runs/20260814-143000/result.md)
- 자동 승인: 검증 명령 전체 PASS 및 미해결 차단 없음
- 다음 작업: M4.2 Trigram 검색

## 최신 상태 보정: M4.2 완료

- 실행 ID: `20260814-151500`
- 구현: [`workmate-agent/app/repositories/meeting_chunks.py`](workmate-agent/app/repositories/meeting_chunks.py)
- 테스트: [`workmate-agent/tests/test_trigram_search_postgres_integration.py`](workmate-agent/tests/test_trigram_search_postgres_integration.py)
- 실제 PostgreSQL pg_trgm 검색·similarity 정렬·사용자 격리·회의 ID/날짜 필터: PASS
- 관련 회귀 7개, `compileall`, `git diff --check`: PASS
- 초기 Fixture 오류는 [`20260814-150000`](docs/evidence/M4/M4.2/runs/20260814-150000/result.md)에 보존하고 수정 후 재검수했다.
- 임시 PostgreSQL 컨테이너 정리 완료
- 상태: M4.2 완료
- 증빙: [`docs/evidence/M4/M4.2/runs/20260814-151500/result.md`](docs/evidence/M4/M4.2/runs/20260814-151500/result.md)
- 자동 승인: 검증 명령 전체 PASS 및 미해결 차단 없음
- 다음 작업: M4.3 Hybrid 검색

## 최신 상태 보정: M4.3 완료

- 실행 ID: `20260814-161500`
- 구현: [`workmate-agent/app/repositories/meeting_chunks.py`](workmate-agent/app/repositories/meeting_chunks.py)
- 테스트: [`workmate-agent/tests/test_hybrid_search_postgres_integration.py`](workmate-agent/tests/test_hybrid_search_postgres_integration.py)
- Dense cosine·Trigram RRF·사용자/metadata 필터·HNSW 계획: PASS
- 검색·Repository 회귀 8개, `compileall`, `git diff --check`: PASS
- 초기 Dense Fixture 오류는 [`20260814-160000`](docs/evidence/M4/M4.3/runs/20260814-160000/result.md)에 보존하고 수정 후 재검수했다.
- 임시 PostgreSQL 컨테이너 정리 완료
- 상태: M4.3 완료
- 증빙: [`docs/evidence/M4/M4.3/runs/20260814-161500/result.md`](docs/evidence/M4/M4.3/runs/20260814-161500/result.md)
- 자동 승인: 검증 명령 전체 PASS 및 미해결 차단 없음
- 다음 작업: M4.4 답변·출처

## 최신 상태 보정: M4.4 완료

- 실행 ID: `20260814-171500`
- 구현: [`workmate-agent/app/meeting_answer.py`](workmate-agent/app/meeting_answer.py)
- 테스트: [`workmate-agent/tests/test_meeting_answer.py`](workmate-agent/tests/test_meeting_answer.py), [`test_meeting_answer_postgres_integration.py`](workmate-agent/tests/test_meeting_answer_postgres_integration.py)
- 답변·출처·원문 evidence 일치·근거 부족 거절·사용자 범위: PASS
- 검색·Repository·답변 통합 8개, `compileall`, `git diff --check`: PASS
- 임시 PostgreSQL 컨테이너 정리 완료
- 상태: M4.4 완료
- 증빙: [`docs/evidence/M4/M4.4/runs/20260814-171500/result.md`](docs/evidence/M4/M4.4/runs/20260814-171500/result.md)
- 자동 승인: 검증 명령 전체 PASS 및 미해결 차단 없음
- 다음 작업: M4.5 검색 평가

## 최신 상태 보정: M4 완료

- 실행 ID: `20260814-181500`
- 평가 검증: [`workmate-agent/tests/test_m45_search_evaluation.py`](workmate-agent/tests/test_m45_search_evaluation.py)
- 실제 평가 원본: 64 Chunk·60 Case
- Hybrid Hit@3 98.21%, HNSW Recall@5 100%, Hybrid DB p95 64.743ms, Query Embedding p95 893.1ms: PASS
- `compileall`, `git diff --check`: PASS
- 상태: M4 완료
- 증빙: [`docs/evidence/M4/M4.5/runs/20260814-181500/result.md`](docs/evidence/M4/M4.5/runs/20260814-181500/result.md)
- 자동 승인: 검증 명령 전체 PASS 및 미해결 차단 없음
- 다음 작업: M5 통합·시연 또는 M3 상위 상태 정리

## 최신 상태 보정: M3 상위 완료 및 M5 진입 게이트 확인

- 실행 ID: `20260814-190500`
- M3.1~M3.6 최신 승인 실행을 대조한 결과 모두 PASS이며 `latest_approved_run_id`가 존재한다.
- 상태: M3 완료
- 증빙: [`docs/evidence/M3/runs/20260814-190500/result.md`](docs/evidence/M3/runs/20260814-190500/result.md), [`docs/evidence/M3/README.md`](docs/evidence/M3/README.md)
- M5 진입 게이트: 대기. M2.4 사용자 육안 검수가 보류되어 M2 상위 완료가 아니므로 M2·M3·M4 전체 완료 조건을 충족하지 못했다.
- 자동 착수 보류 사유: M5 선행조건(M2·M3·M4) 중 M2가 미완료
- 다음 착수 조건: 사용자가 M2.4 UI 육안 검수를 PASS로 승인해 M2 상위가 완료되거나, M2.4의 재검수 결과가 자동 승인될 것

## 최신 상태 보정: M2.4-03 UI 육안 검수 재개 대기

- 실행 ID: `20260814-191000`
- 정적 UI 계약 테스트 1개와 `git diff --check`는 PASS했다.
- 검수 URL `http://127.0.0.1:8001/weekly-report`와 대체 포트 8010에 실행 중인 서버가 없어 실제 화면 검수는 BLOCKED였다.
- 상태: M2.4 검수 중, M2 진행
- 증빙: [`docs/evidence/M2/M2.4/runs/20260814-191000/result.md`](docs/evidence/M2/M2.4/runs/20260814-191000/result.md)
- 자동 승인 보류 사유: 육안 검수·사용자 Token·실제 보고서 데이터 미실행
- 다음 작업: 서버 실행 후 사용자가 M2.4-03 정상·오류 화면을 육안 확인하고 PASS/FAIL 판정

## 최신 상태 보정: M2.4 보류 유지 및 M5 진입 대기

- 실행 ID: `20260814-192000`
- M2.4는 사용자 요청에 따라 `보류`로 유지한다.
- M5 진입 게이트를 확인했으며 M3·M4는 완료, M2는 M2.4 보류로 미완료다.
- 상태: M5 대기
- 자동 착수 보류 사유: M2·M3·M4 전체 완료 조건 중 M2 미충족
- 증빙: [`docs/evidence/M5/runs/20260814-192000/result.md`](docs/evidence/M5/runs/20260814-192000/result.md), [`docs/evidence/M5/README.md`](docs/evidence/M5/README.md)
- 다음 착수 조건: M2.4-03 사용자 육안 PASS 또는 승인된 재검수 실행

## 최신 상태 보정: M5.1 A2A 통합 예외 착수

- 실행 ID: `20260814-193000`
- M5.1 직접 선행조건 M0.3·M1.5·M2.3·M3.5·M4.4가 모두 완료되어 예외 착수했다.
- M2.4는 보류로 유지하며, 이번 착수는 M5 상위 진입·완료를 의미하지 않는다.
- 상태: M5.1 진행, M5 상위 대기
- 현재 범위: Agent Card·HTTP+JSON·5개 Skill·Artifact/Task/오류 변환 계약 정리
- 차단 사항: 운영 Orchestrator 구현과 종단 간 Contract Test가 아직 이 저장소에 없음. `a2a-smoke-test`는 레거시 하네스이므로 완료 증빙으로 사용하지 않는다.
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-193000/result.md`](docs/evidence/M5/M5.1/runs/20260814-193000/result.md)
- 다음 작업: Orchestrator 호출 코드 확보 후 M5.1 실제 Agent Card·5개 Skill 종단 간 검수

## 최신 상태 보정: M5.1 종단 간 검수 차단

- 실행 ID: `20260814-194000`
- 운영 Orchestrator 프로젝트가 없어 실제 Agent Card·5개 Skill 종단 간 호출을 실행하지 못했다.
- `a2a-smoke-test`는 정식 계약과 다른 레거시 하네스이므로 대체 검수에 사용하지 않았다.
- 상태: M5.1 진행 중단, M5 상위 대기
- 자동 승인 보류 사유: Orchestrator 호출 코드·실행 환경 부재
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-194000/result.md`](docs/evidence/M5/M5.1/runs/20260814-194000/result.md)
- 재개 조건: 팀 Orchestrator 프로젝트 또는 실행 가능한 호출 코드와 `WORKMATE_AGENT_URL`·서비스 인증 설정 제공

## 최신 상태 보정: M5.1 Orchestrator 경로 재확인

- 실행 ID: `20260814-195000`
- Downloads 및 `C:\dev\workmate` 후보 경로에서 운영 Orchestrator 프로젝트를 찾지 못했다.
- 상태: M5.1 진행 중단, M5 상위 대기
- 자동 진행 보류 사유: 종단 간 호출 코드·실행 환경이 여전히 없음
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-195000/result.md`](docs/evidence/M5/M5.1/runs/20260814-195000/result.md)

## 최신 상태 보정: M5.1 Workmate A2A 호환성 클라이언트 구현

- 실행 ID: `20260814-200000`
- 구현: [`workmate-agent/tools/m51_a2a_compatibility.py`](workmate-agent/tools/m51_a2a_compatibility.py)
- Agent Card·5개 Skill 실제 HTTP 호출, Artifact Schema 검증, `runtime_bootstrap`/`mock=true` 차단을 수행하는 CLI를 추가했다.
- 정적 검증: `compileall`, `git diff --check` PASS
- 상태: M5.1 진행, 실제 HTTP 실행·Orchestrator 종단 간 검수 대기
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-200000/result.md`](docs/evidence/M5/M5.1/runs/20260814-200000/result.md)
- 실행 명령: `uv run python tools/m51_a2a_compatibility.py`

## 최신 상태 보정: M5.1 실제 HTTP 검수 차단

- 실행 ID: `20260814-201000`
- Agent Card와 5개 Skill 공개 목록은 PASS했다.
- `daily_briefing`, `weekly_report`, `rank_priorities`는 실제 HTTP 호출 PASS.
- `analyze_meeting`, `search_meetings`는 `runtime_bootstrap` Mock Artifact를 반환해 FAIL.
- 원인: [`app/a2a/runtime.py`](workmate-agent/app/a2a/runtime.py)의 Registry가 M3/M4 실제 Workflow 대신 부트스트랩 Handler를 등록함.
- 상태: M5.1 진행 중단, 자동 승인 불가
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-201000/result.md`](docs/evidence/M5/M5.1/runs/20260814-201000/result.md)
- 다음 작업: M3/M4 실제 Workflow를 A2A Registry에 연결한 뒤 동일 클라이언트로 재검수

## 최신 상태 보정: M5.1 Workmate 측 실제 Workflow 재검수 PASS

- 실행 ID: `20260814-203000`
- `analyze_meeting`은 최종 Transcript·실제 LLM·Action Item 근거 저장 경로, `search_meetings`는 실제 Embedding·PostgreSQL Hybrid 검색·출처 답변 경로에 연결했다.
- Agent Card와 `daily_briefing`·`weekly_report`·`analyze_meeting`·`search_meetings`·`rank_priorities` 실제 HTTP 호출이 모두 PASS했다.
- M5.1 직접 관련 테스트 14개 PASS, 0 FAIL, 0 SKIP. 전체 회귀 137개 PASS, 환경 의존 10개 SKIP. `compileall`·`git diff --check` PASS.
- Windows PostgreSQL 실행은 `python -m app.server`를 사용해 Selector Event Loop를 적용한다.
- 상태: M5.1 검수 중, M5 상위 대기. M2.4 보류는 유지한다.
- 자동 승인하지 않은 이유: 실제 Orchestrator 실행 환경이 없어 Orchestrator의 Agent Card 조회·5개 Skill 호출·응답 변환 종단 간 검수를 수행하지 못했다.
- `a2a-smoke-test/orchestrator`는 `/a2a/v1` 레거시 하네스라 정식 `/a2a`·Agent Card 계약 검수에 사용하지 않았다.
- 담당자 Orchestrator 저장소를 `C:\dev\AI-agent_game_platform`에 clone했다. `main` 기준 HEAD는 `5094cad47e15578e9f2775db74563e47394e71ee`이다.
- 해당 Orchestrator는 `/a2a/v1`과 레거시 `parts[1].data.invoked_skill` 응답을 기대하므로 Workmate 정식 `/a2a`·Artifact Schema와 직접 호환되지 않는다. Workmate 공개 계약을 유지하려면 별도 HTTP 어댑터가 필요하다.
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-203000/result.md`](docs/evidence/M5/M5.1/runs/20260814-203000/result.md)
- 다음 작업: Orchestrator 실행 환경 확보 후 M5.1 종단 간 검수
-
## 최신 상태 보정: M5.1 Orchestrator 어댑터 실연동

- 실행일: 2026-08-14
- 구현: [`workmate-agent/tools/m51_legacy_adapter.py`](workmate-agent/tools/m51_legacy_adapter.py)
- 테스트: [`workmate-agent/tests/test_m51_legacy_adapter.py`](workmate-agent/tests/test_m51_legacy_adapter.py) 2 PASS
- 실연동: Workmate upstream(8013)과 어댑터(8012)에서 Agent Card URL 변환 및 `daily_briefing` 호출 PASS
- 상태: M5.1 검수 중 유지
- 보류 사유: 담당 Orchestrator 전체 컨테이너 E2E와 5개 Skill 종단 간 응답 변환 검증이 아직 없음
## 최신 상태 보정: M5.1 Orchestrator 종단 간 검수 차단

- 실행 ID: `20260814-122719`
- 결과: Docker Engine named pipe 권한 오류로 Compose 기동 실패
- 추가 차단: `C:\dev\AI-agent_game_platform\backend`에 `fastapi`·`pytest` 미설치
- 상태: M5.1 재작업
- 자동 승인: 미실행 (FAIL 및 미실행 항목 존재)
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-122719/result.md`](docs/evidence/M5/M5.1/runs/20260814-122719/result.md)
- 재개 조건: Docker Desktop Engine 접근 복구 및 Orchestrator 의존성 설치 후 Compose/E2E 재검수
## 최신 상태 보정: M5.1 Orchestrator daily_briefing E2E PASS

- 실행 ID: `20260814-124019`
- 담당 Orchestrator 로컬 의존성 설치 완료
- Workmate upstream(8013) + legacy adapter(8012) + Orchestrator(8000) 연결
- Agent discovery 및 `daily_briefing` Task 최종 `succeeded` 확인
- 어댑터 호환 보완: 최상위 `url`, registry `name`, `/message:send` endpoint, text→data 변환, messageId UUID 치환
- 어댑터 테스트 3 PASS, compileall·diff-check PASS
- 상태: M5.1 검수 중
- 자동 승인 보류: 5개 Skill 전체 종단 간 검증이 아직 남음
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-124019/result.md`](docs/evidence/M5/M5.1/runs/20260814-124019/result.md)
## 최신 상태 보정: M5.1 5개 Skill E2E 재작업

- 실행 ID: `20260814-124301`
- `rank_priorities`: PASS
- `weekly_report`, `analyze_meeting`, `search_meetings`: 요청은 성공했으나 Artifact가 `daily_briefing`으로 반환되어 FAIL
- 상태: M5.1 재작업
- 자동 진행 중단 사유: 검수 결과가 PASS가 아닌 항목 존재
- 재개 조건: Orchestrator 실제 message payload와 어댑터 Skill 매핑 원인 확인 후 5개 Skill 재검수
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-124301/result.md`](docs/evidence/M5/M5.1/runs/20260814-124301/result.md)
## 최신 상태 보정: M5.1 나머지 Skill E2E 차단

- 실행 ID: `20260814-124744`
- 한국어 입력은 담당 Orchestrator SQLite에 `?`로 저장되어 Skill 추론 불가
- 영어 입력은 Orchestrator Agent 선택 규칙이 Workmate를 선택하지 않아 E2E 미실행
- 상태: M5.1 재작업
- 자동 진행 중단 사유: PASS가 아닌 결과 및 미실행 항목 존재
- 재개 조건: UTF-8 실행 환경과 Workmate Skill ID를 포함한 A2A 요청 또는 Orchestrator 선택 규칙 제공
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-124744/result.md`](docs/evidence/M5/M5.1/runs/20260814-124744/result.md)
## 최신 상태 보정: M5.1 UTF-8 E2E 회의 Skill 입력 차단

- 실행 ID: `20260814-125500`
- `weekly_report`: PASS
- `rank_priorities`: PASS
- `analyze_meeting`: FAIL (필수 회의 입력/Fixture 없음)
- `search_meetings`: FAIL (회의 Chunk/DB Fixture 없음)
- 상태: M5.1 재작업
- 자동 진행 중단 사유: FAIL 결과 존재
- 재개 조건: 회의 분석 입력과 검색 Chunk Fixture를 포함한 Orchestrator 요청 재검수
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-125500/result.md`](docs/evidence/M5/M5.1/runs/20260814-125500/result.md)
## 최신 상태 보정: M5.1 회의 Skill E2E 입력·환경 차단

- 실행 ID: `20260814-130100`
- `analyze_meeting`: meeting_id·최종 Transcript Fixture 필요
- `search_meetings`: query·user_id·PostgreSQL pgvector Fixture·Embedding Provider 필요
- 담당 Orchestrator는 현재 text Part만 전송
- 상태: M5.1 재작업
- 자동 진행 중단 사유: 필수 업무 payload와 실제 검색 실행 환경 미제공
- 재개 조건: Skill payload 전달 및 PostgreSQL/Provider 환경 제공
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-130100/result.md`](docs/evidence/M5/M5.1/runs/20260814-130100/result.md)
## 최신 상태 보정: M5.1 Compose Agent 이름 호환성 차단

- 실행 ID: `20260814-125821`
- Docker Compose 이미지 빌드·Workmate healthcheck·Main health: PASS
- Orchestrator Task 호출: FAIL (`KeyError('Workmate AI')`)
- 원인: 담당 Orchestrator가 Agent Card 표시 이름을 registry 키로 직접 사용
- 상태: M5.1 재작업
- 자동 진행 중단 사유: 종단 간 호출 FAIL
- 재개 조건: Compose에 legacy adapter 포함 또는 Orchestrator registry 키 매핑 수정
- 증빙: [`docs/evidence/M5/M5.1/runs/20260814-125821/result.md`](docs/evidence/M5/M5.1/runs/20260814-125821/result.md)
### 2026-08-14 M5.1 Compose adapter 재검수

- Compose에 Workmate Agent와 legacy adapter를 포함하고 담당 Orchestrator의 `daily_briefing` 호출을 재검수했다.
- 결과: Compose 기동, Agent Card discovery, Task `succeeded`, `daily_briefing` 변환은 PASS.
- M5.1 전체는 미승인: `analyze_meeting` Transcript/meeting fixture와 `search_meetings` PostgreSQL pgvector/Embedding Provider가 필요하다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-040128/result.md`
### 2026-08-14 M5.1 회의 분석·검색 Fixture 검토

- 회의 Workflow와 legacy adapter 단위 계약 테스트 6개 PASS, compileall/diff-check PASS.
- 운영 E2E는 BLOCKED: 담당 Orchestrator가 text Part만 보내 `meeting_id`·Transcript·query를 구조화해 전달하지 않으며 PostgreSQL/Embedding Provider도 Compose에 없음.
- 가짜 Fixture/Embedding 응답은 실제 업무 완료 조건을 위반하므로 추가하지 않았다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-040343/result.md`
### 2026-08-14 Orchestrator payload 확장성 분석

- 담당 Orchestrator는 현재 `TaskRequest.request: str`와 문자열 `message` 중심이라 회의 분석·검색 필수 payload를 전달할 수 없다.
- adapter만의 추정/고정 Fixture 주입은 실제 업무 Workflow 완료 조건을 위반한다.
- Orchestrator 내부에 선택적 `skill_id`·`payload`를 추가하는 방식이면 Workmate 공개 Schema 변경 없이 확장 가능하다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-040500/result.md`
### 2026-08-14 Orchestrator payload 확장 계획

- 기존 문자열 요청을 유지하면서 선택적 `skill_id`·`payload`를 A2A `data` Part로 전달하는 계획을 작성했다.
- Skill별 필수 필드, 하위 호환, 멱등성, 사용자 범위, 회의/검색 E2E 검수 조건을 정의했다.
- 계획 문서: `docs/m5.1-orchestrator-payload-plan.md`
### 2026-08-14 Orchestrator 구조화 payload 구현

- 담당 Orchestrator에 선택적 `skill_id`·`payload`와 Skill별 필수 필드 검증을 추가했다.
- A2A HTTP+JSON `data` Part에 payload를 보존하고 기존 문자열 요청은 하위 호환했다.
- Contract/API 테스트 28개 PASS, compileall/diff-check PASS.
- Push와 실제 Compose 회의 E2E는 미실행이며 M5.1은 검수 중이다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-041045/result.md`
### 2026-08-14 구조화 payload Compose E2E

- Orchestrator → adapter → Workmate까지 구조화 payload 전달은 확인했다.
- `analyze_meeting`은 meeting fixture/최종 Transcript 부재로 FAIL, `search_meetings`는 DATABASE_URL·PostgreSQL/Embedding 부재로 FAIL.
- PASS가 아닌 결과가 있어 M5.1 자동 승인·다음 작업 착수를 중단했다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-041359/result.md`
### 2026-08-14 Compose DB/Fixture 검수

- PostgreSQL/pgvector 기동과 비식별 meeting/MeetingChunk fixture 초기화는 PASS했다.
- `analyze_meeting`은 `OPENAI_API_KEY` 부재, `search_meetings`는 Embedding Provider 환경변수 부재로 FAIL.
- 실제 Provider 없이 가짜 응답을 넣지 않아 M5.1 승인과 자동 진행을 중단했다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-041919/result.md`
### 2026-08-14 실제 Provider Compose 재검수

- Provider 환경변수 존재 여부는 확인했으나 실제 LLM 호출과 Embedding 호출이 실패했다.
- PostgreSQL/pgvector와 Fixture는 정상이다.
- `analyze_meeting`: `INTERNAL: unknown exception`, `search_meetings`: `embedding provider request failed`.
- M5.1 승인·자동 진행은 중단했다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-042329/result.md`
### 2026-08-14 Provider endpoint 최소 검증

- OpenAI 표준 모델명 `gpt-4.1-mini`, `text-embedding-3-small`은 각각 성공했으며 Embedding은 1536차원을 반환했다.
- Workmate 설정의 `openai/` 접두사 모델명은 HTTP 400을 반환했다.
- 네트워크/Token이 아니라 모델명 계약 불일치로 판단했고, 모델 계약을 임의 변경하지 않아 검수를 중단했다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-042501/result.md`
### 2026-08-14 실제 Provider 회의 Skill E2E 성공

- 모델명 매핑 후 실제 OpenAI LLM·Embedding Provider를 사용했다.
- `analyze_meeting`과 `search_meetings`가 Orchestrator → adapter → Workmate → PostgreSQL/pgvector 경로에서 모두 `TASK_STATE_COMPLETED`.
- 검색 응답에 `meeting-chunk:00000000-0000-0000-0000-000000000201` 출처가 포함됐다.
- M5.1 전체는 기존 5개 Skill 회귀와 UI/운영 검수가 남아 있어 아직 승인하지 않았다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-043018/result.md`
### 2026-08-14 5개 Skill Compose 회귀 통과

- `daily_briefing`, `rank_priorities`, `weekly_report`, `analyze_meeting`, `search_meetings` 모두 `succeeded`.
- PostgreSQL/pgvector Fixture와 실제 OpenAI LLM/Embedding Provider를 사용했다.
- M5.1은 5개 Skill 회귀 기준을 통과했으나 UI/운영 육안 검수와 최종 인수 조건이 남아 검수 중이다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-043605/result.md`
### 2026-08-14 UI/운영 Route 검수

- Main/Workmate/adapter UI·Agent Card Route는 HTTP 200, Compose 내부 readiness는 200.
- 호스트 8001은 기존 로컬 프로세스가 점유하여 readiness가 503으로 보였고, Compose 컨테이너 내부는 정상이다.
- 브라우저 제어 도구 부재로 실제 육안 캡처 검수는 미실행되어 M5.1 자동 승인을 보류했다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-044111/result.md`

### 2026-08-14 UI 통합 재검수 재실행

- 기존 8001 점유 Python 프로세스를 종료하고 Compose를 재기동했다.
- Workmate `/internal/skill-chat`, `/tasks`, `/weekly-report`와 Orchestrator `/health`, `/api/agents`가 모두 HTTP 200으로 응답했다.
- 브라우저 제어 도구가 없어 클릭·입력·레이아웃 육안 검수와 캡처는 수행하지 못했다.
- M5.1 상태는 수동 검수 미완료로 `검수 중`을 유지한다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-134348/result.md`

### 2026-08-14 M5.1 UI 육안 검수 승인

- 사용자가 Skill 검증, Task 관리, 주간 보고 화면의 캡처를 제출했다.
- 입력·실행 결과·Task 목록·보고서 섹션·Markdown 출력·레이아웃을 확인했고 모두 PASS로 판정했다.
- Bearer Token은 마스킹되어 Secret 노출이 없었다.
- M5.1을 완료로 갱신하고 승인 실행을 `20260814-135200`으로 기록했다.
- 증빙: `docs/evidence/M5/M5.1/runs/20260814-135200/result.md`

### 2026-08-14 M5.2 계획 착수

- M5.2 운영 공통 기능을 인증·권한, 오류·부분 실패, 재시도·멱등성, 로그·상관관계, Health·Readiness, 통합 회귀의 6개 백로그로 분해했다.
- 구현 전 계획 상태로 `M5.2`를 `진행`으로 기록했으며, 검수 결과가 없어 완료·승인 처리하지 않았다.
- 계획·증빙: `docs/evidence/M5/M5.2/README.md`

### 2026-08-14 M5.2-01 인증·권한 검수 중단

- Workmate 인증·권한 Contract Test 19건은 PASS했다.
- Orchestrator backend 테스트는 시스템 Python의 `pygments` 누락으로 FAIL했고, 프로젝트 가상환경도 없어 안전한 재시도를 수행하지 못했다.
- M5.2-01은 `재작업`으로 유지하며 다음 백로그를 착수하지 않는다.
- 증빙: `docs/evidence/M5/M5.2/runs/20260814-140210/result.md`

### 2026-08-14 M5.2-01 인증·권한 재검수 승인

- 테스트용 임시 의존성 경로를 정리한 뒤 Workmate 19건과 Orchestrator 25건이 모두 PASS했다.
- 누락·불일치 인증 401 및 사용자 범위 격리를 확인해 M5.2-01을 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.2/runs/20260814-141005/result.md`

### 2026-08-14 M5.2-02 오류 변환·부분 실패 승인

- Workmate 부분 실패·warnings 테스트 4건과 Orchestrator 오류 매핑 테스트 25건이 모두 PASS했다.
- 400/401/404/502/503 매핑과 Provider 부분 결과 보존을 확인해 M5.2-02를 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.2/runs/20260814-142015/result.md`

### 2026-08-14 M5.2-03 재시도·멱등성 승인

- Orchestrator A2A Client에 timeout·429·502·503·504 재시도와 `Retry-After` 처리를 구현했다.
- 동일 `messageId` 유지, Workmate Provider 재시도, PostgreSQL 메시지 멱등성을 SKIP 없이 검증해 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.2/runs/20260814-143015/result.md`

### 2026-08-14 M5.2-04 로그·상관관계 승인

- Main Agent와 Workmate에 `X-Request-ID` 응답·로그 상관관계를 구현했다.
- Workmate 4건, Orchestrator 27건, diff 검사가 PASS했고 Secret 비노출을 확인해 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.2/runs/20260814-144010/result.md`

### 2026-08-14 M5.2-05 Health·Readiness 승인

- Main Agent에 `/health/live`, `/health/ready`를 추가하고 Workmate Health 계약을 검증했다.
- Workmate 5건과 Orchestrator 28건이 PASS했고 설정 누락 503·정상 readiness 200을 확인해 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.2/runs/20260814-145010/result.md`

### 2026-08-14 M5.2-06 통합·회귀 승인

- Workmate 운영 공통 회귀 29건과 Orchestrator 회귀 36건이 모두 PASS했고 PostgreSQL Fixture 연결로 SKIP을 제거했다.
- 구문·diff 검사와 Secret 비노출도 PASS하여 M5.2-06 및 M5.2 전체를 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.2/runs/20260814-150010/result.md`

### 2026-08-14 M5.3 계획 착수

- Compose 통합을 환경 변수·Secret, 네트워크·의존성, PostgreSQL/pgvector Fixture, Smoke Test, 통합 회귀의 5개 백로그로 분해했다.
- M5.3을 `진행`으로 기록했으며 실제 Compose 검수 전에는 완료·승인하지 않는다.
- 계획·증빙: `docs/evidence/M5/M5.3/README.md`

### 2026-08-14 M5.3-01 환경 변수·Secret 경계 승인

- Compose 필수 토큰 누락 시 config exit 1, 정상 설정 시 exit 0을 확인했다.
- `config --quiet`를 사용해 렌더링 Secret을 저장·출력하지 않는 방식으로 검수하여 M5.3-01을 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.3/runs/20260814-151010/result.md`

### 2026-08-14 M5.3-02 네트워크·서비스 의존성 승인

- Compose 서비스 health, PostgreSQL `pg_isready`, 내부 DNS, adapter→Workmate HTTP, Main→adapter Agent Card 연결이 모두 PASS했다.
- M5.3-02를 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.3/runs/20260814-152010/result.md`

### 2026-08-14 M5.3-03 PostgreSQL·pgvector Fixture 승인

- `pg_trgm`·`vector` 확장과 meetings/meeting_chunks/tasks Fixture 1/1/1을 확인했다.
- 전체 서비스를 재기동한 뒤 healthy 및 동일 데이터 counts를 확인해 M5.3-03을 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.3/runs/20260814-153010/result.md`

### 2026-08-14 M5.3-04 Smoke Test 중단

- Compose 내부 서비스·DNS·Health·Agent Card는 PASS했다.
- 기존 로컬 Python 프로세스가 호스트 8001을 점유해 Workmate 호스트 readiness가 503으로 실패했다.
- M5.3-04를 `재작업`으로 기록하고 M5.3-05 착수를 중단했다.
- 증빙: `docs/evidence/M5/M5.3/runs/20260814-154010/result.md`

### 2026-08-14 M5.3-04 재검수 중단

- 기존 프로세스 정리, Docker 컨테이너 재생성, 이미지 재빌드 후에도 호스트 8001 readiness가 503으로 반복됐다.
- 컨테이너 내부 readiness는 200이며 다른 8001 Docker 컨테이너는 없었다.
- 동일 원인에 대한 안전한 해결책이 소진되어 자동 진행을 중단했다.
- 증빙: `docs/evidence/M5/M5.3/runs/20260814-155010/result.md`

### 2026-08-14 M5.3-04 Smoke Test 승인

- Docker Desktop의 8001 전달 충돌을 임시 `8011:8001` 호스트 매핑으로 우회했다.
- Workmate readiness 200, Main readiness 200, Adapter Agent Card 200 및 4개 서비스 상태를 확인해 M5.3-04를 자동 승인했다.
- 운영 포트 8001 자체는 별도 환경 정리 항목으로 남겼다.
- 증빙: `docs/evidence/M5/M5.3/runs/20260814-160010/result.md`

### 2026-08-14 M5.3-05 Compose 통합·회귀 검수 재작업

- Compose 서비스·Agent Card는 PASS했지만 5개 Skill 통합 호출은 모두 HTTP 500으로 실패했다.
- 원인은 UUID가 아닌 `fixture-user` 입력과 컨테이너의 `EMBEDDING_BASE_URL`·`EMBEDDING_API_KEY` 미설정이다.
- M5.3-05와 M5.3 전체를 `재작업`으로 유지하고 M5.4는 착수하지 않는다.
- 증빙: `docs/evidence/M5/M5.3/runs/20260814-161010/result.md`

### 2026-08-14 M5.3-05 Compose 통합·회귀 승인

- 유효한 사용자·회의 Fixture UUID와 세션 Embedding 설정으로 5개 Skill을 재검수했다.
- Compose 서비스, Agent Card, 5개 Skill 호출이 모두 PASS하여 M5.3-05와 M5.3을 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.3/runs/20260814-162010/result.md`
- 다음 착수 항목: M5.4 시나리오 시연

### 2026-08-14 M5.4 시나리오 시연 승인

- Main Orchestrator에서 8개 업무 시나리오를 실행하고 모두 `succeeded`를 확인했다.
- 실제 retry endpoint의 `running → succeeded` 전이도 확인해 M5.4를 자동 승인했다.
- 증빙: `docs/evidence/M5/M5.4/runs/20260814-170010/result.md`
- 다음 착수 항목: M5.5 최종 인수

### 2026-08-14 Orchestrator 채팅 Skill 라우팅 연동

- 다른 팀원의 `AI-agent_game_platform` Orchestrator에 Workmate UI를 연동하는 과정에서, 채팅 경로가 `skill_id`를 고르지 못하고 항상 `daily_briefing`으로 고정되는 문제를 발견했다.
- Orchestrator 저장소는 읽기 전용 제약이 있어 Workmate `tools/m51_legacy_adapter.py`에서 사용자 문장 기준으로 5개 Skill을 재판정하고, `search_meetings`의 `query`·`analyze_meeting`의 `meeting_id`를 자동으로 채우도록 구현했다. 필수 입력이 없으면 upstream `INTERNAL` 대신 `400 INVALID_ARGUMENT`로 먼저 거른다.
- 검증 중 `search_meetings`·`analyze_meeting`이 실제로는 `TASK_STATE_COMPLETED`인데 응답이 비어 있는 별도 결함을 발견했다. 원인은 `app/a2a/runtime.py`의 `_artifact_parts`가 구조화 `data`만 있는 결과에서 `text` Part를 생략해, `text`만 읽는 Orchestrator Client가 결과를 놓치는 것이었다. `markdown` 없는 구조화 결과에도 `text/plain` Part를 함께 싣도록 고쳤다(공개 데이터 계약은 유지, Part 하나만 추가하는 하위 호환 변경).
- 신규 단위 테스트 7건 포함 `tests/` 전체 141 passed, 10 skipped, 0 failed.
- 사용자가 Docker Desktop을 기동한 뒤 4개 서비스 Compose E2E를 실행해 6개 채팅 시나리오(5개 Skill 라우팅 + 필수 입력 누락 400) 전부 의도대로 동작함을 확인했다. Secret·Token 로그 비노출도 확인하고 컨테이너를 정리했다.
- 회의 선택 UI(회의 목록 → `meeting_id` 전달)와 Orchestrator 대시보드 패널의 실데이터 연동은 이번 범위에 포함하지 않았다.
- 증빙: `docs/evidence/M5/runs/20260814-201500/result.md`

### 2026-08-15 `workmate-ui` 폐기 결정 번복, `workmate-ui` 정리

- `workmate-ui`(내부 검증 UI Shell)를 폐기된 로컬 샘플로 취급하던 2026-08-12 결정을 번복했다. 2단계
  계획으로 진행한다: 1차로 `docs/workmate-ui-integration-gaps.md`의 갭 목록대로 완성하고 완성본은
  개인용으로 계속 보관(keep)한다. 2차로 완성된 화면·로직을 팀 공통 Orchestrator UI 양식에 맞게 조정해
  M5 통합에 반영한다 — 처음부터 새로 만드는 대신 완성본을 이식하는 방식이다.
- `01-overview-architecture.md`, `06-delivery-plan.md`, `07-technical-specification.md`,
  `09-ui-design.md`, `AGENTS.md`, `workmate-ui/README.md`의 "폐기된 샘플" 문구를 위 2단계 계획에
  맞게 갱신했다.
- `workmate-ui`와는 별도로 존재하던 `workmate-ui`(오케스트레이터를 거치지 않고 `workmate-agent`를
  직접 호출하는 독립 정적 HTML/JS UI, 미추적 로컬 디렉터리)는 두 UI가 혼동을 일으켜 폐기하고 삭제했다.
  기존 설계 문서 어디에도 `workmate-ui`(단독)를 참조하는 곳은 없었다.
- `workmate-ui`의 Superproject 편입 방식(Submodule 등록 vs 일반 추적 디렉터리)은 아직 미확정이며
  후속 결정 필요.

### 2026-09-23 LangGraph 전면 전환 계획 확정과 W0 기준선

- `docs/30-langgraph-migration-plan.md`를 **빅뱅 전면 재작성** 기준으로 개정했다. 초판의 "병행 경로 +
  `WORKMATE_USE_LANGGRAPH` 플래그 + 단계별 점진 전환"은 폐기했다.
- 전제 확정: 운영 배포 중이 아니고, 호환보다 LangGraph 설계 정합성을 우선한다.
- 결정 확정: D1=B(공개 계약까지 `interrupt`/`resume`로 개편), D2=A(계약 스냅샷 선추출),
  D3=B(`langchain-openai` 도입), D4=A(`weekly_classification`→`app/domain/`,
  `external_sync`→`app/sync/` 이동), D5=A(폴링 유지 + `INPUT_REQUIRED` 분기),
  D6=B(`a2a_checkpoints` DROP Migration 포함).
- 동결 구역: `app/workflows/` 전체, `app/a2a/runtime.py`, `app/internal_chat.py`,
  `workmate-ui/app/views/AssistantDrawer.tsx`, `tools/m51_legacy_adapter.py`.
- W0 기준선: `uv run python -m unittest discover -s tests -v` → 440 tests, OK, skipped 12, 실패 0.
  건너뛴 12개는 전부 `WORKMATE_TEST_DATABASE_URL` 미설정으로 SKIP된 PostgreSQL 통합 테스트다.
- 실행 환경 복구(자동 재작업): `.venv`가 사라진 `C:\Python312`(3.12.4)를 가리켜 `uv run`이 실패했다.
  `uv python install 3.12`(3.12.13) → `uv venv --clear --python 3.12` → `uv sync`로 복구했고
  `uv.lock` 의존성 버전은 변경하지 않았다.
- 상태: 검수 중. 자동 진행 보류 사유 — (1) `app/workflows/assistant_router.py`,
  `app/workflows/meetings.py`, `app/meeting_answer.py`와 테스트 2개의 **미커밋 변경**이 남아 있어 전환
  기준 Commit이 확정되지 않았다(다른 작업자의 구현이라 자동 커밋하지 않는다). (2) PostgreSQL 테스트 DB
  미구성으로 해당 경로 기준선이 없다.
- 다음 착수 항목: W1 계약 스냅샷 추출 — 옛 구현이 살아 있는 동안에만 가능하므로 W3보다 먼저 끝낸다.
- 증빙: `docs/evidence/langgraph/W0/runs/20260923-065508/result.md`

### 2026-09-23 LangGraph W0 완료 — 기준선 확정

- 미커밋 변경 5개 파일을 사용자 결정에 따라 2개 로컬 커밋으로 고정했다(`274c204` proposal_id Schema
  누락 수정, `8043c1e` 회의 검색 LLM 근거 답변 + warning 분류). 원격 Push는 하지 않았다.
- PostgreSQL 테스트 DB를 구성했다 — Docker Desktop 기동 후 `pgvector/pgvector:pg16` 컨테이너를
  `55432` 포트로 띄우고 `WORKMATE_TEST_DATABASE_URL`을 설정했다. `migrations/004_search_data.sql`이
  `vector`·`pg_trgm` 확장을 요구해 표준 postgres 이미지가 아닌 pgvector 이미지를 쓴다.
- 확정 기준선: `workmate-agent@8043c1e`, **440 passed / 0 failed / 0 skipped**(20.2s).
  1차 실행에서 SKIP됐던 PostgreSQL 통합 테스트 12개가 전부 실행·통과했다.
- 상태: W0 완료(자동 승인 — 검수 항목 4개 전부 PASS, 미실행·수동 검수·차단 없음).
- 다음 착수 항목: W1 계약 스냅샷 추출. 옛 구현이 살아 있는 동안에만 가능하므로 W3보다 먼저 끝낸다.
- 증빙: `docs/evidence/langgraph/W0/runs/20260923-065508/result.md`

### 2026-09-23 LangGraph 단계별 상세 계획 문서 10건 작성

- `docs/30-langgraph-migration-plan.md` §5의 작업 순서 표가 단계당 한 줄뿐이라 착수 시점마다 설계를
  다시 해야 하는 문제가 있어, W0~W9를 각각 `30-0`~`30-9` 상세 계획 문서로 분리했다.
- 공통 구성(소프트웨어 공학 표준): 문서 정보 → 목적·범위(In/Out) → 선행 조건(Entry criteria) →
  요구사항(`Wn-Rxx`) → 설계 → 작업 분해(`Wn-Txx`, WBS) → 검증 설계(`Wn-Vxx`) → 추적성 매트릭스
  (R↔T↔V) → 완료 정의(Exit criteria) → 위험과 완화 → 롤백·중단 기준 → 참조.
- 단계별 핵심 제약을 문서에 고정했다. W1은 옛 구현 생존 기간에만 가능(시한 제약)하고 비결정 값
  정규화 규칙을 정의한다. W2는 HTTP 4xx/5xx 비재시도 구분 보존이 D3=B의 최대 위험이다. W5는
  오류→HTTP 매핑(422/503)과 A2A 이벤트 순서가 중단 기준이다. W6은 계약 설계안 C1~C5가 별도 승인
  대상이고 오케스트레이터 저장소 수정은 금지다. W7의 DROP Migration은 비가역이라 마지막 커밋으로
  분리한다. W9는 스냅샷 diff에서 "설명 불가 차이 0"을 완료 조건으로 둔다.
- `docs/README.md` 문서 색인과 `docs/30-langgraph-migration-plan.md` §5 표에서 10개 문서로 연결했다.
- 상태: 계획 문서 작성 완료. 다음 착수 항목은 W1(계약 스냅샷 추출)이며 `30-1` 문서의 WBS를 따른다.

### 2026-09-28 W2 상세 계획을 절 단위 문서 12건으로 분해

- `docs/30-2-w2-graph-foundation.md`의 최상위 번호 절 12개를 각각 `30-2-1`~`30-2-12` 문서로 분해했다.
  상위 문서는 요약·색인으로 남기고, 충돌 시 상세 문서를 기준으로 한다.
- 분해 과정에서 코드 전수 조사를 수행해 **재시도 정책 불일치**를 발견했다. OpenAI 호환
  `/chat/completions` 직접 호출은 6곳·5개 모듈이고 환경변수 계열이 `OPENAI_*`와 `LLM_*`로 갈려 있는데,
  재시도 정책도 서로 다르다 — `assistant_router`는 3회·네트워크 오류만 재시도하고 HTTP 4xx/5xx를
  제외하지만(2026-08-19 DNS 대응), `weekly_report._call_llm_with_retry`는 2회 시도하며
  `LLMProviderError`(timeout·429·5xx·Schema 오류)를 재시도 대상에 포함한다.
- 이에 따라 W2 설계를 조정했다. `llm.py`에 RetryPolicy를 **두 종류**(`NETWORK_ONLY_RETRY`,
  `PROVIDER_ERROR_RETRY`) 정의하고 지점별 동작 보존을 기본 방침으로 삼는다. 정책 통일은 동작 변경이라
  전환 범위에서 제외하고 W9 후속 백로그로 넘긴다.
- `docs/30-langgraph-migration-plan.md` §9-6("네트워크 오류만 재시도")은 `assistant_router` 계열에만
  해당하므로 W2 완료 시 서술을 정밀화해야 한다(`30-2-9` §2.5에 기록).
- `email_action_items.py`는 `daily_briefing`(범위 내)과 `dev_gmail_sync_api`·`proposal_api`(범위 밖)가
  공유하므로 LLM 경로를 교체하지 않고 Graph 노드가 기존 함수를 그대로 호출한다(`30-2-5` §5.3).
- 상태: 계획 문서 작성 완료. 다음 착수 항목은 W1(계약 스냅샷 추출), 그다음이 W2다.

### 2026-09-28 W3 상세 계획을 절 단위 문서 12건으로 분해

- `docs/30-3-w3-skill-subgraphs.md`의 최상위 번호 절 12개를 `30-3-1`~`30-3-12`로 분해했다(2,335줄).
  상위 문서는 요약·색인으로 남긴다.
- 분해를 위해 Skill 11개의 구현 구조를 조사했고, 계획에 없던 사실 두 가지를 발견했다.
  1. **`daily_briefing`에 숨은 부작용이 있다.** 내부에서 `rank_priorities` Workflow를 호출하며
     (`daily_briefing.py:139, 238`), 그 과정에서 `snapshot_repository.save_all()`로 우선순위
     Snapshot이 저장된다(`priority.py:123`). 이 부작용은 `daily_briefing` 응답에 드러나지 않아
     **W1 계약 스냅샷으로 검출되지 않는다.** 두 Skill이 저장소를 통해 결합돼 있어, Domain 함수
     호출로 바꾸면 `rank_priorities`의 `changes` 값이 달라진다.
  2. **보조 Skill 5종은 UI REST 함수를 호출하는 얇은 래퍼다.** `review_action_items`→
     `action_item_api`, `review_proposal`→`proposal_api`, `manage_tasks`→`task_api`를 지연 import로
     호출한다. 이 모듈들은 W3 범위 밖이라 억지로 쪼개면 얻는 것 없이 Checkpoint I/O만 늘어난다.
- 이에 따라 요구사항 2건과 검증 1건, 설계 결정 5건을 추가했다.
  - `W3-R10` 숨은 부작용 보존, `W3-R11` 확인 흐름 동결(W6까지 `pending_action` 방식 유지)
  - `W3-V11` 부작용 DB 직접 검증 — 스냅샷으로 잡히지 않는 항목의 전용 검증
  - `W3-D1` 부작용 유지(Subgraph 호출), `W3-D2` 주입 핸들, `W3-D3` 공통 State + `input` 하위 dict,
    `W3-D4` 얇은 래퍼 3노드 최소 분해, `W3-D5` 확인 판정과 실행 사이 노드 분리(W6 대비)
- W3의 "잘 되는 것처럼 보이는 실패" 두 가지를 중단 기준에 반영했다 — 숨은 부작용 소실과 `user_id`
  조건 누락은 전용 검증 없이는 영원히 통과하므로, 하나라도 FAIL이면 W3 전체를 미완료로 본다.
- 상태: 계획 문서 작성 완료. 다음 착수 항목은 W1(계약 스냅샷 추출).

### 2026-09-29 W0~W9 전 단계를 절 단위 문서로 분해 완료

- `docs/30-0`~`30-9`의 모든 최상위 번호 절을 독립 문서로 분해했다. 총 **135개 파일, 26,906줄**.
  상위 10개 문서는 요약·색인으로 남기고 각 문서 상단에 하위 문서 표를 넣었다.
- 공통 구성: 문서 정보 → 목적·범위 → 선행 조건 → 요구사항(`Wn-Rxx`) → 설계 → WBS(`Wn-Txx`) →
  검증 설계(`Wn-Vxx`) → 추적성 매트릭스 → 완료 정의 → 위험 등록부(`Wn-Kxx`) → 롤백·중단 → 참조.
  단계별 고유 절: W0 §10 실행 결과, W1 §12 후행 전달, W6·W9 §10 승인 경계, W9 §12 후속 백로그.
- **분해 과정의 코드 조사에서 계획에 없던 사실 네 건을 발견했고, 해당 단계 설계를 수정했다.**
  1. **재시도 정책이 하나가 아니다**(W2). `assistant_router`는 3회·네트워크 오류만 재시도하고 HTTP
     4xx/5xx를 제외하지만, `weekly_report._call_llm_with_retry`는 2회 시도하며 429·5xx·Schema 오류를
     재시도 대상에 포함한다. 계획서 §9-6("네트워크 오류만 재시도")은 전자에만 해당한다. → RetryPolicy
     2종 정의(W2), 통일하지 않고 각각 보존(W8-D1), §9-6 서술 정밀화를 완료 조건에 추가.
  2. **`daily_briefing`에 숨은 부작용이 있다**(W3). 내부에서 `rank_priorities` Workflow를 호출해
     우선순위 Snapshot이 저장된다. 응답에 드러나지 않아 계약 스냅샷으로 검출되지 않는다.
     → 결정 W3-D1(Subgraph 호출로 부작용 유지) + 전용 검증 W3-V11(DB 직접 확인).
  3. **멱등성이 절반만 구현돼 있다**(W4). `record_message()`는 중복 여부를 bool로 반환하지만
     `runtime.py:223`이 반환값을 무시한다. 같은 `message_id` 재전송이 재실행되고, UI REST는
     `message_id`가 매 요청 새 uuid라 아예 발동하지 않는다. → 결정 W4-D1(96번 설계대로 구현, 동작
     변경) + 전용 검증 W4-V3, W5에서 외부 노출 시점 기록.
  4. **보조 Skill 5종은 UI REST 함수를 호출하는 얇은 래퍼다**(W3). 업무 로직이 W3 범위 밖 모듈에
     있어 억지로 쪼개면 얻는 것 없이 Checkpoint I/O만 늘어난다. → 결정 W3-D4(3노드 최소 분해).
- 이 네 건은 전부 **계약 스냅샷으로 검출되지 않는 변경**이다. 단계마다 "스냅샷이 못 잡는 변경"을
  식별하고 전용 검증을 붙이는 것이 이 전환의 패턴이 됐다(W3-V11, W4-V3, W5-V1-4, W8-V7).
- 승인이 필요한 단계는 둘로 정리됐다. **W6**(계약안 C1~C5 착수 전 승인 + UI 육안 검수)과
  **W9**(문서 개정 + Merge·Push). 나머지 8단계는 검증이 전부 PASS면 자동 승인 대상이다.
- W9에 후속 백로그 10건을 이유·우선순위와 함께 정리했다(`30-9-12`). 중간 우선순위 3건은 HTTP 429
  재시도, `AUTH_REQUIRED` 상태 도입, 오케스트레이터 대응이다.
- `docs/README.md` 색인을 갱신했다.
- 상태: 계획 문서 전체 완료. 다음 착수 항목은 **W1(계약 스냅샷 추출)**이며 `30-1-6` WBS를 따른다.

### 2026-09-29 ReAct Agent 전환 계획 추가 (W10) + LangGraph 증거 산출물 보강

- 사용자 요청으로 **ReAct Agent 전환 계획**을 `docs/30-10-w10-react-agent.md`로 추가했다.
  W0~W9 전환의 일부가 아니라 **W9 완료·승인 후 별도로 착수하는 후속 작업**이다 — 전환의 완료 기준이
  "의도적으로 바꾼 것 외에는 아무것도 안 바뀌었다"(§9-7)인데 ReAct를 섞으면 그 판정이 불가능해진다.
- 착수 전 확정할 결정 7건(D7-1~D7-7)과 선행 승인 2건을 명시했다.
  - **05번 문서 §1 "LLM과 코드의 책임" 표 개정 승인** — 현재 표는 LLM 역할을 "요약·자연어 표현·
    추출·문장 작성·근거 기반 답변"으로 한정하고 "도구를 고르고 실행 순서를 정한다"가 없다. ReAct는
    이 칸을 넓히는 일이라 문서 개정이 선행돼야 한다.
  - 공개 계약 재변경 — `executed_skill_id`가 단수인데 ReAct는 도구를 여러 번 부를 수 있다. W6에서
    한 번 바꾼 계약을 또 바꾸는 것이라 UI·어댑터·02번 문서가 다시 영향받는다.
- **최대 위험은 `_SKILL_CATALOG` 134줄의 규칙 유실**(W10-K1)이다. `week_of` 상대 표현 계산,
  `[분석 완료]` 회의 재분석 금지, 회의 특정 실패 시 되묻기 등 실사용 피드백으로 한 줄씩 쌓인 규칙이
  도구 설명으로 흩어지면서 조용히 사라질 수 있다. → W10-T2(규칙 전수 목록화 + 회귀 케이스)를
  착수 관문으로 두고, 이걸 건너뛰면 W10을 시작하지 않는다.
- 설계 결정 W10-D1: **계산 규칙을 프롬프트가 아니라 코드로 내린다.** 현재 LLM이 `week_of`를 계산하는데
  (프롬프트에 "오늘-7일" 규칙), 도구가 기본값을 계산하고 LLM은 의도(`relative="last_week"`)만
  전달하게 바꾼다. 05번 문서 §1("날짜 범위 계산은 코드")과도 일치한다.
- ReAct가 실제로 해결하는 문제도 기록했다 — 현재 `_ARGUMENTS_SCHEMA`가 **15개 필드를 평평하게**
  갖고 전부 `required`다(OpenAI strict 모드 제약). 코드가 null을 걸러낸다. 도구별 개별 Schema를
  쓰면 이 구조적 문제가 해소되고 인자 오배치가 불가능해진다.
- 신규 검증 W10-V9(선택 안정성): 같은 입력 10회 실행 시 같은 도구 시퀀스가 나오는 비율. 현재 구조는
  사실상 10/10(temperature=0 단발 분류)이고, 이 수치가 떨어지는 것이 ReAct의 대가다. 6/10 이하면
  설계 재검토.
- **함께 보강한 것 — LangGraph 증거 산출물.** "그림만으로는 LangGraph인지 알 수 없다"는 지적에 따라
  구조를 증명하는 산출물을 세 단계에 추가했다.
  - `W4-R11` / `W4-V11`: `graph.get_graph().draw_mermaid()`와 `get_state_history()` 출력을 증빙에.
    손으로 그린 그림과 달리 Graph 객체에서 나온 것이라 코드와 100% 일치한다.
  - `W6-V7-7`: **확인 대기 중 서버 재시작 → resume** 육안 검수. 다른 케이스는 현재의 재요청 방식도
    전부 통과하지만, 서버 재시작을 끼우면 Checkpointer 없이는 통과할 수 없다.
  - `W9-R11`: 개념↔코드 대조표 + **"안 쓰는 것"** 목록(Agent·Tool 추상화·LCEL·Retriever·LangSmith)을
    97번 문서 개정에 포함. 과장하지 않기 위한 경계 기록이다.
- 상태: W10 계획 수립 완료(착수 전 승인 대기). 전환의 다음 착수 항목은 여전히 **W1**이다.

### 2026-09-29 — W10(ReAct Agent 전환) 계획 13개 절별 문서로 분해

- 사용자 요청("w10도 상세계획으로 쪼개")으로 `docs/30-10-w10-react-agent.md` 561줄을 W0~W9와 동일한
  13절 체계로 분해했다. 신규 13개 + 상위 문서 재작성, 총 **2,981줄**.
  - `30-10-1-document-info.md` — 문서 정보·용어·**왜 별도 단계인가**·착수 금지 조건
  - `30-10-2-scope.md` — 목적, 좋아지는 것·나빠지는 것, 범위 내(S1~S9)·외, **후속 백로그 관계**
  - `30-10-3-entry-criteria.md` — W10-E1~E6, 05번 개정이 왜 최우선인가
  - `30-10-4-requirements.md` — **신규 작성** W10-R1~R13 + 요구사항 간 충돌 3건
  - `30-10-5-design.md` — W10-D1~D8, ReAct Graph, State, 도구 Schema, 카탈로그 이전, HITL, 예산
  - `30-10-6-wbs.md` — W10-T1~T11 + 의존 그래프 + 산출물 체크리스트
  - `30-10-7-verification.md` — W10-V1~V10 상세 케이스(V3-1~V3-7, V5-1~V5-6, V6-1~V6-4, V7-1~V7-5)
  - `30-10-8-traceability.md` — **신규 작성**. 요구사항↔작업↔검증, **카탈로그 규칙 추적표 형식**,
    05번 개정↔구현 추적, 계약 변경 누적(W6+W10)
  - `30-10-9-exit-criteria.md` — E-1~E-7, 자동 승인 불가 사유, 승인 요청 시점 셋
  - `30-10-10-approval.md` — **D7-1~D7-7 전부 + 근거**, **05번 §1 개정안 전문**, 대안(D7-7 B안) 비교
  - `30-10-11-risks.md` — W10-K1~K8 + 스냅샷 대응 + 우회 시험
  - `30-10-12-rollback.md` — 부분 롤백(W10-T4는 유지), 중단 vs 재작업 구분, 금지되는 해결 방법
  - `30-10-13-references.md` — 읽을 지점, **"안 쓰는 것" W9 대비 변화표**
- **새로 만든 내용 둘.** 원본에 없던 절이다.
  - **요구사항 W10-R1~R13** — 원본은 설계에서 요구사항으로 바로 넘어갔다. R3(권한 인자 State 주입),
    R6(결정적 규칙 불변), R13(스냅샷 23건 불변)을 명시적 요구사항으로 올려 검증에 1:1 연결했다.
  - **추적성** — 카탈로그 134줄의 각 규칙이 어디로 갔고 무엇이 지키는지 추적하는 표 형식을 정의했다.
    이 단계 증빙의 중심은 코드 변경 기록이 아니라 `catalog-rules.md`(규칙 이전 대장)다.
- **승인 시점을 명확히 했다.** 사용자 질문("d7을 왜 지금 확정해야하지")에 따라 `30-10-10` §1.1에
  **지금 확정하지 않는 이유**를 기록했다. D7-2·D7-3·D7-4·D7-6은 W2~W6을 거치면서 판단 근거가 채워지는
  결정이고, 05번 문서를 미리 고치면 W1~W9 동안 설계 문서가 구현보다 앞서 나간다(W9가 없애려는 문제와
  같은 종류). 계획서 §5 주석과 `docs/README.md`에도 반영했다.
- 승인 지점은 셋이다 — 착수 전(D7 + 05번 개정), 계약 확정(`executed_skill_ids` 설계안), 완료 시(육안
  검수 + 비용 수용 판단). W6이 둘이었던 것보다 하나 많다.
- `AGENTS.md`는 수정 제안이 없다. 충돌 지점을 찾지 못했다 — 점수·근거 ID·`user_id`는 W10 이후에도
  코드가 소유하고 W10-V5·V6이 강제한다(`30-10-10` §3.4).
- 교차 참조 정정: 계획서 §5 주석·§10, `30-9-12-backlog.md`, `docs/README.md`. 절 번호가 바뀌었으므로
  옛 "§11"·"§3·§4" 참조를 파일 링크로 교체했다. 링크 검사 결과 깨진 링크 0.
- 자동 재작업 착수: 해당 없음(문서 작업).
- 상태: **W10 계획 분해 완료. 착수는 W9 완료 후.** 전환의 다음 착수 항목은 여전히 **W1(계약 스냅샷
  추출)** 이며, `docs/30-1-6-wbs.md`가 작업 목록이다. W1은 별도 승인이 필요하지 않다.

### 2026-09-30 — 표준 방식 확인 결과: 계획 W6·W8·W10 설계에 영향 (계획 미개정, 사용자 결정 대기)

- 사용자 요청으로 **표준 방식 학습 랩**을 `C:\dev\langgraph-standard-lab`(저장소 밖)에 만들고
  실제 실행해 확인했다. LangGraph **1.2.12** / langchain **1.4.3** / langchain-core **1.6.6** / Python 3.12.
  예제 6개 전부 `exit=0`. 실제 `OPENAI_API_KEY`로 호출했다(소액 과금).
- **계획서와 어긋나는 사실 둘을 확인했다. 계획 문서는 아직 고치지 않았다.**

**(1) `create_react_agent`가 `langchain` 본체로 이사했다.**

```
from langgraph.prebuilt import create_react_agent   # DeprecationWarning, v2.0에서 제거
from langchain.agents import create_agent           # 현재 표준
```

즉 **표준 에이전트 진입점을 `langchain` 본체가 소유한다.** 세션 중 내가 "본체는 레거시
체인·AgentExecutor라 필요 없다"고 설명한 것은 0.x 기준이었고 1.x에서는 맞지 않는다.
`docs/30-9-4-requirements.md` W9-R11의 "안 쓰는 것" 목록에서 `AgentExecutor`는 여전히 유효하지만,
`langchain` 본체를 의존성에서 제외한다는 전제는 재검토 대상이다.

**(2) W6·W8·W10이 직접 만들기로 한 것이 표준 middleware로 제공된다.** 실행으로 확인했다.

| 계획 항목 | 표준 대체 | 확인 내용 |
| --- | --- | --- |
| W6 확인 게이트 + `_requires_confirmation()` 4종 | `HumanInTheLoopMiddleware(interrupt_on={...})` | 승인·거부·조건부(`when=lambda`) 3종 모두 동작. 거부 시 루프가 끝나지 않고 모델이 대안 제시 |
| W10-D5 루프 예산(반복 6회) | `ModelCallLimitMiddleware(run_limit=)` | `run_limit=1`로 종료 확인. 사유가 AIMessage로 남는다 |
| W10 "같은 도구 연속 2회" | `ToolCallLimitMiddleware(tool_name=, run_limit=)` | **병렬 호출은 함께 센다.** 상한 초과 시 둘 다 차단하고 사유를 ToolMessage로 모델에 전달 |
| W8 재시도 2종 | `ToolRetryMiddleware(tools=[...], retry_on=)` | 도구별로 정책을 나눠 끼울 수 있다. 3회째 성공 확인 |

- `interrupt` payload 실제 구조: `{"action_requests": [{name, args, description}], "review_configs": [{action_name, allowed_decisions}]}`.
  재개는 `Command(resume={"decisions": [{"type": "approve"}]})`이며 **`decisions` 키로 감싸야 한다**(리스트를 바로 넘기면 TypeError).
- **D7-2=B(커스텀 StateGraph)는 여전히 성립하지만 이유가 달라진다.** "표준이 안 해 주니까"가 아니라
  (a) 도구 호출과 무관한 노드(`validate_contract`·`persist_result`)가 필요하고 (b) Skill 11개를
  Subgraph로 나눠 Root에서 분기해야 하고 (c) A2A Task Store와 맞물려야 하기 때문이다. workmate는
  셋 다 해당한다.
- 부수 확인: `langchain-openai`는 `langchain-core`만 전이 의존으로 끌어온다(본체 미포함).
  `langchain` 본체를 추가해도 기존 충돌은 없었으나, 이 랩은 `a2a-sdk`·`fastapi`를 쓰지 않으므로
  workmate에서의 충돌 위험은 별도로 확인해야 한다(W2-T1).
- 랩 구성(1,002줄, 계획 문서 0줄): `domain.py`(도구 6개) · `model.py`(실제/대본 모델) ·
  `01` prebuilt → `02` Checkpointer → `03` HITL → `04` astream 3모드 → `05` 커스텀 StateGraph +
  `draw_ascii`/`draw_mermaid` → `06` 예산·재시도. `langgraph.json`으로 `langgraph dev` Studio 준비됨.
- **미결정 사항.** 위 발견을 계획에 반영할지는 사용자 결정 대기다. 후보는 (a) 계획 유지 +
  이유만 정정 (b) W6·W8·W10을 middleware 기반으로 재설계 (c) 진입점을 `create_agent`로 바꾸고
  Root Graph만 커스텀. 어느 쪽이든 `docs/30-2-5-design.md` §6 의존성, `docs/30-6-5-design.md`,
  `docs/30-8-5-design.md`, `docs/30-10-5-design.md`, `docs/30-10-10-approval.md` D7-2 개정이 필요하다.
- 자동 재작업 착수: 아니오 — 계획 개정은 범위·설계 변경이라 사용자 승인 대상.
- 상태: **전환의 다음 착수 항목은 여전히 W1(계약 스냅샷 추출).** 이 발견은 W1에 영향을 주지 않는다.

### 2026-09-30 — 위 학습 랩 삭제, 표준 방식 영향도 조사로 전환

- 직전 항목의 `C:\dev\langgraph-standard-lab`은 **사용자 요청으로 전부 삭제했다.** 별도 학습
  프로젝트는 의도와 달랐다. 해당 경로는 더 이상 존재하지 않으므로 직전 항목의 랩 구성·파일 목록은
  이력으로만 읽는다. **단, 거기서 실행으로 확인한 라이브러리 사실(표준 진입점 이사, middleware 제공
  범위, interrupt payload 구조)은 유효하다.**
- 사용자 의도는 **기존 `workmate-agent`를 표준 방식으로 바꿀 때의 영향도 조사**다. 코드·계획 문서는
  변경하지 않았다(조사만).

**조사 결과 — 구조적 충돌의 핵심**

| | 표준 방식 | workmate 현재 |
| --- | --- | --- |
| 외부 공개면 | 에이전트 1개 | Agent Card에 **Skill 11개** |
| 무엇을 할지 결정 | 항상 LLM | 호출자가 `skill_id`로 지정 |
| 응답 | messages(+`structured_response`) | **A2A Artifact** (DataPart JSON + text/markdown) |
| 상태 | messages 중심 | `data`·`markdown`·`warnings`·`task_state` |

**호출자별 영향도 (실측)**

| 호출자 | 현재 호출 | 표준(단일 에이전트)로 바꿀 때 |
| --- | --- | --- |
| 오케스트레이터 | 어댑터가 문장을 `assistant_ask`로 넘긴다(`tools/m51_legacy_adapter.py`) | **영향 거의 없음 — 이미 단일 진입점** |
| `AssistantDrawer.tsx` | `assistant_ask` + `analyze_meeting`·`manage_tasks`·`review_action_items` | 중간 |
| `Briefing.tsx` | `daily_briefing`·`rank_priorities` | **버튼=Skill. 에이전트를 끼울 이유 없음** |
| `Report.tsx` | `weekly_report` | 동상 |
| `Search.tsx` | `search_meetings` | 동상 |
| `Archive.tsx` | `analyze_meeting` | 동상 |

**기술적 충돌 셋**
1. 표준에서 최종 응답은 LLM이 만든다. workmate `data`는 Domain 계산값(점수·`source_refs`)과 같아야
   하므로 도구 반환값이 LLM을 우회해야 한다 → 에이전트 뒤 노드가 필요 → StateGraph로 내려감.
2. `create_agent(response_format=)`는 에이전트당 하나. Skill 11개의 서로 다른 Schema를 못 담는다.
3. `warnings` 누적 채널이 AgentState에 없다. `daily_briefing` 3층 부분 실패가 표현되지 않는다.

**영향 규모 (실측)**

| 구분 | 대상 | 규모 |
| --- | --- | --- |
| 전면 교체 | `app/workflows/` 9개 모듈 | 3,144줄 |
| 전면 교체 | `registry.py` | 92줄 |
| 수정 | `runtime.py`·`internal_chat.py`·`persistence.py` | 1,476줄 |
| 재작성 | 의존 테스트 18개 파일 | 4,675줄 (전체 64개 중) |
| **무변경이어야 함** | `repositories`·`domain`·`providers` 19개 파일 | 3,047줄 |
| 수정 | `workmate-ui` 5화면 | Drawer 필수, 나머지 4개는 선택 |
| **승인 필요** | 오케스트레이터 저장소 | 어댑터 흡수 우선 시도 |

**결론** 표준 방식이 맞는 범위는 **`assistant_ask` 하나**이며, 이는 계획 W10과 같은 결론이다.
새로 얻은 것은 (a) 진입점을 `create_agent`로 둘 수 있다(D7-2=A 재검토 여지) (b) HITL·루프 예산·
재시도를 middleware로 대체해 직접 만들 코드가 줄어든다는 점이다.

- 자동 재작업 착수: 아니오 — 조사만 수행. 계획 개정은 사용자 결정 대기.
- 상태: **다음 착수 항목은 여전히 W1(계약 스냅샷 추출).**

### 2026-09-30 — 표준 Agent 영향도 조사 완료 + 의존성 충돌 검증 (docs/31 신규)

- 사용자 요청으로 (1) 미검증 4건을 실제로 검증하고 (2) 조사 결과를 문서로 기록했다.
  **`workmate-agent` 코드와 계획서 W0~W10은 변경하지 않았다.**
- 신규 문서: [`docs/31-standard-agent-impact-analysis.md`](docs/31-standard-agent-impact-analysis.md)
  (조사·기록용, 구현 항목 아님). `docs/README.md`에 색인 추가.

**검증 1 — 의존성 충돌: 없음 (가장 큰 미확인 위험 해소)**

workmate 고정 의존성 11개를 그대로 둔 임시 프로젝트에 LangChain 스택 5개(`langgraph`,
`langgraph-checkpoint-sqlite`, `langgraph-checkpoint-postgres`, `langchain-openai`, `langchain`)를
더해 `uv lock`으로 해석하고, **대조군**(LangChain 없이 재해석)과 비교했다.

| 비교 | 결과 |
| --- | --- |
| 해석 | 91개 패키지, exit 0 |
| **LangChain 추가가 밀리게 하는 기존 패키지** | **0개** |
| 재해석만으로 밀리는 것(LangChain 무관) | 17개 |
| 고정(`==`) 버전 9개 | **전부 유지** (`a2a-sdk 1.1.2`·`fastapi 0.116.1`·`psycopg 3.2.10` 등) |
| `a2a-sdk` + `fastapi` + `langchain` 동시 import | **성공** |

**별건 발견 — 현재 `uv.lock`이 낡았다.** 위 17개는 LangChain과 무관하게 누구든 `uv lock`을 다시
돌리면 밀린다. 그중 **`oauthlib` 3.3.1 → 4.0.0 (메이저)** 가 있어 Google OAuth 경로 영향 가능성이
있다. W2-T1에서 lock이 갱신될 때 함께 드러나므로 그 시점 확인 항목이다.

**버전 상한** workmate의 `requires-python = ">=3.12,<3.13"`에서 `langchain`이 **1.3.2**,
`langgraph`가 **1.2.2**로 해석된다(상한 없이는 1.4.3 / 1.2.12). middleware 14개로 필요한 넷은 전부
포함.

**검증 2~4**

| 항목 | 결과 |
| --- | --- |
| `ModelRetryMiddleware` | 존재 확인. `max_retries`·`retry_on`·backoff. **`tools=` 없음** — 모델 호출 전체에 적용 |
| `response_format` | **에이전트당 1개**(단일 타입). Skill 11개의 서로 다른 Schema를 담을 수 없음 확인 |
| **`create_agent`를 Subgraph로 합성** | **두 방식 모두 성공** — (a) wrapper 노드(부모 State가 `messages` 불필요) (b) `add_node("agent", inner)` 직접(`messages` 채널 겹칠 때). 반환 타입이 `CompiledStateGraph`다 |

세 번째가 A안 성립의 관건이었고 **성립한다.** `WorkmateState`가 `messages`를 갖지 않아도 wrapper
노드로 `assistant_ask` 분기에 끼울 수 있다.

**영향도 조사 결과 (요약)**

- `assistant_router.py` 937줄 → **~354줄 삭제, 146줄 재작성, 137줄(`_SKILL_CATALOG`) 분해 이전, ~180줄 유지**
- UI: [`workmate-format.ts`](workmate-ui/lib/workmate-format.ts) 460줄 중 **~55줄만** 챗봇 계약(나머지 405줄은 버튼 화면용, 무변경)
- 테스트: `test_assistant_router.py` 1,019줄 전면 재작성 등 **1,829줄**
- **정정** Drawer는 `assistant_ask` **하나만** 호출한다. 앞서 "3개를 직접 부른다"고 기록한 것은 틀렸다 — 주석과 확인 대기 판정용 문자열 비교였다.
- **미해결** 오케스트레이터 어댑터의 `INPUT_REQUIRED` 처리. 지금은 `pending_action`을 무시해도 Task가 완료되지만, interrupt로 멈추면 Task가 끝나지 않는다.

**W1~W10 변경 필요 여부**

| 단계 | 변경 |
| --- | --- |
| W1 계약 스냅샷 | **불필요** (+케이스 2건 권장: `history_context`, `context_reference`) |
| W2 Graph 골격 | **필요** — 의존성에 `langchain` 본체, 재시도 소유권 |
| W3·W4·W7 | 작음 |
| W5 진입점 교체 | **불필요** |
| W6 interrupt·계약 | **큼** — C2·C3를 자유롭게 설계할 수 없다(middleware가 모양을 정함) |
| W8 재시도·관측 | **필요** — 에이전트 안쪽은 middleware, 나머지 10개 Skill은 노드 `RetryPolicy`. **두 체계 공존** |
| W9 문서·증빙 | **필요** — W9-R11 "안 쓰는 것"에서 `langchain` 본체 제외 전제가 깨짐 |
| W10 ReAct | **큼** — D7-2 재검토, 예산 4종이 middleware. **단 W10-T2(카탈로그 137줄)와 W10-V5(결정적 규칙 보존)는 그대로 필요** |

**아직 확인하지 않은 것** 440개 테스트 통과 여부(해석 성공 ≠ 런타임 호환, `oauthlib` 4.0 포함),
`AsyncPostgresSaver`와 `psycopg 3.2.10` 실연결, `with_structured_output(method=)` 동등성,
middleware와 A2A `TaskUpdater` 이벤트 순서 상호작용.

- 자동 재작업 착수: 아니오 — 조사·문서화만. 선택지 A/B/C 판단과 계획 개정은 사용자 결정 대기.
- 상태: **다음 착수 항목은 여전히 W1(계약 스냅샷 추출).** 이 조사는 W1에 영향을 주지 않는다.

### 2026-11-03 저장소 구성 정리와 원격 Push

- **사용자 요청으로 원격 Push를 수행했다.** AGENTS.md의 "백로그 완료 시 로컬 커밋만" 규칙에 대한
  명시적 예외(사용자 요청)에 해당한다. 강제 Push는 하지 않았고 기존 커밋을 덮어쓰지 않았다.
- `workmate-ui`를 Submodule로 확정했다(`https://github.com/sjseo1221/workmate-ui-demo.git`).
  2026-09-05 기록에서 "Submodule 등록 vs 일반 추적 디렉터리 미확정"으로 남겨 둔 결정을 Submodule로
  닫았다.
- `workmate-ui`의 화면 소스가 그때까지 **미추적 상태**였다 — `app/views/` 12개와 `lib/` 8개가 한 번도
  커밋된 적이 없었다. 3개 커밋으로 고정했다(로그 ignore → 구현 → 테스트).
  검증: `npm run build` + `node --test` **71개 통과**, `eslint` 경고 0.
- `AI-agent_game_platform` Submodule을 **추적에서 제거**했다(사용자 결정). `.gitmodules` 항목과
  gitlink를 함께 지웠다. 상대 저장소(`harrys-enjoy`)는 전혀 수정하지 않았다 — AGENTS.md 금지 사항
  준수. 연동 작업을 다시 참조해야 하면 `git submodule add`로 되살린다.
- 오케스트레이터 연동 문서 `docs/19`~`docs/25`, `docs/m5.1-orchestrator-payload-plan.md`와
  `a2a-smoke-test/` 11개 파일 삭제를 확정 커밋했다(사용자 결정).
- `.gitignore` 보강: `.local-dev/`(RSA 개인키·발급 JWT 포함), 기동 로그 6종,
  `Workmate-AI-portfolio*.pdf`.
- 캡처용 dev 파라미터 패치(`?token=`·`?view=`·`?q=`·`?chat=`)를 `workmate-ui` 4개 파일에서
  **되돌린 뒤** Push했다. 재사용이 필요하면 `.local-dev/ui-capture-patch/` 사본으로 재적용한다.
- Push 전 검증: `workmate-agent` **440 tests OK (skipped 12)**,
  `git diff --check` 통과, 비밀정보 스캔(`sk-`·`AIza`·PRIVATE KEY·`client_secret`·Bearer) 무검출.
  건너뛴 12개는 `WORKMATE_TEST_DATABASE_URL` 미설정 PostgreSQL 통합 테스트다 — W0 완료 시점에는
  pgvector 컨테이너를 띄워 440개 전부 통과시켰고, 이번 Push 검증에서는 컨테이너를 띄우지 않았다.
- 자동 재작업 착수: 아니오 — 저장소 구성 작업이며 코드 동작 변경이 없다.
- 상태: **다음 착수 항목은 여전히 W1(계약 스냅샷 추출).** 옛 구현이 살아 있는 동안에만 가능하다.
