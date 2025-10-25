import configparser
import json
import socket
import time
from datetime import datetime, timedelta
from random import randint, random

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# MQTT broker 1 details
MQTT_SERVER_1 = '10.6.1.10'

# MQTT broker 2 details
MQTT_SERVER_2 = '10.6.1.4'

MQTT_PORT = 1883

UDP_SERVER = '127.0.0.1'
UDP_PORT = 5000

# Read the configuration file with healthy sensor intervals
config = configparser.ConfigParser()
config.read('healthy_intervals.cfg')

# Get the healthy ranges from the configuration file
temperature_range = (
    float(config.get('SensorIntervals', 'temperature_min')),
    float(config.get('SensorIntervals', 'temperature_max'))
)
pressure_range = (
    float(config.get('SensorIntervals', 'pressure_min')),
    float(config.get('SensorIntervals', 'pressure_max'))
)
luminosity_range = (
    float(config.get('SensorIntervals', 'luminosity_min')),
    float(config.get('SensorIntervals', 'luminosity_max'))
)

# Create an InfluxDB client
token = "n2r4P6ZnaCeSgM7slV2aAdC1s_jb4gWZ09OkNLxtcqDIojwwQHsMjXPL2vDmM_5yAL4mQP_lcBGuWvguE1tqcg=="
org = "SRSA"
url = "https://us-east-1-1.aws.cloud2.influxdata.com"
bucket = "PROJECTB" # CHANGE TO YOUR INFLUXDB CLOUD BUCKET

influxdb_client = InfluxDBClient(url=url, token=token, org=org)
# Instantiate the client. The InfluxDBClient object takes three named parameters: url, org, and token.
write_client = InfluxDBClient(url=url, token=token, org=org)

# Synchronous writes block the application while data is sent to InfluxDB
write_api = write_client.write_api(write_options=SYNCHRONOUS)

alarm_timestamps = {}  # Dictionary to store alarm timestamps
alarm_interval = timedelta(seconds=20)  # Interval for repeating alarms

def send_alarm(sensor, value):
    # Generate an alarm message and send it via UDP
    current_time = datetime.now()
    if sensor in alarm_timestamps:
        # Check if the alarm is repeated within the interval
        if current_time - alarm_timestamps[sensor] < alarm_interval:
            return  # Skip repeated alarm within the interval
    alarm_msg = f"{current_time.strftime('%d/%m/%Y %H:%M:%S')} {sensor} - Value: {value} (NEW ALARM)"
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(alarm_msg.encode(), (UDP_SERVER, UDP_PORT))
    udp_socket.close()
    alarm_timestamps[sensor] = current_time


def send_alarm_cancellation(sensor, value):
    # Generate an alarm cancellation message and send it via UDP
    current_time = datetime.now()
    if sensor in alarm_timestamps:
        # Check if the alarm is repeated within the interval
        if current_time - alarm_timestamps[sensor] < alarm_interval:
            return  # Skip repeated alarm cancellation within the interval
    alarm_cancel_msg = f"{current_time.strftime('%d/%m/%Y %H:%M:%S')} {sensor} - Value: {value} (ALARM CANCELLED)"
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(alarm_cancel_msg.encode(), (UDP_SERVER, UDP_PORT))
    udp_socket.close()
    alarm_timestamps[sensor] = current_time


def calculate_average_temperature(temperatures):
    # Calculate the average temperature from the received values
    average_temp = sum(temperatures) / len(temperatures)
    return average_temp

def convert_to_fahrenheit(celsius):
    # Convert temperature from Celsius to Fahrenheit
    return (celsius * 9/5) + 32

MQTT_PATH1 = [("18_temperature",0), ("18_luminosity",0),("18_pressure",0)] 

MQTT_PATH2 = [("sensor_data_hum_1", 0), ("sensor_data_hum_2", 0),("sensor_data_energy", 0)]

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f'Connected with Broker1: {str(rc)}')
        
    if client._host == MQTT_SERVER_1:
        for topic, _ in MQTT_PATH1:
            client.subscribe(topic)
            
def on_connect2(client, userdata, flags, rc):
    print(f'Connected with Broker2: {str(rc)}')
    if client._host == MQTT_SERVER_2:
        for topic, _ in MQTT_PATH2:
            client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload

    if topic == 'sensor_data_energy':
        data = json.loads(payload)
        peak = data['peak']
        off_peak = data['off_peak']
        print(f'Received Message: peak {str(peak)}')
        print(f'Received Message: off_peak {str(off_peak)}')

        point = Point('peak').field('value', peak).time(datetime.utcnow(), WritePrecision.NS)
        write_api.write(bucket, org, point)

        point = Point('off_peak').field('value', off_peak).time(datetime.utcnow(), WritePrecision.NS)
        write_api.write(bucket, org, point)

    else:
        payload = float(msg.payload.decode())

        print(f'Received Message: {topic} {str(payload)}')

        if topic == '18_temperature':
            # Calculate average temperature in Celsius/Fahrenheit
            temperatures = userdata.get('temperatures', [])
            temperatures.append(payload)
            average_temperature = calculate_average_temperature(temperatures)
            print(f'Average Temperature in Celsius:  {average_temperature} C')
            print(f'Average Temperature in Fahrenheit: {convert_to_fahrenheit(average_temperature)} F')
            userdata['temperatures'] = temperatures

        # Check if the sensor value is outside the healthy range
        if topic == '18_temperature' and (payload < temperature_range[0] or payload > temperature_range[1]):
            send_alarm(topic, payload)
        elif topic == '18_pressure' and (payload < pressure_range[0] or payload > pressure_range[1]):
            send_alarm(topic, payload)
        elif topic == '18_luminosity' and (payload < luminosity_range[0] or payload > luminosity_range[1]):
            send_alarm(topic, payload)
        else:
            send_alarm_cancellation(topic, payload)

        # Save data to Influx DB
        point = Point(topic).field('value', payload).time(datetime.utcnow(), WritePrecision.NS)
        write_api.write(bucket, org, point)


# Create the MQTT client instances
client = mqtt.Client(userdata={'temperatures': []})
client2 = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client2.on_connect = on_connect2
client2.on_message = on_message

# Connect to the MQTT brokers
client.connect(MQTT_SERVER_1, MQTT_PORT, 60)
client2.connect(MQTT_SERVER_2, MQTT_PORT, 60)

# Start the MQTT loops to listen for incoming messages
client.loop_start()
client2.loop_start()

# Keep the script running to receive messages
while True:
    time.sleep(1)  # Add a small delay to avoid high CPU usage