#!/usr/bin/env python3

# Importing the required modules  
import influxdb_client, os, time									# Are all needed?!
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from random import random
from random import randint
from datetime import datetime

# Defining the InfluxDB host  
token = "ShrrsYwE2-3SqSKhY7rxB31jBRcjmkqfRJpA6oO_rWksM4PJuWd-f8y6vN3JT7QPlkykS22Vn5Kr_jK1IJ1M8g==" 	# CHANGE
org = "Proj1"												# CHANGE
url = "https://eu-central-1-1.aws.cloud2.influxdata.com"						# CHANGE
bucket = "SRSA"												# CHANGE

# Instantiate the client. The InfluxDBClient object takes three named parameters: url, org, and token. 
write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org) 

# Synchronous writes block the application while data is sent to InfluxDB
write_api = write_client.write_api(write_options=SYNCHRONOUS)

# Write some data in the database... each second during 30m
# Simulate 2 devices: "device1" and "device2", both with a temperature and humidity sensor attached
# Our devices will be tags (+so that they are indexed), the values of sensor data will be fields

temp1=20.0	# float

while 1:
  temp1+=random()-0.5	# adds -0.5 to 0.5 to current temperature

  if temp1>45:
    temp1 = 45
  if temp1<-10:
    temp1 =-10

  # Send temperature data and use the local time to insert in the database
  p = influxdb_client.Point("Dummy_temp_sensor").field("temperature", temp1).time(datetime.utcnow()) 
  print(f"Value inserted at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ": temperature=",temp1)
  write_api.write(bucket=bucket, org=org, record=p)
  
  time.sleep(2) # wait 2 seconds to generate other values


