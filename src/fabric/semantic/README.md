# Semantic workspace (reserved)

This folder is the future Git-sync root for the `semantic-acc` Fabric workspace (Git-linked directly)
and the deployment target for `semantic-prod` (deployed via CI). It will hold a Direct Lake semantic
model over `lh_gold`, plus the Power BI reports built on top of it.

Semantic models and reports are normally authored in the Fabric/Power BI UI rather than hand-written,
so no item is scaffolded here yet. Add one once the first gold model (see
`src/fabric/transform/.../models/gold/`) is stable enough to report on.
