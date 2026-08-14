# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "45dad4c7-60f6-4961-9e71-583997fcb191",
# META       "default_lakehouse_name": "lh_bronze",
# META       "default_lakehouse_workspace_id": "efce90bf-d5cf-41ce-bb1f-d83e2889332f",
# META       "known_lakehouses": [
# META         {
# META           "id": "45dad4c7-60f6-4961-9e71-583997fcb191"
# META         }
# META       ]
# META     },
# META     "warehouse": {
# META       "known_warehouses": []
# META     }
# META   }
# META }

# CELL ********************

# # Ingest Sales Orders (delta/append load)
#
# Unlike the full-load notebooks, this one never overwrites: each run reads the current max
# `order_id`/`batch_id` out of `raw_sales_orders` (if it exists yet) and appends a fresh batch of new
# orders on top. Run this notebook multiple times to build up order history across "batches" — that's
# what makes it a realistic stand-in for an incrementally-arriving source feed, and what lets you
# practice incremental materializations downstream (e.g. only picking up rows newer than what your
# silver model has already processed).
#
# Run `nb_ingest_customers` at least once first — `customer_id` here is drawn from that table's range.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import random
from datetime import datetime, timedelta

from pyspark.sql import Row
from pyspark.sql.functions import col, current_timestamp, lit

TARGET_TABLE = "lh_bronze.dbo.raw_sales_orders"
ORDERS_PER_BATCH = 20
CUSTOMER_ID_RANGE = (1, 60)  # must match nb_ingest_customers' CUSTOMER_COUNT
COUNTRIES = ["NL", "BE", "DE", "FR", "GB", "US"]
STATUSES = ["created", "shipped", "delivered", "cancelled"]
STATUS_WEIGHTS = [0.35, 0.25, 0.35, 0.05]

if spark.catalog.tableExists(TARGET_TABLE):
    existing = spark.table(TARGET_TABLE)
    last_order_id = existing.selectExpr("max(order_id) as m").collect()[0]["m"] or 0
    last_batch_id = existing.selectExpr("max(batch_id) as m").collect()[0]["m"] or 0
else:
    last_order_id = 0
    last_batch_id = 0

next_batch_id = last_batch_id + 1
now = datetime.utcnow()

rows = []
for i in range(ORDERS_PER_BATCH):
    order_id = last_order_id + i + 1
    order_date = now - timedelta(days=random.randint(0, 3), hours=random.randint(0, 23))
    rows.append(
        Row(
            order_id=order_id,
            customer_id=random.randint(*CUSTOMER_ID_RANGE),
            order_date=order_date.isoformat(),
            order_status=random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0],
            shipping_country=random.choice(COUNTRIES),
            batch_id=next_batch_id,
        )
    )

df = (
    spark.createDataFrame(rows)
    .withColumn("order_date", col("order_date").cast("timestamp"))
    .withColumn("source_system", lit("sales_demo"))
    .withColumn("ingested_at", current_timestamp())
)
display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

(
    df.write.mode("append")
    .format("delta")
    .saveAsTable(TARGET_TABLE)
)
print(f"Appended batch {next_batch_id}: {df.count()} new orders (order_id {last_order_id + 1}-{last_order_id + ORDERS_PER_BATCH}) into {TARGET_TABLE}.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
