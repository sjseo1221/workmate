# Workmate AI 개발 인수인계

이 문서는 저장소의 현재 작업 상태와 다음 착수 항목을 기록한다. 전체 개발 계획은 [`docs/06-delivery-plan.md`](docs/06-delivery-plan.md), 하위 마일스톤의 검수 결과는 `docs/evidence/Mx/Mx.y/result.md`를 기준으로 한다.

## 1. 현재 상태

- 현재 마일스톤: M0 계약·검증 기반
- 진행 중 하위 마일스톤: M0.1 A2A·Artifact 계약
- 현재 스프린트: Sprint 1 — M0.1 Workflow·영속 Task 경계 준비
- 상태: 검수 중
- 마지막 갱신: 2026-08-12 22:22 Asia/Seoul
- 마지막 작업자: Codex
- 기준 Git Commit: `85a4036` (`workmate-agent`)
- 기준 브랜치: `feat/M0.1-01-sdk-runtime`

## 2. 완료된 항목

| 항목 | 상태 | 승인 증빙 |
|---|---|---|
| M0.1-01 SDK HTTP+JSON 런타임 부트스트랩 | 완료 | `docs/evidence/M0/M0.1/runs/20260812-210001/result.md` |
| M0.1-02 공개 A2A 전송 타입 Contract Test | 완료 | `docs/evidence/M0/M0.1/runs/20260812-204500/result.md` |
| M0.1-03 Workflow·영속 Task 경계 구현 | 검수 중 | `docs/evidence/M0/M0.1/runs/20260812-222254/result.md` |

완료 항목은 명시 승인 또는 규칙에 따른 묵시 승인이 기록된 `result.md` 경로만 연결한다. 자동 승인 조건을 충족하지 않은 단순 구현 완료나 일부 테스트 실행만으로 완료 처리하지 않는다.

## 3. 현재 진행 중인 작업

- 백로그 ID: M0.1-03
- 작업: Workflow·영속 Task 경계 PostgreSQL 연결 검수
- 담당자: Codex
- 구현 중인 파일: `workmate-agent/app/a2a/persistence.py`, `app/workflows/registry.py`, `migrations/001_a2a_infrastructure.sql`
- 완료된 부분: M0.1-01 SDK 런타임, M0.1-02 공개 전송 타입·Contract Test 승인, M0.1-03 로컬 영속 경계·Registry·Migration 구현
- 남은 부분: Docker daemon 정상화 후 PostgreSQL 실제 연결·Migration 실행 검증과 최종 Dockerfile 재빌드, M0.1-04 통합 계약 검수
- 현재 테스트 결과: 단위·Contract·Persistence·Migration Test 12개 PASS, PostgreSQL 통합 테스트는 `DATABASE_URL` 미설정으로 SKIP; 최종 Dockerfile 재빌드와 새 이미지 Health·Agent Card 재검증은 Docker daemon 응답 지연으로 보류
- 마지막 실행 명령: `uv lock --check`, `uv sync --frozen`, 테스트 13개(12 PASS·1 SKIP), compileall, `git diff --check`
- 최신 실행 ID: `20260812-222254`
- 최신 승인 실행 ID: `20260812-210001` (M0.1-01), `20260812-212244` (M0.1-02)

## 4. 다음 작업

1. Docker daemon 정상화 후 PostgreSQL `DATABASE_URL` 환경에서 M0.1-03 Migration·Task Store 실제 연결 검증과 최종 Dockerfile 재빌드
2. M0.1-04 Agent Card·5개 Skill·Artifact·인증·오류·Adapter·Streaming 순서·Subscribe 상태·Route allowlist 통합 Contract Test
3. 담당자 배정 후 M0.2-01 기존 모델·OAuth 평가 이력 검수는 M0.1과 병행 가능

## 5. 차단 사항

| 항목 | 원인 | 필요한 조치 | 해소 상태 |
|---|---|---|---|
| Docker Compose 검증 환경 | Dockerfile의 지원되지 않는 `uv sync --system` 옵션 | `--system` 제거, `.venv` PATH 연결 후 이미지 빌드·기동·Health·Agent Card 재검수 PASS | 해소 |
| 루트 문서 Git 추적 | Superproject·Submodule·원격 기준선 필요 | `origin/main`에 기준 Commit Push 완료 | 해소 |
| PostgreSQL·최종 Docker 재검수 | Docker CLI의 컨테이너 실행·Compose build 요청이 제한 시간 내 완료되지 않음 | Docker daemon 정상 응답 후 격리 PostgreSQL 컨테이너와 최종 이미지 재검증 | 진행 |

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
- UI 책임: 폐기된 `workmate-ui-demo`는 구현·검수에 사용하지 않는다. M0.4 내부 검증 UI는 `workmate-agent`가 제공하는 최소 개발자 페이지이며, 다섯 개 제품 화면은 M5의 팀 공통 Orchestrator UI가 담당한다.
- Agent Card Cache: MVP는 `Cache-Control: public, max-age=3600`만 계약으로 유지하고 별도 `ETag`는 요구가 생길 때 추가
- Streaming·Subscribe: `/message:stream` 첫 Task와 후속 상태·Artifact 순서, 활성 Task Subscribe의 현재 Snapshot·신규 이벤트, Terminal Task 오류, 비허용 `GET` Route 차단을 검증
- Mock 응답: 운영 실행 경로에는 Mock Handler·고정 샘플 응답·Mock fallback을 두지 않고 Mock 여부는 단위·계약 테스트의 Fixture·로그·증빙에만 기록
- Git 구조: `C:\dev\workmate`는 문서·증빙 Superproject, `workmate-agent`만 기존 이력을 보존한 Submodule로 관리한다. `workmate-ui-demo`는 추적하지 않는 로컬 샘플이다.
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

- 구현 코드: 구현 전
- Schema 또는 Migration: `docs/schemas/a2a-artifact.schema.json`, `docs/schemas/workmate-skill-schemas.schema.json`; A2A 인프라 Migration은 M0.1-03에서 생성 예정
- 단위 테스트: 구현 전
- 통합 테스트: M0.1-04에서 생성 예정
- UI 테스트: M0.4에서 생성 예정
- Fixture/입력: M0.1-04에서 승인 Schema를 통과하는 5개 Skill Fixture 생성 예정
- 모델 평가 Case: M0.2에서 기존 평가 원본 연결 예정
- 모델 평가 결과: M0.2에서 기존 평가 원본 승인 예정
- 최신 실행 로그: `docs/evidence/M0/M0.1/runs/20260812-222254/result.md`
- 최신 실행 결과: 로컬 테스트 12 PASS·1 SKIP, PostgreSQL·최종 Docker 재검증 보류
- 최신 결과 문서: `docs/evidence/M0/M0.1/README.md`

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
- 정의된 검증 명령이 전부 PASS이고 미실행·수동 검수·차단 항목이 없으면 `자동 승인(검증 명령)`으로 묵시 승인하고 계획표·증빙·HANDOFF를 완료로 갱신한다. 공개 Schema·데이터 모델 변경과 외부 OAuth·UI·모델 평가처럼 명시 승인이 필요한 항목은 자동 승인하지 않는다.
- API Key, Token, Presigned URL, 실제 회의 음성은 커밋·Push하지 않는다.

## 11. 갱신 이력

| 날짜 | 작업자 | 변경 내용 | 기준 Commit |
|---|---|---|---|
| 2026-08-12 | Codex | 권장사항 1~4·6 반영: 입력 Schema, A2A/M1 DB 책임, Package·의존성, Subscribe·Route allowlist, UI 경계와 문서 상태 정합화; 사용자별 Task 권한 결정은 변경하지 않음 | 루트 Git 미구성 |
| 2026-08-12 | Codex | M0.1-04, M0.2~M0.4 백로그, Task 복구·Mock Schema·Adapter·운영 검증 계획 반영 | 루트 Git 미구성 |
| 2026-08-12 | Codex | M0.1 공식 SDK·전송 타입·Workflow 경계 구현 계획 확정, 코드 구현은 원복 | |
| 2026-08-12 | Codex | 구현 전 권장안 반영: Superproject 구조, M0.1 백로그 경계, Streaming·Subscribe 검증, 현재 Task Snapshot 방식, Legacy Smoke 정리와 마일스톤별 Mock 종료 조건 확정 | 루트 Git 미구성 |
| 2026-08-12 | Codex | `workmate-ui-demo`를 폐기된 로컬 샘플로 구현·검수·Submodule 범위에서 제외하고 M0.4를 `workmate-agent` 최소 개발자 검증 페이지로 변경 | 루트 Git 미구성 |
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
