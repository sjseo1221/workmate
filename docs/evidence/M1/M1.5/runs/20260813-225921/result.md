# M1.5-05 통합·회귀 검수 결과

## 1. 기본 정보

- 마일스톤: M1.5
- 제목: 우선순위·오늘 브리핑 PostgreSQL 통합 및 회귀 검수
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-225921

## 2. 최신 실행과 승인

- latest_run_id: 20260813-225921
- latest_run_status: PASS
- latest_approved_run_id: 20260813-225921
- approved_at: 2026-08-13 22:59 Asia/Seoul
- reviewer: 자동 승인(검증 명령)

## 3. 목표와 완료 기준

- 목표: M1.5-01~04의 실제 Workflow가 PostgreSQL 저장 경계와 연결되고 기존 M0/M1 회귀를 통과하는지 확인한다.
- 완료 기준: PostgreSQL·Contract·성능·문서 검사와 기존 M0/M1 회귀가 모두 PASS이며 SKIP·수동 검수·차단이 없다.
- 구현 요약: PostgreSQL JSONB가 `dict`/`list`로 반환되는 경우에도 Snapshot 역직렬화가 동작하도록 [`priority.py`](../../../../../workmate-agent/app/repositories/priority.py)를 보완하고, rank/daily briefing의 PostgreSQL 경계 통합 테스트를 [`test_m1_5_integration.py`](../../../../../workmate-agent/tests/test_m1_5_integration.py)에 추가했다.
- 의도적으로 제외: 실제 OAuth 재호출은 M1.5-04에서 승인되었으므로 이번 실행에서는 반복하지 않았다. 원격 Push·운영 데이터 변경은 수행하지 않았다.

## 4. 구현·테스트 경로

- 구현 코드: [`app/repositories/priority.py`](../../../../../workmate-agent/app/repositories/priority.py), [`app/workflows/priority.py`](../../../../../workmate-agent/app/workflows/priority.py), [`app/workflows/daily_briefing.py`](../../../../../workmate-agent/app/workflows/daily_briefing.py)
- Migration: [`003_priority_snapshots.sql`](../../../../../workmate-agent/migrations/003_priority_snapshots.sql)
- 통합 테스트: [`tests/test_m1_5_integration.py`](../../../../../workmate-agent/tests/test_m1_5_integration.py)
- 회귀 테스트: `tests/`의 integration 제외 80개, PostgreSQL 통합 5개

## 5. 실행 명령과 결과

### 5.1 PostgreSQL 통합

```text
$env:DATABASE_URL='postgresql://postgres:<ephemeral>@127.0.0.1:55432/workmate'
python -m unittest tests.test_m1_5_integration tests.test_m1_1_integration tests.test_postgres_integration tests.test_postgres_sync_state_integration -v
```

- 결과: 5개 PASS, 0개 FAIL, 0개 SKIP
- PostgreSQL 16 Alpine 임시 컨테이너 readiness: PASS
- `rank_priorities` Snapshot 저장·사용자 격리: PASS
- `daily_briefing` Task·sync 경계와 Provider Fixture: PASS
- 기존 M1.1 PostgreSQL Migration·Task Store·Sync State: PASS
- 임시 컨테이너: 검수 후 제거

### 5.2 기존 M0/M1 회귀

```text
python -m unittest tests.test_<non-integration modules> -q
```

- 결과: 80개 PASS, 0개 FAIL, 0개 SKIP
- Contract·A2A Route·Workflow·Repository·Task API·UI 계약 포함

### 5.3 성능·정적 검사

```text
python -m unittest tests.test_priority_workflow tests.test_daily_briefing -q
python -m compileall -q app tests
git diff --check
```

- Fixture 우선순위·브리핑 실행: 0.96초 wall time, PASS
- PostgreSQL M1.5 통합 실행: 2.28초 wall time, PASS
- `compileall`: PASS
- `git diff --check`: PASS

## 6. 재작업 이력

- 최초 PostgreSQL 통합 실행: 2개 ERROR
- 원인: PostgreSQL JSONB를 `str()`로 변환한 뒤 JSON으로 파싱해 Python dict 표현(`{'key': ...}`)이 JSON 문법으로 처리되지 않음.
- 수정: JSONB의 `dict`/`list` 반환값은 직접 사용하고 SQLite 문자열·bytes만 JSON 파싱하도록 정규화.
- 재검수: 수정 후 PostgreSQL 통합 5개 PASS, 회귀 80개 PASS.
- 참고: `DATABASE_URL`을 설정한 채 SQLite 전용 fixture를 함께 실행하면 문자열 사용자 ID가 UUID 컬럼과 충돌한다. 이는 실행 환경 혼합 오류이며, 운영 DB 통합군과 SQLite 회귀군을 분리해 재실행하여 해결했다.

## 7. 최종 판단

- 승인 여부: 승인
- 승인 방식: 자동 승인(검증 명령)
- 검수 의견: M1.5-01~04와 기존 M0/M1 회귀의 정의된 검증 명령이 모두 PASS했고, 실행된 검수군에 SKIP·수동 검수·차단이 없다.
- 다음 조치: M1.5를 완료하고 M2.1 주간 데이터 분류를 착수한다.
