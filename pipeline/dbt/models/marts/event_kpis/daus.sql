{{
    config(
        materialized = 'table',
        tags = ['daily'],
        post_hook = "COPY {{ this }} TO '../../metrics/daus.csv' (HEADER, DELIMITER ',');"
    )
}}

/* This model calculates the number of daily active users DAUs on the bluesky
platform */

select
    timestamp::date as ts_date,
    count(distinct user_id) as daus
from {{ ref('stg_bluesky__events') }}
where event_name in ('follow', 'like', 'post', 'repost')
group by 1
order by 1
