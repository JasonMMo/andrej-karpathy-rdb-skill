---
type: concept
kind: relation                       # relation | rule | invariant | terminology
name: <from>-<verb>-<to>             # 예: customer-has-many-addresses
cardinality: 1:N                     # 1:1 | 1:N | N:M | self  (kind=relation일 때)
from: <entity_name>
to: <entity_name>
fk_column: <column_name>             # FK가 위치하는 컬럼 (N 쪽)
on_delete: restrict                  # restrict | cascade | set_null
status: draft
sources: []
---

# <개념 표시명>

## 정의
<개념의 명확한 정의 1~2문장>

## 근거
<요구사항 또는 비즈니스 규칙 출처>

## 영향
<이 개념이 강제하는 제약·인덱스·triggers>
