""" Pi-to-Propeller Serial Test

    Remember put "init_uart_clock=7372800" in /boot/config.txt

    Sends 100,000 test patterns from the Pi to the Propeller at maximum speed
"""

import serial
import time

MAX_BULBS = 100

COLOR_MASK          = 0xFFF
COLOR_BLACK         = 0x000
COLOR_WHITE         = 0xDDD  # Default controler uses this value for white.
COLOR_BLUE          = 0xF00
COLOR_GREEN         = 0x0F0
COLOR_RED           = 0x00F
COLOR_CYAN          = COLOR_GREEN|COLOR_BLUE
COLOR_MAGENTA       = COLOR_RED|COLOR_BLUE
COLOR_YELLOW        = COLOR_RED|COLOR_GREEN

class Frame:

    def __init__(self, channel, numBulbs):
        self.commands = [0] * MAX_BULBS
        self.lastCommands = [0] * MAX_BULBS
        self.numBulbs = numBulbs
        self.channel = channel
        self.fill(0xCC, COLOR_BLACK)

    def fill(self, intensity, color):
        for i in range(0,self.numBulbs):
            self.setBulb(i, intensity, color)

    def setBulb(self, bulb, intensity, color):
        self.commands[bulb] = (self.channel<<28) | (bulb<<20) | (intensity<<12) | color

class Christmas:
   def __init__(self):
       self.ser = serial.Serial('/dev/ttyAMA0', 460800)
       self.frames = []
       self.setFPS(5)
       self.setup()
       self.enumerateAllFrames()

   def setFPS(self, fps):
       self.FPS = fps;
       self.period = 1.0/fps

   def setup(self):
       raise TypeError, "you must fill in the setup method"

   def enumerateAllFrames(self):
       for frame in self.frames:
           self.enumeration(frame)

   def enumeration(self, frame):
       for i in range(0, frame.numBulbs):
           self.setBulb(frame.channel, i, 0xCC, COLOR_BLACK)
           time.sleep(0.01)

   def setBulb(self, channel, bulb, intensity, color):
       self.ser.write("%X%02X%02X%03X\r" % (channel, bulb, intensity, color))

   def displayFrame(self, frame):
       for i in range(frame.numBulbs):
           if frame.commands[i] != frame.lastCommands[i]:
               self.ser.write("%08X\r" % frame.commands[i]);
               #print "%08X\r" % frame.commands[i]
               frame.lastCommands[i] = frame.commands[i]

   def displayAllFrames(self):
       for frame in self.frames:
           self.displayFrame(frame);

   def totalBulbCount(self):
       total=0
       for frame in self.frames:
           total = total + frame.numBulbs
       return total

   def indexToFrame(self, i):
       # wrap
       tbc = self.totalBulbCount
       if (i<0):
           i=i+tbc
       if (i>=tbc):
           i=i-tbc

       for frame in self.frames:
           if (i<frame.numBulbs):
               return (frame, i)
           else:
               i=i-frame.numBulbs

   def runSimpleSequence(self):
       lastFrame = None
       lastFrameIndex = 0
       index=0
       maxIndex = self.totalBulbCount()
       color = COLOR_MAGENTA
       while True:
           tStart = time.time()
           if (index >= maxIndex):
               index = 0
           (frame, frameIndex) = self.indexToFrame(index)
           frame.setBulb(frameIndex, 0xCC, COLOR_MAGENTA)
           if (lastFrame):
               lastFrame.setBulb(lastFrameIndex, 0xCC, COLOR_BLACK)
           lastFrame=frame
           lastFrameIndex=frameIndex

           self.displayAllFrames()

           index = index + 1

           while (time.time()-tStart) < self.period:
               time.sleep(0.0001)

   def runRainbowSequence(self, colors=[], numEach=1):
       offset = 0
       maxIndex = self.totalBulbCount()
       while True:
           tStart = time.time()
           for i in range(0, self.totalBulbCount()):
               (frame, frameIndex) = self.indexToFrame(i)
               frame.setBulb(frameIndex, 0xCC, colors[ ((i+offset) % len(colors*numEach))/numEach ])

           self.displayAllFrames()

           offset=offset+1

           while (time.time()-tStart) < self.period:
               time.sleep(0.0001)


class MyChristmas(Christmas):
   def setup(self):
       self.frames.append(Frame(0, 50))

c = MyChristmas()
c.runRainbowSequence([COLOR_WHITE, COLOR_BLUE],numEach=3)






