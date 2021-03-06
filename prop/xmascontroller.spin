''
'' commands
''    caaiibgr<CR>
''     c                channel
''      aa              address
''        ii            intensity
''          b           blue
''           g          green
''            r         red      

CON 
    _clkmode    = xtal1 + pll16x
    _xinfreq    = 5_000_000

    ' pins
    PIN_RXSERIAL = 8
    PIN_LIGHTS0 = 16
    PIN_LIGHTS1 = 17
    PIN_LIGHTS2 = 18
    PIN_LIGHTS3 = 19
    PIN_LIGHTS4 = 20
    PIN_LIGHTS5 = 21
    

OBJ
  rxserial : "serial_32bit"
  pst : "Parallax Serial Terminal"

  xmas0 : "xmas2"
  xmas1 : "xmas2"
  xmas2 : "xmas2"
  xmas3 : "xmas2"
  xmas4 : "xmas2"
  xmas5 : "xmas2"  

VAR
  byte curChar
  long testCount
  long errorCount

PUB main | b, channel, bright                                             
  rxserial.start(PIN_RXSERIAL, 460800)
  'pst.start(115200)

  xmas0.start(PIN_LIGHTS0)
  xmas1.start(PIN_LIGHTS1)
  xmas2.start(PIN_LIGHTS2)
  xmas3.start(PIN_LIGHTS3)
  xmas4.start(PIN_LIGHTS4)
  'xmas5.start(PIN_LIGHTS5)    ' we can't enable xmas5 unless we turn off the serial terminal

  repeat
      b := rxserial.rx
      'pst.Hex(b,8)
      'pst.NewLine

      'if (b==$FFFFFFFF)
      '    dumpStats
      '    next

      ' <channel:1><addr:2><bright:2><b><g><r>
        
      channel := b >> 28

      ' set the maximum brightness to $CC
      bright := (b >> 12) & $FF
      if (bright > $CC)
          bright := $CC
      b := (b & $0FF00FFF) | (bright << 12) 

      if (b==$02345678)
          testCount++
      else                                                
          errorCount++

      case channel
          0: xmas0.send_raw_command(b)
          1: xmas1.send_raw_command(b)
          2: xmas2.send_raw_command(b)
          3: xmas3.send_raw_command(b)
          4: xmas4.send_raw_command(b)
          '5: xmas5.send_raw_command(b)   

PUB dumpStats
    pst.Str(string("testCount = "))
    pst.Dec(testCount)
    pst.Str(string(" errorCount = "))
    pst.Dec(errorCount)
    pst.NewLine  