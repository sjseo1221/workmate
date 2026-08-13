# M0.2-05 재검수 결과

## 1. 기본 정보

- 마일스톤: M0.2
- 제목: Calendar OAuth 실제 API·Watch 재검수
- 담당자: Codex
- 검수자: 자동 승인(모든 검증 결과 PASS)
- 상태: 완료
- 실행일: 2026-08-13
- 실행 ID: 20260813-131903
- 코드 버전: `ac0b91c`
- 입력 데이터 버전: 사용자 로컬 OAuth 계정의 비식별 실행 결과

## 2. 최신 실행과 승인

- latest_run_id: 20260813-131903
- latest_run_status: PASS
- latest_approved_run_id: 20260813-131903
- approved_at: 2026-08-13 13:19 Asia/Seoul

## 3. 목표와 완료 기준

- 목표: `AuthorizedSession` REST 전송으로 Gmail·Calendar 실제 API와 Watch 계약을 재검증한다.
- 완료 기준:
  - Gmail profile/messages/history와 Calendar events가 모두 `pass`일 것
  - `--watch` 실행에서 Gmail·Calendar Watch가 모두 `pass`이고 식별자·만료 시각이 존재할 것
  - Secret·Token·원본 메시지·일정 내용을 증빙에 기록하지 않을 것
- 백로그 범위: M0.2-05
- 미완료·보류 백로그: 없음

## 4. 구현 경로

- 구현 코드: [`smoke_test.py`](../../../../../../google-oauth-test/smoke_test.py)
- 의존성: [`requirements.txt`](../../../../../../google-oauth-test/requirements.txt)
- Schema 또는 Migration: 해당 없음
- UI 코드: 해당 없음

`smoke_test.py`는 `AuthorizedSession`을 사용해 Gmail profile/messages/history와 Calendar events를 조회하고, `--watch`에서 Gmail watch·Calendar watch를 등록한다. 응답 본문은 증빙에 저장하지 않고 검증에 필요한 존재 여부와 개수만 기록한다.

## 5. 테스트 파일 경로

- 단위 테스트: [`test_config.py`](../../../../../../google-oauth-test/tests/test_config.py)
- 통합 테스트: [`smoke_test.py`](../../../../../../google-oauth-test/smoke_test.py) 실제 사용자 로컬 실행
- UI 테스트: 해당 없음
- Fixture/입력: 사용자 로컬 OAuth 설정(Secret·Token 비공개)
- 기대 결과: 모든 검사 항목이 정확히 `pass`
- 모델 평가 Case: 해당 없음
- 모델 평가 결과: 해당 없음

## 6. 실행 명령과 결과

```text
cd C:\dev\workmate\google-oauth-test
venv\Scripts\python.exe smoke_test.py
venv\Scripts\python.exe smoke_test.py --watch
```

사용자가 제공한 두 실행 결과:

- 기본 실행: `gmail_profile`, `gmail_messages`, `gmail_history`, `calendar_events` 모두 `pass`; Gmail message count 1, history ID/page 존재, Calendar event count 1
- Watch 실행: 위 항목과 `watch` 모두 `pass`; Gmail history ID/expiration, Calendar resource ID/expiration 모두 존재
- 미실행·경고·보류·실패 항목: 없음

## 7. 검수 항목

| 항목 | 결과 | 근거 경로 |
| --- | --- | --- |
| Gmail profile/messages/history | PASS | 사용자 실행 `smoke_test.py` 결과 |
| Calendar events | PASS | 사용자 실행 `smoke_test.py` 결과 |
| Gmail·Calendar Watch | PASS | 사용자 실행 `smoke_test.py --watch` 결과 |
| Secret 비저장 | PASS | 본 결과에는 존재 여부·개수·식별자 존재 여부만 기록 |
| 자동 승인 조건 | PASS | 모든 검증 결과가 정확히 `pass`, 미실행·수동 검수·차단 없음 |

## 8. 문제와 수정 이력

- 이전 실행 `20260813-130230`에서는 관리형 실행 환경의 OAuth timeout과 Watch 미실행으로 자동 승인을 중단했다.
- 사용자 로컬 실행에서 실제 Gmail·Calendar API 및 Watch가 모두 성공해 재검수 조건을 충족했다.
- 이전 실패 결과는 [`20260813-130230/result.md`](../20260813-130230/result.md)에 보존하며 덮어쓰거나 삭제하지 않는다.
- 재검수 실행 ID: 20260813-131903

## 9. 최종 판단

- 승인 여부: 승인
- 검수 의견: 모든 검증 명령 결과가 정확히 `PASS`이므로 자동 승인 규칙을 적용한다.
- 다음 조치: M0.2 전체 통합 검수
