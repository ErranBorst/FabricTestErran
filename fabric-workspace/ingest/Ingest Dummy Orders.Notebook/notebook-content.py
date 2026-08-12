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

# # Ingest Dummy Orders Into Fabric Lakehouse
#
# This notebook creates a raw orders dataset and saves it as a Delta table in the attached Fabric lakehouse.

# CELL ********************

from pyspark.sql import Row
from pyspark.sql.functions import col, current_timestamp, lit

target_table = "raw_dummy_orders"
rows = [
    Row(order_id=1, customer_id=101, product_category="laptop", quantity=1, unit_price=1200.0, order_status="created", order_date="2026-08-01"),
    Row(order_id=2, customer_id=102, product_category="monitor", quantity=2, unit_price=340.0, order_status="shipped", order_date="2026-08-02"),
    Row(order_id=3, customer_id=103, product_category="keyboard", quantity=3, unit_price=55.0, order_status="created", order_date="2026-08-03"),
    Row(order_id=4, customer_id=101, product_category="mouse", quantity=2, unit_price=35.0, order_status="delivered", order_date="2026-08-04"),
    Row(order_id=5, customer_id=104, product_category="dock", quantity=1, unit_price=210.0, order_status="cancelled", order_date="2026-08-05")
]

df = (
    spark.createDataFrame(rows)
    .withColumn("order_date", col("order_date").cast("date"))
    .withColumn("source_system", lit("dummy_seed"))
    .withColumn("ingested_at", current_timestamp())
)
display(df)

# CELL ********************

df.write.mode("overwrite").format("delta").saveAsTable(target_table)
print(f"Table {target_table} refreshed with {df.count()} rows.")

# CELL ********************

display(spark.table(target_table))
