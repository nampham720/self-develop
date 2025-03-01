from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time
import subprocess
import logging

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'start_date': datetime.now(),  # Set start date
    'end_date': datetime.now() + timedelta(minutes=15),
    'schedule': timedelta(minutes=3)  # Runs every 3 minutes
}

# Define the DAG
dag = DAG(
    'kafka_token_processing',
    default_args=default_args,
    description='Process Kafka tokens: producer, consumer, and analytics',
    schedule=timedelta(minutes=3),  # Run every 3 minutes
    catchup=False,
)

# Producer function that simulates producing tokens
def producer_task():
    logging.info("Running producer task...")
    try:
        # Run the producer script here (you can call the Python file for the producer)
        result = subprocess.run(["python", "../producers.py"], check=True, capture_output=True)
        logging.info(f"Producer task output: {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running producer script: {e}")
        raise

# Consumer function that simulates consuming tokens from Kafka
def consumer_task():
    logging.info("Running consumer task...")
    try:
        # Run the consumer script here (you can call the Python file for the consumer)
        result = subprocess.run(["python", "../consumers.py"], check=True, capture_output=True)
        logging.info(f"Consumer task output: {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running consumer script: {e}")
        raise

# Analytics function that processes the data
def analytics_task():
    logging.info("Running analytics task...")
    try:
        # Run the analytics script here (you can call the Python file for analytics)
        result = subprocess.run(["python", "../token_analysis.py"], check=True, capture_output=True)
        logging.info(f"Analytics task output: {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running analytics script: {e}")
        raise

# Define the tasks in the DAG
producer = PythonOperator(
    task_id='produce_tokens',
    python_callable=producer_task,
    dag=dag,
    trigger_rule="all_success",  # Run producer task first
)

consumer = PythonOperator(
    task_id='consume_tokens',
    python_callable=consumer_task,
    dag=dag,
    trigger_rule="all_success",  # Consumer task should run after producer task
    start_date=datetime(2025, 2, 28, 0, 2),  # Runs 2 minutes after producer completes
)

analytics = PythonOperator(
    task_id='analyze_tokens',
    python_callable=analytics_task,
    dag=dag,
    trigger_rule="all_success",  # Analytics task runs after consumer
    start_date=datetime(2025, 2, 28, 0, 3),  # Runs 1 minute after consumer task
)

# Set task dependencies
producer >> consumer >> analytics
