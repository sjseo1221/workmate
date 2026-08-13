# M0.4-01 재검수 결과

## 기본 정보

- 마일스톤: M0.4 내부 검증 UI
- 백로그: M0.4-01 Skill·입력 UI
- 실행 ID: `20260813-155148`
- 코드 버전: `workmate-agent` `4460b15`
- 상태: 검수 중

## 문제와 수정

- 문제: 페이지 최초 로드 시 Token이 비어 있으면 Skill 목록 요청이 401로 실패하고, 이후 Token을 입력해도 목록을 다시 조회하지 않았다.
- 수정: Token 입력 이벤트와 실행 직전에 Skill 목록을 재조회한다. 목록 실패 시 select에 HTTP 상태를 표시하고, 빈 입력은 실행하지 않는다.

## 검증 명령과 결과

```text
.venv\Scripts\python.exe -m unittest tests/test_internal_chat_ui.py tests/test_internal_chat.py tests/test_persistence.py tests/test_contract.py
.venv\Scripts\python.exe -m compileall -q app
git diff --check
```

- 테스트: **PASS (24건)**
- Python 구문 검사: **PASS**
- `git diff --check`: **PASS**

## 구현 경로

- [내부 UI](../../../../../../workmate-agent/app/internal_chat_ui.py)
- [UI 테스트](../../../../../../workmate-agent/tests/test_internal_chat_ui.py)

## 최종 판단

- 자동 검증: PASS
- UI 육안 검수: 사용자 브라우저 재확인 필요
- 상태: `검수 중`
