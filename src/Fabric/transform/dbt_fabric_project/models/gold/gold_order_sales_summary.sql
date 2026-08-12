select
    order_date,
    product_category,
    order_status,
    count(*) as order_count,
    sum(quantity) as total_quantity,
    round(sum(order_amount), 2) as total_revenue,
    max(transformed_at) as last_transformed_at
from {{ ref('silver_dummy_orders') }}
group by
    order_date,
    product_category,
    order_status
