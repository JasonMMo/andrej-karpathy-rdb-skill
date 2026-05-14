---
type: entity
name: address
display: 주소
domain: [고객관리]
table: address
status: draft
columns:
  - { name: id,          type: bigserial, pk: true, nullable: false }
  - { name: customer_id, type: bigint,    nullable: false }
---

# address
