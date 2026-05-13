---
type: protocols
---

# 작업 프로토콜 인덱스

본 파일은 AI가 작업 전 매번 읽는다. 각 프로토콜의 상세는 plugin의 `protocols/` 디렉터리 참조.

## Protocol 1 — Ingest (`protocols/02-ingest.md`)
입력(프롬프트 또는 raw 파일) → `sources/`, `domains/`, `entities/`, `concepts/` 갱신.

핵심 규칙:
1. 새 entity는 `entities/<name>/profile.md` 생성, 필수 frontmatter 채움
2. 새 관계는 `concepts/<from>-<verb>-<to>.md` 생성
3. 매 작업 후 `_log.md`에 1줄 추가: `YYYY-MM-DD HH:MM | ingest | <요약>`
4. 절대 silent overwrite 금지 — 충돌 시 `decisions/`에 기록

## Protocol 2 — Compile (`protocols/03-compile.md`)
wiki 전체 → `_blueprint.yaml` + `compile-report.md`.

핵심 규칙:
1. `entities/*/profile.md`와 `concepts/*.md`의 frontmatter를 읽어 manifest 빌드
2. V001~V010 검증 실행
3. ERROR가 있으면 `compile-report.md`에 기록하고 `_blueprint.yaml`의 `validation.passed: false`
4. WARN/INFO만 있으면 `validation.passed: true`로 생성

## Protocol 3 — Init (`protocols/01-init.md`)
빈 프로젝트에 wiki 골격 + 선택한 도메인 프리셋 적용.
