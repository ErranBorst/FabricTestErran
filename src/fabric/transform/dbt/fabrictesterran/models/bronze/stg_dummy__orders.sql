with source as (

    select * from {{ source('dummy', 'raw_orders') }}

),

renamed as (

    select
        order_id
        , customer_id
        , product_category
        , quantity
        , cast(unit_price as decimal(18, 2)) as unit_price
        , order_status
        , order_date
        , source_system
        , ingested_at

    from source

)

select * from renamed
