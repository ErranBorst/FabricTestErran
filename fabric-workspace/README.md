# Fabric Workspace Sync Root

Connect your Microsoft Fabric workspace Git integration to this folder, not to the repository root.

## Included Fabric items
- `ingest/Ingest Dummy Orders.Notebook`
- `lakehouse/Bronze Lakehouse.Lakehouse`
- `lakehouse/Silver Lakehouse.Lakehouse`
- `lakehouse/Gold Lakehouse.Lakehouse`
- `ops/Fabric ETL Orchestration.DataPipeline`
- `transform/Run dbt for Fabric Lakehouse.Notebook`

## Notes
- The existing `src/Fabric` tree is kept as supporting project code and documentation.
- Fabric Git integration only imports recognized item folders that contain `.platform` metadata and item definition files.
- After the first sync, open the imported pipeline in Fabric and bind notebook activities if you want runtime-executable notebook references.
