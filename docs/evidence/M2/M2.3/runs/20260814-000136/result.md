# M2.3-01 검수 결과

## 1. 기본 정보

- 마일스톤: M2.3 보고서 생성
- 하위 백로그: M2.3-01 주간 보고 입력 조립·LLM 생성 Workflow
- 담당자: Codex
- 검수자: 미정
- 상태: 검수 중
- 실행일: 2026-08-14
- 실행 ID: `20260814-000136`
- 코드 버전: workmate-agent 작업 트리
- 입력 데이터 버전: 테스트 SQLite Fixture

## 2. 최신 실행과 승인

- latest_run_id: `20260814-000136`
- latest_run_status: 코드·대상 테스트 PASS, 전체 회귀 5개 SKIP
- latest_approved_run_id: null
- approved_at: null

## 3. 목표와 완료 기준

- 목표: M2.1의 결정론적 분류와 M2.2의 근거 있는 계획을 입력으로 받아 source-backed weekly report를 생성한다.
- 완료 기준: LLM은 summary만 생성하고 분류·계획 kind·source_refs는 Workflow가 보존한다. Provider 실패 시 고정 Mock으로 대체하지 않고 source-backed 부분 결과와 retryable warning을 반환한다.
- 백로그 범위: M2.3-01
- 미완료·보류 백로그: M2.3-02 Artifact/DataPart·Schema 검증, M2.3-03 Provider 재시도 정책, M2.3-04 통합·회귀 검수

## 4. 구현 경로

- Workflow: [`weekly_report.py`](../../../../../../workmate-agent/app/workflows/weekly_report.py)
- 입력 분류·계획: [`weekly_classification.py`](../../../../../../workmate-agent/app/workflows/weekly_classification.py)
- 런타임 등록: [`runtime.py`](../../../../../../workmate-agent/app/a2a/runtime.py)
- 환경변수 예시: [`.env.example`](../../../../../../workmate-agent/.env.example)
- 핵심 테스트: [`test_weekly_report_generation.py`](../../../../../../workmate-agent/tests/test_weekly_report_generation.py)

## 5. 구현 요약

- 기존 `TaskRepository`를 조회해 사용자 범위의 주간 데이터를 조립하고, 운영 환경에서는 기존 `_repositories()` 규칙에 따라 PostgreSQL을 우선 선택한다.
- M2.2 계획 후보를 허용된 task/source ID와 대조해 근거가 있는 계획만 결과에 포함한다.
- OpenAI 호환 `/chat/completions` 호출을 주입 가능한 `LLMClient`로 감싸고, 응답은 summary 문자열만 반영한다.
- LLM timeout·HTTP 오류·응답 형식 오류는 `LLM_PROVIDER_UNAVAILABLE` warning과 결정론적 source-backed 부분 결과로 반환한다. 운영 응답을 Mock으로 바꾸지 않는다.
- 의도적으로 제외한 범위: A2A `DataPart`·Markdown Artifact 변환 및 공개 Schema 검증(M2.3-02), Provider별 재시도/백오프(M2.3-03), 실제 운영 Provider 통합 검수(M2.3-04).

## 6. 테스트 파일 경로와 결과

### 대상 테스트

```text
.\.venv\Scripts\python.exe -m unittest tests.test_weekly_report_generation tests.test_weekly_plan_grounding tests.test_weekly_source_link tests.test_m2_1_integration tests.test_contract -v
```

- 결과: 23개 PASS, 0 FAIL, 0 SKIP

### 전체 회귀 테스트

```text
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

- 결과: 103개 PASS, 0 FAIL, 5 SKIP
- SKIP 사유: `DATABASE_URL` 미설정으로 PostgreSQL 통합 테스트 5개가 실행되지 않음

### 정적 검사

```text
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

- 결과: PASS

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| M2.1/M2.2 입력을 사용한 보고서 생성 | PASS | `test_weekly_report_generation.py` |
| LLM이 summary 외 결정 필드를 변경하지 않음 | PASS | `test_weekly_report_generation.py` |
| Provider 실패 시 부분 결과·warning 반환 | PASS | `test_weekly_report_generation.py` |
| 전체 회귀·PostgreSQL 경로 | 보류 | 전체 회귀 5개 SKIP (`DATABASE_URL` 미설정) |
| 실제 Provider 운영 호출 | 보류 | M2.3-03/M2.3-04 범위 |

## 8. 문제와 수정 이력

- 발견된 문제: 전체 회귀 테스트에서 PostgreSQL 통합 테스트 5개가 `DATABASE_URL` 미설정으로 SKIP됨.
- 원인: 현재 실행 환경에 PostgreSQL DSN이 주입되지 않음.
- 수정 내용: 보고서 Workflow가 일일 브리핑과 동일한 PostgreSQL 우선 Repository 선택 규칙을 재사용하도록 정리함.
- 재검수 조건: PostgreSQL DSN을 설정한 뒤 전체 회귀를 다시 실행하고, M2.3-02~04 검수를 완료한다.

## 9. 최종 판단

- 승인 여부: 자동 승인하지 않음
- 검수 의견: 대상 기능과 정적 검사는 PASS지만, 전체 회귀에 미실행 항목이 있어 AGENTS.md의 자동 승인 조건(모든 항목 PASS, SKIP 없음)을 충족하지 못했다.
- 다음 조치: PostgreSQL 통합 검수 재실행 후 M2.3-02 착수 여부를 판단한다.
