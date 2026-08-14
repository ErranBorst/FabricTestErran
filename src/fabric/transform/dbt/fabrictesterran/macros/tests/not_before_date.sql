{#
  Domain invariant: a date/timestamp column should never hold a value before the source system's
  epoch/go-live date. Catches sentinel dates that slipped past normalize_sentinel_date() and genuinely
  bad source data alike. Parameterize `min_date` per column via the schema yml config.
#}
{% test not_before_date(model, column_name, min_date) %}

with validation as (

    select {{ column_name }} as date_value
    from {{ model }}
    where {{ column_name }} is not null

)

select *
from validation
where date_value < cast('{{ min_date }}' as date)

{% endtest %}
