""" Pi-to-Propeller Serial Test

    Remember put "init_uart_clock=7372800" in /boot/config.txt

    Sends 100,000 test patterns from the Pi to the Propeller at maximum speed
"""

"""
import ephem
o=ephem.Observer()
o.lat="44"
o.long="-123"
s=ephem.Sun()
s.compute(o)
twilight = 0 #-12 * ephem.degree
print "is_day", s.alt > twilight, "alt", s.alt
"""

import sys
import time
import threading
import tty
import termios
import ephem
import traceback
import random

MAX_BULBS = 100

PIN_POWER = 18

COLOR_MASK          = 0xFFF
COLOR_BLACK         = 0x000
COLOR_WHITE         = 0xDDD  # Default controler uses this value for white.
COLOR_BLUE          = 0xF00
COLOR_GREEN         = 0x0F0
COLOR_RED           = 0x00F
COLOR_CYAN          = COLOR_GREEN|COLOR_BLUE
COLOR_MAGENTA       = COLOR_RED|COLOR_BLUE
COLOR_YELLOW        = COLOR_RED|COLOR_GREEN
COLOR_ORANGE        = 0x04F

COLOR_NAME_MAP =  {COLOR_BLACK: "black",
                   COLOR_WHITE: "white",
                   COLOR_BLUE: "blue",
                   COLOR_GREEN: "green",
                   COLOR_RED: "red",
                   COLOR_CYAN: "cyan",
                   COLOR_MAGENTA: "magenta",
                   COLOR_YELLOW: "yellow",
                   COLOR_ORANGE: "orange"}

class Frame:
    def __init__(self, channel, numBulbs, reverse=False, badBulbs={}):
        self.commands = [0] * MAX_BULBS
        self.lastCommands = [0] * MAX_BULBS
        self.numBulbs = numBulbs
        self.channel = channel
        self.reverse = reverse
        self.badBulbs = badBulbs
        self.fill(0xCC, COLOR_BLACK)

    def fill(self, intensity, color):
        for i in range(0,self.numBulbs):
            self.setBulb(i, intensity, color)

    def setBulb(self, bulb, intensity, color):
        if (bulb in self.badBulbs) and ((self.badBulbs[bulb] & color) != 0):
            color = COLOR_BLACK
        self.commands[bulb] = (self.channel<<28) | (bulb<<20) | (intensity<<12) | color


class Animation(object):
   def __init__(self, frameset):
       self.frameset = frameset
       self.maxIndex = self.frameset.totalBulbCount()
       self.colors = [COLOR_BLUE]
       self.program_name = "base"
       self.numEach = 0
       self.maxFPS = 20
       self.multFPS = 1   # multFPS is a cheap way to make the FPS go faster, without modifying the UI slider to go past 20

   def update(self):
       pass

   def getColorNames(self):
        colorNames = []
        for color in self.colors:
            colorNames.append(COLOR_NAME_MAP.get(color, "unknown"))
        return colorNames

class SimpleSequenceAnimation(Animation):
   def __init__(self, frameset):
       super(SimpleSequenceAnimation, self).__init__(frameset)

       self.lastFrame = None
       self.lastFrameIndex = 0
       self.index=0
       self.program_name="simpleSequence"

   def update(self):
       if (self.index >= self.maxIndex):
           self.index = 0
       (frame, frameIndex) = self.frameset.indexToFrame(index)
       frame.setBulb(frameIndex, 0xCC, self.colors[0])
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
        self.program_name = "sequence"

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
       self.program_name = "fade"

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
        self.program_name = "cycle"

    def update(self):
        for i in range(0, self.maxIndex):
            (frame, frameIndex) = self.frameset.indexToFrame(i)
            frame.setBulb(frameIndex, 0xCC, self.colors[self.offset % len(self.colors)])

        self.frameset.displayAllFrames()

        self.offset = self.offset+1

class ColorMorphAnimation(Animation):
    def __init__(self, frameset, colors=[], dwell=3):
        super(ColorMorphAnimation, self).__init__(frameset)
        self.offset = 0
        self.program_name = "morph"
        self.colors = colors

        self.morphedColors = []
        for i in range(0,len(colors)):
            lastColor = colors[i]
            nextColor = colors[(i+1) % len(colors)]

            for i in range(0,8):
                color = self.combine_colors(lastColor, nextColor, i)
                self.morphedColors.append(color)

                #print "%03x" % color

            for i in range(0,dwell):
                self.morphedColors.append(nextColor)

                #print "%03x" % nextColor

    def combine_colors(self, a, b, i):
        ra = a & 0xF
        ga = (a>>4) & 0xF
        ba = (a>>8) & 0xF
        rb = b & 0xF
        gb = (b>>4) & 0xF
        bb = (b>>8) & 0xF
        j = 8-i

        rc = min(((ra*j) + (rb*i)) / 8, 0xF)
        gc = min(((ga*j) + (gb*i)) / 8, 0xF)
        bc = min(((ba*j) + (bb*i)) / 8, 0xF)

        c = (bc<<8) + (gc<<4) + (rc);

        return c

    def update(self):
        for i in range(0, self.maxIndex):
            (frame, frameIndex) = self.frameset.indexToFrame(i)
            frame.setBulb(frameIndex, 0xCC, self.morphedColors[self.offset % len(self.morphedColors)])

        self.frameset.displayAllFrames()

        self.offset = self.offset+1

class SolidColorAnimation(Animation):
    def __init__(self, frameset, colors=[]):
        super(SolidColorAnimation, self).__init__(frameset)
        self.done = False
        self.colors = colors
        self.program_name = "single"

    def update(self):
        if (not self.done):
            self.offset = 0
            for i in range(0, self.maxIndex):
                (frame, frameIndex) = self.frameset.indexToFrame(i)
                frame.setBulb(frameIndex, 0xCC, self.colors[self.offset % len(self.colors)])
                self.offset = self.offset + 1

            self.frameset.displayAllFrames()

            self.done = True

class SingleBulbAnimation(Animation):
    def __init__(self, frameset, colors=[], bulb_number=0):
        super(SingleBulbAnimation, self).__init__(frameset)
        self.done = False
        self.colors = colors
        self.bulb_number = int(bulb_number)
        self.program_name = "single_bulb"

    def update(self):
        if (not self.done):
            for i in range(0, self.maxIndex):
                (frame, frameIndex) = self.frameset.indexToFrame(i)
                if (i==self.bulb_number):
                    frame.setBulb(frameIndex, 0xCC, self.colors[0])
                else:
                    frame.setBulb(frameIndex, 0xCC, COLOR_BLACK)

            self.frameset.displayAllFrames()

            self.done = True

class SingleBulbChaseAnimation(Animation):
    def __init__(self, frameset, colors=[]):
        super(SingleBulbChaseAnimation, self).__init__(frameset)
        self.done = False
        self.colors = colors
        self.offset = 0
        self.program_name = "single_bulb_chase"

    def update(self):
        if (not self.done):
            for i in range(0, self.maxIndex):
                (frame, frameIndex) = self.frameset.indexToFrame(i)
                if (i==(self.offset % self.maxIndex)):
                    frame.setBulb(frameIndex, 0xCC, self.colors[0])
                else:
                    frame.setBulb(frameIndex, 0xCC, COLOR_BLACK)

            self.offset = self.offset + 1

            self.frameset.displayAllFrames()

class RandomFillAnimation(Animation):
    def __init__(self, frameset, colors=[]):
        super(RandomFillAnimation, self).__init__(frameset)
        self.offset = 0
        self.colors = colors
        self.program_name = "randomfill"
        self.multFPS = 4
        self.todo = []

    def nextColor(self):
        color = self.colors[self.offset % len(self.colors)]
        for i in range(0, self.maxIndex):
            (frame, frameIndex) = self.frameset.indexToFrame(i)
            self.todo.append( (frame, frameIndex, color) )

        random.shuffle(self.todo)

        self.offset = self.offset + 1

    def update(self):
        if self.todo == []:
            self.nextColor()

        (frame, frameIndex, color) = self.todo.pop()
        frame.setBulb(frameIndex, 0xCC, color)

        self.frameset.displayAllFrames()

def GET_BULB(x):
    return ((x>>20) & 0xFF)

class BaseChristmas(threading.Thread):
   def __init__(self, noSerial=False):
       super(BaseChristmas, self).__init__()
       self.daemon = True
       self.timer_state = "startup"
       if (noSerial):
           self.ser = None
           self.gpio = None
       else:
           import serial
           self.ser = serial.Serial('/dev/ttyAMA0', 460800)

           import RPi.GPIO as GPIO
           GPIO.setmode(GPIO.BCM)
           GPIO.setup(PIN_POWER, GPIO.OUT)
           self.gpio = GPIO

       self.lastAnimationChange = time.time()
       self.frames = []
       self.power = "unknown"
       self.nextPower = False
       self.setFPS(5)
       self.setup()
       self.nextAnimation = RainbowSequenceAnimation(self, [COLOR_WHITE, COLOR_BLUE], numEach=3)
       self.animation = None
       self.start()

   def setAnimation(self, anim):
       self.nextAnimation = anim
       self.lastAnimationChange = time.time()

   def setFPS(self, fps):
       if (fps<1):
           fps = 1
       self.FPS = fps;

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
           self.ser.write("%08X\r" % ((channel<<28) | (bulb<<20) | (intensity<<12) | color))

   def displayFrame(self, frame):
       for i in range(frame.numBulbs):
           if frame.commands[i] != frame.lastCommands[i]:
               if self.ser:
                   self.ser.write("%08X\r" % frame.commands[i]);
               #print "%08X\r" % frame.commands[i]
               frame.lastCommands[i] = frame.commands[i]

   def displayAllFramesOld(self):
       for frame in self.frames:
           self.displayFrame(frame);

   # Interleaving the frames is important, as it takes tiem for each command
   # to be sent out to the LED set.

   def displayAllFrames(self):
       maxBulbs = 0
       for frame in self.frames:
           maxBulbs = max(maxBulbs, frame.numBulbs)
       for i in range(0, maxBulbs):
           for frame in self.frames:
               if (i<frame.numBulbs):
                   if frame.commands[i] != frame.lastCommands[i]:
#                       if (GET_BULB(frame.commands[i]) not in [13,14]):
#                           continue
                       if self.ser:
                           self.ser.write("%08X\r" % frame.commands[i]);
                       #print "%08X\r" % frame.commands[i]
                       frame.lastCommands[i] = frame.commands[i]

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

   def setPreprogrammed(self, which=None):
       if (which==None) or (which < 0):
           which=random.randrange(0,9)

       if (which == 0):
            newProgram = RainbowSequenceAnimation(self, [COLOR_MAGENTA, COLOR_BLUE], numEach=3)
            fps = 5
       elif (which == 1):
            newProgram = RainbowSequenceAnimation(self, [COLOR_WHITE, COLOR_BLUE], numEach=3)
            fps = 5
       elif (which == 2):
            newProgram = RainbowSequenceAnimation(self, [COLOR_YELLOW, COLOR_GREEN], numEach=3)
            fps = 5
       elif (which == 3):
            newProgram = RainbowSequenceAnimation(self, [COLOR_RED, COLOR_WHITE], numEach=3)
            fps = 5
       elif (which == 4):
            newProgram = FadeColorAnimation(self, [COLOR_RED, COLOR_GREEN, COLOR_BLUE], numEach=1)
            fps = 20
       elif (which == 5):
            newProgram = AllColorCycleAnimation(self, [COLOR_RED,COLOR_GREEN,COLOR_BLUE,COLOR_WHITE,COLOR_MAGENTA,COLOR_YELLOW])
            fps = 1
       elif (which == 6):
            newProgram = RainbowSequenceAnimation(self, [COLOR_ORANGE, COLOR_BLACK], numEach=6)
            fps = 5
            #newProgram = RainbowSequenceAnimation(self, [COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE], numEach=8)
            #fps = 20
       elif (which == 7):
            newProgram = ColorMorphAnimation(self, [COLOR_RED,COLOR_GREEN,COLOR_BLUE])
            fps = 5
       elif (which == 8):
            newProgram = RandomFillAnimation(self, [COLOR_RED,COLOR_GREEN,COLOR_BLUE,COLOR_YELLOW,COLOR_WHITE,COLOR_MAGENTA])
            fps = 20
       else:
            print "XXX unknown value for 'which'", which

       self.setAnimation(newProgram)
       self.setFPS(fps)

   def run(self):
       while True:
           tStart = time.time()

           if (self.nextPower != self.power):
               self.power = self.nextPower
               if (self.gpio):
                    if self.power:
                        print "powering on"
                        self.gpio.output(PIN_POWER, 1)
                    else:
                        print "powering off"
                        self.gpio.output(PIN_POWER, 0)
               time.sleep(0.50)
               self.enumerateAllFrames()

           if (self.power):
               if (self.nextAnimation) :
                   self.animation = self.nextAnimation
                   self.nextAnimation = None
                   print "set animation to", self.animation.program_name, ",".join(self.animation.getColorNames())

               self.animation.update()

           self.check_schedule()

           self.check_autochange()

           if self.animation:
               period = 1.0/min(self.animation.maxFPS, self.FPS)/self.animation.multFPS
           else:
               period = 1.0/5.0

           while (time.time()-tStart) < period:
               time.sleep(0.0001)

   def setPower(self, value):
       self.nextPower = value

   def is_daylight(self):
        o=ephem.Observer()
        o.lat="44"
        o.long="-123"
        s=ephem.Sun()
        s.compute(o)
        twilight = 0 # -12 * ephem.degree
        return s.alt > twilight

   def check_schedule(self):
       if self.is_daylight():
           if (self.timer_state!="turned_off"):
               self.timer_state="turned_off"
               self.setPower(False)
               print "timer turn off"
       else:
           if (self.timer_state!="turned_on"):
               self.timer_state="turned_on"
               self.setPower(True)
               print "timer turn on"

   def check_autochange(self):
       if (time.time() - self.lastAnimationChange) > 300:
           self.setPreprogrammed()

class MyChristmas(BaseChristmas):
   def setup(self):
       self.frames.append(Frame(1, 52, reverse=True))  # front door
       self.frames.append(Frame(0, 50,                 # garage roof
                                badBulbs={9: COLOR_RED}))
       self.frames.append(Frame(2, 32))                # rv park
       self.frames.append(Frame(3, 36))                # garage door
       self.frames.append(Frame(4, 13))                # desk top
       self.frames.append(Frame(5, 13))                # junk


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






