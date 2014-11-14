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
  rxserial : "jm_serial_rx"
  pst : "Parallax Serial Terminal"

VAR
  byte curChar

PUB main | b
  rxserial.start(8, 460800)
  pst.start(115200)

  getchar
  repeat
      if (curChar == "L")
          handle_L
      else
          getchar

PUB getchar
  curChar := rxserial.rx

PUB handle_L | v, channel
  v:=0
  repeat
      curChar := rxserial.rx
      if (curChar=>"0") and (curChar=<"9")
          v := (v<<4) | (curChar-"0")
      elseif (curChar=>"A") and (curChar=<"F")
          v := (v<<4) | (10+curChar-"A")
      elseif (curChar==13)
          channel := (v>>28)
          v:=v & $03FFFFFF
          pst.Str(string(" channel="))
          pst.Dec(channel)
          pst.Str(string(" command="))
          pst.Hex(v,8)
          pst.NewLine
          ' handle_L always returns with a character in curChar
          curChar := rxserial.rx
          return
      else
          ' invalid character
          return
  
  




  