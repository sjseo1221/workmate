# 화면, 개발 계획, 테스트

[← 이전](05-ai-security-operations.md) · [목차](README.md)

## 1. 최소 화면

1. **홈/브리핑**: 오늘 일정, 메일 할 일 신호, 경고, Top 3, 새로고침
2. **주간 보고서**: 기간, 섹션별 보고서, Markdown 복사
3. **회의**: 회의 목록, 실시간 녹음·파일 업로드, 처리 상태, 전체 회의록, 분석 직후 후보 검토/승인
4. **회의 검색**: 질문, 답변, 클릭 가능한 출처
5. **할 일 관리**: 목록, 등록·수정 폼, 상태 변경, 삭제 확인

별도 우선순위 관리 화면은 만들지 않는다. 홈의 Top 3에서 재계산과 변경 사유를 제공한다.

## 2. 마일스톤 개발 계획

구현 시 모델·검색·녹음 계약은 [구현·검증 가이드](12-implementation-verification-guide.md)를 기준으로 한다. 마일스톤은 기능 묶음이 아니라 검수 가능한 결과 단위로 종료한다. 각 마일스톤의 완료 기준과 증빙이 충족되기 전에는 다음 마일스톤을 완료로 표시하지 않는다.

| ID  | 마일스톤         | 목표                                                     | 기존 Phase | 선행 조건  | 상태      |
| --- | ---------------- | -------------------------------------------------------- | ---------- | ---------- | --------- |
| M0  | 계약·검증 기반   | A2A·모델·OAuth 계약과 내부 Skill 검증 챗봇 확보          | Phase 0    | 없음       | 완료      |
| M1  | 데이터·우선순위  | Task, Gmail, Calendar를 통합하고 Top 3를 결정적으로 계산 | Phase 1    | M0         | 완료      |
| M2  | 브리핑·주간 보고 | 일일 브리핑과 근거 기반 주간 보고서 제공                 | Phase 2    | M1         | 진행      |
| M3  | 회의 분석        | 파일·실시간 녹음에서 STT·Action Item·Task 승인까지 연결  | Phase 3    | M0, M1     | 완료      |
| M4  | 회의 검색        | Embedding·Trigram RRF·HNSW와 출처 응답 완성              | Phase 4    | M3         | 완료      |
| M5  | 통합·시연        | Orchestrator·UI·Docker Compose 종단 간 인수 테스트       | Phase 1~4  | M2, M3, M4 | 대기      |

구현 상태는 `대기 → 진행 → 검수 중 → 완료`로 관리한다. 평가 결과, 테스트 로그, 화면 캡처 또는 API 응답은 해당 마일스톤의 증빙으로 연결한다.

상위 마일스톤의 선행 조건은 **진입 게이트**다. 하위 마일스톤 표의 선행 항목은 가장 가까운 기술 의존성만 표시하므로, 상위 진입 게이트를 완화하지 않는다. 예를 들어 M1.1의 직접 기술 선행은 M0.1이지만 M1 구현 상태를 `진행`으로 바꾸려면 M0 전체가 완료되어야 한다. 다만 `M0.4-03`처럼 실제 업무 장기 Task가 연결되기 전에는 완료할 수 없는 UI 검수 백로그는 차단 해소에 필요한 선행 업무 백로그의 분석·구현·검수를 예외적으로 진행할 수 있다. 이 예외는 M0 전체 완료를 의미하지 않으며, 차단 해소 후 M0.4-03 잔여 검수와 M0 전체 완료 검수를 별도로 수행한다. M0.4-03은 테스트 전용 실행 환경과 사용자 육안 승인으로 완료되었고, M0 통합 검수 `20260813-214548`도 PASS하여 M0 전체가 완료되었다.

M3 상위 상태는 M3.1~M3.6 각 README의 `latest_approved_run_id`가 존재하고 최신 실행이 PASS일 때만 `완료`로 갱신한다. 현재 여섯 하위 마일스톤이 모두 이 조건을 충족해 M3를 완료 처리했다. M5 상위 진입은 M2·M3·M4가 모두 완료되어야 하므로, M2.4의 사용자 육안 검수가 승인되기 전까지 M5는 `대기`로 유지한다.

### 2.1 하위 마일스톤 추적표

담당자와 완료 예정일은 팀 작업 시작 시 채운다. 하위 마일스톤은 하나의 담당 단위와 하나의 검수 결과를 갖도록 유지한다.

| ID   | 하위 목표         | 주요 산출물                                                                 | 선행                         | 담당 | 완료 예정일 | 완료 기준·증빙                                                             | 상태 | 다음 착수 항목           |
| ---- | ----------------- | --------------------------------------------------------------------------- | ---------------------------- | ---- | ----------- | -------------------------------------------------------------------------- | ---- | ------------------------ |
| M0.1 | A2A·Artifact 계약 | Agent Card, Message/Task/Artifact Schema·A2A 인프라 Task Store              | 없음                         | 미정 | 미정        | SDK REST Route·AgentExecutor·Contract Test·Streaming·재시작 복구 검증 결과 | 완료 | M0.2 모델·OAuth 확정 |
| M0.2 | 모델·OAuth 확정   | LLM·Embedding·STT·OAuth 설정과 평가 이력                                    | 없음                         | 미정 | 미정        | 기존 평가 승인·OAuth HISTORY·미검증 위험 기록                              | 완료 | M0.3 내부 챗봇 API |
| M0.3 | 내부 챗봇 API     | Skill 목록·메시지·장기 Task 조회 API                                        | M0.1                         | 미정 | 미정        | 5개 Skill·인증·장기 Task·부분 실패 API 검증                                | 완료 | M1.4 Task 제안           |
| M0.4 | 내부 챗봇 UI      | `workmate-agent` 최소 개발자 페이지의 Skill 선택·자연어/JSON 입력·결과 화면 | M0.3                         | 미정 | 미정        | 5개 Skill·Artifact·상태·오류 화면 검수                                     | 완료 | M1.4 Task 제안 |
| M1.1 | 업무 DB 기반      | Task·Gmail·Calendar PostgreSQL Migration·Repository·샘플 데이터             | M0.1                         | 미정 | 미정        | 업무 Migration·Repository 테스트                                           | 완료 | M1.2 외부 소스 연동 |
| M1.2 | 외부 소스 연동    | Gmail·Calendar Adapter·정규화·동기화 Cursor                                 | M1.1                         | 미정 | 미정        | Gmail/Calendar 실제 조회·Watch·Cursor 테스트 결과                          | 완료 | M1.3 Task 관리 |
| M1.3 | Task 관리         | 등록·조회·수정·Soft Delete API/UI                                           | M1.1                         | 미정 | 미정        | CRUD·중복·삭제 테스트                                                      | 완료 | M1.4 Task 제안 |
| M1.4 | Task 제안         | 메일·일정 SSE 제안·승인·무시·중복 검증                                      | M1.2, M1.3                   | 미정 | 미정        | 승인·중복 방지 테스트                                                      | 완료 | M1.5 우선순위·브리핑 |
| M1.5 | 우선순위·브리핑   | 점수 계산·Top 3·오늘 브리핑                                                 | M1.2, M1.3                   | 미정 | 미정        | 결정성·Top 3·Snapshot·부분 실패·날짜 경계 테스트                          | 완료 | M2.1 주간 데이터 분류 |
| M2.1 | 주간 데이터 분류  | 완료·진행·지연·이슈 집계                                                    | M1.1, M1.2                   | 미정 | 미정        | 분류 결과와 source ID                                                      | 완료 | M2.2-01 다음 주 계획 근거 추출 |
| M2.2 | 계획·근거 추출    | 다음 주 계획과 제안/확정 구분                                               | M2.1                         | 미정 | 미정        | 근거 없는 계획 차단 테스트                                                 | 완료 | M2.3-01 백로그 정의 필요 |
| M2.3 | 보고서 생성       | LLM 보고서·Schema 검증·Artifact                                             | M2.2                         | 미정 | 미정        | [통합 회귀 107개 PASS](evidence/M2/M2.3/result.md)                          | 완료 | M2.4-01 백로그 정의 필요 |
| M2.4 | 보고서 UI         | 기간 선택·섹션 표시·Markdown 복사                                           | M2.3                         | 미정 | 미정        | [`M2.4 수동 검수 절차`](13-manual-verification-guide.md#2-m24-03-주간-보고서-ui-육안-검수) | 보류 | 사용자 추후 육안 검수 |
| M3.1 | 회의 입력         | 회의 생성·파일 업로드·메타데이터                                            | M1.1                         | 미정 | 미정        | MIME·크기·중복 테스트                                                      | 완료 | [M3.1 증빙](evidence/M3/M3.1/README.md) |
| M3.2 | 실시간 녹음       | RecordingSession·WebSocket·Chunk 재연결                                     | M3.1                         | 미정 | 미정        | ACK·Gap·중복·재연결 테스트                                                 | 완료 | [M3.2 증빙](evidence/M3/M3.2/README.md) |
| M3.3 | STT·Transcript    | 임시/최종 STT·timestamp 원문 저장                                           | M3.1, M3.2                   | 미정 | 미정        | STT 평가·Transcript 검증                                                   | 완료 | [M3.3 증빙](evidence/M3/M3.3/README.md) |
| M3.4 | 회의 분석         | 통합 요약·Action Item·근거 구간                                             | M3.3                         | 미정 | 미정        | Action Item Schema·근거 테스트                                             | 완료 | [M3.4 증빙](evidence/M3/M3.4/README.md) |
| M3.5 | 승인·Task 등록    | Action Item 검토·승인·멱등 Task 생성                                        | M3.4, M1.3                   | 미정 | 미정        | 동일 Action Item 중복 승인 테스트                                          | 완료 | [M3.5 증빙](evidence/M3/M3.5/README.md) |
| M3.6 | R2 연동           | Storage Adapter·Presigned URL·Object Key                                    | 백엔드 준비 후 M3.1          | 미정 | 미정        | PUT/HEAD/GET/checksum/Lifecycle                                            | 완료 | [M3.6 증빙](evidence/M3/M3.6/README.md) |
| M4.1 | 검색 데이터       | MeetingChunk·Embedding 저장·재임베딩                                        | M3.3                         | 미정 | 미정        | `vector(1536)` Migration                                                   | 완료 | [M4.1 증빙](evidence/M4/M4.1/README.md) |
| M4.2 | Trigram 검색      | pg_trgm Keyword 검색·metadata 필터                                          | M4.1                         | 미정 | 미정        | Keyword 검색 테스트                                                        | 완료 | [M4.2 증빙](evidence/M4/M4.2/README.md) |
| M4.3 | Hybrid 검색       | Dense·Trigram RRF·HNSW                                                      | M4.2                         | 미정 | 미정        | Recall·Index Scan·지연 측정                                                | 완료 | [M4.3 증빙](evidence/M4/M4.3/README.md) |
| M4.4 | 답변·출처         | 근거 기반 답변·출처·근거 부족 처리                                          | M4.3                         | 미정 | 미정        | 출처 누락·환각 검증                                                        | 완료 | [M4.4 증빙](evidence/M4/M4.4/README.md) |
| M4.5 | 검색 평가         | 실제 64 Chunk·60 Case 평가                                                  | M4.4                         | 미정 | 미정        | Hybrid Hit@3 기준 충족                                                     | 완료 | [M4.5 증빙](evidence/M4/M4.5/README.md) |
| M5.1 | A2A 통합          | Orchestrator Agent Card·5개 Skill 호출                                      | M0.3, M1.5, M2.3, M3.5, M4.4 | 미정 | 미정        | A2A 계약 테스트                                                            | 완료 | [M5.1 최신 증빙](evidence/M5/M5.1/runs/20260814-135200/result.md) |
| M5.2 | 운영 공통 기능    | 인증·권한·오류·재시도·로그·Health                                           | M5.1                         | 미정 | 미정        | 401·부분 실패·재시도 테스트                                                | 완료 | [M5.2 승인 증빙](evidence/M5/M5.2/runs/20260814-150010/result.md) |
| M5.3 | Compose 통합      | 서비스 환경변수·Network·DB·시연 데이터                                      | M5.2                         | 미정 | 미정        | Docker Compose smoke test                                                  | 완료 | [M5.3 승인 증빙](evidence/M5/M5.3/runs/20260814-162010/result.md) |
| M5.4 | 시나리오 시연     | 8개 시나리오 종단 간 실행                                                   | M5.3                         | 미정 | 미정        | 시나리오별 결과 캡처                                                       | 완료 | [M5.4 승인 증빙](evidence/M5/M5.4/runs/20260814-170010/result.md) |
| M5.5 | 최종 인수         | 문서·결과·보류 항목·인수 보고                                               | M5.4                         | 미정 | 미정        | 팀 최종 승인                                                               | 대기 | 백로그 정의 필요         |

### 2.1.2 M1.1 Task DB 기반 실제 Workflow 착수 계획

`M0.4-03`은 실제 장기 Task가 없어 조건부 보류 상태였으므로 선행 업무 백로그인 `M1.1`의 구현 계획을 먼저 확정했다. 이후 M1.1~M1.3을 완료했지만 M1.3은 동기 업무 Task CRUD이므로 A2A `WORKING` Task를 제공하지 않는다는 점이 재검수에서 확인됐다. 운영 Route를 변경하지 않는 테스트 전용 UI 검수 환경을 자동 착수했고 사용자 육안 승인까지 완료하여 M0.4-03을 완료했다.

| 백로그 ID | 계획 작업 | 계획 구현 경로 | 계획 테스트·증빙 | 완료 조건 | 상태 |
| --- | --- | --- | --- | --- | --- |
| M1.1-01 | 업무 도메인 Migration 초안 | `workmate-agent/migrations/002_work_domain.sql` | `tests/test_work_domain_migration.py`, M1.1 실행 증빙 | Task·Gmail sync state·Calendar sync state가 `docs/03-data-priority-rules.md` 필드와 일치하고 M0.1 A2A 인프라 테이블과 책임이 겹치지 않음 | 완료 |
| M1.1-02 | Task Repository 경계 | `workmate-agent/app/domain/`, `app/repositories/` | `tests/test_task_repository.py`, `tests/test_postgres_integration.py` | 모든 조회에 요청 `user_id`를 적용하고 Soft Delete·원본 중복 방지·결정적 정렬을 Repository 경계에서 보장하며 PostgreSQL 실제 연결 검수가 PASS | 완료 |
| M1.1-03 | 외부 동기화 상태 Repository | `workmate-agent/app/repositories/sync_state.py` | `tests/test_sync_state_repository.py`, `tests/test_postgres_sync_state_integration.py` | Gmail `historyId`, Calendar `nextSyncToken`, Watch 식별자·만료 시각을 사용자 범위로 저장·조회 | 완료 |
| M1.1-04 | 샘플 데이터·Fixture | `workmate-agent/tests/fixtures/` | `tests/test_work_domain_fixtures.py` | 정상·Soft Delete·중복 원본·사용자 격리 Fixture가 실제 업무 결과를 흉내 내는 고정 Mock 응답으로 운영 경로에 유입되지 않음 | 완료 |
| M1.1-05 | Migration·Repository 통합 검수 | `workmate-agent/tests/test_m1_1_integration.py`, `tests/test_postgres_integration.py`, `tests/test_postgres_sync_state_integration.py` | `docs/evidence/M1/M1.1/runs/{run_id}/result.md` | PostgreSQL Migration 재실행 멱등성·Repository 권한 필터·Soft Delete·Sync 상태 격리 테스트가 모두 PASS | 완료 |

관련 결정은 [데이터와 우선순위 규칙](03-data-priority-rules.md), [기술 상세 설계 8.3](07-technical-specification.md#83-migration과-db-접근), [A2A Task 저장 경계](02-a2a-interface.md#611-task-store와-재시작-복구)를 따른다. 공개 Schema·DDL 필드 또는 unique constraint를 변경해야 하면 구현 전에 별도 승인과 문서·Contract Test 갱신이 필요하다.

### 2.1.3 M1.2 외부 소스 연동 백로그

| 백로그 ID | 계획 작업 | 구현 경로 | 테스트·증빙 | 완료 조건 | 상태 |
| --- | --- | --- | --- | --- | --- |
| M1.2-01 | OAuth 세션 주입 경계 | `workmate-agent/app/providers/google.py` | `tests/test_google_adapters.py` | `AuthorizedSession`을 주입받고 Secret·Token을 Adapter가 저장하지 않음 | 완료 |
| M1.2-02 | Gmail Adapter·정규화 | `workmate-agent/app/providers/google.py` | Adapter 계약·실제 OAuth 조회 | Profile·Messages·History 응답과 `message_id`를 정규화 | 완료 |
| M1.2-03 | Calendar Adapter·정규화 | `workmate-agent/app/providers/google.py` | Adapter 계약·실제 OAuth 조회 | Events·Watch 응답과 `{calendar_id}:{event_id}` 원본 키를 정규화 | 완료 |
| M1.2-04 | Cursor·Watch 동기화 | `workmate-agent/app/workflows/external_sync.py`, `app/repositories/sync_state.py` | Cursor 만료·부분 결과·실제 Watch 증빙 | Gmail `historyId`·Calendar `nextSyncToken` 저장, `410 Gone` 초기화 경고, Watch 결과 처리 | 완료 |

M1.2의 외부 OAuth·Provider 실행은 사용자 승인 후 수행한다. 실제 Provider 호출 결과가 PASS가 아니면 M1.2를 완료하지 않고 즉시 중단하며, 실행 `result.md`와 `HANDOFF.md`에 자동 진행 보류 사유와 재개 조건을 기록한다.

M0.1 구현은 다음 네 백로그를 순서대로 검수한다. M0.1-01은 실행 `20260812-210001`, M0.1-02는 구현 설명을 보강한 실행 `20260812-212244`, M0.1-03은 실행 `20260812-224743`, M0.1-04는 통합 Docker·Contract Test까지 포함한 실행 `20260812-230413`으로 자동 승인 완료됐다. M0.1의 네 하위 백로그가 모두 완료되어 다음 선행 조건 백로그로 이동한다.

| ID      | 작업명                         | 구현 경로                                                                                          | 테스트 경로                                                             | 완료 조건                                                                                                                                                                                                                                                   | 관련 의사결정                                                              | 다음 작업      | 상태 |
| ------- | ------------------------------ | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------- | ---- |
| M0.1-01 | 공식 A2A SDK 런타임 부트스트랩 | `workmate-agent/app/main.py`, `app/a2a/runtime.py`, `pyproject.toml`, `uv.lock`, Dockerfile·README | SDK 부팅·Agent Card·허용 Route Smoke Test                               | `a2a-sdk[http-server]==1.1.2`를 고정하고 `pyproject.toml`·`uv.lock`을 단일 의존성 원장으로 사용하며 공식 REST Handler·`AgentExecutor`와 테스트용 결정론적 Executor로 Agent Card와 허용 Route가 부팅됨. 이 백로그는 공개 전송 타입 전환 완료를 주장하지 않음 | `docs/02-a2a-interface.md` 5.1, `docs/07-technical-specification.md` 2.1·4 | M0.1-02        | 완료 |
| M0.1-02 | 공개 A2A 전송 타입 전환        | `workmate-agent/app/a2a/runtime.py`, Legacy `app.py`·`smoke_test.py`                               | Message·Task·Artifact Contract Test                                     | 공개 `/a2a` 경로에서 자체 Pydantic 전송 모델과 Legacy Route를 제거하고 공식 SDK 타입만 사용하며, Legacy Smoke Test를 승인 Schema 기반 Contract Test로 교체                                                                                                  | `docs/07-technical-specification.md` 7.1                                   | M0.1-03        | 완료 |
| M0.1-03 | Workflow·Task 실행 경계        | `workmate-agent/app/workflows/registry.py`, `app/a2a/runtime.py`, `app/a2a/persistence.py`, `migrations/`, `tests/test_persistence.py`, `tests/test_migration.py`, `tests/test_postgres_integration.py` | Registry·Artifact 변환·Task 복구·취소·Subscribe·Migration 테스트 | Executor는 Workflow 선택만 담당하고 M0.1 A2A 인프라 Migration으로 장기 Task·Message 멱등성·Artifact·Checkpoint를 영속 저장해 재시작 후 복구. Subscribe는 현재 Task 스냅샷 뒤에 연결 이후 신규 이벤트만 전송. 실제 PostgreSQL 연결과 최종 Docker 검증 PASS | `docs/02-a2a-interface.md` 6, `docs/07-technical-specification.md` 6·7·8.3 | M0.1-04 | 완료 |
| M0.1-04 | 통합 A2A 계약 검수             | `workmate-agent/tests/`                                                                            | Agent Card·5개 Skill·Artifact·인증·오류·Adapter·Streaming Contract Test | `Cache-Control`과 승인 Schema 검증, `/message:stream` 첫 Task 및 후속 상태·Artifact 순서, 활성 Task `POST` Subscribe, Terminal Task Subscribe 오류, 비허용 `GET` Subscribe와 기타 Route `404/405`, 조회·취소·부분 실패 통과                                 | `docs/02-a2a-interface.md` 4.5·5.1·6                                       | M0.1 통합 검수 | 완료 |

M0.2-01 실행 `20260813-093322`에서 메타데이터 보완 평가기로 실제 Provider Pilot 4/4, Full Case 1 20/20, Full Case 2 20/20을 Schema·의미 기준 모두 통과했다. 생성 설정과 Hash는 기록됐고 Provider 실패는 없었다. 비용표 미설정과 모델 선택은 사람 확인 항목이었으나, 사용자가 기본 모델 `openai/gpt-4.1-mini`과 비용 미산정 사유를 승인해 `latest_approved_run_id=20260813-093322`로 확정했으며 M0.2-01은 `완료`다.

M0.2-02 실행 `20260813-114046`에서 실제 64 Chunk·60 Case 평가 원본을 재검토했다. Hybrid Hit@3 98.21%, HNSW Recall@5 100%, Hybrid DB p95 66.3ms, Query Embedding p95 893.1ms로 기준을 통과했다. Cosine 0.45 답변 가능성 판정의 정상 질문 거절률 41.07%는 운영 최종 판정에서 제외하는 정책으로 사용자 승인했으며, M0.2-02를 `완료`로 전환했다. 상세 결과는 [`M0.2-02 검수 결과`](evidence/M0/M0.2/runs/20260813-114046/result.md)에 기록한다.

M0.2-03 실행 `20260813-121052`에서 `gpt-4o-transcribe` 합성 파일 20 Case 중 19건(95%), Realtime 2 Case 중 2건, Chunk 재연결·최종 STT E2E 2건 중 2건을 통과했다. Provider 오류는 0건이다. 실제 회의 음성 WER/CER·화자 분리·잡음·겹침 발화는 M3.3 완료 조건으로 이관하는 것으로 사용자 승인해 M0.2-03을 `완료`로 전환했다. 상세 결과는 [`M0.2-03 검수 결과`](evidence/M0/M0.2/runs/20260813-121052/result.md)에 기록한다.

M0.2-04 실행 `20260813-122007`에서 readonly Scope·설정·단위 테스트 2건·구문 검사는 통과했다. 기존 `google-oauth-test/HISTORY.md`에는 Gmail Profile·Message·History 조회와 Gmail Watch `historyId`·`expiration` 등록 성공이 기록돼 있다. 현재 환경에서 Google API 재실행은 소켓 권한 및 연결 timeout으로 보류됐으나, 사용자가 기존 성공 이력을 승인해 M0.2-04를 `완료`로 전환했다. 상세 결과는 [`M0.2-04 검수 결과`](evidence/M0/M0.2/runs/20260813-122007/result.md)에 기록한다.

M0.2-05 실행 `20260813-122321`에서 Calendar readonly Scope·설정·단위 테스트 2건·구문 검사는 통과했다. 기존 `google-oauth-test/HISTORY.md`에는 Calendar Events 조회와 Calendar Watch `resourceId`·`expiration` 등록 성공이 기록돼 있다. 현재 환경에서 Google API 재실행은 네트워크 차단으로 보류됐으나, 사용자가 기존 성공 이력을 승인해 M0.2-05를 `완료`로 전환했다. 상세 결과는 [`M0.2-05 검수 결과`](evidence/M0/M0.2/runs/20260813-122321/result.md)에 기록한다.

후속 재검수 `20260813-130230`에서 사용자 로컬 비교 결과를 바탕으로 `httplib2` IPv6 fallback 실패를 확정하고 테스트 하네스를 `AuthorizedSession` REST 전송으로 교체했다. 회귀 테스트 3건·dry-run·구문 검사는 PASS였으나 Codex 관리형 실행 환경의 실제 OAuth 호출이 timeout이고 Watch가 미실행이므로 자동 승인하지 않는다. M0.2-05를 `재작업`으로 되돌리고 사용자 로컬 실제 API·Watch PASS 전까지 다음 작업을 중단한다. 상세 결과는 [`M0.2-05 재검수 결과`](evidence/M0/M0.2/runs/20260813-130230/result.md)에 기록한다.

사용자 로컬 실행 `20260813-131903`에서 `smoke_test.py`와 `smoke_test.py --watch`의 Gmail profile/messages/history, Calendar events, Gmail·Calendar Watch 검사가 모두 정확히 `pass`였고 미실행·경고·보류·차단 항목이 없었다. 따라서 자동 승인 규칙을 적용해 M0.2-05를 `완료`로 전환한다. 이전 실패 실행 `20260813-130230`은 보존하며, 상세 결과는 [`M0.2-05 최신 승인 결과`](evidence/M0/M0.2/runs/20260813-131903/result.md)에 기록한다. M0.2 상위 항목은 통합 검수 전까지 `진행`으로 유지한다.

M0.2 통합 검수 `20260813-133446`에서 M0.2-02의 `PASS_WITH_CAVEAT`·권장 기준 FAIL, M0.2-03의 실제 회의 음성 평가 보류, M0.2-04의 실제 API 재현 보류가 확인됐다. 통합 자동 승인 규칙에 따라 검수를 즉시 중단하고 M0.2를 `재작업`으로 전환한다. 개별 승인 증빙은 보존하며, 상세 결과는 [`M0.2 통합 검수 결과`](evidence/M0/M0.2/runs/20260813-133446/result.md)에 기록한다.

차단 해소 방안은 [`M0.2 통합 검수 차단 해소 계획`](evidence/M0/M0.2/remediation-plan.md)으로 확정했다. M0.2-02는 단일 Cosine 임계값을 진단 지표로만 두고 답변 가능성 판정을 M4.4로 이관하며, M0.2-03은 실제 회의 음성 품질을 M3.3으로 이관하고 합성·Realtime·E2E 범위만 재검수한다. M0.2-04는 사용자 로컬 `20260813-131903` Gmail PASS 결과를 전용 증빙으로 분리한다. 세 새 결과가 정확히 `PASS`가 되기 전에는 통합 재검수를 승인하지 않는다.

M0.2-02 재검수 `20260813-134129`에서 모델 차원·Hybrid 품질·HNSW·지연·단위 테스트·구문 검사·문서 diff가 모두 정확히 `PASS`가 됐다. 단일 Cosine 답변 가능성 판정은 M4.4 후속 범위로 분리했으며, 이전 평가 원본은 보존한다. M0.2-02는 완료로 유지하고 다음 재검수는 M0.2-03이다. M0.2 상위 상태는 M0.2-03·04 재검수와 통합 검수 전까지 `재작업`으로 유지한다. 상세 결과는 [`M0.2-02 재검수 결과`](evidence/M0/M0.2/runs/20260813-134129/result.md)에 기록한다.

M0.2-03 재검수 `20260813-134542`에서 합성 파일·Realtime Streaming·Chunk 재연결·최종 STT E2E와 단위 테스트·dry-run·구문 검사·문서 diff가 모두 정확히 `PASS`가 됐다. 실제 회의 음성 품질은 M3.3 후속 범위로 명시적으로 분리했으며, 이전 평가 원본은 보존한다. M0.2-03은 완료로 유지하고 다음 재검수는 M0.2-04이다. M0.2 상위 상태는 M0.2-04 재검수와 통합 검수 전까지 `재작업`으로 유지한다. 상세 결과는 [`M0.2-03 재검수 결과`](evidence/M0/M0.2/runs/20260813-134542/result.md)에 기록한다.

M0.2-04 재검수 `20260813-134915`에서 Gmail readonly Scope·AuthorizedSession·Profile/Message/History·Watch와 단위 테스트·구문 검사·문서 diff가 모두 정확히 `PASS`가 됐다. 사용자가 제공한 로컬 실제 OAuth 결과를 Gmail 전용 증빙으로 분리했고, 이전 결과는 보존한다. M0.2-04는 완료로 유지하며 M0.2-01~05의 재검수 결과가 모두 정확히 `PASS`가 되었으므로 M0.2 통합 재검수를 실행할 수 있다. 상세 결과는 [`M0.2-04 재검수 결과`](evidence/M0/M0.2/runs/20260813-134915/result.md)에 기록한다.

M0.2 통합 재검수 `20260813-135158`에서 M0.2-01~05 최신 승인 실행이 모두 정확히 `PASS`임을 확인했다. 이전 통합 차단은 새 개별 재검수로 해소됐고, M0.2를 `완료`로 전환한다. 상세 결과는 [`M0.2 통합 재검수 결과`](evidence/M0/M0.2/runs/20260813-135158/result.md)에 기록한다. 다음 착수 항목은 M0.3 내부 챗봇 API다.

답변 가능성은 `Dense + Trigram RRF Top-K → metadata·직접 근거 검증 → 조건부 Reranker/groundedness → 답변 또는 insufficient_evidence`로 분리한다. 단일 Cosine 임계값은 운영 거절 조건으로 사용하지 않으며, 실제 검색 Workflow·출처 검증·RRF fallback은 M4.4에서 구현한다.

M0.2는 기존 평가를 무조건 다시 실행하지 않는다. **설계 확정**은 모델·Scope가 선택된 상태이고, **검수 완료**는 평가 원본·버전·제약·미검증 위험을 M0.2 증빙에서 승인한 상태다. 합성 STT 평가는 M0.2에서 승인하되 실제 회의 음성 평가는 M3.3 검수 조건으로 넘긴다.

M0.1의 PostgreSQL 범위는 A2A Task·Message 멱등성·Artifact·`task_id ↔ thread_id`·Checkpoint 복구에 필요한 인프라 Migration으로 제한한다. 공개 이벤트 전체 이력과 재생 Cursor는 MVP에서 저장하지 않고 Subscribe 연결 시 현재 Task 스냅샷 뒤에 신규 이벤트만 전송한다. M1.1은 Task·Gmail·Calendar 업무 데이터와 Repository·샘플 데이터를 추가하며 M0.1 Migration을 다시 만들거나 덮어쓰지 않는다.

| ID      | 작업명              | 평가·검증 원본                                                        | 완료 조건                                                           | 관련 의사결정                            | 다음 작업      | 상태 |
| ------- | ------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------- | -------------- | ---- |
| M0.2-01 | LLM 평가 승인       | `llm-evaluation/`, `docs/11-llm-evaluation-plan.md`                   | 기본 모델·Schema 평가 이력 승인, 할당량 소진 시 재평가 Trigger 기록 | `docs/07-technical-specification.md` 9.1 | M0.2-02        | 완료 |
| M0.2-02 | Embedding 평가 승인 | `embedding-evaluation/`, `docs/10-embedding-evaluation-plan.md`       | 모델·1536차원·Hybrid 지표·HNSW 결과 승인                            | `docs/06-delivery-plan.md` 5.1           | M0.2-03        | 완료 |
| M0.2-03 | STT 평가 승인       | `stt-evaluation/`, `docs/12-implementation-verification-guide.md` 2.2 | 합성 평가 결과 승인, 실제 회의 음성 미평가를 M3.3 위험으로 연결     | `docs/07-technical-specification.md` 9.3 | M0.2-04        | 완료 |
| M0.2-04 | Gmail OAuth 승인    | `google-oauth-test/`                                                  | readonly Scope·Profile/Message/History·Watch 이력 승인              | `docs/07-technical-specification.md` 10  | M0.2-05        | 완료 |
| M0.2-05 | Calendar OAuth 승인 | `google-oauth-test/`                                                  | readonly Scope·Events/Watch 이력 승인, 테스트 사용자 차단 여부 기록 | `docs/07-technical-specification.md` 10  | M0.2 통합 검수 | 완료 |

M0.3과 M0.4는 다음 최소 백로그만 미리 고정한다. 상세 구현 경로와 실행 명령은 해당 백로그 착수 시 실제 저장소 구조를 확인해 채운다.

| ID      | 작업명                | 완료 조건                                               | 다음 작업      | 상태 |
| ------- | --------------------- | ------------------------------------------------------- | -------------- | ---- |
| M0.3-01 | Skill·입력 API        | 5개 Skill 목록과 자연어/JSON 입력 검증                  | M0.3-02        | 완료 |
| M0.3-02 | 공통 Workflow 호출    | A2A와 같은 Workflow·Repository·Domain 경계 사용         | M0.3-03        | 완료 |
| M0.3-03 | 장기 Task API         | Task 조회·Polling·취소와 Terminal 상태 검증             | M0.3-04        | 완료 |
| M0.3-04 | 인증·Schema·부분 실패 | Session/OIDC, `user_id`, 승인 Artifact, `warnings` 검증 | M0.3 통합 검수 | 완료 |
| M0.4-01 | Skill·입력 UI         | 5개 Skill 선택과 자연어/JSON 입력                       | M0.4-02        | 완료 |
| M0.4-02 | 결과·상태 UI          | Artifact, 최신성, 경고, 오류, 장기 Task 상태 표시       | M0.4-03        | 완료 |
| M0.4-03 | UI 통합 검수          | 5개 Skill 화면, Polling·취소·권한 차단 검수             | 사용자 UI 육안 승인 | 완료 |
| M4.1-01 | 검색 Chunk Migration  | pgvector·`meetings`·`meeting_chunks` DDL 검증            | M4.1-02        | 완료 |
| M4.1-02 | Chunk Repository      | 저장·조회·수정·사용자 범위 테스트                        | M4.1-03        | 완료 |
| M4.1-03 | Embedding Adapter     | 1536차원·Provider 오류·재임베딩 테스트                  | M4.1-04        | 완료 |
| M4.1-04 | 검색 데이터 통합 검수 | Migration·Repository·Embedding·Index 통합 검수          | M4.2           | 완료 |

M0.4-01 실행 `20260813-160540`은 자동 검증과 사용자 UI 육안 검수를 모두 PASS하여 완료 처리했다. Token 입력 후 Skill 목록 재조회, `daily_briefing` 실행, `mock: true`·`business_result: false` 표시를 확인했다. Mock 응답은 실제 업무 완료 증빙으로 인정하지 않는다. 상세 결과는 [`M0.4-01 UI 육안 검수 결과`](evidence/M0/M0.4/runs/20260813-160540/result.md)에 기록한다.

M0.4-02 실행 `20260813-160824`의 Artifact·Task 상태·Mock 여부·warnings·오류 요약 UI 자동 검증 24건과 구문·diff 검사가 모두 PASS했고, 사용자 육안 검수 실행 `20260813-161223`도 PASS했다. 따라서 M0.4-02를 완료 처리한다. 상세 결과는 [`M0.4-02 UI 검수 결과`](evidence/M0/M0.4/runs/20260813-161223/result.md)에 기록한다. Mock 응답은 실제 업무 결과 증빙으로 인정하지 않는다.

M0.4-03 실행 `20260813-162027`은 페이지 진입과 잘못된 Token의 401 차단은 PASS했으나, Polling·취소 컨트롤이 없어 FAIL했고 유효 Token 미제공으로 5개 Skill 실행·사용자 범위 검수를 완료하지 못했다. PASS가 아닌 결과가 있으므로 자동 승인과 다음 백로그 착수를 중단하고 `재작업`으로 기록한다. 상세 결과는 [`M0.4-03 통합 UI 검수 결과`](evidence/M0/M0.4/runs/20260813-162027/result.md)에 기록한다.

M4.1-03 실행 `20260814-131500`은 Adapter 단위·회귀 테스트 8개, `compileall`, `git diff --check`, 실제 `openai/text-embedding-3-small` Provider smoke를 모두 PASS했다. 1536차원 응답·Provider 오류 보존·사용자 범위 검증을 확인하여 자동 승인하고 완료 처리한다. 상세 결과는 [`M4.1-03 Embedding Adapter 검수 결과`](evidence/M4/M4.1/runs/20260814-131500/result.md)에 기록한다.

M4.1-04 초기 실행 `20260814-140500`은 사용자 범위 필터와 HNSW 정렬을 하나의 계획에서 검증하려다 B-tree 계획을 선택해 재작업으로 기록했다. 수정 후 실행 `20260814-143000`에서 PostgreSQL·pgvector 통합, 재임베딩, 사용자 격리, HNSW Index Scan, 회귀·정적 검사가 모두 PASS하여 자동 승인하고 M4.1을 완료 처리한다. 상세 결과는 [`M4.1-04 통합 검수 결과`](evidence/M4/M4.1/runs/20260814-143000/result.md)에 기록한다.

M4.2 초기 실행 `20260814-150000`은 복합 외래 키 Fixture와 사용자별 검색 기대값이 잘못되어 재작업으로 기록했다. 수정 후 실행 `20260814-151500`에서 pg_trgm 검색, similarity 정렬, user_id 격리, 회의 ID·날짜 필터, 회귀·정적 검사가 모두 PASS하여 자동 승인하고 완료 처리한다. 상세 결과는 [`M4.2 Trigram 검수 결과`](evidence/M4/M4.2/runs/20260814-151500/result.md)에 기록한다.

M4.3 초기 실행 `20260814-160000`은 Dense Fixture가 같은 방향 벡터를 사용해 cosine 순위 기대가 불안정했다. 수정 후 실행 `20260814-161500`에서 Dense·Trigram RRF, 사용자·metadata 필터, HNSW 계획, 회귀·정적 검사가 모두 PASS하여 자동 승인하고 완료 처리한다. 상세 결과는 [`M4.3 Hybrid 검수 결과`](evidence/M4/M4.3/runs/20260814-161500/result.md)에 기록한다.

M4.4 실행 `20260814-171500`에서 Hybrid 검색 결과 기반 답변, 회의명·Chunk 출처, 원문 `evidence_text` 일치, 근거 부족 거절, PostgreSQL·회귀·정적 검사가 모두 PASS하여 자동 승인하고 완료 처리한다. 상세 결과는 [`M4.4 답변·출처 검수 결과`](evidence/M4/M4.4/runs/20260814-171500/result.md)에 기록한다.

M4.5 실행 `20260814-181500`에서 실제 64 Chunk·60 Case 원본 무결성, Hybrid Hit@3 98.21%, HNSW Recall@5 100%, Hybrid DB p95 64.743ms, Query Embedding p95 893.1ms를 재검증했다. 모든 기준이 PASS하여 자동 승인하고 M4 전체를 완료 처리한다. 상세 결과는 [`M4.5 검색 평가 결과`](evidence/M4/M4.5/runs/20260814-181500/result.md)에 기록한다.

M0.4-03 재검수 실행 `20260813-162530`에서 Polling·취소 컨트롤, 1초 상태 갱신, Terminal 자동 중지, 잘못된 Token 401 차단과 24개 자동 테스트가 PASS했다. 유효 Token 기반 5개 Skill 실행·Polling·취소·사용자 범위 검수는 미실행이므로 자동 승인하지 않고 `검수 중`으로 유지한다. 상세 결과는 [`M0.4-03 재검수 결과`](evidence/M0/M0.4/runs/20260813-162530/result.md)에 기록한다.

M0.4-03 재검수 실행 `20260813-163114`에서 Task Artifact metadata에 `mock`·`business_result`를 저장하고 POST→GET 재조회 결과가 일치하는지 확인했다. 24개 테스트·구문·diff 검사는 모두 PASS했지만 유효 Token 기반 5개 Skill 통합 육안 검수와 실제 장기 Task 취소는 미실행이므로 `검수 중`을 유지한다. 상세 결과는 [`M0.4-03 metadata 재검수 결과`](evidence/M0/M0.4/runs/20260813-163114/result.md)에 기록한다.

M0.4-03 재검수 실행 `20260813-163631`에서 5개 Skill의 `TASK_STATE_COMPLETED`, `mock: true`, `business_result: false`, `경고 없음` 표시가 모두 PASS했다. Runtime Mock이 즉시 완료되어 실제 장기 Task 취소와 사용자 범위 격리는 미실행이므로 자동 승인하지 않고 `검수 중`으로 유지한다. 상세 결과는 [`M0.4-03 5개 Skill 검수 결과`](evidence/M0/M0.4/runs/20260813-163631/result.md)에 기록한다.

M0.4-03 재검수 실행 `20260813-163927`에서 테스트 전용 `WORKING` Task Fixture의 취소 상태 전환과 사용자 범위 격리 테스트가 PASS했다. 운영 Runtime에는 지연 Mock을 추가하지 않았으며, 실제 장기 Workflow 연결 후 취소 버튼 활성화 육안 확인이 남아 `보류(선행 M1.3 대기)`로 기록한다. 상세 결과는 [`M0.4-03 취소·권한 검수 결과`](evidence/M0/M0.4/runs/20260813-163927/result.md)에 기록한다.

M1.1-01 실행 `20260813-170714`는 사용자가 공개 DDL·제약을 확인하고 승인했다. 계약·회귀 테스트 5개, `compileall`, `git diff --check`가 PASS였고, 승인된 실행을 기준으로 M1.1-01을 `완료` 처리한다. PostgreSQL 실제 적용·재실행은 M1.1-05에서 수행한다. 상세 결과는 [`M1.1-01 사용자 재검수 결과`](evidence/M1/M1.1/runs/20260813-170714/result.md)에 기록한다.

M1.1-02 실행 `20260813-192221`에서 Task 도메인·SQLite 계약 Adapter·PostgreSQL Adapter를 확인했다. 격리 PostgreSQL 16 컨테이너 readiness, PostgreSQL 통합 테스트, Repository 생성·조회·멱등·Soft Delete 스모크, 전체 39개 테스트가 모두 PASS하고 SKIP이 없어 자동 승인 처리한다. 상세 결과는 [`M1.1-02 검수 결과`](evidence/M1/M1.1/runs/20260813-192221/result.md)에 기록한다. M1.1-03과 M1.1-05는 별도 선행 작업으로 유지한다.

M1.1-03 실행 `20260813-193324`에서 SQLite 계약 테스트는 PASS했지만 PostgreSQL 동기화 상태 통합 테스트가 `users.user_id` 외래키 위반으로 FAIL했다. 자동 승인 규칙에 따라 즉시 중단하고 `재작업`으로 기록한다. 자동 진행 보류 사유는 Repository가 동기화 상태 저장 전에 사용자 원장 행을 보장하지 않은 것이며, 수정 후 격리 PostgreSQL 전용 테스트와 전체 테스트가 모두 정확히 PASS해야 재개한다. 상세 결과는 [`M1.1-03 실패 검수 결과`](evidence/M1/M1.1/runs/20260813-193324/result.md)에 기록한다.

M1.1-03 재검수 `20260813-193615`에서 `PostgresSyncStateRepository`가 사용자 원장 행을 멱등적으로 보장하도록 수정한 뒤 동기화 상태 PostgreSQL 통합 1개, 기존 PostgreSQL 통합 1개, 전체 44개 테스트, `compileall`, `git diff --check`가 모두 PASS했다. SKIP·수동 검수·차단 항목이 없어 자동 승인하고 완료 처리한다. 최초 실패 실행은 보존하며, 상세 결과는 [`M1.1-03 최신 승인 결과`](evidence/M1/M1.1/runs/20260813-193615/result.md)에 기록한다. 다음은 M1.1-05 통합 검수다.

M1.1-05 실행 `20260813-193901`에서 Migration 재실행 멱등성, Task 사용자 격리·원본 중복·Soft Delete, Sync 상태 사용자 격리를 포함한 PostgreSQL 통합 12개와 전체 45개 테스트, `compileall`, `git diff --check`가 모두 PASS했다. SKIP·수동 검수·차단 항목이 없어 자동 승인하고 완료 처리한다. M1.1-04 샘플 데이터·Fixture는 별도 백로그로 유지한다. 상세 결과는 [`M1.1-05 통합 검수 결과`](evidence/M1/M1.1/runs/20260813-193901/result.md)에 기록한다.

M1.1-04 실행 `20260813-194043`에서 정상·Soft Delete·외부 원본 중복·사용자 격리·Gmail/Calendar Cursor Fixture 5개와 `compileall`, `git diff --check`가 모두 PASS했다. Fixture는 테스트 경로에만 존재하고 운영 Workflow·운영 DB에 연결하지 않았으므로 자동 승인·완료 처리한다. 상세 결과는 [`M1.1-04 Fixture 검수 결과`](evidence/M1/M1.1/runs/20260813-194043/result.md)에 기록한다. 다음은 M1.2 외부 소스 연동이다.

M1.1의 M1.1-01~05가 모두 승인되어 M1.1을 완료 처리한다. 다음 M1.2는 Gmail·Google Calendar 실제 API와 OAuth·Watch를 포함하므로 자동 착수 예외이며, 외부 Provider 사용 승인 후 시작한다. 자동 진행 보류 사유와 재개 조건은 `HANDOFF.md`에 기록한다.

M1.2 실행 `20260813-194801`에서 Gmail·Calendar REST Adapter와 Cursor 동기화 Workflow를 구현했다. Adapter 계약 테스트 5개, 실제 Gmail Profile·Messages·History, Calendar Events, Gmail·Calendar Watch, 새 Adapter의 실제 OAuth 세션 정규화가 모두 PASS했다. 외부 Provider 사용에 대한 사용자 승인이 완료된 상태에서 미실행·차단 항목이 없어 자동 승인·완료 처리하고 M1.3으로 이동한다. 상세 결과는 [`M1.2 검수 결과`](evidence/M1/M1.2/runs/20260813-194801/result.md)에 기록한다.

`M0.4-03` 재검수 `20260813-212246`에서 내부 API·UI 자동 테스트 11건, `WORKING` Fixture 취소, 사용자 범위, 구문·diff 검사는 PASS했다. 그러나 M1.3 Task CRUD는 동기 API라 실제 `WORKING` A2A Task를 제공하지 않으며, 5개 Skill도 아직 즉시 완료 runtime bootstrap이다. 따라서 실제 취소 버튼 활성화 육안 검수는 `BLOCKED`이고 자동 승인·다음 백로그 진행을 중단한다. 운영 Route에 지연 Mock을 추가하지 않는 테스트 전용 실행 환경을 마련한 뒤 재검수한다. 상세 결과는 [`M0.4-03 최신 재검수 결과`](evidence/M0/M0.4/runs/20260813-212246/result.md)에 기록한다.

M0.4-03 재작업은 `20260813-213733`에 자동 착수했다. 테스트 전용 로컬 OIDC·JWKS와 `WORKING` Task Fixture를 추가하고, 실제 HTTP·브라우저에서 `TASK_STATE_WORKING` → `TASK_STATE_CANCELED` 전환을 확인했다. 자동 검증은 모두 PASS했지만 UI 육안 검수는 사용자 판단 항목이므로 M0.4-03을 `검수 중`으로 유지한다. 상세 결과는 [`M0.4-03 재작업 검수 결과`](evidence/M0/M0.4/runs/20260813-213733/result.md)에 기록한다.

사용자가 `20260813-213733` 브라우저 화면의 `WORKING` 상태·활성 취소 버튼·`TASK_STATE_CANCELED` 전환을 `y`로 승인했다. 자동·HTTP·브라우저 검증과 사용자 육안 검수가 모두 PASS하여 M0.4-03과 M0.4를 `완료`로 전환한다. 상세 결과는 [`M0.4-03 승인 결과`](evidence/M0/M0.4/runs/20260813-213733/result.md)에 기록한다. 다음은 M0 통합 검수다.

M0.3-04 실행 `20260813-153001`은 개발 인증 우회 없이 운영 OIDC JWT 코드 경로를 로컬 JWKS Fixture로 검증했다. 유효·만료·서명·audience 오류, 사용자 범위 격리, 승인 Schema, 부분 실패 Warning 보존을 포함한 22건 테스트와 구문·diff 검사가 모두 정확히 PASS하여 자동 승인하고 `완료`로 전환했다. 상세 결과는 [`M0.3-04 검수 결과`](evidence/M0/M0.3/runs/20260813-153001/result.md)에 기록한다.

M0 통합 검수 실행 `20260813-214548`에서 M0.1~M0.4 최신 승인 증빙 4건과 현재 코드 통합 회귀 테스트 26건, `compileall`, `git diff --check`가 모두 PASS했다. 미실행·수동 검수·미해소 차단이 없어 자동 승인 규칙을 적용하고 M0을 `완료`로 전환한다. 통합 결과는 [`M0 통합 검수`](evidence/M0/runs/20260813-214548/result.md), 상위 증빙은 [`M0 README`](evidence/M0/README.md)에 기록한다. 다음 착수 항목은 M1.4 Task 제안이다.

담당자·완료 예정일·다음 착수 항목은 계획 수립용 필드이며, 작업 시작 시 실제 백로그 ID로 갱신한다. 아직 세부 작업을 정하지 않은 항목은 `백로그 정의 필요`로 표시한다. 실제 완료 여부는 반드시 테스트 결과나 화면·API 증빙으로 갱신한다. M1~M5의 상세 백로그는 해당 하위 마일스톤 착수 직전에만 분해하며, 구현하지 않을 미래 작업을 미리 상세 설계하지 않는다.

### 2.1.1 하위 마일스톤 백로그 분해 규칙

하위 마일스톤의 구현 작업은 백로그 항목으로 더 세분화할 수 있다. 백로그는 개발 작업의 추적 단위이며, 공식 완료·승인 단위는 기존 하위 마일스톤(`M2.1` 등)으로 유지한다. 백로그 항목을 별도 마일스톤이나 별도 인수 단위로 만들지 않는다.

백로그 ID는 `{하위 마일스톤 ID}-{순번}` 형식을 사용한다.

```text
M2.1 주간 데이터 분류
├─ M2.1-01 Task 상태 분류 로직
├─ M2.1-02 회의 Action Item 연결
├─ M2.1-03 메일 요청사항 연결
├─ M2.1-04 완료·진행·지연 집계 테스트
└─ M2.1-05 source_id 검증
```

각 백로그 항목에는 다음 정보를 기록한다.

| 항목          | 기록 내용                                          |
| ------------- | -------------------------------------------------- |
| ID            | `M2.1-01` 형식의 고유 ID                           |
| 작업명        | 구현하거나 검증할 세부 작업                        |
| 선행 작업     | 먼저 완료되어야 하는 백로그 ID 또는 하위 마일스톤  |
| 담당자·예정일 | 작업 담당자와 완료 예정일                          |
| 구현 경로     | 코드·Schema·Migration·UI 파일 경로                 |
| 테스트 경로   | 단위·통합·UI 테스트 파일 경로                      |
| 완료 조건     | 해당 작업을 완료로 판단할 구체적인 조건            |
| 관련 의사결정 | 적용한 설계 문서와 절 번호 또는 결정 링크          |
| 다음 작업     | 다음에 착수할 백로그 ID                            |
| 상태          | `대기 / 진행 / 완료 / 보류`                        |
| 증빙 경로     | 해당 하위 마일스톤의 `docs/evidence/Mx/Mx.y/` 경로 |

예시:

| ID      | 작업명                | 구현 경로            | 테스트 경로                           | 완료 조건                              | 관련 의사결정                        | 다음 작업 | 상태 |
| ------- | --------------------- | -------------------- | ------------------------------------- | -------------------------------------- | ------------------------------------ | --------- | ---- |
| M2.1-01 | Task 상태 분류        | `workmate-agent/...` | `tests/test_weekly_classification.py` | 완료·진행·지연 분류 통과               | `docs/03-data-priority-rules.md`     | M2.1-02   | 대기 |
| M2.1-02 | 회의 Action Item 연결 | `workmate-agent/...` | `tests/test_action_item_link.py`      | 회의 근거와 Task 연결                  | `docs/07-technical-specification.md` | M2.1-03   | 대기 |
| M2.1-03 | source_id 검증        | `workmate-agent/...` | `tests/test_source_id.py`             | 모든 보고 항목에 유효한 source ID 존재 | `docs/02-a2a-interface.md`           | M2.1-04   | 대기 |

백로그 항목이 모두 완료되면 하위 마일스톤 통합 테스트를 실행하고, 결과를 기존 증빙 경로에 기록한다.

```text
백로그 완료
→ 하위 마일스톤 통합 테스트
→ docs/evidence/M2/M2.1/result.md 갱신
→ 검수 승인
→ M2.1 완료
```

백로그 작업 중 일부가 실패하거나 보류되면 하위 마일스톤은 완료로 표시하지 않는다. 실패한 백로그 ID, 원인, 재검수 실행 ID는 해당 하위 마일스톤의 `README.md` 또는 `result.md`에 남긴다.

### 2.2 전체 마일스톤 증빙 저장 규칙

M2뿐 아니라 모든 마일스톤의 최종 검수 자료는 다음 공통 경로에 저장한다. 하위 마일스톤 단위로 폴더를 나누며, 각 폴더의 `README.md`에는 현재 상태와 최신 실행·승인 ID를 요약하고, `result.md`에는 완료 기준과 검수 결과를 기록한다. 구현 결과가 생기기 전에는 빈 `result.md`를 만들지 않는다.

```text
docs/evidence/
├─ M0/M0.1/ ... M0.4/   # 계약·모델·OAuth·내부 챗봇
├─ M1/M1.1/ ... M1.5/   # DB·외부 연동·Task·우선순위
├─ M2/M2.1/ ... M2.4/   # 주간 데이터·계획·보고서·UI
├─ M3/M3.1/ ... M3.6/   # 회의 입력·STT·분석·승인·R2
├─ M4/M4.1/ ... M4.5/   # Chunk·검색·RRF·HNSW·평가
└─ M5/M5.1/ ... M5.5/   # A2A·운영·Compose·시연·인수
```

| 마일스톤 | 구현 원본                                         | 평가·테스트 원본                                                                                                   | `docs/evidence/`에 저장할 최종 자료                             |
| -------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------- |
| M0       | `docs/`, `workmate-agent/`(내부 검증 페이지 포함) | `workmate-agent/` 계약 테스트, `google-oauth-test/`, `llm-evaluation/`, `embedding-evaluation/`, `stt-evaluation/` | 계약 검증 결과, 모델·OAuth 평가 요약, 내부 챗봇 화면/API 결과   |
| M1       | `workmate-agent/`                                 | 백엔드 단위·통합 테스트                                                                                            | Migration 결과, CRUD·동기화·Top 3 테스트 결과                   |
| M2       | `workmate-agent/`                                 | `llm-evaluation/`와 주간 보고 테스트                                                                               | 분류 JSON, 계획 검증, 보고서 JSON/Markdown, 내부 검증 화면 캡처 |
| M3       | `workmate-agent/`                                 | `stt-evaluation/`, `meeting-recording-test/`, `r2-storage-test/`                                                   | STT·Transcript·Action Item·R2 검증 요약                         |
| M4       | `workmate-agent/`                                 | `embedding-evaluation/`                                                                                            | 검색 지표, 출처 검증, HNSW·지연 결과                            |
| M5       | Orchestrator 팀 공통 UI·`workmate-agent/`         | `workmate-agent/` A2A 계약 테스트와 Docker Compose 테스트                                                          | 제품 UI 종단 간 API 응답, 시나리오 캡처, 인수 결과              |

평가 폴더의 원본 JSONL·CSV·오디오·Secret은 원래 위치에 보존하고, `docs/evidence/`에는 요약·링크·검수용 작은 JSON/Markdown·화면 캡처만 복사한다. 실제 Token, API Key, Presigned URL, 원본 회의 음성은 `docs/evidence/`와 Git에 저장하지 않는다.

### 2.3 증빙 생성·갱신 시점

증빙은 하위 마일스톤의 상태에 따라 다음 시점에 생성·갱신한다.

| 시점           | 수행 내용                                                                 | 상태                 |
| -------------- | ------------------------------------------------------------------------- | -------------------- |
| 작업 시작      | `docs/evidence/Mx/Mx.y/README.md` 생성, 목표·담당자·시작일·선행 조건 기록 | `대기`               |
| 구현 진행      | 코드 경로·실행 명령·테스트 Case·원본 평가 링크를 추가                     | `진행`               |
| 구현 완료      | API 응답·JSON/Markdown 결과·화면 캡처·테스트 로그·보완 내역 저장          | `검수 중`            |
| 검수 통과      | 완료 기준 확인, 명시·묵시 승인과 완료일·최종 판단 기록                    | `완료`               |
| 실패 또는 보류 | 실패 원인·재현 명령·후속 조치·재검수 조건 기록                            | `보류` 또는 `재작업` |

기존 평가가 완료된 M0 항목은 각 평가 폴더의 결과를 바탕으로 증빙을 사후 작성할 수 있다. 반면 아직 구현하지 않은 M1~M5 항목은 작업 시작 전에 폴더와 `README.md`만 만들고, 결과가 생긴 뒤 내용을 채운다. M5.5 최종 인수 시 각 하위 폴더의 상태와 링크를 다시 확인해 마일스톤 전체 증빙을 잠근다.

### 2.4 반복 검수와 최신 승인 실행 표시

같은 하위 마일스톤을 여러 번 검수해도 이전 결과를 덮어쓰거나 삭제하지 않는다. 실행별 결과는 `runs/{run_id}/` 아래에 저장하고, 하위 마일스톤의 `README.md`에는 항상 최신 실행과 최신 승인 실행을 구분해 표시한다.

```text
docs/evidence/M2/M2.3/
├─ README.md
└─ runs/
   ├─ 20260811-101500/
   │  └─ result.md
   └─ 20260812-143000/
      ├─ result.md
      └─ result.json  # 구조화 결과가 필요한 실행만 생성
```

실행별 검수 의견은 `runs/{run_id}/result.md`에 함께 기록한다. 별도 `review.md`는 검수 내용이 `result.md`에 들어가는 경우 만들지 않는다.

각 하위 마일스톤 `README.md`의 상단에는 다음 필드를 유지한다.

```text
status: 검수 중 | 완료 | 재작업 | 보류
latest_run_id: 가장 최근 실행 ID
latest_run_status: 가장 최근 실행 결과
latest_approved_run_id: 가장 최근 승인된 실행 ID 또는 null
approved_at: 최신 승인 시각 또는 null
reviewer: 승인자 또는 null
```

- 새 실행이 실패하면 `latest_run_id`만 갱신하고 `latest_approved_run_id`는 이전 승인 결과를 유지한다. 상태는 `재작업`으로 표시한다.
- 새 실행이 통과하고 검수자가 명시 승인하거나 아래 묵시 승인 조건을 충족하면 승인 ID를 해당 실행으로 갱신하고 상태를 `완료`로 표시한다.
- 실행 결과의 모든 검수 항목과 정의된 검증 명령이 정확히 `PASS`이고 미실행·수동 검수·차단 항목이 없으면 별도 승인 질문 없이 `reviewer: 자동 승인(검증 명령)`으로 묵시 승인한다. `PASS_WITH_CAVEAT`, `보류`, `경고`, `FAIL`, `미실행`, `사용자 승인 필요`가 하나라도 있으면 자동 승인하지 않고 즉시 작업을 중단해 `검수 중` 또는 `재작업`으로 유지한다. 자동 승인 시 `latest_approved_run_id`와 `approved_at`을 기록하고 이 문서의 백로그 상태 및 `HANDOFF.md`를 같은 작업에서 `완료`로 갱신한다.
- 공개 A2A Schema·데이터 모델 변경, 외부 OAuth·실제 Provider 검증, UI 육안 검수, 모델 평가처럼 사람의 판단이나 별도 권한이 필요한 항목은 묵시 승인 대상에서 제외한다. 검증 명령을 하나라도 실행하지 않았거나 결과에 완료 조건에 영향을 주는 경고·보류·미해소 차단이 있으면 `검수 중` 또는 `재작업`을 유지한다.
- 이후 하위 마일스톤 검수는 이 규칙을 우선 적용한다. `PASS`가 아닌 결과가 하나라도 나오면 정규 다음 백로그는 착수하지 않는다. 단, 현재 검수 범위에서 원인이 명확하고 안전하며 아직 실행하지 않은 해결 방법이 남아 있으면 실패 실행을 보존한 뒤 해당 재작업·재검수를 자동 수행한다.
- 자동으로 다음 백로그를 착수하지 않은 경우에는 왜 착수하지 않았는지 설명하는 `자동 진행 보류 사유`를 반드시 함께 보고한다. 사유에는 `판정`(중단/보류/사용자 승인 대기), `관련 검증 항목과 결과`, `미실행·수동 검수·차단 항목`, `필요한 조치 또는 승인`, `재개 조건`, `다음 백로그`를 포함하며 실행 `result.md`와 `HANDOFF.md`에 동일하게 기록한다.
- 자동구현을 착수하지 않은 경우에도 `자동 구현 보류 사유`를 별도로 기록한다. 구현 코드가 아직 변경되지 않은 이유를 `판정`(중단/보류/사용자 승인 대기), 구현을 막은 검증 항목과 결과, 미실행·수동 검수·차단 항목, 필요한 조치 또는 승인, 재개 조건, 다음 구현 백로그로 설명한다. 단순히 상태만 `대기`·`검수 중`으로 기록하는 것은 완료 보고로 인정하지 않는다.
- 자동 다음 백로그 미착수 사유가 `재작업`인 경우에는 정규 후속 백로그로 진행하지 않고, 실행 `result.md`와 `HANDOFF.md`에 기록된 `재개 조건` 또는 `다음 착수 항목`의 재작업·재검수 백로그를 자동 착수한다. 이 자동 착수는 로컬 구현·테스트 등 별도 승인이 필요 없는 범위에만 적용하며, 외부 OAuth·실제 Provider, 공개 Schema·데이터 모델 변경, UI 육안 검수, 모델 평가, 원격 Push는 사용자 또는 검수자 승인을 기다린다.
- 자동 재작업·재검수에서 결과가 모두 정확히 `PASS`가 되면 그때 원래 정규 다음 백로그를 자동 착수한다. 다시 `PASS`가 아닌 결과가 나오더라도 서로 다른 미실행 해결 방법이 남아 있으면 후보별로 한 번씩 자동 수행한다. 동일 원인이 반복되거나 후보가 소진되거나 새 사용자 입력·권한이 필요하면 기존 승인 실행을 유지한 채 최종 중단하고 실패 항목·재현 명령·재개 조건을 갱신한다.
- 자동 재시도는 작업 디렉터리, module path, 환경 변수 전달, 일시적 프로세스·네트워크 상태처럼 완료 조건과 공개 계약을 바꾸지 않는 수정에 한정한다. 테스트 삭제·우회, 기대값 완화, 공개 Schema·데이터 모델 변경, 데이터 삭제는 자동 해결 방법에서 제외한다. 이미 승인된 외부 Provider 검수의 동등 범위 명령 수정은 기존 승인으로 재시도할 수 있지만 새 Scope·계정·Secret·외부 부작용은 다시 승인을 받아야 한다.
- 단, 선행 업무 기능이 아직 구현되지 않아 UI 육안 검수를 수행할 수 없는 경우에는 해당 UI 백로그를 선행 조건과 함께 `보류`로 기록할 수 있다. 이 예외는 차단 해소에 필요한 업무 구현을 진행할 수 있게 하는 일정 예외일 뿐이며, 보류된 UI 백로그를 완료로 표시하거나 후속 마일스톤 완료로 간주하지 않는다. 선행 작업 후에도 완료 조건을 제공하지 못한 것이 확인되면 기존 선행 가정을 수정하고 `재작업`으로 전환하며, 운영 Route를 변경하지 않는 테스트 전용 검수 환경 등 구체적인 재개 조건을 기록한다.
- 백로그의 묵시 승인은 하위 마일스톤 전체 승인을 뜻하지 않는다. 모든 백로그와 하위 마일스톤 통합 완료 기준을 충족한 뒤에만 하위 마일스톤을 `완료`로 표시한다.
- 자동 승인된 실행은 별도 진행 질문 없이 `다음 작업` 열의 백로그를 즉시 착수한 것으로 기록한다. 자동 착수한 백로그에서도 `PASS`가 아닌 결과가 하나라도 나오면 즉시 작업을 중단하고 사용자에게 상태와 재개 조건을 보고한다.

#### 자동 착수 허용 조건 요약

자동 착수는 다음 두 경로 중 하나일 때 허용한다. 두 경로 모두 외부 권한이나 사람의 판단이 필요한 예외 항목에는 적용하지 않는다.

| 경로 | 자동 착수 조건 | 자동 착수 대상 | 다음 단계 |
| --- | --- | --- | --- |
| 정상 진행 | 현재 실행의 모든 검수 항목·검증 명령이 정확히 `PASS`이고 미실행·수동 검수·경고·보류·차단이 없음 | 계획표의 정규 `다음 작업` 백로그 | 즉시 정규 백로그 진행 |
| 재작업 | 상태가 `재작업`이고 `result.md`·`HANDOFF.md`에 재개 조건과 로컬 재작업·재검수 백로그가 명시됨 | 명시된 재작업·재검수 백로그 | 재검수 전체가 정확히 `PASS`이면 정규 `다음 작업`으로 자동 전환 |

`다음 작업` 열에 문제 해결을 위한 재작업·재검수 항목이 지정된 경우에는 해당 항목을 정규 후속 백로그보다 우선 착수한다. 로컬 코드·테스트·환경 보정처럼 별도 권한이나 사람의 판단이 필요 없는 재작업이면 별도 진행 질문 없이 자동 착수한다. 재작업이 PASS로 끝나기 전에는 정규 후속 백로그를 시작하지 않는다.

`재작업` 재검수에서 `PASS`가 아닌 결과가 나오면 기존 승인 실행을 유지하고 남은 안전한 미실행 해결 방법을 후보별로 한 번씩 자동 수행한다. 동일 원인이 반복되거나 후보가 소진되면 중단한다. 외부 OAuth·실제 Provider 호출, 공개 Schema·데이터 모델 변경, UI 육안 검수, 모델 평가, 원격 Push는 최초 실행이나 범위 확장 전에 사용자 또는 검수자 승인이 필요하다. 이미 승인된 외부 검수의 동등 범위 명령·경로 수정 재시도는 기존 승인으로 수행할 수 있다. 자동 착수하지 않은 경우에는 `자동 진행 보류 사유`와 재개 조건을 실행 증빙 및 `HANDOFF.md`에 기록한다.

#### 검수 판정 알고리즘

자동 승인 대상인 하위 마일스톤은 다음 순서로 판정한다.

1. 실행 결과의 모든 검수 항목과 정의된 검증 명령을 수집한다.
2. 결과가 모두 정확히 `PASS`이고 `미실행`, `수동 검수`, `경고`, `보류`, `FAIL`, `차단`이 없으면 해당 실행을 `자동 승인(검증 명령)`으로 기록한다.
3. `PASS`가 아닌 결과가 하나라도 있으면 자동 승인과 정규 다음 백로그 판정을 중단한다. `latest_approved_run_id`는 변경하지 않고 상태를 `재작업`으로 유지한다. 현재 범위의 안전한 미실행 해결 방법이 있으면 실패를 먼저 기록한 뒤 자동 수정·재검수하고, 후보가 없거나 동일 실패가 반복될 때 최종 중단한다.
4. 중단 사유, 실패한 검증 항목, 재현 명령, 재개 조건을 해당 `runs/{run_id}/result.md`와 `HANDOFF.md`에 기록한다.
5. 자동 승인 조건을 충족하면 별도 진행 질문 없이 계획표·증빙·`HANDOFF.md`를 갱신하고 `다음 작업` 백로그를 즉시 착수한다. 단, 외부 OAuth·실제 Provider, 공개 Schema·데이터 모델 변경, UI 육안 검수, 모델 평가, 원격 Push처럼 명시 승인이 필요한 작업은 PASS여도 자동 착수하지 않는다.
6. 자동 승인 조건을 충족했더라도 예외로 다음 작업을 자동 착수하지 않으면, `자동 진행 보류 사유`와 재개 조건을 계획표·실행 증빙·`HANDOFF.md`에 표시한다. 문서만 읽어도 자동 진행이 멈춘 이유와 필요한 사용자 조치를 확인할 수 있어야 한다.
7. 3번에 따라 `재작업`이 된 경우, 재개 조건에 명시된 안전한 재작업·재검수는 별도 질문 없이 자동 착수한다. 재검수 실패 시 서로 다른 미실행 후보가 남아 있으면 후보별로 한 번씩 계속하고, 모두 `PASS`가 된 경우에만 5번의 정규 다음 백로그로 전환한다. 동일 원인 반복·후보 소진·새 승인 필요 시 자동 진행을 멈추고 중단 사유를 갱신한다.

이 알고리즘은 외부 OAuth·실제 Provider 검증, 공개 Schema·데이터 모델 변경, UI 육안 검수, 모델 평가처럼 별도 사용자 또는 검수자 판단이 필요한 항목의 최초 실행·범위 확장에는 적용하지 않는다. 해당 항목은 명시 승인을 받아야 하며, 승인 후 동일 범위에서 발생한 명령·경로 오류의 안전한 재시도에는 자동 재작업 규칙을 적용한다.
- M5.5 최종 인수는 각 하위 마일스톤 `README.md`의 `latest_approved_run_id`를 기준으로 판단한다.
- `README.md`에는 실행 명령, 코드/데이터 버전, 결과 경로와 수정 이력을 함께 기록한다.

### 2.5 `result.md` 표준 양식

각 하위 마일스톤의 검수 결과는 `docs/evidence/Mx/Mx.y/result.md`에 기록한다. 반복 실행 결과는 `runs/{run_id}/result.md`에 같은 양식을 사용한다. 양식의 모든 항목을 모든 작업에 채우지 않으며, 작업과 관련된 항목은 경로를 생략하지 않고 관련 없는 항목은 `해당 없음`으로 표시한다.

````markdown
# {Mx.y} 검수 결과

## 1. 기본 정보

- 마일스톤:
- 제목:
- 담당자:
- 검수자:
- 상태: 대기 / 진행 / 검수 중 / 완료 / 재작업 / 보류
- 실행일:
- 실행 ID:
- 코드 버전:
- 입력 데이터 버전:
- 작업 유형: API / DB·Migration / UI / 모델 평가 / 문서 / 기타

## 2. 최신 실행과 승인

- latest_run_id:
- latest_run_status:
- latest_approved_run_id:
- approved_at:

## 3. 목표와 완료 기준

- 목표:
- 완료 기준:
- 백로그 범위:
- 미완료·보류 백로그:

## 4. 구현 내용과 경로

- 구현 요약:
- 변경 전 동작:
- 변경 후 동작:
- 핵심 함수·클래스:
- 구현 코드:
- Schema 또는 Migration: (해당 작업만)
- UI 코드: (UI 작업만)
- 제외 범위:

구현 코드·Schema·Migration·UI·테스트 경로는 저장소 내 파일로 이동하는 Markdown 링크로 기록한다. 삭제된 파일은 링크를 만들지 않고 삭제 사실과 대체 검증 경로를 기록한다.

## 5. 테스트 파일 경로

- 단위 테스트: (해당 작업만)
- 통합 테스트: (해당 작업만)
- UI 테스트: (UI 작업만)
- Fixture/입력: (Fixture가 있는 작업만)
- 기대 결과:
- 모델 평가 Case: (LLM·Embedding·STT·RAG 평가만)
- 모델 평가 결과: (LLM·Embedding·STT·RAG 평가만)

## 6. 실행 명령과 결과

```text
{실행 명령}
```

- 실행 로그: (실행 로그가 필요한 작업만)
- API 응답 또는 Artifact: (API·A2A·Workflow 작업만)
- 화면 캡처: (UI·시연 작업만)
- 함수 문서화: (핵심 함수가 있는 코드 작업만)

## 7. 검수 항목

| 항목        | 결과      | 근거 경로         |
| ----------- | --------- | ----------------- |
| 완료 기준 1 | PASS/FAIL | 파일 또는 실행 ID |
| 완료 기준 2 | PASS/FAIL | 파일 또는 실행 ID |

## 8. 문제와 수정 이력

- 발견된 문제:
- 원인:
- 수정 내용:
- 재검수 실행 ID:

## 8.1 자동 진행 판정

- 자동 진행 판정: 자동 착수 / 중단 / 보류 / 사용자 승인 대기
- 자동 재작업 착수: 예 / 아니오 (재작업 사유일 때 기록된 재작업·재검수 백로그의 자동 착수 여부)
- 자동 진행 보류 사유:
- 판정을 막은 검증 항목과 결과:
- 미실행·수동 검수·차단 항목:
- 필요한 조치 또는 사용자 승인:
- 재개 조건:
- 다음 백로그:

## 9. 최종 판단

- 승인 여부:
- 검수 의견:
- 다음 조치:
````

`result.md`에는 Secret, 실제 Token, API Key, Presigned URL, 원본 회의 음성을 넣지 않고 경로·요약·checksum 또는 비식별 결과만 기록한다.

### 2.6 루트 `HANDOFF.md` 운영 규칙

저장소 루트의 `HANDOFF.md`는 전체 계획이나 검수 결과를 대신하지 않고, 현재 작업자가 다음 작업을 이어받을 수 있도록 최신 진행 상태를 요약한다. 다음 항목을 필수로 유지한다.

- 현재 마일스톤·하위 마일스톤·스프린트·상태
- 마지막 갱신 시각·작업자·기준 Git Commit·브랜치
- 완료된 항목과 승인된 `docs/evidence/Mx/Mx.y/result.md` 경로
- 현재 백로그 ID, 구현 중인 파일, 완료·잔여 작업
- 다음 착수 항목, 선행 조건, 담당자
- 차단 사항과 필요한 조치
- 중요한 기술 결정과 실행 방법
- 단위·통합·UI 테스트, Fixture, 평가 Case·결과 경로
- 최신 실행 ID와 최신 승인 실행 ID

`HANDOFF.md`는 작업 시작, 백로그 완료, 테스트 실패·차단, 하위 마일스톤 승인, 담당자 변경 시 갱신한다. 완료 항목은 명시 승인 또는 묵시 승인 조건을 충족한 증빙이 있을 때만 기록하고, 실제 Secret·API Key·Token·Presigned URL은 저장하지 않는다. 이전 인수인계 내용은 삭제하지 않고 `갱신 이력`에 남긴다.

### 2.7 루트 `AGENTS.md` 작업 규칙

저장소 루트의 `AGENTS.md`는 구현 Agent와 개발자가 작업할 때 지켜야 할 공통 절차를 정의한다. 작업자는 `docs/README.md`와 대상 폴더 README, `HANDOFF.md`, 관련 마일스톤 문서, 승인 증빙, Schema·테스트 순서로 확인한 뒤 구현을 시작한다.

다음 규칙을 적용한다.

- 루트에 없는 `README.md`를 전제로 하지 않고 대상 폴더의 README를 확인한다.
- `Workspace` 권한 범위를 임의로 추가하지 않으며, 현재 계약에 정의된 요청 `user_id` 조건을 모든 조회에 적용한다.
- 작업 시작 시 증빙 폴더의 `README.md`를 준비하고, 실행 결과가 생긴 뒤에만 `runs/{run_id}/result.md`를 작성한다.
- 모든 테스트를 무조건 실행하지 않고 변경 범위에 해당하는 기존 테스트를 우선 실행한다. 외부 Secret이 필요한 테스트는 설정 여부와 미실행 사유를 기록한다.
- 함수 Docstring/JSDoc, 테스트 파일 경로, Fixture·평가 Case·결과 경로를 검수 자료에 기록한다.
- 완료 시 `HANDOFF.md`에 변경 내용·테스트 결과·증빙·남은 문제·다음 백로그를 갱신한다.

`AGENTS.md`는 개발 절차를 정의하고, 마일스톤 완료 기준은 이 문서의 하위 마일스톤 표와 `result.md`가 정의한다. 두 문서의 내용이 다르면 공개 Schema·API 계약과 승인된 증빙을 우선 확인하고 변경 사항을 문서에 반영한다.

### 2.8 커밋·Push 및 Pull Request 규칙

구현 변경은 백로그와 증빙을 추적할 수 있도록 작업 브랜치에서 수행한다. 로컬 커밋은 백로그 단위로 세분화하되 원격 Push는 하위 마일스톤 완료 체크포인트로 묶는다. 이 절의 규칙은 코드, Schema, Migration, UI, 테스트와 문서 변경에 모두 적용한다.

권장 Git 구조는 `C:\dev\workmate`를 루트 문서·증빙·평가 자료를 추적하는 Superproject로 사용하고 기존 `workmate-agent` 저장소만 Submodule로 등록해 이력을 보존하는 방식으로 확정한다. `workmate-ui`는 1차로 완성해 개인용으로 보관하고 2차로 팀 공통 Orchestrator UI 양식에 맞게 이식하는 대상으로 결정이 바뀌었다 — 더 이상 `.gitignore` 제외·Submodule/구현/검수 범위 제외 대상이 아니다. `workmate-ui`를 Superproject에 어떻게 편입할지(Submodule 등록 vs 일반 추적 디렉터리)는 별도로 확정해 `HANDOFF.md`에 기록한다. 구현 착수 전 Superproject 구성과 기준 Commit을 만들고 `workmate-agent` Submodule Commit을 `HANDOFF.md`에 기록한다. 기존 하위 저장소를 병합하거나 이력을 다시 만들지 않으며, 실제 Superproject 구성이 끝나기 전까지는 구현 착수 차단 사항으로 유지한다.

#### 브랜치와 커밋

- 브랜치는 기본적으로 하위 마일스톤 단위로 만든다. 권장 형식은 `feat/M0.1-a2a-contract`, `feat/M1.2-external-sources`이며, 독립 배포나 긴급 수정처럼 분리가 필요한 경우에만 `fix/M1.2-04-watch-renewal` 같은 백로그 브랜치를 사용한다.
- 기준 브랜치에 직접 Push하지 않고 작업 브랜치에서 Pull Request를 만든다.
- 한 커밋은 하나의 논리적 변경만 포함한다. 구현·테스트·증빙 커밋을 분리하면 검수 이력이 명확해진다.
- 커밋 메시지는 `<type>(<backlog-id>): <change>` 형식을 사용한다.
- 백로그가 완료돼도 구현·테스트·증빙은 로컬 커밋으로만 보존한다. 하위 마일스톤의 모든 백로그와 통합 완료 기준이 승인된 뒤 관련 커밋을 한 번에 원격 Push한다.
- 중간 Push는 다른 작업자 인수인계·원격 협업, 장기간 작업의 원격 백업, 사용자 명시 요청이 있는 경우에만 수행한다. 단순 테스트 PASS, 증빙 추가, 상태 변경만으로는 Push하거나 Push 승인을 묻지 않는다.

예시:

```text
feat(M1.2-04): implement Gmail watch renewal
test(M1.2-04): add duplicate notification tests
docs(M1.2-04): document watch expiration contract
evidence(M1.2-04): record verification run
```

#### Push 전 확인

하위 마일스톤 완료 또는 위 예외 조건으로 실제 Push 시점에 도달했을 때 다음 조건을 모두 확인한 뒤 작업 브랜치를 Push한다.

1. 변경 범위의 단위·통합·UI 테스트를 실행한다.
2. `git diff --check`를 실행한다.
3. 관련 Schema와 A2A Contract Test를 확인한다.
4. Secret, API Key, Token, Presigned URL, 원본 회의 음성이 변경에 포함되지 않았는지 확인한다.
5. `docs/evidence/Mx/Mx.y/runs/{run_id}/result.md`에 실행 명령·결과·경로를 기록한다.
6. `HANDOFF.md`에 현재 상태·테스트·증빙·남은 문제·다음 백로그를 갱신한다.

#### Pull Request와 Merge

Pull Request에는 백로그 ID, 변경 파일, 테스트 명령과 결과, 실행 ID·증빙 경로, 남은 문제, Schema/API 계약 변경 여부를 기록한다. 마일스톤은 명시 승인 또는 묵시 승인 조건으로 `latest_approved_run_id`가 확정된 뒤에만 완료로 표시하고 Merge한다. 실패한 실행은 삭제하지 않고 다음 실행과 별도로 보존한다.

`HANDOFF.md`의 `기준 Git Commit`은 인수인계 시점에 검증된 마지막 커밋을 의미한다. 증빙의 실행 ID와 함께 기록하며, 이후 인수인계 문서 갱신 커밋과 구분한다.

### 2.9 개발 진행상황 보고 규칙

개발 진행상황은 일일 보고가 아니라 작업 이벤트가 발생할 때 갱신한다. 정기적인 일일 보고서나 동일 내용의 반복 보고서는 만들지 않는다.

보고가 필요한 시점:

1. 백로그 작업 시작
2. 구현 범위 또는 담당자 변경
3. 테스트 실행 결과 발생
4. 테스트 실패·외부 인증·Provider 장애 등 차단 발생
5. 하위 마일스톤 검수 시작
6. 검수 승인 또는 재작업 결정
7. 다음 작업자에게 인수인계

진행상황은 `HANDOFF.md`에 요약하고, 실행 결과와 검수 근거는 `docs/evidence/Mx/Mx.y/`에 기록한다. 보고서에는 다음 항목을 포함한다.

```text
마일스톤·하위 마일스톤:
백로그 ID:
상태: 대기 / 진행 / 검수 중 / 완료 / 재작업 / 보류
작업·변경 내용:
변경 파일:
실행한 테스트와 결과:
실행 ID·증빙 경로:
차단 사항·남은 문제:
다음 착수 작업:
브랜치·기준 Git Commit:
```

`완료` 보고는 명시 승인 또는 묵시 승인 조건으로 확정된 `latest_approved_run_id`가 있을 때만 작성한다. 테스트 결과가 없는 구현 진행 내용은 `진행`으로만 기록하고 완료 항목에 포함하지 않는다.

### M0 — 계약·검증 기반

주요 산출물:

- Orchestrator와 A2A 버전·인증·Artifact Schema 합의
- LLM `openai/gpt-4.1-mini`, Embedding `openai/text-embedding-3-small` 1536차원, STT `gpt-4o-transcribe` 확정
- Gmail·Google Calendar OAuth 범위와 Watch 계약 확정
- Workmate 내부 5개 Skill 검증 챗봇과 UI
- 샘플 데이터와 공통 Artifact 검증 테스트

완료 기준:

- 내부 검증 챗봇과 Orchestrator가 같은 5개 Skill에서 동일한 구조화 Artifact를 받는다.
- Agent Card, Skill Schema, Artifact Schema 검증이 통과한다.
- Legacy Mock Shell은 운영 실행 경로에서 제거한다. 아직 구현하지 않은 업무 Workflow는 성공한 고정 응답으로 위장하지 않고 명시적인 미구현 오류를 반환하며, Mock·Fake는 테스트 Fixture에서만 사용한다.

### M1 — 데이터·우선순위

주요 산출물:

- DB Migration과 샘플 데이터
- Task 등록·조회·수정·Soft Delete API와 UI
- Task·Gmail·Calendar 응답 정규화
- Gmail Push·History와 Calendar Watch·증분 동기화
- SSE 임시 할 일 제안과 중복 검증
- 날짜 범위·우선순위 계산·오늘 브리핑 A2A 응답

완료 기준:

- 같은 입력에서 같은 Top 3와 점수가 나온다.
- Gmail·Calendar 원본 중복 Task가 생성되지 않는다.
- Task·Gmail·Calendar·브리핑·우선순위 운영 경로가 실제 Repository·Provider Workflow를 사용하며 고정 Mock 응답이나 Mock fallback을 사용하지 않는다.

### M2 — 브리핑·주간 보고

주요 산출물:

- 완료·진행·지연·미해결 이슈 분류
- 근거 있는 다음 주 계획 추출
- LLM 보고서와 Schema 검증
- 주간 보고서 UI와 Markdown 복사

완료 기준:

- 모든 보고서 항목이 source ID를 가진다.
- 근거 없는 계획은 확정 계획으로 표시되지 않는다.
- 주간 보고 운영 경로가 실제 집계 데이터와 승인된 LLM Workflow를 사용하며 고정 보고서 Mock이나 Mock fallback을 사용하지 않는다.

### M3 — 회의 분석

주요 산출물:

- 녹음 파일 업로드와 실시간 녹음
- 임시·최종 STT와 비동기 분석 Task
- 백엔드 준비 후 R2 Storage Adapter·Presigned URL·원본 Object Key 저장 연결
- 통합 회의 분석 Text와 Action Item 추출
- 사용자 승인 후 Task 등록

완료 기준:

- 같은 Action Item을 두 번 승인해도 Task는 하나다.
- 최종 Transcript와 Action Item 근거 구간을 조회할 수 있다.
- 회의 입력·STT·분석·승인 운영 경로가 실제 Storage·STT·DB·LLM Workflow를 사용하며 고정 Transcript·Action Item Mock이나 Mock fallback을 사용하지 않는다.

### M4 — 회의 검색

주요 산출물:

- MeetingChunk와 Embedding 저장
- `meeting_chunks.embedding vector(1536)` Migration과 전체 재임베딩
- Dense + PostgreSQL Trigram RRF 검색
- pgvector HNSW 인덱스와 출처 응답
- 근거 부족 처리

완료 기준:

- 평가 질문의 Hybrid Top-3 검색 정확도 80% 이상이다.
- 모든 답변에 회의명·날짜·Chunk 출처가 있다.
- 회의 검색 운영 경로가 실제 Chunk·Embedding·Trigram·HNSW와 근거 기반 답변 Workflow를 사용하며 고정 검색 결과 Mock이나 Mock fallback을 사용하지 않는다.

### M5 — 통합·시연

주요 산출물:

- Orchestrator 종단 간 연결
- `http://workmate-agent:8001/a2a/message:send` 호출
- Agent Card 조회와 5개 공개 Skill 호출
- 잘못된 Bearer Token의 HTTP 401 검증
- 권한·부분 실패·로그·데이터 최신성 표시
- Docker Compose와 시연 데이터 초기화

완료 기준:

- 여덟 시나리오 종단 간 시연과 인수 테스트를 통과한다.
- 내부 검증 챗봇 결과와 Orchestrator 결과의 Schema·Artifact 형태가 일치한다.
- 다섯 공개 Skill 모두 실제 업무 Workflow에 연결되고 운영 Profile에서 Mock Handler·고정 샘플 응답·Mock fallback이 활성화되지 않는다.

#### M5.1 예외 착수 규칙

M5.1의 직접 선행조건(`M0.3`, `M1.5`, `M2.3`, `M3.5`, `M4.4`)이 모두 완료되면 M2.4 UI 육안 검수가 보류 중이어도 A2A 통합 구현을 예외적으로 착수할 수 있다. 이 예외는 M5 상위 진입이나 완료를 의미하지 않으며, M5 상위 상태는 M2·M3·M4 전체 완료 전까지 `대기`로 유지한다. M5.1 결과는 별도 증빙으로 검수하고 실제 Orchestrator 종단 간 호출이 확인되기 전에는 완료 처리하지 않는다.

## 3. 테스트

| 영역          | 최소 검증                                                                                                                                 |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 날짜          | 월/연도 경계, 월요일/일요일, timezone, DST                                                                                                |
| 우선순위      | 점수 요소, 동점, 완료 제외, 변경 사유                                                                                                     |
| 할 일         | 등록·수정·상태 변경, 삭제 후 조회·브리핑·우선순위 제외                                                                                    |
| Gmail         | 읽음 감지, `sync_cursor(historyId)` 복구, 브라우저 연결·종료, 승인·무시, Message ID 중복 Task 방지                                        |
| Gmail과 Top 3 | `rank_priorities`에서 Gmail 미호출, Gmail 장애 중 계산, 미승인 메일 제외, 승인 시 마감·중요도 저장                                        |
| Calendar 제안 | Watch 갱신, `sync_cursor(nextSyncToken)` 복구와 `410 Gone` 초기화, 브라우저 연결·종료, 동일 원본 차단, 유사 Task 재확인, 브리핑 등록 상태 |
| 통합          | 소스 하나 실패 시 부분 결과                                                                                                               |
| 회의          | 목록·상세 조회, Chunk Pagination, 선택 근거 자동 스크롤·강조, `evidence_text` 원문 일치·읽기 전용, 중복 승인                              |
| RAG           | 실제 회의록 64 Chunk·60 Case, Hybrid Hit@3 80% 이상, 출처 검증                                                                            |
| 보안          | 권한 없는 사용자 접근 차단, 토큰 누락 거부                                                                                                |
| A2A           | Agent Card, 즉시 응답, 장기 Task 성공/실패                                                                                                |

A2A 테스트는 공식 SDK REST Route 계약을 기준으로 한다. 업무 Skill 구현과 AgentExecutor·Artifact·Agent Card·인증·Streaming·Task 조회·취소 테스트를 개발·검수 범위에 포함한다. Push Notification은 저장소·발송기 연결 전까지 비활성화하고 별도 후속 범위로 기록한다.

성능 목표:

- 브리핑/우선순위: 외부 Provider 지연 제외 5초 이내
- 주간 보고서: 15초 이내
- 회의 검색: 5초 이내
- 우선순위: 같은 입력에 항상 같은 결과
- Action Item 필수 필드 정확도: 평가 세트 기준 80% 이상

## 4. 데모 순서

1. 회의의 미승인 Action Item을 확인하고 승인
2. 오늘 브리핑에서 새 Task가 포함된 Top 3 확인
3. Task 마감일 변경 후 순위 변경 사유 확인
4. 과거 회의 결정사항 질문과 출처 확인
5. 주간 보고서에서 완료/진행/이슈/다음 주 계획 확인

## 5. 구현 전 결정사항

| 결정           | 권장 기본값                                                                                                    |
| -------------- | -------------------------------------------------------------------------------------------------------------- |
| 메일/캘린더    | Gmail API와 Google Calendar API                                                                                |
| Task 원장      | Workmate PostgreSQL                                                                                            |
| LLM            | OpenAI 호환 API · `openai/gpt-4.1-mini`; [평가 계획과 이력](11-llm-evaluation-plan.md)에 따라 보류 후보 재평가 |
| Embedding      | `openai/text-embedding-3-small`, 1536차원; Dense + Trigram RRF + HNSW                                          |
| STT            | OpenAI `gpt-4o-transcribe`; 파일 기반·Realtime Streaming MVP 확정                                              |
| 원본 음성 저장 | Cloudflare R2 Private 단일 버킷 `workmate`; Object Key만 DB 저장                                               |
| A2A 버전       | Orchestrator와 동일한 고정 버전                                                                                |
| 원본 음성 보존 | 설계상 30일 보존·삭제; 실제 R2 Lifecycle 검증 대기                                                             |
| 보고서 대상    | 개인부터 시작, 팀/경영 보고는 권한 확정 후 추가                                                                |

### 5.1 Embedding 확정 근거

2026-08-11 실제 회의록 평가에서 다음 결과를 확인해 운영 검색 구성을 확정했다.

| 항목      | 확정값                                            | 근거                                                  |
| --------- | ------------------------------------------------- | ----------------------------------------------------- |
| 모델      | `openai/text-embedding-3-small`                   | 실제 `/embeddings` 응답과 1536차원 출력 확인          |
| 저장 차원 | `vector(1536)`                                    | 모델 출력 차원과 PostgreSQL Migration 호환            |
| 거리 함수 | Cosine                                            | `vector_cosine_ops` 기반 비교 및 HNSW Index Scan 확인 |
| 검색      | Dense + Trigram RRF + HNSW                        | 64 Chunk·60 Case에서 Hybrid Hit@3 98.21%, Hit@5 100%  |
| HNSW 품질 | Recall@5 100%                                     | 정확 검색 대비 결과 일치 및 Index Scan 확인           |
| 지연      | Hybrid DB p95 66.3ms, Query Embedding p95 893.1ms | 운영 성능 기준 통과                                   |

상세 결과는 [Embedding 평가 계획](10-embedding-evaluation-plan.md)과 [평가 이력](../embedding-evaluation/EVALUATION_HISTORY.md), [PostgreSQL 지표](../embedding-evaluation/results/postgres-metrics-20260811-101253.json)에 기록했다. 모델 변경 시 전체 Chunk 재임베딩과 동일 평가를 다시 수행한다.

## 6. 최종 산출물

- Workmate AI A2A 서버와 Agent Card
- PostgreSQL+pgvector 스키마와 시연 데이터
- 다섯 개 최소 화면
- 여덟 시나리오 인수 테스트
- Docker Compose 실행 환경
- API/A2A Schema 문서와 데모 스크립트
### 2.1.4 M1.3 Task 관리 진행 상태

M1.3-01에서 `/api/v1/tasks` 등록·조회·수정·Soft Delete API를 구현했고, M1.3-02에서 `/tasks` UI와 PostgreSQL 통합 검수를 완료했다. 실행 `20260813-201500`은 전체 59개 테스트와 UI 계약 검수가 PASS였고 사용자 육안 검수도 승인되어 M1.3을 완료 처리했다. M0.4-03 재검수 결과 M1.3의 동기 Task CRUD는 실제 `WORKING` A2A Task를 제공하지 않는 것으로 확인됐다. 따라서 다음 작업은 운영 Route를 변경하지 않는 테스트 전용 `WORKING` Task UI Fixture 실행 환경 마련이다.

| ID | 작업 | 구현 경로 | 테스트 경로 | 완료 조건 | 상태 |
| --- | --- | --- | --- | --- | --- |
| M1.3-01 | Task CRUD API | [`app/task_api.py`](../workmate-agent/app/task_api.py), [`app/main.py`](../workmate-agent/app/main.py) | [`tests/test_task_api.py`](../workmate-agent/tests/test_task_api.py) | 등록·조회·수정·Soft Delete·사용자 격리·외부 원본 중복 테스트 PASS | 완료 |
| M1.3-02 | Task 관리 UI 및 통합 검수 | `workmate-agent/app/task_ui.py` | `tests/test_task_ui.py`, PostgreSQL 통합 테스트 | Task 목록·등록·수정·상태 변경·삭제 확인과 PostgreSQL 통합 테스트 PASS | 완료 |

### 2.1.5 M1.4 Task 제안 진행 상태

M1.4는 외부 동기화 결과에서 후보로 판정된 Gmail Message·Calendar Event만 사용자별 메모리 Hub로 발행하고, SSE로 전달한다. 제안은 DB에 저장하지 않으며 사용자가 `approve`한 경우에만 `Task.source_type`·`source_id`를 지정해 기존 Task Repository에 저장한다. `ignore`는 저장하지 않는다. 모든 검토 POST는 `Idempotency-Key`를 요구하고 동일 원본·유사 Task를 각각 멱등·재확인 규칙으로 처리한다.

실행 `20260813-215728`에서 M1.2 Adapter 정규화, M1.3 Task Repository·API와 M1.4 제안 Hub·SSE·승인 API를 묶은 51개 회귀 테스트, `compileall`, `git diff --check`가 모두 PASS했다. PostgreSQL 통합 테스트는 M1.1/M1.2 승인 증빙에서 이미 완료했으며 이번 실행에는 외부 DB 미설정으로 인한 SKIP을 포함하지 않았다. 자동 승인 규칙에 따라 M1.4를 `완료`로 전환한다. 상세 결과는 [`M1.4 검수 결과`](evidence/M1/M1.4/runs/20260813-215728/result.md)에 기록한다.

| ID | 작업 | 구현 경로 | 테스트 경로 | 완료 조건 | 상태 |
| --- | --- | --- | --- | --- | --- |
| M1.4-01 | 제안 Hub·SSE 발행 | [`app/proposal_api.py`](../workmate-agent/app/proposal_api.py), [`app/workflows/external_sync.py`](../workmate-agent/app/workflows/external_sync.py) | [`tests/test_proposals.py`](../workmate-agent/tests/test_proposals.py) | 사용자별 후보 발행·SSE Event·비후보 제외 PASS | 완료 |
| M1.4-02 | 승인·무시·원본 멱등 | [`app/proposal_api.py`](../workmate-agent/app/proposal_api.py), [`app/main.py`](../workmate-agent/app/main.py) | [`tests/test_proposals.py`](../workmate-agent/tests/test_proposals.py) | 승인 시 1개 Task, 무시 시 0개, Idempotency-Key·사용자 범위 PASS | 완료 |
| M1.4-03 | 유사 Task 재확인 | [`app/proposal_api.py`](../workmate-agent/app/proposal_api.py) | [`tests/test_proposals.py`](../workmate-agent/tests/test_proposals.py) | `SIMILAR_TASK_EXISTS` 후 명시 허용 시에만 생성 PASS | 완료 |

### 2.1.6 M1.5 우선순위·브리핑 구현 계획 검토

M1.5는 M1.4까지 승인된 Task·Gmail·Calendar 경계를 사용해 결정적 우선순위와 오늘 브리핑을 연결한다. M1.5-01~04 구현과 실제 Provider 검수를 완료했고, M1.5-05에서 PostgreSQL·Contract·성능·기존 M0/M1 회귀를 통합 검수했다. 상세 결과는 [`M1.5-05 실행 결과`](evidence/M1/M1.5/runs/20260813-225921/result.md)에 기록했으며 자동 승인 규칙에 따라 M1.5를 완료 처리했다.

#### 구현 전 확정해야 할 계약

- 우선순위 계산 입력은 승인·저장된 미완료 Task와 사용자 timezone 기준 `as_of`다. `rank_priorities`는 Gmail을 호출하지 않으며, Gmail·Calendar의 실시간 신호는 승인 Task 또는 별도 브리핑 신호로만 사용한다.
- `PrioritySnapshot`은 사용자·Task별 계산 시점의 점수·순위·점수 구성·변경 사유를 PostgreSQL에 저장한다. 동일 `user_id`·`as_of` 재실행은 동일 결과를 반환하고 Snapshot 중복 정책을 명시한다.
- `priority_hint`(0~10)는 설계 규칙의 중요도 구간으로 결정적으로 매핑한다. 권장 기본 매핑은 `0~2=0`, `3~4=8(보통)`, `5~7=15(높음)`, `8~10=20(긴급)`이며, 구현 전 이 매핑을 테스트 Fixture와 함께 고정한다.
- `blocked_or_overdue`는 `status=blocked`를 15점, 완료·취소가 아닌 기한 초과를 10점으로 계산하고 두 조건이 동시에 성립할 때의 상한·우선 규칙을 명시한다. Task DB에 없는 “타 업무 영향” 정보는 새 컬럼을 임의로 추가하지 않고 M1.5 범위에서 제외하거나 별도 승인 백로그로 분리한다.
- `meeting_commitment`는 M1.5에서 `source_type=action_item`으로 저장된 승인 Task만 10점으로 간주한다. 회의 원본·ActionItem 테이블을 새로 만들거나 공개 Schema를 변경하지 않으며, 실제 회의 분석 연결은 M3.4~M3.5에서 확장한다.
- `calendar_relevance`의 “관련” 판정 입력과 시간 창(24시간/3일)을 명시한다. Calendar Event 원문을 DB에 저장하지 않고, Adapter 결과의 사용자 범위·timezone 정규화 값으로만 계산한다.
- `daily_briefing`은 Calendar·Gmail 장애 시 Task 기반 Top 3와 사용 가능한 신호를 반환하고 `warnings`와 데이터 기준 시각을 포함한다. 핵심 Task 저장소를 읽지 못하면 성공 Artifact가 아니라 정의된 실패 상태를 반환한다.
- 요청 본문의 `user_id`는 인증된 OIDC subject와 일치해야 하며, 모든 Task·Snapshot·Provider 조회에 동일한 사용자 범위를 적용한다.

#### M1.5 백로그 분해

| ID | 작업 | 구현 경로 | 테스트·증빙 | 완료 조건 | 다음 작업 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| M1.5-01 | 점수 Domain·시간 경계 | [`app/domain/priority.py`](../workmate-agent/app/domain/priority.py) | [`tests/test_priority_domain.py`](../workmate-agent/tests/test_priority_domain.py) | 공식 점수식·priority_hint 매핑·상태 제외·UTC/사용자 timezone·DST·동점 정렬이 결정적으로 PASS | M1.5-02 | 완료 |
| M1.5-02 | PrioritySnapshot 저장 경계 | [`migrations/003_priority_snapshots.sql`](../workmate-agent/migrations/003_priority_snapshots.sql), [`app/repositories/priority.py`](../workmate-agent/app/repositories/priority.py) | [`tests/test_priority_repository.py`](../workmate-agent/tests/test_priority_repository.py) | 사용자 격리·점수 구성·순위·변경 사유 저장과 재조회·동일 계산 시점 멱등 정책 PASS; 실제 PostgreSQL 연결은 M1.5-05에서 검수 | M1.5-03 | 완료 |
| M1.5-03 | `rank_priorities` Workflow/API | [`app/workflows/priority.py`](../workmate-agent/app/workflows/priority.py), [`app/a2a/runtime.py`](../workmate-agent/app/a2a/runtime.py) | [`tests/test_priority_workflow.py`](../workmate-agent/tests/test_priority_workflow.py), [`tests/test_contract.py`](../workmate-agent/tests/test_contract.py) | Gmail 미호출·Task DB 후보만 사용·Top 3·source_refs·변경 사유·인증 범위 PASS | M1.5-04 | 완료 |
| M1.5-04 | 오늘 브리핑 Workflow | [`app/workflows/daily_briefing.py`](../workmate-agent/app/workflows/daily_briefing.py), [`app/a2a/runtime.py`](../workmate-agent/app/a2a/runtime.py) | [`tests/test_daily_briefing.py`](../workmate-agent/tests/test_daily_briefing.py), [`tests/test_google_adapters.py`](../workmate-agent/tests/test_google_adapters.py), [`tests/test_contract.py`](../workmate-agent/tests/test_contract.py) | 오늘 범위·Calendar/Gmail 신호·Top 3 통합, Provider 부분 실패 `warnings`, 최신성 표시, 승인 Schema 및 Gmail·Calendar 실호출 PASS | M1.5-05 | 완료 |
| M1.5-05 | 통합·회귀 검수 | [`tests/test_m1_5_integration.py`](../workmate-agent/tests/test_m1_5_integration.py), [`M1.5-05 실행 결과`](evidence/M1/M1.5/runs/20260813-225921/result.md) | PostgreSQL·Contract·성능·문서 검사 | M1.5-01~04와 기존 M0/M1 회귀가 모두 정확히 PASS, SKIP·수동 검수·차단 없음 | M2.1 | 완료 |

M1.5 계획 검토에서 확인된 누락·충돌은 다음과 같다: 현재 `PrioritySnapshot` Migration·Repository·Workflow·테스트가 없고, `priority_hint`와 중요도 점수의 매핑이 문서에 정의되지 않았으며, Calendar 연관성·blocked/overdue 동시 조건·Snapshot 중복 정책이 미확정이다. 이 항목을 확정하지 않은 상태에서 구현하면 결과가 결정적이지 않거나 승인된 Skill Schema의 `score_breakdown`, `changes`, `source_refs`를 채우지 못할 수 있다.

### 2.1.7 검증 PASS 후 자동 다음 백로그 착수 규칙

검증 실행의 모든 검수 항목과 정의된 검증 명령이 정확히 `PASS`이고 `SKIP`·수동 검수·경고·차단이 없으면, 해당 실행을 `자동 승인(검증 명령)`으로 기록한 뒤 `다음 작업` 열의 백로그를 별도 진행 질문 없이 즉시 착수한다. 계획표의 현재 백로그와 다음 백로그 상태, 실행 증빙 `README.md`·`result.md`, `HANDOFF.md`를 같은 변경에서 갱신한다.

이 규칙은 현재 M1.5-05처럼 PostgreSQL·Contract·회귀 검수가 모두 PASS한 정상 진행에 적용한다. 다음 백로그가 외부 OAuth·실제 Provider 호출, 공개 Schema·데이터 모델 변경, UI 육안 검수, 모델 평가 또는 원격 Push를 포함하면 PASS 여부와 관계없이 사용자 또는 검수자의 명시 승인을 먼저 받는다. `PASS`가 아닌 결과가 하나라도 나오면 정규 다음 백로그 자동 착수를 중단하고 실패·재개 조건을 기록한다.

### 2.1.8 M2.1 주간 데이터 분류 백로그 정의 및 구현 계획

M2.1은 승인된 Task·Gmail·Calendar·회의 Action Item 원본을 주간 기간과 사용자 범위로 분류해 `weekly_report`의 네 개 업무 목록과 `source_refs`를 제공하는 기반을 만든다. 이 단계에서는 LLM 보고서 문장 생성이나 다음 주 계획 확정을 수행하지 않으며, 해당 책임은 M2.2~M2.3으로 넘긴다. 운영 Workflow는 실제 Repository와 동기화 결과를 사용하고 고정 보고서 Mock이나 Mock fallback을 사용하지 않는다.

M2.1-06 통합 검수가 모두 PASS하여 M2.2-01을 착수했다. M2.2-01은 결정론적 근거 후보 추출만 담당하고, LLM 문장 생성과 제안·확정 의미 판정은 M2.2-02 이후 별도 검수 범위로 유지한다.

#### 구현 전 확정 계약

- 기간은 사용자 timezone 기준 `week_of`부터 7일 미만의 주간 범위로 정규화하고, 경계 시각은 `as_of`와 동일한 timezone으로 비교한다.
- Task 상태는 `done`을 완료, `todo`·`in_progress`를 진행, 마감일 초과 또는 `blocked`를 지연으로 분류한다. 하나의 Task는 한 목록에만 들어가며 `cancelled`·Soft Delete 항목은 제외한다.
- Gmail 요청사항과 Calendar 제안은 승인되어 Task 원장에 저장된 항목만 분류한다. 승인되지 않은 신호는 보고서 목록에 넣지 않는다.
- 회의 Action Item은 M3에서 생성될 `source_type=action_item` Task와 연결할 수 있도록 `source_refs`에 원본 ID를 남기며, M2.1에서는 회의 원문·Transcript를 새로 저장하지 않는다.
- 모든 분류 항목은 최소 하나의 유효한 `source_refs`를 가져야 하며, 원장에 없는 ID·LLM이 생성한 ID·사용자 범위가 다른 ID는 실패로 처리한다.
- 집계 결과가 비어 있으면 빈 배열과 명시적인 기간을 반환한다. Provider가 실패하면 사용 가능한 Task 원장으로 부분 결과를 반환하고 `warnings`를 남긴다.

#### M2.1 백로그

| ID | 작업 | 구현 경로 | 테스트·증빙 | 완료 조건 | 다음 작업 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| M2.1-01 | 주간 기간·사용자 범위 정규화 | [`app/domain/weekly.py`](../workmate-agent/app/domain/weekly.py) | [`tests/test_weekly_classification.py`](../workmate-agent/tests/test_weekly_classification.py), [`M2.1-01 실행 결과`](evidence/M2/M2.1/runs/20260813-231130/result.md) | timezone·DST·주 경계와 `user_id` 필터가 결정적으로 PASS | M2.1-02 | 완료 |
| M2.1-02 | Task 상태 분류 | [`app/domain/weekly.py`](../workmate-agent/app/domain/weekly.py) | [`tests/test_weekly_classification.py`](../workmate-agent/tests/test_weekly_classification.py), [`M2.1-02 실행 결과`](evidence/M2/M2.1/runs/20260813-231401/result.md) | 완료·진행·지연·취소·Soft Delete 분류가 상호 배타적으로 PASS | M2.1-03 | 완료 |
| M2.1-03 | Gmail·Calendar 승인 Task 연결 | [`app/workflows/weekly_classification.py`](../workmate-agent/app/workflows/weekly_classification.py) | [`tests/test_weekly_source_link.py`](../workmate-agent/tests/test_weekly_source_link.py), [`M2.1-03 실행 결과`](evidence/M2/M2.1/runs/20260813-231904/result.md) | 승인된 원본만 포함되고 source ID·사용자 범위가 검증됨 | M2.1-04 | 완료 |
| M2.1-04 | 회의 Action Item 연결 경계 | [`app/workflows/weekly_classification.py`](../workmate-agent/app/workflows/weekly_classification.py) | [`tests/test_weekly_source_link.py`](../workmate-agent/tests/test_weekly_source_link.py), [`M2.1-04 실행 결과`](evidence/M2/M2.1/runs/20260813-232223/result.md) | `source_type=action_item` Task가 원본 ID와 연결되고 미존재 원본은 차단됨 | M2.1-05 | 완료 |
| M2.1-05 | 주간 집계·Artifact 입력 생성 | [`app/workflows/weekly_classification.py`](../workmate-agent/app/workflows/weekly_classification.py) | [`tests/test_weekly_source_link.py`](../workmate-agent/tests/test_weekly_source_link.py), [`tests/test_contract.py`](../workmate-agent/tests/test_contract.py), [`M2.1-05 실행 결과`](evidence/M2/M2.1/runs/20260813-232437/result.md) | 네 목록·기간·source_refs가 승인 Schema 입력으로 검증됨 | M2.1-06 | 완료 |
| M2.1-06 | 통합·부분 실패 검수 | [`tests/test_m2_1_integration.py`](../workmate-agent/tests/test_m2_1_integration.py) | [`M2.1-06 실행 결과`](evidence/M2/M2.1/runs/20260813-232643/result.md) | 실제 Repository·Provider 경계, 부분 실패 warnings, 회귀 검사가 모두 PASS | M2.2-01 | 완료 |

### 2.1.9 M2.2 계획·근거 추출 백로그

| ID | 작업명 | 구현 경로 | 테스트 경로 | 완료 조건 | 다음 작업 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| M2.2-01 | 다음 주 계획 근거 후보 추출 | [`app/workflows/weekly_classification.py`](../workmate-agent/app/workflows/weekly_classification.py) | [`tests/test_weekly_source_link.py`](../workmate-agent/tests/test_weekly_source_link.py), [`M2.2-01 실행 결과`](evidence/M2/M2.2/runs/20260813-233115/result.md) | 다음 주 마감·미완료 Action Item·근거 있는 명시 계획만 추출하고 근거 없는 계획 차단 | M2.2-02 | 완료 |
| M2.2-02 | 제안·확정 의미 판정 및 LLM 평가 경계 | [`app/workflows/weekly_report.py`](../workmate-agent/app/workflows/weekly_report.py) | [`tests/test_weekly_plan_grounding.py`](../workmate-agent/tests/test_weekly_plan_grounding.py), [`M2.2-02 수동 의미 검수 결과`](evidence/M2/M2.2/runs/20260813-235246/result.md), LLM 평가 Case | 모든 확정 계획에 source_refs가 있고 실제 LLM 평가·수동 검수가 승인됨 | M2.3-01 | 완료 |

### 2.1.10 M2.3 보고서 생성 백로그 정의 및 구현 계획

M2.3은 M2.1의 결정론적 분류와 M2.2의 근거 있는 다음 주 계획을 입력으로 받아 `weekly_report` Result Envelope와 A2A Artifact를 생성한다. Task 상태 분류·source_refs·계획 kind는 코드가 소유하고, LLM은 요약 문장과 이미 검증된 계획 표현만 생성한다. 공개 Schema와 Artifact 계약은 변경하지 않는다.

#### 구현 전 확정 계약

- 입력은 승인된 `WeeklyReportResult` 후보와 사용자 `user_id`, `request_id`, 기간, `data_freshness`, `warnings`를 사용한다.
- 결과는 `WorkmateResultEnvelope.result.type=weekly_report`와 `WeeklyReportResult`를 사용하며 `schema_version`, `generated_at`, `data_freshness`, `warnings`를 포함한다.
- `completed`, `in_progress`, `delayed`, `unresolved_issues`, `source_refs`는 M2.1 결정론적 결과를 그대로 보존한다. LLM이 Task 상태·점수·source ID를 생성하거나 변경하지 않는다.
- `next_week_plans`는 M2.2에서 통과한 `PlanItem`만 사용한다. `planned`·`carry_over`·`suggestion` 외 kind와 입력에 없는 source ID는 차단한다.
- Artifact는 구조화 `DataPart(application/json)`와 UI용 `TextPart(text/markdown)`를 함께 제공한다. `mock`, `received` 등 Mock 전용 필드는 공개 Artifact에 넣지 않는다.
- Provider 실패·timeout·429·5xx는 정의된 부분 결과와 `warnings`를 반환한다. Schema 검증 실패는 완료 Artifact를 발행하지 않고 Task를 실패 처리한다.
- 보고서 생성은 장기 Task로 실행될 수 있으며 영속 Task Store와 기존 `task_id ↔ thread_id` 경계를 사용한다.

#### M2.3 백로그

| ID | 작업명 | 구현 경로 | 테스트 경로 | 완료 조건 | 관련 의사결정 | 다음 작업 | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M2.3-01 | 주간 보고 입력 조립·LLM 생성 Workflow | [`weekly_report.py`](../workmate-agent/app/workflows/weekly_report.py), [`weekly_classification.py`](../workmate-agent/app/workflows/weekly_classification.py) | [`test_weekly_report_generation.py`](../workmate-agent/tests/test_weekly_report_generation.py), [`M2.3-01 승인 결과`](evidence/M2/M2.3/runs/20260814-002128/result.md) | M2.1 분류와 M2.2 계획을 입력으로 받아 요약·계획 표현을 생성하고 원본 목록·source_refs를 보존 | [`docs/02-a2a-interface.md`](02-a2a-interface.md) §4.5, [`docs/07-technical-specification.md`](07-technical-specification.md) §5 | M2.3-02 | 완료 |
| M2.3-02 | Result Envelope·Artifact 변환·Schema 검증 | [`registry.py`](../workmate-agent/app/workflows/registry.py), [`weekly_report.py`](../workmate-agent/app/workflows/weekly_report.py), [`runtime.py`](../workmate-agent/app/a2a/runtime.py) | [`test_weekly_report_artifact.py`](../workmate-agent/tests/test_weekly_report_artifact.py), [`M2.3-02 승인 결과`](evidence/M2/M2.3/runs/20260814-003029/result.md) | `WeeklyReportResult`와 A2A Artifact의 DataPart·Markdown Part가 승인 Schema를 통과하고 Mock 필드가 없음 | [`docs/schemas/workmate-skill-schemas.schema.json`](schemas/workmate-skill-schemas.schema.json), [`docs/schemas/a2a-artifact.schema.json`](schemas/a2a-artifact.schema.json) | M2.3-03 | 완료 |
| M2.3-03 | Provider 부분 실패·재시도·경고 경계 | [`weekly_report.py`](../workmate-agent/app/workflows/weekly_report.py) | [`test_weekly_report_provider_failure.py`](../workmate-agent/tests/test_weekly_report_provider_failure.py), [`M2.3-03 승인 결과`](evidence/M2/M2.3/runs/20260814-065824/result.md) | Provider timeout·429·5xx 재시도 후 부분 결과와 warnings를 반환하고 원본 분류를 훼손하지 않음 | [`docs/05-ai-security-operations.md`](05-ai-security-operations.md) §3, [`docs/07-technical-specification.md`](07-technical-specification.md) §5.3 | M2.3-04 | 완료 |
| M2.3-04 | 통합·회귀 검수 | [`app/`](../workmate-agent/app/) | [`test_m2_3_integration.py`](../workmate-agent/tests/test_m2_3_integration.py), [`M2.3-04 승인 결과`](evidence/M2/M2.3/runs/20260814-070047/result.md) | 전체 보고서 경로·영속 Task·권한 범위·Schema·부분 실패 검사가 모두 PASS하고 실제 Workflow에서 고정 Mock을 사용하지 않음 | [`docs/12-implementation-verification-guide.md`](12-implementation-verification-guide.md) §7, [`docs/06-delivery-plan.md`](06-delivery-plan.md) §2.2 | M2.4-01 | 완료 |
