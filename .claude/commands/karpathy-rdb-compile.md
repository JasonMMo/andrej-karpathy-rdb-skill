---
name: karpathy-rdb-compile
description: wiki 전체를 스캔하여 _blueprint.yaml 생성 + V001-V010 정합성 검증
argument-hint: ""
allowed-tools: Read, Write, Glob, Grep, Bash
---

# /karpathy-rdb compile

당신은 **compile 프로토콜**을 실행하는 에이전트다.

## 절차
1. **`wiki/_schema.md`, `wiki/_protocols.md` 읽기**
2. **`.claude/skills/karpathy-rdb/protocols/03-compile.md`와 `references/blueprint-spec.md` 읽기**
3. Python CLI 실행: `python scripts/rdb_index.py compile wiki/`
4. 출력 파일 확인:
   - `wiki/_blueprint.yaml`
   - `wiki/compile-report.md`
5. ERROR 카운트 보고. ERROR 있으면 어떤 wiki 페이지를 고쳐야 하는지 안내.

## 사전 조건
- `wiki/` 존재
- `scripts/rdb_index.py` 존재 (plugin install 경로)

## 산출물
- `wiki/_blueprint.yaml`
- `wiki/compile-report.md`
- `_log.md`에 `compile` 이벤트 1줄 추가

## 다음 단계
ERROR 0개일 때 사용자에게: "`_blueprint.yaml`을 2단계 DDL 생성 플러그인에 전달하세요."
