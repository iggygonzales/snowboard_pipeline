{{ config(materialized='table') }}

SELECT
    resort,
    DATE_TRUNC('day', fetched_at) AS day,
    MIN(temp_f) AS min_temp,
    MAX(temp_f) AS max_temp,
    CASE
        WHEN MIN(temp_f) <= 28 AND MAX(temp_f) >= 34 THEN 1
        ELSE 0
    END AS freeze_thaw_flag
FROM {{ source('main', 'conditions') }}
GROUP BY resort, DATE_TRUNC('day', fetched_at)