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
| 13 | [사용자 수동 검수 목록](13-manual-verification-guide.md) | 나중에 수행할 UI 육안 검수의 작업명·확인 방법·판정 기준 |
| 14 | [workmate-ui 백엔드 연동 갭 분석 및 구현 계획](14-workmate-ui-integration-gaps.md) | `workmate-ui`와 설계 문서 대조로 찾은 갭 목록, 화면별 구현 계획 |
| 15 | [workmate-ui 화면별 기능·데이터 참조](15-workmate-ui-screens-reference.md) | 02·03·04·07·09를 종합한 화면별 목표 기능·조회값 정의(Source of Truth), 14번 갭 분석의 1차 기준 |
| 16 | [LLM 프롬프트 목록](16-llm-prompts.md) | 코드가 실제로 호출하는 모든 System Prompt 원문(회의 분석·Gmail 할 일 추출·주간 보고서 요약) |
| 17 | [workmate-ui 갭 분석 v2](17-workmate-ui-gap-analysis.md) | 15번 문서 기준 `workmate-ui` 재분석, 갭 목록 |
| 18 | [Workmate 어시스턴트(Drawer) 구현 계획 및 완료 보고](18-workmate-assistant-implementation-plan.md) | `workmate-ui` 내부 Drawer 챗봇 설계·구현 결과 |
| 19 | [workmate-ui → 오케스트레이터 이식 작업 계획](19-workmate-ui-orchestrator-port-plan.md) | `workmate-ui`가 구현한 7개 화면을 `AI-agent_game_platform`(오케스트레이터)로 이식하는 단계별 계획·결정·구현 완료 기록 |
| 20 | [오케스트레이터 AI Chat → Workmate Skill 라우팅 구현 계획](20-orchestrator-ai-chat-skill-routing-plan.md) | "Workmate AI" 채팅이 5개 Skill로 라우팅되는 구현 계획 |
| 21 | [오케스트레이터 Workmate 화면 수동 검수 체크리스트](21-orchestrator-workmate-manual-verification-checklist.md) | 19번 문서로 이식한 7개 화면의 화면별 수동 검수 항목(13번 문서 형식) |
| 22 | [오늘 브리핑·주간 업무보고 재이식 계획](22-today-briefing-weekly-report-port-plan.md) | 19번 문서 3단계 롤백 후, `workmate-ui` 원본과 대조해 빠진 필드(경고 배너·소스 상태·배점 내역) 없이 다시 이식하는 계획·구현 완료 기록 |
| 23 | [오케스트레이터 vs workmate-ui "제안함" 로직 차이 분석](23-proposals-orchestrator-vs-workmate-ui-diff.md) | 인증 방식·SSE Provider 마운트 범위·개발 서버 동작 등 두 구현의 실제 코드 차이를 항목별로 정리(분석·기록용, 구현 항목 아님) |
| 24 | [오케스트레이터 vs workmate-ui "제안함" UI(시각) 차이 분석](24-proposals-orchestrator-vs-workmate-ui-ui-diff.md) | 23번 문서의 로직 분석과 짝을 이루는 화면 표현 차이 — 버튼 시각 위계·상태 색 표시·Toast 구성·안 읽은 배지·카드 스니펫/추천 이유 노출 여부를 JSX·CSS 대조로 정리(분석·기록용, 구현 항목 아님) |
| 25 | [오케스트레이터 pull 이후 충돌·드리프트 기록](25-orchestrator-pull-conflicts.md) | 모노레포 재구성 이후 빌드 경로·포트·환경변수·볼륨 드리프트와 로컬 검증 결과 |
| 26 | [회의 검색 데모 환경 보완 가이드](26-meeting-search-demo-environment.md) | `search_meetings` HTTP 503 원인, 팀 전달용 Compose 보완 항목과 검증 절차 |
| 30 | [Workmate LangGraph 전면 전환 계획](30-langgraph-migration-plan.md) | 빅뱅 전면 재작성의 전제·원칙·범위·확정 결정(D1~D6)·위험·완료 기준. 단계별 상세는 30-0~30-9 |
| 30-0~30-9 | [W0 기준선](30-0-w0-baseline.md) · [W1 계약 스냅샷](30-1-w1-contract-snapshot.md) · [W2 Graph 골격](30-2-w2-graph-foundation.md) · [W3 Skill Subgraph](30-3-w3-skill-subgraphs.md) · [W4 Root Graph](30-4-w4-root-graph.md) · [W5 진입점 교체](30-5-w5-entrypoint-swap.md) · [W6 interrupt·공개 계약](30-6-w6-interrupt-resume.md) · [W7 레거시 삭제](30-7-w7-legacy-removal.md) · [W8 재시도·관측](30-8-w8-retry-observability.md) · [W9 문서·증빙](30-9-w9-docs-evidence.md) | 단계별 계획의 **요약·색인**. 각 문서 상단에 하위 문서 표가 있다 |
| 30-10 | [ReAct Agent 전환 계획](30-10-w10-react-agent.md) | **전환 후속 작업**의 요약·색인. `assistant_ask`의 단발 분류 라우팅을 ReAct 루프로. 05번 문서 §1 개정과 결정 D7-1~D7-7 승인이 선행 조건이며, 승인은 **착수 시점에** 받는다 |
| 30-10-1~13 | W10의 절별 상세 (예: [30-10-5 설계](30-10-5-design.md), [30-10-10 승인 경계](30-10-10-approval.md)) | 30-0~30-9와 같은 13절 체계. W10 고유 절: §10 승인 경계(**D7-1~D7-7 + 05번 개정안 + 대안 비교**) |
| 30-N-1~13 | 각 단계의 절별 상세 문서 (예: [30-2-5 설계](30-2-5-design.md), [30-6-10 승인 경계](30-6-10-approval.md)) | 절 단위 상세 — 문서 정보 / 목적·범위 / 선행 조건 / 요구사항 `Wn-Rxx` / 설계 / WBS `Wn-Txx` / 검증 `Wn-Vxx` / 추적성 / 완료 정의 / 위험 `Wn-Kxx` / 롤백 / 참조. 단계별 고유 절: W0 §10 실행 결과, W1 §12 후행 전달, W6·W9 §10 승인 경계, W9 §12 후속 백로그 |
| 31 | [표준 Agent 방식 전환 영향도 분석](31-standard-agent-impact-analysis.md) | **조사·기록용**(구현 항목 아님). `langchain.agents.create_agent` + middleware가 표준 진입점임을 실행으로 확인하고, 기존 `workmate-agent`를 그 방식으로 바꿀 때의 영향을 심볼·줄 단위로 정리. 선택지 A/B/C와 W1~W10 변경 필요 여부, 의존성 충돌 검증 결과 포함 |
| 96 | [Workmate LangGraph StateGraph 목표 아키텍처](96-workmate-langgraph-target-architecture.md) | Workmate를 실제 LangGraph `StateGraph`로 구현했다고 가정한 Root Graph·Subgraph·Checkpoint·Interrupt 목표 도식 |
| 97 | [Workmate LangGraph 구조 도식](97-workmate-langgraph-structure.md) | 전체 문서를 종합한 목표 LangGraph, 현재 Workflow Runtime, Skill별 분기·상태·영속성 도식 |
| 99 | [Workmate PPT 콘텐츠 원고](99-workmate-ppt-content.md) | Skill, 모델·API 스펙, LangGraph 설계와 실제 Workflow 구조, LLM·Embedding·STT 평가 및 구현 반영 내용 |

문서 번호 8은 기존 통합 초안과의 링크 충돌을 피하기 위해 예약 번호로 남기며 새 문서에 재사용하지 않는다.

## 권장 읽기 순서

- 팀 전체: 1 → 2 → 6 → 12
- 백엔드 담당: 2 → 3 → 4 → 5 → 7 → 12
- AI/RAG 담당: 4 → 5 → 7 → 10 → 11 → 12 → 16
- 프론트 담당: 2 → 4 → 6 → 9 → 14 → 15

## 현재 결정 요약

- Workmate AI는 하나의 A2A Agent로 배포한다.
- 내부 기능은 별도 Agent가 아니라 모듈로 구분한다.
- 날짜, 권한, 상태, 점수는 코드가 처리한다.
- LLM은 근거 기반 요약과 구조화 추출만 담당한다.
- 회의 Action Item은 사용자 승인 후에만 Task로 등록한다.
- MVP 회의 입력은 녹음 파일 업로드와 실시간 녹음을 모두 지원한다. 실시간 결과는 임시 자막으로 사용하고, 녹음 종료 후 최종 파일 STT와 회의 분석을 수행한다.
