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
# Downloads the dbt project straight from GitHub into a writable temp directory, then runs `dbt deps`
# followed by `dbt build`. Uses the notebook's own Fabric identity (authentication: fabric_notebook)
# — no secrets, no interactive login.
#
# This fetches from GitHub instead of Fabric's built-in Notebook Resources (Resources/builtin) for two
# reasons: that feature did not reliably sync nested resource files into this notebook item in
# testing (the `builtin` folder was created but stayed empty), and — more importantly — anything
# inside a Fabric item's own folder (<name>.Notebook/, .Lakehouse/, etc.) gets overwritten by Fabric's
# own git commit-back on the next workspace sync, which silently deleted the whole dbt project from
# Git once. The dbt project now lives at src/fabric/transform/dbt/fabrictesterran/ — a plain folder
# next to this notebook item, not inside it — specifically so Fabric's git sync has no item to
# recognize there and leaves it alone.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

%pip install dbt-fabricspark==1.12.9

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import io
import shutil
import tarfile
import urllib.request
from pathlib import Path

GITHUB_OWNER = "ErranBorst"
GITHUB_REPO = "FabricTestErran"
GITHUB_REF = "acceptance"  # fabric-cicd's config/parameter.yml overrides this for the prod deploy

PROJECT_NAME = "fabrictesterran"
DBT_PROJECT_PATH_IN_REPO = f"src/fabric/transform/dbt/{PROJECT_NAME}"
WORKING_DBT_DIR = Path("/tmp") / PROJECT_NAME

archive_url = f"https://codeload.github.com/{GITHUB_OWNER}/{GITHUB_REPO}/tar.gz/refs/heads/{GITHUB_REF}"
with urllib.request.urlopen(archive_url) as response:
    archive_bytes = response.read()

if WORKING_DBT_DIR.exists():
    shutil.rmtree(WORKING_DBT_DIR)
WORKING_DBT_DIR.mkdir(parents=True)

extracted = 0
with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as tar:
    members = tar.getmembers()
    # GitHub names the archive's single top-level folder after the repo+ref (with "/" in the ref
    # replaced by "-"), so read it back from the archive itself rather than reconstructing it.
    top_level_dir = members[0].name.split("/")[0]
    prefix = f"{top_level_dir}/{DBT_PROJECT_PATH_IN_REPO}/"

    for member in members:
        if not member.name.startswith(prefix):
            continue
        relative_name = member.name[len(prefix):]
        if not relative_name:
            continue
        member.name = relative_name
        tar.extract(member, WORKING_DBT_DIR)
        extracted += 1

assert extracted > 0, f"No files extracted — check GITHUB_REF ({GITHUB_REF}) and DBT_PROJECT_PATH_IN_REPO"
assert (WORKING_DBT_DIR / "dbt_project.yml").exists(), "dbt_project.yml missing after download"
assert (WORKING_DBT_DIR / "profiles.yml").exists(), "profiles.yml missing after download"

print(f"dbt project ready at {WORKING_DBT_DIR} ({extracted} files)")

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
