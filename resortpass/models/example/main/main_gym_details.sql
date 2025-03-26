WITH source_gym_details AS (
SELECT * 
FROM {{source('raw','gym_details')}}
),

final AS (
    SELECT * 
    FROM source_gym_details
)

SELECT *
FROM final