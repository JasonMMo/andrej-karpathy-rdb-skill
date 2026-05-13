---
name: karpathy-rdb-init
description: RDB wiki 골격을 사용자 프로젝트에 설치하고 도메인 프리셋을 적용한다
argument-hint: "<도메인명> [--preset <preset-key>]"
allowed-tools: Read, Write, Edit, Glob, Bash
---

# /karpathy-rdb init

당신은 안드레이 카파시 LLM Wiki 패턴을 RDB에 적용하는 플러그인의 **init 프로토콜**을 실행하는 에이전트다.

## 사용법
- `/karpathy-rdb init 고객관리`
- `/karpathy-rdb init 주문관리 --preset 주문관리`

## 절차
1. **`.claude/skills/karpathy-rdb/protocols/01-init.md`를 먼저 읽는다.**
2. 그 안의 Phase 1~6을 순서대로 실행한다.
3. Phase 1의 질문은 **한 번에 하나씩** AskUserQuestion으로 물어본다.
4. 모든 phase 완료 후 사용자에게 다음 명령을 안내: `/karpathy-rdb ingest`

## 입력 검증
- `<도메인명>` 미제공 시 사용자에게 한국어로 질문하고 받기
- `wiki/` 디렉터리가 이미 있으면 **즉시 abort**하고 사용자에게 보고 (`init`은 비멱등)
- `--preset`이 있을 때 해당 preset 파일이 plugin의 `presets/`에 없으면 abort

## 산출물
- 사용자 프로젝트의 `wiki/` 디렉터리 (template 복사본 + 도메인 커스터마이즈)
- 프로젝트 루트의 `CLAUDE.md`에 wiki 섹션 추가
- `wiki/entities/<첫entity>/profile.md` 1개

## 완료 보고
- 생성된 파일 트리 (`find wiki -type f` 결과)
- 다음 단계 안내
