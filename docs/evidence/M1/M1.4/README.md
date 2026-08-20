status: 완료
latest_run_id: 20260813-215728
latest_run_status: PASS
latest_approved_run_id: 20260813-215728
approved_at: 2026-08-13 21:57 Asia/Seoul
reviewer: 자동 승인(검증 명령)

# M1.4 Task 제안 증빙

## 범위

- M1.4-01: 외부 동기화 후보의 사용자별 메모리 Hub·SSE 발행
- M1.4-02: 메일·Calendar 제안 승인·무시·Idempotency-Key·사용자 범위
- M1.4-03: 동일 원본 멱등성과 유사 Task 재확인

최신 실행: [`20260813-215728/result.md`](runs/20260813-215728/result.md)

제안은 DB에 저장하지 않고 프로세스 메모리와 SSE로만 전달한다. 승인 시 기존 Task Repository에만 저장하며, 실제 Gmail·Calendar OAuth 호출은 승인된 M1.2 Adapter 경계를 통해 상위 동기화 Workflow가 제공한다.
