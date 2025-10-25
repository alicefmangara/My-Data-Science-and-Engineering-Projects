#!/bin/env python3
import os
import random
import time

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError


def get_temp_parameters():
    mean = float(os.getenv('TEMP_MEAN', 20))
    stddev = float(os.getenv('TEMP_STDDEV', 5))
    return mean, stddev


def generate_temperature_data(mean, stddev):
    while True:
        # Send data every 30 seconds
        time.sleep(30)
        temperature = random.normalvariate(mean, stddev)
        temperature = max(min(temperature, 45), -5)
        message = f"temperature value={temperature}"
        data = f"temperature,host=my_host temperature1={temperature}"
        producer.send('sh-temperature', data.encode())
        print(f"Sending data: {data}")
        producer.flush()

if __name__ == "__main__":
    print('Connecting to Kafka...')
    producer = KafkaProducer(bootstrap_servers='kafka:9092')
    print('Connected to Kafka!')

    print("Starting temperature sensor...")
    # Get the temperature parameters from environmental variables
    mean, stddev = get_temp_parameters()
    # Start generating and sending temperature data
    generate_temperature_data(mean, stddev)
