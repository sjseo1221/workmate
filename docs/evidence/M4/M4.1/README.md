status: 완료
latest_run_id: 20260814-143000
latest_run_status: PASS
latest_approved_run_id: 20260814-143000
approved_at: 2026-08-14
reviewer: 자동 승인(검증 명령)

# M4.1 검색 데이터

## 목표

회의 Transcript를 사용자 범위로 Chunk화하고 `openai/text-embedding-3-small`의 1536차원 Vector를 PostgreSQL `meeting_chunks.embedding`에 저장·재생성할 기반을 구현한다.

## 착수 검토 결과

- M3.3 Transcript 저장·조회가 선행 조건으로 승인되어 있다.
- `workmate-agent`의 `meeting_chunks` Migration, Repository, Embedding Adapter와 M4.1-04 통합 검수가 모두 완료되었다.
- PostgreSQL을 단일 저장소로 사용하며 별도 Vector DB는 도입하지 않는다.
- 공개 검색 API와 RRF/HNSW 검색 로직은 M4.2~M4.4 범위로 분리한다.
- Embedding Provider Secret은 코드·Fixture·증빙에 저장하지 않는다.

## 구현 순서

1. `M4.1-01`: pgvector 확장과 `meetings`/`meeting_chunks` Migration 계약 확정
2. `M4.1-02`: `user_id` 범위가 적용된 Chunk Repository와 CRUD 테스트
3. `M4.1-03`: Embedding Adapter·1536차원 검증·재임베딩 경계 구현
4. `M4.1-04`: PostgreSQL 통합·Index Scan·재임베딩 회귀 검수

## M4.1-01 착수 결과

- `workmate-agent/migrations/004_search_data.sql`에 pgvector·pg_trgm 확장, `meetings`, `meeting_chunks`, 사용자 범위 복합 FK, 시간 구간 제약, Trigram·HNSW Index를 추가했다.
- `workmate-agent/tests/test_search_data_migration.py`에 Migration 계약 테스트를 추가했다.
- 실제 PostgreSQL 적용과 Index Scan 검증은 M4.1-04에서 수행한다.

M4.1-01 승인 증빙: [20260814-120000 실행 결과](runs/20260814-120000/result.md)

M4.1-02 검수 증빙: [20260814-123000 실행 결과](runs/20260814-123000/result.md)

M4.1-02 PostgreSQL 보류 증빙: [20260814-124000 실행 결과](runs/20260814-124000/result.md)

M4.1-02 최신 승인 증빙: [20260814-125000 실행 결과](runs/20260814-125000/result.md)

M4.1-03 최신 승인 증빙: [20260814-131500 실행 결과](runs/20260814-131500/result.md)

M4.1-04 초기 재작업 증빙: [20260814-140500 실행 결과](runs/20260814-140500/result.md)

M4.1-04 최신 승인 증빙: [20260814-143000 실행 결과](runs/20260814-143000/result.md)

## M4.1-03 구현 요약

- `OpenAICompatibleEmbeddingClient`가 `EMBEDDING_BASE_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`을 사용해 `/embeddings`를 호출한다.
- `openai/text-embedding-3-small`와 1536차원 응답을 강제하고, Provider 오류 시 기존 Chunk를 보존한다.
- `ReembeddingService`는 사용자 범위를 확인하고 검증 완료 후 Embedding version을 증가시킨다.
- 단위·회귀 8개, `compileall`, `git diff --check`, 실제 Provider smoke가 모두 PASS하여 자동 승인했다.

## M4.1-04 통합 검수 요약

- 실제 PostgreSQL 16 + pgvector에서 Migration·Repository·재임베딩을 검증했다.
- 200개 Chunk의 사용자 범위 조회, 1536차원 재임베딩, Embedding version 증가를 확인했다.
- `meeting_chunks_embedding_idx` HNSW Index Scan 계획을 확인했다.
- 최종 통합·회귀 6개, `compileall`, `git diff --check`가 PASS하여 자동 승인했다.

## 완료 조건

- `vector(1536)` Migration과 Cosine 연산 계약이 적용된다.
- 모든 Chunk 조회·수정·재임베딩에 요청 `user_id` 범위가 적용된다.
- 모델 응답 차원이 1536이 아니면 저장하지 않고 명시적 오류를 반환한다.
- Provider 장애는 기존 Chunk를 삭제하지 않고 경고·실패 상태로 남긴다.
- PostgreSQL 통합 테스트와 `compileall`, `git diff --check`가 PASS다.

구현 결과가 생긴 뒤 실행별 `runs/{run_id}/result.md`를 작성하고, 모든 검증 명령이 정확히 PASS일 때만 자동 승인한다.
