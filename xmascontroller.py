""" Pi-to-Propeller Serial Test

    Remember put "init_uart_clock=7372800" in /boot/config.txt

    Sends 100,000 test patterns from the Pi to the Propeller at maximum speed
"""

import sys
import time
import threading
import tty
import termios

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
    def __init__(self, channel, numBulbs, reverse=False):
        self.commands = [0] * MAX_BULBS
        self.lastCommands = [0] * MAX_BULBS
        self.numBulbs = numBulbs
        self.channel = channel
        self.reverse = reverse
        self.fill(0xCC, COLOR_BLACK)

    def fill(self, intensity, color):
        for i in range(0,self.numBulbs):
            self.setBulb(i, intensity, color)

    def setBulb(self, bulb, intensity, color):
        self.commands[bulb] = (self.channel<<28) | (bulb<<20) | (intensity<<12) | color

class Animation(object):
   def __init__(self, frameset):
       self.frameset = frameset
       self.maxIndex = self.frameset.totalBulbCount()

   def update(self):
       pass

class SimpleSequenceAnimation(Animation):
   def __init__(self, frameset):
       super(SimpleSequenceAnimation, self).__init__(frameset)

       self.lastFrame = None
       self.lastFrameIndex = 0
       self.index=0
       self.color = COLOR_MAGENTA

   def update(self):
       if (self.index >= self.maxIndex):
           self.index = 0
       (frame, frameIndex) = self.frameset.indexToFrame(index)
       frame.setBulb(frameIndex, 0xCC, COLOR_MAGENTA)
       if (self.lastFrame):
           self.lastFrame.setBulb(self.lastFrameIndex, 0xCC, COLOR_BLACK)
       self.lastFrame=self.frame
       self.lastFrameIndex=self.frameIndex

       self.frameset.displayAllFrames()

       self.index = self.index + 1

class RainbowSequenceAnimation(Animation):
    def __init__(self, frameset, colors=[], numEach=1):
        super(RainbowSequenceAnimation, self).__init__(frameset)
        self.colors = colors
        self.numEach = numEach
        self.offset = 0

    def update(self):
        for i in range(0, self.frameset.totalBulbCount()):
           (frame, frameIndex) = self.frameset.indexToFrame(i)
           frame.setBulb(frameIndex, 0xCC, self.colors[ ((i+self.offset) % (len(self.colors)*self.numEach))/self.numEach ])

        self.frameset.displayAllFrames()

        self.offset=self.offset+1

class FadeColorAnimation(Animation):
   def __init__(self, frameset, colors=[], numEach=1):
       super(FadeColorAnimation, self).__init__(frameset)
       self.direction = 1
       self.intensity = 0
       self.colors = colors
       self.numEach = numEach

   def update(self):
       for i in range(0, self.maxIndex):
           (frame, frameIndex) = self.frameset.indexToFrame(i)
           frame.setBulb(frameIndex, self.intensity, self.colors[ ((i) % len(self.colors*self.numEach))/self.numEach ])

       self.frameset.displayAllFrames()

       self.intensity=self.intensity+self.direction
       if (self.intensity>=0x40):
           self.direction=-1
       elif (self.intensity<=0):
           self.direction=1

class AllColorCycleAnimation(Animation):
    def __init__(self, frameset, colors=[]):
        super(AllColorCycleAnimation, self).__init__(frameset)
        self.offset = 0
        self.colors = colors

    def update(self):
        for i in range(0, self.maxIndex):
            (frame, frameIndex) = self.frameset.indexToFrame(i)
            frame.setBulb(frameIndex, 0xCC, self.colors[self.offset % len(self.colors)])

        self.frameset.displayAllFrames()

        self.offset = self.offset+1

class SolidColorAnimation(Animation):
    def __init__(self, frameset, colors=[]):
        super(SolidColorAnimation, self).__init__(frameset)
        self.done = False
        self.colors = colors

    def update(self):
        if (not self.done):
            self.offset = 0
            for i in range(0, self.maxIndex):
                (frame, frameIndex) = self.frameset.indexToFrame(i)
                frame.setBulb(frameIndex, 0xCC, self.colors[self.offset % len(self.colors)])
                self.offset = self.offset + 1

            self.frameset.displayAllFrames()

            self.done = True

class BaseChristmas(threading.Thread):
   def __init__(self, noSerial=False):
       super(BaseChristmas, self).__init__()
       self.daemon = True
       if (noSerial):
           self.ser = None
       else:
           import serial
           self.ser = serial.Serial('/dev/ttyAMA0', 460800)
       self.frames = []
       self.setFPS(5)
       self.setup()
       self.enumerateAllFrames()
       self.nextAnimation = RainbowSequenceAnimation(self, [COLOR_WHITE, COLOR_BLUE], numEach=3)
       self.animation = None
       self.start()

   def setAnimation(self, anim):
       self.nextAnimation = anim

   def setFPS(self, fps):
       if (fps<1):
           fps = 1
       if (fps>20):
           fps = 20
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
           if self.ser:
               # pause if we're actually sending out the commands
               time.sleep(0.01)

   def setBulb(self, channel, bulb, intensity, color):
       if self.ser:
           self.ser.write("%X%02X%02X%03X\r" % (channel, bulb, intensity, color))

   def displayFrame(self, frame):
       for i in range(frame.numBulbs):
           if frame.commands[i] != frame.lastCommands[i]:
               if self.ser:
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
               if frame.reverse:
                   return (frame, frame.numBulbs-i-1)
               else:
                   return (frame, i)
           else:
               i=i-frame.numBulbs

   def run(self):
       while True:
           tStart = time.time()

           if (self.nextAnimation) :
               self.animation = self.nextAnimation
               self.nextAnimation = None

           self.animation.update()

           while (time.time()-tStart) < self.period:
               time.sleep(0.0001)

class MyChristmas(BaseChristmas):
   def setup(self):
       self.frames.append(Frame(2, 32))                # rv park
       self.frames.append(Frame(0, 50))                # garage
       self.frames.append(Frame(1, 49, reverse=True))  # front door
       self.frames.append(Frame(3, 25))                # desk top

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

Christmas = None
def startup(noSerial=False):
    global Christmas
    Christmas = MyChristmas(noSerial)

def main():
    startup()
    c = Christmas

    print "q ... quit"
    print "+ ... increase fps"
    print "- ... decrease fps"
    print "r ... solid red"
    print "g ... solid green"
    print "b ... solid blue"
    print "w ... solid white"
    print "1 ... blue white sequence"
    print "2 ... yellow green sequence"
    print "3 ... red white sequence"
    print "4 ... fade"
    print "5 ... all color cycle"

    while True:
        ch = getch()
        if (ch=='q'):
            return
        elif (ch=='r'):
            c.setAnimation(SolidColorAnimation(c,[COLOR_RED]))
        elif (ch=='g'):
            c.setAnimation(SolidColorAnimation(c,[COLOR_GREEN]))
        elif (ch=='b'):
            c.setAnimation(SolidColorAnimation(c,[COLOR_BLUE]))
        elif (ch=='w'):
            c.setAnimation(SolidColorAnimation(c,[COLOR_WHITE]))
        elif (ch=='1'):
            c.setAnimation(RainbowSequenceAnimation(c,[COLOR_WHITE, COLOR_BLUE], numEach=3))
        elif (ch=='2'):
            c.setAnimation(RainbowSequenceAnimation(c,[COLOR_YELLOW, COLOR_GREEN], numEach=3))
        elif (ch=='3'):
            c.setAnimation(RainbowSequenceAnimation(c,[COLOR_RED, COLOR_WHITE], numEach=3))
        elif (ch=='4'):
            c.setAnimation(FadeColorAnimation(c,[COLOR_RED, COLOR_GREEN, COLOR_BLUE], numEach=1))
        elif (ch=='5'):
            c.setAnimation(AllColorCycleAnimation(c,[COLOR_RED,COLOR_GREEN,COLOR_BLUE,COLOR_WHITE,COLOR_MAGENTA,COLOR_YELLOW]))
        elif (ch=='+'):
            c.setFPS(c.FPS+1)
        elif (ch=='-'):
            c.setFPS(c.FPS-1)

        time.sleep(0.01)

if __name__ == "__main__":
    main()






