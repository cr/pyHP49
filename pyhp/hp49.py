#!/usr/bin/env python
# -*- coding: utf-8 -*-

#http://www.beyondlogic.org/usbnutshell/usb1.shtml

import com
import cmd
import hpstr
import protocol
from time import sleep
import sys
from pydoc import help as doc

def find():
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

def waitforhp():
    """Interacts with user until HP-49 is connected via USB.
    """
    if len( com.find() ) == 0:
      print "Please connect HP49-compatible USB device...",
      sys.stdout.flush()
      while len( com.find() ) == 0:
        sleep( 1 )
      sleep( 1 ) # This one is important
      print "OK"
      
def connect( cid=0 ):
    """Connects to to the first HP-49 listed on USB,
       or to the list number specified in cid.
       Returns success status
    """
    return com.connect( cid=cid, vendor=0x03f0, product=0x0121 )

def open():
    """Convenience wrapper that interacts with user until HP is
       connected and set-up properly.
    """
    waitforhp()
    connect()
    waitforxmodem()

def connected():
    """Returns connection status.
       WARNING: Will still return True if device is unplugged during operation.
    """
    return com.dev != None

def reset():
    """Resets USB device. It MAY recover when communication with the HP is stuck,
       but it WILL segfault pyusb if you reset twice in a row.
    """
    com.reset()

def waitforxmodem():
    """Interacts with user until XMODEM is enabled.
    """
    try:
      com.reset()
      sleep( 1 ) # This one is important
      cmd.version()
      return
    #should be except usb.USBError:, but for sake of modularity
    except: # might mask different errors, resulting in pyusb segfaults
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

def read( length=0, timeout=1000, until=False, hexdump=False ):
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

def write( data, timeout=1000 ):
    """Writes data to USB.
       Returns number of bytes written.
    """
    return com.write( data, timeout=timeout )

def readpacket( timeout=1000, hexdump=False ):
    """Reads a HP format packet (length, data, checksum) from device.
       Handles error recovery and ACKing.
       Returns data or prints hexdump if told so.
    """
    data = protocol.readpacket()
    if hexdump == True:
      print hpstr.tohexstr( data )
    else:
      return data

def hpcmd( command, args=None ):
    """Sends raw HP command string to device with optional argument string.
       There is no implicit conversion the strings.
       Known so far:
       "V": version info 
       "M": memory info
       "E","str": execute RPL string
       "G","obj": get object
       "P",obj": put object
    """
    protocol.cmd( command, args=args )

def waitack():
    """Reads next byte from device and
       returns True if it was an ACK(0x06).
    """
    print hex( com.read( 1 )[0] )

def sendack():
    """Sends ACK(0x06) to device.
    """
    protocol.sendack()

def sendnack():
    """Sends NACK(0x15) to device.
    """
    protocol.sendnack()

def xeq( command, utf=True ):
    """Converts utf-8 RPL command string to HP-encoding and executes it on device.
       Returns whether ACK status is True.
    """
    if utf == True:
      command = cmd.decode('utf-8')
    protocol.cmd( "E", args=hpstr.utftohp( command ) )
    return protocol.waitack()

def download():
    """Downloads data from device in HP's XMODEM dialects.
       Device must be prepared with the "G" command.
       Returns data array.
    """
    return protocol.download()

def ls():
    """Prints listing of current directory.
    """
    ls = cmd.ls()
    for f in ls:
      print '{0:016b}  {1:7}  {2:7} '.format( 
        f[3], cmd.objtype( f[1] ), f[2] ), hpstr.hptoutf( f[0] )

def tohp( s ):
    """Converts string (regular or unicode) to HP encoding.
    """
    if isinstance( s, unicode ):
      return hpstr.utftohp( s )
    elif isinstance( s, str ):
      return hpstr.utftohp( s.decode( "utf-8" ) )
    else:
      print "Unsupported encoding:", s
      return s

def headstr( utf=True ):
    """Returns head of the stack as unicode string object.
       Optionally skips utf encoding and returns HP-encoded string.
       WARNING: will stop at first '#'. You must fetch the rest manually.
       WARNING: will hang comms if stack is empty.
    """
    xeq( "IF DEPTH 0 ≠ THEN DUP →STR XMIT DROP END \"\t\" XMIT DROP" )
    s = com.read( until=ord('\t') )[:-1]
    s = hpstr.tostr( s )
    if utf == True:
      s = hpstr.hptoutf( s )
    return s

def popstr( utf=True ):
    """Pops head of the stack and returns as unicode string object.
       Optionally skips utf encoding and returns HP-encoded string.
       WARNING: will stop at first '#'. You must fetch the rest manually.
       WARNING: will hang comms if stack is empty.
    """
    xeq( "IF DEPTH 0 ≠ THEN →STR XMIT DROP END \"\t\" XMIT DROP" )
    s = com.read( until=ord('\t') )[:-1]
    s = hpstr.tostr( s )
    if utf == True:
      s = hpstr.hptoutf( s )
    return s

def pushstr( s, utf=True ):
    """Converts utf8-encoded string to stack.
       Optionally skips conversion.
    """
    return xeq( '"'+s+'"', utf=utf )

def pushobj( s, utf=True ):
    """Like pushstr(), but also converts to object.
    """
    pushstr( s, utf=utf )
    sleep( 0.1 )
    return xeq( "STR→" )

def path():
    """Returns current device directory as HP-encoded string.
       Example: "{ HOME CASDIR }"
    """
    xeq( "PATH →STR XMIT DROP" )
    response = com.read( until=ord('}') )
    return hpstr.tostr( response )

def pwd():
    """Prints current device directory.
    """
    print hpstr.hptoutf( path() )

def cd( remoteobj ):
    """Changes device directory to specified HP-encoded object string.
       Returns ACK status.
    """
    remoteobj = tohp( remoteobj )
    protocol.cmd( "E", remoteobj )
    return protocol.waitack()

def rm( remoteobj ):
    """Deletes remote object specified by HP-encoded string.
       Returns ACK status.
    """
    remoteobj = tohp( remoteobj )
    protocol.cmd( "E", "'"+remoteobj+"' PURGE" )
    return protocol.waitack()

def get( remoteobj, hexdump=False ):
    """Receives remote object specified by unicode or utf-8-encoded
       string that is passed through HP encoding.
       Currently only BINARY transfer is supported.
       Returns data or prints hexdump if told so.
    """
    remoteobj = tohp( remoteobj )
    data = cmd.get( remoteobj )
    if hexdump == False:
      return data
    else:
      print hpstr.tohexstr( data )
      return

def put( remoteobj, data ):
    """Writes data to remote object specified by unicode or
       utf-8-encoded string that is passed through HP encoding.
       Currently only BINARY transfer is supported.
       WARNING: data is not checked for correct format.
       Returns ACK status.
    """
    remoteobj = tohp( remoteobj )
    return cmd.put( remoteobj, hpstr.toarr( data ) )

def version():
    """Returns version string of XMODEM server.
    """
    return cmd.version()

def meminfo():
    """Returns number of bytes available on device.
    """
    return cmd.meminfo()

def info():
    """Prints device info to screen in a well-known format.
    """
    print "****", version(), "****"
    print meminfo(), "bytes free"

def specialchars():
    """Prints a few utf-8-encoded special characters used im RPL programs.
    """
    print u'∠ ā ∇ √ ∫ Σ ▶ π ∂ ≤ ≥ ≠ α → ← ↓ ↑ γ δ ε η θ λ ρ σ τ ω Δ Π Ω ■ ∞'

def help():
    """Prints usage information.
    """
    doc( sys.modules[__name__] )

