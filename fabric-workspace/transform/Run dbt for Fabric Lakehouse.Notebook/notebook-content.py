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

# MARKDOWN ********************

# # Run dbt for Fabric Lakehouse
#
# This notebook installs dbt-fabricspark, writes a local Fabric Notebook auth profile, and runs the repository dbt project.

# CELL ********************

workspace_id = "<fabric-workspace-guid>"
lakehouse_id = "<fabric-lakehouse-guid>"
lakehouse_name = "bronze_lakehouse"
schema_name = "bronze_lakehouse"
dbt_project_dir = "/lakehouse/default/Files/FabricTestErran/src/Fabric/transform/dbt_fabric_project"

# CELL ********************

%pip install -U dbt-fabricspark

# CELL ********************

from pathlib import Path

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

# CELL ********************

%cd {dbt_project_dir}
!dbt debug
!dbt deps
!dbt build
