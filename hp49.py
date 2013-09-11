#!/usr/bin/env python
# -*- coding: utf-8 -*-

#http://www.beyondlogic.org/usbnutshell/usb1.shtml

from IPython.terminal.embed import InteractiveShellEmbed
ipshell = InteractiveShellEmbed( banner1="ready.", exit_msg="bye." )

import pyhp
import pyhp.hp49 as hp

# main ##########################################################################################
if __name__ == "__main__":

  hp.open()
  hp.info()

  ipshell()

  # Flag: overwrite existing files
  #hp.xeq( "E", "-36 CF" )
  #x=r'"%%%%HP: T(3)A("CASE -17. FS? THEN "R" END -18. FS? THEN "G" END "D" END +")F(" + IF -51. FS? THEN "," ELSE "." END ");\x0a" + + IFERR \x27%s\x27 RCL STR + \x27ttt\x27 STO THEN CLEAR "N" ELSE "Y" END XMIT'
