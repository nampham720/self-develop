import time
from confluent_kafka import Producer
from datetime import datetime
import random
import json  # To serialize the message as JSON
import logging

# Set up logging to capture messages to a file
logging.basicConfig(filename='producer_log.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Text source: https://www.bbc.com/news/articles/cm2j1r1qn3zo
# The text to send to Kafka
text1 = """When Japanese journalist Shiori Ito decided to speak up about her rape allegations, she knew she was standing in the face of a society that preferred silence.
"I'm scared…but all I want to do is to talk about the truth", Shiori says in the opening scene of her Oscar-nominated documentary Black Box Diaries.
Shiori became the face of Japan's MeToo movement after she accused a prominent journalist Noriyuki Yamaguchi of rape."""
text2= """Her acclaimed directorial debut, based on her memoir of the same name, is a retelling of her quest for justice after authorities found the evidence insufficient to pursue criminal charges.
But there is one country where it is yet to play: Japan, where it has run into huge controversy. Her former lawyers have accused her of including audio and video footage she did not have permission to use, which, they say, has violated trust and put her sources at risk. Shiori defends what she did as necessary for "public good"."""
text3 = """It's a startling turn in a story that gripped Japan when it first broke -the then 28-year-old Shiori ignored her family's request to remain silent. And after her public accusation did not result in a criminal case, she filed a civil lawsuit against Yamaguchi and won $30,000 (£22,917) in damages.
Shiori told the BBC making the film involved "reliving her trauma": "It took me four years [to make the film] because emotionally I was struggling."
She was an intern at Reuters news agency in 2015, when she says Yamaguchi invited her to discuss a job opportunity. He was the Washington bureau chief for a major Japanese media firm, Tokyo Broadcasting System."""

# Select random text
text = random.choice([text1, text2, text3])

# Log which text was selected
logging.info(f"Selected text: {text[:10]}...")  # Log the first 50 characters of the selected text for clarity


# Split the text into tokens (words in this case)
tokens = text.split()

# Configure the Kafka producer
conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka server
    'client.id': 'token-producer'
}

# Create a producer instance
producer = Producer(conf)

# Callback function to handle message delivery reports
def delivery_report(err, msg):
    if err is not None:
        logging.info(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Produce tokens to Kafka at a rate of 2 tokens per second
topic = 'my-logs'  # Kafka topic to which messages will be sent
for token in tokens:
    
    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create the message with token and timestamp as a dictionary
    token_to_send = {
        'token': token,
        'timesent': timestamp
    }

    # Serialize the dictionary into a JSON string before sending
    message = json.dumps(token_to_send)

    # Send the message (JSON-encoded string) to Kafka
    producer.produce(topic, message, callback=delivery_report)
    
    # Wait for 0.2 seconds to send a token
    time.sleep(0.1)  # sleep for 0.2 seconds

# Flush the message
producer.flush()

# Log the completion of the message sending process
logging.info("Token production finished successfully.")

