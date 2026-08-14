# Naming conventions

Applied consistently to every Fabric item in this repository. Copied verbatim from the reference
architecture (`architecture-overview.md` in the Customer-Hillfresh-Fabric repo).

| Resource type | Prefix | Example |
|---|---|---|
| Lakehouse | `lh_` | `lh_silver` |
| Notebook | `nb_` | `nb_dbt_transformations` |
| Data pipeline | `pl_` | `pl_nightly_transform` |
| Trigger | `trg_` | `trg_nightly_transform` |
| View | `vw_` | `vw_item_ledger_entry` |
| Shortcut | `sc_` | `sc_source_mirror` |
| Semantic model | `sm_` | `sm_finance` |
| Variable Library | `vl_` | `vl_runtime_config` |
| Environment (Spark) | `env_` | `env_dbt` |
| Connection | `con_` | `con_sharepoint_excel` |

**Workspaces**: lowercase kebab-case, `<function>-<environment>` (e.g. `lakehouse-acc`), no type
prefix. Two environments only: `acceptance` (Git-linked directly, live development) and `production`
(deployed via CI). There is no separate `dev` tier.

**dbt models**: bronze staging = `stg_<source>__<entity>`; silver/gold use their functional object
name (no layer prefix). If a silver and gold model would otherwise share the same name (they usually
will), give the gold model file a distinguishing logical name and set `{{ config(alias=...) }}` to
the desired physical/consumer-facing name — see `models/gold/orders_gold.sql` for the pattern.

**Other rules**: no generic sequence names (`pipeline1`), no version suffixes (`_v2` — versioning is
git's job), only use agreed/documented abbreviations, and record the reason whenever a naming
exception is required (e.g. to preserve an existing consumer-facing contract).
