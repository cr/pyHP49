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
    if autoconnect == True:
      self.waitforhp()
      self.connect()
      self.waitforxmodem()

  def find( self ):
    hps = com.find()
    if len( hps ) == 0:
      print "No HP49-compatible USB devices connected."
      sys.stdout.flush()
    else:
      print "Number of HP49-compatible USB devices: %d" % len( hps )
      sys.stdout.flush()
    return len( hps )

  def waitforhp( self ):
    if len( com.find() ) == 0:
      print "Please connect HP49-compatible USB device...",
      sys.stdout.flush()
      while len( com.find() ) == 0:
        sleep( 1 )
      sleep( 1 ) # This one is important
      print "OK"
      
  def connect( self, cid=0 ):
    return com.connect( cid=cid, vendor=0x03f0, product=0x0121 )

  def connected( self ):
    return com.dev != None

  def waitforxmodem( self ):
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

  def read( self, length=0, timeout=1000, until=False ):
    if until != False:
      return com.read( length=length, timeout=timeout, until=until )
    elif length == 0:
      data = protocol.readpacket()
    else:
      data = com.read( length, timeout=timeout )
    print hpstr.tohexstr( data )
    print hpstr.torepr( data )
    return data

  def write( self, data, timeout=1000 ):
    return com.write( data, timeout=timeout )

  def cmd( self, cmd, args=None ):
    protocol.cmd( cmd, args=args )

  def waitack( self ):
    print hex( com.read( 1 )[0] )

  def sendack( self ):
    protocol.sendack()

  def sendnack( self ):
    protocol.sendnack()

  def xeq( self, args ):
    protocol.cmd( "E", args=args )
    return protocol.waitack()

  def download( self ):
    return protocol.download()

  def ls( self ):
    ls = cmd.ls()
    for f in ls:
      print '{0:016b}  {1:7}  {2:7} '.format( 
        f[3], cmd.objtype( f[1] ), f[2] ), hpstr.hptoutf( f[0] )

  def tohp( self, s ):
    if isinstance( s, unicode ):
      return hpstr.utftohp( s )
    elif isinstance( s, str ):
      return hpstr.utftohp( s.decode( "utf-8" ) )
    else:
      print "Unsupported encoding:", s
      return s

  def path( self ):
    protocol.cmd( "E", "PATH \x8dSTR XMIT DROP" )
    protocol.waitack()
    response = com.read( until=ord( '}' ) )
    return hpstr.tostr( response )

  def pwd( self ):
    print hpstr.hptoutf( self.path() )

  def cd( self, remoteobj ):
    remoteobj = self.tohp( remoteobj )
    protocol.cmd( "E", remoteobj )
    return protocol.waitack()

  def rm( self, remoteobj ):
    remoteobj = self.tohp( remoteobj )
    protocol.cmd( "E", "'"+remoteobj+"' PURGE" )
    return protocol.waitack()

  def get( self, remoteobj, hexdump=False ):
    remoteobj = self.tohp( remoteobj )
    data = cmd.get( remoteobj )
    if hexdump == False:
      return data
    else:
      print hpstr.tohexstr( data )
      return

  def put( self, remoteobj, data ):
    remoteobj = self.tohp( remoteobj )
    return cmd.put( remoteobj, hpstr.toarr( data ) )

  def version( self ):
    return cmd.version()

  def meminfo( self ):
    return cmd.meminfo()

  def info( self ):
    self.version()
    self.meminfo()

