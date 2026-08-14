with stg_orders as (

    select * from {{ ref('stg_dummy__orders') }}

),

final as (

    select
        {{ dbt_utils.generate_surrogate_key(['order_id', 'source_system']) }} as order_key
        , order_id
        , customer_id
        , product_category
        , quantity
        , unit_price
        , order_status
        -- demonstrates the sentinel-date macro; the dummy dataset has no real sentinels to clean up
        , {{ normalize_sentinel_date('order_date') }} as order_date
        , source_system
        , ingested_at

    from stg_orders

)

select * from final
