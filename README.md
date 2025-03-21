# Bluesky Events Pipeline

## Table of Contents
1. [Instructions for running the pipeline](#instructions-for-running-the-pipeline)
2. [Explanation of Approach (Choices and Limitations)](#explanation-of-approach-choices-and-limitations)
3. [Productionising the Code](#productionising-the-code)
4. [Additional Metric](#additional-metric---daily-active-users)
5. [Tasks not Completed](#tasks-not-completed)

## Instructions for running the pipeline

1. First create a virtual environment and then activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Upgrade pip and install the requirements:
```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

3. Load the bluesky events in json format:
```bash
python3 bluesky.events
```

4. Run the transformation scripts to transform the data and output the metrics
as csv files in the /metrics folder. There are four options for this:

* Option 1: Run the dbt pipeline
```bash
cd pipeline/dbt
dbt deps
dbt build
```

* Option 2: Run the python script bluesky_events.py
(this script is written in python but the transformations are in SQL)
```bash
python3 pipeline/python/bluesky_events.py
```

* Option 3: Run the python script likes_per_minute.py
(this is done completely in python using no SQL)
```bash
python3 pipeline/python/likes_per_minute.py
```

For the purpose of this task, only the metric 'likes per minute' has been transformed
in this way. However this could be replicated for the other metrics.
This file was solely created to show proficiency transforming data in python. For
something more scalable a class would be created, such as in the
python/bluesky_events.py script.

* Option 4: Running the airflow dag
This can be found in the /airflow-dags folder.
This option hasn't been fully implemented as it would require setting up airflow
however it is a good option to have in a production environment since the DAG
ensures that the pipeline runs in the correct order. This dag is designed to run the
bluesky.events script and then the dbt models and tests every 30 minutes.

## Explanation of Approach (Choices and Limitations)

### Orchestration

My favoured approach (in a production environment with many different pipelines)
would be to use an orchestrator (e.g. Airflow) to run the DAG. The DAG would
consist of the python script bluesky.events to load the data and a dbt project
to transform the data. An example of the airflow script can be found in
/airflow-dags/bluesky_events.py

The main advantge of using an orchestrator such as Airflow to schedule the DAG
is to ensure that the scripts are always run in the correct order so the
transformation scripts wouldn't be run on data that is out of date. Moreover
it has many integrations allowing for the possibility of setting up slack alerts
for monitoring.

The main limitation of using an orchestrator is that it needs to be maintained
so using Airflow to just manage one pipeline would be overkill. Such maintenance
would include making sure that Airflow is kept up to date when new updates are
released. Using a managed service (e.g. Astronomer or MWAA) would be easier to
maintain but would add additional cost to the business.

### Transformation

For a simple pipeline such as this one transforming the data in python
(e.g. polars, pandas, or duckdb) would suffice. An example of this can be seen
in the python/likes_per_minute.py file. However there are many advantages to
using dbt in production as the number of models grows:

1. The ability to reference upstream models ensures that the models run in the
correct order with no circular referencing
2. The ease of adding tests at each stage of the pipeline helps to ensure data
integrity. I have included some examples in this pipeline
3. dbt docs allows one to easily see the data lineage for easy debugging
4. The ease of creating incremental models allows new data to be added to large
tables without creating the whole table from scratch
5. Macros can be created to keep code concise

As an analytics engineer one of the most important things is to ensure data
integrity. Having tests and alerts at multiple stages of the pipeline is pivotal
to creating an environment where users have trust in the data.

The main limitations of using dbt are:

1. The number of models can quickly grow and become messy if high standards are
not upheld, particularly if there are inexperienced engineers as part of the team.
2. If using dbt Cloud this will add an additional cost to the business
3. dbt is more suited to batch processing of data so may not be suitable where
live data needs to be streamed

### dbt Project Design

The pipeline was created using dbt and duckdb. The project utilises dbt best
practices. The structure mimics [dbt's guidelines](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview).
The staging model is materialised as a view so that it is quick to build.
Meanwhile the models in the mart layer are materialised as tables since we
expect them to be regularly queried.

#### Sources

The bluesky.events file is listed as a source. I have included a source freshness
snapshot. In production this would be run reguarly so it is useful to know how up
to date the source data is.

#### Staging

In the staging layer the json event data is flattened and data types are cast.

#### Intermediate

Since this is a very simple pipeline I haven't included any intermediate models.
However in production I would normally use this layer for joins, unions, and
more complex calculations. I often utilise dbt macros (particularly dbt utils
surrogate key and dbt union relations) to keep my code concise.

#### Marts

This layer contains the production ready data. I've added post hooks to the
models to write the data to csv files in the metrics/ folder

#### Tests

There are some unique and not null tests in the marts layer to ensure that the
primary keys don't contain duplicates. I often add tests and create slack alerts
for these so that any data issues are caught quickly.

#### Tags

Tags were added to the models. While they don't do anything in this pipeline, which
can be used to dictate when the pipelines run.

## Productionising the Code

The following changes would be made to run the code in production.

### CI/CD

The following could be created using Github workflows:
* pre-hooks to lint the code - black and flake8 for python, sqlfluff for dbt models,
  yaml-lint for yml files
* post-hooks to generate and upload the dbt docs to an s3 bucket

Linting the code would ensure that high coding standards are upheld.
Generating dbt docs would enable one to easily see data lineage while also enabling the
possibility of running models using `--defer` flag, saving compute resources since
the upstream tables wouldn't require rebuilding in dev.

### Secrets Management

While this particular pipeline doesn't require any secrets, in a real production pipeline
secrets would have to be managed securely, for example by storing them in AWS secrets
manager.

### dbt Targets

There would be separate targets for dev and prod. For dev each user would have their
own schema in the data warehouse where their dev runs are stored.

### Pull Request Template

A pull request template would be created to ensure that high standards are upheld.
For example the user who committed the pull request will need to demonstrate that all
dbt models and tests have passed and show sufficient verification to ensure that the
data is accurate (e.g. comparing the output to the source data). Ensuring data integrity
is of utmost importance for a company that wants to become more data driven.

### Orchestration

An orchestrator such as Airflow or Dagster would be used in production to ensure that
models are run in the correct order and to enable easy viewing of the data lineage.

### Monitoring

Results of the dbt runs and tests would be sent to a slack channel so that the data team
is alerted if there are any failures.

### Storage

The raw bluesky.events files would be sent to a storage bucket (e.g. S3 or GCP bucket).
The tables and views would be stored in a data warehouse, e.g. Snowflake or Bigquery.

### Containerisation

In production the code would be run inside a container on AWS or GCP rather than locally
on a laptop to ensure reliability and robustness in the pipeline.

In development, while running the code in a virtual environment is often sufficient it
would be better to run the code inside a dev container to ensure an exact replica of 
the conditions inside the production container.

## Additional Metric - Daily Active Users

I have included the metric Daily Active Users (DAUs). DAUs measures the number of
unique people who use the app each day. It is a key metric for social media
applications like bluesky. Monitoring it can help determine whether the business
is growing or shrinking. Understanding the DAU can also help to determine retention
rates from which the lifetime value (LTV) can be calculated. The main limitation of
DAU is that, while it is often used to indicate a applications's stickiness (i.e. how
likely a user is to return to the app), sometimes the DAU can increase for other
reasons, e.g. an increase in marketing spending could cause people to log into the
app and then never return.

In a production environment it is likely that we would be able to ingest a
'users' table into the data warehouse which would include the date that
the user joined the platform. Were this information available to me I would use
it to look at retention rates (particularly in the first 7 days of joining the
platform). My experience has shown that the amount of activity the user
exhibits in the first 7 days has a profound impact on how likely they are to use
the platform long term.

## Tasks not completed

I have not created the 'handle-streams' or 'periodic' executable files. The
reason for this is because the stacks that I have always worked with in the past
have used an orchestrator like Airflow to schedule the DAGs (I have some
familiarity with Dagster also). I am therefore not familiar with writing
executable files to accept events via stdin. As an alternative I have included
a python script in the /airflow-dags folder to demonstrate my competency with
Airflow and scheduling DAGs. I am also aware that both Airflow and Dagster have
sensors that can detect new files being added to an S3 bucket. This is an option
that could be used in production to detect new events.

N.B. I am starting with a mentor this week and I would be happy to ask him to
teach me how to write such executable files if is something that would be useful
for the job.
