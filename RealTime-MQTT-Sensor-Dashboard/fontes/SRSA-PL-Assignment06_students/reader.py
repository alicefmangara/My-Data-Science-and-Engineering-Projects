#!/usr/bin/env python3

# Importing the required modules
from flightsql import FlightSQLClient
import time


# Define the query client
query_client = FlightSQLClient(
  host = "[HOST HERE]",					# CHANGE TO YOUR INFLUXDB CLOUD HOST
  token = "[TOKEN HERE]",				# CHANGE TO YOUR INFLUXDB CLOUD TOKEN
  metadata={"bucket-name": "[BUCKET HERE]"})		# CHANGE TO YOUR INFLUXDB CLOUD BUCKET

while 1:
  # Define the queries
  query1 = """SELECT COUNT(*) total FROM '[MEASUREMENT NAME HERE]' WHERE time >= now() - INTERVAL '1 HOUR'"""	# CHANGE TO YOUR MEASUREMENT NAME
  query2 = """SELECT * FROM '[MEASUREMENT NAME HERE]' LIMIT 3"""
  query3 = """SELECT AVG(temperature) avg_temp, MAX(temperature) max_temp,MIN(temperature) min_temp FROM '[MEASUREMENT NAME HERE]' WHERE time >= now() - INTERVAL '30 SECONDS'"""

  print(f"")
  print(f"")

  # Execute the query1
  info = query_client.execute(query1)
  reader = query_client.do_get(info.endpoints[0].ticket)
  data = reader.read_all()
  df = data.to_pandas()
  print(">> The total number of tuples inserted in the last hour was: ",df['total'][0])
 
  # Execute the query2
  info = query_client.execute(query2)
  reader = query_client.do_get(info.endpoints[0].ticket)
  data = reader.read_all()
  df = data.to_pandas().sort_values(by="time")
  print(f">> Table with the last 3 inserted rows:")
  print(df)
  #print(df['humidity'].tolist())

  # Execute the query3
  info = query_client.execute(query3)
  reader = query_client.do_get(info.endpoints[0].ticket)
  data = reader.read_all()
  df = data.to_pandas()
  print(f">> AVG, MAX and MIN temperature in last 30 seconds:")
  print("AVG TEMP= ",df['avg_temp'][0]," MAX TEMP=",df['max_temp'][0]," MIN TEMP=",df['min_temp'][0])

  time.sleep(5) # wait 5 seconds to generate other values