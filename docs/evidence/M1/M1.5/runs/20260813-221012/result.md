# M1.5-01 검수 결과

## 1. 기본 정보

- 마일스톤: M1.5 우선순위·브리핑
- 제목: 점수 Domain·시간 경계
- 담당자: Codex
- 검수자: 자동 승인(검증 명령)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-221012
- 코드 버전: workmate-agent 작업 트리
- 입력 데이터 버전: 테스트 고정 Fixture

## 2. 최신 실행과 승인

- latest_run_id: 20260813-221012
- latest_run_status: PASS
- latest_approved_run_id: 20260813-221012
- approved_at: 2026-08-13 22:10 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: 승인된 점수식을 순수 Domain 함수로 구현하고 사용자 timezone·상태 제외·동점 정렬을 결정적으로 보장한다.
- 완료 기준: 공식 점수 구성, `priority_hint` 매핑, 차단·기한 초과 점수, 완료·취소·Soft Delete 제외, timezone-aware `as_of`, 동점 정렬 테스트가 PASS한다.
- 백로그 범위: M1.5-01
- 미완료·보류 백로그: 없음

## 4. 구현 경로

- 구현 코드: [`app/domain/priority.py`](../../../../../../workmate-agent/app/domain/priority.py)
- Schema 또는 Migration: 해당 없음 — M1.5-02에서 PrioritySnapshot 경계를 추가한다.
- UI 코드: 해당 없음

## 5. 테스트 파일 경로

- 단위 테스트: [`tests/test_priority_domain.py`](../../../../../../workmate-agent/tests/test_priority_domain.py)
- 통합 테스트: 해당 없음
- UI 테스트: 해당 없음
- Fixture/입력: 테스트 내부의 고정 Task Fixture
- 기대 결과: 동일 입력에서 동일 점수·구성·순위와 상태 제외
- 모델 평가 Case: 해당 없음
- 모델 평가 결과: 해당 없음

## 6. 구현 요약

- `ScoreBreakdown`으로 deadline·importance·blocked_or_overdue·meeting_commitment·calendar_relevance를 분리했다.
- `priority_hint`를 `0~2=0`, `3~4=8`, `5~7=15`, `8~10=20`으로 결정적으로 매핑했다.
- 사용자 IANA timezone 기준 지역 날짜로 마감임박도를 계산하고, `as_of`가 timezone-aware가 아니면 거부한다.
- 완료·취소·Soft Delete Task를 제외하고 점수, due_at, updated_at, task_id 순으로 결정적으로 정렬한다.
- `source_type=action_item`인 승인 Task에 회의 약속 10점을 부여한다. Calendar 연관성은 후속 Workflow가 명시된 값으로 전달한다.

## 7. 실행 명령과 결과

```text
cd C:\dev\workmate\workmate-agent
.\.venv\Scripts\python.exe -m unittest tests.test_priority_domain tests.test_task_repository -q
.\.venv\Scripts\python.exe -m compileall -q app tests
git diff --check
```

- 단위·회귀 테스트: PASS (11개)
- 구문 검사: PASS
- 문서 diff 검사: PASS
- 미실행·수동 검수·차단: 없음

## 8. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| 공식 점수식과 구성 범위 | PASS | `tests/test_priority_domain.py` |
| timezone·`as_of` 검증 | PASS | `test_score_uses_local_date_and_hint_mapping`, `test_invalid_timezone_and_naive_as_of_are_rejected` |
| 완료·취소 제외 | PASS | `test_rank_excludes_done_cancelled_and_deleted` |
| 차단·기한 초과 상한 | PASS | `test_blocked_caps_overdue_component_at_15` |
| 동점 결정성 | PASS | `test_tie_breaks_by_due_updated_then_id` |

## 9. 자동 진행 판정

- 자동 진행 판정: 자동 착수
- 자동 재작업 착수: 아니오
- 자동 진행 보류 사유: 없음
- 판정을 막은 검증 항목과 결과: 없음
- 미실행·수동 검수·차단 항목: 없음
- 필요한 조치 또는 사용자 승인: 없음
- 재개 조건: 해당 없음
- 다음 백로그: M1.5-02 PrioritySnapshot 저장 경계

## 10. 최종 판단

- 승인 여부: 승인 — 자동 승인(검증 명령)
- 검수 의견: 정의된 검증 명령과 완료 기준이 모두 정확히 PASS하여 M1.5-01을 완료한다.
- 다음 조치: M1.5-02에서 PostgreSQL PrioritySnapshot Migration·Repository를 구현한다.
