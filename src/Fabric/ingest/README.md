# Ingest

This layer contains Fabric notebooks that land raw data into the lakehouse.

## Assets
- `notebooks/01_ingest_dummy_orders_to_lakehouse.ipynb`: creates a raw Delta table named `raw_dummy_orders` in the attached lakehouse.

## Expected pattern
- Land raw data in Delta tables.
- Keep transformations out of ingest notebooks.
- Use this layer for APIs, files, event streams, and dummy test loads.
