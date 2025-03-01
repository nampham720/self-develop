import sqlite3
import json  # To deserialize the JSON message
from confluent_kafka import Consumer, KafkaException, KafkaError
import logging
import time  # To measure the elapsed time

# Set up logging to capture messages to a file
logging.basicConfig(filename='consumer_log.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# SQLite database (it will create a file named 'kafka_data.db')
conn = sqlite3.connect('kafka_data.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS token_data (
    token TEXT,
    timestamp TEXT
)
''')

# Configure Kafka Consumer
conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker
    'group.id': 'my-consumer-group',        # Consumer group
    'auto.offset.reset': 'earliest',        # Start reading from the earliest message
}

# Create Kafka Consumer
consumer = Consumer(conf)

# Subscribe to Kafka topic
consumer.subscribe(['my-logs'])

# Initialize the time tracking variable
last_message_time = time.time()

# Consumer loop to read messages from Kafka
try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            print("Waiting for message...")

            # Check if the consumer has been waiting for more than 10 seconds
            if time.time() - last_message_time > 10:
                logging.info("No message received for 10 seconds, ending the loop.")
                break
        elif msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logging.info(f"End of partition reached: {msg.partition()}, offset: {msg.offset()}")
            else:
                raise KafkaException(msg.error())
        else:
            # Decode the message from JSON string to Python dictionary
            message = msg.value().decode('utf-8')  # Decode the byte message to string
            decoded_message = json.loads(message)  # Deserialize the JSON string to dictionary

            token = decoded_message['token']  # Extract the token from the dictionary
            timestamp = decoded_message['timesent']  # Extract the timestamp

            # Insert token into SQLite database
            cursor.execute("""
                INSERT INTO token_data (token, timestamp)
                VALUES (?, ?)
            """, (token, timestamp))

            # Commit transaction to save data
            conn.commit()

            logging.info(f"Inserted token: {token} at {timestamp}")

            # Update the last message time after processing a message
            last_message_time = time.time()

except KeyboardInterrupt:
    logging.info("Consumer interrupted")

finally:
    # Close the consumer and database connection
    consumer.close()
    cursor.close()
    conn.close()
    logging.info("Consumer and database connection closed.")
