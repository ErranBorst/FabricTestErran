# Fabric ETL Project

This repository contains a starter Microsoft Fabric ETL project with dedicated layers for ingest, lakehouse design, operations, semantic outputs, and dbt-based transformations.

## Fabric Git Integration

Connect the Fabric workspace to the `fabric-workspace` folder in this repository, not to the repository root.

- `fabric-workspace` contains Fabric-recognizable Git item folders such as `.Notebook`, `.Lakehouse`, and `.DataPipeline` items.
- `src/Fabric` remains the engineering project tree with supporting notebooks, dbt code, templates, and documentation.
- Generic project files in `src/Fabric` are useful for development, but Fabric Source Control does not import them as workspace items unless they are expressed in Fabric item format.

## Structure

- `fabric-workspace`: Fabric Git sync root with supported item definitions.
- `src/Fabric/ingest`: notebooks that land raw data into a Fabric lakehouse.
- `src/Fabric/lakehouse`: documentation for the intended bronze, silver, and gold lakehouse layout.
- `src/Fabric/ops`: orchestration and operational templates.
- `src/Fabric/semantic`: semantic model starter definitions for reporting.
- `src/Fabric/transform`: a dbt Fabric Spark project and the notebook used to run it inside Fabric.

## Quick start

1. Open `src/Fabric/ingest/notebooks/01_ingest_dummy_orders_to_lakehouse.ipynb` in Fabric and run it against an attached lakehouse.
2. Update the variables in `src/Fabric/transform/notebooks/run_dbt_fabricspark.ipynb` with your workspace and lakehouse values.
3. Run the dbt notebook to execute `dbt debug`, `dbt deps`, and `dbt build`.

## dbt integration

The transform layer uses `dbt-fabricspark`, which is the correct dbt adapter for Fabric Lakehouse through Spark. The notebook integration is configured for `fabric_notebook` authentication so the dbt run can execute directly inside a Fabric notebook runtime.