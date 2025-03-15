{{
    config(
        materialized = 'table',
        tags = ['daily','every_30_mins'],
        post_hook = "COPY {{ this }} TO '../../metrics/posts-by-time-of-day.csv' (HEADER, DELIMITER ',');"
    )
}}

/* This model calculates the number of posts by
day of week and hour of day */

select
    dayofweek(timestamp) as day_of_week,
    hour(timestamp) as hour_of_day,
    count(*) as number_of_posts
from {{ ref('stg_bluesky__events') }}
where event_name = 'post'
group by 1,2
order by 3 desc
limit 100
