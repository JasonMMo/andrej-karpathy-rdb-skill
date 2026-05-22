---
name: karpathy-rdb
description: |
  사용자가 비즈니스 업무(고객관리, 주문관리, 재고관리, 인사관리, 재무관리 등)의
  DB 스키마/도메인 모델을 설계·정의하려 할 때 자동 발동. Karpathy LLM Wiki 패턴을
  RDB 비즈니스-도메인-엔티티 컨텍스트에 이식하여 markdown wiki와 _blueprint.yaml
  manifest를 산출한다. business-fullstack-creater 파이프라인의 1단계(Plan)를 담당.
argument-hint: "[init|ingest|compile] [도메인명]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# karpathy-rdb skill

## 무엇을 하는가
Andrej Karpathy의 LLM Wiki 패턴 (markdown + frontmatter, no vector DB)을 관계형 DB 스키마 설계에 적용. 사용자는 markdown wiki를 큐레이션하고, LLM은 컴파일·정합성 검증을 담당한다.

## 언제 발동되는가
- 사용자가 "<업무명> DB 설계해줘" / "<업무명> 스키마 만들어줘" / "엔티티 정의해줘" / "도메인 모델 설계해줘"
- 사용자가 `/karpathy-rdb` 명령으로 명시 호출
- `wiki/_schema.md`가 존재하는 프로젝트에서 RDB 관련 질문

## 워크플로우
4개 슬래시 커맨드:
1. `/karpathy-rdb init <도메인명> [--preset <key>]` — wiki 골격 설치
2. `/karpathy-rdb ingest [<프롬프트>|--file <path>]` — 요구사항을 wiki로 변환
3. `/karpathy-rdb compile` — wiki → `_blueprint.yaml` + 검증
4. `/karpathy-rdb contribute <도메인명>` — 현재 프로젝트의 신규 지식을 글로벌 카탈로그로 역류 (Karpathy 복리식 축적)

## 참조 문서 (이 디렉터리)
- `protocols/01-init.md` — init 프로토콜 (Phase 1~6)
- `protocols/02-ingest.md` — ingest 프로토콜
- `protocols/03-compile.md` — compile 프로토콜 + V001~V010
- `protocols/04-contribute.md` — contribute 프로토콜 (Phase 1~7, 글로벌 카탈로그 역류)
- `references/frontmatter-schema.md` — entity/concept/domain frontmatter 스키마
- `references/blueprint-spec.md` — `_blueprint.yaml` 명세 (2단계 계약)
- `references/seed-spec.md` — `presets/*.seed.md` 컨벤션 (init/contribute 시드 형식)
- `wiki-template/` — init이 복사할 wiki 골격
- `presets/` — 도메인 프리셋 (12개: 결재/게시판/고객관리/공통코드/권한관리/배송관리/알림/인사관리/재고관리/재무관리/주문관리/파일관리)
- `presets/INDEX.md` — 프리셋 매칭 인덱스. init 시 입력 도메인명과 비교하여 유사 후보 3개를 자동 추천 (v0.3.x C-2)

## 핵심 원칙
1. **Wiki-first**: markdown이 진실의 근원, `_blueprint.yaml`은 항상 생성 산출물
2. **사람 큐레이션, LLM 유지보수**: 사용자는 wiki만 본다. yaml은 자동 생성.
3. **No vector DB, No RAG**: frontmatter + 컨텍스트 윈도우로 충분
4. **2단계 계약 안정성**: `_blueprint.yaml`의 `version` 필드로 호환성 관리
5. **지식 누적 (Karpathy 복리식)**: `wiki/learn-log.md`에 새로 발견한 entity/concept/rule을 누적. 향후 `/karpathy-rdb contribute`가 이를 읽어 글로벌 도메인 카탈로그로 역류시킨다 (v0.2+).

## 두 종류의 로그 (역할 구분)
- `wiki/_log.md` — **작업 이력**. "언제 ingest/compile을 했나". 형식: `YYYY-MM-DD HH:MM | <action> | <요약>`
- `wiki/learn-log.md` — **지식 누적**. "이 프로젝트에서 새로 알게 된 것". 형식: `YYYY-MM-DD | <kind> | <name> | <domain> | <요약>`. `kind` ∈ {`new_entity`, `new_concept`, `new_rule`, `false_belief`, `contribute`}

## 파이프라인 위치
business-fullstack-creater의 4단계 파이프라인:
1. **Plan (본 스킬)** — 요구사항 → wiki → `_blueprint.yaml`
2. Backend — `_blueprint.yaml` → DDL
3. Middle — `/nexacro-fullstack-starter`
4. Frontend — `/nexacro-claude-skills`

## Ownership & Self-Check (Phase A — 2026-05-22)

이 skill 은 **business-fullstack-creater 5축 책임표의 `skill (Stage 1)` 축**을 담당. 활동 뷰는 `business-fullstack-creater/learn-log.md` §0.

- **깊이 누적 위치**: `presets/*.seed.md` (현 12개 도메인) + `protocols/` (init/ingest/compile/contribute) + `wiki-template/`
- **단위 테스트**: `tests/` (pytest)
- **누적 트랩 (0)**: 없음 (wiki 큐레이션 레이어)
- **미해결 환류**: 없음
- **Self-check (Growth 종료 시)**: 새 도메인 wiki 큐레이션이 발생했다면 `/karpathy-rdb contribute` 로 글로벌 카탈로그 역류 + `business-fullstack-creater/learn-log.md` §0 skill 행 (필요 시) + §2 (도메인) 갱신했는가?
