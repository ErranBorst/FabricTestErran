{{ config(alias='orders') }}

-- Logical/file name carries a _gold suffix only to avoid colliding with silver's `orders` model name
-- (dbt model names must be unique project-wide) — the alias above is what actually lands in lh_gold,
-- so the physical, consumer-facing table name stays clean.
select
    order_key
    , order_id
    , customer_id
    , product_category
    , quantity
    , unit_price
    , round(quantity * unit_price, 2) as order_total
    , order_status
    , order_date

from {{ ref('orders') }}
