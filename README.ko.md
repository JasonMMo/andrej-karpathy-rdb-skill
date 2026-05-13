# andrej-karpathy-rdb-skill

> Andrej Karpathy의 LLM Wiki 패턴을 관계형 DB 스키마 설계에 이식한 Claude Code 플러그인. 한국어 기본.

## 무엇인가
markdown + frontmatter로 비즈니스 도메인·엔티티·관계를 정의하고, 한 번의 컴파일로 `_blueprint.yaml` manifest를 산출. 2단계 DDL 생성 플러그인이 manifest를 입력으로 받아 PostgreSQL DDL을 생성한다.

**핵심 철학**:
- ✅ markdown + YAML frontmatter (no vector DB, no RAG)
- ✅ 사람은 wiki만 큐레이션, LLM이 컴파일·검증
- ✅ Wiki-first: markdown이 진실의 근원
- ✅ 한국어 기본, 식별자는 영문

## 설치
```
/plugin install andrej-karpathy-rdb-skill@<marketplace>
```

또는 git clone 후 marketplace에 등록.

## 빠른 시작
```
# 1. wiki 골격 설치 + 고객관리 프리셋 적용
/karpathy-rdb init 고객관리 --preset 고객관리

# 2. 요구사항 ingest (자유 프롬프트)
/karpathy-rdb ingest 고객은 이름과 이메일을 가지며, 이메일은 유일하다.
                     주소는 여러 개 등록할 수 있고 기본 주소를 1개 지정한다.

# 3. 컴파일 (wiki → _blueprint.yaml + 정합성 검증)
/karpathy-rdb compile

# 4. _blueprint.yaml을 2단계 DDL 생성 플러그인에 전달
```

## 슬래시 커맨드

| 커맨드 | 기능 |
| :-- | :-- |
| `/karpathy-rdb init <도메인> [--preset <key>]` | wiki 골격 + 프리셋 설치 |
| `/karpathy-rdb ingest [<프롬프트>\|--file <path>]` | 요구사항 → wiki 페이지 |
| `/karpathy-rdb compile` | wiki → `_blueprint.yaml` |

## 도메인 프리셋 카탈로그

| 프리셋 | 시드 entities | 시드 concepts |
| :-- | :-- | :-- |
| 고객관리 | customer, address, contact_log | customer↔address(1:N), customer↔contact_log(1:N) |
| 주문관리 | sales_order, order_item, payment | sales_order↔order_item(1:N), sales_order↔payment(1:1) |
| 재고관리 | product, sku, warehouse, stock | product↔sku(1:N), sku↔warehouse(N:M via stock) |
| 인사관리 | employee, department, position | dept↔employee(1:N), position↔employee(1:N), dept↔dept(self) |
| 재무관리 | account, fiscal_period, ledger_entry | account↔account(self), account↔ledger(1:N), period↔ledger(1:N) |

새 프리셋 추가는 `.claude/skills/karpathy-rdb/presets/README.md` 참조.

## wiki 디렉터리 구조 (설치 후)
```
wiki/
├── _schema.md / _protocols.md / _log.md
├── _blueprint.yaml          ← compile 산출물
├── compile-report.md        ← 검증 보고서
├── raw/                     ← 원본 요구사항
├── sources/                 ← LLM 압축 요약
├── domains/                 ← 비즈니스 도메인
├── entities/                ← DB 테이블 정의
├── concepts/                ← ER 관계·비즈니스 규칙
├── decisions/, explorations/, comparisons/
└── rules.md / false-beliefs.md
```

## frontmatter 표준
- Entity: `entities/<name>/profile.md` — PK/FK/columns/indexes/constraints/relations
- Concept: `concepts/<name>.md` — relation/rule/invariant/terminology
- Domain: `domains/<name>/profile.md` — 소속 entities/concepts

자세한 스키마는 `.claude/skills/karpathy-rdb/references/frontmatter-schema.md`.

## `_blueprint.yaml` 스키마 (2단계 핸드오프)
`.claude/skills/karpathy-rdb/references/blueprint-spec.md` 참조.

## 검증 코드 V001~V010

| 코드 | 레벨 | 검증 |
| :-: | :-: | :-- |
| V001 | ERROR | 모든 entity는 PK 컬럼 1개 이상 |
| V002 | ERROR | FK가 참조 PK/UQ 컬럼을 가리킴 |
| V003 | WARN | 컬럼명 snake_case + 예약어 회피 |
| V004 | WARN | FK 컬럼 타입이 참조 PK 타입과 동일 |
| V005 | WARN | 순환 의존 검출 (DAG) |
| V006 | WARN | concept이 참조하는 entity 미존재 |
| V007 | WARN | entity가 어느 domain에도 속하지 않음 |
| V008 | INFO | rules.md ↔ entity·concept 매핑 보고 |
| V009 | INFO | entity sources 누락 |
| V010 | INFO | locked entity는 decisions 1개 이상 권장 |

## 파이프라인 위치
business-fullstack-creater의 4단계 중 **1단계 (Plan)** 담당.

| 단계 | 산출물 | 도구 |
| :-: | :-- | :-- |
| 1 Plan | `_blueprint.yaml` | 본 플러그인 |
| 2 Backend | DDL + 마이그레이션 | 별도 플러그인 |
| 3 Middle | Spring Boot war | `/nexacro-fullstack-starter` |
| 4 Frontend | Nexacro project | `/nexacro-claude-skills` |

## 영감
- [Andrej Karpathy LLM Wiki pattern](https://x.com/karpathy/status/2039805659525644595)
- [Benboerba620/karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki) — 원본 구현 참조
