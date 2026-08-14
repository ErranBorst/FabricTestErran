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

# # Ingest Customers (full load)
#
# Regenerates the whole `raw_customers` dimension every run (`overwrite`). This is the "full load"
# pattern: the source is treated as a complete snapshot each time, so there's no batching/watermark
# logic — just replace the table. A fixed random seed makes the output deterministic across runs,
# which makes it easy to reason about while you're learning; remove the seed if you want the data to
# actually change run to run.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import random
from datetime import date, timedelta

from pyspark.sql import Row
from pyspark.sql.functions import col, current_timestamp, lit

random.seed(42)

FIRST_NAMES = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Lucas", "Mia", "Ethan", "Sophia", "Mason",
               "Isabella", "Logan", "Amelia", "James", "Charlotte", "Benjamin", "Harper", "Elijah",
               "Evelyn", "Oliver"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "de Vries", "Jansen", "Bakker", "Visser", "Peters"]
COUNTRIES = ["NL", "BE", "DE", "FR", "GB", "US"]
SEGMENTS = ["retail", "business", "vip"]

CUSTOMER_COUNT = 60
epoch = date(2022, 1, 1)

rows = []
for customer_id in range(1, CUSTOMER_COUNT + 1):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    signup_offset_days = random.randint(0, 1000)
    rows.append(
        Row(
            customer_id=customer_id,
            first_name=first,
            last_name=last,
            email=f"{first.lower()}.{last.lower().replace(' ', '')}{customer_id}@example.test",
            country=random.choice(COUNTRIES),
            customer_segment=random.choice(SEGMENTS),
            signup_date=(epoch + timedelta(days=signup_offset_days)).isoformat(),
        )
    )

df = (
    spark.createDataFrame(rows)
    .withColumn("signup_date", col("signup_date").cast("date"))
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

spark.sql("""
    CREATE TABLE IF NOT EXISTS lh_bronze.dbo.raw_customers (
        customer_id BIGINT,
        first_name STRING,
        last_name STRING,
        email STRING,
        country STRING,
        customer_segment STRING,
        signup_date DATE,
        source_system STRING,
        ingested_at TIMESTAMP
    ) USING DELTA
""")

target_table = "lh_bronze.dbo.raw_customers"
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
