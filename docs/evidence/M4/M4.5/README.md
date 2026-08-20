status: 완료
latest_run_id: 20260814-181500
latest_run_status: PASS
latest_approved_run_id: 20260814-181500
approved_at: 2026-08-14
reviewer: 자동 승인(검증 명령)

# M4.5 검색 평가

## 목표

실제 회의록 64 Chunk·60 Case 평가 원본의 무결성과 Hybrid Hit@3·HNSW Recall·지연 기준을 재검증한다.

## 구현·검증 요약

- [`test_m45_search_evaluation.py`](../../../../workmate-agent/tests/test_m45_search_evaluation.py)가 승인된 Corpus·Case·Metrics 원본을 검증한다.
- 64개 Chunk, 60개 Case, 고유 ID, 정답 Chunk·Meeting 참조 무결성을 확인했다.
- Hybrid Hit@3 98.21%, HNSW Recall@5 100%, Hybrid DB p95 64.743ms, Query Embedding p95 893.1ms를 확인했다.
- 실제 원본 결과는 `embedding-evaluation/results/postgres-metrics-20260811-101253.json`에서 관리하며 Secret·Token은 복사하지 않았다.

최신 승인 증빙: [20260814-181500 실행 결과](runs/20260814-181500/result.md)
