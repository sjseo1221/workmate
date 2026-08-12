# Workmate AI 설계문서 목차

Workmate AI는 메일, 캘린더, 회의록, Task DB 정보를 통합해 브리핑, 보고서, 회의 분석, 회의록 검색, 업무 우선순위를 제공하는 업무지원 Agent다.

현재 작업 상태와 다음 착수 항목은 저장소 루트의 [개발 인수인계 문서](../HANDOFF.md)를 확인한다.
개발 Agent의 공통 작업 규칙은 저장소 루트의 [AGENTS.md](../AGENTS.md)를 따른다.

## 문서 구성

| 순서 | 문서 | 내용 |
| --- | --- | --- |
| 1 | [프로젝트 개요와 아키텍처](01-overview-architecture.md) | 목표, MVP 범위, 사용자, 시스템 구성, 기술 선택 |
| 2 | [A2A 인터페이스](02-a2a-interface.md) | Agent Skill, 요청·응답, 내부 API |
| 3 | [데이터와 우선순위 규칙](03-data-priority-rules.md) | 데이터 모델, 날짜 범위, 중복 제거, 점수 공식 |
| 4 | [시나리오별 처리 흐름](04-scenarios.md) | 브리핑, 주간 보고, 회의 분석, 검색, 재계산, 할 일 관리, Gmail 제안 |
| 5 | [AI·보안·운영](05-ai-security-operations.md) | LLM 책임, 개인정보, 오류와 부분 실패 |
| 6 | [개발 및 검증 계획](06-delivery-plan.md) | 화면, Phase, 테스트, 데모, 미결정 사항 |
| 7 | [기술 상세 설계](07-technical-specification.md) | 버전 기준, LangGraph, A2A, DB, 검색, 인증, 실행 환경 |
| 9 | [UI 설계](09-ui-design.md) | Workmate 화면 구성과 할 일 관리 UI |
| 10 | [Embedding 모델 평가 계획](10-embedding-evaluation-plan.md) | 후보, 평가 데이터, 검색 지표, 선정 기준과 이력 관리 |
| 11 | [LLM 모델 평가 계획과 이력](11-llm-evaluation-plan.md) | 평가 Case, 품질 기준, 모델 선정과 기존 개선 이력 |
| 12 | [구현·검증 가이드](12-implementation-verification-guide.md) | 회의 녹음·Embedding·STT 평가 결과를 실제 구현에 적용하는 기준 |

문서 번호 8은 기존 통합 초안과의 링크 충돌을 피하기 위해 예약 번호로 남기며 새 문서에 재사용하지 않는다.

## 권장 읽기 순서

- 팀 전체: 1 → 2 → 6 → 12
- 백엔드 담당: 2 → 3 → 4 → 5 → 7 → 12
- AI/RAG 담당: 4 → 5 → 7 → 10 → 11 → 12
- 프론트 담당: 2 → 4 → 6 → 9

## 현재 결정 요약

- Workmate AI는 하나의 A2A Agent로 배포한다.
- 내부 기능은 별도 Agent가 아니라 모듈로 구분한다.
- 날짜, 권한, 상태, 점수는 코드가 처리한다.
- LLM은 근거 기반 요약과 구조화 추출만 담당한다.
- 회의 Action Item은 사용자 승인 후에만 Task로 등록한다.
- MVP 회의 입력은 녹음 파일 업로드와 실시간 녹음을 모두 지원한다. 실시간 결과는 임시 자막으로 사용하고, 녹음 종료 후 최종 파일 STT와 회의 분석을 수행한다.
