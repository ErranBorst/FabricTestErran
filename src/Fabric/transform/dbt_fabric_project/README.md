# dbt Fabric Project

This dbt project is configured for Fabric Lakehouse using `dbt-fabricspark`.

## Project flow
- `ingest` lands `raw_dummy_orders` in the attached lakehouse.
- `bronze` standardizes the raw source.
- `silver` applies business cleanup and incremental merge logic.
- `gold` builds an aggregated sales summary for semantic consumption.

## Run options
- In Fabric notebook: use `../notebooks/run_dbt_fabricspark.ipynb`.
- Locally: install `dbt-fabricspark[cli]`, authenticate with `az login`, and create `~/.dbt/profiles.yml`.
