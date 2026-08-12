select
    cast(order_id as bigint) as order_id,
    cast(customer_id as bigint) as customer_id,
    lower(trim(product_category)) as product_category,
    cast(quantity as int) as quantity,
    cast(unit_price as double) as unit_price,
    lower(trim(order_status)) as order_status,
    cast(order_date as date) as order_date,
    cast(source_system as string) as source_system,
    cast(ingested_at as timestamp) as ingested_at
from {{ source('fabric_raw', 'raw_dummy_orders') }}
