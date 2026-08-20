status: 완료
latest_run_id: 20260814-171500
latest_run_status: PASS
latest_approved_run_id: 20260814-171500
approved_at: 2026-08-14
reviewer: 자동 승인(검증 명령)

# M4.4 답변·출처

## 목표

Hybrid 검색 결과만 사용해 근거 기반 답변을 생성하고, 모든 답변에 회의명·Chunk 출처를 포함하며 근거 부족 시 답변을 거절한다.

## 구현 요약

- [`MeetingAnswerService`](../../../../workmate-agent/app/meeting_answer.py)가 Hybrid 검색 결과를 답변과 출처로 변환한다.
- 출처에는 meeting ID·회의명·회의일·Chunk ID·원문 `evidence_text`를 포함한다.
- RRF 점수가 임계값 미만이거나 결과가 없으면 `grounded=false`, `warnings`와 함께 답변을 거절한다.
- 실제 PostgreSQL Hybrid 검색 결과가 답변 출처로 연결되는지 통합 검증했다.

최신 승인 증빙: [20260814-171500 실행 결과](runs/20260814-171500/result.md)
