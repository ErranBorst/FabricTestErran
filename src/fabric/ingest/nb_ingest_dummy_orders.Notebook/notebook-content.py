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

# MARKDOWN ********************


# CELL ********************

# # Ingest Dummy Orders Into lh_bronze
#
# Seeds a raw orders dataset as a Delta table in the attached bronze lakehouse. This stands in for a
# real source connection (Fabric Mirroring / OneLake shortcut) until one is wired up — delete once a
# real source lands in src/fabric/ingest.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import Row
from pyspark.sql.functions import col, current_timestamp, lit

lakehouse_name = "lh_bronze"
target_table_name = "raw_orders"
target_table = f"{lakehouse_name}.dbo.{target_table_name}"
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
    .withColumn("source_system", lit("dummy"))
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
    df.write.mode("overwrite")
    .format("delta")
    .option("overwriteSchema", "true")
    .saveAsTable(target_table)
)
print(f"Bronze table {target_table} refreshed with {df.count()} rows.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

display(spark.table(target_table))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
