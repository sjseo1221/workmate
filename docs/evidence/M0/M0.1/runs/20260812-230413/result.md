# M0.1-04 검수 결과

## 1. 기본 정보

- 마일스톤: M0.1
- 제목: 통합 A2A 계약 검수
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-12
- 실행 ID: `20260812-230413`
- 코드 버전: `workmate-agent@d00a858`
- 입력 데이터 버전: 승인 Schema·Contract Fixture

## 2. 최신 실행과 승인

- latest_run_id: `20260812-230413`
- latest_run_status: PASS
- latest_approved_run_id: `20260812-230413`
- approved_at: 2026-08-12 23:04 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: Agent Card·5개 Skill·Artifact·인증·오류·Streaming·Subscribe·Route allowlist의 통합 A2A 계약을 검증한다.
- 완료 기준: 승인 Schema 검증, 5개 Skill 공개 호출, Streaming 이벤트 순서, 활성 Task Snapshot Subscribe, Terminal Subscribe 오류, 비허용 GET Subscribe·기타 Route 차단, Cache-Control과 Docker Health를 통과한다.
- 백로그 범위: `M0.1-04`
- 미완료·보류 백로그: 없음. 실제 업무 Provider Workflow 연결은 M1 이후 범위다.

## 4. 구현 경로

- 런타임·인증: [`app/main.py`](../../../../../../workmate-agent/app/main.py), [`app/a2a/runtime.py`](../../../../../../workmate-agent/app/a2a/runtime.py)
- 통합 Contract Test: [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py), [`tests/test_runtime_boot.py`](../../../../../../workmate-agent/tests/test_runtime_boot.py)
- 승인 Schema: [`a2a-artifact.schema.json`](../../../../../../docs/schemas/a2a-artifact.schema.json), [`workmate-skill-schemas.schema.json`](../../../../../../docs/schemas/workmate-skill-schemas.schema.json)
- 실행 설정: [`README.md`](../../../../../../workmate-agent/README.md)

## 5. 구현 요약

- 공식 SDK REST Route allowlist에서 `POST /a2a/tasks/{id}:subscribe`만 공개하고 SDK 호환용 GET Subscribe는 제거했다.
- Agent Card에 `Cache-Control: public, max-age=3600`을 적용했다.
- 5개 Skill 입력을 승인 Schema로 검증하고 공개 `/a2a/message:send` 호출 및 Artifact Schema를 검증한다.
- `/message:stream`의 첫 Task·상태·Artifact·Terminal 상태 이벤트 순서를 검증한다.
- 활성 Task Subscribe가 현재 Task Snapshot을 먼저 전달하는지 SDK Handler 경계에서 확인한다.
- Terminal Task의 POST Subscribe 오류와 비허용 GET Subscribe `404/405`를 검증한다.
- Windows에서 PostgreSQL async 연결이 가능하도록 Selector 이벤트 루프 정책을 앱 초기화에 반영했다.

## 6. 실행 명령과 결과

```text
$env:DATABASE_URL='(격리 테스트 DB; 값은 증빙에 기록하지 않음)'
uv lock --check --cache-dir ..\\.uv-cache
uv sync --frozen --cache-dir ..\\.uv-cache
uv run --frozen --cache-dir ..\\.uv-cache python -m unittest discover -s tests -v
uv run --frozen --cache-dir ..\\.uv-cache python -m compileall -q app tests
git diff --check
docker compose build --progress plain
docker compose up -d
```

- 전체 테스트: 19개 PASS
- PostgreSQL 통합 테스트: 실제 격리 PostgreSQL 16.14 연결·Migration·Task Snapshot·Message 멱등성·삭제 PASS
- Lock·sync·compile·diff: PASS
- Docker build: PASS
- Docker 컨테이너: `healthy`
- 최종 Docker Agent Card: HTTP 200, `Cache-Control: public, max-age=3600`
- 최종 Docker Health: `/health/live` HTTP 200, `/health/ready` HTTP 200
- 최종 Docker 통합 HTTP: Message 완료, Streaming Task·Artifact·완료 이벤트, GET Subscribe 404, Terminal POST Subscribe 400, Agent Card 5 Skill 확인
- 테스트용 PostgreSQL 컨테이너와 Compose 컨테이너는 실행 후 제거했다.

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Agent Card·HTTP+JSON 1.0·5 Skill·Streaming | PASS | [`tests/test_runtime_boot.py`](../../../../../../workmate-agent/tests/test_runtime_boot.py), [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py) |
| 승인 Skill·Artifact Schema | PASS | [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py), [`docs/schemas/`](../../../../../../docs/schemas) |
| 인증·A2A-Version 오류 | PASS | [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py) |
| Streaming 이벤트 순서 | PASS | [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py) |
| 활성 Task POST Subscribe Snapshot | PASS | [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py) |
| Terminal Subscribe 오류·비허용 GET Route | PASS | [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py) |
| Route allowlist·Legacy/Push/Task 목록 차단 | PASS | [`tests/test_runtime_boot.py`](../../../../../../workmate-agent/tests/test_runtime_boot.py) |
| Docker Health·Agent Card·Cache-Control | PASS | 실행 ID `20260812-230413` |

## 8. 문제와 수정 이력

- 발견된 문제: 구현·README·테스트가 GET Subscribe를 허용했지만 승인 문서는 POST만 정식 계약으로 정의했다.
- 원인: SDK가 제공하는 GET 호환 Route를 MVP 공개 목록에 잘못 포함했다.
- 수정 내용: GET Route 제거, README·Runtime Test·Contract Test를 POST 전용 계약으로 통일했다. Agent Card Cache-Control과 Windows PostgreSQL 이벤트 루프도 보강했다.
- 재검수 실행 ID: `20260812-230413`

## 9. 최종 판단

- 승인 여부: 자동 승인(검증 명령)
- 검수 의견: M0.1-04 통합 A2A 계약과 최종 Docker 검증을 통과했다. 운영 업무 Workflow Mock을 추가한 것이 아니라 전송·검증 경계만 확인했다.
- 다음 조치: M0.2 모델·OAuth 확정 또는 M1 업무 기능 구현 계획에 따라 다음 백로그를 착수한다.
