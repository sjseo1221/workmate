# LLM 프롬프트 목록

## 목적

`workmate-agent`가 실제로 호출하는 모든 LLM System Prompt를 한 곳에 모아 원문 그대로 보여준다. 코드
여러 파일에 흩어져 있어 "지금 LLM한테 정확히 뭐라고 시키고 있는지"를 확인하려면 파일을 하나씩 열어야
했던 문제를 해결한다.

**원본은 코드다.** 이 문서는 코드를 복사해온 참조 문서이지 별도로 편집하는 원본이 아니다 — 프롬프트를
바꿀 때는 코드를 고치고, 같은 커밋/작업에서 이 문서도 함께 갱신한다. 두 값이 다르면 코드가 맞다.

**평가용 프롬프트는 다루지 않는다.** `llm-evaluation/`·`embedding-evaluation/`·`stt-evaluation/` 같은
평가 하네스가 실험에 쓰는 프롬프트·Case는 각 폴더의 `EVALUATION_HISTORY.md`가 별도로 관리한다. 이
문서는 **실제 서비스 코드(`workmate-agent/app/`)가 프로덕션에서 호출하는 프롬프트만** 다룬다.

## 목록

| # | 이름 | 호출 위치 | 시나리오 |
| --- | --- | --- | --- |
| 1 | 회의 분석 | [`app/meeting_analysis.py`](../workmate-agent/app/meeting_analysis.py) `analyze_transcript()` | [04 §3](04-scenarios.md#3-회의록-입력-및-분석) |
| 2 | Gmail 할 일 후보 추출 | [`app/email_action_items.py`](../workmate-agent/app/email_action_items.py) `extract_action_items()` | [04 §7](04-scenarios.md#7-gmail-읽음-메일의-할-일-제안) |
| 3 | 주간 업무보고 요약 | [`app/workflows/weekly_report.py`](../workmate-agent/app/workflows/weekly_report.py) | [04 §2](04-scenarios.md#2-주간-업무보고) |

세 곳 모두 07-technical-specification.md §9.1의 기본 LLM(`openai/gpt-4.1-mini`, `temperature=0`)과
`response_format: json_schema`(`strict: true`)를 쓴다 — Provider가 스키마를 어긴 응답을 내면 그 자체가
실패로 처리되고, LLM이 자유 형식 텍스트로 답하게 두지 않는다.

---

## 1. 회의 분석

**위치**: [`app/meeting_analysis.py:46`](../workmate-agent/app/meeting_analysis.py) — `analyze_transcript()`

**입력**: 최종 확정된 회의 Transcript 전문(문자열 하나, User 메시지로 그대로 전달)

**System Prompt**:

```
Return only the requested JSON schema. Every evidence_text MUST be an exact contiguous
substring copied from the transcript; never invent or translate evidence. Use empty
action_items when no explicit action exists.
```

**응답 Schema** (`meeting_analysis`, strict):

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `summary` | string | 회의 요약 |
| `action_items[].action_item_id` | string | LLM이 자체적으로 매기는 값 — 전역 유일성이 보장되지 않아 서버가 `(action_item_id, meeting_id)` 복합 키로 저장한다(2026-08-15, [14번 문서](14-workmate-ui-integration-gaps.md) 참고) |
| `action_items[].title` | string | 할 일 제목 |
| `action_items[].assignee_id` | string \| null | 담당자(있으면) |
| `action_items[].due_at` | string \| null | 마감(있으면) |
| `action_items[].evidence_text` | string | 원문에서 그대로 복사한 근거 문장 |
| `action_items[].start_ms` / `end_ms` | integer | 근거 구간(밀리초) |

**서버 측 후검증**: LLM 응답을 그대로 신뢰하지 않는다 — 각 `action_item`의 `evidence_text`가 실제
Transcript 원문의 부분 문자열인지, `end_ms >= start_ms`인지 코드가 다시 검사하고 하나라도 어기면
`MeetingAnalysisProviderError`로 실패 처리한다(`evidence_text`를 LLM이 지어내거나 번역해 반환하는 것을
막기 위함, 07 §9.1 "LLM이 작성한 인용문을 원문으로 신뢰하지 않는다"와 같은 원칙).

---

## 2. Gmail 할 일 후보 추출

**위치**: [`app/email_action_items.py:37`](../workmate-agent/app/email_action_items.py) — `_SYSTEM_PROMPT`,
`extract_action_items()`

**입력**: `제목: {subject}\n\n본문:\n{body[:8000]}` (User 메시지, 본문은 8000자로 자름)

**System Prompt**:

```
너는 업무 메일을 검토해 실제로 할 일(Task)로 등록할 가치가 있는 항목만 추려내는 보조자다. 다음은
절대 할 일로 만들지 마라: 단순 정보 공유·공지·광고·뉴스레터, 전달(FYI)만 목적인 메일, 배달 실패·
시스템 알림, 이미 완료된 일을 보고하는 내용. 발신자가 명시적으로 요청·확인·승인·검토를 요구하거나
마감이 있는 항목만 할 일로 인정한다. 근거가 없으면 절대 지어내지 말고 action_items를 빈 배열로
반환하라. 제목은 메일 언어를 그대로 따르고, 무엇을 해야 하는지 한 문장으로 명확히 적어라.
```

**응답 Schema** (`email_action_items`, strict):

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `action_items[].title` | string | 할 일 제목(메일 언어 그대로) |
| `action_items[].reason` | string | 왜 할 일로 판단했는지 근거 |

메일 한 통이 여러 할 일 후보를 낼 수도, 0개를 낼 수도 있다(단순 정보 공유 메일 등). `evidence_text`
검증 같은 원문 대조 후검증은 없다 — `reason`은 사람이 승인 여부를 판단하는 참고 문구일 뿐 회의 분석의
`evidence_text`처럼 원문 부분 문자열로 강제하지 않는다.

---

## 3. 주간 업무보고 요약

**위치**: [`app/workflows/weekly_report.py:151`](../workmate-agent/app/workflows/weekly_report.py)

**입력**: 그 주 Task·회의 집계 결과를 JSON으로 직렬화한 값(User 메시지) — Task 상태·`source_refs`는
LLM이 절대 바꾸지 않는다는 전제로 만든 입력이다.

**System Prompt**:

```
주간 업무 데이터를 근거로 한국어 요약을 작성한다. 입력의 Task 상태와 source_refs는 변경하지 않는다.
```

**응답 Schema** (`weekly_report_summary`, strict):

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `summary` | string (1~3000자) | 주간 요약 텍스트 |

완료·진행 중·지연 업무 분류나 "다음 주 계획" 같은 나머지 보고서 항목은 이 LLM 호출이 아니라 코드가
결정적으로 집계한다 — LLM은 이미 계산된 값을 한국어 문장으로 다듬는 역할만 한다.

---

## LLM을 쓰지 않는 곳 (혼동 방지용)

아래는 이름만 보면 LLM을 쓸 것 같지만 실제로는 결정적 코드로만 처리한다:

- **오늘 브리핑**(`daily_briefing`): Gmail·Calendar Provider 결과를 규칙대로 모아 보여줄 뿐 LLM 요약을
  거치지 않는다.
- **우선순위 계산**(`rank_priorities`): [03 §6](03-data-priority-rules.md)의 점수 공식으로 계산한다.
- **회의록 검색 답변**(`search_meetings`): `MeetingAnswerService`가 검색된 근거 Chunk를 고정된 한국어
  템플릿(`"'{query}'에 대해 검색된 회의 근거입니다..."`)에 채워 넣을 뿐 LLM 생성이 아니다.

> 이 문서를 작성하며 07-technical-specification.md §9.1의 "LLM 사용 위치" 목록이 위 실제 구현과 다르다는
> 것(예전 서술은 "브리핑과 주간 보고서 작성"·"검색 Context 기반 답변"도 LLM을 쓴다고 돼 있었음)을
> 발견해 07번 문서도 같이 정정했다(2026-08-15).

## 변경 이력

- 2026-08-15: 초안 작성. 코드 전수 검색(`"role": "system"`)으로 실제 프로덕션 LLM 호출 3곳(회의 분석,
  Gmail 할 일 추출, 주간 보고서 요약) 확인. 이 과정에서 07번 문서 §9.1의 "LLM 사용 위치" 서술이 실제
  구현과 다르다는 것(브리핑·검색 답변은 LLM을 쓰지 않음)을 발견해 07번 문서도 함께 정정.
  `docs/README.md` 목차에 16번으로 등재.
