"""
This code gets the SQL scripts from the sql_scripts file and uses duckdb to create tables
in the data warehouse and run write the output data to csv files in the /metrics folder.
"""
import duckdb
from sql_scripts import STAGING_BLUESKY_EVENTS, FAST_LIKERS, LIKES_PER_MINUTE, TOP_TEN_WORD

class BlueskyEvents(object):

    def __init__(self, metric, table_name, sql_script):
        self.conn = duckdb.connect('analytics_dev.duckdb')

        self.metric = metric
        self.table_name = table_name
        self.sql_script = sql_script

    def main(self):
        full_sql = ''.join([f'CREATE OR REPLACE TABLE { table_name } AS ', STAGING_BLUESKY_EVENTS, sql_script, ';'])
        self.conn.execute(full_sql)
        print(self.conn.execute(f'SELECT * FROM { table_name } LIMIT 5;').fetchdf())
        print (f'Executed SQL for { metric }')
        self.conn.execute(f"COPY { table_name } TO 'metrics/{ metric }.csv' (HEADER, DELIMITER ',');")
        print (f'Saved { metric } to csv')

# The format of the config file is (metric, table name, sql script name)
# The output csv file will have the same name as the metric

config = [
    ('fast-likers', 'FAST_LIKERS', FAST_LIKERS),
    ('likes-per-minute', 'LIKES_PER_MINUTE', LIKES_PER_MINUTE),
    ('top-ten-word', 'TOP_TEN_WORD', TOP_TEN_WORD)
]

if __name__ == "__main__":
    for metric, table_name, sql_script in config:
        BlueskyEvents(metric, table_name, sql_script).main()
