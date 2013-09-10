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
      com.reset()
      try:
        cmd.version()
        return
      except:
        print "Please enable XMODEM server mode (right-shift-release arrow-right)...",
        sys.stdout.flush()
        sys.exit(5) # TODO: fix detection and remove hackish workaround
      while True:
        try:
          protocol.cancel()
          com.flush()
          com.dev.reset()
          cmd.version()
          break
        except:
          sleep( 1 )
      print "OK"
      sys.stdout.flush()

  def connected( self ):
    return com.dev != None

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
      print "OK"

  def connect( self, id=0 ):
    com.connect( id )
    sleep( 1 )

  def cmd( self, cmd, args=None ):
    protocol.cmd( cmd, args=args )

  def waitack( self ):
    print hex( com.read( 1 )[0] )

  def read( self, len=0 ):
    if len == 0:
      data = protocol.readpacket()
    else:
      data = com.read( len )
    print hpstr.tohexstr( data )
    print hpstr.torepr( data )
    return data

  def sendack( self ):
    protocol.sendack()

  def sendnack( self ):
    protocol.sendnack()

  def write( self, data ):
    return com.write( data )

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

  def cd( self, remoteobj ):
    remoteobj = self.tohp( remoteobj )
    protocol.cmd( "E", remoteobj )
    return protocol.waitack()

  def rm( self, remoteobj ):
    remoteobj = self.tohp( remoteobj )
    protocol.cmd( "E", "'"+remoteobj+"' PURGE" )
    return protocol.waitack()

  def get( self, remoteobj, ret=False ):
    remoteobj = self.tohp( remoteobj )
    data = cmd.get( remoteobj )
    if ret == False:
      print hpstr.tohexstr( data )
      return
    else:
      return data

  def put( self, remoteobj, data ):
    remoteobj = self.tohp( remoteobj )
    return cmd.put( remoteobj, hpstr.toarr( data ) )

  def version( self ):
    print cmd.version()

  def meminfo( self ):
    print cmd.meminfo(), "bytes free."

  def info( self ):
    self.version()
    self.meminfo()

