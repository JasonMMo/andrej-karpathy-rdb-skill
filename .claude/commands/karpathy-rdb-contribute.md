---
name: karpathy-rdb-contribute
description: 현재 프로젝트의 신규 entity/concept/rule을 글로벌 도메인 카탈로그로 역류시킨다 (Karpathy 복리식 축적)
argument-hint: "<도메인명>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# /karpathy-rdb contribute

당신은 안드레이 카파시 LLM Wiki 패턴을 RDB에 적용하는 플러그인의 **contribute 프로토콜**을 실행하는 에이전트다.

## 사용법
- `/karpathy-rdb contribute 고객관리`
- `/karpathy-rdb contribute 주문관리`

## 절차
1. **`.claude/skills/karpathy-rdb/protocols/04-contribute.md`를 먼저 읽는다.**
2. 그 안의 Phase 1~7을 순서대로 실행한다.
3. Phase 4의 범용성 confirm은 **항목별로 한 번씩** AskUserQuestion으로 물어본다 (자동 승인 금지).
4. 모든 phase 완료 후 갱신된 카탈로그 파일 경로와 새 version을 보고한다.

## 입력 검증
- `<도메인명>` 미제공 시 사용자에게 질문하고 받기
- 현재 프로젝트에 `wiki/`가 없으면 즉시 abort (init이 먼저 필요함을 안내)
- `wiki/learn-log.md`가 비었으면 alert (ingest 선행 권장)

## 산출물
- `~/.karpathy-rdb/catalog/<도메인>.seed.md` (신규 또는 version 증분)
- 충돌 시: `wiki/decisions/contribute-<YYYY-MM-DD>-<도메인>.md`
- `wiki/_log.md`, `wiki/learn-log.md` 갱신

## 안전장치
- **자동 머지 금지** — 모든 항목은 사용자 confirm 후에만 카탈로그에 반영
- **타입 충돌 시 자동 overwrite 금지** — decisions/ 파일 작성 후 사용자 검토 대기
- **카탈로그 디렉터리 자동 생성**은 안전하나, 카탈로그 파일을 사용자 동의 없이 수정 금지
