{{ config(materialized='table') }}

SELECT
    resort,
    fetched_at,
    snowfall_in,
    SUM(COALESCE(snowfall_in, 0)) OVER (
        PARTITION BY resort
        ORDER BY fetched_at
        ROWS BETWEEN 72 PRECEDING AND CURRENT ROW
    ) AS rolling_72hr_snowfall
FROM {{ source('main', 'conditions') }}