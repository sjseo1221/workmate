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
| M0  | 계약·검증 기반   | A2A·모델·OAuth 계약과 내부 Skill 검증 챗봇 확보          | Phase 0    | 없음       | 구현 대기 |
| M1  | 데이터·우선순위  | Task, Gmail, Calendar를 통합하고 Top 3를 결정적으로 계산 | Phase 1    | M0         | 대기      |
| M2  | 브리핑·주간 보고 | 일일 브리핑과 근거 기반 주간 보고서 제공                 | Phase 2    | M1         | 대기      |
| M3  | 회의 분석        | 파일·실시간 녹음에서 STT·Action Item·Task 승인까지 연결  | Phase 3    | M0, M1     | 대기      |
| M4  | 회의 검색        | Embedding·Trigram RRF·HNSW와 출처 응답 완성              | Phase 4    | M3         | 대기      |
| M5  | 통합·시연        | Orchestrator·UI·Docker Compose 종단 간 인수 테스트       | Phase 1~4  | M2, M3, M4 | 대기      |

구현 상태는 `대기 → 진행 → 검수 중 → 완료`로 관리한다. 평가 결과, 테스트 로그, 화면 캡처 또는 API 응답은 해당 마일스톤의 증빙으로 연결한다.

상위 마일스톤의 선행 조건은 **진입 게이트**다. 하위 마일스톤 표의 선행 항목은 가장 가까운 기술 의존성만 표시하므로, 상위 진입 게이트를 완화하지 않는다. 예를 들어 M1.1의 직접 기술 선행은 M0.1이지만 M1 구현 상태를 `진행`으로 바꾸려면 M0 전체가 완료되어야 한다. 선행 마일스톤 완료 전에는 후속 백로그의 분석·분해만 허용하고 구현·검수 실행은 시작하지 않는다.

### 2.1 하위 마일스톤 추적표

담당자와 완료 예정일은 팀 작업 시작 시 채운다. 하위 마일스톤은 하나의 담당 단위와 하나의 검수 결과를 갖도록 유지한다.

| ID   | 하위 목표         | 주요 산출물                                                                 | 선행                         | 담당 | 완료 예정일 | 완료 기준·증빙                                                             | 상태 | 다음 착수 항목           |
| ---- | ----------------- | --------------------------------------------------------------------------- | ---------------------------- | ---- | ----------- | -------------------------------------------------------------------------- | ---- | ------------------------ |
| M0.1 | A2A·Artifact 계약 | Agent Card, Message/Task/Artifact Schema·A2A 인프라 Task Store              | 없음                         | 미정 | 미정        | SDK REST Route·AgentExecutor·Contract Test·Streaming·재시작 복구 검증 결과 | 진행 | M0.1-03 Workflow·영속 Task 경계 |
| M0.2 | 모델·OAuth 확정   | LLM·Embedding·STT·OAuth 설정과 평가 이력                                    | 없음                         | 미정 | 미정        | 기존 평가 승인·OAuth HISTORY·미검증 위험 기록                              | 대기 | M0.2-01 LLM 평가 승인    |
| M0.3 | 내부 챗봇 API     | Skill 목록·메시지·장기 Task 조회 API                                        | M0.1                         | 미정 | 미정        | 5개 Skill·인증·장기 Task·부분 실패 API 검증                                | 대기 | M0.3-01 입력 API         |
| M0.4 | 내부 챗봇 UI      | `workmate-agent` 최소 개발자 페이지의 Skill 선택·자연어/JSON 입력·결과 화면 | M0.3                         | 미정 | 미정        | 5개 Skill·Artifact·상태·오류 화면 검수                                     | 대기 | M0.4-01 입력 UI          |
| M1.1 | 업무 DB 기반      | Task·Gmail·Calendar PostgreSQL Migration·Repository·샘플 데이터             | M0.1                         | 미정 | 미정        | 업무 Migration·Repository 테스트                                           | 대기 | 백로그 정의 필요         |
| M1.2 | 외부 소스 연동    | Gmail·Calendar Adapter·정규화·동기화 Cursor                                 | M1.1                         | 미정 | 미정        | Gmail/Calendar 테스트 결과                                                 | 대기 | 백로그 정의 필요         |
| M1.3 | Task 관리         | 등록·조회·수정·Soft Delete API/UI                                           | M1.1                         | 미정 | 미정        | CRUD·중복·삭제 테스트                                                      | 대기 | 백로그 정의 필요         |
| M1.4 | Task 제안         | 메일·일정 SSE 제안·승인·무시·중복 검증                                      | M1.2, M1.3                   | 미정 | 미정        | 승인·중복 방지 테스트                                                      | 대기 | 백로그 정의 필요         |
| M1.5 | 우선순위·브리핑   | 점수 계산·Top 3·오늘 브리핑                                                 | M1.2, M1.3                   | 미정 | 미정        | 결정성·Top 3 테스트                                                        | 대기 | 백로그 정의 필요         |
| M2.1 | 주간 데이터 분류  | 완료·진행·지연·이슈 집계                                                    | M1.1, M1.2                   | 미정 | 미정        | 분류 결과와 source ID                                                      | 대기 | 백로그 정의 필요         |
| M2.2 | 계획·근거 추출    | 다음 주 계획과 제안/확정 구분                                               | M2.1                         | 미정 | 미정        | 근거 없는 계획 차단 테스트                                                 | 대기 | 백로그 정의 필요         |
| M2.3 | 보고서 생성       | LLM 보고서·Schema 검증·Artifact                                             | M2.2                         | 미정 | 미정        | 주간 보고 Schema 테스트                                                    | 대기 | 백로그 정의 필요         |
| M2.4 | 보고서 UI         | 기간 선택·섹션 표시·Markdown 복사                                           | M2.3                         | 미정 | 미정        | UI 검수 화면                                                               | 대기 | 백로그 정의 필요         |
| M3.1 | 회의 입력         | 회의 생성·파일 업로드·메타데이터                                            | M1.1                         | 미정 | 미정        | MIME·크기·중복 테스트                                                      | 대기 | 백로그 정의 필요         |
| M3.2 | 실시간 녹음       | RecordingSession·WebSocket·Chunk 재연결                                     | M3.1                         | 미정 | 미정        | ACK·Gap·중복·재연결 테스트                                                 | 대기 | 백로그 정의 필요         |
| M3.3 | STT·Transcript    | 임시/최종 STT·timestamp 원문 저장                                           | M3.1, M3.2                   | 미정 | 미정        | STT 평가·Transcript 검증                                                   | 대기 | 백로그 정의 필요         |
| M3.4 | 회의 분석         | 통합 요약·Action Item·근거 구간                                             | M3.3                         | 미정 | 미정        | Action Item Schema·근거 테스트                                             | 대기 | 백로그 정의 필요         |
| M3.5 | 승인·Task 등록    | Action Item 검토·승인·멱등 Task 생성                                        | M3.4, M1.3                   | 미정 | 미정        | 동일 Action Item 중복 승인 테스트                                          | 대기 | 백로그 정의 필요         |
| M3.6 | R2 연동           | Storage Adapter·Presigned URL·Object Key                                    | 백엔드 준비 후 M3.1          | 미정 | 미정        | PUT/HEAD/GET/checksum/Lifecycle                                            | 대기 | 백로그 정의 필요         |
| M4.1 | 검색 데이터       | MeetingChunk·Embedding 저장·재임베딩                                        | M3.3                         | 미정 | 미정        | `vector(1536)` Migration                                                   | 대기 | 백로그 정의 필요         |
| M4.2 | Trigram 검색      | pg_trgm Keyword 검색·metadata 필터                                          | M4.1                         | 미정 | 미정        | Keyword 검색 테스트                                                        | 대기 | 백로그 정의 필요         |
| M4.3 | Hybrid 검색       | Dense·Trigram RRF·HNSW                                                      | M4.2                         | 미정 | 미정        | Recall·Index Scan·지연 측정                                                | 대기 | 백로그 정의 필요         |
| M4.4 | 답변·출처         | 근거 기반 답변·출처·근거 부족 처리                                          | M4.3                         | 미정 | 미정        | 출처 누락·환각 검증                                                        | 대기 | 백로그 정의 필요         |
| M4.5 | 검색 평가         | 실제 64 Chunk·60 Case 평가                                                  | M4.4                         | 미정 | 미정        | Hybrid Hit@3 기준 충족                                                     | 대기 | 백로그 정의 필요         |
| M5.1 | A2A 통합          | Orchestrator Agent Card·5개 Skill 호출                                      | M0.3, M1.5, M2.3, M3.5, M4.4 | 미정 | 미정        | A2A 계약 테스트                                                            | 대기 | 백로그 정의 필요         |
| M5.2 | 운영 공통 기능    | 인증·권한·오류·재시도·로그·Health                                           | M5.1                         | 미정 | 미정        | 401·부분 실패·재시도 테스트                                                | 대기 | 백로그 정의 필요         |
| M5.3 | Compose 통합      | 서비스 환경변수·Network·DB·시연 데이터                                      | M5.2                         | 미정 | 미정        | Docker Compose smoke test                                                  | 대기 | 백로그 정의 필요         |
| M5.4 | 시나리오 시연     | 8개 시나리오 종단 간 실행                                                   | M5.3                         | 미정 | 미정        | 시나리오별 결과 캡처                                                       | 대기 | 백로그 정의 필요         |
| M5.5 | 최종 인수         | 문서·결과·보류 항목·인수 보고                                               | M5.4                         | 미정 | 미정        | 팀 최종 승인                                                               | 대기 | 백로그 정의 필요         |

M0.1 구현은 다음 네 백로그를 순서대로 검수한다. M0.1-01은 실행 `20260812-210001`, M0.1-02는 실행 `20260812-204500`으로 승인 완료됐다.

| ID      | 작업명                         | 구현 경로                                                                                          | 테스트 경로                                                             | 완료 조건                                                                                                                                                                                                                                                   | 관련 의사결정                                                              | 다음 작업      | 상태 |
| ------- | ------------------------------ | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------- | ---- |
| M0.1-01 | 공식 A2A SDK 런타임 부트스트랩 | `workmate-agent/app/main.py`, `app/a2a/runtime.py`, `pyproject.toml`, `uv.lock`, Dockerfile·README | SDK 부팅·Agent Card·허용 Route Smoke Test                               | `a2a-sdk[http-server]==1.1.2`를 고정하고 `pyproject.toml`·`uv.lock`을 단일 의존성 원장으로 사용하며 공식 REST Handler·`AgentExecutor`와 테스트용 결정론적 Executor로 Agent Card와 허용 Route가 부팅됨. 이 백로그는 공개 전송 타입 전환 완료를 주장하지 않음 | `docs/02-a2a-interface.md` 5.1, `docs/07-technical-specification.md` 2.1·4 | M0.1-02        | 완료 |
| M0.1-02 | 공개 A2A 전송 타입 전환        | `workmate-agent/app/a2a/runtime.py`, Legacy `app.py`·`smoke_test.py`                               | Message·Task·Artifact Contract Test                                     | 공개 `/a2a` 경로에서 자체 Pydantic 전송 모델과 Legacy Route를 제거하고 공식 SDK 타입만 사용하며, Legacy Smoke Test를 승인 Schema 기반 Contract Test로 교체                                                                                                  | `docs/07-technical-specification.md` 7.1                                   | M0.1-03        | 완료 |
| M0.1-03 | Workflow·Task 실행 경계        | `workmate-agent/app/workflows/registry.py`, `app/a2a/runtime.py`, `migrations/`                    | Registry·Artifact 변환·Task 복구·취소·Subscribe·Migration 테스트        | Executor는 Workflow 선택만 담당하고 M0.1 A2A 인프라 Migration으로 장기 Task·Message 멱등성·Artifact·Checkpoint를 영속 저장해 재시작 후 복구. Subscribe는 현재 Task 스냅샷 뒤에 연결 이후 신규 이벤트만 전송                                                 | `docs/02-a2a-interface.md` 6, `docs/07-technical-specification.md` 6·7·8.3 | M0.1-04        | 대기 |
| M0.1-04 | 통합 A2A 계약 검수             | `workmate-agent/tests/`                                                                            | Agent Card·5개 Skill·Artifact·인증·오류·Adapter·Streaming Contract Test | `Cache-Control`과 승인 Schema 검증, `/message:stream` 첫 Task 및 후속 상태·Artifact 순서, 활성 Task `POST` Subscribe, Terminal Task Subscribe 오류, 비허용 `GET` Subscribe와 기타 Route `404/405`, 조회·취소·부분 실패 통과                                 | `docs/02-a2a-interface.md` 4.5·5.1·6                                       | M0.1 통합 검수 | 대기 |

M0.2는 기존 평가를 무조건 다시 실행하지 않는다. **설계 확정**은 모델·Scope가 선택된 상태이고, **검수 완료**는 평가 원본·버전·제약·미검증 위험을 M0.2 증빙에서 승인한 상태다. 합성 STT 평가는 M0.2에서 승인하되 실제 회의 음성 평가는 M3.3 검수 조건으로 넘긴다.

M0.1의 PostgreSQL 범위는 A2A Task·Message 멱등성·Artifact·`task_id ↔ thread_id`·Checkpoint 복구에 필요한 인프라 Migration으로 제한한다. 공개 이벤트 전체 이력과 재생 Cursor는 MVP에서 저장하지 않고 Subscribe 연결 시 현재 Task 스냅샷 뒤에 신규 이벤트만 전송한다. M1.1은 Task·Gmail·Calendar 업무 데이터와 Repository·샘플 데이터를 추가하며 M0.1 Migration을 다시 만들거나 덮어쓰지 않는다.

| ID      | 작업명              | 평가·검증 원본                                                        | 완료 조건                                                           | 관련 의사결정                            | 다음 작업      | 상태 |
| ------- | ------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------- | -------------- | ---- |
| M0.2-01 | LLM 평가 승인       | `llm-evaluation/`, `docs/11-llm-evaluation-plan.md`                   | 기본 모델·Schema 평가 이력 승인, 할당량 소진 시 재평가 Trigger 기록 | `docs/07-technical-specification.md` 9.1 | M0.2-02        | 대기 |
| M0.2-02 | Embedding 평가 승인 | `embedding-evaluation/`, `docs/10-embedding-evaluation-plan.md`       | 모델·1536차원·Hybrid 지표·HNSW 결과 승인                            | `docs/06-delivery-plan.md` 5.1           | M0.2-03        | 대기 |
| M0.2-03 | STT 평가 승인       | `stt-evaluation/`, `docs/12-implementation-verification-guide.md` 2.2 | 합성 평가 결과 승인, 실제 회의 음성 미평가를 M3.3 위험으로 연결     | `docs/07-technical-specification.md` 9.3 | M0.2-04        | 대기 |
| M0.2-04 | Gmail OAuth 승인    | `google-oauth-test/`                                                  | readonly Scope·Profile/Message/History·Watch 이력 승인              | `docs/07-technical-specification.md` 10  | M0.2-05        | 대기 |
| M0.2-05 | Calendar OAuth 승인 | `google-oauth-test/`                                                  | readonly Scope·Events/Watch 이력 승인, 테스트 사용자 차단 여부 기록 | `docs/07-technical-specification.md` 10  | M0.2 통합 검수 | 대기 |

M0.3과 M0.4는 다음 최소 백로그만 미리 고정한다. 상세 구현 경로와 실행 명령은 해당 백로그 착수 시 실제 저장소 구조를 확인해 채운다.

| ID      | 작업명                | 완료 조건                                               | 다음 작업      | 상태 |
| ------- | --------------------- | ------------------------------------------------------- | -------------- | ---- |
| M0.3-01 | Skill·입력 API        | 5개 Skill 목록과 자연어/JSON 입력 검증                  | M0.3-02        | 대기 |
| M0.3-02 | 공통 Workflow 호출    | A2A와 같은 Workflow·Repository·Domain 경계 사용         | M0.3-03        | 대기 |
| M0.3-03 | 장기 Task API         | Task 조회·Polling·취소와 Terminal 상태 검증             | M0.3-04        | 대기 |
| M0.3-04 | 인증·Schema·부분 실패 | Session/OIDC, `user_id`, 승인 Artifact, `warnings` 검증 | M0.3 통합 검수 | 대기 |
| M0.4-01 | Skill·입력 UI         | 5개 Skill 선택과 자연어/JSON 입력                       | M0.4-02        | 대기 |
| M0.4-02 | 결과·상태 UI          | Artifact, 최신성, 경고, 오류, 장기 Task 상태 표시       | M0.4-03        | 대기 |
| M0.4-03 | UI 통합 검수          | 5개 Skill 화면, Polling·취소·권한 차단 검수             | M0.4 통합 검수 | 대기 |

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
- 실행 결과에 정의된 검증 명령이 모두 PASS이고 미실행·수동 검수·차단 항목이 없으면 별도 승인 질문 없이 `reviewer: 자동 승인(검증 명령)`으로 묵시 승인한다. `latest_approved_run_id`와 `approved_at`을 기록하고 이 문서의 백로그 상태 및 `HANDOFF.md`를 같은 작업에서 `완료`로 갱신한다.
- 공개 A2A Schema·데이터 모델 변경, 외부 OAuth·실제 Provider 검증, UI 육안 검수, 모델 평가처럼 사람의 판단이나 별도 권한이 필요한 항목은 묵시 승인 대상에서 제외한다. 검증 명령을 하나라도 실행하지 않았거나 결과에 경고·보류·미해소 차단이 있으면 `검수 중` 또는 `재작업`을 유지한다.
- 백로그의 묵시 승인은 하위 마일스톤 전체 승인을 뜻하지 않는다. 모든 백로그와 하위 마일스톤 통합 완료 기준을 충족한 뒤에만 하위 마일스톤을 `완료`로 표시한다.
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

## 4. 구현 경로

- 구현 코드:
- Schema 또는 Migration: (해당 작업만)
- UI 코드: (UI 작업만)

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

권장 Git 구조는 `C:\dev\workmate`를 루트 문서·증빙·평가 자료를 추적하는 Superproject로 사용하고 기존 `workmate-agent` 저장소만 Submodule로 등록해 이력을 보존하는 방식으로 확정한다. 폐기된 `workmate-ui-demo`는 루트 `.gitignore`로 제외하고 Submodule·구현·검수 범위에 포함하지 않는다. 구현 착수 전 Superproject 구성과 기준 Commit을 만들고 `workmate-agent` Submodule Commit을 `HANDOFF.md`에 기록한다. 기존 하위 저장소를 병합하거나 이력을 다시 만들지 않으며, 실제 Superproject 구성이 끝나기 전까지는 구현 착수 차단 사항으로 유지한다.

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
