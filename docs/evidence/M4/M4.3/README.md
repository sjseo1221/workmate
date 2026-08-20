status: 완료
latest_run_id: 20260814-161500
latest_run_status: PASS
latest_approved_run_id: 20260814-161500
approved_at: 2026-08-14
reviewer: 자동 승인(검증 명령)

# M4.3 Hybrid 검색

## 목표

Dense cosine 검색과 `pg_trgm` 키워드 검색을 RRF(k=60)로 결합하고 사용자·회의 metadata 필터를 유지한다.

## 구현 요약

- [`DenseSearchHit`](../../../../workmate-agent/app/repositories/meeting_chunks.py)와 [`HybridSearchHit`](../../../../workmate-agent/app/repositories/meeting_chunks.py)를 추가했다.
- `search_dense`는 1536차원 cosine distance로 후보를 조회한다.
- `search_hybrid`는 Dense·Trigram 후보 순위를 `1 / (60 + rank)`로 결합하고 결정적으로 정렬한다.
- 모든 후보 조회에 `user_id`, 선택적 `meeting_id`, 시작일 범위를 적용한다.
- 실제 PostgreSQL에서 HNSW Index Scan 계획과 RRF 결과를 검증했다.

최신 승인 증빙: [20260814-161500 실행 결과](runs/20260814-161500/result.md)
초기 재작업 증빙: [20260814-160000 실행 결과](runs/20260814-160000/result.md)
