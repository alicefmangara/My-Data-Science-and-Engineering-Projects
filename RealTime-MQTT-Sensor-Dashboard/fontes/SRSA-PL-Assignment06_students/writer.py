#!/usr/bin/env python3

# Importing the required modules  
import influxdb_client, os, time	
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from random import random
from random import randint
from datetime import datetime

# Defining the InfluxDB host  
token = "[TOKEN HERE]" 			# CHANGE TO YOUR INFLUXDB CLOUD TOKEN
org = "[ORGANIZATION HERE]"		# CHANGE TO YOUR INFLUXDB CLOUD ORGANIZATION
url = "[URL HERE]"			# CHANGE CHANGE TO YOUR INFLUXDB CLOUD HOST URL
bucket = "[BUCKET HERE]"		# CHANGE TO YOUR INFLUXDB CLOUD BUCKET

# Instantiate the client. The InfluxDBClient object takes three named parameters: url, org, and token. 
write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org) 

# Synchronous writes block the application while data is sent to InfluxDB
write_api = write_client.write_api(write_options=SYNCHRONOUS)

# Write some data in the database... each second during 30m
# Simulate 2 devices: "device1" and "device2", both with a temperature and humidity sensor attached
# Our devices will be tags (+so that they are indexed), the values of sensor data will be fields

temp1=23.5	# float
hum1=50		# integer

temp2=10.0	# float
hum2=20		# integer


i = 1
while i < 1800:
  temp1+=random()-0.5	# adds -0.5 to 0.5 to current temperature
  hum1+=randint(-5,5)	# adds -5 to 5 to current humidity
  temp2+=random()-0.5	# adds -0.5 to 0.5 to current temperature
  hum2+=randint(-5,5)	# adds -5 to 5 to current humidity

  if hum1>100:
    hum1=99
  if hum1<0:
    hum1=1
  if hum2>100:
    hum2=99
  if hum2<0:
    hum2=1

  # Send data from both sensors of "Device1" and use the local time to insert in the database
  p = influxdb_client.Point("[MEASUREMENT NAME HERE]").tag("device", "device1").field("temperature", temp1).field("humidity", hum1).time(datetime.now()) 	# CHANGE TO YOUR MEASUREMENT NAME
  write_api.write(bucket=bucket, org=org, record=p)
  print(f"Value inserted: device1 temperature=",temp1,"; device1 humidity=",hum1)

  # Send data from sensors of "Device2", one at each time; no time is provided so InfluxDB will use the local database server time (it will probably be different!!!)
  p = influxdb_client.Point("[MEASUREMENT NAME HERE]").tag("device", "device 2").field("temperature", temp2)	# CHANGE TO YOUR MEASUREMENT NAME
  write_api.write(bucket=bucket, org=org, record=p)
  print(f"Value inserted: device2 temperature=",temp2)

  p = influxdb_client.Point("[MEASUREMENT NAME HERE]").tag("device", "device 2").field("humidity", hum2)	# CHANGE TO YOUR MEASUREMENT NAME
  write_api.write(bucket=bucket, org=org, record=p)
  print(f"Value inserted: device2 humidity=",hum2)

  time.sleep(1) # wait 1 second to generate other values
  i += 1

