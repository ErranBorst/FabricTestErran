# FabricTestErran

A Microsoft Fabric + dbt medallion (bronze → silver → gold) data platform, following the reference
architecture documented in the Customer-Hillfresh-Fabric repo's `docs/architecture-template/`. One
dbt project runs on Spark inside Fabric (`dbt-fabricspark`, method `livy`); ingestion lands data in
`lh_bronze`, dbt owns bronze→silver→gold, and reporting will eventually sit on Direct Lake semantic
models over `lh_gold`.

## Structure

```
src/fabric/
  ingest/     nb_ingest_dummy_orders.Notebook  — seeds the example dataset (stand-in for a real source)
  lakehouse/  lh_bronze / lh_silver / lh_gold Lakehouse items
  transform/  dbt/fabrictesterran (the dbt project) + nb_dbt_transformations.Notebook (runs it) + env_dbt.Environment
  ops/        pl_scheduled_transform.DataPipeline (triggers the dbt-run notebook)
  semantic/   reserved for the future Direct Lake semantic model + reports
docs/         naming-conventions.md, dbt-conventions.md
config/       parameter.yml — fabric-cicd GUID substitution for the production deploy
scripts/      deploy_fabric_items.py — fabric-cicd deploy wrapper used by CI
.github/workflows/  deploy-production.yml
```

Two environments only — no separate `dev` tier:

- **acceptance**: Git-linked directly in the Fabric portal. This is where you work day to day; there
  is no CI step for it, the same way a `dev` workspace would normally need none.
- **production**: never Git-linked. Reached only through `deploy-production.yml`, gated by a GitHub
  Environment approval, triggered from a `release/*` branch.

Each `src/fabric/<function>` folder is the intended Git-sync root for its own `<function>-acceptance`
Fabric workspace (`<function>-<environment>`, e.g. `lakehouse-acc`) — see "Manual follow-up" below.

## Running dbt locally

```bash
cd "src/fabric/transform/dbt/fabrictesterran"
az login
pip install -r requirements-dev.txt
dbt deps
dbt build --target acceptance
```

The `acceptance` target authenticates via your Azure CLI login; `<<FABRIC_WORKSPACE_ID>>` and
`<<SILVER_LAKEHOUSE_ID>>` in `profiles.yml` need to be filled in with your acceptance
workspace/lakehouse IDs first (see "Manual follow-up").

## Running it in Fabric

`nb_dbt_transformations.Notebook` downloads the dbt project straight from GitHub (this repo is
public) into a writable temp directory, then runs `dbt deps` + `dbt build` using the notebook's own
Fabric identity (`fabric_notebook` target — no secrets). `pl_scheduled_transform` is the pipeline that
will eventually trigger it on a schedule.

This downloads from GitHub instead of copying from Fabric's built-in Notebook Resources
(`Resources/builtin/`, the architecture's original design) for two reasons: that Fabric feature did
not reliably sync nested resource files into the notebook item in testing, and — worse — anything
committed inside a Fabric item's own folder gets overwritten by Fabric's *own* git commit-back on the
next workspace sync, which silently deleted the whole dbt project from Git once it was placed there.
That's why the dbt project now lives at `src/fabric/transform/dbt/fabrictesterran/`, a plain folder
next to (not inside) `nb_dbt_transformations.Notebook/` — Fabric's Git sync only manages recognized
item folders (`*.Notebook`, `*.Lakehouse`, etc.), so a plain folder next to one is never touched by it.

## Adding a new business entity

Follow `docs/dbt-conventions.md` ("Adding a new entity"): bronze source yml entry → bronze staging
model → silver model → gold model → schema/test yml, then delete `stg_dummy__orders` /
`nb_ingest_dummy_orders.Notebook` / the `orders` example models once a real entity replaces them.

## Manual follow-up (not doable via file edits)

1. **Acceptance workspaces**: create Fabric workspaces `ingest-acc`, `lakehouse-acc`,
   `transform-acc`, `ops-acc`, `semantic-acc` (repurpose/rename the existing single workspace as one
   of these), and connect each one's Git integration to its matching `src/fabric/<function>` folder —
   Fabric binds one workspace to one folder, so 5 separate connections replace the old single-folder
   sync.
2. **Production workspaces**: create `ingest-prod`, `lakehouse-prod`, `transform-prod`, `ops-prod`,
   `semantic-prod`. Do **not** Git-link these — they're populated only by `deploy-production.yml`.
3. **Placeholders**: once the acceptance workspaces/lakehouses exist, fill in
   `<<FABRIC_WORKSPACE_ID>>`, `<<SILVER_LAKEHOUSE_ID>>` in `profiles.yml`, and
   `<<TRANSFORM_NOTEBOOK_ID>>` in `pl_scheduled_transform`'s pipeline definition (the ones in
   `config/parameter.yml` are resolved automatically at deploy time, or filled in by hand once the
   production items they reference exist — see the comments there).
4. **CI/CD**: register an Entra ID app registration with federated credentials (OIDC) for GitHub
   Actions, add its client/tenant/subscription IDs as repo variables, and create a `production`
   GitHub Environment with an approval gate.
