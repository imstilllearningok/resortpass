WITH source_gym_details AS (
SELECT * 
FROM {{source('raw','gym_details')}}
),

final AS (
    SELECT 
    gym_id,
    CASE 
    WHEN has_sauna IS true THEN 'Yes'
    ELSE 'NO' 
    END has_sauna,
    market,
    tier
    FROM source_gym_details
)

SELECT *
FROM final