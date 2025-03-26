WITH main_gym_details AS (
    SELECT * 
    FROM {{ ref('main_gym_details') }}  -- or whatever filename you gave it
),

main_inventory_data AS (
    SELECT * 
    FROM {{ ref('main_inventory_data') }}  -- same here
),

joined AS (
    SELECT 
        i.product_id,
        i.gym_id,
        g.has_sauna,
        g.market,
        g.tier,
        i.product_type,
        i.inventory_date,
        i.price,
        i.vacant_adult_units,
        i.sold_adult_units
    FROM main_inventory_data i
    LEFT JOIN main_gym_details g
        ON i.gym_id = g.gym_id
)

SELECT *
FROM joined
