---
name: karpathy-rdb-ingest
description: 자유 프롬프트 또는 wiki/raw/ 파일을 wiki 페이지(entities/concepts/domains)로 ingest
argument-hint: "[<프롬프트>|--file <path>]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# /karpathy-rdb ingest

당신은 **ingest 프로토콜**을 실행하는 에이전트다.

## 사용법
- `/karpathy-rdb ingest 고객은 이메일과 이름을 가진다. 이메일은 유일하다.`
- `/karpathy-rdb ingest --file wiki/raw/2026-05-13-요구사항.md`
- `/karpathy-rdb ingest` (인자 없음 → `wiki/raw/`의 미처리 파일 자동 처리)

## 절차
1. **`wiki/_schema.md`, `wiki/_protocols.md` 읽기 (헌법 + 프로토콜)**
2. **`.claude/skills/karpathy-rdb/protocols/02-ingest.md`를 읽는다.**
3. 입력 모드 판별 (프롬프트 vs 파일)
4. 프로토콜 순서대로 실행:
   - 압축 → sources/ 생성
   - entity 후보 추출 → 사용자 확인 → entity 페이지 생성·갱신
   - 관계 후보 추출 → concept 페이지 생성
   - 충돌 검사 → decisions/ 기록
   - `_log.md` 1줄 추가
5. 사용자에게 결과 보고 + 미해결 질문 제시

## 사전 조건
- `wiki/` 존재 (없으면 `/karpathy-rdb init` 안내)

## 산출물
- 신규/갱신된 wiki 페이지 목록 출력
