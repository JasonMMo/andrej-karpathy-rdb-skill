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
  columns:
    - { name, type, pk, null, unique, default, comment }
  indexes:
    - { name, columns, unique, method }
  constraints:
    - { name, check }                # CHECK constraint
```

## Relation 객체
```yaml
- from: <entity_name>
  to: <entity_name>
  cardinality: 1:1|1:N|N:M
  fk:
    column: <column_name>
    on_delete: restrict|cascade|set_null
  concept_name: <string>             # 원천 concept (역추적용)
```

N:M은 별도 join entity로 자동 변환 또는 explicit join entity 정의 둘 다 허용.

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
