# dbt conventions

## Layer responsibilities

| Layer | Materialization | Responsibility | Naming |
|---|---|---|---|
| **Bronze** | `ephemeral` | 1:1 per source entity: cast + rename to snake_case. **Only place `source()` is used.** No business logic. | `stg_<source>__<entity>` |
| **Silver** | `table` (default; `view`/`incremental` as exception) | Business entities: joins, enrichment, deduplication, surrogate keys, business rules. Reads only via `ref()`. | `<entity>` (functional name) |
| **Gold** | `table` | Thin presentation layer: explicit column selection, renamed to consumer-facing names. Feeds Direct Lake semantic models. | `<presentation-name>` (see naming-conventions.md for the silver/gold name-collision rule) |

## Rules

1. `source()` **only** in bronze; every downstream reference uses `ref()` so lineage stays visible.
2. Bronze does **union + cast + rename only** — no joins, no aggregation, no business rules.
3. Business logic belongs in **silver** — this is where most engineering effort goes.
4. Gold stays **thin**: no `select *`, explicit column list, renamed for the consuming
   report/semantic model.
5. Bronze is `ephemeral`, so it produces no physical object — it's inlined into whatever silver model
   references it.

## Testing baseline

Every silver/gold entity gets a `description` and column-level tests in a per-folder
`_<layer>__models.yml` (or `_bronze__sources.yml` for bronze sources):

- `unique` + `not_null` on the surrogate/business key
- `not_null` on required attributes
- `relationships` for foreign keys
- `accepted_values` for enum-like codes
- the custom `not_before_date` generic test (see `macros/tests/not_before_date.sql`) for date/time
  sanity, parameterized per column with `min_date`

## SQLFluff

- `sqlfluff lint models/` — check for style violations
- `sqlfluff fix models/` — auto-fix what can be auto-fixed
- Config lives in `.sqlfluff` at the dbt project root; see the file for which rules are excluded and
  why (quoted/spaced source identifiers, staging wildcard selects).

## Adding a new entity

1. Add/extend the source table entry in `models/bronze/_bronze__sources.yml`.
2. Add `models/bronze/stg_<source>__<entity>.sql` — cast + rename only.
3. Add `models/silver/<entity>.sql` + an entry in `models/silver/_silver__models.yml` with baseline
   tests.
4. Add `models/gold/<entity>_gold.sql` (or whatever avoids a name collision with silver) + an entry in
   `models/gold/_gold__models.yml`.
5. Run `dbt build` locally against the `acceptance` target before opening a PR.
