---
type: concept
kind: relation
name: customer-has-many-addresses
cardinality: 1:N
from: customer
to: address
fk_column: customer_id
on_delete: cascade
status: draft
---

# customer ↔ address
