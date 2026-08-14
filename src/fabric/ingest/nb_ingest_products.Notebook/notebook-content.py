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

# # Ingest Products (full load)
#
# Same "full load" pattern as `nb_ingest_customers`: the whole `raw_products` catalog is regenerated
# and overwritten every run. A second full-load example, deliberately using the same technique, so
# it's clear the pattern isn't special-cased per table — it's just "overwrite the whole target".

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import random

from pyspark.sql import Row
from pyspark.sql.functions import current_timestamp, lit

random.seed(7)

CATEGORIES = {
    "laptop": (700, 2200),
    "monitor": (150, 600),
    "keyboard": (20, 150),
    "mouse": (10, 90),
    "dock": (60, 250),
    "headphones": (30, 350),
    "webcam": (25, 180),
    "cable": (5, 40),
    "chair": (100, 900),
    "desk": (150, 1200),
}
PRODUCT_COUNT = 40

rows = []
for product_id in range(1, PRODUCT_COUNT + 1):
    category = random.choice(list(CATEGORIES.keys()))
    low, high = CATEGORIES[category]
    rows.append(
        Row(
            product_id=product_id,
            product_name=f"{category.capitalize()} Model {product_id}",
            category=category,
            unit_price=round(random.uniform(low, high), 2),
            is_active=random.random() > 0.1,  # ~10% discontinued, useful for testing filters/joins
        )
    )

df = (
    spark.createDataFrame(rows)
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

target_table = "lh_bronze.dbo.raw_products"
(
    df.write.mode("overwrite")
    .format("delta")
    .option("overwriteSchema", "true")
    .saveAsTable(target_table)
)
print(f"Full load complete: {target_table} now has {df.count()} rows.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
