con
  _clkfreq = 160_000_000
  
  RX1     = 35  { I }                                           ' programming / debug
  TX1     = 37  { O }
  BR_TERM  = 115_200                                            ' terminal baud rate
  
obj
  term : "jm_fullduplexserial"
  
pub main
  term.start(RX1, TX1, %0000, BR_TERM)
  repeat
    pintoggle(56)
    term.fstr0(string("It's working!\r\n"))
    waitms(250)
      
          