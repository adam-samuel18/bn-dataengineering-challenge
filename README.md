# Senior Data Engineering - Take home task

### Pipeline Design

The pipeline was created using dbt and duckdb.

# Sources

The bluesky.events file is listed as a source. I have included source freshness
snapshot as in production this would be run reguarly so it is useful to know
how up to date the source data is.

# Staging

In the staging layer the json event data is flattened and data types are cast.

# Intermediate

Since this is a very simple pipeline I haven't included any intermediate models.
However in production I would normally use this layer for joins, unions, and
more complex calculations. I often utilise dbt macros (particularly dbt utils
surrogate key and dbt union relations) to keep my code concise.

# Marts

This layer contains the production ready data. I've added post hooks to the
models to write the data to csv files in the metrics/ folder

# Tests

I've added some unique and not null tests in the marts layer to ensure that the
primary keys don't contain duplicates. I often add tests and create slack alerts
for these so that any data issues are caught quickly.

# Tags

I've added tags to the models. While they don't do anything in this pipeline, I
usually use these tags to dictate when the pipelines run.

# Code Linting

While I haven't used it here I have added a .sqlfluff file as I usually use this
to lint my code.

# Additional Metric - Posts by time of day

I have included the metric "Posts by time of day" as it is useful for the business
to know which days of the week and what time of day people are most active on the
platform. Such information could be used to price ads for example (if bluesky has ads).
