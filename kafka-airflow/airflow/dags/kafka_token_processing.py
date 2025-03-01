from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
import subprocess
import logging

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'start_date': days_ago(1),  # Starts 1 day ago for testing
}

# Define the DAG
dag = DAG(
    'kafka_token_processing',
    default_args=default_args,
    description='Process Kafka tokens: producer, consumer, and analytics',
    schedule_interval=timedelta(minutes=5),  # Producer runs every 5 minutes
    catchup=False,  # Don't backfill for past runs
)

# Producer function that simulates producing tokens
def producer_task():
    logging.info("Running producer task...")
    try:
        # Run the producer script here
        result = subprocess.run(["python3", "/Users/nampham/git_repos/self-develop/kafka-airflow/producers.py"], check=True, capture_output=True)
        logging.info(f"Producer task output: {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running producer script: {e}")
        raise

# Consumer function that simulates consuming tokens from Kafka
def consumer_task():
    logging.info("Running consumer task...")
    try:
        # Run the consumer script here
        result = subprocess.run(["python3", "/Users/nampham/git_repos/self-develop/kafka-airflow/consumers.py"], check=True, capture_output=True)
        logging.info(f"Consumer task output: {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running consumer script: {e}")
        raise

# Analytics function that processes the data
def analytics_task():
    logging.info("Running analytics task...")
    try:
        # Run the analytics script here
        result = subprocess.run(["python3", "/Users/nampham/git_repos/self-develop/kafka-airflow/token_analysis.py"], check=True, capture_output=True)
        logging.info(f"Analytics task output: {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running analytics script: {e}")
        raise

# Define the tasks in the DAG
producer = PythonOperator(
    task_id='produce_tokens',
    python_callable=producer_task,
    dag=dag,
)

consumer = PythonOperator(
    task_id='consume_tokens',
    python_callable=consumer_task,
    dag=dag,
    start_date=default_args['start_date'] + timedelta(minutes=2),  # Runs 2 minutes after producer
)

analytics = PythonOperator(
    task_id='analyze_tokens',
    python_callable=analytics_task,
    dag=dag,
    start_date=default_args['start_date'] + timedelta(minutes=4),  # Runs 2 minutes after consumer
)

# Set task dependencies
producer >> consumer >> analytics
