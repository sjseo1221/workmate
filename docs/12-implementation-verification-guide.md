# 구현·검증 가이드

[← 기술 상세 설계](07-technical-specification.md) · [목차](README.md)

이 문서는 평가와 통합 테스트에서 확정된 값을 실제 Workmate 구현에 적용하기 위한 실행 기준이다. 평가 원본과 전체 실행 이력은 각 평가 폴더에 보존하고, 이 문서에는 구현에 필요한 계약·기본 경로·검증 기준만 정리한다.

## 1. 문서와 결과의 관계

| 목적 | 기준 문서 |
| --- | --- |
| 개발 작업 절차·현재 상태 | [AGENTS.md](../AGENTS.md) · [HANDOFF.md](../HANDOFF.md) |
| 회의 업무 흐름 | [04-scenarios.md](04-scenarios.md) |
| 기술·API·DB 기준 | [07-technical-specification.md](07-technical-specification.md) |
| 개발 단계와 완료 기준 | [06-delivery-plan.md](06-delivery-plan.md) |
| Embedding 평가 방법 | [10-embedding-evaluation-plan.md](10-embedding-evaluation-plan.md) |
| LLM 평가 방법 | [11-llm-evaluation-plan.md](11-llm-evaluation-plan.md) |
| Embedding 실행 이력 | [embedding-evaluation/EVALUATION_HISTORY.md](../embedding-evaluation/EVALUATION_HISTORY.md) |
| STT 실행 이력 | [stt-evaluation/EVALUATION_HISTORY.md](../stt-evaluation/EVALUATION_HISTORY.md) |
| 녹음 통합 테스트 이력 | [meeting-recording-test/HISTORY.md](../meeting-recording-test/HISTORY.md) |

평가 결과 파일에 있는 Secret, 실제 Base URL, 원본 음성은 구현 문서나 Git에 복사하지 않는다.

마일스톤별 최종 검수 자료는 [06-delivery-plan.md의 증빙 저장 규칙](06-delivery-plan.md#22-전체-마일스톤-증빙-저장-규칙)에 따라 `docs/evidence/Mx/Mx.y/`에 저장한다. 평가 원본과 실행 이력은 각 평가 폴더에 그대로 보존하고, 증빙 폴더에는 요약·검증 결과·링크·화면 캡처만 둔다.

증빙 폴더는 하위 마일스톤 작업 시작 시 생성하고, 구현 중에는 실행 명령과 원본 결과 링크를 추가하며, 검수 완료 시 최종 결과와 검수자·완료일을 기록한다. 구현 전 항목은 빈 결과 파일을 미리 만들지 않으며, 기존 평가 결과가 있는 M0만 사후 요약할 수 있다.

반복 검수 결과는 [06-delivery-plan.md의 최신 승인 실행 규칙](06-delivery-plan.md#24-반복-검수와-최신-승인-실행-표시)에 따라 `runs/{run_id}/`에 누적한다. 각 증빙 폴더의 `README.md`에는 `latest_run_id`와 `latest_approved_run_id`를 별도로 기록하며, 최종 인수는 최신 승인 실행만 기준으로 삼는다.

검수 결과 문서는 [06-delivery-plan.md의 `result.md` 표준 양식](06-delivery-plan.md#25-resultmd-표준-양식)을 사용한다. 작업 유형에 해당하는 단위·통합·UI 테스트 파일, Fixture, 모델 평가 Case와 결과 경로를 기록하며, 관련 없는 항목은 `해당 없음`으로 표시한다.

## 2. 확정된 모델과 검색 구성

### 2.1 Embedding

| 항목 | 구현값 |
| --- | --- |
| 모델 | openai/text-embedding-3-small |
| Vector 차원 | 1536 |
| PostgreSQL 타입 | vector(1536) |
| 거리 | Cosine (vector_cosine_ops) |
| 기본 검색 | Dense + PostgreSQL Trigram RRF |
| 인덱스 | pgvector HNSW |
| 기본 Reranker | 사용하지 않음 |

운영 확정 근거는 실제 회의록 64 Chunk·60 Case 평가다.

- Hybrid Hit@1: 96.43%
- Hybrid Hit@3: 98.21%
- Hybrid Hit@5: 100%
- HNSW Recall@5: 100%
- Hybrid DB p95: 66.3ms
- Query Embedding p95: 893.1ms

구현 규칙:

1. Chunk 저장 시 1536차원 embedding을 생성하고 meeting_chunks.embedding에 저장한다.
2. Vector 비교는 Cosine 기준으로 통일한다.
3. Vector 후보와 Trigram 후보를 각각 생성한 뒤 RRF로 합친다.
4. HNSW는 후보 검색 인덱스로 사용하고 정확 검색 대비 Recall을 모니터링한다.
5. 검색 기본 경로에는 Reranker를 넣지 않는다. 필요하면 조건부 호출 후 실패·지연 시 RRF 결과로 돌아간다.
6. date_to는 미만(Exclusive)이다. 하루 조회는 다음 날짜를 date_to로 전달한다.
7. Cosine 0.45 단독 답변 가능성 판정은 정상 질문 오탐이 높아 운영 기본값으로 사용하지 않는다.

답변 가능성 판정은 검색 점수와 분리한다. 운영 Workflow는 `Dense + Trigram RRF Top-K → metadata·근거 검증 → 조건부 Reranker/groundedness → 답변 또는 insufficient_evidence` 순서를 사용한다. Reranker는 후보 Chunk ID 밖의 근거를 반환할 수 없고, 실패·Timeout이면 RRF 결과와 `warnings`를 반환한다. 단일 Cosine 임계값은 평가용 진단 지표로만 기록한다.

Reranker 재평가 결과는 Hit@1·3·5 94.64%, p95 1,406.7ms였고 일부 순위 악화가 있어 조건부 경로로 보류한다.

### 2.2 STT

| 항목 | 구현값 |
| --- | --- |
| 모델 | OpenAI gpt-4o-transcribe |
| 언어 | 한국어 ko |
| 파일 분석 입력 | 한국어 회의 녹음 파일 |
| Streaming 입력 | mono PCM16 24kHz, 200ms Chunk |
| Streaming API | WebSocket Realtime Transcription |
| 저장 결과 | timestamp가 포함된 최종 transcript |

평가 근거:

- gTTS 합성 한국어 20 Case: Provider 오류 0건, 핵심어 19/20(95%)
- Streaming Pilot 2 Case: Partial·Final 수신 성공, Provider 오류 0건
- 실제 회의 음성의 WER/CER, 화자 분리, 잡음·겹침 발화는 아직 평가하지 않았다.

따라서 MVP는 파일 분석과 실시간 임시 자막을 지원하되, 화자 분리와 실시간 품질 최적화는 후속 범위로 둔다.

## 3. 회의 녹음 구현 계약

### 3.1 입력 흐름

~~~text
회의 생성
→ upload 또는 realtime 입력 선택
→ realtime이면 Recording WebSocket 연결
→ 200ms 음성 Chunk 전송
→ ACK와 transcript.partial 표시
→ 녹음 종료
→ 최종 파일 STT
→ LLM 회의 분석
→ Action Item 검토
→ 승인된 항목만 Task 등록
~~~

아래 경로는 정식 운영 API가 아니라 내부 테스트 하네스가 사용하는 테스트 어댑터 경로다. 정식 운영 API 계약은 [A2A 인터페이스](02-a2a-interface.md)의 `/api/v1/...` 경로를 따른다. 테스트 어댑터는 운영 경로와 상태 전이·멱등성 규칙을 검증하기 위한 축약 경로이며, 운영 API에 배포하지 않는다.

~~~text
POST /meetings
WS   /meetings/{meeting_id}/recording?session_id={recording_session_id}
POST /meetings/{meeting_id}/recording/complete
POST /meetings/{meeting_id}/analysis
GET  /meetings/{meeting_id}/analysis
GET  /meetings/{meeting_id}/actions
POST /meetings/{meeting_id}/actions/{action_item_id}/review
POST /meetings/{meeting_id}/actions/{action_item_id}/register-task
~~~

테스트 어댑터의 경로 표기는 운영 경로와 다를 수 있다. 어댑터를 실행할 때는 정식 운영 경로와의 매핑을 확인하고, 상태·권한·멱등성 규칙은 동일하게 유지한다.

### 3.2 WebSocket 메시지

테스트 하네스는 JSON과 Base64를 사용한다.

~~~json
{
  "chunk_no": 0,
  "audio_base64": "...",
  "sample_rate": 16000,
  "format": "pcm16"
}
~~~

현재 테스트 하네스는 16kHz 원본 WAV Chunk를 전송한다. STT Streaming Provider Adapter가 이를 24kHz PCM16으로 변환해 Provider에 전달한다. 운영 브라우저 구현에서는 음성 Binary Frame과 Chunk 메타데이터를 분리할 수 있지만, 어떤 전송 형식을 사용해도 chunk_no는 순서 복구와 중복 판정에 사용한다.

서버 이벤트 순서는 다음을 보장한다.

~~~text
정상 Chunk → chunk_ack → transcript.partial
~~~

클라이언트는 ACK와 Partial을 이벤트 타입으로 분리해 처리해야 한다. ACK를 기다리는 동안 Partial 이벤트를 버퍼에 남겨 다음 ACK로 오인하면 안 된다.

### 3.3 오류와 멱등성

| 상황 | 계약 |
| --- | --- |
| 순번 건너뜀 | CHUNK_GAP, 기대 순번 반환 |
| 같은 Chunk 재전송 | duplicate=true ACK, 음성 중복 저장 금지 |
| 잘못된 Session | HTTP 404 |
| 분석 실패 | TASK_STATE_FAILED, retryable 오류 저장 |
| 분석 재시도 | 기존 Task·Artifact 문맥을 유지하고 TASK_STATE_WORKING으로 Resume |
| Action Item 재승인 | 기존 결과 반환, 중복 Task 생성 금지 |
| Task 재등록 | 기존 task_id 반환, idempotent=true |

### 3.4 Action Item과 근거

Action Item은 다음 필드를 유지한다.

~~~text
action_item_id
title
assignee_id
due_at
evidence_span.meeting_chunk_ids
evidence_span.start_ms/end_ms
evidence_text
approval_status
task_id
~~~

evidence_text는 LLM이 만든 문장을 그대로 신뢰하지 않고, 최종 transcript와 Chunk에서 서버가 다시 추출한다. 사용자는 근거 문장을 눌러 전체 회의록의 해당 구간으로 이동할 수 있어야 한다.

## 4. 상태·저장 구현

### 4.1 Task 상태

~~~text
TASK_STATE_WORKING
  → TASK_STATE_COMPLETED
  → TASK_STATE_FAILED
  → TASK_STATE_WORKING (retry/resume)
~~~

분석 Task에는 외부 A2A Task ID와 내부 LangGraph thread_id를 함께 저장한다. 재시도는 새 Task를 만들지 않고 기존 Task 문맥을 재개한다.

### 4.2 저장소 경계

테스트 하네스는 SQLite results/recording-test.db와 Docker named volume을 사용했다. 운영 구현에서는 다음으로 교체한다.

| 테스트 | 운영 |
| --- | --- |
| SQLite | PostgreSQL |
| 테스트 JSON payload | 정규화된 Meeting·Chunk·Artifact 테이블 |
| Docker volume | 운영 Object Storage와 PostgreSQL |
| Mock 분석 | STT·LLM Provider 및 LangGraph Workflow |

원본 음성은 DB에 직접 넣지 않고 Cloudflare R2의 Private 단일 버킷 `workmate`에 저장하며, DB에는 R2 Object Key·checksum·보존기한을 기록한다. Presigned URL은 단기 전송용으로만 사용하고 DB에 저장하지 않는다. 실시간 녹음은 종료 후 Chunk를 하나의 원본 파일로 병합해 업로드한다.

## 5. Docker와 로컬 검증

회의 녹음 하네스 실행:

~~~powershell
cd C:\dev\workmate\meeting-recording-test
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
docker compose up --build -d
docker compose ps
# recording-mock가 (healthy)가 된 뒤 실행
python client/test_recording.py --base-url http://127.0.0.1:8010 --audio ..\stt-evaluation\audio\pilot\meeting-001.wav
python client/test_errors.py --base-url http://127.0.0.1:8010 --audio ..\stt-evaluation\audio\pilot\meeting-001.wav
docker compose down
~~~

Embedding 검증:

~~~powershell
cd C:\dev\workmate\embedding-evaluation
python run_postgres_eval.py --corpus corpus/real_meeting_chunks.jsonl --cases cases/real_cases_60.jsonl
python run_reranker_eval.py --corpus corpus/real_meeting_chunks.jsonl --cases cases/real_cases_60.jsonl --search-result results/postgres-run-<timestamp>.jsonl --suite-name real_meeting
~~~

STT 검증:

~~~powershell
cd C:\dev\workmate\stt-evaluation
python run_eval.py --cases cases/pilot_cases.jsonl
python run_streaming_eval.py --cases cases/pilot_cases.jsonl --chunk-ms 200
~~~

실행 전 .env에 Provider Secret을 넣고, Secret은 결과 JSON·CSV·문서에 기록하지 않는다.

### 5.1 평가용 환경변수에서 운영 환경변수로 복사

평가 폴더의 변수명은 Provider별 평가 실행기에 맞춘 이름이고, Workmate 운영 코드는 공통 이름을 사용한다. 값 자체가 아니라 필요한 변수명과 Secret을 운영 환경에 옮긴다.

| 평가 폴더 | Workmate 운영 변수 | 비고 |
| --- | --- | --- |
| `llm-evaluation`의 `OPENAI_BASE_URL2` | `LLM_BASE_URL` | OpenAI 호환 LLM Base URL |
| `llm-evaluation`의 `OPENAI_API_KEY2` | `LLM_API_KEY` | Secret Store로 이동 |
| `llm-evaluation`의 `OPENAI_MODEL2` | `LLM_MODEL` | 평가 후 확정된 모델 ID |
| `embedding-evaluation`의 `EMBEDDING_BASE_URL` | `EMBEDDING_BASE_URL` | 그대로 사용 |
| `embedding-evaluation`의 `EMBEDDING_API_KEY` | `EMBEDDING_API_KEY` | Secret Store로 이동 |
| `embedding-evaluation`의 `EMBEDDING_MODEL` | `EMBEDDING_MODEL` | `openai/text-embedding-3-small` |
| `stt-evaluation`의 `OPENAI_STT_BASE_URL` | `STT_BASE_URL` | STT Provider Base URL |
| `stt-evaluation`의 `OPENAI_STT_API_KEY` | `STT_API_KEY` | Secret Store로 이동 |
| `stt-evaluation`의 `OPENAI_STT_MODEL` | `STT_MODEL` | `gpt-4o-transcribe` |
| `google-oauth-test`의 OAuth 설정 | `OAUTH_*`, `GOOGLE_*` | Client JSON·Token은 운영 Secret Store로 전환 |
| 팀 공용 R2 설정 | `R2_ENDPOINT`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_REGION` | 단일 Private 버킷 `workmate`; Access Key는 문서·Git에 기록하지 않음 |

PostgreSQL 연결 변수와 A2A Service Token은 운영 Compose 또는 Secret Store의 별도 계약을 따른다. 실제 값은 이 문서에 기록하지 않는다.

### 5.2 R2 발급 키를 Workmate 구현에 적용하는 절차

R2 연결 검증이 끝나면 `r2-storage-test/.env`에 입력한 값을 Workmate 실행 환경의 `.env` 또는 Docker Compose Secret으로 복사한다. 값 자체를 채팅·문서·Git에 복사하지 않고, 변수명만 다음처럼 동일하게 유지한다.

```text
r2-storage-test/.env                 Workmate .env / Secret
R2_ENDPOINT                    ->    R2_ENDPOINT
R2_ACCESS_KEY_ID               ->    R2_ACCESS_KEY_ID
R2_SECRET_ACCESS_KEY           ->    R2_SECRET_ACCESS_KEY
R2_BUCKET                      ->    R2_BUCKET
R2_REGION                      ->    R2_REGION
```

복사 후 Workmate 컨테이너에 해당 변수가 주입되는지 확인하고, `r2-storage-test/.env`는 계속 로컬 전용으로 보관한다. API Key는 브라우저나 UI 환경변수에 넣지 않으며, 키를 교체할 때는 R2 Token을 새로 발급하고 두 환경의 값을 함께 갱신한 뒤 기존 키를 폐기한다.

## 6. 구현 완료 체크리스트

- [ ] gpt-4o-transcribe 파일·Streaming Provider Adapter 구현
- [ ] 24kHz PCM16 변환과 200ms Chunk 경계 구현
- [ ] ACK·Partial 이벤트 분리 처리
- [ ] Gap·중복·재연결·잘못된 Session 처리
- [ ] 최종 transcript timestamp 저장
- [ ] Action Item 근거 구간 재추출
- [ ] 승인 후 Task 등록과 멱등성 보장
- [ ] 실패·재시도·LangGraph Checkpoint 복구
- [ ] vector(1536)와 Cosine HNSW Migration
- [ ] Trigram RRF 기본 검색 구현
- [ ] date_to Exclusive 규칙 적용
- [ ] Reranker 조건부 호출과 RRF fallback
- [ ] Health Check와 Docker Compose 검증
- [ ] 백엔드 준비 후 R2 Storage Adapter·Presigned URL API 구현
- [ ] 백엔드 준비 후 `Meeting.source_audio_uri` Object Key 저장과 R2 `HeadObject` 검증 연결
- [ ] R2 30일 Lifecycle 정책을 관리 권한으로 확인
- [ ] 실제 운영 DB·Object Storage·Orchestrator A2A 계약 테스트

## 7. 운영 전 남은 검증

현재 결과만으로 확정하지 않은 항목은 다음 마일스톤의 완료 조건으로 연결한다. 조건이 발생하지 않은 항목을 미리 실행하거나 완료로 표시하지 않는다.

| 검증 항목 | 담당 마일스톤 | 수행 시점·완료 조건 |
| --- | --- | --- |
| 공식 SDK·Adapter·Streaming·Task 재시작 복구 | M0.1-04 | Agent Card `Cache-Control`, 5개 Skill, 헤더·상태·오류 변환, `/message:stream` 첫 Task와 후속 상태·Artifact 순서, 조회·취소, 활성 Task `POST /a2a/tasks/{id}:subscribe`, Terminal Task Subscribe 오류, 비허용 `GET` Subscribe와 제외 Route `404/405` Contract Test 통과 |
| LLM 보류 후보 재평가 | M0.2-01 | 기본 모델의 할당량 소진·계약 종료·완료 기준 미달이 발생할 때 동일 Case로 재평가 |
| Google OAuth 테스트 사용자 | M0.2-04·05 | 기존 승인 계정 이력 검수; 새 계정 사용 시 OAuth 동의 화면의 테스트 사용자 등록 후 재검증 |
| 브라우저 MediaRecorder Binary Frame 종단 간 테스트 | M3.2 | 실제 브라우저 연결·ACK·Gap·중복·재연결 통과 |
| 실제 회의 음성 WER/CER·화자 분리·잡음·겹침 발화 | M3.3 | 실제 회의 평가 세트와 결과·제약을 증빙에 기록 |
| R2 30일 Lifecycle 실제 삭제 | M3.6 | Dashboard 또는 관리 권한으로 규칙과 만료 삭제를 확인 |
| 운영 동시 접속·비용·Provider rate limit | M5.2 | 목표 부하에서 제한·재시도·부분 실패 동작 측정 |
| PostgreSQL 운영 Migration·백업·복구 | M5.3 | Compose/운영형 환경에서 Migration과 복구 Drill 통과 |
| Docker Compose 실행 환경 | M5.3 | Linux Docker Engine 기동 후 Health·Migration·Smoke Test 통과 |
| Orchestrator 실제 A2A 호출과 장기 Task 재개 | M5.4 | 실제 Orchestrator에서 5개 Skill과 Terminal 상태까지 종단 간 검증 |

## 8. Google OAuth 검증 결과

2026-08-11 `google-oauth-test`에서 다음 항목을 실제 테스트 계정으로 확인했다.

- Gmail readonly·Calendar readonly OAuth 인증 성공
- Gmail Profile·Message·History 조회 성공
- Calendar Events 조회 성공
- Gmail Watch 등록 성공: historyId·expiration 반환
- Calendar Events Watch 등록 성공: resourceId·expiration 반환
- 결과 이력: [google-oauth-test/HISTORY.md](../google-oauth-test/HISTORY.md)

2026-08-13 사용자 로컬 검증에서 동일 Gmail URL이 `requests`에서는 HTTP 401을 반환하고 `httplib2`에서는 timeout이 발생했으며, IPv4 제한 시 `httplib2`도 HTTP 401을 반환했다. 테스트 하네스와 M1.2 Adapter의 Google API HTTP 전송은 `google-auth`의 `AuthorizedSession` 기반 REST 호출로 고정하고 `site-packages` 수정이나 전역 socket monkeypatch는 사용하지 않는다.

구현 시 Access Token·Refresh Token은 Secret Store 또는 암호화 저장소에 보관하고, Watch 응답의 식별자와 만료 시각만 저장한다. Gmail 알림은 전달된 historyId로 History API를 다시 조회하고, Calendar 알림은 저장한 channel/resource 식별자를 검증한 뒤 events.list 증분 조회를 수행한다.

실제 메일 수신·읽음 변경과 일정 변경의 Push 전달, Gmail History ID 만료 복구, Calendar syncToken 410 복구는 테스트 계정에서 수동 변경 이벤트를 발생시켜 추가 확인한다.

## 9. Cloudflare R2 저장소 검증 결과

`r2-storage-test`에서 실제 R2 단일 Private 버킷에 테스트 객체를 생성해 다음을 확인했다.

- Presigned PUT 업로드 성공
- `HeadObject` 조회 성공
- Presigned GET 다운로드 및 checksum 일치
- 테스트 객체 삭제 성공
- 파일 MIME `audio/wav`, 크기 26 bytes 확인

Lifecycle 조회는 제한형 R2 Token의 `AccessDenied`로 확인하지 못했다. 따라서 30일 삭제 정책은 Cloudflare Dashboard에서 확인하거나 Lifecycle 조회 권한이 있는 별도 관리 Token으로 검증해야 한다. 테스트 이력은 [r2-storage-test/HISTORY.md](../r2-storage-test/HISTORY.md)에 기록한다.
