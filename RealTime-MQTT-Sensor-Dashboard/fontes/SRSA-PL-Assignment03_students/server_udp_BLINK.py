#!/usr/bin/env python3
import sys
import socket
from gpiozero import Device, LED
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

GPIO_PIN = 17
led = LED(GPIO_PIN)

def runBlink():
    while True:
        # As the loop executes, we are toggling GPIO pin LedPin, our output pin, on and off
        print ('...LED ON')
        # Turn on LED
        led.on()
        sleep(1)
        print ('LED OFF...')
        # Turn off LED
        led.off()
        sleep(1)

# Define a destroy function for clean up everything after the script finished
def destroy():
    # INSERT CODE HERE
    # COMPLETE THE CODE TO TURN OFF LED AND CLOSE SOCKET
    sleep(1)

def main():
    global ServerSocket

    if len(sys.argv) != 3:
        print("Usage: {sys.argv[0]} <host> <port>")
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])

    # INSERT CODE HERE
    # COMPLETE THE CODE TO RECEIVE THE MESSAGE FROM CLIENT USING SOCKETS
    # IF MESSAGE IS "BLINK" THE LED MUST BLINK


if __name__ == '__main__':
    setup()
    try:
        main()
    # WHEN CTRL+C IS PRESSED, CALL destroy()
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt, exiting")
    finally:
        destroy()
