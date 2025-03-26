WITH source_inventory_data AS (
SELECT * 
FROM {{source('raw','inventory_data')}}
),

final AS (
    SELECT 
    product_id,
    gym_id,
    product_type,
    DATE(inventory_date) AS inventory_date,
    price,
    vacant_adult_units,
    sold_adult_units
    FROM source_inventory_data
)

SELECT *
FROM final