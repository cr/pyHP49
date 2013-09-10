#!/usr/bin/env python
# -*- coding: utf-8 -*-

import array

#http://www.hpmuseum.org/cgi-sys/cgiwrap/hpmuseum/articles.cgi?read=1218
_hp = u'\x1F\x7F\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8A\x8B\x8C\x8D\x8E\x8F\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9A\x9B\x9C\x9D\x9E\x9F'
_utf = u'\u2026\u2592\u2220\u0101\u2207\u221A\u222B\u03A3\u25B6\u03C0\u2202\u2264\u2265\u2260\u03B1\u2192\u2190\u2193\u2191\u03B3\u03B4\u03B5\u03B7\u03B8\u03BB\u03C1\u03C3\u03C4\u03C9\u0394\u03A0\u03A9\u25A0\u221E'
_transhptoutf = dict( ( ord( a ), b ) for a, b in zip( _hp, _utf ) ) # maketrans workaround for unicode
_transutftohp = dict( ( ord( a ), b ) for a, b in zip( _utf, _hp ) ) # maketrans workaround for unicode

def tostr( data ):
    """Converts a string or byte array to a string.
    """
    if isinstance( data, str ):
      return data
    else:
      return ''.join( map( chr, data ) )

def toarr( data ):
    """Converts a string or byte array to a byte array.
    """
    if isinstance( data, array.array ):
      return data
    else:
      return array.array( 'B', data )

def tohexstr( data ):
    """Converts raw data to a hex representation string.
    """
    return ' '.join( '%02x' % b for b in toarr( data ) )

def torepr( data ):
    """Converts raw data to a printable string representation. 
    """
    return ''.join( repr( c )[1:-1] for c in tostr( data ) )

def hptoutf( hpstring ):
    """Converts an HP encoded string to a unicode string.
    """
    global _transhptoutf
    return hpstring.decode( "raw_unicode_escape" ).translate( _transhptoutf )

def utftohp( utfstring ):
    """Converts a unicode string to an HP encoded string.
    """
    global _transutftohp
    return utfstring.translate( _transutftohp ).encode( "raw_unicode_escape" )

