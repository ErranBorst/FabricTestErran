# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from pyspark.sql import Row
from pyspark.sql.functions import current_timestamp

table_name = "dummy_sales_orders"

dummy_rows = [
    Row(order_id=1001, customer_name="Contoso Retail", product="Laptop", quantity=2, unit_price=899.99, country="Netherlands"),
    Row(order_id=1002, customer_name="Fabrikam Services", product="Monitor", quantity=4, unit_price=249.50, country="Germany"),
    Row(order_id=1003, customer_name="Northwind Traders", product="Keyboard", quantity=10, unit_price=45.00, country="Belgium"),
    Row(order_id=1004, customer_name="Adventure Works", product="Mouse", quantity=12, unit_price=25.75, country="France"),
    Row(order_id=1005, customer_name="Litware", product="Docking Station", quantity=3, unit_price=179.99, country="United Kingdom")
]

df = spark.createDataFrame(dummy_rows).withColumn("ingested_at", current_timestamp())
display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df.write.mode("overwrite").format("delta").saveAsTable(table_name)
print(f"Wrote {df.count()} rows to lakehouse table '{table_name}'.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

display(spark.table(table_name))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
