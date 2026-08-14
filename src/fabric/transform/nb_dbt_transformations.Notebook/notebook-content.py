# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "",
# META       "default_lakehouse_name": "lh_silver",
# META       "default_lakehouse_workspace_id": ""
# META     },
# META     "environment": {
# META       "environmentId": "",
# META       "workspaceId": ""
# META     }
# META   }
# META }

# CELL ********************

# # Run dbt for Fabric Lakehouse
#
# Copies the built-in dbt project out of this notebook's read-only Resources folder into a writable
# temp directory, then runs `dbt deps` followed by `dbt build`. Uses the notebook's own Fabric
# identity (authentication: fabric_notebook) — no secrets, no interactive login.

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

import shutil
from pathlib import Path

PROJECT_NAME = "fabrictesterran"
BUILTIN_DBT_DIR = Path(notebookutils.nbResPath) / "builtin" / "dbt" / PROJECT_NAME
WORKING_DBT_DIR = Path("/tmp") / PROJECT_NAME

if WORKING_DBT_DIR.exists():
    shutil.rmtree(WORKING_DBT_DIR)
shutil.copytree(BUILTIN_DBT_DIR, WORKING_DBT_DIR)

assert (WORKING_DBT_DIR / "dbt_project.yml").exists(), "dbt_project.yml missing after copy"
assert (WORKING_DBT_DIR / "profiles.yml").exists(), "profiles.yml missing after copy"

print(f"dbt project ready at {WORKING_DBT_DIR}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import os

from dbt.cli.main import dbtRunner

os.chdir(WORKING_DBT_DIR)

dbt = dbtRunner()
common_args = ["--project-dir", str(WORKING_DBT_DIR), "--profiles-dir", str(WORKING_DBT_DIR), "--target", "fabric_notebook"]

deps_result = dbt.invoke(["deps", *common_args])
if not deps_result.success:
    raise RuntimeError("dbt deps failed") from deps_result.exception

build_result = dbt.invoke(["build", *common_args])
if not build_result.success:
    raise RuntimeError("dbt build failed") from build_result.exception

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
