---
type: schema
version: 1
generated_by: karpathy-rdb init
locale: ko
---

# Wiki 헌법 (_schema.md)

> 본 wiki는 RDB 스키마 설계를 위한 markdown 기반 진실의 근원. AI는 매 작업 전 본 파일을 읽는다.

## 1. 5계층 변화율 구조
- `raw/` — 불변 원본 요구사항
- `sources/` — LLM 압축 요약 (1 source = 1 page)
- `domains/`, `entities/`, `concepts/` — 주/월 단위 갱신
- `explorations/` — 쿼리당 갱신
- `decisions/`, `rules.md`, `false-beliefs.md` — 분기 단위 갱신

## 2. 용어
- **Domain (도메인)**: 비즈니스 영역 (예: 고객관리). 여러 entity를 포함.
- **Entity (엔티티)**: 1 DB 테이블 = 1 entity. frontmatter에 PK/FK/columns 정의.
- **Concept (개념)**: ER 관계, 비즈니스 규칙, 불변식. entity 간 연결을 담당.

## 3. 식별자 규약
- entity name: `snake_case` 영문 (예: `customer`, `order_item`)
- table name: entity name 그대로
- column name: `snake_case` 영문
- 표시명(`display`): 한국어 허용

## 4. 변경 절차
1. `/karpathy-rdb ingest`로 원본·프롬프트를 wiki 페이지로 변환
2. `/karpathy-rdb compile`로 wiki → `_blueprint.yaml` 생성 + 정합성 검증
3. 검증 실패 시 wiki 수정 후 재컴파일

## 5. 핸드오프
`_blueprint.yaml`은 2단계 DDL 생성 플러그인의 공식 입력. 스키마는 `references/blueprint-spec.md` 참조.
