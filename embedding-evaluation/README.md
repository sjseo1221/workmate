# Workmate Embedding Evaluation

[평가 계획과 이력](../docs/10-embedding-evaluation-plan.md)

`openai/text-embedding-3-small`의 한국어 회의록 Dense 검색 품질을 먼저 검증한다. 실제 Base URL과 API Key는 `.env`에만 넣는다.

```powershell
cd C:\dev\workmate\embedding-evaluation
Copy-Item .env.example .env
python -m pip install -r requirements.txt
```

Case와 Corpus만 검사:

```powershell
python run_eval.py --dry-run
python -m unittest discover -s tests
```

Pilot 평가:

```powershell
python run_eval.py
```

지연·안정성 3회 반복 평가:

```powershell
python run_eval.py --repeat 3
```

결과는 `results/run-*.jsonl`과 `results/summary-*.csv`에 생성된다. Pilot은 Python Cosine 정확 검색이며 PostgreSQL+pgvector, Keyword, RRF와 HNSW 평가는 다음 단계에서 수행한다.

PostgreSQL+pgvector 통합 평가:

```powershell
python run_postgres_eval.py
```

`.env`의 `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`로 PostgreSQL에 직접 연결한다. 평가는 `embedding_eval_chunks` 테스트 전용 Table을 다시 만들고 pgvector 정확 검색, PostgreSQL `simple` FTS, `pg_trgm`, HNSW와 `HNSW + pg_trgm` RRF를 비교한다.

기본값은 Trigram 최소 유사도 0.05와 DB 워밍업 10회다. DB 지연시간은 하나의 `psycopg2` 연결을 재사용해 측정하므로 `docker exec`와 `psql` 프로세스 시작 시간을 포함하지 않는다. 한국어 `simple` FTS 실패는 비교 기준선으로 결과에 그대로 기록한다.

합성 확장 평가 데이터 생성과 실행:

```powershell
python generate_expanded_dataset.py
python run_eval.py --corpus corpus/expanded_meeting_chunks.jsonl --cases cases/expanded_cases.jsonl --dry-run
python run_postgres_eval.py --corpus corpus/expanded_meeting_chunks.jsonl --cases cases/expanded_cases.jsonl
```

확장 데이터는 합성 Chunk 1,000개와 질문 60개로 구성되며 실제 회의록 평가를 대신하지 않는다. 답변 가능 질문의 순위 지표와 답변 불가 질문의 오탐률은 분리해 계산한다.

한영 혼합 용어 Holdout 평가:

```powershell
python run_lexical_eval.py
```

이 평가는 기존 1,000 Chunk 평가 Table을 변경하지 않고 원본 Trigram과 한영 Alias 후보 확장을 비교한다. Alias 확장은 운영 기본값이 아니며 원본 순위를 보존한 추가 후보 생성 용도로만 평가한다.

Reranker·답변 가능성 평가:

```powershell
python run_reranker_eval.py
```

`llm-evaluation/.env`의 `OPENAI_BASE_URL2`, `OPENAI_API_KEY2`, `OPENAI_MODEL2`를 사용한다. 기존 확장 검색과 Alias Holdout 결과에 저장된 Top-5 후보를 재사용하므로 Embedding API를 다시 호출하거나 PostgreSQL을 변경하지 않는다. 연결 확인은 `--limit 2`, 특정 실패 Case 재검증은 `--case-id retrieval-016`처럼 실행한다.

실제 회의록 60 Case 평가:

```powershell
python run_postgres_eval.py --corpus corpus/real_meeting_chunks.jsonl --cases cases/real_cases_60.jsonl
python run_reranker_eval.py --corpus corpus/real_meeting_chunks.jsonl --cases cases/real_cases_60.jsonl --search-result results/postgres-run-<timestamp>.jsonl --suite-name real_meeting
```

실제 Corpus는 `chunk_id/title/created_at/participants` 필드를 평가기 표준 필드로 변환한다. `date_to`는 기존 계약대로 미만(Exclusive)으로 처리하므로 같은 날짜의 하루 범위를 조회하려면 다음 날짜를 `date_to`로 지정해야 한다.
