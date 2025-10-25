import re
import socket
import time

UDP_IP = '127.0.0.1'
UDP_PORT = 5000
REPEAT_ALARM_INTERVAL = 20  # Repeat alarms every 20 seconds

def receive_alarms():
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_IP, UDP_PORT))

    alarms = {}

    while True:
        data, addr = udp_socket.recvfrom(1024)
        alarm_msg = data.decode()

        print(f"Received alarm message: {alarm_msg}")

        # Extract sensor information and value using regular expressions
        match = re.search(r'sensor_data_([^ ]+) - Value: ([^ ]+)', alarm_msg)
        if match:
            sensor_info = match.group(1)
            value = match.group(2)

            print(f"Extracted sensor info: {sensor_info}")
            print(f"Extracted value: {value}")

            if sensor_info in alarms:
                # Check if it's time to repeat the alarm
                if time.time() - alarms[sensor_info] >= REPEAT_ALARM_INTERVAL:
                    print(f"REPEATED ALARM: {alarm_msg}")
                    alarms[sensor_info] = time.time()
            else:
                # New alarm received
                alarms[sensor_info] = time.time()
                print(f"ALARM: {alarm_msg}")
        else:
            print(f"Ignoring malformed alarm message: {alarm_msg}")

    udp_socket.close()

if __name__ == '__main__':
    receive_alarms()
