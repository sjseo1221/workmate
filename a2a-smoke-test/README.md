# 분리형 A2A Smoke Test

> 이 폴더는 정식 Workmate 운영 계약이 아닌 분리형·레거시 통신 검증 하네스다. 이 하네스는 `/a2a/v1`, `SERVICE_TOKEN`, `PUBLIC_BASE_URL`, `WORKMATE_BASE_URL`을 사용한다. 정식 구현은 `http://workmate-agent:8001/a2a`, `WORKMATE_SERVICE_TOKEN`, 공식 Agent Card와 Workmate Schema를 기준으로 한다.

두 폴더는 서로 코드, Dockerfile, Compose Network를 공유하지 않는다. 각각 다른 PC에 복사해서 실행할 수 있다.

```text
a2a-smoke-test/
├─ workmate-agent/   # Workmate PC
└─ orchestrator/     # Orchestrator PC
```

## PC 1: Workmate 실행

```powershell
cd C:\dev\workmate\a2a-smoke-test\workmate-agent
$env:SERVICE_TOKEN="team-test-token"
$env:PUBLIC_BASE_URL="http://192.168.0.11:8001/a2a/v1"
docker compose up --build -d
```

Workmate PC의 실제 Wi-Fi IPv4 주소로 `192.168.0.11`을 교체한다.

## PC 2: Orchestrator 실행

```powershell
cd C:\dev\workmate\a2a-smoke-test\orchestrator
$env:SERVICE_TOKEN="team-test-token"
$env:WORKMATE_BASE_URL="http://192.168.0.11:8001/a2a/v1"
docker compose up --build -d
python smoke_test.py
```

두 PC의 `SERVICE_TOKEN`은 반드시 같아야 한다.

## 같은 PC에서 분리 실행

Workmate와 Orchestrator 폴더에서 각각 `docker compose up --build -d`를 실행한다. Orchestrator는 기본값 `host.docker.internal:8001`로 Workmate Host Port에 접근한다.

- Workmate Agent Card: <http://localhost:8001/.well-known/agent-card.json>
- Workmate Health: <http://localhost:8001/health>
- Orchestrator Swagger: <http://localhost:9000/docs>

각 폴더에서 별도로 종료한다.

```powershell
docker compose down
```

다른 PC에서 접속되지 않으면 Workmate PC의 개인 네트워크 방화벽에서 TCP 8001을 허용하고 공유기의 AP Isolation 설정을 확인한다.
