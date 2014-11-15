""" Pi-to-Propeller Serial Test

    Remember put "init_uart_clock=7372800" in /boot/config.txt

    Sends 100,000 test patterns from the Pi to the Propeller at maximum speed
"""

import serial
import time

ser = serial.Serial('/dev/ttyAMA0', 460800)
for i in range(0, 100000):
    ser.write("12345678\r")


