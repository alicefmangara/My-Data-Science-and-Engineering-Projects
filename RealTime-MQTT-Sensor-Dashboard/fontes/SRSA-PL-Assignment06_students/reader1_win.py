#!/usr/bin/env python3

# Reader
# Uses Flux queries to Query data from InfluxDB
# To better understand this example refer to:
# https://docs.influxdata.com/influxdb/cloud/api-guide/client-libraries/python/

# Importing modules
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from random import random
from random import randint
from datetime import datetime

def query_data(query_requested):
  # The query client sends the Flux query to InfluxDB and returns a Flux object with a table structure.
  result = query_api.query(org=org, query=query_requested)

  results = []		#results list
  for table in result:
    for record in table.records:
      results.append((record.get_value(), record.get_field()))
  print(results)


# Defining the InfluxDB host  
token = "[TOKEN HERE]" 			# CHANGE TO YOUR INFLUXDB CLOUD TOKEN
org = "[ORGANIZATION HERE]"		# CHANGE TO YOUR INFLUXDB CLOUD ORGANIZATION
url = "[URL HERE]"			# CHANGE CHANGE TO YOUR INFLUXDB CLOUD HOST URL
bucket = "[BUCKET HERE]"		# CHANGE TO YOUR INFLUXDB CLOUD BUCKET

# Instantiate the client. The InfluxDBClient object takes three named parameters: url, org, and token. 
read_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org) 

# Instantiate the query client
query_api = read_client.query_api()

# Create Flux queries

query3 = 'from(bucket: "[BUCKET HERE]")\
  |> range(start: -30s)\
  |> filter(fn: (r) => (r._measurement == "[MEASUREMENT NAME HERE]") and (r._field == "temperature"))\
  |> drop(columns: ["device"])\
  |> mean()'
# drop is used to calculate max() for all devices

print("Average:")
query_data(query3)

query4 = 'from(bucket: "[BUCKET HERE]")\
  |> range(start: -30s)\
  |> filter(fn: (r) => (r._measurement == "[MEASUREMENT NAME HERE]") and (r._field == "temperature"))\
  |> drop(columns: ["device"])\
  |> max()'

print("Max:")
query_data(query4)

query5 = 'from(bucket: "[BUCKET HERE]")\
  |> range(start: -30s)\
  |> filter(fn: (r) => (r._measurement == "[MEASUREMENT NAME HERE]") and (r._field == "temperature"))\
  |> drop(columns: ["device"])\
  |> min()'

print("Min:")
query_data(query5)





