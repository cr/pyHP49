#!/usr/bin/env python
# -*- coding: utf-8 -*-

#http://www.beyondlogic.org/usbnutshell/usb1.shtml

from IPython import embed
import com
import cmd
import hpstr
import protocol
from time import sleep
import sys

class HP49( object ):

  def __init__( self, autoconnect=False ):
    """Class constructor. Attempts autoconnect when told so.
       WARNING: Consider this class singleton.
    """
    if autoconnect == True:
      self.waitforhp()
      self.connect()
      self.waitforxmodem()

  def find( self ):
    """Prints user message and returns the number of HP-49 connected via USB.
    """
    hps = com.find()
    if len( hps ) == 0:
      print "No HP49-compatible USB devices connected."
      sys.stdout.flush()
    else:
      print "Number of HP49-compatible USB devices: %d" % len( hps )
      sys.stdout.flush()
    return len( hps )

  def waitforhp( self ):
    """Interacts with user until HP-49 is connected via USB.
    """
    if len( com.find() ) == 0:
      print "Please connect HP49-compatible USB device...",
      sys.stdout.flush()
      while len( com.find() ) == 0:
        sleep( 1 )
      sleep( 1 ) # This one is important
      print "OK"
      
  def connect( self, cid=0 ):
    """Connects to to the first HP-49 listed on USB,
       or to the list number specified in cid.
       Returns success status
    """
    return com.connect( cid=cid, vendor=0x03f0, product=0x0121 )

  def connected( self ):
    """Returns connection status.
       WARNING: Will still return True if device is unplugged during operation.
    """
    return com.dev != None

  def reset( self ):
    """Resets USB device. It MAY recover when communication with the HP is stuck,
       but it WILL segfault pyusb if you reset twice in a row.
    """
    com.reset()

  def waitforxmodem( self ):
    """Interacts with user until XMODEM is enabled.
    """
    try:
      com.reset()
      sleep( 1 ) # This one is important
      cmd.version()
      return
    except:
      print "Please enable XMODEM server mode (right-shift-release arrow-right)...",
      sys.stdout.flush()
      sleep( 1 )
    while True:
      try:
        com.reset()
        cmd.version()
        print "OK"
        break
      except:
        sleep( 0.1 )

  def read( self, length=0, timeout=1000, until=False, hexdump=False ):
    """Reads specified number of bytes from device.
       Default 0 reads the whole buffer.
       When a stop byte (int) is specified in until, length is ignored.
       Returns data read or prints hexdump if told so.
    """
    data = com.read( length, timeout=timeout, until=until )
    if hexdump == True:
      print hpstr.tohexstr( data )
    else:
      return data

  def write( self, data, timeout=1000 ):
    """Writes data to USB.
       Returns number of bytes written.
    """
    return com.write( data, timeout=timeout )

  def readpacket( self, timeout=1000, hexdump=False ):
    """Reads a HP format packet (length, data, checksum) from device.
       Handles error recovery and ACKing.
       Returns data or prints hexdump if told so.
    """
    data = protocol.readpacket()
    if hexdump == True:
      print hpstr.tohexstr( data )
    else:
      return data

  def cmd( self, cmd, args=None ):
    """Sends HP command packet to device with optional argument string.
       Known so far:
       "V": version info 
       "M": memory info
       "E","str": execute RPL string
       "G","obj": get object
       "P",obj": put object
    """
    protocol.cmd( cmd, args=args )

  def waitack( self ):
    """Reads next byte from device and
       returns True if it was an ACK(0x06).
    """
    print hex( com.read( 1 )[0] )

  def sendack( self ):
    """Sends ACK(0x06) to device.
    """
    protocol.sendack()

  def sendnack( self ):
    """Sends NACK(0x15) to device.
    """
    protocol.sendnack()

  def xeq( self, cmd, utf=True ):
    """Converts utf-8 RPL cmd string to HP-encoding and executes it on device.
       Returns whether ACK status is True.
    """
    if utf == True:
      cmd = cmd.decode('utf-8')
    protocol.cmd( "E", args=hpstr.utftohp( cmd ) )
    return protocol.waitack()

  def download( self ):
    """Downloads data from device in HP's XMODEM dialects.
       Device must be prepared with the "G" command.
       Returns data array.
    """
    return protocol.download()

  def ls( self ):
    """Prints listing of current directory.
    """
    ls = cmd.ls()
    for f in ls:
      print '{0:016b}  {1:7}  {2:7} '.format( 
        f[3], cmd.objtype( f[1] ), f[2] ), hpstr.hptoutf( f[0] )

  def tohp( self, s ):
    """Converts string (regular or unicode) to HP encoding.
    """
    if isinstance( s, unicode ):
      return hpstr.utftohp( s )
    elif isinstance( s, str ):
      return hpstr.utftohp( s.decode( "utf-8" ) )
    else:
      print "Unsupported encoding:", s
      return s

  def headstr( self, utf=True ):
    """Returns head of the stack as unicode string object.
       Optionally skips utf encoding and returns HP-encoded string.
       WARNING: will stop at first '#'. You must fetch the rest manually.
       WARNING: will hang comms if stack is empty.
    """
    self.xeq( "IF DEPTH 0 ≠ THEN DUP →STR XMIT DROP END \"#\" XMIT DROP" )
    s = com.read( until=ord('#') )[:-1]
    s = hpstr.tostr( s )
    if utf == True:
      s = hpstr.hptoutf( s )
    return s

  def popstr( self, utf=True ):
    """Pops head of the stack and returns as unicode string object.
       Optionally skips utf encoding and returns HP-encoded string.
       WARNING: will stop at first '#'. You must fetch the rest manually.
       WARNING: will hang comms if stack is empty.
    """
    self.xeq( "IF DEPTH 0 ≠ THEN →STR XMIT DROP END \"#\" XMIT DROP" )
    s = com.read( until=ord('#') )[:-1]
    s = hpstr.tostr( s )
    if utf == True:
      s = hpstr.hptoutf( s )
    return s

  def pushstr( self, s, utf=True ):
    """Converts utf8-encoded string to stack.
       Optionally skips conversion.
    """
    return self.xeq( '"'+s+'"', utf=utf )

  def pushobj( self, s, utf=True ):
    """Like pushstr(), but also converts to object.
    """
    self.pushstr( s, utf=utf )
    sleep( 0.1 )
    return self.xeq( "STR→" )

  def path( self ):
    """Returns current device directory as HP-encoded string.
       Example: "{ HOME CASDIR }"
    """
    self.xeq( "PATH →STR XMIT DROP" )
    response = com.read( until=ord('}') )
    return hpstr.tostr( response )

  def pwd( self ):
    """Prints current device directory.
    """
    print hpstr.hptoutf( self.path() )

  def cd( self, remoteobj ):
    """Changes device directory to specified HP-encoded object string.
       Returns ACK status.
    """
    remoteobj = self.tohp( remoteobj )
    protocol.cmd( "E", remoteobj )
    return protocol.waitack()

  def rm( self, remoteobj ):
    """Deletes remote object specified by HP-encoded string.
       Returns ACK status.
    """
    remoteobj = self.tohp( remoteobj )
    protocol.cmd( "E", "'"+remoteobj+"' PURGE" )
    return protocol.waitack()

  def get( self, remoteobj, hexdump=False ):
    """Receives remote object specified by unicode or utf-8-encoded
       string that is passed through HP encoding.
       Currently only BINARY transfer is supported.
       Returns data or prints hexdump if told so.
    """
    remoteobj = self.tohp( remoteobj )
    data = cmd.get( remoteobj )
    if hexdump == False:
      return data
    else:
      print hpstr.tohexstr( data )
      return

  def put( self, remoteobj, data ):
    """Writes data to remote object specified by unicode or
       utf-8-encoded string that is passed through HP encoding.
       Currently only BINARY transfer is supported.
       WARNING: data is not checked for correct format.
       Returns ACK status.
    """
    remoteobj = self.tohp( remoteobj )
    return cmd.put( remoteobj, hpstr.toarr( data ) )

  def version( self ):
    """Returns version string of XMODEM server.
    """
    return cmd.version()

  def meminfo( self ):
    """Returns number of bytes available on device.
    """
    return cmd.meminfo()

  def info( self ):
    """Prints device info to screen in a well-known format.
    """
    print "****", self.version(), "****"
    print self.meminfo(), "bytes free"

  def specialchars( self ):
    """Prints a few utf-8-encoded special characters used im RPL programs.
    """
    print u'∠ ā ∇ √ ∫ Σ ▶ π ∂ ≤ ≥ ≠ α → ← ↓ ↑ γ δ ε η θ λ ρ σ τ ω Δ Π Ω ■ ∞'

  def help( self ):
    """Prints usage information.
    """
    help( self )
