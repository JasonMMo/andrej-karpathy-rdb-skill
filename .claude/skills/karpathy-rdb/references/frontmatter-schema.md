---
type: reference
---

# Frontmatter Schema Reference

본 문서는 wiki/ 안의 모든 markdown 파일이 따라야 하는 YAML frontmatter 스키마를 정의한다.

## Entity (`entities/<name>/profile.md`)

| 필드 | 타입 | 필수 | 설명 |
| :-- | :-- | :-: | :-- |
| `type` | string | ✅ | 항상 `entity` |
| `name` | string | ✅ | snake_case 영문 식별자 |
| `display` | string | ⬜ | 한국어 표시명 |
| `domain` | string[] | ✅ | 소속 도메인 (1개 이상 권장 — V007) |
| `table` | string | ⬜ | 물리 테이블명 (기본 = `name`) |
| `schema` | string | ⬜ | PostgreSQL 스키마 (기본 `public`) |
| `status` | enum | ✅ | `draft` \| `reviewed` \| `locked` |
| `columns` | object[] | ✅ | 컬럼 정의. PK 1개 이상 — V001 |
| `indexes` | object[] | ⬜ | 인덱스 정의 |
| `constraints` | object[] | ⬜ | CHECK 등 추가 제약 |
| `relations` | object[] | ⬜ | 관계 (concept 링크) |
| `sources` | wikilink[] | ⬜ | 출처 (`[[sources/...]]`) |
| `decisions` | wikilink[] | ⬜ | 결정 로그 (locked일 때 권장 — V010) |

### `columns[]` 객체
```yaml
- name: <snake_case>           # 필수
  type: <pg type>              # 필수: bigserial, varchar(N), text, int, bool, timestamptz, numeric(p,s), jsonb, ...
  pk: <bool>                   # 기본 false
  null: <bool>                 # 기본 true
  unique: <bool>               # 기본 false
  default: <expr>              # SQL expression
  comment: <string>            # 선택
```

### `indexes[]` 객체
```yaml
- name: ix_<table>_<cols>      # 필수
  columns: [<col>, ...]        # 필수
  unique: <bool>               # 기본 false
  method: btree|gin|gist|hash  # 기본 btree
```

### `relations[]` 객체
```yaml
- kind: has_many|has_one|belongs_to|many_to_many   # 필수
  to: <entity name>            # 필수
  fk: <column name>            # 필수 (N 쪽 기준)
  concept: "[[<concept name>]]"  # 필수
```

## Concept (`concepts/<name>.md`)

| 필드 | 타입 | 필수 | 설명 |
| :-- | :-- | :-: | :-- |
| `type` | string | ✅ | 항상 `concept` |
| `kind` | enum | ✅ | `relation` \| `rule` \| `invariant` \| `terminology` |
| `name` | string | ✅ | `<from>-<verb>-<to>` 형식 권장 |
| `cardinality` | enum | ⬜* | `1:1` \| `1:N` \| `N:M` \| `self` (*kind=relation일 때 필수) |
| `from` | string | ⬜* | entity name (*kind=relation일 때) |
| `to` | string | ⬜* | entity name (*kind=relation일 때) |
| `fk_column` | string | ⬜* | FK 컬럼명 (*kind=relation일 때) |
| `on_delete` | enum | ⬜ | `restrict` \| `cascade` \| `set_null` (기본 restrict) |
| `status` | enum | ✅ | `draft` \| `reviewed` \| `locked` |

## Domain (`domains/<name>/profile.md`)

| 필드 | 타입 | 필수 | 설명 |
| :-- | :-- | :-: | :-- |
| `type` | string | ✅ | 항상 `domain` |
| `name` | string | ✅ | 식별자 |
| `display` | string | ⬜ | 한국어 표시명 |
| `description` | string | ⬜ | 한 줄 설명 |
| `entities` | string[] | ✅ | 소속 entity name 리스트 |
| `concepts` | string[] | ⬜ | 도메인 내부 concept 리스트 |
| `status` | enum | ✅ | `draft` \| `reviewed` \| `locked` |
