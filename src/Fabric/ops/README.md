# Ops

This layer contains operational guidance for running and deploying the Fabric ETL project.

## Operational responsibilities
- Schedule ingest notebooks.
- Trigger dbt notebook runs after raw loads complete.
- Monitor dbt test failures and notebook execution logs.
- Promote workspace and lakehouse settings between dev, test, and prod.
