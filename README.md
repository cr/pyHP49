pyHP49
=======

This is experimental code and most likely unfit for your purposes. It might accidentally delete all your calculator data, or worse. Make a backup!

It has been developed on a HP-50g, but should easily be made to work, perhaps work out of the box, on any HP-49x series calculator with a USB port.

## Requirements

* pip install pyusb

## Usage

Connect the calculator via USB, put it into XMODEM server mode (right-shift-release
right-arrow), and then run ./hp49.py. Or run it first, and it will prompt you through
the steps.

You are dropped into an IPython shell, so you can have some fun with the hp module.
To get some usage information, use

* hp.help()

If you want to dive into the depths of the code, also try

* help( pyhp.cmd )
* help( pyhp.hpstr )
* help( pyhp.protocol )
* help( pyhp.com.hpusb )

## Examples
``` python
$ ./hp49.py 
XModem Version 1.0
197220 bytes free.
ready.
In [1]: hp.ls()
0010000011000001  DOLIST      17.5  ΣPAR
1000011010011100  DOARRY     175.0  ΣDAT
0000111000100001  DOEXT0    1048.5  ΣPRODAT
1000000010000111  DOLIB    47319.5  stat49pr
0100000101001011  DOLIST      28.0  IOPAR
0011110010011001  DOLIST      74.5  PPAR
1110001101101100  DORRP      358.5  CASDIR

In [2]: hp.get( "ΣPAR", hexdump=True )
48 50 48 50 34 39 2d 43 74 2a c0 94 2f 61 f9 72 93 2f 37 f9 42 21 3e 2b 31 00 00 00 f9 88 8a 00 00 34 50 32 76 16 58 4e 09 78 9f 00 81 f6 00 60 31 17 bf 5d 80 51 75 2d 08 3c 22 55 b0 60 12 8b 0e 24 80 23 05 0b 16 f7 41 15 47 70 41 15 47 51 71 e1 0d 60 41 83 ca 6a e1 05 06 90 41 15 27 fa 19 55 17 f7 fa 1b 55 17 f7 11 18 55 17 f7 70 41 15 47 31 16 54 58 1d eb 10 00 03 1c c5 10 99 10

In [3]: data = hp.get( "PPAR" )

In [4]: hp.cd( "CASDIR" )
Out[4]: True

In [5]: hp.put( "TEST", data )
Out[5]: True

In [6]: hp.ls()
0011110010011001  DOLIST      74.5  TEST
1101110010011111  DOLIST      74.5  PPAR
0011010101101001  DOCOL      149.5  VDIV
1110011100010000  DOINT        6.5  MODULO
0001001110110001  DOLIST      27.5  REALASSUME
0101001100100110  DOSYMB      12.5  PERIOD
1001111000111110  DOIDNT       4.5  VX
1101001011001100  DOREAL      10.5  EPS

In [7]: hp.rm( "TEST" )
Out[7]: True

n [8]: hp.specialchars()
∠ ā ∇ √ ∫ Σ ▶ π ∂ ≤ ≥ ≠ α → ← ↓ ↑ γ δ ε η θ λ ρ σ τ ω Δ Π Ω ■ ∞

In [9]: hp.pushobj( "'∫(0,2*π,SIN(X)/X,X)'" )
Out[9]: True

In [10]: hp.xeq( "EVAL" )
Out[10]: True

In [11]: print hp.popstr()
1.41815157613
```
