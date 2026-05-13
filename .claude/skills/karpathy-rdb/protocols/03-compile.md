---
type: protocol
protocol: compile
version: 1
---

# Protocol 03 — Compile

`/karpathy-rdb compile` 실행 시 AI가 따르는 절차.

## 절차
1. **스캔**: `wiki/entities/*/profile.md`, `wiki/concepts/*.md`, `wiki/domains/*/profile.md`의 frontmatter 읽기
2. **빌드**: `wiki/_blueprint.yaml` 생성 (스키마는 `references/blueprint-spec.md` 참조)
3. **검증**: V001~V010 실행
4. **보고**: `wiki/compile-report.md` 작성
5. **로그**: `_log.md`에 1줄 추가

## 검증 규칙

| 코드 | 레벨 | 검증 |
| :-: | :-: | :-- |
| V001 | ERROR | 모든 entity는 PK 컬럼 1개 이상 (`columns[].pk: true`) |
| V002 | ERROR | `relations.fk_column`이 to-entity의 PK 또는 UQ 컬럼을 참조해야 함 |
| V003 | WARN | 컬럼명은 `snake_case`, PostgreSQL 예약어 회피 (목록: `references/blueprint-spec.md`) |
| V004 | WARN | FK 컬럼 타입이 참조 PK 타입과 동일해야 함 |
| V005 | WARN | entity 간 FK 순환 의존 검출 (DAG가 아님) |
| V006 | WARN | concept이 참조하는 entity가 wiki에 미존재 |
| V007 | WARN | entity가 어떤 domain에도 속하지 않음 (`domain: []`) |
| V008 | INFO | `rules.md`의 RULE이 어느 entity·concept에 매핑되는지 보고 |
| V009 | INFO | entity의 `sources: []` 비어있음 (출처 미기록) |
| V010 | INFO | `status: locked` entity는 `decisions: []`에 1개 이상 권장 |

## ERROR가 있는 경우
- `_blueprint.yaml`의 `validation.passed: false`
- `compile-report.md` 상단에 ERROR 카운트 + 상세
- 2단계로 핸드오프 차단

## 보고서 포맷 (`compile-report.md`)
```
# Compile Report — YYYY-MM-DD HH:MM

## Summary
- ERROR: N
- WARN: N
- INFO: N
- entities: N, concepts: N, domains: N

## Details
### ERROR
- V001 [entity:foo]: PK 컬럼 없음 — `columns[].pk: true`인 컬럼 1개 이상 필요

### WARN
- ...

### INFO
- ...
```
