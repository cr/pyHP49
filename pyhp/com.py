#!/usr/bin/env python
# -*- coding: utf-8 -*-

#http://www.beyondlogic.org/usbnutshell/usb1.shtml

import usb

dev = None
cfg = None
intf = None
epin = None
epout = None

def find( vendor=0x03f0, product=0x0121 ):
    """Returns list of usb device objects of all connected HPs.
    """
    return usb.core.find( find_all=True, idVendor=vendor, idProduct=product )

def connect( device=0, vendor=0x03f0, product=0x0121 ):
    """Connects to the HP49 in the system numbered by device.
       Returns True if successfull, else False.
    """
    global dev, cfg, intf, epin, epout

    # TODO: this should not be a global singleton
    dev = usb.core.find( find_all=True, idVendor=vendor, idProduct=product )[device]
    if not dev:
      return False

    # use default config
    dev.set_configuration()

    # so far it has always been like this on my hp50g  
    assert( dev.bLength == 18 )
    assert( dev.bDescriptorType == 1 )
    assert( dev.bDeviceClass == 255 )
    assert( dev.bDeviceProtocol == 0 )
    assert( dev.bDeviceSubClass == 0 )
    assert( dev.bNumConfigurations == 1 )

    # get an endpoint instance
    cfg = dev.get_active_configuration()

    # so far it has always been like this on my hp50g  
    assert( cfg.bNumInterfaces == 1 )

    intf = cfg[(0,0)] # (interface index, altsetting index)

    # so far it has always been like this on my hp50g  
    assert( intf.bInterfaceNumber == 0 )
    assert( intf.bAlternateSetting == 0 )

    # not required with just one alt setting
    #intf.set_altsetting()

    # so far it has always been like this on my hp50g  
    assert( intf.bNumEndpoints == 2 )

    # hardcoded assumption. should filter for in/out
    epin = intf[0]
    epout = intf[1]

    # so far it has always been like this on my hp50g  
    assert( usb.util.endpoint_direction( epin.bEndpointAddress ) == usb.util.ENDPOINT_IN )
    assert( usb.util.endpoint_type( epin.bEndpointAddress ) == usb.util.ENDPOINT_TYPE_ISO )
    assert( usb.util.endpoint_direction( epout.bEndpointAddress ) == usb.util.ENDPOINT_OUT )
    assert( usb.util.endpoint_type( epout.bEndpointAddress ) == usb.util.ENDPOINT_TYPE_INTR )
    assert( epin.bEndpointAddress == 129 ) # srsly?
    assert( epout.bEndpointAddress == 3 )

    return True

def write( data, timeout=1000 ):
    """Sends data to calculator. data can be a string or array.
       Returns the number of bytes written.
    """ 
    global epout
    return epout.write( data, timeout=timeout )

def read( length, timeout=1000 ):
    """Reads length bytes of data from the calculator and returns them as
       array.array of bytes.
    """
    global epin
    inp = []
    while len( inp ) < length:
    	inp += epin.read( length-len(inp), timeout=timeout )
    return inp

def reset():
    """Resets USB state.
    """
    global dev
    dev.reset()

def flush( self, timeout=200 ):
    """Flushes the input buffer.
    """
    while True:
      try:
        read( 128, timeout=timeout )
      except:
        break
    reset()
