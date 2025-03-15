"""
This script is not part of the pipeline but is in this repo to show
further proficiency in python. This script uses polars to read the json
events and calculate the number of likes per minute. It then writes the
output to a csv file.
"""

import polars as pl

# The schema specifies the desired fields and datatypes from the bluesky.events file
# Then a dataframe df is created from the json file containing these desired fields

schema = {
    'timestamp': pl.Datetime,
    'path': pl.String
}

df = pl.read_ndjson('bluesky.events', schema = schema)

# The columns 'ts_min' and 'event_name' are added to the dataframe
# The dataframe is then filtered to only show like events

df = df.with_columns(
    pl.col('timestamp').dt.truncate('1m').alias('ts_min'),
    pl.col('path').str.split('/').list.get(0).
        str.split('.').list.get(3, null_on_oob = True).alias('event_name')
)

df = df.filter(pl.col('event_name') == 'like')

# Finally the likes per minute is calculated and the data is written to csv

df = df.group_by('ts_min').len().sort('ts_min')
df.write_csv('./metrics/likes_per_minute_python.csv')
