{{ config(materialized='table') }}

SELECT
    c.resort,
    c.state,
    c.fetched_at,
    c.temp_f,
    c.wind_speed_mph,
    c.snowfall_in,
    c.conditions,
    COALESCE(s.rolling_72hr_snowfall, 0) AS rolling_72hr_snowfall,
    COALESCE(ft.freeze_thaw_flag, 0)     AS freeze_thaw_flag,
    COALESCE(ft.min_temp, c.temp_f)      AS day_min_temp,
    COALESCE(ft.max_temp, c.temp_f)      AS day_max_temp
FROM {{ source('main', 'conditions') }} c
LEFT JOIN {{ ref('rolling_snowfall') }} s
    ON c.resort = s.resort AND c.fetched_at = s.fetched_at
LEFT JOIN {{ ref('freeze_thaw') }} ft
    ON c.resort = ft.resort
    AND DATE_TRUNC('day', c.fetched_at) = ft.day