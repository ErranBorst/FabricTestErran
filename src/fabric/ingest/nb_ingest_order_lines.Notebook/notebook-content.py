# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "",
# META       "default_lakehouse_name": "lh_bronze",
# META       "default_lakehouse_workspace_id": "",
# META       "known_lakehouses": []
# META     },
# META     "warehouse": {
# META       "known_warehouses": []
# META     }
# META   }
# META }

# CELL ********************

# # Ingest Order Lines (delta/append load, two-table relation)
#
# Instead of tracking batches like `nb_ingest_sales_orders`, this notebook works out what's new by
# comparing two tables: it finds every `order_id` in `raw_sales_orders` that doesn't have line items
# in `raw_order_lines` yet, and only generates lines for those. That's a different (and very common)
# flavor of incremental logic — "process what's missing downstream" instead of "process the newest
# batch" — and it's naturally idempotent: re-running it without new orders does nothing.
#
# Run `nb_ingest_sales_orders` and `nb_ingest_products` at least once first.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import random

from pyspark.sql import Row
from pyspark.sql.functions import current_timestamp, lit

ORDERS_TABLE = "lh_bronze.dbo.raw_sales_orders"
PRODUCTS_TABLE = "lh_bronze.dbo.raw_products"
TARGET_TABLE = "lh_bronze.dbo.raw_order_lines"

assert spark.catalog.tableExists(ORDERS_TABLE), f"{ORDERS_TABLE} doesn't exist yet — run nb_ingest_sales_orders first."
assert spark.catalog.tableExists(PRODUCTS_TABLE), f"{PRODUCTS_TABLE} doesn't exist yet — run nb_ingest_products first."

all_order_ids = [r.order_id for r in spark.table(ORDERS_TABLE).select("order_id").distinct().collect()]
active_products = [
    (r.product_id, r.unit_price)
    for r in spark.table(PRODUCTS_TABLE).where("is_active = true").select("product_id", "unit_price").collect()
]

if spark.catalog.tableExists(TARGET_TABLE):
    existing = spark.table(TARGET_TABLE)
    covered_order_ids = {r.order_id for r in existing.select("order_id").distinct().collect()}
    last_line_id = existing.selectExpr("max(order_line_id) as m").collect()[0]["m"] or 0
else:
    covered_order_ids = set()
    last_line_id = 0

pending_order_ids = [oid for oid in all_order_ids if oid not in covered_order_ids]
print(f"{len(pending_order_ids)} order(s) still need line items.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

rows = []
next_line_id = last_line_id + 1
for order_id in pending_order_ids:
    for _ in range(random.randint(1, 4)):
        product_id, unit_price = random.choice(active_products)
        rows.append(
            Row(
                order_line_id=next_line_id,
                order_id=order_id,
                product_id=product_id,
                quantity=random.randint(1, 5),
                unit_price=unit_price,
            )
        )
        next_line_id += 1

if rows:
    df = (
        spark.createDataFrame(rows)
        .withColumn("source_system", lit("sales_demo"))
        .withColumn("ingested_at", current_timestamp())
    )
    display(df)
    (
        df.write.mode("append")
        .format("delta")
        .saveAsTable(TARGET_TABLE)
    )
    print(f"Appended {df.count()} line items for {len(pending_order_ids)} order(s) into {TARGET_TABLE}.")
else:
    print("Nothing to do — every existing order already has line items.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
