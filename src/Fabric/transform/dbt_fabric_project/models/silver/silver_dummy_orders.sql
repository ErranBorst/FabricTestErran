{{ config(
    unique_key='order_id',
    file_format='delta'
) }}

with source_data as (
    select
        order_id,
        customer_id,
        product_category,
        quantity,
        unit_price,
        quantity * unit_price as order_amount,
        order_status,
        order_date,
        source_system,
        ingested_at,
        current_timestamp() as transformed_at
    from {{ ref('bronze_dummy_orders') }}
    where order_status <> 'cancelled'
)

select *
from source_data
{% if is_incremental() %}
where ingested_at >= coalesce((select max(ingested_at) from {{ this }}), cast('1900-01-01' as timestamp))
{% endif %}
