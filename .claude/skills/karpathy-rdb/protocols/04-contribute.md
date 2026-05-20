---
type: protocol
protocol: contribute
version: 2
---

# Protocol 04 — Contribute

`/karpathy-rdb contribute <도메인명>` 실행 시 AI가 따르는 절차.
**목적**: 현재 프로젝트에서 새로 발견한 entity/concept/rule을 **글로벌 도메인 카탈로그**로 역류시켜 다음 프로젝트에서 재사용 가능하게 한다.

## 글로벌 카탈로그 위치
- 디렉터리: `~/.karpathy-rdb/catalog/`
- 도메인별 파일: `~/.karpathy-rdb/catalog/<도메인>.seed.md`
- 형식: 플러그인 `presets/<도메인>.seed.md`와 동일 (preset frontmatter + entities/concepts/rules 섹션)
- 디렉터리/파일이 없으면 자동 생성

## Phase 1 — 전제 검사
1. 현재 wiki(`wiki/_schema.md` 존재) 인지 확인. 아니면 abort.
2. `<도메인명>` 인자 검증. 빈 문자열·공백 금지.
3. 현재 프로젝트 wiki에 `wiki/learn-log.md`가 비어 있으면 사용자에게 alert: "이 프로젝트에서 신규 발견된 지식이 없음. ingest를 먼저 실행했는지 확인."

## Phase 2 — 후보 추출
다음 소스에서 `<도메인>`에 속하는 항목을 모두 모은다:
1. `wiki/entities/*/profile.md` — frontmatter `domain` 배열에 `<도메인>` 포함된 entity
2. `wiki/concepts/*.md` — 위 entity 사이의 concept (relation 등)
3. `wiki/rules.md` — `<도메인>` 태그가 있거나 위 entity를 참조하는 규칙
4. `wiki/learn-log.md` — `kind=new_*` 중 `domain=<도메인>` 항목 (보조 인덱스)

## Phase 3 — Diff
1. 대상 카탈로그 파일 결정:
   - `~/.karpathy-rdb/catalog/<도메인>.seed.md`가 있으면 그것이 base
   - 없으면 플러그인 `presets/<도메인>.seed.md`가 base (있는 경우만)
   - 둘 다 없으면 빈 base (신규 도메인)
2. base와 Phase 2 후보를 비교해 다음 분류:
   - **신규 entity** — base에 없는 entity 전체
   - **변경 entity** — 같은 이름 entity의 컬럼/제약 차이
   - **신규 concept** — base에 없는 concept
   - **신규 rule** — base에 없는 rule

## Phase 4 — 범용성 검증 (사용자 confirm, 항목별)
각 신규/변경 항목에 대해 사용자에게 한 번씩 묻는다:

> "[항목 표시] — 이 변경을 다른 프로젝트에도 적용할 만큼 범용적입니까? (yes/no/skip)"

- `yes` → 카탈로그에 병합
- `no` → 영구 제외 (이 프로젝트에서만 의미 있는 것으로 간주)
- `skip` → 이번 contribute에서 보류 (다음에 다시 물음)

**자동 머지 금지** — 사용자 confirm 없이 카탈로그 변경 절대 금지.

## Phase 5 — 충돌 처리
변경 entity의 컬럼 타입이 기존 catalog와 다른 경우:
1. 카탈로그를 자동 overwrite 하지 않는다
2. `wiki/decisions/contribute-<YYYY-MM-DD>-<도메인>.md` 생성, 충돌 내용 기록
3. 사용자에게 alert: "타입 충돌 — 카탈로그 변경 보류. decisions/ 파일 검토 후 재시도."

## Phase 6 — 카탈로그 갱신
`yes` 항목만 카탈로그에 반영:
1. `~/.karpathy-rdb/catalog/<도메인>.seed.md`가 없으면 신규 생성 (frontmatter `preset: <도메인>`, `version: 1`)
2. 있으면 `version` 자동 증분 (예: 1 → 2)
3. `entities (시드)` / `concepts (시드 관계)` / `rules (시드 비즈니스 규칙)` 섹션에 승인된 항목 추가

## Phase 7 — 후처리
1. `wiki/_log.md`에 1줄: `YYYY-MM-DD HH:MM | contribute | <도메인> v<old>→v<new>: <건수> 항목`
2. `wiki/learn-log.md`에 1줄: `YYYY-MM-DD | contribute | <도메인> | <도메인> | v<old>→v<new>, +<n> entities, +<m> concepts, +<k> rules`
3. **`presets/INDEX.md` (또는 글로벌 동급 인덱스) 갱신** — 신규 도메인이면 항목 추가, 기존 도메인이면 aliases/keywords/entities/한 줄을 갱신 (v0.3.x C-2). 인덱스가 갱신되지 않으면 다음 프로젝트의 init 추천이 새 지식을 모름.
4. 사용자에게 보고:
   - 카탈로그 파일 경로
   - 새 version
   - 거부(`no`) / 보류(`skip`) 항목 수
   - 다음 프로젝트에서 `/karpathy-rdb init <명> --preset <도메인>` 실행 시 갱신된 시드 자동 적용됨을 안내

## 멱등성
같은 항목을 다시 contribute 시도 시: 이미 카탈로그에 있는 항목은 자동 skip(중복 방지). 사용자에게 "변경 없음, 카탈로그 v 그대로" 보고.

## 패턴 기여 (v0.3+)

`/karpathy-rdb contribute --kind pattern <pattern-name>` 으로 Stage 4 form pattern 디렉터리를 글로벌 카탈로그로 승격:

1. 로컬 패턴 위치 확인: `<stage4-repo>/.claude/skills/karpathy-rdb-nexacro/patterns/<name>/` (manifest.yaml + form.xfdl.j2 + README.md)
2. 글로벌 대상 위치: `~/.karpathy-rdb/catalog/patterns/<name>/`. 없으면 신규 생성.
3. 두 경로의 디렉터리 diff 표시 (신규/변경 파일 강조)
4. 사용자에게 항목별 confirm: **"이 pattern 이 다른 프로젝트에도 일반화 가능합니까? (yes/no/skip)"**
5. `yes` 항목만 디렉터리에 복사. `manifest.yaml` 의 `version` 증분 (없으면 1 부여).
6. `wiki/_log.md` 와 `wiki/learn-log.md` 에 `pattern-contribute` 이벤트 1줄 기록 (`YYYY-MM-DD | pattern-contribute | <name> | - | v<old>→v<new>`)

**Karpathy 정신 유지**: 자동 머지 금지 (entity contribute 와 동일 규칙), 디렉터리 단위 파일 기반, LLM 추론/벡터 검색 없음.
