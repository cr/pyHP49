#!/usr/bin/env python
# -*- coding: utf-8 -*-

import array

dev = None

def find():
    """Returns list of device objects of all connected HPs.
    """
    ###############
    # TODO: WRITEME 
    ###
    return []

def connect( cid=0 ):
    """Connects to the HP49 in the system numbered by device.
       Returns True if successfull, else False.
    """
    global dev
    ###############
    # TODO: WRITEME 
    ###
    return False

def write( data, timeout=1000 ):
    """Sends data to calculator. data can be a string or array.
       Returns the number of bytes written.
    """ 
    global dev
    ###############
    # TODO: WRITEME 
    ###
    return 0

def read( length=0, timeout=1000, until=False ):
    """Reads length bytes of data from the calculator with optional
       stop byte.
       Returns data as array.array of bytes.
    """
    global dev
    ###############
    # TODO: WRITEME 
    ###
    return data

def reset():
    """Resets USB state.
    """
    global dev
    ###############
    # TODO: WRITEME 
    ###
    dev.reset()

def flush( all=False, timeout=100 ):
    """Flushes the input buffer and returns flushed bytes.
    """
    global dev
    ###############
    # TODO: WRITEME 
    ###
    return data
