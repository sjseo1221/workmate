# M0.2-02 검수 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: Embedding 평가 승인
- 담당자: Codex
- 검수자: 사용자 승인
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-114046
- 코드 버전: `e2de4be`
- 입력 데이터 버전: 실제 비식별 회의록 64 Chunk·60 Case, 2026-08-11 평가 원본

## 2. 최신 실행과 승인

- latest_run_id: 20260813-114046
- latest_run_status: PASS_WITH_CAVEAT (사용자 승인)
- latest_approved_run_id: 20260813-114046
- approved_at: 2026-08-13 11:53 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: Embedding 모델·1536차원·거리 함수·Dense+Trigram RRF·HNSW 결과를 검토하고 운영 검색 후보를 승인한다.
- 완료 기준: Hybrid Hit@3 80% 이상, HNSW Recall@5 90% 이상 권장, DB 검색 p95 300ms 이하, 모델과 `vector(1536)` Migration 호환.
- 백로그 범위: M0.2-02
- 미완료·보류 백로그: 없음. 답변 가능성 거절률은 승인된 운영 정책에 따라 최종 판정에서 제외

## 4. 구현 경로

- 구현 코드: [run_eval.py](../../../../../../embedding-evaluation/run_eval.py), [run_postgres_eval.py](../../../../../../embedding-evaluation/run_postgres_eval.py)
- Schema 또는 Migration: [Embedding 평가 계획](../../../../../../docs/10-embedding-evaluation-plan.md), [구현·검증 가이드](../../../../../../docs/12-implementation-verification-guide.md)
- UI 코드: 해당 없음

## 5. 테스트 파일 경로

- 단위 테스트: [test_runner.py](../../../../../../embedding-evaluation/tests/test_runner.py)
- 통합 테스트 지표: [postgres-metrics-20260811-101253.json](../../../../../../embedding-evaluation/results/postgres-metrics-20260811-101253.json)
- UI 테스트: 해당 없음
- Fixture/입력: [real_meeting_chunks.jsonl](../../../../../../embedding-evaluation/corpus/real_meeting_chunks.jsonl), [real_cases_60.jsonl](../../../../../../embedding-evaluation/cases/real_cases_60.jsonl)
- 기대 결과: Hybrid Hit@3 80% 이상, HNSW Recall@5 90% 이상 권장, DB p95 300ms 이하
- 모델 평가 Case: 실제 회의록 60 Case
- 모델 평가 결과: [EVALUATION_HISTORY.md](../../../../../../embedding-evaluation/EVALUATION_HISTORY.md)

## 6. 실행 명령과 결과

```text
python -m unittest discover -s embedding-evaluation/tests -v
python -m py_compile embedding-evaluation/run_eval.py embedding-evaluation/run_postgres_eval.py embedding-evaluation/run_reranker_eval.py
git diff --check
```

- 실행 로그: 단위 테스트 16개 PASS, Python 구문 검사 PASS, `git diff --check` PASS
- API 응답 또는 Artifact: 2026-08-11 실제 PostgreSQL 평가 지표 검토
- 화면 캡처: 해당 없음
- 함수 문서화: 평가기 핵심 함수와 검수 경로 확인

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| `openai/text-embedding-3-small` 출력 차원 1536 | PASS | [metrics](../../../../../../embedding-evaluation/results/postgres-metrics-20260811-101253.json) |
| Hybrid Hit@3 80% 이상 | PASS (98.21%) | [metrics](../../../../../../embedding-evaluation/results/postgres-metrics-20260811-101253.json) |
| HNSW Recall@5 90% 이상 권장 | PASS (100%) | [metrics](../../../../../../embedding-evaluation/results/postgres-metrics-20260811-101253.json) |
| Hybrid DB 검색 p95 300ms 이하 | PASS (66.3ms) | [metrics](../../../../../../embedding-evaluation/results/postgres-metrics-20260811-101253.json) |
| Query Embedding p95 1초 권장 | PASS (893.1ms) | [metrics](../../../../../../embedding-evaluation/results/postgres-metrics-20260811-101253.json) |
| 답변 가능성 잘못된 거절률 10% 이하 권장 | FAIL (41.07%) | 운영 답변 가능성 판정에는 사용하지 않음 |
| 모델·검색 조합 운영 승인 | PASS (사용자 승인) | 이 결과와 `docs/06-delivery-plan.md` M0.2-02 |

## 8. 문제와 수정 이력

- 발견된 문제: Cosine 0.45 단일 임계값에서 정상 질문 56건 중 23건을 거절했다.
- 원인: Embedding 유사도 하나를 답변 가능성 판정으로 사용하면 정상적인 의미 재표현을 과도하게 거절한다.
- 수정 내용: 운영 검색 후보는 Hybrid RRF로 사용하고, 단일 Cosine 임계값은 평가용 진단 지표로만 유지한다. `RRF Top-K → metadata·직접 근거 검증 → 조건부 Reranker/groundedness → 답변 또는 insufficient_evidence` Workflow와 Reranker 장애·Timeout 시 RRF fallback·`warnings` 정책을 문서에 반영했다. 실제 검색 코드와 Contract Test는 M4.4에서 구현한다.
- 재검수 실행 ID: 20260813-114046 (사용자 승인 반영)

## 9. 최종 판단

- 승인 여부: 승인
- 검수 의견: 사용자가 `openai/text-embedding-3-small`, `vector(1536)`, Cosine, Dense+Trigram RRF+HNSW 조합과 단일 Cosine 임계값을 운영 거절 조건으로 사용하지 않는 방침을 승인했다.
- 다음 조치: M0.2-03 STT 평가 승인
