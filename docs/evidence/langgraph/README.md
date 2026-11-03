# LangGraph 전면 전환 증빙

전환 계획은 [`docs/30-langgraph-migration-plan.md`](../../30-langgraph-migration-plan.md)를 기준으로 한다.
기존 마일스톤(`Mx.y`) 증빙과 달리 이 작업은 마일스톤 번호가 아닌 **작업 단계(W0~W9)** 단위로 기록한다.

## 단계별 증빙

| 단계 | 내용 | 상태 | 최신 승인 실행 |
| --- | --- | --- | --- |
| W0 | 기준선 채증과 출발점 정리 | 완료 | [`20260923-065508`](W0/runs/20260923-065508/result.md) |
| W1 | 계약 스냅샷 추출 | 진행 | — |
| W2 | State·어댑터·Checkpointer·LLM 골격 | 대기 | — |
| W3 | Skill Subgraph 11개 재작성 | 대기 | — |
| W4 | Root Graph 조립 | 대기 | — |
| W5 | 진입점 교체 | 대기 | — |
| W6 | `interrupt`·공개 계약 개편 | 대기 | — |
| W7 | 레거시 삭제·이동·Migration | 대기 | — |
| W8 | 재시도와 관측 | 대기 | — |
| W9 | 문서·증빙 정리 | 대기 | — |

## 확정된 기준선 (W0)

- 기준 Commit: `workmate-agent@8043c1e` (브랜치 `feat/M0.1-01-sdk-runtime`)
- 테스트: 440 passed / 0 failed / 0 skipped
- 실행 환경: CPython 3.12.13, `uv.lock` 그대로, PostgreSQL 16 + pgvector 테스트 컨테이너
- 테스트 DB: `docker run -d --name workmate-test-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=workmate_test -p 55432:5432 pgvector/pgvector:pg16`

## 확정된 전제와 결정

- 전제: 운영 배포 중이 아니며, 호환보다 LangGraph 설계 정합성을 우선한다(계획서 §0.1).
- 결정: D1=B(공개 계약까지 개편), D2=A(계약 스냅샷 선추출), D3=B(`langchain-openai` 도입),
  D4=A(비-Skill 모듈 이동), D5=A(폴링 유지 + `INPUT_REQUIRED` 분기), D6=B(`a2a_checkpoints` DROP).

## 기록 규칙

- 실행 결과가 생긴 뒤에만 `W{n}/runs/{run_id}/result.md`를 작성한다.
- 승인된 실행만 이 표의 `최신 승인 실행` 열에 연결한다.
- Secret·Token·개인정보는 증빙에 기록하지 않는다.
