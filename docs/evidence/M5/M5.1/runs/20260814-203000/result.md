# M5.1 Workmate 실제 Workflow A2A 재검수 결과

## 1. 기본 정보

- 마일스톤: M5.1 A2A 통합
- 제목: M3/M4 실제 Workflow Registry 연결과 Workmate 측 종단 간 재검수
- 담당자: Codex
- 검수자: 자동 검수(검증 명령)
- 상태: 검수 중
- 실행일: 2026-08-14
- 실행 ID: `20260814-203000`
- 코드 버전: 작업 트리
- 입력 데이터 버전: M5.1 비식별 임시 회의·검색 Fixture

## 2. 구현 요약

- `analyze_meeting`을 사용자 소유 최종 Transcript 조회, 실제 LLM 분석, Action Item 근거 검증·저장, `meeting_analysis` Artifact 생성 경로에 연결했다.
- `search_meetings`를 실제 Embedding Provider, PostgreSQL Dense+Trigram RRF 검색, 근거 답변·출처 생성, `grounded_answer` Artifact 경로에 연결했다.
- 공개 5개 Skill Contract Test는 회의 Workflow 코드에 명시적 테스트 Provider·Repository Fixture를 주입해 Mock 부트스트랩 성공을 더 이상 허용하지 않는다.
- Windows의 psycopg async 제약을 피하도록 Selector Event Loop를 설정하는 로컬 Uvicorn 진입점을 추가했다.
- 호환성 클라이언트의 기본 사용자·회의 ID를 PostgreSQL UUID 계약에 맞췄다.

## 3. 구현·테스트 경로

- A2A Registry: [`app/a2a/runtime.py`](../../../../../../workmate-agent/app/a2a/runtime.py)
- 회의 Workflow: [`app/workflows/meetings.py`](../../../../../../workmate-agent/app/workflows/meetings.py)
- Windows 실행 진입점: [`app/server.py`](../../../../../../workmate-agent/app/server.py)
- 호환성 클라이언트: [`tools/m51_a2a_compatibility.py`](../../../../../../workmate-agent/tools/m51_a2a_compatibility.py)
- Workflow 테스트: [`tests/test_meeting_workflows.py`](../../../../../../workmate-agent/tests/test_meeting_workflows.py)
- A2A Contract Test: [`tests/test_contract.py`](../../../../../../workmate-agent/tests/test_contract.py)
- 내부 검증 API 테스트: [`tests/test_internal_chat.py`](../../../../../../workmate-agent/tests/test_internal_chat.py)
- 공개 Schema 변경: 해당 없음

## 4. 실행 명령과 결과

```text
python -m unittest tests/test_contract.py tests/test_meeting_workflows.py tests/test_postgres_integration.py tests/test_meeting_answer_postgres_integration.py
```

- 결과: 14개 PASS, 0 FAIL, 0 SKIP

```text
python -m unittest discover -s tests -p "test_*.py"
python -m compileall -q app tests tools
git diff --check
```

- 전체 회귀: 137개 PASS, 0 FAIL, 환경 의존 10개 SKIP
- `compileall`: PASS
- `git diff --check`: PASS

```text
python tools/m51_a2a_compatibility.py
```

- Agent Card·5개 Skill 목록: PASS
- `daily_briefing`: PASS
- `weekly_report`: PASS
- `analyze_meeting`: PASS
- `search_meetings`: PASS
- `rank_priorities`: PASS
- Artifact Schema·Mock 차단: PASS
- 실제 Provider: LLM·Embedding 사용
- 실제 저장소: 임시 PostgreSQL 16+pgvector 및 사용자 범위 SQLite Transcript 사용
- Secret·Token·Presigned URL: 기록하지 않음
- 임시 PostgreSQL 컨테이너: 정리 완료

## 5. 검수 항목

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| M3/M4 실제 Workflow Registry 연결 | PASS | 관련 14개 테스트 |
| Workmate Agent Card 조회 | PASS | 호환성 클라이언트 |
| Workmate 5개 Skill 실제 HTTP 호출 | PASS | 호환성 클라이언트 |
| 비 Mock 업무 Artifact | PASS | Artifact Schema·Mock 차단 |
| 실제 Orchestrator 종단 간 호출 | 미실행 | 로컬 Orchestrator 부재 |

## 6. 문제와 수정 이력

- 첫 회귀 실패: 기존 Contract·내부 UI 테스트가 Mock-era 성공을 가정했다. 실제 Workflow와 명시적 테스트 Fixture로 수정했다.
- 첫 HTTP 재검수 실패: Windows Proactor Event Loop에서 psycopg async 연결을 사용할 수 없었다. `python -m app.server` 진입점에서 Selector Event Loop를 설정했다.
- 담당자 Orchestrator 저장소를 `C:\dev\AI-agent_game_platform`에 `main` 브랜치로 clone했다. 저장소 HEAD는 `5094cad47e15578e9f2775db74563e47394e71ee`이다.
- clone된 Orchestrator는 기본 Workmate URL을 `/a2a/v1`로 사용하고 Agent Card 경로도 `/a2a/v1` 기준으로 계산한다. 정식 Workmate 계약은 `/a2a`이므로 직접 연결할 수 없다.
- clone된 smoke test는 `parts[1].data.invoked_skill` 레거시 Artifact를 기대한다. 정식 Workmate Artifact Schema와 다르므로 M5.1 승인 검수에 그대로 사용할 수 없다.
- 남은 차단: Workmate 공개 Route·Artifact를 변경하지 않으려면 `/a2a/v1`을 `/a2a`로 변환하고 Agent Card·Artifact를 변환하는 별도 어댑터가 필요하다. 어댑터 없이 직접 연결하는 종단 간 검수는 수행하지 않았다.

## 7. 최종 판단

- 승인 여부: 미승인
- 검수 의견: Workmate 측 M5.1 준비 조건은 PASS했다. 실제 Orchestrator가 Agent Card를 조회하고 5개 Skill을 호출하는 종단 간 결과가 없으므로 M5.1 완료·자동 승인은 불가하다.
- 다음 조치: Orchestrator 실행 환경을 제공한 뒤 동일 5개 Skill을 종단 간 호출하고 응답 변환 계약을 검증한다.
-
## Orchestrator 어댑터 실연동 보완 검증

- 구현 경로: [`tools/m51_legacy_adapter.py`](../../../../../../workmate-agent/tools/m51_legacy_adapter.py)
- 테스트 경로: [`tests/test_m51_legacy_adapter.py`](../../../../../../workmate-agent/tests/test_m51_legacy_adapter.py)
- 어댑터 단위 테스트: 2 PASS, 0 FAIL
- 임시 upstream(`8013`)과 어댑터(`8012`) 실연동: Agent Card URL 변환 PASS, `daily_briefing` HTTP 호출 PASS
- 제한: 담당 Orchestrator 전체 컨테이너 E2E는 아직 실행하지 않았으므로 M5.1 자동 승인은 보류
