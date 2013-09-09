#!/usr/bin/env python
# -*- coding: utf-8 -*-

#http://www.beyondlogic.org/usbnutshell/usb1.shtml

from IPython import embed
import sys
import usb
import xmodem
from string import maketrans
from struct import pack
from time import sleep

def lsusb():
  for bus in usb.busses:
    for dev in usb.devices:
      print repr(dev)
      print "Device:", dev.filename
      print "  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor)
      print "  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct)
      print "Manufacturer:", dev.iManufacturer
      print "Serial:", dev.iSerialNumber
      print "Product:", dev.iProduct

#lsusb()


class HP49( object ):


  def __init__( self ):
    self.dev = None
    self.cfg = None
    self.intf = None
    self.epin = None
    self.epout = None
    self.modem = None
    self.inithputf()

  def connect( self ):
    # so far just the first hp49 is supported
    self.dev = usb.core.find(idVendor=0x03f0, idProduct=0x0121)
    if not self.dev:
      return None

    # use default config
    self.dev.set_configuration()

    # so far it has always been like this on my hp50g  
    assert( self.dev.bLength == 18 )
    assert( self.dev.bDescriptorType == 1 )
    assert( self.dev.bDeviceClass == 255 )
    assert( self.dev.bDeviceProtocol == 0 )
    assert( self.dev.bDeviceSubClass == 0 )
    assert( self.dev.bNumConfigurations == 1 )

    # get an endpoint instance
    self.cfg = self.dev.get_active_configuration()

    # so far it has always been like this on my hp50g  
    assert( self.cfg.bNumInterfaces == 1 )

    self.intf = self.cfg[(0,0)] # (interface index, altsetting index)

    # so far it has always been like this on my hp50g  
    assert( self.intf.bInterfaceNumber == 0 )
    assert( self.intf.bAlternateSetting == 0 )

    # not required with just one alt setting
    #self.intf.set_altsetting()

    # so far it has always been like this on my hp50g  
    assert( self.intf.bNumEndpoints == 2 )

    # hardcoded assumption. should filter for in/out
    self.epin = self.intf[0]
    self.epout = self.intf[1]

    # so far it has always been like this on my hp50g  
    assert( usb.util.endpoint_direction( self.epin.bEndpointAddress ) == usb.util.ENDPOINT_IN )
    assert( usb.util.endpoint_type( self.epin.bEndpointAddress ) == usb.util.ENDPOINT_TYPE_ISO )
    assert( usb.util.endpoint_direction( self.epout.bEndpointAddress ) == usb.util.ENDPOINT_OUT )
    assert( usb.util.endpoint_type( self.epout.bEndpointAddress ) == usb.util.ENDPOINT_TYPE_INTR )
    assert( self.epin.bEndpointAddress == 129 ) # srsly?
    assert( self.epout.bEndpointAddress == 3 )

    # see https://pypi.python.org/pypi/xmodem
    # and http://pythonhosted.org/xmodem/xmodem.html
    self.modem = xmodem.XMODEM( self.getc, self.putc )

    self.dev.reset()
    return self.intf

  def getc( self, size, timeout=1 ):
    data = self.read( size, timeout=timeout*1000 )
    print "getc:", size, data
    return 

  def putc( self, data, timeout=1 ):
    print "putc: ", data
    return self.epout.write( data, timeout=timeout*1000 )

  def mkpacket( self, data ):
    crc = self.modem.calc_checksum( data )
    return pack( ">h%dsB" % len( data ), len( data ), data, crc )

  def tohexstr( self, dat ):
    if isinstance( dat, str ):
      return ' '.join( '%02x' % ord( c ) for c in dat )
    else:
      return ' '.join( '%02x' % b for b in dat )

  def torepr( self, dat ):
    if isinstance( dat, str ):
      return ''.join( repr( c )[1:-1] for c in dat )
    else:
      return ''.join( repr( chr( b ) )[1:-1] for b in dat )

  def tostr( self, arr ):
    if isinstance( arr, str ):
      return arr
    else:
      return ''.join( chr( b ) for b in arr )

  def cmd( self, cmd, args=None ):
    if args:
      s = cmd + self.mkpacket( args )
      print "CMD:", self.tohexstr( s )
      self.epout.write( s[0] )
      sleep( 0.1 )
      self.epout.write( s[1:] )
    else:
      s = cmd
      print "CMD:", self.tohexstr( s )
      self.epout.write( s )

  def waitack( self, timeout=1000 ):
    ack = self.epin.read( 1, timeout=timeout )[0]
    print "ACK:", hex( ack )
    return ack == 6

  def sendack( self ):
    self.epout.write( '\x06' )

  def sendnack( self ):
    self.epout.write( '\x15' )

  def write( self, data ):
    return self.epout.write( data )

  def read( self, length, timeout=2000 ):
    inp = []
    while len( inp ) < length:
    	inp += self.epin.read( length-len(inp), timeout=2000 )
    return inp

  def sendpacket( self, dat ):
    pkt = self.mkpkt( dat )
    while True:
      self.write( pkt )
      if self.waitack():
        break
      else:
        print "CRC NACK. RESENDING."
        # TODO: retry limit

  def readpacket( self ):
    l = self.epin.read( 1, timeout=1000 )[0]*256
    l += self.epin.read( 1, timeout=1000 )[0]
    print "LEN:", l
    l += 1 # also read crc, else freakish outcome
    while True:
      inp = self.read( l, timeout=1000 ) 
      dat = self.tostr( inp[:-1] )
      crc = inp[-1]
      print "DATA:", self.tohexstr( dat ) 
      print "     ", self.torepr( dat )
      print "CRC:", "%02x" % crc
      if crc == self.modem.calc_checksum( dat ):
        break
      else:
        print "CRC NACK!"
        self.sendnack()
        # TODO: retry limit
    self.sendack()
    return dat

  def flush( self, timeout=1000 ):
    while True:
      inp = []
      try:
        inp += self.read( 64, timeout=timeout )
        print "FLUSH:", self.tohexstr( inp )
        print "      ", self.torepr( inp )
      except:
        break
    dat = self.tostr( inp )
    return dat  

  def inithputf( self ):
    #http://www.hpmuseum.org/cgi-sys/cgiwrap/hpmuseum/articles.cgi?read=1218
    hp = u'\x1F\x7F\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8A\x8B\x8C\x8D\x8E\x8F\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9A\x9B\x9C\x9D\x9E\x9F'
    utf = u'\u2026\u2592\u2220\u0101\u2207\u221A\u222B\u03A3\u25B6\u03C0\u2202\u2264\u2265\u2260\u03B1\u2192\u2190\u2193\u2191\u03B3\u03B4\u03B5\u03B7\u03B8\u03BB\u03C1\u03C3\u03C4\u03C9\u0394\u03A0\u03A9\u25A0\u221E'
    self.transhptoutf = dict( ( ord( a ), b ) for a, b in zip( hp, utf ) ) # maketrans workaround for unicode
    self.transutftohp = dict( ( ord( a ), b ) for a, b in zip( utf, hp ) ) # maketrans workaround for unicode

  def hptoutf( self, s ):
    return s.decode( "raw_unicode_escape" ).translate( self.transhptoutf )

  def utftohp( self, s ):
    return s.translate( self.transutftohp ).encode( "raw_unicode_escape" )

  def objtype( self, t ):
    #http://www.hpcalc.org/details.php?id=5910
    types = {
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
    return types[t][0]

  def ls( self ):
    self.cmd( "L" )
    raw = self.readpacket()
    p = 0
    ls = []
    while p<len(raw):
      l = ord(raw[p]) ; p += 1
      name = raw[p:p+l] ; p += l
      objtype = ord(raw[p])*256 + ord(raw[p+1]) ; p += 2
      size = (ord(raw[p]) + ord(raw[p+1])*256 + ord(raw[p+2])*256*256) / 2.0 ; p += 3
      unknown = ord(raw[p])*256 + ord(raw[p+1]) ; p += 2
      ls.append( (self.hptoutf(name), self.objtype(objtype), size, unknown ) )    
    for f in ls:
      print f[0], f[1], f[2], f[3]

hp = HP49()
if not hp.connect():
  print "ERROR: no hp49 found"
  sys.exit( 5 )

embed()
sys.exit()

# Flag: overwrite existing files
hp.cmd( "E", "-36 CF" ) ; hp.waitack()

# Memory info
hp.cmd( "M" ) ; print hp.readpacket()

# Version info
hp.cmd( "V" ) ; print hp.readpacket()

# Directory listing
#hp.cmd( "L" ) ; print hp.readpacket()

# Path
hp.cmd( "E", "PATH \x8dSTR XMIT DROP"  ) ; hp.waitack() ; print hp.readpacket()

# Chdir
hp.cmd( "E", "CASDIR" ) ; hp.waitack()

x=r'"%%%%HP: T(3)A("CASE -17. FS? THEN "R" END -18. FS? THEN "G" END "D" END +")F(" + IF -51. FS? THEN "," ELSE "." END ");\x0a" + + IFERR \x27%s\x27 RCL STR + \x27ttt\x27 STO THEN CLEAR "N" ELSE "Y" END XMIT'


