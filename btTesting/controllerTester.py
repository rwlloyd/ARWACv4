#!/usr/bin/env python3

"""
This is a script to test the bluetooth controller: 8BitDo SN30+Pro
"""

import eightbitdo as bt

print("    4 Wheel Drive Remote Control for Serial-Curtis Bridge v1.3 and Generic Bluetooth Controller")


# change to unique MAC address of bluetooth controller
controllerMAC = "E4:17:D8:9A:F7:7B" 

# create an object for the bluetooth control
controller = bt.eightbitdo("/dev/input/event2")

def main():

    while True:
        # Check to see if there is new input from the controller
        try:
            newStates = controller.readInputs()
            controller.printStates()
        except IOError:
            pass
        
if __name__ == "__main__":
    main()
