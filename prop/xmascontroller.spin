''
'' commands
''    Lcaaiibgr<CR>
''    L                 a capital L
''     c                channel
''      aa              address
''        ii            intensity
''          b           blue
''           g          green
''            r         red      

CON 
    _clkmode    = xtal1 + pll16x
    _xinfreq    = 5_000_000

    STATE_WAIT = 1

OBJ
  rxserial : "serial_32bit"
  pst : "Parallax Serial Terminal"

VAR
  byte curChar
  long testCount
  long errorCount
  long loopCount

PUB main | b, channel                                             
  rxserial.start(8, 460800)
  pst.start(115200)

  repeat
      b := rxserial.rx
      'pst.Hex(b,8)
      'pst.NewLine 

      loopCount++
      if (b==$12345678)
          testCount++
      else                                                
          errorCount++
      
      channel := b >> 28
      b &= $0FFCCFFF ' <addr:2><bright:2><b><g><r>

      if ((loopCount // 1000) == 0)
          dumpStats       

PUB dumpStats
    pst.Str(string("testCount = "))
    pst.Dec(testCount)
    pst.Str(string(" errorCount = "))
    pst.Dec(errorCount)
    pst.NewLine  
