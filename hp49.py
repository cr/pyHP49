#!/usr/bin/env python
# -*- coding: utf-8 -*-

#http://www.beyondlogic.org/usbnutshell/usb1.shtml

from IPython import embed
import sys
import pyhp
from pyhp import *

from IPython.terminal.embed import InteractiveShellEmbed
ipshell = InteractiveShellEmbed( banner1="ready.", exit_msg="bye." )

# main ##########################################################################################
if __name__ == "__main__":

  hp = pyhp.hp49.HP49( autoconnect=True )
  hp.info()

  # Flag: overwrite existing files
  #hp.cmd( "E", "-36 CF" ) ; hp.waitack()
  # Memory info
  #hp.cmd( "M" ) ; print hp.readpacket()
  # Version info
  #hp.cmd( "V" ) ; print hp.readpacket()
  # Directory listing
  #hp.cmd( "L" ) ; print hp.readpacket()
  # Path
  #hp.cmd( "E", "PATH \x8dSTR XMIT DROP"  ) ; hp.waitack() ; print hp.readpacket()
  # Chdir
  #hp.cmd( "E", "CASDIR" ) ; hp.waitack()
  #x=r'"%%%%HP: T(3)A("CASE -17. FS? THEN "R" END -18. FS? THEN "G" END "D" END +")F(" + IF -51. FS? THEN "," ELSE "." END ");\x0a" + + IFERR \x27%s\x27 RCL STR + \x27ttt\x27 STO THEN CLEAR "N" ELSE "Y" END XMIT'

  #embed()
  ipshell()
