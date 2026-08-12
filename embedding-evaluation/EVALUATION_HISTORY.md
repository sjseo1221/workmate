# Workmate Embedding 평가 및 개선 이력

[평가 계획](../docs/10-embedding-evaluation-plan.md)

Embedding 모델 평가 결과와 평가 중 발생한 수정사항을 날짜순으로 기록한다. 결과가 좋지 않더라도 기존 기록은 삭제하지 않는다.

## 2026-08-10

### 평가 계획 수립

- 대상: `openai/text-embedding-3-small` 단일 모델
- 범위: 한국어 게임 개발 회의록의 Dense 검색, Keyword 검색, RRF 하이브리드 검색과 HNSW 성능
- 최소 기준: 하이브리드 Hit@3 80% 이상
- 상태: API 연결과 Vector 차원 확인 후 Pilot 평가 준비
- 분류: `계획`

### Provider 연결 확인

- 모델: `openai/text-embedding-3-small`
- 실제 응답 모델명: `text-embedding-3-small`
- `/embeddings`: 정상 응답
- Vector 차원: 1536
- `/models`: Provider에서 제공하지 않음(HTTP 404)
- 인증: 기존 로컬 Secret으로 성공했으며 실제 Key와 Base URL은 기록하지 않음
- 분류: `Provider`, `모델`

### Dense Pilot 1차 평가

- 결과: [metrics-20260810-142816.json](results/metrics-20260810-142816.json), [summary-20260810-142816.csv](results/summary-20260810-142816.csv), [run-20260810-142816.jsonl](results/run-20260810-142816.jsonl)
- 데이터: 비식별 합성 회의 Chunk 32개, 답변 가능 질문 20개
- 모델: `openai/text-embedding-3-small`
- Vector 차원: 1536
- 품질:
  - Hit@1 80%
  - Hit@3 100%
  - Hit@5 100%
  - MRR 0.90
  - nDCG@10 0.9262
- 지연:
  - Query p50 960.2ms
  - Query p95 1,095.6ms
  - 문서 32개 Batch 2,649.3ms
- 사용량: 문서 996 Token, 질문 479 Token
- Hit@1 실패:
  - `retrieval-008`: 트레일러 검수보다 같은 트레일러의 음원 Chunk가 1위
  - `retrieval-009`: 저사양 그림자보다 고사양 그림자 Chunk가 근소하게 1위
  - `retrieval-012`: 로그인 분석 Action Item보다 같은 회의의 현상 설명 Chunk가 1위
  - `retrieval-018`: 서버 재시작 절차보다 프로파일링 Action Item이 1위
- 판단:
  - Dense 검색은 Pilot Hit@3 기준을 통과했다.
  - 한영 혼합 용어와 같은 회의의 인접 Chunk 구분은 Keyword·RRF와 인접 문맥 확장으로 재검증한다.
  - API 포함 p95가 권장 1초를 약 96ms 초과해 반복 측정이 필요하다.
  - 답변 불가 질문, 실제 회의록 60개 Case, PostgreSQL+pgvector, Keyword·RRF와 HNSW 평가는 아직 수행하지 않았다.
- 분류: `모델`, `Pilot`, `평가기`

### Dense Pilot 3회 반복 검증

- 결과: [metrics-20260810-152629.json](results/metrics-20260810-152629.json), [summary-20260810-152629.csv](results/summary-20260810-152629.csv), [run-20260810-152629.jsonl](results/run-20260810-152629.jsonl)
- 실행: 20개 Case를 3회 반복해 Query 60건 평가
- 품질:
  - Hit@1 80%, Hit@3 100%, Hit@5 100%
  - MRR 0.90, nDCG@10 0.9262
  - 세 반복에서 모든 Case의 정답 순위가 동일함
- 전체 지연: p50 995.9ms, p95 1,164.4ms
- 반복별 지연:
  - 1회차 p50 1,009.0ms, p95 1,190.8ms
  - 2회차 p50 996.9ms, p95 1,139.6ms
  - 3회차 p50 971.9ms, p95 1,091.3ms
- 안정성: Provider 오류 0건, 순위 변동 Case 0건
- 사용량: 문서 996 Token, 질문 1,437 Token
- 판단:
  - Dense 검색 품질과 반복 안정성은 통과했다.
  - API 포함 p95 1초 기준은 세 반복 모두 통과하지 못했다.
  - PostgreSQL+pgvector 검증은 현재 Docker Engine이 실행되지 않고 로컬 `psql`도 없어 시작하지 못했다.
  - Docker 또는 접근 가능한 PostgreSQL이 준비되면 Keyword·RRF와 HNSW 검증을 진행한다.
- 검증: Python 구문 검사, 단위 테스트 5개, Corpus 32개·Case 20개 dry-run 통과
- 분류: `모델`, `Pilot`, `성능`, `운영 환경`

### PostgreSQL·pgvector·HNSW 통합 Pilot

- 실행 날짜: 2026-08-10
- 결과: [postgres-metrics-20260810-153853.json](results/postgres-metrics-20260810-153853.json), [postgres-summary-20260810-153853.csv](results/postgres-summary-20260810-153853.csv), [postgres-run-20260810-153853.jsonl](results/postgres-run-20260810-153853.jsonl)
- 환경: PostgreSQL 16.14, pgvector 0.8.2, pg_trgm 1.6, `vector(1536)`, Corpus 32개·Case 20개
- Dense 정확 검색: Hit@1 80%, Hit@3 100%, Hit@5 100%, MRR 0.90
- HNSW 검색: Hit@1 80%, Hit@3 100%, Hit@5 100%, MRR 0.90
- HNSW Recall@5: 정확 검색 대비 100%; `EXPLAIN`에서 `embedding_eval_chunks_hnsw_idx` Index Scan 사용 확인
- PostgreSQL `simple` FTS: Hit@1·3·5 0%, MRR 0
- RRF: Keyword 결과가 없어 Dense와 동일한 Hit@1 80%, Hit@3·5 100%, MRR 0.90
- 지연시간: Dense p95 318.7ms, Keyword p95 235.7ms, HNSW p95 270.3ms
- 발견된 문제:
  - `plainto_tsquery('simple', 전체 한국어 질문)`은 공백 단위 Lexeme를 AND 조건으로 만들며, 조사·어미가 붙은 회의 원문과 일치하지 않아 Keyword 결과가 비었다.
  - Dense p95는 기준 300ms를 18.7ms 초과했다.
- 원인 분류: `검색식`, `한국어 토큰화`, `측정 환경`
- 판단:
  - 선택한 Embedding과 pgvector/HNSW Migration은 Pilot 기준을 통과했다.
  - 현재 Keyword·RRF는 운영 검색식으로 채택하지 않는다. `pg_trgm` 또는 한국어 형태소 분석 기반 Keyword 검색을 별도 비교한 뒤 RRF를 다시 평가한다.
  - 지연시간은 매 Query마다 `docker exec`와 `psql` 프로세스를 시작한 왕복시간이다. DB 자체 p95 판정에는 지속 연결 방식으로 재측정해야 한다.
- 검증: Python 구문 검사, 단위 테스트 6개 통과
- 분류: `PostgreSQL`, `pgvector`, `HNSW`, `Keyword`, `Pilot`

### Keyword·RRF·지연시간 측정 개선 및 재평가

- 실행 날짜: 2026-08-10
- 최종 결과: [postgres-metrics-20260810-161539.json](results/postgres-metrics-20260810-161539.json), [postgres-summary-20260810-161539.csv](results/postgres-summary-20260810-161539.csv), [postgres-run-20260810-161539.jsonl](results/postgres-run-20260810-161539.jsonl)
- 변경 전 문제:
  - 한국어 `simple` FTS 결과 없음 100%로 RRF가 Dense와 동일했다.
  - `docker exec`와 `psql` 시작 시간이 DB 지연에 포함됐다.
- 변경 내용:
  - 정규화한 회의명·본문에 `pg_trgm` GiST 검색과 최소 유사도 0.05 적용
  - HNSW + Trigram RRF 적용; 동점은 HNSW 순위 우선
  - `psycopg2` 지속 연결과 DB 워밍업 10회 적용
  - nDCG, 결과 없음 비율, 질문 유형별 지표 추가
- 중간 평가: [postgres-metrics-20260810-161202.json](results/postgres-metrics-20260810-161202.json)
  - RRF 개선 1건, 유지 18건, 악화 1건
  - RRF 동점을 Chunk ID로 정렬한 것이 악화 원인이어서 HNSW 순위 우선으로 수정
- 최종 품질:
  - Trigram Hit@1 80%, Hit@3·5 90%, 결과 없음 10%
  - HNSW + Trigram RRF Hit@1 85%, Hit@3·5 100%, MRR 0.925, nDCG@10 0.9446
  - HNSW 대비 개선 1건, 유지 19건, 악화 0건
- 최종 지연:
  - Hybrid DB p50 56.079ms, p95 62.429ms
  - Query Embedding API p50 1,124.5ms, p95 1,202.6ms
- 판단:
  - Keyword·RRF와 DB 지연 측정 문제는 Pilot 범위에서 개선됐다.
  - 혼합 용어 Trigram 결과 없음 50%와 API p95 1초 초과는 남은 개선사항이다.
  - 실제 질문 60개, 답변 불가 질문, 1,000개 이상 Chunk 평가 전에는 최종 운영 확정으로 보지 않는다.
- 검증: Python 구문 검사, 단위 테스트 8개, 실제 PostgreSQL 통합 평가 통과
- 분류: `Keyword`, `RRF`, `지연시간`, `평가기`, `Pilot`

### 합성 1,000 Chunk·60 Case 확장 평가

- 실행 날짜: 2026-08-10
- 데이터: 합성 Chunk 1,000개, 답변 가능 질문 50개, 답변 불가 질문 10개
- 생성 파일: `generate_expanded_dataset.py`, `corpus/expanded_meeting_chunks.jsonl`, `cases/expanded_cases.jsonl`
- 첫 결과: [postgres-metrics-20260810-162708.json](results/postgres-metrics-20260810-162708.json)
  - 기본 HNSW Recall@5 68.8%, HNSW Hit@3 56%
  - 원인: 기본 `ef_search=40`과 Filter 후 후보 부족
- HNSW 조정 결과: [postgres-metrics-20260810-163055.json](results/postgres-metrics-20260810-163055.json)
  - `ef_search=200`, `iterative_scan=strict_order` 적용
  - Recall@5 88%, HNSW Hit@3 78%; 기준 미달
- 최종 비교: [postgres-metrics-20260810-163701.json](results/postgres-metrics-20260810-163701.json), [postgres-summary-20260810-163701.csv](results/postgres-summary-20260810-163701.csv), [postgres-run-20260810-163701.jsonl](results/postgres-run-20260810-163701.jsonl)
- 최종 검색 품질:
  - Dense 정확 + Trigram RRF Hit@1 90%, Hit@3·5 98%, MRR 0.9367, nDCG@10 0.9479
  - HNSW Recall@5 89.6%, HNSW + Trigram RRF Hit@3·5 94%
  - 정확 RRF는 Dense 대비 개선 4건, 유지 46건, 악화 0건
- 답변 불가:
  - 임계값 0.45에서 오탐 0%, 정상 질문 거절 16%
  - Sweep 범위에서 두 비율을 동시에 10% 이하로 만족하지 못함
- 지연:
  - Dense 정확 + Trigram DB p95 97.924ms
  - HNSW + Trigram DB p95 67.075ms
  - Query Embedding API p95 1,218.5ms
- 판단:
  - 1,000 Chunk 이하에서는 약 30ms 절약보다 검색 품질을 우선해 Dense 정확 + Trigram RRF를 선택한다.
  - HNSW는 Recall 손실 10.4%p로 보류한다.
  - 단일 Cosine 임계값은 답변 불가 최종 판정에 사용하지 않는다.
  - 실제 비식별 회의록 평가 전에는 최종 운영 확정으로 보지 않는다.
- 검증: Corpus·Case 검증, Python 구문 검사, 단위 테스트 10개, 실제 PostgreSQL 평가 통과
- 분류: `확장 평가`, `Dense`, `Trigram`, `RRF`, `HNSW`, `답변 불가`

### 한영 혼합 용어 Holdout 평가

- 실행 날짜: 2026-08-10
- 데이터: 기존 1,000 Chunk, 별도 Holdout 질문 20개
- 변경 파일: `cases/lexical_holdout_cases.jsonl`, `run_lexical_eval.py`, `run_postgres_eval.py`
- 목적: `retrieval-009`와 같은 한영 혼합 Query의 Candidate Recall 개선
- 최대 점수 병합: [lexical-metrics-20260810-164925.json](results/lexical-metrics-20260810-164925.json)
  - Hit@1 85%, Hit@3·5 100%
  - 개선 7, 유지 12, 악화 1
  - Alias 유사 오답이 기존 정답 1위를 덮어써 미채택
- RRF 병합: [lexical-metrics-20260810-165018.json](results/lexical-metrics-20260810-165018.json)
  - Hit@1 60%, Hit@3 95%, Hit@5 100%
  - 개선 7, 유지 12, 악화 1
  - 낮은 점수의 원본 오답까지 순위 신호가 되어 미채택
- 최종 원본 순위 보존 방식: [lexical-metrics-20260810-165152.json](results/lexical-metrics-20260810-165152.json), [lexical-run-20260810-165152.jsonl](results/lexical-run-20260810-165152.jsonl)
  - 원본: Hit@1·3 65%, Hit@5 75%, MRR 0.6750
  - Alias 후보 추가: Hit@1 65%, Hit@3 85%, Hit@5 100%, MRR 0.7708
  - 개선 5, 유지 15, 악화 0
  - p95 2.095ms에서 3.402ms로 1.307ms 증가
- 판단:
  - Alias는 운영 기본 순위에 적용하지 않는다.
  - 원본 순위를 보존하는 선택적 Candidate 확장으로만 사용한다.
  - 다음 평가에서 Reranker 또는 Groundedness 검증과 결합한다.
- 검증: Case 검증, Python 구문 검사, 단위 테스트 12개, 실제 PostgreSQL 평가 통과
- 분류: `한영 혼합`, `Alias`, `Trigram`, `Holdout`, `Candidate Recall`

### Reranker·답변 가능성 평가

- 실행 날짜: 2026-08-10
- 모델: `openai/gpt-4.1-mini`
- 데이터: 확장 검색 60 Case와 Alias Holdout 20 Case, 총 80 Case
- 평가기: `run_reranker_eval.py`
- 입력 후보: 저장된 Dense 정확+Trigram RRF Top-5와 Alias 확장 Top-5
- 최초 결과: [reranker-metrics-20260810-170526.json](results/reranker-metrics-20260810-170526.json), [reranker-run-20260810-170526.jsonl](results/reranker-run-20260810-170526.jsonl)
  - 전체 Hit@1 94.29%, Hit@3·5 95.71%
  - 답변 불가 오탐 0건, 정상 질문 거절 3건
  - `retrieval-009`는 정답 후보 누락, `retrieval-016`과 `retrieval-046`은 Reranker 오판
- 원인 분류: `검색 후보`, `프롬프트`, `평가기`
- 수정 이유:
  - 여러 Chunk가 질문의 서로 다른 부분을 함께 뒷받침할 수 있다는 규칙이 모호했다.
  - 담당자·기한·행동이 명시된 후속업무 문장을 직접 근거로 인정하는 규칙이 필요했다.
- 부분 재검증: [reranker-metrics-20260810-170703.json](results/reranker-metrics-20260810-170703.json)
  - 오판 2건 모두 답변 가능과 정답 Top-1 회복
- 최종 결과: [reranker-metrics-20260810-170901.json](results/reranker-metrics-20260810-170901.json), [reranker-summary-20260810-170901.csv](results/reranker-summary-20260810-170901.csv), [reranker-run-20260810-170901.jsonl](results/reranker-run-20260810-170901.jsonl)
  - 전체 기존 후보 Hit@1 82.86%에서 Reranker 97.14%로 개선
  - 확장 Set Hit@1 90%에서 96%, Alias Holdout 65%에서 100%로 개선
  - 후보 Recall 98.57%; 개선 11, 유지 58, 악화 0, 검색 후보 누락 1
  - 전체 답변 불가 오탐 0%, 정상 질문 거절 1.43%
  - 검색 후보 누락 제외 시 Reranker 판단 79/79, 100%
  - Provider 오류 0건
  - p50 1,109.3ms, p95 2,639.5ms
  - 입력 38,245 Token, 출력 1,420 Token
- 최종 판단:
  - 합성 평가의 품질 기준은 통과했다.
  - 높은 추가 지연 때문에 상시 적용은 보류하고 조건부 호출과 실제 비식별 회의록 평가를 진행한다.
  - `retrieval-009`는 Alias 후보를 실제 검색 파이프라인에 연결한 뒤 재검증한다.
- 검증: Python 구문 검사, 단위 테스트 16개, 실제 API 전체 80건 평가 통과
- 분류: `Reranker`, `Groundedness`, `답변 불가`, `Alias`, `지연시간`

### 실제 회의록 60 Case 검색·Reranker 평가

- 실행 날짜: 2026-08-10
- 입력: `corpus/real_meeting_chunks.jsonl` 5개 Chunk·3개 회의, `cases/real_cases_60.jsonl` 60개
- 표준화: 실제 필드 `chunk_id/title/created_at/participants`를 평가기 표준 필드로 입력 경계에서 변환
- Embedding: `openai/text-embedding-3-small`, 1536차원
- 검색 결과: [postgres-metrics-20260810-171951.json](results/postgres-metrics-20260810-171951.json), [postgres-summary-20260810-171951.csv](results/postgres-summary-20260810-171951.csv), [postgres-run-20260810-171951.jsonl](results/postgres-run-20260810-171951.jsonl)
- 검색 결과:
  - Dense 정확 + Trigram RRF Hit@1 88%, Hit@3·5 94%, MRR 0.9067
  - HNSW Recall@5 100%, Hybrid DB p95 63.939ms
  - Query Embedding p95 1,165.3ms
  - Metadata Filter Hit@1 40%, Hit@3 70%
  - Cosine 0.45 정상 질문 거절 56%, 답변 불가 오탐 0%
- 문제 분류:
  - `retrieval-043/044/045`: `date_to` 미만 규약과 같은 날짜 입력 충돌로 후보 누락
  - `retrieval-028`: 의미 재표현을 Reranker가 답변 불가로 판정
- Reranker 결과: [reranker-metrics-20260810-172528.json](results/reranker-metrics-20260810-172528.json), [reranker-summary-20260810-172528.csv](results/reranker-summary-20260810-172528.csv), [reranker-run-20260810-172528.jsonl](results/reranker-run-20260810-172528.jsonl)
  - 모델: `openai/gpt-4.1-mini`
  - 후보 Recall 94% (47/50)
  - 기존 RRF Hit@1 88% → Reranker 92%
  - 기존 RRF Hit@3·5 94% → Reranker 92%
  - 개선 3, 유지 43, 악화 1, 검색 후보 누락 3
  - 답변 불가 오탐 0%, 정상 질문 거절 8%
  - 후보 존재 Case만 보면 정상 질문 거절 1/47, 2.13%
  - p50 1,165.4ms, p95 1,520.7ms, Provider 오류 0건
- 수정 파일: `run_postgres_eval.py`, `run_reranker_eval.py`, `README.md`, `docs/10-embedding-evaluation-plan.md`
- 최종 판단:
  - 실제 데이터 검색은 Hybrid Hit@3 기준을 통과했다.
  - Reranker는 Metadata Filter 입력 보강 후 일부 순위를 개선했지만 전체 Top-3를 개선하지 못했으므로 상시 적용하지 않는다.
  - 날짜 범위 Case를 보정하고 실제 Chunk를 확장한 뒤 조건부 Reranker를 재평가한다.
- 검증: Python 구문 검사, 단위 테스트 16개, 실제 Embedding API 검색 60건, 실제 LLM Reranker 60건 통과
- 분류: `실제 데이터`, `PostgreSQL`, `RRF`, `Metadata Filter`, `Reranker`, `평가 계약`

### 실제 Case 날짜 범위 보정

- 실행 날짜: 2026-08-10
- 대상: `retrieval-043`, `retrieval-044`, `retrieval-045`
- 문제: `date_to`가 종료일 미만(Exclusive) 규칙인데 `date_from`과 같은 날짜로 입력되어 해당 날짜의 검색 결과가 제외됨
- 수정:
  - `retrieval-043`: `date_to` `2026-08-01` → `2026-08-02`
  - `retrieval-044`: `date_to` `2026-07-22` → `2026-07-23`
  - `retrieval-045`: `date_to` `2026-07-15` → `2026-07-16`
- 수정 파일: `embedding-evaluation/cases/real_cases_60.jsonl`
- 다음 평가: 보정된 Case로 PostgreSQL 검색 60건과 Reranker 60건 재실행
- 분류: `평가 계약`, `Metadata Filter`, `date_to`

### 실제 Case 날짜 보정 후 재평가

- 실행 날짜: 2026-08-10
- 검색 결과: [postgres-metrics-20260810-173735.json](results/postgres-metrics-20260810-173735.json), [postgres-summary-20260810-173735.csv](results/postgres-summary-20260810-173735.csv), [postgres-run-20260810-173735.jsonl](results/postgres-run-20260810-173735.jsonl)
- Reranker 결과: [reranker-metrics-20260810-173859.json](results/reranker-metrics-20260810-173859.json), [reranker-summary-20260810-173859.csv](results/reranker-summary-20260810-173859.csv), [reranker-run-20260810-173859.jsonl](results/reranker-run-20260810-173859.jsonl)
- 검색 결과:
  - Dense 정확 + Trigram RRF Hit@1 94%, Hit@3·5 100%, MRR 0.9667
  - HNSW Recall@5 100%, Hybrid DB p95 63.378ms
  - Metadata Filter Hit@1 70%, Hit@3 100%
  - Query Embedding p95 1,191.6ms
- Reranker 결과:
  - 후보 Recall 100%
  - RRF Hit@1 94% → Reranker 98%
  - RRF Hit@3·5 100% → Reranker 98%
  - 개선 3, 유지 46, 악화 1, 검색 후보 누락 0
  - 답변 불가 오탐 0%, 정상 질문 거절 1/50, 2%
  - p50 1,161.1ms, p95 1,650.5ms, Provider 오류 0건
- 남은 문제: `retrieval-028`의 의미 재표현 1건을 Reranker가 거절
- 최종 판단: 날짜 계약 오류는 해소됐고 검색 품질 기준을 통과했다. Reranker는 품질을 개선했지만 추가 지연과 1건의 의미 재표현 실패가 있어 실제 Chunk 확장 후 조건부 적용을 최종 결정한다.
- 분류: `재평가`, `Metadata Filter`, `Reranker`, `date_to`, `실제 데이터`

### 2026-08-11 최신 실제 회의록 64 Chunk·60 Case 재평가

- 대상: `corpus/real_meeting_chunks.jsonl` 64개 Chunk·61개 회의, `cases/real_cases_60.jsonl` 60개 Case
- 모델: Embedding `openai/text-embedding-3-small`(1536차원), Reranker `openai/gpt-4.1-mini`
- 검색 결과: [postgres-metrics-20260811-101253.json](results/postgres-metrics-20260811-101253.json), [postgres-summary-20260811-101253.csv](results/postgres-summary-20260811-101253.csv), [postgres-run-20260811-101253.jsonl](results/postgres-run-20260811-101253.jsonl)
- 검색 품질: Dense+Trigram RRF Hit@1 96.43%, Hit@3 98.21%, Hit@5 100%, MRR 0.9777
- HNSW Recall@5 100%, Hybrid DB p95 66.3ms, Query Embedding p95 893.1ms
- Cosine 0.45 답변 가능성 기준: 정상 질문 23건 거절(오탐 41.07%), 운영 사용 중단
- Reranker 결과: [reranker-metrics-20260811-101533.json](results/reranker-metrics-20260811-101533.json), [reranker-summary-20260811-101533.csv](results/reranker-summary-20260811-101533.csv), [reranker-run-20260811-101533.jsonl](results/reranker-run-20260811-101533.jsonl)
- Reranker 품질: Hit@1·3·5 94.64%, MRR 0.9464; 답변 가능성 정확도 95%; 오탐 0/4; 정상 질문 거절 3/56
- 순위 변화: 개선 1, 유지 52, 악화 3(`retrieval-009/047/048`), 후보 누락 0
- 지연: Reranker p50 1,088ms, p95 1,406.7ms; Provider 오류 0/60
- 판단: RRF/HNSW는 운영 후보로 통과. Reranker는 기본 경로가 아닌 조건부 호출+RRF fallback으로 보류.
- 분류: `실제 데이터`, `PostgreSQL`, `RRF`, `HNSW`, `Reranker`, `성능`

## 기록 양식

```markdown
### 변경 또는 평가 제목

- 실행 날짜:
- 후보 모델과 Revision:
- Corpus·Case 버전:
- 결과 파일:
- 변경 전 결과:
- 발견된 문제:
- 원인 분류: 모델 / 데이터 / Chunk / 검색식 / Index / 평가기
- 수정 이유:
- 변경 파일과 내용:
- 재평가 결과:
- 최종 판단:
```
