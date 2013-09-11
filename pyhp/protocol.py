#!/usr/bin/env python
# -*- coding: utf-8 -*-

import com.hpusb as com
import hpstr
from struct import pack
from time import sleep

def mkpacket( data ):
    # TODO: check maximum size
    crc = hpchk( data )
    return pack( ">h%dsB" % len( data ), len( data ), data, crc )

def cmd( cmd, args=None ):
    if args:
      s = cmd + mkpacket( args )
      #print "CMD:", hpstr.tohexstr( s )
      # TODO: can we send as one chunk?
      com.write( s[0] )
      sleep( 0.1 )
      com.write( s[1:] )
    else:
      s = cmd
      #print "CMD:", hpstr.tohexstr( s )
      com.write( s )

def waitack( timeout=1000 ):
    ack = com.read( 1, timeout=timeout )[0]
    #print "ACK:", hex( ack )
    return ack == 6

def sendack():
    com.write( '\x06' )

def sendnack():
    com.write( '\x15' )

def cancel():
    com.write( '\x18' ) 
    com.write( '\x18' ) 
    com.write( '\x18' ) 

def sendpacket( data ):
    pkt = mkpkt( data )
    while True:
      com.write( pkt )
      if waitack():
        break
      else:
        print "CRC NACK. RESENDING."
        # TODO: retry limit

def readpacket():
    l = com.read( 1, timeout=1000 )[0]*256
    l += com.read( 1, timeout=1000 )[0]
    #print "LEN:", l
    l += 1 # also read crc, else freakish outcome
    while True:
      inp = com.read( l, timeout=1000 ) 
      data = inp[:-1]
      crc = inp[-1]
      #print "DATA:", hpstr.tohexstr( data ) 
      #print "     ", hpstr.torepr( data )
      #print "CRC:", "%02x" % crc
      if crc == hpchk( data ):
        break
      else:
        print "CRC NACK!"
        sendnack()
        # TODO: retry limit
    sendack()
    return data

def get( remotefile ):
    cmd( "G", remotefile )
    if not waitack():
      print "NACK on remote file", remotefile
      return False
    sleep(1)
    return download()

def download():
    data = []
    cmd( "D" )

    while True:
      sleep(0.1)
      ptype = com.read( 1 )[0]

      if ptype == 1: #SOH
        #print "SOH",
        inp = com.read( 132 )
        #print hpstr.tohexstr( inp ),
        crc = hpcrc( inp[2:-2] )
        if inp[-2]*256 + inp[-1] == crc:        
            sendack()
            data += inp[2:-2]
            #print "CHKSUM OK"
        else:
            sendnack()
            print "CHKSUM FAIL"

      elif ptype == 2: #STX
        #print "STX",
        inp = com.read( 1028 )
        #print hpstr.tohexstr( inp ),
        crc = hpcrc( inp[2:-2] )
        if inp[-2]*256 + inp[-1] == crc:        
            sendack()
            data += inp[2:-2]
            #print "CHKSUM OK"
        else:
            sendnack()
            print "CHKSUM FAIL"

      elif ptype == 4: #EOT
        #print "EOT"
        sendack()
        break

      else:
        print "UNSUPPORTED PACKET TYPE", hex(ptype)
        com.flush( all=True )
        cancel()
        return None

    sleep(0.5)
    sendack()
    return data # TODO: trim padding, don't rely on binary format

def put( remotefile, data ):
    cmd( "P", remotefile )
    if not waitack():
      print "NACK on remote file", remotefile
      return False
    sleep(1)
    return upload( data )

def upload( data ):
    data = hpstr.toarr( data )
    resp = com.read( 1 )[0]
    if resp != ord( 'D' ):
      cancel()
      print "Device didn't accept file:", hex( resp )
      return False

    pos = 0
    pktnr = 1
    while pos < len( data ):
      sleep(0.1)

      size = len( data ) # len data may change due to padding
      if size-pos >= 1024:
        ptype = 2
        plen = 1024
      if  size-pos >= 128:
        ptype = 1
        plen = 128
      else:
        while size-pos < 128:
          data.append( 0x1a )
          size += 1
        ptype = 1
        plen = 128

      chunk = data[pos:pos+plen]
      if ptype == 1: #SOH
        com.write( [1] )
        #print "SOH",
        sleep( 0.1 )
        com.write( [pktnr, 255-pktnr] )
        #print hpstr.tohexstr( [pktnr, 255-pktnr] ),
        com.write( chunk )
        #print hpstr.tohexstr( chunk ),
        crc = hpcrc( chunk )
        com.write( [crc>>8, crc & 0xff ] )
        if waitack() == True:
          #print "CHKSUM ACK"
          pos += plen
        else:
          print "CHKSUM NACK"
          # TODO: retry counter
        # TODO: cancel checking

    com.write( [4]  ) #EOT
    #print "EOT"
    #waitack()
    #sendack()
    return waitack()

def hpchk( data, start=0 ):
    return ( sum( hpstr.toarr( data ) ) + start ) & 0xff

def hpcrc( data, start=0 ):
    e = start
    for x in hpstr.toarr( data ):
      lo =  (x       ^ e) & 0xf
      e  =  (e >> 4) ^ (lo + (lo << 7) + (lo << 12))
      hi = ((x >> 4) ^ e) & 0xf
      e  =  (e >> 4) ^ (hi + (hi << 7) + (hi << 12))
    return e

