# W2-3 — 선행 조건

> [30-2-w2-graph-foundation.md](30-2-w2-graph-foundation.md) §3의 상세 문서.

## 1. 선행 조건 목록

| ID | 조건 | 출처 | 확인 방법 | 미충족 시 |
| --- | --- | --- | --- | --- |
| W2-E1 | W1 계약 스냅샷이 전건 PASS | [30-1](30-1-w1-contract-snapshot.md) §9 | `uv run python -m unittest tests.contracts.test_contract_snapshots -v` | W2 착수 금지 |
| W2-E2 | 기준선 테스트가 유지됨 | [30-0](30-0-w0-baseline.md) §10 | 전체 스위트 실행 | 원인 규명 후 착수 |
| W2-E3 | 기준 Commit이 고정돼 있음 | [30-0](30-0-w0-baseline.md) §10 | `git status --porcelain`이 비어 있음 | 미커밋 변경 처리 후 착수 |
| W2-E4 | 테스트용 PostgreSQL이 기동 중 | [30-0](30-0-w0-baseline.md) §10.1 | `docker ps`에 `workmate-test-pg` | 컨테이너 재기동 |
| W2-E5 | 전환 브랜치가 준비됨 | 계획서 §5 | `git branch --show-current` = `feat/lg-rewrite` | 브랜치 생성 |

## 2. 각 조건의 근거

### 2.1 W2-E1 — 왜 스냅샷이 먼저여야 하는가

W1 스냅샷은 **옛 구현이 살아 있는 동안에만** 만들 수 있다. W2는 아직 옛 구현을 지우지 않지만, W2에서
의존성(`langchain-openai`)이 추가되고 `uv.lock`이 갱신되면 기존 LLM 호출 경로의 실행 환경이 미세하게
달라질 수 있다.

스냅샷이 이미 확보돼 있으면 그 차이가 드러난다. 확보 전이면 "원래 그랬는지 W2가 바꾼 건지"를 판정할
수단이 없다.

### 2.2 W2-E2 — 기준선 유지 확인

W0 기준선은 **440 passed / 0 failed / 0 skipped**다. W2 착수 직전 다시 한 번 확인한다. W0과 W2 사이에
W1 작업이 있었으므로, W1이 기존 테스트에 영향을 주지 않았음을 확인하는 의미도 있다.

기대값: 440 + W1 신규 스냅샷 테스트, 실패 0.

### 2.3 W2-E3 — 기준 Commit 고정

W2는 의존성을 바꾼다. 의존성 변경은 되돌릴 일이 생겼을 때 "어느 시점으로 되돌릴지"가 명확해야 한다.
작업 트리에 정체불명의 변경이 섞여 있으면 revert 범위를 특정할 수 없다.

### 2.4 W2-E4 — PostgreSQL 기동

W2-T6(Checkpointer)은 `AsyncPostgresSaver`를 다룬다. `DATABASE_URL` 분기(W2-R6)를 검증하려면 실제
PostgreSQL이 필요하다. SQLite 경로만 확인하고 넘어가면 운영 백엔드가 미검증으로 남는다.

W0에서 구성한 컨테이너를 그대로 쓴다.

```
docker run -d --name workmate-test-pg \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=workmate_test \
  -p 55432:5432 pgvector/pgvector:pg16
```

### 2.5 W2-E5 — 전환 브랜치

계획서 §7.1에 따라 전환은 `feat/lg-rewrite` 단일 브랜치에서 진행한다. `main`과 현재 작업 브랜치
(`feat/M0.1-01-sdk-runtime`)는 전환 기간 내내 옛 구조를 유지한다.

브랜치 생성 시점은 W1 착수 전이 자연스럽지만, 늦어도 W2 전에는 있어야 한다. W2부터 의존성이
바뀌므로 기준 브랜치와 격리돼야 한다.

## 3. 착수 전 확인 명령

```bash
cd workmate-agent

# W2-E3
git status --porcelain            # 출력 없어야 함
git rev-parse --short HEAD        # 기준 Commit과 일치

# W2-E5
git branch --show-current         # feat/lg-rewrite

# W2-E4
docker ps --filter name=workmate-test-pg --format "{{.Status}}"

# W2-E1, W2-E2
WORKMATE_TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55432/workmate_test" \
  uv run python -m unittest discover -s tests -v
```

## 4. 환경 전제 (조건은 아니지만 확인 필요)

| 항목 | 값 | 확인 |
| --- | --- | --- |
| Python | 3.12.13 (`>=3.12,<3.13`) | `uv run python -V` |
| uv | 0.11.x | `uv --version` |
| 네트워크 | PyPI 접근 가능 | W2-T1에서 패키지 다운로드 필요 |
| OS | Windows 11 | Selector Event Loop 설정 유지 확인([30-2-10](30-2-10-risks.md) W2-K5) |

**네트워크 접근은 W2에서 처음 필수가 된다.** W0·W1은 기존 의존성만 썼지만 W2-T1은 새 패키지를
받아야 한다. 오프라인 환경이면 W2 자체가 진행되지 않는다.

## 5. 미충족 시 처리

| 조건 | 미충족 상황 | 처리 |
| --- | --- | --- |
| W2-E1 | 스냅샷 일부 실패 | W1로 복귀. 정규화 보완 후 재시도([30-1](30-1-w1-contract-snapshot.md) §11) |
| W2-E1 | 스냅샷 미작성 Skill 존재 | W1 §11의 "검증 불가 사유" 기록이 있으면 진행 가능. 없으면 복귀 |
| W2-E2 | 기존 테스트 실패 | **착수 금지.** 기준선이 깨진 상태로 전환하면 원인 분리 불가 |
| W2-E3 | 미커밋 변경 존재 | 변경 주체를 확인하고 커밋 또는 보류. 임의 폐기 금지 |
| W2-E4 | 컨테이너 미기동 | 재기동. 이미지가 없으면 다시 받는다 |
| W2-E5 | 브랜치 없음 | 기준 Commit에서 생성 |

## 6. 후행 단계의 선행 조건에 미치는 영향

W2의 검증 결과는 W3의 선행 조건이 된다.

| W2 검증 | W3 선행 조건 | 관계 |
| --- | --- | --- |
| W2-V1~V9 전체 | W3-E2 | W2가 완료돼야 W3 착수 |
| **W2-V6 (LLM 구조화 출력 동등성)** | W3-E3 | **미충족 시 LLM 의존 Skill 착수 금지** |

W3-E3이 별도로 존재하는 이유는, 결정적 Skill(`rank_priorities` 등)은 LLM 동등성과 무관하게 진행할 수
있기 때문이다. W2-V6만 실패한 경우 W3의 일부는 착수 가능하다.

## 7. 참조

- [30-0](30-0-w0-baseline.md) §10 — 기준선 확정값
- [30-1](30-1-w1-contract-snapshot.md) §9, §11 — 스냅샷 완료 정의와 중단 기준
- [30-3](30-3-w3-skill-subgraphs.md) §3 — W3의 선행 조건
