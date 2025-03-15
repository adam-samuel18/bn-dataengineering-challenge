"""
This DAG loads the Bluesky events data using the bluesky.events script and
then runs the dbt models to transform the data and run tests.
"""

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from datetime import timedelta, datetime

# "Global" variables
AIRFLOW_HOME = "/usr/local/airflow"
dag_name = "Bluesky-Events-Pipeline"
env = Variable.get("env")

activate_venv = "source /usr/local/airflow/venv/bin/activate && "
dbt_path = "cd pipeline/dbt &&"
load_bluesky_events_cmd = f"python3 {AIRFLOW_HOME}/bluesky.events -env " + env
transform_bluesky_events_cmd = f"dbt build --select tag:daily,tag:every_30_mins -t" + env

load_bluesky_events_bash = ''.join([activate_venv, load_bluesky_events_cmd])
transform_bluesky_events_bash = ''.join([activate_venv, dbt_path, transform_bluesky_events_cmd])

# Airflow ENV variables
dag_schedule = Variable.get("bluesky_pipeline_schedule", "*/30 * * * *")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 3, 15),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

dag = DAG(dag_name_var, default_args=default_args, schedule_interval=dag_schedule, catchup=False)

load_bluesky_events = BashOperator(task_id = f"{dag_name}-load",
                            bash_command = load_bluesky_events_bash,
                            dag=dag)

transform_bluesky_events = BashOperator(task_id = f"{dag_name}-transform",
                            bash_command = transform_bluesky_events_bash,
                            dag=dag)

load_bluesky_events >> transform_bluesky_events
