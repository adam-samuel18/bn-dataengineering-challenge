{{
    config(
        materialized = 'view',
        tags = ['daily','every_30_mins']
    )
}}

/* This model flattens the json file and stores the result as a view */

select
    timestamp::timestamp as timestamp,
    action,
    split_part(split_part(path, '.', 4), '/', 1) as event_name,
    replace(replace(lower(record->'$.text') , ',', '') , '.', '') as record_text,
    repo as user_id
from {{ source('bluesky', 'events') }}
