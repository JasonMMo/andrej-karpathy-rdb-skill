# INSTALL-FOR-AI.md — Auto-install protocol

> **Audience**: AI agents (Claude Code, Cursor, Cline, etc.). If a human user pastes this file's URL and says "install this for me", follow the steps below in order.

## Phase 1 — Clarify (한 번에 한 질문)
1. **wiki 디렉터리 위치?** 기본: `./wiki/`. 이미 존재하면 abort.
2. **첫 비즈니스 도메인?** 자유 입력 (예: 고객관리)
3. **도메인 프리셋 적용?** 옵션: 고객관리/주문관리/재고관리/인사관리/재무관리/없음
4. **프로젝트 루트에 `CLAUDE.md` 있나?** yes/no
5. **시작 entity 이름 1개?** snake_case 영문 (예: customer)

## Phase 2 — Plugin 설치 확인
```bash
# /plugin install 명령으로 설치된 경우 skip.
# 수동 설치 시:
git clone https://github.com/<owner>/andrej-karpathy-rdb-skill.git .karpathy-rdb-tmp
# Claude Code 플러그인 디렉터리에 복사
```

## Phase 3 — Wiki Scaffold
`.claude/skills/karpathy-rdb/wiki-template/` 전체를 사용자의 `<wiki 디렉터리 위치>`로 복사.

## Phase 4 — 도메인 커스터마이즈
1. `wiki/domains/_template/`를 `wiki/domains/<도메인>/`로 복사·rename
2. frontmatter의 `name`, `display`를 도메인명으로 치환
3. 선택한 preset이 있으면 `.claude/skills/karpathy-rdb/presets/<도메인>.seed.md`의 entities/concepts/rules를 wiki에 적용

## Phase 5 — `CLAUDE.md` 통합
프로젝트 루트의 `CLAUDE.md`에 다음 섹션 추가 (없으면 신규 생성):
```
## RDB Wiki
- 모든 ingest/compile 전 `wiki/_schema.md`, `wiki/_protocols.md`를 읽는다.
- 새 entity 추가 시 관련 domain·concept을 갱신한다.
```

## Phase 6 — 첫 Entity Scaffold
1. `wiki/entities/<첫entity>/profile.md` 생성 (template에서 복사)
2. frontmatter의 `name`, `display`, `table` 채움
3. 본문은 비워둠 — 내용 추측 금지

## Phase 7 — Verify + Hand-off
1. `python <plugin_path>/scripts/rdb_index.py --lint <wiki_path>` 실행
2. 에러 0개 확인
3. `.karpathy-rdb-tmp/` 삭제
4. 사용자에게 안내:
   > "wiki/ 설치 완료. 다음: `/karpathy-rdb ingest`로 요구사항을 추가하세요."

## 절대 하지 말 것
- 사용자가 명시하지 않은 entity content 생성
- silent overwrite
- locale을 사용자 동의 없이 변경
