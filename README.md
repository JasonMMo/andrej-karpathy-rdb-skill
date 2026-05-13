# andrej-karpathy-rdb-skill

> Claude Code plugin that ports Andrej Karpathy's LLM Wiki pattern to relational database schema design. Korean-first.

For Korean documentation, see [README.ko.md](README.ko.md) (default).

## What is this
Define business domains, entities, and relations in markdown + YAML frontmatter. A single `compile` step produces a `_blueprint.yaml` manifest consumed by a downstream DDL-generation plugin to emit PostgreSQL DDL.

**Core philosophy**:
- ✅ markdown + YAML frontmatter (no vector DB, no RAG)
- ✅ Human curates the wiki; LLM compiles and validates
- ✅ Wiki-first: markdown is the source of truth
- ✅ Korean prompts by default, identifiers in English

## Install
```
/plugin install andrej-karpathy-rdb-skill@<marketplace>
```

## Quick Start
```
/karpathy-rdb init customer-management --preset 고객관리
/karpathy-rdb ingest A customer has a unique email and can register many addresses.
/karpathy-rdb compile
```

## Commands
| Command | Purpose |
| :-- | :-- |
| `/karpathy-rdb init <domain> [--preset <key>]` | Scaffold wiki + apply preset |
| `/karpathy-rdb ingest [<prompt>\|--file <path>]` | Ingest requirements into wiki |
| `/karpathy-rdb compile` | wiki → `_blueprint.yaml` + validation |

## Domain Presets

| Preset (Korean) | Seed entities | Seed concepts |
| :-- | :-- | :-- |
| 고객관리 (Customer) | customer, address, contact_log | 1:N |
| 주문관리 (Order) | sales_order, order_item, payment | 1:N, 1:1 |
| 재고관리 (Inventory) | product, sku, warehouse, stock | 1:N, N:M |
| 인사관리 (HR) | employee, department, position | 1:N, self |
| 재무관리 (Finance) | account, fiscal_period, ledger_entry | 1:N, self |

## Validation Codes
See [README.ko.md](README.ko.md) for full V001~V010 table.

## Pipeline Position
Stage 1 (Plan) of the `business-fullstack-creater` 4-stage pipeline:
1. **Plan (this plugin)** — requirements → wiki → `_blueprint.yaml`
2. Backend — DDL generation
3. Middle — Spring Boot (`/nexacro-fullstack-starter`)
4. Frontend — Nexacro (`/nexacro-claude-skills`)

## Inspiration
- [Karpathy LLM Wiki pattern](https://x.com/karpathy/status/2039805659525644595)
- [Benboerba620/karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki) — reference implementation
