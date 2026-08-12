# M0.1-01 Docker 재검수 결과

## 1. 기본 정보

- 마일스톤: M0.1 A2A·Artifact 계약
- 백로그: M0.1-01 공식 A2A SDK HTTP+JSON 런타임 부트스트랩
- 담당자: Codex
- 검수자: 사용자
- 상태: 완료
- 실행일: 2026-08-12
- 실행 ID: `20260812-210001`
- 코드 버전: `workmate-agent` `0149b921b9c74139774f66c56a174d5b34c671f1`
- 입력 데이터 버전: 해당 없음

## 2. 최신 실행과 승인

- latest_run_id: `20260812-210001`
- latest_run_status: PASS (승인)
- latest_approved_run_id: `20260812-210001`
- approved_at: 2026-08-12 21:06:29 +09:00

## 3. 목표와 완료 기준

- 목표: Docker Desktop Linux engine에서 Workmate 이미지를 빌드하고 A2A 런타임을 정상 기동한다.
- 완료 기준: Compose 빌드·기동 성공, 컨테이너 `healthy`, liveness·readiness·Agent Card 응답 정상
- 백로그 범위: M0.1-01의 기존 Docker Compose 보류 항목 재검수
- 미완료·보류 백로그: 해당 없음

## 4. 구현 경로

- 구현 코드: `workmate-agent/Dockerfile`
- Schema 또는 Migration: 해당 없음
- UI 코드: 해당 없음

### 클릭 가능한 구현 경로

- [Dockerfile](../../../../../../workmate-agent/Dockerfile)
- [compose.yaml](../../../../../../workmate-agent/compose.yaml)

## 5. 테스트 파일 경로

- 단위 테스트: `workmate-agent/tests/test_runtime_boot.py`, `workmate-agent/tests/test_contract.py`
- 통합 테스트: `workmate-agent/compose.yaml` 기반 Docker Compose 기동 검증
- UI 테스트: 해당 없음
- Fixture/입력: `workmate-agent/.env`의 로컬 설정 사용, Secret 값은 기록하지 않음
- 기대 결과: 이미지 빌드 성공, 컨테이너 healthy, `/health/live`, `/health/ready`, Agent Card 정상 응답
- 모델 평가 Case: 해당 없음
- 모델 평가 결과: 해당 없음

### 클릭 가능한 테스트 경로

- [test_runtime_boot.py](../../../../../../workmate-agent/tests/test_runtime_boot.py)
- [test_contract.py](../../../../../../workmate-agent/tests/test_contract.py)
- [compose.yaml](../../../../../../workmate-agent/compose.yaml)

## 6. 실행 명령과 결과

```text
docker version
uv run --frozen python -m unittest discover -s tests -v
python -m compileall -q app tests
git diff --check
docker compose up --build -d
docker compose ps --format json
Invoke-RestMethod http://localhost:8001/health/live
Invoke-RestMethod http://localhost:8001/health/ready
Invoke-RestMethod http://localhost:8001/.well-known/agent-card.json
docker compose down
```

- Docker daemon: PASS (`desktop-linux`, Docker Engine 29.4.3)
- 단위·Contract Test: PASS (7개)
- Compile: PASS
- Docker 이미지 빌드·컨테이너 기동: PASS
- Compose 상태: `running`, `healthy`
- Health: `alive`, `ready`
- Agent Card: `Workmate AI`, `HTTP+JSON`, protocol `1.0`, streaming `true`
- 검증 환경 종료: PASS (검증 컨테이너·네트워크 제거)
- 실행 로그: 이 문서의 결과 요약
- API 응답 또는 Artifact: 공개 Health·Agent Card 응답 요약
- 화면 캡처: 해당 없음
- 함수 문서화: 이번 변경은 Docker 실행 명령 수정으로 해당 없음

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Docker daemon 연결 | PASS | 실행 ID `20260812-210001` |
| 잠금 파일 기반 이미지 빌드 | PASS | `workmate-agent/Dockerfile` |
| 컨테이너 기동·Health | PASS | 실행 ID `20260812-210001` |
| Agent Card HTTP+JSON 1.0·Streaming | PASS | 실행 ID `20260812-210001` |
| 기존 단위·Contract Test | PASS | `workmate-agent/tests/` |

## 8. 문제와 수정 이력

- 발견된 문제: 고정된 `uv==0.11.28`에서 `uv sync --system` 옵션을 지원하지 않아 이미지 빌드 실패
- 원인: Dockerfile이 현재 `uv sync` CLI에 존재하지 않는 옵션 사용
- 수정 내용: `--system`을 제거하고 `/app/.venv/bin`을 컨테이너 `PATH`에 연결
- 재검수 실행 ID: `20260812-210001`
- 참고: Compose가 과거의 종료된 `workmate-agent-workmate-1` 컨테이너를 orphan으로 경고했으나 이번 서비스의 빌드·기동·Health에는 영향 없음

## 9. 최종 판단

- 승인 여부: 승인
- 검수 의견: 기존 Docker daemon 미실행 차단이 해소됐고 Docker 재검수 항목이 모두 PASS하여 사용자가 M0.1-01 완료를 승인함
- 다음 조치: M0.1-02 검수 승인
