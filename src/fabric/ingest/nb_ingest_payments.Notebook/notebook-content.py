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

# # Ingest Payments (delta/merge load)
#
# The third delta pattern, and the most realistic one: this doesn't just append, it genuinely
# **upserts** using a real Delta Lake `MERGE`. On each run: a random subset of existing `pending`
# payments transition to `paid`/`failed` (an in-place update to an existing row), and any order that
# doesn't have a payment yet gets a new `pending` row inserted — both in the same MERGE statement.
# This is the pattern you'd reach for whenever a source can both add new records and modify existing
# ones (most real operational systems), as opposed to the append-only pattern in `nb_ingest_order_lines`.
#
# Run `nb_ingest_sales_orders` at least once first. `nb_ingest_order_lines` is optional — if it has
# run, payment amounts are computed from the real order lines; otherwise they fall back to a random
# amount.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import random
from datetime import datetime

from pyspark.sql import Row
from pyspark.sql.functions import col, sum as sum_

ORDERS_TABLE = "lh_bronze.dbo.raw_sales_orders"
ORDER_LINES_TABLE = "lh_bronze.dbo.raw_order_lines"
TARGET_TABLE = "lh_bronze.dbo.raw_payments"
PAYMENT_METHODS = ["ideal", "credit_card", "paypal", "bank_transfer"]

spark.sql("""
    CREATE TABLE IF NOT EXISTS lh_bronze.dbo.raw_payments (
        payment_id BIGINT,
        order_id BIGINT,
        payment_date TIMESTAMP,
        amount DOUBLE,
        payment_method STRING,
        payment_status STRING,
        updated_at TIMESTAMP,
        source_system STRING
    ) USING DELTA
""")

assert spark.catalog.tableExists(ORDERS_TABLE), f"{ORDERS_TABLE} doesn't exist yet — run nb_ingest_sales_orders first."

all_order_ids = [r.order_id for r in spark.table(ORDERS_TABLE).select("order_id").distinct().collect()]

order_totals = {}
if spark.catalog.tableExists(ORDER_LINES_TABLE):
    totals = (
        spark.table(ORDER_LINES_TABLE)
        .groupBy("order_id")
        .agg(sum_(col("quantity") * col("unit_price")).alias("total"))
        .collect()
    )
    order_totals = {r.order_id: round(r.total, 2) for r in totals}


def amount_for(order_id):
    return order_totals.get(order_id, round(random.uniform(20, 500), 2))


now = datetime.utcnow()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

if not spark.catalog.tableExists(TARGET_TABLE):
    # First run: no existing rows to update, so a plain write is enough — seed ~70% of orders with a
    # pending payment, leaving the rest to be picked up as "new orders" on the next run.
    seed_order_ids = random.sample(all_order_ids, k=max(1, int(len(all_order_ids) * 0.7)))
    rows = [
        Row(
            payment_id=i + 1,
            order_id=oid,
            payment_date=now,
            amount=amount_for(oid),
            payment_method=random.choice(PAYMENT_METHODS),
            payment_status="pending",
            updated_at=now,
            source_system="sales_demo",
        )
        for i, oid in enumerate(seed_order_ids)
    ]
    df = spark.createDataFrame(rows)
    df.write.mode("overwrite").format("delta").saveAsTable(TARGET_TABLE)
    print(f"Seeded {df.count()} pending payments into {TARGET_TABLE}.")

else:
    from delta.tables import DeltaTable

    existing = spark.table(TARGET_TABLE)
    last_payment_id = existing.selectExpr("max(payment_id) as m").collect()[0]["m"] or 0
    covered_order_ids = {r.order_id for r in existing.select("order_id").distinct().collect()}

    # a) transition roughly half of the currently-pending payments forward
    pending_rows = existing.where("payment_status = 'pending'").collect()
    sample_size = max(1, len(pending_rows) // 2) if pending_rows else 0
    to_transition = random.sample(pending_rows, k=min(sample_size, len(pending_rows))) if pending_rows else []
    transition_rows = [
        Row(
            payment_id=r.payment_id,
            order_id=r.order_id,
            payment_date=r.payment_date,
            amount=r.amount,
            payment_method=r.payment_method,
            payment_status=random.choices(["paid", "failed"], weights=[0.85, 0.15], k=1)[0],
            updated_at=now,
            source_system=r.source_system,
        )
        for r in to_transition
    ]

    # b) brand-new orders that don't have any payment row yet
    new_order_ids = [oid for oid in all_order_ids if oid not in covered_order_ids]
    insert_rows = [
        Row(
            payment_id=last_payment_id + i + 1,
            order_id=oid,
            payment_date=now,
            amount=amount_for(oid),
            payment_method=random.choice(PAYMENT_METHODS),
            payment_status="pending",
            updated_at=now,
            source_system="sales_demo",
        )
        for i, oid in enumerate(new_order_ids)
    ]

    source_rows = transition_rows + insert_rows
    if source_rows:
        source_df = spark.createDataFrame(source_rows)
        (
            DeltaTable.forName(spark, TARGET_TABLE)
            .alias("t")
            .merge(source_df.alias("s"), "t.payment_id = s.payment_id")
            .whenMatchedUpdate(set={"payment_status": "s.payment_status", "updated_at": "s.updated_at"})
            .whenNotMatchedInsertAll()
            .execute()
        )
        print(f"Merged {len(transition_rows)} status transition(s) and {len(insert_rows)} new payment(s) into {TARGET_TABLE}.")
    else:
        print("Nothing to do — no pending payments to transition and no new orders to insert.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
