{{
    config(
        materialized = 'table',
        tags = ['daily','every_30_mins'],
        post_hook = "COPY {{ this }} TO '../../metrics/top-ten-word.csv' (HEADER, DELIMITER ',');"
    )
}}

/* This model calculates the list of the top 10 meaningful words
used in posts that contain the word "engineering". */

/* First the string is split into rows with one word per row */

with words as (
    select
        regexp_split_to_table(record_text, ' ') as word,
    from {{ ref('stg_bluesky__events') }}
    where record_text like '%engineering%'
)

/* Then words that aren't useful are filtered out and a word count
is calculated */

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
