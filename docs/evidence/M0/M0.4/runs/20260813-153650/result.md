# M0.4-01 검수 결과

## 1. 기본 정보

- 마일스톤: M0.4 내부 검증 UI
- 제목: Skill 선택·자연어/JSON 입력 화면
- 담당자: Codex
- 검수자: 미정
- 상태: 검수 중
- 실행일: 2026-08-13 15:36 Asia/Seoul
- 실행 ID: `20260813-153650`
- 코드 버전: `workmate-agent` `05f5948`
- 입력 데이터 버전: M0.3-04 승인 내부 챗봇 API 계약

## 2. 구현 요약

- `/internal/skill-chat` 최소 개발자 페이지를 추가했다.
- Skill 목록 선택, 자연어/JSON 입력 형식 선택, 입력 textarea, 실행 결과 영역을 제공한다.
- 페이지는 `WORKMATE_INTERNAL_CHAT_ENABLED=true`일 때만 노출한다.
- Bearer Token은 페이지에서 저장하지 않고 API 요청 헤더에만 사용한다.
- 기존 OIDC 보호 API와 `/api/v1/internal/skill-chat/messages`를 그대로 호출한다.

## 3. 구현 경로

- [UI Route](../../../../../../workmate-agent/app/internal_chat_ui.py)
- [FastAPI 등록](../../../../../../workmate-agent/app/main.py)
- [UI 테스트](../../../../../../workmate-agent/tests/test_internal_chat_ui.py)

## 4. 실행 명령과 결과

```text
$env:WORKMATE_INTERNAL_CHAT_ENABLED='true'
$env:WORKMATE_OIDC_ISSUER='https://issuer.test'
$env:WORKMATE_OIDC_AUDIENCE='workmate-internal'
$env:WORKMATE_OIDC_JWKS_URL='http://127.0.0.1:1/jwks.json'
.venv\Scripts\python.exe -m unittest tests/test_internal_chat_ui.py tests/test_internal_chat.py tests/test_persistence.py tests/test_contract.py
.venv\Scripts\python.exe -m compileall -q app
git diff --check
```

- 테스트: **PASS (24건)**
- Python 구문 검사: **PASS**
- `git diff --check`: **PASS**

## 5. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| UI 진입 경로 및 비활성 차단 | PASS | `tests/test_internal_chat_ui.py` |
| Skill 선택 컨트롤 | PASS | `tests/test_internal_chat_ui.py` |
| 자연어/JSON 입력 컨트롤 | PASS | `tests/test_internal_chat_ui.py` |
| 기존 OIDC API 호출 경로 사용 | PASS | `app/internal_chat_ui.py` |
| UI 육안 검수 | 미실행 | 사용자 브라우저 확인 필요 |

## 6. 최종 판단

- 승인 여부: **보류(검수 중)**
- 검수 의견: 자동 검증은 모두 PASS했지만 UI 육안 검수는 자동 승인 예외다.
- 다음 조치: 브라우저에서 `/internal/skill-chat` 화면의 레이아웃·입력·오류 표시를 확인한다. 승인 전에는 M0.4-02를 착수하지 않는다.
