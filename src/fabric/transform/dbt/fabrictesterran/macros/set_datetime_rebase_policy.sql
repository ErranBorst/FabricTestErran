{#
  Adapter workaround, not speculative: Spark's default datetime rebase policy (SPARK-31404) can raise
  or silently shift dates written/read before the Gregorian calendar's 1582-10-15 cutover, which is a
  real risk for operational-system data with old or bad dates. Pinning both read and write to LEGACY
  avoids the exception and keeps round-tripped dates stable. Applied as a pre-hook on silver/gold only
  — bronze is ephemeral and inlines into whatever references it.
#}
{% macro set_datetime_rebase_policy() %}
  {% set statements = [
    "SET spark.sql.parquet.datetimeRebaseModeInRead = LEGACY",
    "SET spark.sql.parquet.datetimeRebaseModeInWrite = LEGACY",
    "SET spark.sql.parquet.int96RebaseModeInRead = LEGACY",
    "SET spark.sql.parquet.int96RebaseModeInWrite = LEGACY"
  ] %}
  {% for statement in statements %}
    {% do run_query(statement) %}
  {% endfor %}
{% endmacro %}
