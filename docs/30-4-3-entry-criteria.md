# W4-3 — 선행 조건

> [30-4-w4-root-graph.md](30-4-w4-root-graph.md) §3의 상세 문서.

## 1. 선행 조건 목록

| ID | 조건 | 출처 | 확인 방법 | 미충족 시 |
| --- | --- | --- | --- | --- |
| W4-E1 | W3 완료 — Skill Subgraph **11개 전부** | [30-3-9](30-3-9-exit-criteria.md) | `ls app/graph/skills/` | 착수 금지 |
| W4-E2 | W3-V1 스냅샷 전건 PASS | 동상 | 대조 실행 | 착수 금지 |
| W4-E3 | Skill 간 직접 import 없음 | [W3-V9](30-3-7-verification.md) | grep | 순환 의존으로 합성 불가 |
| W4-E4 | W2 Checkpointer 동작 확인 | [W2-V4](30-2-7-verification.md) | W2 증빙 | Checkpointer 결합 불가 |
| W4-E5 | 승인 Skill Schema 파일 존재 | — | `docs/schemas/workmate-skill-schemas.schema.json` | `validate_contract` 구현 불가 |
| W4-E6 | Subgraph 주입 인터페이스 정의 | [W3-D2](30-3-5-design.md) §4 | W3 산출물 | 합성 방식 미정 |

## 2. 각 조건의 근거

### 2.1 W4-E1 — 11개 전부여야 하는 이유

**부분 완료로 W4에 올 수 없다.** Root Graph는 `skill_id` 11개를 라우팅 대상으로 갖는다. 하나가 없으면

- `route_skill`의 path map이 불완전해진다
- W4-V1(라우팅 검증)이 성립하지 않는다 — "11개 각각 호출" 자체가 불가
- 없는 Skill을 호출하면 W4-R7(미등록 Skill 처리)과 구분되지 않는다

W3이 Skill 단위 부분 완료를 허용하는 것과 대조적이다([30-3-9](30-3-9-exit-criteria.md) §2.1).

### 2.2 W4-E2 — 대조 기준선

W4는 같은 스냅샷을 **Root Graph를 경유해** 다시 대조한다(W4-V6). W3에서 이미 PASS인 상태여야
"W4가 추가한 공통 노드 때문에 값이 달라졌다"를 분리할 수 있다.

```
W3: Subgraph 직접 호출 → 대조 PASS
W4: Root Graph 경유    → 대조 PASS여야 함
     차이가 나면 원인은 공통 노드 6종 중 하나
```

### 2.3 W4-E3 — 순환 의존 차단

Skill Subgraph가 서로를 직접 import하면 Root가 조립할 때 순환이 생긴다. 특히 `assistant_ask`가
나머지 10개를 import하고, Root가 11개를 전부 import하는 구조가 되면 import 순서에 따라 실패한다.

W3에서 주입 방식(W3-D2)으로 설계했으므로, W4는 그 인터페이스에 실제 값을 넣기만 한다.

```
grep -rn "from app.graph.skills" app/graph/skills/
```

기대: 출력 없음.

### 2.4 W4-E4 — Checkpointer

W4-T5에서 `build_workmate_graph(checkpointer=...)`로 결합한다. W2에서 생성·저장·복원이 확인되지
않았다면 W4에서 문제가 생겨도 원인이 Checkpointer인지 Graph 결합인지 모른다.

### 2.5 W4-E5 — Schema 파일

`validate_contract` 노드가 검증에 쓸 Schema가 필요하다. 현재 테스트가 쓰는 경로를 그대로 쓴다.

```python
# test_priority_workflow.py:70
schema_path = Path(__file__).resolve().parents[2] / "docs" / "schemas" / "workmate-skill-schemas.schema.json"
```

**운영 경로에서 이 파일을 어떻게 찾을지**가 W4의 설계 항목이다. 테스트처럼 상대 경로로 올라가는
방식은 Docker 이미지에서 깨질 수 있다
([이전 커밋 `62f38c5`](../workmate-agent/)가 "vendor docs/schemas + bake into Docker image" 를 한 배경).

### 2.6 W4-E6 — 주입 인터페이스

W3에서 `build_assistant_router_graph(*, subgraphs=...)` 형태로 정의했다. W4는 이 맵을 만들어 넘긴다.
인터페이스가 확정되지 않았으면 W3으로 돌아간다.

## 3. 착수 전 확인 명령

```bash
cd workmate-agent

# W4-E1
ls app/graph/skills/                              # 11개 Subgraph
ls app/graph/skills/assistant_skills/             # 5개

# W4-E3
grep -rn "from app.graph.skills" app/graph/skills/   # 출력 없음

# W4-E5
ls ../docs/schemas/workmate-skill-schemas.schema.json

# W4-E2, W4-E4
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

## 4. 환경 전제

| 항목 | 이유 |
| --- | --- |
| 테스트 PostgreSQL | `persist_result`·Checkpointer의 Postgres 경로 검증 |
| 임시 SQLite | 기본 경로 |

## 5. 미충족 시 처리

| 조건 | 미충족 상황 | 처리 |
| --- | --- | --- |
| W4-E1 | Skill 10개만 완료 | **W3으로 복귀.** 부분 완료로 진행 불가 |
| W4-E2 | 스냅샷 일부 실패 | W3에서 해소 |
| W4-E3 | 직접 import 발견 | W3-T7로 복귀해 주입 방식으로 수정 |
| W4-E4 | Checkpointer 미검증 | W2로 복귀 |
| W4-E5 | Schema 파일 없음 | 경로 확인. 배포 경로 문제면 W4 설계 항목으로 다룬다 |
| W4-E6 | 인터페이스 미정 | W3-T0으로 복귀 |

## 6. 후행 단계의 선행 조건에 미치는 영향

| W4 결과 | W5 선행 조건 | 관계 |
| --- | --- | --- |
| `build_workmate_graph()` 동작 | [W5-E1](30-5-w5-entrypoint-swap.md) | 교체 대상 |
| W4-V3(멱등성) PASS | W5-E2 | **멱등성이 깨진 채 진입점을 바꾸면 중복 실행이 외부에 노출** |
| W4-V7(Checkpoint) PASS | W5-E3 | |
| W4-V6(Root 경유 스냅샷) | W5-V7의 기준선 | |

## 7. 참조

- [30-3-9](30-3-9-exit-criteria.md) — W3 완료 정의
- [30-2-7](30-2-7-verification.md) — W2 Checkpointer 검증
- [30-4-5](30-4-5-design.md) — Schema 경로 설계
