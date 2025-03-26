WITH joined AS (
    SELECT *
    FROM {{ ref('joined') }}
),
calendar AS (
    SELECT *
    FROM {{ ref('calendar_dim') }}
),
with_calendar AS (
    SELECT 
        j.*,
        c.day_of_week_name,
        c.month_name,
        CASE
        WHEN c.day_of_week_name IN ('Saturday', 'Sunday') THEN 1
        ELSE 0
        END AS is_weekend,
        CASE
        WHEN c.month_name IN ('January', 'February', 'March') THEN 'Q1'
        WHEN c.month_name IN ('April', 'May', 'June') THEN 'Q2'
        WHEN c.month_name IN ('July', 'August', 'September') THEN 'Q3'
        ELSE 'Q4'
        END AS quarter
    FROM joined j
    LEFT JOIN calendar c
        ON j.inventory_date = c.date_day
),
add_columns AS (
    SELECT 
        *,
        (sold_adult_units + vacant_adult_units) AS available_units,
        ROUND(SAFE_DIVIDE(sold_adult_units, sold_adult_units + vacant_adult_units),2) AS booking_rate,
        ROUND(SAFE_DIVIDE(vacant_adult_units, sold_adult_units + vacant_adult_units), 2) AS vacancy_rate,
        (sold_adult_units * price) AS revenue
    FROM with_calendar
),
rolling_average_last_4_weeks AS (
    SELECT 
        *,
        AVG(booking_rate) OVER (PARTITION BY gym_id, product_type ORDER BY inventory_date ROWS BETWEEN 28 PRECEDING AND CURRENT ROW) AS rolling_avg_booking_rate_last_4_weeks,
        AVG(vacancy_rate) OVER (PARTITION BY gym_id, product_type ORDER BY inventory_date ROWS BETWEEN 28 PRECEDING AND CURRENT ROW) AS rolling_avg_vacancy_rate_last_4_weeks
    FROM add_columns
),
market_numbers AS (
    SELECT 
        gym_id,
        product_id,
        inventory_date,
        market,
        tier,
        has_sauna,
        product_type,
        PERCENTILE_CONT(price, 0.5) OVER (PARTITION BY inventory_date, market, product_type, tier) AS market_median_price,
        AVG(price) OVER (PARTITION BY inventory_date, market, product_type) AS market_avg_price,
        AVG(booking_rate) OVER (PARTITION BY inventory_date, market, product_type) AS market_avg_booking_rate
    FROM rolling_average_last_4_weeks
),
final AS (
    SELECT 
        r.*,
        m.market_median_price,
        m.market_avg_price,
        m.market_avg_booking_rate,
        ROUND(SAFE_DIVIDE(r.price - m.market_median_price, m.market_median_price), 2) AS price_vs_market_median,
        ROUND(SAFE_DIVIDE(r.booking_rate - m.market_avg_booking_rate, m.market_avg_booking_rate), 2) AS booking_rate_vs_market
    FROM rolling_average_last_4_weeks r
    LEFT JOIN market_numbers m
        ON r.inventory_date = m.inventory_date
        AND r.product_id = m.product_id
        AND r.market = m.market
        AND r.product_type = m.product_type
        AND r.tier = m.tier
        AND r.has_sauna = m.has_sauna
        AND r.gym_id = m.gym_id
         
)
SELECT *
FROM final
ORDER BY 1,2,7 DESC