'' =================================================================================================
''
''   File....... sertest.spin
''   Purpose.... Serial library tester
''   Author..... smbaker
''   E-mail..... smbaker@gmail.com
''   Started.... 
''   Updated.... 11-13-2014
''
'' This program sets up the rxserial library to receive at 460800 baud on pin 8, it then echos
'' the received characters out the Parallax Serial Terminal (which on a prop demo board will go
'' out the USB; use Parallax Serial Terminal application on the PC to view the characters)
''
'' On the pi, make sure to put "init_uart_clock=7372800" in /boot/config.txt
'' Then load minicom using sudo minicom -b 460800 -D /dev/ttyAMA0 
''
'' =================================================================================================

CON 
    _clkmode    = xtal1 + pll16x
    _xinfreq    = 5_000_000

OBJ
  rxserial : "jm_serial_rx"
  pst : "Parallax Serial Terminal"

PUB main | b
  rxserial.start(8, 460800)
  pst.start(115200)

  repeat
      b := rxserial.rx
      pst.char(b)
  