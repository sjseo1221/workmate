# M5.1 Workmate A2A 호환성 클라이언트 착수 결과

## 기본 정보

- 실행 ID: `20260814-200000`
- 상태: 진행
- 구현: [`m51_a2a_compatibility.py`](../../../../../workmate-agent/tools/m51_a2a_compatibility.py)

## 구현 내용

- Agent Card를 Origin의 `/.well-known/agent-card.json`에서 실제 조회한다.
- SDK `Message`를 protobuf JSON으로 직렬화해 `/a2a/message:send`를 호출한다.
- 5개 Skill의 completed Task·Artifact를 확인한다.
- 승인된 `a2a-artifact.schema.json`으로 응답 Artifact를 검증한다.
- `runtime_bootstrap` 또는 `mock=true` Artifact가 반환되면 실패시킨다.
- Token 값은 출력하거나 증빙에 저장하지 않는다.

## 정적 검증

```text
\.venv\Scripts\python.exe -m compileall -q tools/m51_a2a_compatibility.py  PASS
git diff --check                                                       PASS
```

## 실제 실행 상태

실행 가능한 운영 Orchestrator가 없어 이 실행에서는 Workmate Agent 단독 호환성 클라이언트를 추가했다. Agent가 실행 중이고 `WORKMATE_A2A_BASE_URL`·`WORKMATE_SERVICE_TOKEN`이 설정되면 명령을 실행할 수 있다. 실제 Orchestrator 종단 간 검수는 별도 증빙으로 남긴다.

## 판정

클라이언트 구현은 완료했지만 실제 HTTP 실행 결과가 없어 M5.1을 완료 승인하지 않는다.
