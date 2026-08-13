status: 검수 중
latest_run_id: 20260813-151936
latest_run_status: PASS (운영 OIDC 미실행)
latest_approved_run_id: 20260813-150133
approved_at: 2026-08-13 15:01 Asia/Seoul
reviewer: 자동 승인(검증 명령)

# M0.3 내부 챗봇 API

M0.3-01의 입력 경계와 M0.3-02의 공통 Workflow 호출 경계를 구현·검수한다.
M0.3-03의 장기 Task API까지 자동 승인되었고, M0.3-04의 인증·Schema·사용자 범위
구현은 로컬 검증을 통과했다. 운영 OIDC 실제 토큰 검증이 미실행되어 M0.3-04는
검수 중으로 유지한다.

- 최신 실행: [`20260813-151936/result.md`](runs/20260813-151936/result.md)
- 승인된 백로그: M0.3-01, M0.3-02, M0.3-03
- 검수 중 백로그: M0.3-04 인증·Schema·부분 실패
- 다음 착수 항목: OIDC JWT Contract Test 준비 (M0.3-04 재검수 조건)
- 운영 경로는 공유 Workflow 경계를 호출하며, 실제 Gmail·Calendar·업무 DB 결과는 후속 M1~M4에서 연결한다.
