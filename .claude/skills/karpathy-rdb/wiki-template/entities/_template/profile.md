---
type: entity
name: <entity_name>                  # snake_case 영문 (예: customer)
display: <표시명>                     # 한국어
domain: []                            # 소속 도메인 리스트
table: <table_name>                  # 물리 테이블명, 기본 = name
schema: public                        # PostgreSQL 스키마
status: draft                         # draft | reviewed | locked
columns:
  - { name: id, type: bigserial, pk: true, null: false }
  - { name: created_at, type: timestamptz, null: false, default: now() }
  - { name: updated_at, type: timestamptz, null: false, default: now() }
indexes: []
constraints: []
relations: []
sources: []
decisions: []
---

# <표시명> (<entity_name>)

## 의미
<엔티티의 비즈니스 의미>

## 컬럼 설명
| 컬럼 | 의미 | 비고 |
| :-- | :-- | :-- |
| id | 대리키 | bigserial |

## 비즈니스 규칙
- <규칙 1>

## 관련
- 도메인: <위키링크>
- 관계: <위키링크>
