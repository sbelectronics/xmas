'' =================================================================================================
''
''   File....... jm_serial_rx.spin
''   Purpose.... True mode serial receiver with buffer
''   Author..... Jon "JonnyMac" McPhalen 
''               Copyright (c) 2009-2012 Jon McPhalen
''               -- see below for terms of use
''   E-mail..... jon@jonmcphalen.com
''   Started.... 
''   Updated.... 28 AUG 2012
''
'' =================================================================================================


con

  BUF_SIZE = 512                                                ' 16, 32, 64, 128, 256, or 512
  BUF_MASK = BUF_SIZE - 1
  

var

  long  cog

  long  pin                                                     ' rx pin
  long  bitticks                                                ' system tick in one bit
  long  bufaddr                                                 ' hub address of buffer
  long  rxhead                                                  ' head pointer (0..BUF_SIZE-1)
  long  rxtail                                                  ' tail pointer (0..BUF_SIZE-1)

  byte  buffer[BUF_SIZE]                                        ' receive buffer 


pub start(rxd, baud)

'' Creates true mode receive UART on pin rxd at baud rate

  stop                                                          ' stop cog if running
  flush                                                         ' clear buffer

  pin      := rxd                                               ' set parameters
  bitticks := clkfreq / baud
  bufaddr  := @buffer

  cog := cognew(@rxserial, @pin) + 1                            ' start rx cog

  return cog     


pub stop

'' Stops serial RX driver; frees a cog 

  if (cog)
    cogstop(cog - 1)
    cog := 0


pub flush

'' Flush receive buffer

  if (cog)
    repeat while (rxcheck => 0)                                 ' empty buffer
    
  longfill(@rxhead, 0, 2)                                       ' clear everything
  bytefill(@buffer, 0, BUF_SIZE)


pub rxcheck | c

'' Returns byte from buffer if available
'' -- returns -1 if buffer is empty

  if (rxtail <> rxhead)
    c := buffer[rxtail]
    rxtail := ++rxtail & BUF_MASK
    return c
  else
    return -1
      

pub rx | c

'' Returns byte if available
'' -- will wait if buffer is embpty

  repeat while (rxtail == rxhead)
  c := buffer[rxtail]
  rxtail := ++rxtail & BUF_MASK

  return c
  

pub wait(b) | check

'' Waits for specific byte in RX input stream

  repeat
    check := rx                                                 ' get byte from stream
  until (check == b)


pub wait_str(pntr) | count, cpntr, check

'' Waits for specific string in input stream
'' -- pntr is a pointer to the string to wait for

  count := strsize(pntr)
  cpntr := pntr

  repeat while count
    check := rx                                                 ' get byte from stream
    if (check == byte[cpntr])                                   ' compare to string
      --count                                                   ' if match, update count
      ++cpntr                                                   '  and character pointer      
    else
      count := strsize(pntr)                                    ' else reset count
      cpntr := pntr                                             '  and character pointer 


pub get_str(pntr) | c

'' Waits for CR-terminated string
'' -- pntr is a pointer to the string buffer

  repeat
    c := rx                                                     ' wait for a character
    if (c == 13)                                                ' if CR
      c := 0                                                    '  convert to 0
    byte[pntr++] := c                                           ' add to string
    if (c == 0)
      quit


pub address

'' Returns address of rx buffer

  return @buffer
  
  
dat

                        org     0

rxserial                mov     t1, par                         ' get address of parameters
                        rdlong  t2, t1                          ' read rx pin
                        mov     rxmask, #1                      ' convert to mask
                        shl     rxmask, t2

                        add     t1, #4                          ' next parameter
                        rdlong  rxbit1x0, t1                    ' read bit timing
                        mov     rxbit1x5, rxbit1x0              ' create 1.5 bit timing
                        shr     rxbit1x5, #1
                        add     rxbit1x5, rxbit1x0

                        add     t1, #4
                        rdlong  rxbufpntr, t1                   ' get buffer address

                        add     t1, #4
                        mov     rxheadpntr, t1                  ' save pointer to rxhead

                        add     t1, #4
                        mov     rxtailpntr, t1                  ' save pointer to rxtail
                        
                                                  
receive                 mov     rxwork, #0                      ' clear work var
                        mov     rxtimer, rxbit1x5               ' set timer to 1.5 bits
                        
waitstart               waitpne rxmask, rxmask                  ' wait for falling edge
                        add     rxtimer, cnt                    ' sync with system counter

                        { unrolled for best speed }
                        
rxbyte                  waitcnt rxtimer, rxbit1x0               ' wait for middle of bit
                        test    rxmask, ina             wc      ' rx --> c  
                        muxc    rxwork, #%0000_0001             ' c --> bit0  
                        
                        waitcnt rxtimer, rxbit1x0
                        test    rxmask, ina             wc      ' rx --> c  
                        muxc    rxwork, #%0000_0010             ' c --> bit1 

                        waitcnt rxtimer, rxbit1x0
                        test    rxmask, ina             wc      ' rx --> c  
                        muxc    rxwork, #%0000_0100             ' c --> bit2 
                        
                        waitcnt rxtimer, rxbit1x0
                        test    rxmask, ina             wc      ' rx --> c  
                        muxc    rxwork, #%0000_1000             ' c --> bit3 

                        waitcnt rxtimer, rxbit1x0
                        test    rxmask, ina             wc      ' rx --> c  
                        muxc    rxwork, #%0001_0000             ' c --> bit4 
                        
                        waitcnt rxtimer, rxbit1x0
                        test    rxmask, ina             wc      ' rx --> c  
                        muxc    rxwork, #%0010_0000             ' c --> bit5 

                        waitcnt rxtimer, rxbit1x0
                        test    rxmask, ina             wc      ' rx --> c  
                        muxc    rxwork, #%0100_0000             ' c --> bit6 
                        
                        waitcnt rxtimer, rxbit1x0
                        test    rxmask, ina             wc      ' rx --> c  
                        muxc    rxwork, #%1000_0000             ' c --> bit7 

                        waitpeq rxmask, rxmask                  ' wait for stop bit

putrxbuf                rdlong  t1, rxheadpntr                  ' t1 := rxhead
                        add     t1, rxbufpntr                   ' t1 := rxbuf[rxhead]
                        wrbyte  rxwork, t1                      ' rxbuf[rxhead] := rxwork
                        sub     t1, rxbufpntr                   ' t1 := rxhead 
                        add     t1, #1                          ' inc t1
                        and     t1, #BUF_MASK                   ' rollover if needed
                        wrlong  t1, rxheadpntr                  ' rxhead := t1

                        jmp     #receive 

' -------------------------------------------------------------------------------------------------

rxmask                  res     1                               ' mask for rx pin
rxbit1x0                res     1                               ' ticks per bit
rxbit1x5                res     1                               ' ticks per 1.5 bits
rxheadpntr              res     1                               ' pointer to head position
rxtailpntr              res     1                               ' pointer to tail position
rxbufpntr               res     1                               ' pointer to buffer[0]

rxwork                  res     1                               ' rx byte input
rxtimer                 res     1                               ' timer for bit sampling

t1                      res     1
t2                      res     1 
                                 
                        fit     496
                        

dat

{{

  Terms of Use: MIT License 

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to the following
  conditions:

  The above copyright notice and this permission notice shall be included in all copies
  or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
  CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
  OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 

}}                    