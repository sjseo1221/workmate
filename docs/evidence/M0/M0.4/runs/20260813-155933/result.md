# M0.4-01 Mock 응답 구분 재검수

- 실행 ID: `20260813-155933`
- 코드 버전: `workmate-agent` `b20e2fb`
- 상태: 검수 중

## 변경 내용

- `WorkflowResult.mock` 플래그를 추가했다.
- 현재 runtime bootstrap Workflow는 `mock=true`를 반환한다.
- 내부 챗봇 Artifact에 `mock: true`, `business_result: false`를 표시한다.
- 공개 A2A Artifact Schema와 전송 구조는 변경하지 않았다.
- Mock 응답은 실행 가능하지만 실제 업무 완료나 마일스톤 승인 증빙으로 인정하지 않는다.

## 검증

```text
.venv\Scripts\python.exe -m unittest tests/test_internal_chat_ui.py tests/test_internal_chat.py tests/test_persistence.py tests/test_contract.py
.venv\Scripts\python.exe -m compileall -q app
git diff --check
```

- 테스트: **PASS (24건)**
- 구문 검사: **PASS**
- `git diff --check`: **PASS**

## 판정

- Mock 구분 계약: PASS
- 실제 업무 Workflow 연결: 미완료
- M0.4-01 UI 육안 검수: 사용자 확인 필요
- 상태: `검수 중`
