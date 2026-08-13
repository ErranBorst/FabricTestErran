# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "",
# META       "default_lakehouse_name": "Bronze Lakehouse",
# META       "default_lakehouse_workspace_id": ""
# META     }
# META   }
# META }

# CELL ********************

# # Run dbt for Fabric Lakehouse
#
# This notebook installs dbt-fabricspark, writes a local Fabric Notebook auth profile, and runs the repository dbt project.

# METADATA ********************

# META {
# META   "language": "markdown",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

workspace_id = "efce90bf-d5cf-41ce-bb1f-d83e2889332f"
lakehouse_id = "45dad4c7-60f6-4961-9e71-583997fcb191"
lakehouse_name = "bronze_lakehouse"
schema_name = "bronze_lakehouse"
dbt_project_dir = "/lakehouse/default/Files/FabricTestErran/src/Fabric/transform/dbt_fabric_project"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

%pip install -U dbt-fabricspark

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pathlib import Path

workspace_id = globals().get("workspace_id", "<fabric-workspace-guid>")
lakehouse_id = globals().get("lakehouse_id", "<fabric-lakehouse-guid>")
lakehouse_name = globals().get("lakehouse_name", "bronze_lakehouse")
schema_name = globals().get("schema_name", lakehouse_name)

missing_config = [
  name
  for name, value in {
    "workspace_id": workspace_id,
    "lakehouse_id": lakehouse_id,
  }.items()
  if value.startswith("<") and value.endswith(">")
]

if missing_config:
  raise ValueError(
    "Set these notebook variables before running the dbt profile cell: "
    + ", ".join(missing_config)
  )

dbt_dir = Path.home() / ".dbt"
dbt_dir.mkdir(parents=True, exist_ok=True)
profiles_yml = f"""
fabric_etl_project:
  target: dev
  outputs:
    dev:
      type: fabricspark
      method: livy
      endpoint: https://api.fabric.microsoft.com/v1
      workspaceid: {workspace_id}
      lakehouseid: {lakehouse_id}
      lakehouse: {lakehouse_name}
      schema: {schema_name}
      authentication: fabric_notebook
      threads: 1
      retry_all: true
      reuse_session: true
      spark_config:
        name: fabric-dbt-notebook
        conf:
          spark.sql.caseSensitive: "false"
"""
(dbt_dir / "profiles.yml").write_text(profiles_yml, encoding="utf-8")
print((dbt_dir / "profiles.yml").read_text(encoding="utf-8"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

dbt_project_dir = globals().get(
  "dbt_project_dir",
  "/lakehouse/default/Files/FabricTestErran/src/Fabric/transform/dbt_fabric_project",
)

%cd {dbt_project_dir}
!dbt debug
!dbt deps
!dbt build

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
