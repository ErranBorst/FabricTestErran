# Transform

This layer contains the dbt project and notebooks that run Fabric Spark transformations.

## dbt adapter choice
This project is configured for `dbt-fabricspark`, which targets Fabric Lakehouse through Spark and is the correct adapter when your ETL lands in a lakehouse.

## Main assets
- `notebooks/run_dbt_fabricspark.ipynb`: installs dbt, writes a Fabric notebook auth profile, and runs `dbt build`.
- `dbt_fabric_project/`: dbt models, tests, and project configuration.
