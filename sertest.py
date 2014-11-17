""" Pi-to-Propeller Serial Test

    Remember put "init_uart_clock=7372800" in /boot/config.txt

    Sends 100,000 test patterns from the Pi to the Propeller at maximum speed
"""

import serial
import time

FPS=20
PERIOD=(1.0/FPS)

ser = serial.Serial('/dev/ttyAMA0', 460800)
for j in range(0, 100):
    tStart = time.time()
    for i in range(0, 100):
        ser.write("02345678\r")
        ser.write("12345678\r")
        ser.write("22345678\r")
        ser.write("32345678\r")
        ser.write("42345678\r")
        ser.write("52345678\r")
    while (time.time()-tStart < PERIOD):
        pass

ser.write("FFFFFFFF\r")


