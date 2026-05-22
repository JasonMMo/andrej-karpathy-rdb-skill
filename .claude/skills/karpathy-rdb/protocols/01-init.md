---
type: protocol
protocol: init
version: 2
---

# Protocol 01 — Init

`/karpathy-rdb init <도메인명> [--preset <preset-key>]` 실행 시 AI가 따르는 절차.

## Phase 1 — Clarify (한 번에 한 질문)
1. **wiki 디렉터리 위치?** 기본: `./wiki/`. 이미 존재하면 abort.
2. **추가 도메인 프리셋?** 사용자가 명령에 `--preset`를 주지 않았다면 다음 3단계 추천 절차를 따른다 (v0.6 C-2 — 알리먼트 리뷰 §7.2). 단계 2-2/2-3 는 글로벌 카탈로그/메타 부재 시 자동 SKIP, 로컬 INDEX 결과만 사용.

   **2-1. 로컬 INDEX.md 매칭 (필수)**
   - `presets/INDEX.md`를 읽고 사용자 입력 `<도메인명>`과 모든 preset의
     (제목·aliases·keywords·entities·한 줄)을 비교 (INDEX.md 하단 "매칭 알고리즘" 절차 그대로)

   **2-2. 글로벌 카탈로그 추가 스캔 (있을 때만)**
   - `~/.karpathy-rdb/catalog/` 디렉터리가 존재하면 그 안의 `*.seed.md` frontmatter
     (domain/aliases/keywords)를 동일 알고리즘으로 비교해 후보 풀에 합산
   - 디렉터리/파일 부재 → SKIP=PASS (로컬 결과만)
   - 로컬 INDEX.md 와 글로벌 카탈로그에 같은 도메인이 있으면 글로벌 우선 (이전 프로젝트의 누적 시드가 더 신선) — 단 점수는 두 출처 중 높은 값 사용

   **2-3. 메타 컨텍스트 부착 (있을 때만)**
   - 후보 도메인 `<X>` 에 대해 `~/.karpathy-rdb/catalog/meta/<X>_meta.md` (C-1 출력) 가 존재하면
     "반복 등장 entity / 반복 등장 concept / false-belief 패턴" 표를 추천 컨텍스트로 부착
   - 파일 부재 → SKIP=PASS (메타 없이 추천)
   - 부착 시 사용자에게 1줄로 알림: > "메타 지식 적용됨: `<X>_meta.md` (소스 프로젝트 N개)"

   **추천 제시 (합산 점수 기반)**
   - **점수 ≥ 5 (정확 매치)**: 한 개 제시 + confirm 요청
     > "`<preset>` 프리셋이 정확히 일치합니다 (근거: `<key>`, 출처: local|global). 이걸 사용할까요?"
   - **점수 2~4 (유사 매치)**: 상위 3개 + "없음" 옵션 제시
     > "정확한 매치 없음. 유사한 후보:
     >   1. `<preset1>` — `<한줄>` (근거: `<key>`, 출처: local|global)
     >   2. `<preset2>` — `<한줄>` (근거: `<key>`, 출처: local|global)
     >   3. `<preset3>` — `<한줄>` (근거: `<key>`, 출처: local|global)
     >   4. 없음 (빈 wiki로 시작)"
   - **매치 0**: "프리셋 없음 — 빈 wiki로 시작합니다. ingest로 처음부터 정의하세요."
3. **프로젝트 루트에 `CLAUDE.md` 있나?** 없으면 신규 생성, 있으면 wiki 섹션만 추가.
4. **시작 entity 1개?** 예시 entity 이름 (snake_case 영문).

## Phase 2 — Scaffold
1. plugin의 `wiki-template/` 전체를 사용자 프로젝트의 `wiki/`로 복사
2. `wiki/raw/.gitkeep` 유지 (빈 디렉터리 보존)

## Phase 3 — 도메인 커스터마이즈
1. `wiki/domains/_template/` → `wiki/domains/<도메인명>/`로 복사·rename
2. `_template/profile.md`의 placeholder를 도메인명으로 치환
3. 선택한 preset이 있으면 seed.md를 다음 우선순위로 탐색하여 적용 (entities/concepts 시드 페이지 생성):
   1. **글로벌 카탈로그**: `~/.karpathy-rdb/catalog/<도메인>.seed.md` — 이전 프로젝트에서 `/karpathy-rdb contribute`로 누적된 최신 시드
   2. **플러그인 내장 preset**: `presets/<도메인>.seed.md` — 플러그인 출시 기본값
   3. 둘 다 없으면 빈 wiki로 시작 (사용자에게 alert: "preset 없음 — ingest로 처음부터 정의 필요")
4. 글로벌 카탈로그가 사용된 경우 사용자에게 알림: `~/.karpathy-rdb/catalog/<도메인>.seed.md v<n>이 적용됨 (이전 프로젝트의 누적 지식)`

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
