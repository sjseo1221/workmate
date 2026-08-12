# M0.1 A2A·Artifact 계약 증빙

status: 검수 중
latest_run_id: 20260812-222254
latest_run_status: 부분 PASS (로컬 테스트 PASS, PostgreSQL·최종 Docker 재검증 보류)
latest_approved_run_id: 20260812-212244
approved_at: 2026-08-12 21:22:44 +09:00
reviewer: 자동 승인(검증 명령)

`latest_approved_run_id`는 구현 설명을 보강해 재검증한 M0.1-02 실행을 가리킨다. M0.1-01은 실행 `20260812-210001`로 승인됐다. M0.1-03은 로컬 SQLite 재시작·계약 검증은 통과했지만 Docker daemon 응답 지연으로 PostgreSQL 실제 연결·최종 Dockerfile 재검증이 남아 `검수 중`이다.

## 목표

공식 `a2a-sdk[http-server]==1.1.2`의 Agent Card·Message·Task·Artifact 타입과 Executor 런타임을 Workmate의 고정 A2A 1.0 HTTP+JSON 계약 경계에 연결한다.

## 구현 예정 범위

- 공식 SDK REST Handler·`AgentExecutor` 런타임과 정확한 버전 고정
- A2A 전송용 자체 Pydantic 모델을 공식 SDK 타입으로 교체
- 전송 계층과 실제 업무 Workflow의 실행 경계
- A2A Task·Message 멱등성·Artifact·`task_id ↔ thread_id` 최소 PostgreSQL Migration
- PostgreSQL Task Store와 LangGraph Checkpoint 연결, 재시작 복구·취소, 현재 Task 스냅샷 이후 신규 이벤트 Streaming
- Agent Card, 인증, Adapter, 5개 Skill, Streaming, Task 조회·취소·Subscribe Contract Test
- Mock 전용 필드 없는 정식 Result Envelope·Artifact Schema 검증

## 백로그

| ID | 범위 | 완료 판단 |
| --- | --- | --- |
| M0.1-01 | 공식 SDK HTTP+JSON 런타임 부트스트랩 | 버전 고정, 공식 Handler·Executor와 테스트용 결정론적 Executor로 Agent Card·허용 Route 부팅 |
| M0.1-02 | 공개 A2A 전송 타입 | 공개 경로에서 자체 전송 모델·Legacy Route 제거, SDK 타입 Contract Test와 승인 Schema 기반 신규 Smoke Test 통과 |
| M0.1-03 | Workflow·영속 Task 경계 | Registry·A2A 인프라 Migration·Artifact 변환·복구·취소·Subscribe 검증 |
| M0.1-04 | 통합 계약 검수 | 5개 Skill·Schema·인증·상태·오류·부분 실패, Streaming 순서, 활성 Task `POST /a2a/tasks/{id}:subscribe`, Terminal 오류, 비허용 `GET` Subscribe와 제외 Route 차단 전체 통과 |

## 현재 상태

M0.1-01에서 `workmate-agent`에 공식 SDK `DefaultRequestHandler`, `AgentExecutor`, Agent Card, Streaming·Subscribe를 포함한 HTTP+JSON 런타임 골격을 연결했다. M0.1-02에서는 승인 Schema 기반 Contract Test로 교체하고 Legacy `smoke_test.py`와 자체 전송 기준을 제거했으며 실행 `20260812-204500`으로 승인 완료했다. M0.1-03에서는 Registry, A2A 인프라 Migration, SQLite·PostgreSQL Task Store 경계, Message 멱등성, Artifact·Checkpoint 저장을 구현했다. 실제 Gmail·Calendar 업무 Workflow와 M1.1 업무 DB는 아직 연결하지 않았다.

M0.1-01 실행 결과:

- 런타임 부트스트랩: [`runs/20260812-112000/result.md`](runs/20260812-112000/result.md)
- 주석·Docstring 정책 보강: [`runs/20260812-203320/result.md`](runs/20260812-203320/result.md)
- 공개 전송 타입 Contract Test: [`runs/20260812-204500/result.md`](runs/20260812-204500/result.md)
- Docker 이미지·Health·Agent Card 재검수: [`runs/20260812-210001/result.md`](runs/20260812-210001/result.md)
- 구현 설명을 포함한 M0.1-02 재검수: [`runs/20260812-212244/result.md`](runs/20260812-212244/result.md)
- M0.1-03 Workflow·영속 Task 경계: [`runs/20260812-215216/result.md`](runs/20260812-215216/result.md)
- M0.1-03 PostgreSQL·최종 Docker 재검수 시도: [`runs/20260812-222254/result.md`](runs/20260812-222254/result.md)

M0.1은 A2A 런타임 복구에 필요한 최소 인프라 Migration만 완료한다. Task·Gmail·Calendar 업무 도메인 Migration과 Repository·샘플 데이터는 M1.1의 완료 범위다.
