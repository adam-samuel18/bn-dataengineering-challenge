{{
    config(
        materialized = 'table',
        tags = ['daily','early_morning'],
        post_hook = "COPY {{ this }} TO '../../metrics/fast-likers.csv' (HEADER, DELIMITER ',');"
    )
}}

/* This model calculates the list of all users who liked at
least 50 posts in less than a minute. */

/* This cte takes the timestamp of a 'like' event (see where clause)
and then uses the lead function to get the timestamp of the like event
that is 49 ahead of that one chronologically for that particular user.
It then calculates the difference between the two timestamps */

with timestamp_diffs as (
    select
        user_id,
        timestamp as ts_like_1,
        lead(timestamp, 49) over(partition by user_id order by timestamp) as ts_like_50,
        datediff('second', ts_like_1, ts_like_50) as ts_diff
    from {{ ref('stg_bluesky__events') }}
    where event_name = 'like'
)

/* Finally we get all the user ids where the timestamp difference is less than 60s */

select distinct
    user_id
from timestamp_diffs
where ts_diff < 60
