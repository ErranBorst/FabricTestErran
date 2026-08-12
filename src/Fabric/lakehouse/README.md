# Lakehouse

This folder documents the intended Fabric lakehouse layout for the ETL project.

## Recommended setup
- `bronze_lakehouse`: raw landing zone for ingest outputs.
- `silver_lakehouse`: validated and conformed data products.
- `gold_lakehouse`: curated marts for analytics and semantic consumption.

## Notes
- For a single-lakehouse starter setup, keep all objects in one lakehouse and promote with table naming.
- For dbt on Fabric Spark, schema-enabled lakehouses are recommended when you want separate bronze, silver, and gold schemas.
