HP49USB
=======

This is experimental code and most likely unfit for your purposes.

## Requirements

* pip install pyusb xmodem

## Usage

Connect the calculator via USB, put it into XMODEM server mode (right-shift-release
right-arrow), and then run ./hp49.py. You are dropped into an Ipython shell,
so you can have some fun with the hp object.

## Examples
```
$ ./hp49.py 
XModem Version 1.0
197201 bytes free.
ready.
In [1]: hp.ls()
0010000011000001  DOLIST      17.5  ΣPAR
1000011010011100  DOARRY     175.0  ΣDAT
0000111000100001  DOEXT0    1048.5  ΣPRODAT
1000000010000111  DOLIB    47319.5  stat49pr
0100000101001011  DOLIST      28.0  IOPAR
0000011111011010  DOREAL      10.5  TEST
0011110010011001  DOLIST      74.5  PPAR
1110001101101100  DORRP      358.5  CASDIR

In [2]: hp.get( "PPAR" )
48 50 48 50 34 39 2d 43 74 2a 70 97 02 00 40 45 09 42 66 54 91 00 00 00 00 00 65 20 02 77 29 00 00 54 94 20 64 46 15 00 00 00 00 00 00 80 43 80 e4 02 01 58 37 f9 72 97 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 af c9 83 e4 02 01 59 2b 31 10 0a 00 04 54 45 53 54 04 33 29 70 01 00 00 00 00 00 10 10 02 00 05 49 4f 50 41 52 05 74 2a 30 93 02 05 00 00 00 00 20 15 01 37 f9 72 93

In [3]: data = hp.get( "ΣPRODAT", ret=True )

In [4]: hp.xeq( "VERSION" )
```
