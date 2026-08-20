# M4.1-04 검수 결과

- 실행 ID: 20260814-140500
- 상태: 재작업
- 결과: FAIL

## 실패 내용

- 사용자 `user_id` 조건과 HNSW 정렬 계획을 하나의 EXPLAIN에서 동시에 확인하려 했으나 PostgreSQL이 사용자 범위 B-tree Index를 선택했다.
- 원인: 사용자 필터와 Vector 정렬이 서로 다른 인덱스 요구를 가져 단일 계획에서 HNSW 선택을 보장하지 않음.
- 수정 방향: 사용자 범위 조회는 Repository 테스트로 확인하고, HNSW Index Scan은 별도 Vector 정렬 EXPLAIN으로 검증한다.
- 재검수 조건: 수정한 통합 테스트에서 사용자 격리·재임베딩·HNSW 계획을 모두 PASS.
