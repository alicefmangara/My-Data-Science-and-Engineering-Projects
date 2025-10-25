import time

import paho.mqtt.publish as publish
import RPi.GPIO as GPIO

import BMP085 as BMP085
import PCF8591 as ADC

## PHOTORESISTOR CODE

DO = 17
GPIO.setmode(GPIO.BCM)
ADC_VALUE = 0.0048828125

def setup():
	ADC.setup(0x48)
	GPIO.setup(DO, GPIO.IN)
 
MQTT_SERVER = '10.6.1.10'

def loop():
    status = 1
    while True:
        # -- Retrieve Data from Sensors
        # Barometer
        sensor = BMP085.BMP085()                
        temp = sensor.read_temperature()	                # Read temperature to var temp (In C)
        pressure = sensor.read_pressure()	                # Read pressure to var pressure (In Pa)
        
        # Photoresistor
        luminosity = (250.0/(ADC_VALUE*ADC.read(1)))-50     # Read luminosity to var lux (In Lux)
        
        # -- Publish Data to Topics
        topics = {'18_temperature': float (temp),
                  '18_pressure': float(pressure),
                  '18_luminosity': float(luminosity)}
        
        message = []
        
        for topic, content in topics.items():
            message.append({'topic':topic, 'payload':content})
        
        publish.multiple(message,hostname=MQTT_SERVER)      # Send multiple messages to server every 3s
        
        # -- Print Data
        print ('')
        print ('      Raw value: ', ADC.read(1))  
        print ('      Luminosity from sensor = {0:0.2f} Lux'.format(luminosity))
        print ('      Temperature = {0:0.2f} C'.format(temp))		# Print temperature from Barometer
        print ('      Pressure = {0:0.2f} Pa'.format(pressure))	    # Print pressure from Barometer
        time.sleep(3)			
        print ('')

def destroy():
	pass

if __name__ == '__main__':		# Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		destroy()
