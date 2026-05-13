---
type: entity
name: customer
display: 고객
domain: [고객관리]
table: customer
status: draft
columns:
  - { name: id,    type: bigserial,    pk: true, null: false }
  - { name: email, type: varchar(255), null: false, unique: true }
indexes:
  - { name: ix_customer_email, columns: [email], unique: true }
relations:
  - { kind: has_many, to: address, fk: customer_id, concept: "[[customer-has-many-addresses]]" }
sources: []
---

# customer
