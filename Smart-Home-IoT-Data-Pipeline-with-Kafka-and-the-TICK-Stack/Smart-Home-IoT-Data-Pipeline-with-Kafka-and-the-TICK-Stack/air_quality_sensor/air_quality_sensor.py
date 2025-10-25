#!/bin/env python3
import os
import random
import time

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError


def get_air_quality_parameters():
    mean = float(os.getenv('AIR_QUALITY_MEAN', 100))
    stddev = float(os.getenv('AIR_QUALITY_STDDEV', 25))
    return mean, stddev

def generate_air_quality_data(mean, stddev):
    while True:
        time.sleep(30)
        air_quality = random.normalvariate(mean, stddev)
        air_quality = max(min(air_quality, 200), 0)
        message = f"air_quality value={air_quality}"
        data = f"air_quality,host=my_host aqy={air_quality}"
        producer.send('sh-air_quality', data.encode())
        print(f"Sending data: {data}")
        producer.flush()
        
if __name__ == "__main__":
    print('Connecting to Kafka...')
    producer = KafkaProducer(bootstrap_servers='kafka:9092')
    print('Connected to Kafka!')

    print("Starting air_quality sensor...")
    mean, stddev = get_air_quality_parameters()
    generate_air_quality_data(mean, stddev)