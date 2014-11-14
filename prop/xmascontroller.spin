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
          handle_L2
      else
          getchar

PUB getchar
  curChar := rxserial.rx

PUB hexval
  if (curChar=>"0") and (curChar=<"9")
      return curChar-"0"
  if (curChar=>"A") and (curChar=<"F")
      return 10+curChar-"A"
  return -1

PUB handle_L2 | v, channel
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
          curChar := rxserial.rx
          return
      else
          ' invalid character
          return
  
  

PUB handle_L | v, address, bright, r, g, b, channel, command
  getchar
  v:=hexval
  if (v==-1)
      return
  channel := v
  
  getchar
  v:=hexval
  if (v==-1)
      return
  address := v<<4
  
  getchar
  v:=hexval
  if (v==-1)
      return
  address := address | v
  
  getchar
  v:=hexval
  if (v==-1)
      return
  bright := v<<4

  getchar
  v:=hexval
  if (v==-1)
      return
  bright := bright | v

  getchar
  b:=hexval
  if (b==-1)
      return

  getchar
  g:=hexval
  if (g==-1)
      return

  getchar
  r:=hexval
  if (r==-1)
      return

  pst.Str(string("channel="))
  pst.Dec(channel)
  pst.Str(string(" addr="))
  pst.Dec(address)
  pst.Str(string(" bright="))
  pst.Dec(bright)
  pst.Str(string(" r="))
  pst.Dec(r)
  pst.Str(string(" g="))
  pst.Dec(g)
  pst.Str(string(" b="))
  pst.Dec(b)
  pst.NewLine

  if (bright>$CC)
      bright:=$CC

  command := ((address&$3F)<<20) | ((bright&$FF)<<12) | ((b&$F)<<8) | ((g&$F)<<4) | (r & $F)

  pst.Str(string(" command="))
  pst.Hex(command,8)
  pst.NewLine

  ' command handler always ends with the next character in curChar
  getchar


  