# M5.1 Docker Compose 재검수 결과

## 결과

- Docker Engine: PASS
- Workmate 전용 Compose 이미지 빌드: PASS
- Workmate healthcheck: PASS
- Main Agent health: PASS
- Orchestrator Task 호출: FAIL
- 실패 원인: 공식 Agent Card의 `name`이 `Workmate AI`인데 담당 Orchestrator가 이를 registry 키로 사용해 `KeyError('Workmate AI')` 발생
- 호환 어댑터는 Compose에 포함하지 않은 별도 프로세스이므로 이번 Compose는 공식 Workmate 직접 연결 상태였다.
- 검수 컨테이너와 네트워크는 정리했다.

## 판단

Compose 기동만 PASS이고 종단 간 Task 호출이 FAIL이므로 M5.1 자동 승인하지 않는다. 어댑터 서비스를 Compose에 포함하거나 담당 Orchestrator가 registry 키와 Agent Card 표시 이름을 분리해야 한다.
