status: 완료
latest_run_id: 20260814-081500
latest_run_status: PASS
latest_approved_run_id: 20260814-081500
approved_at: 2026-08-14T08:15:00+09:00
reviewer: 자동 승인(검증 명령)

# M3.1 회의 입력

회의 메타데이터 생성·조회와 multipart 녹음 입력의 MIME·크기·SHA-256 중복 검증을 구현한다. 원본 음성은 저장하지 않으며 R2 Object Key 연결은 M3.6에서 수행한다.

## 검수 규칙

- `tests/test_meeting_api.py`와 compileall, `git diff --check`가 모두 PASS여야 승인한다.
- 의존성 설치·프로세스 잠금 등으로 테스트가 실행되지 않으면 자동 승인하지 않고 재작업으로 중단한다.
