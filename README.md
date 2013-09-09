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
hp.ls()
hp.cmd("M") ; hp.readpacket()
hp.cmd("E", "VERSION") ; hp.sendack() # happens on stack
hp.flush() ; hp.dev.reset() # might help when stuck
```
