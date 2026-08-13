# M0.2-02 재검수 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: Embedding 평가 범위 재정리 및 재검수
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-134129
- 코드 버전: `483809b`
- 입력 데이터 버전: 실제 비식별 회의록 64 Chunk·60 Case, 2026-08-11 평가 원본

## 2. 최신 실행과 승인

- latest_run_id: 20260813-134129
- latest_run_status: PASS
- latest_approved_run_id: 20260813-134129
- approved_at: 2026-08-13 13:41 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: M0.2에서 모델·차원·검색 품질·HNSW·지연 기준만 확정하고, 답변 가능성 판정은 M4.4 범위로 분리한다.
- 완료 기준:
  - `openai/text-embedding-3-small` 출력 차원 1536
  - Hybrid Hit@3 80% 이상
  - HNSW Recall@5 90% 이상 권장
  - Hybrid DB 검색 p95 300ms 이하
  - Query Embedding p95 1초 이하 권장
  - 단위 테스트·구문 검사·문서 diff 검사가 모두 성공
- 백로그 범위: M0.2-02
- 미완료 백로그: 없음
- 후속 범위: 답변 가능성·Reranker·근거 부족 처리는 M4.4에서 별도 검증

## 4. 구현·설계 경로

- 평가기: [`run_eval.py`](../../../../../../embedding-evaluation/run_eval.py), [`run_postgres_eval.py`](../../../../../../embedding-evaluation/run_postgres_eval.py), [`run_reranker_eval.py`](../../../../../../embedding-evaluation/run_reranker_eval.py)
- 테스트: [`test_runner.py`](../../../../../../embedding-evaluation/tests/test_runner.py)
- 평가 계획: [`10-embedding-evaluation-plan.md`](../../../../../10-embedding-evaluation-plan.md)
- 후속 구현 기준: [`06-delivery-plan.md`](../../../../../06-delivery-plan.md)의 M4.4
- Schema·Migration·UI: 해당 없음

이번 재검수에서 단일 Cosine 임계값은 운영 답변 거절 조건으로 사용하지 않는다는 범위를 확정했다. 기존 41.07% 오거절 지표는 삭제하지 않고 진단·후속 M4.4 평가 대상으로 유지한다.

## 5. 실행 명령과 결과

```text
python -m unittest discover -s embedding-evaluation/tests -v
python -m py_compile embedding-evaluation/run_eval.py embedding-evaluation/run_postgres_eval.py embedding-evaluation/run_reranker_eval.py
git diff --check
```

- 단위 테스트: 16개 모두 `PASS`
- Python 구문 검사: `PASS`
- `git diff --check`: `PASS`
- 기존 실제 평가 지표: Hybrid Hit@3 98.21%, HNSW Recall@5 100%, Hybrid DB p95 66.3ms, Query Embedding p95 893.1ms
- 미실행·경고·수동 검수·차단 항목: 없음

## 6. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Embedding 출력 차원 1536 | PASS | `postgres-metrics-20260811-101253.json` |
| Hybrid Hit@3 80% 이상 | PASS (98.21%) | `postgres-metrics-20260811-101253.json` |
| HNSW Recall@5 90% 이상 권장 | PASS (100%) | `postgres-metrics-20260811-101253.json` |
| Hybrid DB 검색 p95 300ms 이하 | PASS (66.3ms) | `postgres-metrics-20260811-101253.json` |
| Query Embedding p95 1초 이하 권장 | PASS (893.1ms) | `postgres-metrics-20260811-101253.json` |
| 단위 테스트 16개 | PASS | `python -m unittest discover -s embedding-evaluation/tests -v` |
| 구문 검사 | PASS | `python -m py_compile ...` |
| 문서 diff 검사 | PASS | `git diff --check` |
| M0.2 답변 가능성 판정 범위 분리 | PASS | M4.4 후속 범위로 문서화 |

## 7. 문제와 수정 이력

- 이전 평가의 단일 Cosine 답변 가능성 지표는 검색 모델 채택 기준과 다른 업무 판정 지표였다.
- M0.2 완료 기준에서 해당 운영 판정을 분리하고, M4.4의 근거 검증·Reranker·insufficient_evidence Workflow로 이관했다.
- 이전 실행 [`20260813-114046`](../20260813-114046/result.md)은 원본 결과로 보존한다.

## 8. 최종 판단

- 승인 여부: 승인
- 검수 의견: M0.2-02의 모델·검색·성능 기준과 재현성 검증이 모두 정확히 `PASS`이며 자동 승인 조건을 충족했다.
- 다음 조치: M0.2-03 STT 재검수
