STAGING_BLUESKY_EVENTS = """

with stg_bluesky__events as (
    select
        timestamp::timestamp as timestamp,
        action,
        split_part(split_part(path, '.', 4), '/', 1) as event_name,
        replace(replace(lower(record->'$.text') , ',', '') , '.', '') as record_text,
        repo as user_id
    from read_json('bluesky.events')
)

"""

FAST_LIKERS = """

, timestamp_diffs as (
    select
        user_id,
        timestamp as ts_like_1,
        lead(timestamp, 49) over(partition by user_id order by timestamp) as ts_like_50,
        datediff('second', ts_like_1, ts_like_50) as ts_diff
    from stg_bluesky__events
    where event_name = 'like'
)

select distinct
    user_id
from timestamp_diffs
where ts_diff < 60

"""

LIKES_PER_MINUTE = """

select
    date_trunc('minute', timestamp) as ts_minute,
    count(*) as likes
from stg_bluesky__events
where event_name = 'like'
group by 1
order by 1

"""

TOP_TEN_WORD = """

, words as (
    select
        regexp_split_to_table(record_text, ' ') as word,
    from stg_bluesky__events
    where record_text like '%engineering%'
)

select
    word,
    count(*) as word_count
from words
where word not in (
    'engineering',
    'the',
    'and',
    'to',
    'of',
    'in',
    'a',
    'for',
    'is',
    'that',
    'you',
    'at',
    '&',
    'has',
    'its',
    'on',
    'it',
    'every',
    'their',
    'into',
    'this',
    'our'
    )
group by 1
order by 2 desc
limit 10

"""