---
type: reference
---

# `_blueprint.yaml` Specification

본 문서는 1단계(`karpathy-rdb compile`)와 2단계(DDL 생성 플러그인) 사이의 공식 계약 스키마.

## 최상위 구조

```yaml
version: 1                          # 정수. 호환 변경 시 증가
generated_at: <ISO-8601>            # 컴파일 타임스탬프
project: <string>                   # wiki/_schema.md의 project name
domains: [...]                      # Domain 객체 배열
entities: [...]                     # Entity 객체 배열
relations: [...]                    # Relation 객체 배열
business_rules: [...]               # Business rule 객체 배열
sources: [...]                      # Source 메타 배열
validation:
  passed: <bool>
  errors: [...]
  warnings: [...]
  infos: [...]
```

## Domain 객체
```yaml
- name: <string>
  description: <string>
  entities: [<entity_name>, ...]
```

## Entity 객체
```yaml
- name: <snake_case>
  table: <string>
  schema: <string>
  extends: <catalog_entity_name>     # 선택. 글로벌 카탈로그의 base entity
  columns:
    - { name, type, pk, null, unique, default, comment }
  indexes:
    - { name, columns, unique, method }
  constraints:
    - { name, check }                # CHECK constraint
```

### `extends` 필드 (선택, v0.2+)
- 같은 이름 또는 `extends`로 명시한 catalog entity가 글로벌 카탈로그(`~/.karpathy-rdb/catalog/<도메인>.seed.md`)에 있으면, base의 columns/indexes/constraints를 상속한 뒤 본 entity의 동명 필드로 override
- 충돌 규칙: 컬럼 이름이 같으면 본 entity의 정의가 우선 (override)
- 카탈로그에 base가 없으면 명시적 에러 (silent fallback 금지) — 사용자가 의도를 분명히 하도록
- `extends` 필드 없는 기존 blueprint는 그대로 동작 (하위 호환). `version: 1` 유지.

## Relation 객체
```yaml
- from: <entity_name>
  to: <entity_name>
  cardinality: 1:1|1:N|N:M
  fk:
    column: <column_name> | [<col_a>, <col_b>]   # v0.3+: list = composite FK
    on_delete: restrict|cascade|set_null
  concept_name: <string>             # 원천 concept (역추적용)
```

N:M은 explicit junction entity로만 표현한다 (자동 변환 없음 — Karpathy 정신: 명시적·파일 기반).

### 복합 PK / 복합 FK / N:M junction (v0.3+)

- **복합 PK**: `entities[].columns[]` 중 둘 이상의 row가 `pk: true` 이면 자연 지원. Stage 2 가 단일 PK 일 때는 컬럼 인라인 `PRIMARY KEY`, 둘 이상일 때는 테이블 레벨 `PRIMARY KEY (a, b)` 로 emit.
- **복합 FK**: `relations[].fk.column` 을 list 로 선언:
  ```yaml
  relations:
    - from: child
      to: parent
      fk: { column: [a_id, b_id], on_delete: cascade }
  ```
  Stage 2 가 다중 컬럼 `FOREIGN KEY (a_id, b_id) REFERENCES parent(...)` 로 emit. 단일 컬럼은 string OR 1-원소 list 모두 허용 (하위 호환).
- **N:M junction**: 사용자가 junction entity 를 직접 선언한다 — PK = 두 FK 컬럼의 합, 비-PK 컬럼은 메타 컬럼 (`created_at` 등) 만. 양쪽 부모 entity 는 각각 `relations: [{kind: has_many, to: <junction>, fk: <one_col>}]` 로 junction 을 가리킨다. Stage 1 의 V005 가 junction 패턴을 감지해 INFO 메시지 (`validation.infos[]`) 를 emit. ERROR/WARN 아님 — 사용자 의도를 정보로 기록.

V005 판정 기준 (`scripts/rdb_index.py:is_junction_entity`): PK 컬럼이 2개 이상이고, PK 컬럼이 모두 outgoing FK 컬럼 집합에 포함되며, 비-PK 컬럼은 메타 컬럼 (`META_COLUMNS = {created_at, updated_at, created_by, updated_by}`) 뿐일 때.

### 입력(엔티티 frontmatter) → 출력(blueprint) 매핑

소스 wiki의 `entities/<name>/profile.md`는 `frontmatter-schema.md` 정의에 따라
flat 형식 `fk: <column>` 만 명시한다. `cardinality`와 `on_delete`는 링크된
`concepts/<name>.md`의 `cardinality` / `on_delete` 필드에서 가져온다.

| profile.md `relations[]` | concept | blueprint `relations[]` |
| :-- | :-- | :-- |
| `kind: has_many` | `cardinality: 1:N` | `cardinality: 1:N` |
| `kind: has_one` | `cardinality: 1:1` | `cardinality: 1:1` |
| `kind: many_to_many` | — | `cardinality: N:M` |
| `fk: <col>` | `fk_column: <col>` | `fk.column: <col>` (profile 우선) |
| (없음) | `on_delete: <v>` | `fk.on_delete: <v>` (없으면 `restrict`) |
| `concept: "[[name]]"` | — | `concept_name: name` |

## Business Rule 객체
```yaml
- id: BR-<NNN>
  text: <한국어 설명>
  enforced_by: [<constraint or index name>, ...]
  source_concept: <concept name>
```

## Source 객체
```yaml
- id: SRC-<NNN>
  file: <relative path from wiki/>
  title: <string>
```

## Validation 객체
```yaml
validation:
  passed: <bool>
  errors:
    - { code: V001, target: "entity:foo", message: "..." }
  warnings: [...]
  infos: [...]
```

## PostgreSQL 예약어 회피 목록 (V003)
다음 단어는 컬럼명·테이블명으로 권장하지 않음:
`user, order, group, table, schema, type, role, name, value, key, primary, foreign, references, default, check, unique, index, constraint, select, insert, update, delete, from, where, join, having, by, on, as, in, is, not, null, true, false`

전체 목록은 PostgreSQL 공식 문서의 `KEY_WORDS` 표 참조.

## 2단계 핸드오프 규약
- 2단계는 본 스키마의 `version`을 먼저 확인해야 함
- `validation.passed: false`이면 DDL 생성 거부
- `entities`·`relations`·`business_rules`만으로 DDL 생성 가능 (다른 필드는 참고용)
