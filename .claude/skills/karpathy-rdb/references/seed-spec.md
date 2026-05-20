---
type: reference
---

# Preset Seed File Specification

본 문서는 `presets/<도메인>.seed.md`(및 동등 위치인 글로벌 카탈로그
`~/.karpathy-rdb/catalog/<도메인>.seed.md`)의 파일 구조를 정의한다.

이 컨벤션을 따르는 파일은:
- `protocol/01-init.md` Phase 3에서 wiki 초기화의 시드로 사용된다.
- `protocol/04-contribute.md`가 역류 머지의 대상으로 삼는다.
- Stage 2 catalog 외부화(`andrej-karpathy-rdb-ddl/catalogs/preset-catalog.yaml`)와
  대응을 이룬다 — seed 의 entity 목록이 catalog YAML 의 도메인 키와 일치해야
  contribute → init 의 복리 루프가 끊기지 않는다.

## 1. 파일 위치 및 명명

| 위치 | 용도 |
| :-- | :-- |
| `<plugin>/.claude/skills/karpathy-rdb/presets/<도메인>.seed.md` | 플러그인 빌트인 시드 |
| `~/.karpathy-rdb/catalog/<도메인>.seed.md` | 사용자 글로벌 시드 (contribute 출력) |

- 파일명: `<도메인>.seed.md` — `<도메인>` 은 한국어 또는 영문 단일 토큰
  (예: `고객관리`, `공급망`, `auth-rbac`). 공백·슬래시 금지.
- 두 위치에 동시 존재 시 우선순위: **글로벌 > 플러그인** (contribute로
  사용자가 명시적으로 확장한 시드를 존중).

## 2. Frontmatter (필수)

```yaml
---
preset: <도메인>      # 필수, 파일명과 동일해야 함
version: <int>        # 필수, 1부터 시작, contribute 시 자동 증분
---
```

| 필드 | 타입 | 필수 | 설명 |
| :-- | :-- | :-: | :-- |
| `preset` | string | ✅ | 도메인 식별자. 파일명(stem에서 `.seed` 제거)과 정확히 일치해야 한다. |
| `version` | int | ✅ | 시드 버전. 신규 시 1, contribute 시 +1. |

추가 키는 허용되지만 해석되지 않는다(향후 확장 여지).

## 3. 본문 구조

순서·제목은 다음과 같이 고정한다 — 파서가 H2 제목으로 섹션을 구분한다.

```markdown
# <도메인>

(선택) 도메인 개요 1~3 단락. 다른 도메인과의 연계 등 메타 설명.

## entities (시드)

### <entity_name>
\`\`\`yaml
type: entity
name: <entity_name>
...
\`\`\`

(엔티티 N개 반복)

## concepts (시드 관계)

### <concept_name>
\`\`\`yaml
type: concept
kind: relation
...
\`\`\`

(컨셉 M개 반복; relation 없는 도메인은 섹션 자체를 생략 가능)

## rules (시드 비즈니스 규칙)
- 규칙 1
- 규칙 2
- ...
```

### 3.1 H1
- 정확히 1개. 텍스트는 frontmatter `preset` 와 일치해야 한다.

### 3.2 `## entities (시드)` (필수)
- 0개 entity 인 도메인은 허용하지 않는다 (시드의 정의에 어긋남).
- 각 entity 는 `### <entity_name>` H3 + 바로 다음 ` ```yaml ``` ` 코드블록 1개.
- 코드블록 내부 스키마는 `references/frontmatter-schema.md` Entity 섹션을 따른다.
  최소 요건: `type: entity`, `name`, `domain` (배열), `status`, `columns`(PK 1개 이상).
- `name` 은 H3 텍스트와 동일해야 한다.
- `pattern` 필드(예: `L2`, `D2`, `MD`, `TR`, `RO`, `F1`, `C1`)는 권장 — Stage 4
  form_gen이 화면 패턴 결정에 사용한다.

### 3.3 `## concepts (시드 관계)` (선택)
- 보통 entity 간 FK 관계를 명시적 concept 으로 등재한다 — `kind: relation`,
  `from`/`to`/`fk_column`/`cardinality`/`on_delete`.
- entity `relations[]` 의 `concept: "[[<name>]]"` 참조가 이 섹션의 concept 을
  가리켜야 한다 (참조 무결성). 누락 시 ingest/init에서 빈 위키로 복사된 뒤
  Stage 1 컴파일러가 `fk_column` fallback 으로 보강하지만, 컨벤션상
  명시적 concept 등재가 정답.
- 도메인 내부에서 entity 가 1개뿐이거나 관계가 전혀 없으면 섹션 자체를
  생략해도 된다.

### 3.4 `## rules (시드 비즈니스 규칙)` (선택)
- 마크다운 bullet 리스트. 1줄 1규칙.
- `_log.md` 가 아닌 자연어 비즈니스 규칙 — 컴파일러가 직접 해석하지 않지만
  ingest 가 `wiki/rules.md` 시드로 복사한다.

## 4. 도메인 표기 컨벤션

- entity `domain:` 필드는 항상 **배열**. 단일 도메인 entity 도 `[고객관리]`.
- 같은 entity 가 여러 도메인에 속할 수 있다 (cross-domain). 예: `app_user`
  는 `[권한관리]` 단일이지만 `customer` 는 향후 `[고객관리, 영업관리]` 등으로
  확장될 수 있다. V007 (Stage 1) 이 이를 권장.
- 도메인 토큰은 다른 seed 파일명과 일치해야 cross-preset init 시 누락이 없다.

## 5. cross-preset 참조 (FK)

다른 preset 에 정의된 entity 를 FK 로 참조할 때:
- 참조 entity 의 정의는 **반복 등재하지 말 것** — 사용자가 두 preset 을
  init 시 함께 선택하도록 안내(개요 단락에 명시).
- `### <concept>` 에서 `from`/`to` 에 외부 entity 이름을 그대로 적는다.
  Stage 1 V005 가 cross-domain concept 까지 인식한다 (Growth-21b-4).

예 (`공급망.seed.md`):
> 기존 도메인과의 연계:
> - 재고관리(sku, warehouse): purchase_order_item·goods_receipt_item이 sku에 FK,
>   purchase_order·goods_receipt가 warehouse에 FK (입고 창고)
> - 권한관리(app_user): requester_user_id로 발주 요청자 RBAC와 직결

## 6. 변경 정책

- **신규 추가**: `version: 1`. `presets/INDEX.md` 동시 갱신 필수
  (`test_preset_index.py` 강제).
- **변경(contribute)**: protocol/04-contribute.md Phase 6 — `version` +1,
  사용자 confirm 항목만 머지. 자동 머지 금지.
- **삭제**: 비권장. 호환성 깨짐. 삭제 대신 `status: locked` + 도메인 개요에
  비활성 표기.

## 7. 검증

`tests/test_seed_spec.py` 가 본 컨벤션을 강제한다:
1. 모든 `presets/*.seed.md` 가 유효한 YAML frontmatter 를 가진다.
2. frontmatter `preset` 값이 파일명 stem 과 일치한다.
3. `version` 이 양의 정수다.
4. H1 텍스트가 `preset` 과 일치한다.
5. `## entities (시드)` 섹션이 존재하고 최소 1개의 `### <name>` + ```yaml ```
   블록을 가진다.
6. 각 entity YAML 블록의 `name` 이 그 H3 텍스트와 일치한다.

위반 발견 시 회귀 — 신규 contribute 작성자도 본 spec 한 페이지만 보면
컨벤션 충족 가능해야 한다.
