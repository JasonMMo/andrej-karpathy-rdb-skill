---
type: protocol
protocol: init
version: 1
---

# Protocol 01 — Init

`/karpathy-rdb init <도메인명> [--preset <preset-key>]` 실행 시 AI가 따르는 절차.

## Phase 1 — Clarify (한 번에 한 질문)
1. **wiki 디렉터리 위치?** 기본: `./wiki/`. 이미 존재하면 abort.
2. **추가 도메인 프리셋?** 사용자가 명령에 `--preset`를 주지 않았다면 후보 제시 (고객관리/주문관리/재고관리/인사관리/재무관리/없음).
3. **프로젝트 루트에 `CLAUDE.md` 있나?** 없으면 신규 생성, 있으면 wiki 섹션만 추가.
4. **시작 entity 1개?** 예시 entity 이름 (snake_case 영문).

## Phase 2 — Scaffold
1. plugin의 `wiki-template/` 전체를 사용자 프로젝트의 `wiki/`로 복사
2. `wiki/raw/.gitkeep` 유지 (빈 디렉터리 보존)

## Phase 3 — 도메인 커스터마이즈
1. `wiki/domains/_template/` → `wiki/domains/<도메인명>/`로 복사·rename
2. `_template/profile.md`의 placeholder를 도메인명으로 치환
3. 선택한 preset이 있으면 `presets/<도메인>.seed.md`의 내용을 wiki에 적용 (entities/concepts 시드 페이지 생성)

## Phase 4 — `CLAUDE.md` 통합
프로젝트 루트의 `CLAUDE.md`에 다음 섹션 추가 (없으면 파일 생성):

```
## RDB Wiki
이 프로젝트는 `wiki/`에 RDB 설계 문서를 관리한다.
- 모든 ingest/compile 전 `wiki/_schema.md`, `wiki/_protocols.md`를 읽는다.
- 새 entity 추가 시 관련 domain·concept을 갱신한다.
```

## Phase 5 — 첫 Entity Scaffold
Phase 1 Q4에서 받은 entity 이름으로:
1. `wiki/entities/<name>/profile.md`를 `entities/_template/profile.md`에서 복사
2. frontmatter의 `name`, `display`, `table`을 채움 (display는 사용자에게 한 번 더 물음)
3. 본문은 비워둠 — 내용 추측 금지

## Phase 6 — Verify + Hand-off
1. `python scripts/rdb_index.py --lint wiki/` 실행 (plugin scripts/ 경로)
2. 에러 0개 확인
3. 사용자에게 안내:
   > "wiki/ 설치 완료. 다음: `/karpathy-rdb ingest`로 요구사항을 추가하세요. `wiki/_schema.md`와 `wiki/_protocols.md`를 매 작업 전 읽습니다."
