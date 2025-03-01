# Manually running the task for debugging purposes
from airflow.utils.dates import days_ago
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging
from datetime import timedelta
import subprocess

# Define the function to be executed
def testing():
    result = subprocess.run(["pwd"], check=True, capture_output=True)
    logging.info(f"Iteration: {result.stdout.decode()}")

# Define the DAG
dag = DAG(
    'testing_dag',
    default_args={
        'owner': 'airflow',
        'retries': 5,
        'start_date': days_ago(1),
    },
    description='Simple testing DAG',
    schedule_interval=timedelta(minutes=1),
)

# Defining the PythonOperator
print_pwd_task = PythonOperator(
    task_id='print_pwd_5_times',
    python_callable=testing,
    dag=dag,
)

# Run the task directly
print_pwd_task
