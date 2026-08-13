# Workmate Embedding 모델 평가 계획

[← 기술 상세 설계](07-technical-specification.md) · [목차](README.md)

## 1. 목적

회의록 검색에 사용할 `openai/text-embedding-3-small`의 채택 가능 여부와 `meeting_chunks.embedding`의 Vector 차원을 확정한다. 단일 모델의 문장 유사도만 확인하지 않고 다음 실제 검색 경로가 기준을 통과하는지 평가한다.

```text
질문 Embedding
→ PostgreSQL pgvector 검색
→ PostgreSQL Keyword 검색
→ RRF 결과 통합
→ 관련 회의 Chunk와 출처 반환
```

최종 산출물은 다음과 같다.

- `EMBEDDING_MODEL`
- `EMBEDDING_VERSION`
- `EMBEDDING_DIMENSION`
- Query와 Document 전처리 규칙
- 정규화 여부와 Cosine Distance 사용 규칙
- 품질·지연·비용 기준선

## 2. 평가 대상

| 모델 ID | 실행 방식 | 확인 차원 | 평가 상태 |
| --- | --- | ---: | --- |
| `openai/text-embedding-3-small` | OpenAI 호환 API | 1536 | **운영 후보 확정** — 실제 64 Chunk·60 Case 평가 통과 |

API Base URL과 Key는 각각 `EMBEDDING_BASE_URL`, `EMBEDDING_API_KEY`로 주입하고 문서와 결과 파일에는 실제 값을 기록하지 않는다. 모델 ID는 `EMBEDDING_MODEL=openai/text-embedding-3-small`로 고정한다.

2026-08-10 실제 `/embeddings` 요청으로 모델 사용 가능 여부와 1536차원 출력을 확인했다. Provider의 `/models` Operation은 제공되지 않으므로 실제 Embedding 생성 요청을 연결 검증 기준으로 사용한다.

## 3. 평가 데이터

실제 또는 비식별화한 한국어 게임 개발 회의록 10개 이상과 질문 60개를 준비한다.

| 질문 유형 | 권장 개수 | 예시 |
| --- | ---: | --- |
| 정확한 용어·고유명사 | 15 | `QA 빌드 일정은 언제야?` |
| 의미가 같은 다른 표현 | 15 | `로그인 장애 조사 담당자는 누구야?` |
| 한영 혼합 게임 개발 용어 | 10 | `리소스 Hotfix 결정 내용은?` |
| 날짜·회의·참여자 필터 | 10 | `지난주 김서연이 말한 배포 일정은?` |
| 답이 없는 질문 | 10 | `콘솔 버전 출시일은?` |

각 Case는 다음 값을 가진다.

```json
{
  "case_id": "retrieval-001",
  "query": "QA 빌드는 언제 배포하기로 했어?",
  "relevant_meeting_ids": ["meeting-101"],
  "relevant_chunk_ids": ["chunk-101-3"],
  "filters": {
    "date_from": null,
    "date_to": null,
    "participant_user_ids": []
  },
  "category": "semantic_paraphrase",
  "answerable": true
}
```

정답 Meeting과 Chunk는 사람이 원문을 확인해 확정한다. 같은 주제를 다루지만 정답이 아닌 Chunk를 포함해 유사한 문맥을 구분할 수 있는지도 평가한다.

## 4. 고정 조건

반복 평가 사이에 다음 조건을 동일하게 유지한다.

- 동일한 회의 원문과 Chunk 분할
- 동일한 질문, 정답과 Metadata 필터
- Cosine Distance 사용
- Vector Top-K 20, Keyword Top-K 20, Trigram 최소 유사도 0.05
- RRF 상수 60, 동점이면 HNSW 순위를 우선
- Dense 안정성은 Query당 3회 반복하고, PostgreSQL 통합 Pilot은 DB 워밍업 10회 후 측정
- DB 지연은 하나의 `psycopg2` 연결을 유지한 상태에서 SQL 실행과 결과 수신 시간만 측정
- Query와 Document Embedding 생성 규칙 기록
- 출력 Vector 정규화 여부 기록

Pilot에서는 Python Cosine 정확 검색으로 모델 자체의 품질을 먼저 확인한다. 이후 PostgreSQL+pgvector 정확 검색과 HNSW를 검증하고, 전체 기준을 통과한 뒤 운영 Migration을 `vector(1536)`으로 고정한다.

## 5. 평가 단계

### 5.1 Case와 Corpus 검증

- 중복 Case ID 검사
- 존재하지 않는 Meeting·Chunk ID 검사
- 답변 가능 Case의 정답 Chunk 누락 검사
- 답변 불가 Case에 정답 Chunk가 들어간 오류 검사
- 질문 유형별 개수 검사

### 5.2 Dense 검색 품질

선택한 모델의 Vector 검색을 실행해 검색 품질을 측정한다. 처음에는 HNSW 없이 정확 검색을 사용한다.

### 5.3 하이브리드 검색 품질

동일 Case에서 다음 결과를 비교한다.

1. 실패 기준선인 PostgreSQL `simple` FTS
2. 정규화한 회의명과 본문의 `pg_trgm` 검색
3. pgvector Dense 정확 검색과 HNSW 검색
4. HNSW와 Trigram 순위를 합친 RRF 검색

원시 Vector 점수와 Keyword 점수를 직접 가중 합산하지 않는다. RRF 점수가 같으면 의미 검색 결과를 보존하기 위해 HNSW 순위를 우선한다. 별도 Reranker는 기본 경로에 상시 넣지 않고, 하이브리드 품질·지연을 확인한 뒤 모호한 질의에 대한 조건부 호출로 평가한다.

### 5.4 HNSW와 운영 성능

선택한 모델에 HNSW를 적용하고 정확 검색 대비 품질 손실과 성능 개선을 측정한다.

DB 지연시간은 `docker exec`나 매 요청마다 새 `psql` 프로세스를 실행하는 방식으로 측정하지 않는다. 애플리케이션과 같은 지속 DB 연결을 사용하고, 연결 및 인덱스 워밍업 10회는 측정에서 제외한다.

- Query Embedding 지연 p50·p95
- DB 검색 지연 p50·p95
- 1,000개 Chunk Batch Embedding 시간
- 초당 처리 Chunk 수
- 최대 RAM·VRAM
- Vector와 HNSW Index 저장 용량
- API Token 비용 또는 로컬 실행 비용
- Timeout과 Rate Limit 비율

## 6. 평가 지표와 통과 기준

| 구분 | 지표 | 최소 기준 |
| --- | --- | ---: |
| 검색 품질 | 하이브리드 Hit@3 | 80% 이상 |
| 검색 품질 | 하이브리드 Recall@5 | 90% 이상 권장 |
| 순위 품질 | MRR@10, nDCG@10 | 후보 비교값 기록 |
| 답변 불가 | 오탐률 | 10% 이하 |
| 답변 가능 | 잘못된 답변 거절률 | 10% 이하 권장 |
| 근사 검색 | HNSW Recall 손실 | 정확 검색 대비 5%p 이하 |
| DB 성능 | 검색 지연 p95 | 300ms 이하 |
| 전체 성능 | Query Embedding 포함 p95 | API 1초, 로컬 2초 이하 권장 |
| 안정성 | 요청 오류율 | 1% 이하 |

전체 점수만 보지 않고 질문 유형별 결과를 함께 기록한다. 특정 유형이 60% 미만이면 전체 평균을 통과해도 원인을 검토한다.

## 7. 모델 채택 규칙

1. 하이브리드 Hit@3가 80% 이상인지 확인
2. 답변 불가 질문 오탐률이 10% 이하인지 확인
3. 운영 환경의 지연·비용 조건을 충족하는지 확인
4. PostgreSQL+pgvector와 HNSW Migration이 정상 동작하는지 확인
5. 모든 필수 기준을 통과하면 운영 모델로 채택
6. 필수 기준을 통과하지 못한 경우에만 대체 후보를 추가해 재평가

채택 후 `embedding_model`, `embedding_version`과 1536차원을 Schema와 Migration에 반영한다. 모델 변경 시 기존 `meeting_chunks` 전체를 다시 Embedding해야 한다.

## 8. 결과와 수정 이력 관리

실행 결과는 `embedding-evaluation/results/`에 저장하고, 평가 중 발견된 문제와 수정 이유는 [Embedding 평가 및 개선 이력](../embedding-evaluation/EVALUATION_HISTORY.md)에 날짜순으로 기록한다.

이력에는 다음 항목을 반드시 남긴다.

1. 실행 날짜, 후보 모델과 Revision
2. Corpus·Case 버전과 결과 파일
3. 품질·지연·비용 결과
4. 실패 원인이 모델, 데이터, Chunk, 검색식, Index 또는 평가기 중 어디인지
5. 수정 전 문제와 수정한 이유
6. 변경 파일과 변경 내용
7. 같은 조건으로 재평가한 결과

평가 기준을 낮춰 실패를 통과시키지 않는다. 잘못된 정답이나 평가기 오류를 수정한 경우에도 변경 전 결과를 삭제하지 않고 재평가 결과를 별도로 남긴다.

## 9. 문서 반영 범위

모델이 확정되면 다음 문서를 갱신한다.

- `01-overview-architecture.md`: 최종 Embedding 모델
- `06-delivery-plan.md`: 구현 전 결정사항과 Phase 0 완료 상태
- `07-technical-specification.md`: 모델, 차원, 전처리와 환경변수
- PostgreSQL Migration: `vector(EMBEDDING_DIMENSION)`을 실제 숫자로 고정

## 10. 2026-08-10 Keyword·RRF·지연시간 개선 평가

### 10.1 수정 전 문제

- `plainto_tsquery('simple', 전체 한국어 질문)`이 모든 Case에서 결과를 반환하지 않아 Keyword Hit@1·3·5가 0%였다.
- Keyword 결과가 비어 있어 기존 RRF는 Dense 결과를 그대로 반환했으며 하이브리드 검색을 검증하지 못했다.
- 검색마다 `docker exec`와 `psql`을 새로 실행해 DB 검색 p95에 프로세스 시작 시간이 포함됐다.
- 최초 Trigram RRF 재평가에서는 Dense와 Trigram 순위가 반대인 동점 결과를 Chunk ID로 정렬해 1건이 악화됐다.

### 10.2 적용한 개선

1. 회의명과 본문을 소문자화하고 특수문자·중복 공백을 제거한 `search_text`를 저장한다.
2. `pg_trgm` GiST Index와 최소 유사도 0.05를 사용하는 Keyword Top-20 검색을 추가한다.
3. 운영 후보 RRF는 `HNSW + pg_trgm` 순위를 결합한다.
4. RRF 점수가 같으면 Chunk ID가 아니라 HNSW 순위를 우선해 의미 검색의 기존 정답 순위를 보존한다.
5. `psycopg2` 연결 하나를 재사용하고 DB 워밍업 10회 이후 각 SQL 왕복시간을 측정한다.
6. FTS·Trigram·Dense·HNSW·RRF 각각의 Hit, MRR, nDCG, 결과 없음 비율과 질문 유형별 지표를 기록한다.

변경 파일은 다음과 같다.

- `embedding-evaluation/run_postgres_eval.py`: Trigram, RRF 동점 처리, 지속 연결, 세부 지표와 지연 측정
- `embedding-evaluation/sql/001_pgvector_eval.sql`: `search_text`와 `gist_trgm_ops` Index
- `embedding-evaluation/tests/test_runner.py`: 정규화, nDCG, RRF 동점 처리 검사
- `embedding-evaluation/requirements.txt`: PostgreSQL Driver 고정

### 10.3 평가 수행 조건

- 모델: `openai/text-embedding-3-small`, 1536차원
- 환경: PostgreSQL 16.14, pgvector 0.8.2, pg_trgm 1.6
- 데이터: 비식별 합성 회의 Chunk 32개, 답변 가능 질문 20개
- Vector·Keyword Top-K: 20
- RRF 상수: 60
- Trigram 최소 유사도: 0.05
- DB 워밍업: 10회
- 최종 결과: [전체 지표](../embedding-evaluation/results/postgres-metrics-20260810-161539.json), [Case 요약](../embedding-evaluation/results/postgres-summary-20260810-161539.csv), [상세 결과](../embedding-evaluation/results/postgres-run-20260810-161539.jsonl)

### 10.4 최종 평가 결과

| 검색 방식 | Hit@1 | Hit@3 | Hit@5 | MRR | nDCG@10 | 결과 없음 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dense 정확 검색 | 80% | 100% | 100% | 0.900 | 0.9262 | 0% |
| `simple` FTS 기준선 | 0% | 0% | 0% | 0.000 | 0.0000 | 100% |
| `pg_trgm` | 80% | 90% | 90% | 0.850 | 0.8631 | 10% |
| HNSW | 80% | 100% | 100% | 0.900 | 0.9262 | 0% |
| HNSW + Trigram RRF | **85%** | **100%** | **100%** | **0.925** | **0.9446** | **0%** |

RRF는 HNSW 대비 1개 Case를 개선하고 19개는 유지했으며 악화한 Case는 없다. 개선된 `retrieval-018`은 서버 재시작 절차가 HNSW 2위에서 Trigram 1위 근거를 받아 RRF 1위가 됐다.

질문 유형별 RRF Hit@1은 정확 용어 100%, 의미 재표현 100%, Action Item 75%, 한영 혼합 용어 50%다. Trigram은 혼합 용어 4건 중 2건에서 결과가 없어 이 유형은 Dense에 의존했다.

### 10.5 지연시간 결과

| 구간 | p50 | p95 |
| --- | ---: | ---: |
| Query Embedding API | 1,124.5ms | 1,202.6ms |
| Dense 정확 DB | 52.049ms | 58.399ms |
| `simple` FTS DB | 4.096ms | 5.302ms |
| Trigram DB | 4.622ms | 8.120ms |
| HNSW DB | 52.307ms | 56.807ms |
| HNSW + Trigram 순차 실행 | 56.079ms | 62.429ms |

이전 HNSW p95 270.3ms와 Dense p95 318.7ms는 `docker exec`와 `psql` 시작 비용을 포함한 값이었다. 지속 연결로 다시 측정한 결과 Hybrid DB p95는 62.429ms로 300ms 기준을 통과했다. Query Embedding API p95는 1,202.6ms로 권장 1초를 통과하지 못해 전체 지연의 주된 병목이다.

### 10.6 결론과 다음 개선사항

이 절의 결론은 Chunk 32개 Pilot에 대한 판단이며, 아래 1,000 Chunk 확장 평가 결과가 검색 경로 선택을 대체한다.

- 32개 Chunk Pilot 당시에는 pgvector HNSW와 `HNSW + pg_trgm RRF`를 개발 단계 후보로 판단했다.
- Pilot에서는 하이브리드 Hit@3 100%, HNSW Recall@5 100%, DB p95 62.429ms로 품질·DB 기준을 통과했다.
- `simple` FTS는 운영 검색에서 사용하지 않고 실패 비교 기준선으로만 유지한다.
- 한영 혼합 용어는 Trigram 결과 없음 비율이 50%이므로 빌드명·버전·이슈 ID의 정확 Token 검색을 추가해 별도 검증한다.
- 이 결과는 답변 가능 합성 질문 20개와 Chunk 32개에 한정되므로 당시에는 확장 평가 전 최종 운영 확정으로 보지 않았다.
- Trigram 임계값은 현재 평가 Case에 맞춰 추가 조정하지 않는다. 별도 튜닝 Set과 최종 평가 Set을 분리한 뒤 조정한다.
- Embedding API 지연은 반복 측정과 Timeout·Retry 정책을 검증하고, 동일 질문 Vector 캐시가 필요한지는 실제 중복률을 측정한 뒤 결정한다.

## 11. 2026-08-10 합성 확장 평가

### 11.1 목적과 데이터

작은 Pilot에서 확인하지 못한 대규모 방해 문맥, 답변 불가 질문, HNSW Recall 손실을 검증했다. 실제 비식별 회의록이 아직 없으므로 다음 합성 데이터로 수행했으며 실제 데이터 평가와 구분한다.

- Corpus: 1,000 Chunk
  - 기존 Pilot Chunk 32개
  - 신규 정답 Chunk 30개와 유사 오답 Chunk 30개
  - 템플릿 기반 방해 Chunk 908개
- 질문: 60개
  - 답변 가능 50개
  - 답변 불가 10개
- 유형: 정확 용어 11, 의미 재표현 17, 한영 혼합 10, Action Item 8, Metadata Filter 4, 답변 불가 10
- 생성기: `embedding-evaluation/generate_expanded_dataset.py`
- 데이터: `corpus/expanded_meeting_chunks.jsonl`, `cases/expanded_cases.jsonl`
- Document Embedding Batch: 100개

### 11.2 평가기 확장

- 답변 가능 질문만 Hit·MRR·nDCG 검색 품질에 포함한다.
- 답변 불가 질문은 HNSW가 아닌 Dense 정확 검색 최고 Cosine 점수로 답변 여부를 판정한다.
- 사전 임계값은 0.45로 고정하고 0.35~0.60 Sweep은 사후 분석값으로만 기록한다.
- 오탐률과 잘못된 답변 거절률을 분리한다.
- `Dense 정확 검색 + Trigram RRF`와 `HNSW + Trigram RRF`를 함께 비교한다.
- HNSW는 `ef_search=200`, `iterative_scan=strict_order`를 적용한다.

### 11.3 HNSW 조정 이력

첫 확장 실행은 기본 `ef_search=40`에서 HNSW Recall@5가 68.8%로 떨어졌다. [첫 결과](../embedding-evaluation/results/postgres-metrics-20260810-162708.json)

`ef_search=200`과 `strict_order`를 적용하자 Recall@5가 88~89.6%로 회복됐지만 최소 기준 95%에는 도달하지 못했다. 인덱스를 다시 생성한 반복 실행에서도 근사 순위가 조금 달라져 운영 검색 경로로 확정하지 않았다. [조정 결과](../embedding-evaluation/results/postgres-metrics-20260810-163055.json)

### 11.4 최종 결과

최종 결과 파일은 [전체 지표](../embedding-evaluation/results/postgres-metrics-20260810-163701.json), [Case 요약](../embedding-evaluation/results/postgres-summary-20260810-163701.csv), [상세 결과](../embedding-evaluation/results/postgres-run-20260810-163701.jsonl)이다.

| 검색 방식 | Hit@1 | Hit@3 | Hit@5 | MRR | nDCG@10 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Dense 정확 검색 | 84% | 92% | 96% | 0.8922 | 0.9137 |
| Trigram | 86% | 96% | 96% | 0.9033 | 0.9179 |
| Dense 정확 + Trigram RRF | **90%** | **98%** | **98%** | **0.9367** | **0.9479** |
| HNSW | 72% | 80% | 84% | 0.7700 | 0.7877 |
| HNSW + Trigram RRF | 78% | 94% | 94% | 0.8624 | 0.8917 |

Dense 정확 + Trigram RRF는 Dense 대비 4건을 개선하고 46건을 유지했으며 악화한 Case는 없다. 유일한 Top-5 실패는 `retrieval-009`로, 영어 `Low-end device/shadow quality` 질문과 한국어 저사양 그림자 원문이 Trigram과 Dense Top-20 모두에서 누락됐다.

질문 유형별 Dense 정확 + Trigram RRF Hit@1·3은 다음과 같다.

| 유형 | Hit@1 | Hit@3 |
| --- | ---: | ---: |
| Action Item | 87.5% | 100% |
| 정확 용어 | 90.9% | 100% |
| Metadata Filter | 100% | 100% |
| 한영 혼합 용어 | 80% | 90% |
| 의미 재표현 | 94.1% | 100% |

### 11.5 답변 불가 판정

Dense 최고 점수 임계값 0.45 결과는 다음과 같다.

- 답변 불가 오탐: 0/10, 0%
- 답변 가능 질문의 잘못된 거절: 8/50, 16%
- 전체 정확도: 86.7%

임계값 0.40은 정상 질문 거절률을 6%로 낮추지만 오탐률이 30%가 된다. 0.35~0.60 범위에서 오탐률과 정상 질문 거절률을 동시에 10% 이하로 만족하는 임계값은 없었다. 답변 가능 점수는 최저 0.301, 답변 불가 점수는 최고 0.443으로 겹치므로 단일 Cosine 임계값만으로 답변 여부를 확정하지 않는다.

### 11.6 지연시간과 비용 신호

| 구간 | p50 | p95 |
| --- | ---: | ---: |
| Query Embedding API | 1,086.7ms | 1,218.5ms |
| Dense 정확 DB | 68.737ms | 95.167ms |
| Trigram DB | 3.060ms | 5.127ms |
| Dense 정확 + Trigram 순차 실행 | 72.999ms | 97.924ms |
| HNSW DB | 53.102ms | 64.689ms |
| HNSW + Trigram 순차 실행 | 55.719ms | 67.075ms |

HNSW가 정확 검색보다 약 30ms 빠르지만 Recall 손실이 10.4%p라 품질 기준을 통과하지 못했다. Dense 정확 + Trigram도 DB p95 97.924ms로 300ms 기준을 충분히 통과하므로 현재 규모에서는 정확 검색을 선택한다.

문서 1,000개 Embedding에는 46,596 Token이 사용됐다. 같은 데이터의 Batch 생성시간은 실행별 약 33.5초, 35.4초, 157.1초로 Provider 변동이 컸으며, Query Embedding p95도 권장 1초를 통과하지 못했다.

### 11.7 결정과 다음 단계

- 1,000 Chunk 이하 개발 환경의 검색 경로는 `Dense 정확 검색 + pg_trgm RRF`로 결정한다.
- HNSW Index는 Migration 가능 상태로 유지하되 검색 경로에는 사용하지 않는다.
- HNSW는 실제 Corpus가 정확 검색의 300ms 기준을 넘을 때 `ef_search`, Index 생성 옵션과 Recall을 다시 평가한다.
- 단일 Cosine 임계값은 답변 불가 최종 판정에 사용하지 않는다. 검색된 근거의 직접 포함 여부, Reranker 또는 LLM Groundedness 검증을 별도 평가한다.
- `retrieval-009` 유형을 위해 한영 용어 사전 또는 정확 Token 검색을 추가하되 별도 튜닝·최종 평가 Set으로 검증한다.
- 이번 데이터는 합성 방해 Chunk가 반복되는 한계가 있으므로 실제 비식별 회의록과 사람이 확정한 질문 60개로 최종 재평가한다.

## 12. 2026-08-10 한영 혼합 용어 Holdout 평가

### 12.1 목적과 조건

확장 평가에서 유일하게 Top-5에서 누락된 `Low-end device/shadow quality` 유형을 일반화해 한영 혼합 용어 검색을 별도로 평가했다.

- Corpus: 기존 합성 확장 1,000 Chunk
- Holdout 질문: 20개
- 대상 용어: 저사양·그림자 품질, Matchmaking·Rollout, Frame Pacing, Hotfix·Resource Bundle, MMR Decay, Shader Cache, CDN Purge, Telemetry, Save File, Voice Chat
- Case: `cases/lexical_holdout_cases.jsonl`
- 평가기: `run_lexical_eval.py`
- Embedding API 호출과 DB 변경 없이 `pg_trgm` 검색만 비교

한영 Alias는 Query를 한국어 게임 개발 용어로 변환해 별도 Trigram 후보를 생성한다. 원본 Query와 Alias Query의 점수는 직접 합산하지 않는다.

### 12.2 결합 방식 검토 이력

첫 번째 방식은 원본과 Alias 결과의 최대 Trigram 점수를 사용했다. Hit@1 85%, Hit@3·5 100%로 높았지만 `emergency patch asset bundle` Case가 1위에서 3위로 악화됐다. [결과](../embedding-evaluation/results/lexical-metrics-20260810-164925.json)

두 번째 방식은 두 순위를 RRF로 결합했다. 낮은 점수의 원본 오답까지 순위 신호가 되어 Hit@1이 60%로 하락하고 1건이 악화됐다. [결과](../embedding-evaluation/results/lexical-metrics-20260810-165018.json)

최종 방식은 원본 Trigram 순서를 변경하지 않고 Alias에서만 발견한 후보를 뒤에 추가한다. 기존 정답 순위를 떨어뜨리지 않는 안전한 후보 확장 방식이다.

### 12.3 최종 결과

최종 결과는 [전체 지표](../embedding-evaluation/results/lexical-metrics-20260810-165152.json)와 [상세 결과](../embedding-evaluation/results/lexical-run-20260810-165152.jsonl)에 저장했다.

| 방식 | Hit@1 | Hit@3 | Hit@5 | MRR | p95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 원본 Trigram | 65% | 65% | 75% | 0.6750 | 2.095ms |
| 원본 순위 보존 + Alias 후보 | 65% | **85%** | **100%** | **0.7708** | 3.402ms |

- 개선 5건
- 유지 15건
- 악화 0건
- 추가 지연 1.307ms

### 12.4 판단과 다음 단계

- 한영 Alias는 최종 순위 결정기가 아니라 Candidate Recall을 높이는 선택적 후보 확장으로만 사용한다.
- 운영 `query_trigram` 기본값은 Alias 미사용으로 유지한다.
- Alias 후보는 향후 Dense 결과와 함께 Reranker에 전달하고, Reranker가 원문 근거 일치도를 판단하도록 평가한다.
- 현재 용어 사전은 합성 Holdout을 기반으로 하므로 실제 팀 문서의 빌드명·시스템명·약어를 수집한 뒤 별도 Version으로 관리한다.
- 답변 불가 판정과 Alias 후보 순위 결정을 결합한 Reranker 평가는 아래 13절에서 수행했다. 실제 비식별 회의록이 확보되면 합성 데이터보다 우선한다.

## 13. 2026-08-10 Reranker·답변 가능성 평가

### 13.1 목적과 조건

단일 Cosine 임계값이 답변 불가 오탐과 정상 질문 거절을 동시에 해결하지 못했고, Alias 후보 확장은 최종 순서를 결정하지 않았다. 이에 현재 확정 LLM인 `openai/gpt-4.1-mini`가 검색 후보 원문만 보고 다음 두 작업을 수행할 수 있는지 평가했다.

1. 질문을 직접 뒷받침하는 후보가 있는지 판단
2. 답변 가능하면 직접 근거가 강한 순서로 Chunk ID 재정렬

- 평가기: `run_reranker_eval.py`
- 확장 Set: 합성 1,000 Chunk 검색 결과의 60 Case(답변 가능 50, 답변 불가 10)
- Alias Holdout: 한영 혼합 질문 20 Case
- 전체: 80 Case, 답변 가능 70, 답변 불가 10
- 후보: 확장 Set의 Dense 정확+Trigram RRF Top-5와 Holdout의 안전한 Alias 확장 Top-5
- 제약: 후보에 없는 ID 생성 금지, 답변 불가이면 빈 배열, Schema·의미 오류 시 한 번만 재요청
- 재사용: 저장된 검색 결과와 Corpus를 사용해 Embedding API와 PostgreSQL을 다시 호출하지 않음

### 13.2 최초 평가와 수정

[최초 전체 결과](../embedding-evaluation/results/reranker-metrics-20260810-170526.json)는 다음과 같았다.

- 전체 Reranker Hit@1 94.29%, Hit@3·5 95.71%
- 답변 불가 오탐 0/10
- 정상 질문 거절 3/70
- Provider 오류 0건

정상 거절 3건 중 `retrieval-009`는 정답 Chunk가 Top-5 후보에 없는 검색 실패였다. 나머지 `retrieval-016`, `retrieval-046`은 후보에 명시적 근거가 있었지만, 프롬프트가 여러 Chunk의 공동 근거와 후속업무 실행 문장을 충분히 설명하지 않아 Reranker가 잘못 거절했다.

프롬프트에 두 판단 규칙을 명시하고 [오판 2건을 먼저 재검증](../embedding-evaluation/results/reranker-metrics-20260810-170703.json)했다. 두 Case 모두 답변 가능 판정과 정답 Top-1을 회복한 뒤 전체를 같은 조건으로 다시 평가했다. 최초 결과는 삭제하지 않았다.

### 13.3 최종 결과

최종 결과는 [전체 지표](../embedding-evaluation/results/reranker-metrics-20260810-170901.json), [Case 요약](../embedding-evaluation/results/reranker-summary-20260810-170901.csv), [상세 결과](../embedding-evaluation/results/reranker-run-20260810-170901.jsonl)에 저장했다.

| 평가 Set | 방식 | Hit@1 | Hit@3 | Hit@5 | MRR |
| --- | --- | ---: | ---: | ---: | ---: |
| 전체 70개 답변 가능 | 기존 후보 순서 | 82.86% | 94.29% | 98.57% | 0.8893 |
| 전체 70개 답변 가능 | Reranker | **97.14%** | **98.57%** | **98.57%** | **0.9786** |
| 확장 Set 50개 | 기존 RRF | 90% | 98% | 98% | 0.9367 |
| 확장 Set 50개 | Reranker | **96%** | 98% | 98% | **0.9700** |
| Alias Holdout 20개 | Alias 후보 | 65% | 85% | 100% | 0.7708 |
| Alias Holdout 20개 | Reranker | **100%** | **100%** | 100% | **1.0000** |

- 후보 Recall: 69/70, 98.57%
- 순위 변화: 개선 11건, 유지 58건, 악화 0건, 검색 후보 누락 1건
- 전체 답변 불가 오탐: 0/10, 0%
- 전체 정상 질문 거절: 1/70, 1.43%
- 검색 후보 누락을 제외한 Reranker 판단: 79/79, 100%
- Provider 오류: 0/80
- 지연시간: p50 1,109.3ms, p95 2,639.5ms
- 사용량: 입력 38,245 Token, 출력 1,420 Token

### 13.4 판단과 다음 단계

- Reranker는 검색 후보가 존재할 때 답변 불가 오탐과 정상 질문 거절 기준을 모두 통과했고, 특히 Alias 후보의 Top-1을 65%에서 100%로 개선했다.
- 최종 실패 `retrieval-009`는 Reranker 문제가 아니라 기존 확장 검색 결과에 Alias 후보가 결합되지 않은 Candidate Recall 문제다.
- Reranker p95 2.64초가 Query Embedding과 DB 검색 뒤에 추가되므로 즉시 모든 검색에 항상 적용하는 운영 결정은 보류한다.
- 다음에는 실제 비식별 회의록과 사람이 확정한 질문 60개로 품질을 재검증하고, Reranker 상시 적용과 불확실한 Case에만 적용하는 조건부 호출의 지연·품질을 비교한다.
- 실제 데이터 확보 전에는 이번 합성 결과를 최종 운영 확정으로 보지 않는다.

## 14. 2026-08-10 실제 회의록 60 Case 평가

### 14.1 데이터와 호환 처리

사용자가 제공한 실제 회의록과 질문을 기존 검색·Reranker 평가 경로에 연결했다.

- Corpus: [real_meeting_chunks.jsonl](../embedding-evaluation/corpus/real_meeting_chunks.jsonl), 5개 Chunk·3개 회의
- Case: [real_cases_60.jsonl](../embedding-evaluation/cases/real_cases_60.jsonl), 60개(답변 가능 50, 답변 불가 10)
- 유형: exact 15, semantic paraphrase 15, 한영 혼합 10, metadata filter 10, unanswerable 10
- 표준화: `chunk_id/title/created_at/participants`를 `meeting_chunk_id/meeting_title/meeting_date/participant_user_ids`로 입력 경계에서 변환
- 모델: `openai/text-embedding-3-small`, 1536차원

`date_to`는 기존 계약과 PostgreSQL 조건에 따라 미만(Exclusive)이다. 기존 `retrieval-043`, `retrieval-044`, `retrieval-045`가 같은 날짜를 `date_to`에 넣어 검색 결과가 비었던 문제를 확인해 각각 다음 날짜로 수정했다. 이제 하루 범위는 `[date_from, 다음 날 00:00)`으로 평가한다.

### 14.2 PostgreSQL 검색 결과

보정 후 결과: [전체 지표](../embedding-evaluation/results/postgres-metrics-20260810-173735.json), [Case 요약](../embedding-evaluation/results/postgres-summary-20260810-173735.csv), [상세 결과](../embedding-evaluation/results/postgres-run-20260810-173735.jsonl)

| 방식 | Hit@1 | Hit@3 | Hit@5 | MRR |
| --- | ---: | ---: | ---: | ---: |
| Dense 정확 검색 | 94% | 100% | 100% | 0.9667 |
| Trigram | 68% | 68% | 68% | 0.6800 |
| Dense 정확 + Trigram RRF | **94%** | **100%** | **100%** | **0.9667** |
| HNSW + Trigram RRF | 94% | 100% | 100% | 0.9667 |

- HNSW Recall@5: 100% (5개 Chunk 규모)
- DB Hybrid p95: 63.378ms
- Query Embedding API p95: 1,191.6ms
- `simple` FTS: 한국어 검색 결과 0건
- Metadata Filter Hit@1: 70%, Hit@3: 100%
- Cosine 0.45 답변 불가 판정: 오탐 0%, 정상 질문 거절 56%

### 14.3 실제 회의록 Reranker 결과

보정 후 결과: [전체 지표](../embedding-evaluation/results/reranker-metrics-20260810-173859.json), [Case 요약](../embedding-evaluation/results/reranker-summary-20260810-173859.csv), [상세 결과](../embedding-evaluation/results/reranker-run-20260810-173859.jsonl)

검색 결과의 RRF Top-5를 `openai/gpt-4.1-mini`에 전달했다. Reranker 입력에는 질문, 검색 필터, 회의 ID·일자·참여자 메타데이터와 Chunk 원문을 포함했다.

- 후보 Recall: 50/50, 100%
- 기존 RRF: Hit@1 94%, Hit@3·5 100%, MRR 0.9667
- Reranker: Hit@1·3·5 98%, MRR 0.9800
- 순위 변화: 개선 3건, 유지 46건, 악화 1건, 검색 후보 누락 0건
- 답변 불가 오탐: 0/10, 0%
- 정상 질문 거절: 1/50, 2%
- 검색 후보가 존재한 50건에서 정상 질문 거절: 1건(2%)
- Reranker 지연: p50 1,161.1ms, p95 1,650.5ms
- Provider 오류: 0/60

`retrieval-046`은 참여자 메타데이터를 Reranker 입력에 포함한 뒤 3위에서 1위로 개선됐다. `retrieval-028`은 기존 검색 1위 후보가 있었지만 “새벽에 서버 닫고”라는 표현을 원문의 정기 점검으로 충분히 연결하지 못해 Reranker가 거절했다. `retrieval-043/044/045`는 날짜 범위 보정 후 후보가 정상적으로 검색됐다.

### 14.4 판단과 다음 단계

- 실제 회의록에서도 Dense 정확 + Trigram RRF는 검색 Hit@3 100%로 기준 80%를 통과했다.
- 단일 Cosine 임계값은 실제 데이터에서도 정상 질문을 과도하게 거절하므로 사용하지 않는다.
- Reranker는 답변 불가 오탐 0%, 정상 질문 거절 2%로 기준을 통과했다. 단, `retrieval-028` 의미 재표현 1건은 여전히 거절했다.
- Reranker는 현재 검색에 항상 적용하지 않고, 후보 간 점수 차이가 작거나 Metadata Filter 질문인 경우 조건부로 호출하는 방식을 우선 검토한다.
- 날짜 범위 Case 3건은 보정 후 재평가를 완료했다. 실제 회의록 Chunk를 60개 이상으로 확장해 대표성을 높인 뒤 최종 운영 확정한다.
- 이번 결과는 실제 제공 데이터 5개 Chunk에 대한 평가이며, 최종 운영 확정 전 데이터 규모 확장이 필요하다.

## 15. 2026-08-11 최신 실제 회의록 64 Chunk·60 Case 재평가

### 15.1 평가 입력과 검증

- Corpus: `embedding-evaluation/corpus/real_meeting_chunks.jsonl` (64개 Chunk, 61개 회의)
- Case: `embedding-evaluation/cases/real_cases_60.jsonl` (60개, 답변 가능 56개·불가 4개)
- 모든 JSONL 행, Case ID·Chunk ID 유일성, 정답 Chunk 존재 여부, 날짜 범위를 사전 검증했다.
- 모델: `openai/text-embedding-3-small` (1536차원)
- DB: PostgreSQL 16.14, pgvector 0.8.2, pg_trgm 1.6
- Reranker: `openai/gpt-4.1-mini` (`OPENAI_BASE_URL2`)

### 15.2 검색 결과

결과 파일: [postgres-metrics-20260811-101253.json](../embedding-evaluation/results/postgres-metrics-20260811-101253.json), [postgres-summary-20260811-101253.csv](../embedding-evaluation/results/postgres-summary-20260811-101253.csv), [postgres-run-20260811-101253.jsonl](../embedding-evaluation/results/postgres-run-20260811-101253.jsonl)

| 방식 | Hit@1 | Hit@3 | Hit@5 | MRR |
| --- | ---: | ---: | ---: | ---: |
| Dense 정확 검색 | 73.21% | 96.43% | 100% | 0.8482 |
| Trigram | 92.86% | 94.64% | 94.64% | 0.9375 |
| Dense + Trigram RRF | **96.43%** | **98.21%** | **100%** | **0.9777** |
| HNSW + Trigram RRF | **96.43%** | **98.21%** | **100%** | **0.9777** |

- HNSW Recall@5는 정확 검색 대비 100%였고 Index Scan을 확인했다.
- Hybrid DB p95는 66.3ms, Query Embedding API p95는 893.1ms였다.
- 단일 Cosine 0.45 기준은 정상 질문 23건을 거절(오탐 41.07%)해 운영 기준으로 사용하지 않는다.

### 15.3 Reranker 결과

결과 파일: [reranker-metrics-20260811-101533.json](../embedding-evaluation/results/reranker-metrics-20260811-101533.json), [reranker-summary-20260811-101533.csv](../embedding-evaluation/results/reranker-summary-20260811-101533.csv), [reranker-run-20260811-101533.jsonl](../embedding-evaluation/results/reranker-run-20260811-101533.jsonl)

- 후보 Recall: 100% (검색 후보에 정답이 없는 Case 0건)
- RRF 기준(답변 가능 56건): Hit@1 96.43%, Hit@3 98.21%, Hit@5 100%, MRR 0.9777
- Reranker: Hit@1·3·5 94.64%, MRR 0.9464
- 순위 변화: 개선 1건(`retrieval-011`), 유지 52건, 악화 3건(`retrieval-009/047/048`)
- 답변 불가 오탐: 0/4, 정상 질문 거절: 3/56 (5.36%), 정확도 95%
- Provider 오류: 0/60
- Reranker 지연: p50 1,088ms, p95 1,406.7ms

이번 데이터에서는 Reranker가 RRF 순위를 개선하지 못하고 오히려 3건 악화했으므로 전체 검색에 상시 적용하지 않는다. 후보 점수 차이가 작거나 질의가 복잡한 경우에만 조건부로 호출하고, 호출 전 RRF 결과를 보존한다.

### 15.4 운영 채택 판단

- Dense+Trigram RRF와 HNSW는 품질(Hit@3 98.21%)·지연 기준을 통과했다.
- Reranker는 답변 가능성 판정 정확도 95%지만 순위 품질과 지연이 RRF보다 낮아 기본 경로로 채택하지 않는다.
- 운영 전 필수 후속: 지속 연결 방식의 실제 DB p95 재측정, 더 다양한 회의·질의로 회귀 평가, Reranker 조건부 호출 기준 확정, 모니터링과 실패 시 RRF fallback 구현.

### 15.5 답변 가능성 운영 Workflow

단일 Cosine 임계값으로 답변 가능 여부를 판정하지 않는다. 검색과 근거 충분성 판정을 다음처럼 분리한다.

```text
요청 범위·Metadata 필터
→ Dense + Trigram 후보 검색
→ RRF Top-K
→ 필터·Chunk ID·직접 근거 검증
→ 필요할 때만 Reranker/groundedness
→ 근거 답변 또는 insufficient_evidence
```

- RRF는 후보 검색과 기본 순위에 사용한다.
- Reranker는 점수 차이가 작거나 다중 Chunk·Metadata 질문일 때만 호출한다.
- Reranker는 검색 후보 ID만 재정렬하며 새 근거·출처를 생성하지 않는다.
- Reranker 장애·Timeout 시 RRF 결과와 `warnings`를 반환한다.
- 답변은 검증된 Chunk에서만 생성하고, 근거가 부족하면 답변을 추정하지 않는다.
- `abstain_score=0.45`는 평가용 진단 지표로만 유지하며 운영 답변 거절 조건으로 사용하지 않는다.

이 Workflow의 실제 구현·출처 검증·부분 실패 Contract Test는 M4.4에서 완료한다.
