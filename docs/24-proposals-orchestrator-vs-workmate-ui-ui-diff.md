# 오케스트레이터 vs workmate-ui "제안함" UI(시각) 차이 분석

작성일: 2026-08-19
상태: 분석·기록만(구현 항목 아님) — [23번 문서](23-proposals-orchestrator-vs-workmate-ui-diff.md)가
다룬 "로직" 차이와 짝을 이루는 "화면에 실제로 어떻게 보이는가" 관점의 분석

## 배경

23번 문서는 인증 방식·SSE 생명주기 등 **동작 로직**의 차이를 다뤘다. 이 문서는 그와 별개로,
같은 화면을 실제로 렌더링했을 때 **눈에 보이는 결과물**이 얼마나 다른지를 JSX·CSS를 직접 대조해
정리한다. workmate-ui는 `app/views/Proposals.tsx` + `app/views/ToastStack.tsx` +
`app/globals.css`, 오케스트레이터는 `MainUiPanels.tsx`의 `ProposalsDetailPanel`/`ProposalsInner`/
`ProposalCard`를 대상으로 한다.

## 요약 표

| 요소 | workmate-ui | 오케스트레이터 | 체감 차이 |
| --- | --- | --- | --- |
| CSS 방식 | `.panel`/`.primary`/`.secondary`/`.muted`/`.source-status` 등 공유 클래스(디자인 토큰) 재사용 | 전용 CSS가 아예 없음(`styles.css`에 `.proposals-detail` 규칙 0건) — 전부 요소별 인라인 `style={{...}}` | 오케스트레이터는 값을 손으로 복붙해 화면 간 색상·여백이 미묘하게 어긋날 여지가 있음 |
| 승인/무시 버튼 | `className="primary"`(초록 채움)/`"secondary"`(흰 배경+테두리) — 시각적으로 주/보조가 구분됨 | `<button type="button">`에 className 없음 — 브라우저 기본 버튼 모양, 승인·무시가 똑같이 생김 | 어떤 버튼이 "권장 동작"인지 시각적으로 구분이 안 됨 |
| SSE·데스크톱 알림 상태 표시 | `<i className={connected ? "ok" : "warn"} />` — 초록/주황 점 색으로 상태를 즉시 구분 | 고정 회색 "●" 문자 — 연결 여부와 무관하게 항상 같은 색 | 오케스트레이터는 텍스트를 읽어야만 SSE가 끊겼는지 알 수 있음 |
| 새 제안 Toast | 흰 카드 + 그림자(`box-shadow`), 출처별 이모지(✉️/📅), "제안함으로 가기"/"무시" 두 버튼, 화면 어디서든 상단(top:84) | 진한 초록 배경(`#19352c`)의 단색 알약형 박스, 아이콘 없음, 클릭하면 그냥 닫힘(이동 버튼 없음), 제안함 탭 안에서만(top:16) | 오케스트레이터 Toast는 "알림"이라기보다 "잠깐 뜨는 라벨"에 가까움 — 이동 동작이 없는 건 23번 문서가 지적한 탭 스코프 SSE의 자연스러운 결과 |
| 읽지 않은 제안 배지(종 아이콘) | Shell 상단에 `.bell` 버튼 — `♢` 아이콘 + 주황 숫자 배지(`unseenCount`), 클릭 시 제안함으로 이동(`app/page.tsx`) | `unseenCount`를 계산은 하지만(`proposal-notifications.tsx`) **어디에도 렌더링하지 않음** — 죽은 값 | 오케스트레이터엔 "안 읽은 제안이 몇 건인지" 한눈에 보여주는 UI 자체가 없음 |
| 카드 안 이메일 본문 스니펫 | `metadata.snippet`을 카드에 그대로 보여줌(HTML 엔티티 디코딩 포함) | **렌더링 안 함** — `ProposalCard`에 `snippet` 참조 자체가 없음 | 오케스트레이터에서는 메일 제목·날짜만 보이고 무슨 내용인지 카드에서 못 봄 |
| LLM 추천 이유 | `metadata.reason`을 💡 이모지 + 초록 텍스트로 보여줌("왜 이걸 제안했는지") | **렌더링 안 함** | 왜 이 제안이 떴는지 설명이 아예 안 보임 |
| 제안 ID 노출 | 카드 헤더 우측에 `proposal.proposal_id`를 `muted` 텍스트로 표시 | 표시 안 함 | 디버깅·문의 시 참조할 ID를 화면에서 못 찾음(사소하지만 실사용 중 문의 응대에 영향) |
| 공통 에러 표시 | `<ErrorState message={...} />` 공유 컴포넌트(하나로 통일된 배너 스타일) | `<p style={{color:"#bd655b", fontSize:12}}>{error}</p>` 인라인 — 페이지 레벨·카드 레벨 에러가 각각 다른 코드로 따로 그려짐 | 기능은 같지만 일관성 있는 컴포넌트가 아니라 매번 새로 그림 |
| 헤더 안내 문구 | "다른 화면에 있어도 우측 상단 Toast와 종 배지로 알려줍니다. (개발 환경: 2분마다 자동으로 Gmail·Calendar를 확인합니다...)" — 배경 동작을 사용자에게 설명 | "Gmail·Calendar에서 발행된 임시 Task 제안을 실시간으로 받고 승인·무시합니다." — 짧게 축약 | 오케스트레이터 사용자는 왜 2분마다 자동으로 뭔가 도는지, 다른 탭에 있으면 왜 알림이 안 오는지 화면에서 설명을 못 받음(23번 문서가 지적한 실제 동작 차이와도 맞물림 — 애초에 다른 탭에서는 안 되므로 그 문구를 그대로 옮기지 않은 것으로 보임) |

## 상세

### 1. 디자인 시스템 재사용 여부

workmate-ui는 이 화면을 "새 화면"으로 취급하면서도 새 CSS를 추가하지 않고 기존
`.panel`/`.primary`/`.secondary`/`.muted`/`.badge-like` 토큰만 재사용했다고 코드 주석에 명시돼
있다(`Proposals.tsx:9-10`, `ToastStack.tsx:7-8`). 실제로 `.panel`(흰 배경, `border`, `border-radius:
16px`, `padding: 22px`)과 `.primary`(초록 채움)/`.secondary`(흰 배경+테두리)는 `app/globals.css`에
정의돼 있어 이 화면 전체가 다른 화면(할 일 관리·회의 관리 등)과 같은 시각 언어를 공유한다.

오케스트레이터는 outer wrapper에 `className="proposals-detail"`을 붙였지만 `styles.css`에 이
클래스에 대한 규칙이 **하나도 없다** — 실제 시각 효과는 전부 각 JSX 요소의 인라인 `style={{...}}`
에서 나온다(`padding:16, background:"#fff", border:"1px solid #dfe7e1", borderRadius:12` 같은 값이
Google 계정 연결 패널·Gmail 동기화 패널·Calendar 동기화 패널·각 제안 카드에 매번 따로따로
적혀 있다). 지금 보기엔 workmate-ui의 `.panel`과 색감이 비슷하지만(흰 배경, 옅은 회색 테두리,
둥근 모서리), **하나의 소스가 아니라 여러 곳에 같은 값이 반복**돼 있어 나중에 한 곳만 고치면
불일치가 생기기 쉬운 구조다.

### 2. 버튼 시각적 위계 — 주 동작(승인) vs 보조 동작(무시)

workmate-ui의 "승인" 버튼은 `.primary`(진한 초록 채움, 흰 글자)로, "무시"는 `.secondary`(흰
배경, 테두리)로 렌더링돼 사용자가 어떤 게 권장되는 동작인지 색으로 구분할 수 있다. 오케스트레이터의
"승인"·"무시" 버튼은 둘 다 `<button type="button">`에 className이 없어 브라우저 기본 버튼(대개
연회색 사각 버튼)으로 렌더링되고, 두 버튼이 서로 구분되지 않는다. 팝업 확인창의 "Google 계정
연결"/"연결 해제" 버튼도 마찬가지다.

### 3. 실시간 연결 상태 표시 — 색 신호 유무

workmate-ui는 `.source-status i.ok`(초록 점, `#43a975`)/`.warn`(주황 점, `#e7a439`)로 SSE·데스크톱
알림 상태를 색으로 즉시 알려준다. 오케스트레이터는 `● SSE {연결됨|연결 안 됨}`을 항상 같은 회색
(`#75867f`)으로 그린다 — 연결이 끊겨도 화면 색은 변하지 않고, 사용자가 텍스트를 직접 읽어야만
안다.

### 4. Toast(새 제안 알림)의 정보량과 상호작용

가장 큰 시각적 차이다.

- **workmate-ui** (`ToastStack.tsx`): 흰 카드 + 그림자, 출처별 이모지(✉️/📅), "새 제안 도착"
  레이블(초록, 굵게) + 제안 제목(별도 줄), 그 아래 "제안함으로 가기"(주 버튼, 클릭 시 제안함
  화면으로 이동 + Toast 닫힘)와 "무시"(보조 버튼, Toast만 닫고 제안 자체는 남김) 두 개의 명확한
  선택지. 화면 상단(top:84, header 아래)에 폭 340px로 쌓인다.
- **오케스트레이터**: 진한 초록 단색 배경(`#19352c`) 알약형 박스에 흰 글자로 "새 제안:
  {제목}" 한 줄만. 아이콘 없음. 박스 전체가 클릭 영역이고 누르면 그냥 닫힌다 — "이동" 개념
  자체가 없다(제안함 탭 안에서만 뜨는 구조이니 이동할 곳이 이미 지금 화면이라 자연스러운
  결과이긴 하다, 23번 문서 참고). 화면 최상단 모서리(top:16)에 폭 280px로 쌓인다.

기능적으로 "무시만 가능"이라는 점에서 오케스트레이터 쪽이 정보와 선택지 모두 더 적다.

### 5. 읽지 않은 제안 개수 배지 — 오케스트레이터엔 아예 없음

workmate-ui는 Shell 상단바에 원형 `.bell` 버튼(`♢` 문자 아이콘)을 두고, 안 읽은 제안이 있으면
주황 원형 배지에 숫자(9 초과 시 "9+")를 얹는다(`app/page.tsx:106-107`). 클릭하면 제안함 화면으로
바로 이동한다.

오케스트레이터의 `proposal-notifications.tsx`도 정확히 같은 계산식으로 `unseenCount`를
만든다(`proposals.filter((item) => !seenIds.has(item.proposal_id)).length`, 훅 반환값에도
포함돼 있다) — **그런데 이 값을 소비하는 곳이 코드 어디에도 없다.** `App.tsx`/`MainUiPanels.tsx`
전체를 찾아봐도 `unseenCount`를 렌더링하는 곳이 없다 — 계산은 하지만 화면에 못 보여주는 죽은
값이다. 즉 오케스트레이터 사용자는 제안함 탭을 직접 열어보기 전까지는 새 제안이 몇 건 쌓였는지
전혀 알 방법이 없다(23번 문서의 "탭을 벗어나면 SSE도 끊긴다"는 지적과 겹쳐, 사실상 제안함은
"직접 들어가 봐야만 아는" 화면이 됐다).

### 6. 카드 내용 — 스니펫·추천 이유가 빠짐

workmate-ui의 `ProposalCard`는 제목·날짜 아래에:

1. `metadata.snippet`(메일 본문 일부, HTML 엔티티 디코딩 처리) — 있으면 그대로 표시
2. `metadata.reason`(LLM이 이 메일/일정을 제안한 이유) — 있으면 💡 이모지와 함께 초록 텍스트로 표시

를 보여준다. 오케스트레이터의 `ProposalCard`는 제목·날짜 다음 바로 승인/무시 폼(제목·담당자·
마감·우선순위 입력 필드)으로 넘어간다 — `snippet`/`reason`을 참조하는 코드 자체가 없다. 실사용
관점에서는 **오케스트레이터 사용자가 카드만 보고는 "이 메일이 무슨 내용인지", "왜 이게
제안됐는지"를 알 수 없고, 제목과 날짜만으로 승인/무시를 판단해야 한다.**

### 7. 제안 ID 표시

workmate-ui는 카드 헤더 오른쪽에 `proposal.proposal_id`를 작은 회색 글씨로 보여준다(디버깅이나
문의 시 "어떤 제안인지" 특정하는 용도로 보인다). 오케스트레이터 카드에는 이 값이 아예 없다.

### 8. `.badge-like` 클래스는 사실 두 화면 다 시각 효과가 없다(참고)

workmate-ui의 카드 헤더 MAIL/CALENDAR 라벨에 `className="badge-like"`가 붙어 있어 "칩(pill)
배지"처럼 보일 거라 예상했지만, 실제로 `app/globals.css`를 포함해 workmate-ui 어디에도
`.badge-like`를 정의하는 CSS가 없다 — 정의되지 않은 클래스라 시각 효과가 전혀 없고, 결과적으로
그냥 `color: var(--green)`가 적용된 굵은 텍스트로 렌더링된다. 오케스트레이터의 동일 위치도
`<b style={{color:"#397454"}}>`로 사실상 같은 모양이다 — **이 항목은 진짜 차이가 아니다**(둘 다
"칩처럼 보이길 의도했지만 실제로는 색 있는 텍스트"인 상태).

## 정리

기능(승인/무시가 되는지, 필드 편집이 되는지)은 23번 문서가 확인한 대로 동일하지만, **화면에
실제로 보이는 정보량과 시각적 명확성은 오케스트레이터 쪽이 확연히 적다**:

- 카드에서 메일 내용·추천 이유를 못 보여준다 (6번)
- 안 읽은 제안 개수를 어디에도 안 보여준다 (5번)
- 연결 상태·주요 동작을 색으로 구분하지 못한다 (2, 3번)
- Toast가 "이동" 없이 "잠깐 보이고 사라지는 라벨"에 가깝다 (4번)

전부 코드가 없어서(렌더링 자체를 안 해서) 생긴 차이이지, 데이터가 없어서 생긴 차이가 아니다 —
즉 서버가 이미 내려주는 `metadata.snippet`/`metadata.reason`/`proposal_id`나 훅이 이미 계산해
둔 `unseenCount`를 오케스트레이터 프론트가 그냥 안 쓰고 있을 뿐이다. 개선하려면 API 변경 없이
`MainUiPanels.tsx`의 JSX만 손보면 된다 — 다만 이 문서는 분석·기록 목적이라 실제 수정은 하지
않았다.

## 완료 보고 (2026-08-19)

위 "정리"에서 언급한 항목 중 **5번(안 읽은 제안 배지)·6번(카드 스니펫·추천 이유)만** 반영했다 —
나머지(1·2·3·4·7·8번)는 이 요청 범위 밖이라 그대로 둔다.

### 6번 — 카드에 스니펫·추천 이유 추가

`MainUiPanels.tsx`의 `ProposalCard`에 workmate-ui `Proposals.tsx`와 같은 두 블록을 그대로
옮겼다 — 날짜 줄 다음, 승인/무시 폼 앞:

```tsx
{typeof (proposal.metadata as Record<string, unknown> | null)?.snippet === "string" && (
  <p style={{ margin: "0 0 8px", fontSize: 12, color: "#75867f" }}>{decodeHtmlEntities(String((proposal.metadata as Record<string, unknown>).snippet))}</p>
)}
{typeof (proposal.metadata as Record<string, unknown> | null)?.reason === "string" && (
  <p style={{ margin: "0 0 10px", fontSize: 12, color: "#397454" }}>💡 {decodeHtmlEntities(String((proposal.metadata as Record<string, unknown>).reason))}</p>
)}
```

`decodeHtmlEntities`는 이미 `workmate/format.ts`에서 import돼 있어 추가 import가 필요 없었다.
workmate-ui는 `className="muted"`/`var(--green)` 토큰을 쓰지만, 오케스트레이터는 이 파일 전체가
인라인 스타일 방식이라(위 "1. 디자인 시스템 재사용 여부" 참고) 같은 값을 인라인으로 옮겼다
(`#75867f`/`#397454` — 이 파일 다른 곳에서 이미 쓰던 것과 같은 색).

### 5번 — 안 읽은 제안 배지

`useProposalNotifications()`에서 `unseenCount`를 destructure해 "제안함" 제목 옆에 주황 원형
배지로 보여준다(workmate-ui `.bell em`과 같은 주황색 `#d66b34`, 9 초과 시 "9+").

**완전히 같은 경험은 아니다** — workmate-ui는 Shell 상단(`app/page.tsx`)에 이 배지를 올려
"제안함 탭을 안 열어도" 보이지만, 오케스트레이터는 `ProposalNotificationsProvider`가
[23번 문서](23-proposals-orchestrator-vs-workmate-ui-diff.md)가 지적한 대로 "제안함" 탭
안에서만 마운트돼 있어 탭 밖에 배지를 놓을 자리가 없다. Provider를 App.tsx Shell로 올리는 건
이번 범위를 넘는 더 큰 구조 변경(23번 문서 "남는 질문"에 이미 기록됨)이라 손대지 않았다 —
대신 지금은 **탭에 들어온 직후** 제목 옆에 배지가 뜬다. 다만 같은 컴포넌트의
`useEffect(() => { markAllSeen(); ... }, [proposals.length])`가 마운트 직후 바로 읽음 처리를
하므로, 배지는 첫 렌더와 그 Effect가 도는 사이 **잠깐만 보였다가 0으로 사라진다** — "탭 밖에서도
안 읽은 개수를 계속 보여주는" workmate-ui 수준의 배지는 아니고, 최소한 "죽은 값이던 `unseenCount`
를 화면에 실제로 쓰기 시작했다" 정도의 개선이다.

### 검증

- `tsc --noEmit`: 클린
- `vite build`: 클린(`✓ built in 12.72s`)
- 실사용 화면 확인(브라우저)은 하지 않음 — 다음에 localhost:5173에서 실제 메일/일정 동기화
  후 카드에 스니펫·이유가 뜨는지, 탭 진입 순간 배지가 잠깐 뜨는지 직접 확인 필요

## 관련 문서

- [23-proposals-orchestrator-vs-workmate-ui-diff.md](23-proposals-orchestrator-vs-workmate-ui-diff.md)
  — 같은 두 화면의 로직(인증·SSE 생명주기 등) 차이.
- [19-workmate-ui-orchestrator-port-plan.md](19-workmate-ui-orchestrator-port-plan.md) — 제안함
  이식 계획(7단계)과 "범위를 하나 좁혔다"는 기록.
