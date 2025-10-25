# **Smart Home IoT Data Pipeline with Kafka and the TICK Stack**

This repository contains the complete solution for establishing a reliable, containerized data pipeline to simulate and monitor a **Smart Home** environment. The project leverages messaging queues and a time-series database for real-time data handling, storage, alerting, and visualization.

### **Project Overview**

The goal was to simulate key components of a Smart Home system to test infrastructure concepts learned in the SIC course. The solution implements a scalable architecture capable of handling multiple sensor data streams, processing them in real-time using Kafka, and providing monitoring and alerting services using the TICK stack.

### **Core Architecture & Technologies**

The entire system is orchestrated using **Docker Compose** for easy, single-command deployment.

| Component | Role | Technology |
| :---- | :---- | :---- |
| **Data Sources** | Emulation of environmental sensors (Temperature, Humidity, Air Quality). | Python Scripts |
| **Messaging Queue** | High-throughput, fault-tolerant data streaming/buffering. | **Kafka** (w/ Zookeeper) |
| **Data Ingestion** | Collects data from Kafka and writes it to the time-series database. | **Telegraf** |
| **Time Series DB** | Stores all collected sensor data efficiently. | **InfluxDB** |
| **Alerting Engine** | Implements threshold checks and logic for anomaly detection. | **Kapacitor** |
| **Visualization** | Real-time monitoring dashboard for all sensor readings. | **Chronograf** |

###  **Key Features Implemented**

* **Sensor Emulation:** Python scripts generate time-series data for two temperature sensors, one humidity sensor, and one air quality sensor.  
* **Real-Time Streaming:** Data is published to and consumed from a **Kafka** broker, ensuring reliable, high-speed delivery.  
* **Containerization:** Full stack deployment is managed via a single docker-compose.yml file, defining all necessary services and interconnections.  
* **Time-Series Data Storage:** Data is indexed and persisted in **InfluxDB** for efficient query performance.  
* **Alert Notification System:** Custom alert definitions in **Kapacitor** monitor sensor data against defined thresholds (e.g., high temperature, low air quality) and trigger alerts.  
* **Dashboard Visualization:** Data is presented in a dynamic, user-friendly dashboard using **Chronograf**.

### **Quick Setup (Docker)**

1. **Prerequisites:** Ensure Docker and Docker Compose are installed.  
2. **Deployment:** Run the following command in the directory containing the docker-compose.yml file:  
   docker-compose up \-d

3. **Access Dashboard:** Open your web browser and navigate to the Chronograf interface (typically http://localhost:8888).