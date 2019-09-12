#!/usr/bin/env python
# coding: utf-8

"""
Created by Eric Reuter, 2019

The script controls the Hyundai Kona EV VESS.

If run without arguments, it will increment speed from 0 kmh to 32 kmh and then
terminate, though the VESS will stop repsonding at 30 kmh.

If a speed is specificed as the first argument, it will operate at that speed
indefinitely.  Example:

~$python3 vess.py 12

If an argument of 'r' is included, it will behave as above, but with the backup
tone.  Examples:

~$python3 vess.py r
~$python3 vess.py 12 r

"""

from __future__ import print_function

import can
import time
import sys

def vess():

# You may have to change your CAN interface from can0 to whatever
    bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)

# Pardon the crude argsparsing.

# Determine whether user has defined a speed
    try:
        if sys.argv[1].isdigit:
            constSpeed = int(sys.argv[1])
            userSpeed = True
        else:
            userSpeed = False
    except:
        userSpeed = False

# Determine whether user has set reverse
    try:
        if (sys.argv[1] == 'r') or (sys.argv[2] == 'r'):
            gear = 0b00111000
        else: gear = 0b00101000
    except:
        gear = 0b00101000


    if userSpeed:
        speed = constSpeed * 256 # Speed is a a 16-bit value, kmh * 256
    else:
         speed = 0x00

    while speed < 8192:  # VESS doesn't respond above 30 kmh (8192 = 32 kmh)

        speedLSB = speed & 0x00FF # CAN data field is in 1-byte chunks
        speedMSB = speed >> 8     # This splits up the 16-bit value

        msg = can.Message(arbitration_id=0x524,
                          data=[0x60, 0x01, speedMSB, speedLSB, 0x5A, 0x01, 0xC0, 0x02],
                          is_extended_id=False)
        try:
            bus.send(msg)
        except can.CanError:
            print("Message 0x524 NOT sent")

        time.sleep(0.020)

        msg = can.Message(arbitration_id=0x200,
                          data=[0x00, gear, 0x00, 0x10, 0x00, 0x3B, 0xD0, 0x00],
                          is_extended_id=False)
        try:
            bus.send(msg)
        except can.CanError:
            print("Message 0x200 NOT sent")

        time.sleep(.020)

        if userSpeed == False: # If user hasn't defined speed, increment
            speed +=32
        print(speed/256) # print speed in kmh


if __name__ == '__main__':
    vess()
