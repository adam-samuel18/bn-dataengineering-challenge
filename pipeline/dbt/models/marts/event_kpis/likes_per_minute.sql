{{
    config(
        materialized = 'table',
        tags = ['daily','early_morning'],
        post_hook = "COPY {{ this }} TO '../../metrics/likes-per-minute.csv' (HEADER, DELIMITER ',');"
    )
}}

/* This model calculates the number of likes over time (minute by minute) */

select
    date_trunc('minute', timestamp) as ts_minute,
    count(*) as likes
from {{ ref('stg_bluesky__events') }}
where event_name = 'like'
group by 1
order by 1
