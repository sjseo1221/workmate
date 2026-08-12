# Workmate AI 개발 작업 규칙

이 문서는 저장소에서 구현·검수 작업을 수행하는 개발자와 AI Agent가 공통으로 따른다. 전체 계획은 [`docs/06-delivery-plan.md`](docs/06-delivery-plan.md), 현재 진행 상태는 [`HANDOFF.md`](HANDOFF.md), 승인된 검수 결과는 `docs/evidence/Mx/Mx.y/result.md`를 기준으로 한다.

## 작업 시작 순서

1. `docs/README.md`와 작업 대상 폴더의 `README.md`를 읽는다.
2. 루트 `HANDOFF.md`에서 현재 진행 작업과 다음 착수 항목을 확인한다.
3. 관련 마일스톤 문서를 읽는다.
4. 승인된 증빙 `docs/evidence/Mx/Mx.y/result.md`를 확인한다.
5. 관련 Schema, API 계약과 테스트 파일을 먼저 확인한다.
6. 변경 범위에 해당하는 기존 테스트를 실행한다.

루트에 단일 `README.md`가 있다고 가정하지 않는다. 외부 인증이나 Provider Secret이 필요한 테스트는 설정 여부를 먼저 확인하고, 실행하지 못한 경우 원인과 재현 조건을 기록한다.

## 구현 규칙

- 기존 Schema와 API 계약을 임의로 변경하지 않는다.
- 변경이 필요하면 관련 문서·Schema·Contract Test를 함께 수정한다.
- 공개 A2A 응답과 테스트 Fixture는 승인된 Artifact·Skill Schema를 통과해야 하며 Mock 전용 필드를 공개 응답에 추가하지 않는다.
- 공식 A2A SDK는 계획서에 고정된 정확한 버전과 lockfile을 사용하고, 버전 변경 시 M0.1 Contract Test를 다시 실행한다.
- `workmate-agent`의 Python 의존성 원장은 `pyproject.toml`과 `uv.lock`으로 유지한다. `requirements.txt`가 필요하면 lockfile에서 생성한 호환 산출물로만 관리한다.
- M0.1은 A2A Task·Message 멱등성·Artifact·`task_id ↔ thread_id`·Checkpoint의 최소 인프라 Migration을 소유하고, M1.1은 Task·Gmail·Calendar 업무 도메인 Migration을 소유한다. 공개 이벤트 전체 이력은 MVP에서 별도 저장하지 않는다.
- 공식 SDK가 제공하는 Route를 전부 공개하지 않는다. 승인된 MVP Route allowlist만 등록하고 제외 Route의 `404` 또는 `405` Contract Test를 유지한다.
- 우선순위 점수는 결정적으로 계산한다.
- LLM이 Task 순위와 근거 ID를 생성하거나 변경하지 않도록 한다.
- 모든 조회에 요청된 `user_id` 조건을 적용한다.
- 외부 Provider 장애 시 정의된 부분 결과와 `warnings`를 반환한다.
- 공개 함수와 핵심 업무 규칙 함수에는 Docstring 또는 JSDoc을 작성한다.
- 주석·Docstring은 다음 기준을 따른다.
  - 모듈·공개 API·Domain·Adapter·인증·Streaming 경계에는 역할과 계약을 기록한다.
  - 새로 작성하거나 수정하는 Python Docstring과 JSDoc은 한글을 기본 언어로 사용한다. 함수명·클래스명·프로토콜·Schema 필드명·환경변수명·SDK 타입명은 원문 식별자를 유지한다.
  - 기존 영문 Docstring은 기능 변경 없이 일괄 번역하지 않으며, 해당 코드를 수정하거나 문서화 보강 작업을 할 때 한글로 정리한다.
  - 가능하면 입력, 반환값, 예외, 외부 시스템 제약을 포함한다.
  - 이벤트 순서, 멱등성, 재시도, 취소처럼 코드만 읽어도 놓치기 쉬운 불변식은 명시한다.
  - 단순한 코드 동작을 반복하는 인라인 주석은 작성하지 않는다.
  - `TODO`에는 백로그 ID와 완료 조건을 함께 기록하고, 막연한 TODO는 남기지 않는다.
  - Secret, Token, API Key, 개인정보는 주석·Docstring·Fixture에 기록하지 않는다.
  - 생성된 SDK·Migration·외부 라이브러리 파일은 직접 수정하거나 주석을 추가하지 않는다.
- FastAPI Route에는 업무 규칙을 직접 작성하지 않고 Workflow·Domain 함수로 전달한다.
- 장기 Task의 원장은 영속 Task Store로 유지하고 프로세스 메모리 상태만으로 완료·복구를 판정하지 않는다.

## 완료 규칙

- 코드만 작성하고 완료 처리하지 않는다.
- 변경 범위에 해당하는 단위·통합·UI 테스트를 실행한다.
- 작업 시작 시 `docs/evidence/Mx/Mx.y/README.md`를 준비하고, 실행 결과가 생기면 `runs/{run_id}/result.md`에 기록한다.
- 승인된 실행만 하위 마일스톤의 상위 `result.md`에 연결한다.
- `result.md`에 해당 작업의 구현 코드·Schema·테스트·Fixture·평가 Case와 결과 경로를 기록한다. 관련 없는 항목은 `해당 없음`으로 표시한다.
- `result.md`의 구현·Schema·Migration·UI·테스트 경로는 저장소 내 파일로 이동하는 Markdown 링크를 사용한다. 삭제된 파일은 링크를 만들지 않고 삭제 사실과 대체 검증 경로를 기록한다.
- `result.md`에는 파일 경로만 나열하지 않고 구현 요약, 변경 전후 동작, 핵심 함수·클래스, 의도적으로 제외한 범위를 기록한다. 문서만 읽어도 무엇을 구현했는지 설명할 수 있어야 한다.
- `HANDOFF.md`의 현재 상태·다음 작업·차단 사항·갱신 이력을 수정한다.
- 마일스톤이 담당하는 실제 Workflow가 운영 실행 경로에서 Mock·고정 샘플 응답을 반환하면 완료 처리하지 않는다. Fake·Mock은 단위·계약 테스트의 명시적인 Fixture에서만 허용한다.
- 실행 결과에 정의된 검증 명령이 모두 PASS이고 미실행·수동 검수·차단 항목이 없으면 해당 실행을 `자동 승인(검증 명령)`으로 묵시 승인한다. `latest_approved_run_id`·`approved_at`·`reviewer`를 기록하고 `docs/06-delivery-plan.md`의 백로그 상태와 `HANDOFF.md`를 `완료`로 함께 갱신한다.
- 공개 A2A Schema·데이터 모델 변경, 외부 OAuth·실제 Provider, UI 육안 검수, 모델 평가처럼 사람의 판단이나 별도 권한이 필요한 항목은 자동 승인하지 않는다. 검증을 하나라도 건너뛰었거나 완료 조건에 영향을 주는 경고·보류·미해소 차단이 있으면 `검수 중` 또는 `재작업`을 유지한다.

## 커밋·Push 규칙

- 구현 착수 전에 `C:\dev\workmate`를 문서·증빙용 Superproject로 구성하고 기존 `workmate-agent` Git 이력은 Submodule로 보존한다. Superproject와 Submodule의 기준 브랜치·Commit을 `HANDOFF.md`에 기록하며 기존 하위 저장소를 병합하거나 이력을 다시 만들지 않는다. `workmate-ui-demo`는 폐기된 로컬 샘플이므로 Submodule·구현·검수 대상에 포함하지 않는다.
- 작업 브랜치는 기본적으로 하위 마일스톤 단위로 만든다. 권장 형식은 `feat/M0.1-a2a-contract`, `feat/M1.2-external-sources`이며, 독립 배포나 긴급 수정처럼 분리가 필요한 경우에만 `fix/M1.2-04-watch-renewal` 같은 백로그 브랜치를 사용한다.
- `main` 또는 기준 브랜치에 직접 Push하지 않는다. 작업 브랜치를 Push하고 Pull Request로 검토받는다.
- 하나의 커밋에는 하나의 논리적 변경만 넣는다. 구현, 테스트, 증빙은 가능한 한 별도 커밋으로 분리한다.
- 커밋 메시지는 `<type>(<backlog-id>): <change>` 형식을 사용한다. 예: `feat(M1.2-04): implement Gmail watch renewal`.
- 백로그 완료 시에는 구현·테스트·증빙을 로컬 커밋으로만 남기고 원격 Push하지 않는다. 하위 마일스톤의 모든 백로그와 통합 완료 기준이 승인된 시점에 관련 로컬 커밋을 한 번에 Push한다.
- 중간 Push는 다른 작업자에게 인수인계하거나 원격 협업이 필요할 때, 장기간 작업의 원격 백업이 필요할 때, 또는 사용자가 명시적으로 요청한 경우에만 허용한다. Push 승인 질문도 실제 Push 조건에 도달했을 때 한 번만 한다.
- Push 전에 변경 범위의 테스트, `git diff --check`, Schema·Contract Test 확인, Secret 검사, 증빙 경로와 `HANDOFF.md` 갱신을 완료한다.
- 구현 결과가 생기기 전에는 빈 `result.md`를 만들지 않는다. 테스트 결과가 생긴 뒤 `runs/{run_id}/result.md`를 작성한다.
- 마일스톤 완료와 Merge는 명시 승인 또는 완료 규칙에 따른 묵시 승인으로 `latest_approved_run_id`가 확정된 뒤에만 수행한다.
- 공유 브랜치에 강제 Push하지 않는다. 이전 커밋이나 승인 증빙을 덮어쓰거나 삭제하지 않는다.
- API Key, Token, Presigned URL, 실제 회의 음성, 평가 원본 Secret은 커밋·Push하지 않는다.

## 금지 사항

- API Key, Token, Presigned URL, 실제 회의 음성을 Git에 저장하지 않는다.
- 기존 승인 증빙을 덮어쓰거나 삭제하지 않는다.
- 실패한 테스트를 삭제하거나 우회하지 않는다.
- 사용자 승인 없이 데이터 모델과 공개 A2A Schema를 변경하지 않는다.
- 관련 없는 파일을 함께 정리하거나 대규모 포맷 변경을 하지 않는다.

## 작업 보고

일일 보고는 작성하지 않는다. 다음 이벤트가 발생할 때만 진행상황을 보고서와 `HANDOFF.md`에 남긴다: 작업 시작, 상태·범위·담당자 변경, 테스트 결과, 차단·실패, 검수 시작, 검수 승인·재작업 결정, 인수인계.

보고에는 다음 내용을 남긴다.

- 변경 파일과 핵심 변경 내용
- 실행한 테스트 명령과 결과
- 실행 ID와 증빙 경로
- 남은 문제·보류 사항
- 다음 착수 백로그 ID
- 브랜치와 기준 Git Commit
- 상태: `대기 / 진행 / 검수 중 / 완료 / 재작업 / 보류`
