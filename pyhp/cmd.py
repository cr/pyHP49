#!/usr/bin/env python
# -*- coding: utf-8 -*-

import protocol
import hpstr

#http://www.hpcalc.org/details.php?id=5910
objtypes = {
      0x3329: ("DOREAL","real (%) 153."),
      0x7729: ("DOCMP","complex (C%) (3.,4.)"),
      0x2C2A: ("DOCSTR","string ($) 'Hello'"),
      0xE829: ("DOARRY","array ( [] ) [3. 4.]"),
      0x742A: ("DOLIST","list ( {} ) {3 4}"),
      0x482E: ("DOIDNT","global name (id) 'MYPROG'"),
      0x6D2E: ("DOLAM","local name (lam) 'j'"),
      0x9D2D: ("DOCOL","program ( :: ; ) :: %1 %2 x+ ;"),
      0xB82A: ("DOSYMB","algebraic (alg) '1+2*3^4'"),
      0x4E2A: ("DOHSTR/XS" "user binary integer (hxs) #1234567890123456h"),
      0x1E2B: ("DOGROB","grob"),
      0xFC2A: ("DOTAG","tagged :Price:153.95"),
      0xDA2A: ("DOEXT","unit 365.2422_d"),
      0x922E: ("DOROMP","xlib (romptr) XLIB F0 BA"),
      0x1129: ("DOBINT","bint ~ FFFFFh"),
      0x962A: ("DORRP","dir (rrp) DIR ... END"),
      0x5529: ("DOEREL","long real (%%) 1.23456789012345E12345"),
      0x9D29: ("DOECMP","long complex (C%%) (3E0,4E0)"),
      0x0A2A: ("DOLNKARRY","linked array ( l[] )"),
      0xBF29: ("DOCHAR","character"),
      0xCC2D: ("DOCODE","code object"),
      0x402B: ("DOLIB","library"),
      0x622B: ("DOBAK","backup object"),
      0x882B: ("DOEXT0","library data (aka EXT0)"),
      0xAA2B: ("DOEXT1","or DOACPTR access pointer (aka Extended Ptr, and EXT1)"),
      0xCC2B: ("DOEXT2","font (erroneously called EXT2 by Vger)"),
      0xFE26: ("DOMINIFONT","MiniFont"),
      0xEE2B: ("DOEXT3","ext3  note: was dispatch type DF in HP48"),
      0x102C: ("DOEXT4","ext4"),
      0x1426: ("DOINT","integer (ZINT)"),
      0x3A26: ("DOLNGREAL","infinite-precision real (not yet implemented)"),
      0x6026: ("DOLNGCMP","infinite-precision complex (not yet implemented)"),
      0x8626: ("DOMATRIX","symbolic matrix"),
      0xAC26: ("DOFLASHP","Flash Pointer (FPTR n n; FPTR2 ^name)"),
      0xD526: ("DOAPLET","Aplet (not yet implemented)")
}

def objtype( integer, verbose=0 ):
    """Translates object type number into a string representation.
       The default verbose=0 gives a compact descriptor, =1 a verbose description.
    """
    return objtypes[integer][verbose]

def version():
    """Returns the server version string.
    """
    protocol.cmd( "V" )
    return hpstr.tostr( protocol.readpacket() )

def meminfo():
    """Returns the number of free bytes in calculator memory.
    """
    protocol.cmd( "M" )
    return int( hpstr.tostr( protocol.readpacket()[:-1] ) )

def ls():
    """Returns a list with objects in the current directory.
    """
    protocol.cmd( "L" )
    raw = protocol.readpacket()
    p = 0
    ls = []
    while p < len(raw):
      l = raw[p] ; p += 1
      name = hpstr.tostr( raw[p:p+l] ) ; p += l
      objtype = raw[p]*256 + raw[p+1] ; p += 2
      size = (raw[p] + raw[p+1]*256 + raw[p+2]*256*256) / 2.0 ; p += 3
      flags = raw[p]*256 + raw[p+1] ; p += 2
      ls.append( [ name, objtype, size, flags ] )    
    return ls

def get( remotefile ):
    """Reads remotefile from current directory and returns it as byte array.
       Currently only binary mode is supported.
    """
    return protocol.get( remotefile )

