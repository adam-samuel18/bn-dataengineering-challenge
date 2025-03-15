# Senior Data Engineering - Take home task

## Instructions for running the pipeline

1. First create a virtual environment and then activate it by running:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Upgrade pip and install the requirements by running:
```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

3. Load the bluesky events in json format by running:
```bash
python3 bluesky.events
```

4. Run the transformation scripts to transform the data and output the metrics as csv files in
the /metrics folder. There are three options for this.

Option 1: Running the dbt pipeline
```bash
cd pipeline/dbt
dbt deps
dbt build
```

Option 2: Running the python script
```bash
python3 pipeline/python/bluesky_events.py
```

Option 3: Running the airflow dag which can be found in the /airflow-dags folder
This option hasn't been fully implemented as it would require setting up airflow
however it is a good option to have in a production environment since the DAG ensures
that the pipeline runs in the correct order. This dag runs the bluesky.events script
and then the dbt models and tests every 30 minutes.

## Explanation of Approach (Choices and Limitations)

### Orchestration

My favoured approach (in a production environment with many different pipelines) would be
to use an orchestrator (e.g. Airflow) to run the DAG. The DAG would consist of the python
script bluesky.events to load the data and a dbt project to transform the data. An example
of the airflow script can be found in /airflow-dags/bluesky_events.py

The main advantge of using an orchestrator such as Airflow to schedule the DAG is to ensure
that the scripts are always run in the correct order so resources wouldn't be wasted running
the transformation scripts if the load script fails. Moreover it has many integrations allowing
for the possibility of setting up slack alerts for monitoring.

The main limitation of using an orchestrator is that it needs to be maintained so using Airflow
to just manage one pipeline would be overkill. Such maintenance would include making sure that 
Airflow is kept up to date when new updates are released. Using a managed service (e.g. Astronomer
or MWAA) would be easier to maintain but would add additional cost to the business.

### Transformation

For a simple pipeline such as this one transforming the data in python (e.g. polars, pandas, or duckdb)
would suffice. However there are many advantages to using dbt in production as the number of models grows:

1. The ability to reference upstream models ensures that the models run in the correct order with no
circular referencing
2. The ease of adding tests at each stage of the pipeline helps to ensure data integrity. I have
included some examples in this pipeline
3. dbt docs allows one to easily see the data lineage for easy debugging
4. The ease of creating incremental models allows new data to be added to large tables without
creating the whole table from scratch
5. Macros can be created to keep code concise

As an analytics engineer one of the most important things is to ensure data integrity. Having tests
and alerts at multiple stages of the pipeline is pivotal to creating an environment where users 
have trust in the data.

The main limitations of using dbt are:

1. The number of models can quickly grow and become messy if high standards are not upheld, particularly if there
are inexperienced engineers as part of the team.
2. If using dbt Cloud this will add an additional cost to the business
3. dbt is more suited to batch processing of data so may not be suitable where live data needs to be 
streamed

## dbt Project Design

The pipeline was created using dbt and duckdb. The project utilises dbt best practices.
The structure mimics [dbt's guidelines](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)

### Sources

The bluesky.events file is listed as a source. I have included a source freshness
snapshot. In production this would be run reguarly so it is useful to know
how up to date the source data is.

### Staging

In the staging layer the json event data is flattened and data types are cast.

### Intermediate

Since this is a very simple pipeline I haven't included any intermediate models.
However in production I would normally use this layer for joins, unions, and
more complex calculations. I often utilise dbt macros (particularly dbt utils
surrogate key and dbt union relations) to keep my code concise.

### Marts

This layer contains the production ready data. I've added post hooks to the
models to write the data to csv files in the metrics/ folder

### Tests

I've added some unique and not null tests in the marts layer to ensure that the
primary keys don't contain duplicates. I often add tests and create slack alerts
for these so that any data issues are caught quickly.

### Tags

I've added tags to the models. While they don't do anything in this pipeline, I
usually use these tags to dictate when the pipelines run.

## Code Linting

The code linting packages that I would normally use in production are:
- sqlfluff - for dbt models
- black & flake8 - for python scripts

## Additional Metric - Posts by time of day

I have included the metric "Posts by time of day" as it is useful for the business
to know which days of the week and what time of day people are most active on the
platform. Such information could be used to price ads for example (if bluesky has ads).

In a production environment it is likely that we would be able to ingest a 'users' table
into the data warehouse which would likely include the date that the user joined the
platform. Were this information available to me I would use it to look at user retention
(particularly in the first 7 days of joining the platform). My experience has shown me
that the amount of activity the user exhibits in the first 7 days has a profound impact
on how likely they are to use the platform long term.

## Tasks not completed

I have not created the 'handle-streams' or 'periodic' executable files. The reason for this
is because the stacks that I have always worked with in the past have used an orchestrator
like Airflow to schedule the DAGs (I have some familiarity with Dagster also). I am therefore not
familiar with writing executable files to accept events via stdin. As an alternative I have included
a python script in the /airflow-dags folder to demonstrate my competency with Airflow and scheduling
DAGs.

N.B. I am starting with a mentor this week and I would be happy to ask him to teach me
how to write such executable files if is something that would be useful for the job.
