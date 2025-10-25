#!/bin/env python3
import os
import random
import time

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError


def get_humidity_parameters():
    mean = float(os.getenv('HUMIDITY_MEAN', 50))
    stddev = float(os.getenv('HUMIDITY_STDDEV', 10))
    return mean, stddev

def generate_humidity_data(mean, stddev):
    while True:
        time.sleep(30)
        humidity = random.normalvariate(mean, stddev)
        humidity = max(min(humidity, 100), 0)
        message = f"humidity value={humidity}"
        data = f"humidity,host=my_host Hum={humidity}"
        producer.send('sh-humidity', data.encode())
        print(f"Sending data: {data}")
        producer.flush()
        

if __name__ == "__main__":
    print('Connecting to Kafka...')
    producer = KafkaProducer(bootstrap_servers='kafka:9092')
    print('Connected to Kafka!')

    print("Starting humidity sensor...")
    mean, stddev = get_humidity_parameters()
    generate_humidity_data(mean, stddev)
