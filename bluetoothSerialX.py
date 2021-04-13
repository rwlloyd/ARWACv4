#!/usr/bin/env python3

"""
Current status

steering - working but shit.... everything's sloppy, actuator seems a bit weak. 
tool - working but inverted - needs power connecting too
wheels - fixed
enable - doesn't seem to work yet, but everything is enabled.... fix this first!
Connect ESTOP buttons
"""


import serial
import math
from time import sleep
import eightbitdo as bt
import subprocess as sp

print("    4 Wheel Drive Remote Control for Serial-Curtis Bridge v1.3 and Generic Bluetooth Controller")
print("    Four wheel drive electronic differential with ackermann steering via linear actuator and ancilliary lift")
print("    Usage: Left or Right Trigger = Toggle Enable")
print("    Usage: Left Joystick for forward and reverse motion")
print("    Usage: Right Joystick for steering left and right")
print("    Usage: DPad up/down to raise/lower tool")
print("    Usage: estop enable = either joystick buttons, cancel estop = both bumper buttons")
print("     - Rob Lloyd. 02/2021")

# change to unique MAC address of bluetooth controller
controllerMAC = "E4:17:D8:9A:F7:7B" 

# create an object for the bluetooth control
controller = bt.eightbitdo("/dev/input/event0")

# create an object for the serial port controlling the curtis units
try:
    curtisData = serial.Serial("/dev/ttyUSB1", 115200, timeout=1)
except:
    print("Curtis-Serial Bridge Failed to connect")
    pass

# create an object for the serial port controlling the curtis units
try:
    actData = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
except:
    print("Actuator Controller Failed to connect")
    pass

## Functions -----------------------------------------------------------------------

def rescale(val, in_min, in_max, out_min, out_max):
    """
    Function to mimic the map() function in processing and arduino.
    """
    return out_min + (val - in_min) * ((out_max - out_min) / (in_max - in_min))

def generateCurtisMessage(estopState: bool, enable: bool, v1 , v2, v3, v4):
    """
    Accepts an input of two bools for estop and enable. 
    Then two velocities for right and left wheels between -100 and 100
    """
    # Empty list to fill with our message
    messageToSend = []
    # # # Check the directions of the motors, False (0) = (key switch) forward, True (1) = reverse
    # # # Velocities are scaled from -100 to +100 with 0 (middle of joystick) = no movement
    # # # If vel >= 0 = forward, if vel < 0 backward
    vels = [v1, v2, v3, v4]
    dirs = [False, False, False, False]
    for i in range(len(vels)):
        if vels[i] >= 0:
            dirs[i] = False
        elif vels[i] < 0:
            dirs[i] = True


    # Check to see if we're allowed to move. estop and enable
    if estopState or not enable:
        for i in vels:
            vels[i] = 0

    # # Build the message. converting everything into positive integers
    # # Message is 10 bits [estopState, enable, motor 0 direction, motor 0 velocity, motor 1 direction, motor 1 velocity, motor 2 direction, motor 2 velocity, motor 3 direction, motor 3 velocity]
    # # motor numbering:
    # #  Front    
    # # 0  1
    # # 2  3
    # # Back (key end)
    messageToSend.append(int(estopState))
    messageToSend.append(int(enable))
    messageToSend.append(int(dirs[0]))
    messageToSend.append(abs(int(vels[0])))
    messageToSend.append(int(dirs[1]))
    messageToSend.append(abs(int(vels[1])))
    messageToSend.append(int(dirs[2]))
    messageToSend.append(abs(int(vels[2])))
    messageToSend.append(int(dirs[3]))
    messageToSend.append(abs(int(vels[3])))
    
    print("Sending: %s" % str(messageToSend))
    return messageToSend

def generateActMessage(estopState:bool, enable: bool, height, angle):
    """
    Accepts an input of two ints between -100 and 100
    """
    # Empty list to fill with our message
    messageToSend = []
    messageToSend.append(int(estopState))
    messageToSend.append(int(enable))
    messageToSend.append(int(height))
    messageToSend.append(int(angle))
    
    print("Sending: %s" % str(messageToSend))
    return messageToSend

# def send(message_in, conn, actData, curtisData):
#     """
#     Function to send a message_in made of ints, convert them to bytes and then send them over a serial port
#     message length, 10 bytes.
#     This is the one modified by pete. probably better but confusing and threw errors
#
#     """
#     if conn == 0:
#         messageLength = 10
#         message = []
#         for i in range(messageLength):
#             try:
#                 message.append(message_in[i].to_bytes(1, 'little'))
#             except:
#                 print(i, [j for j in message_in])
#         for i in range(messageLength):
#             curtisData.write(message[i])
#     elif conn == 1:
#         messageLength = 4
#         message = []
#         for i in range(messageLength):
#             message.append(message_in[i].to_bytes(1, 'little'))
#         for i in range(messageLength):
#             actData.write(message[i])
#     #print(message)

def send(message_in, conn):
    """
    Function to send a message_in made of ints, convert them to bytes and then send them over a serial port
    message length, 10 bytes.
    """
    if conn == 0:
        messageLength = 10
        message = []
        for i in range(0, messageLength):
            message.append(message_in[i].to_bytes(1, 'little'))
        for i in range(0, messageLength):
            curtisData.write(message[i])
    elif conn == 1:
        messageLength = 4
        message = []
        for i in range(0, messageLength):
            message.append(message_in[i].to_bytes(1, 'little'))
        for i in range(0, messageLength):
            actData.write(message[i])
    #print(message)

def receive(message):
    """
    Function to read whatever is presented to the serial port and print it to the console.
    Note: For future use: Currently not used in this code.
    """
    messageLength = len(message)
    last_message = []
    try:
        while arduinoData.in_waiting > 0:
            for i in range(0, messageLength):
                last_message.append(int.from_bytes(arduinoData.read(), "little"))
        #print("GOT: ", last_message)
        return last_message
    except:
        print("Failed to receive serial message")
        pass

def isEnabled():
    """ 
    Function to handle enable and estop states. it was geeting annoying to look at.
    """
    # to reset after estop left and right bumper buttons - press together to cancel estop
    if newStates["trigger_l_2"] == 1 and newStates["trigger_r_2"] == 0:
        estopState = False

    # left and right joystick buttons trigger estop
    if newStates["button_left_xy"] == 1 or newStates["button_right_xy"] == 0:
        estopState = True #this shouldnt reset. but it does
    
    if estopState == True:
        enable = False #ok
    print(newStates["trigger_l_1"])
    # dead mans switch left or right trigger button
    if newStates["trigger_l_1"] == 1 or newStates["trigger_r_1"] == 1:
        if estopState == False:
            enable = True
    else:
        enable = False

    return enable

# def calculateVelocities(vehicleLength: float, vehicleWidth: float, velocity, angle):
#     # Appl Sci 2017, 7, 74
#     if angle > 0: #turn Left
#         R = vehicleLength/math.tan(angle)
#         v1 = velocity*(1-(vehicleWidth/R))
#         v2 = velocity*(1+(vehicleWidth/R))
#         v3 = velocity*((R-(vehicleWidth/2)/R))
#         v4 = velocity*((R+(vehicleWidth/2)/R))
#     elif angle < 0: #turn Right
#         R = vehicleLength/math.tan(angle)
#         v1 = velocity*(1+(vehicleWidth/R))
#         v2 = velocity*(1-(vehicleWidth/R))
#         v3 = velocity*((R+(vehicleWidth/2)/R))
#         v4 = velocity*((R-(vehicleWidth/2)/R))
#     elif angle < 0.001 and angle > -0.001:
#         angle = 0
#         v1 = velocity
#         v2 = velocity
#         v3 = velocity
#         v4 = velocity

#     if sum([v1, v2, v3, v4]) < 4.00:
#         return v1, v2, v3, v4
#     else:
#         raise ValueError(f'Velocity value incorrect: {v1}, {v2}, {v3}, {v4} Angle {angle} Sum: {sum([v1, v2, v3, v4])}')

def calculateSimpleVelocities(inputVel: float):
    velocity = rescale(inputVel, 0, 255, -100, 100)
    v1 = velocity
    v2 = velocity
    v3 = velocity
    v4 = velocity

    return v1, v2, v3, v4

def limit(num, minimum=1, maximum=255):
  """Limits input 'num' between minimum and maximum values.
  Default minimum value is 1 and maximum value is 255."""
  return max(min(num, maximum), minimum)


def main():

    ## Describe the critical dimensions of the vehicle 4WD
    vehicleWidth = 1.5
    vehicleLength = 2.0

    # # change to unique MAC address of bluetooth controller
    # controllerMAC = "E4:17:D8:9A:F7:7B" 

    # # create an object for the bluetooth control
    # controller = bt.eightbitdo("/dev/input/event0")

    # # create an object for the serial port controlling the curtis units
    # try:
    #     curtisData = serial.Serial("/dev/ttyUSB1", 115200, timeout=1)
    # except:
    #     print("Curtis-Serial Bridge Failed to connect")
    #     pass

    # # create an object for the serial port controlling the curtis units
    # try:
    #     actData = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
    # except:
    #     print("Actuator Controller Failed to connect")
    #     pass

    # So the direction in general can be reversed
    direction = False

    # Initialise  values for enable and estop
    estopState = False
    enable = False
    left_y = 32768
    right_x = 32768
    toolPos = 128

    curtisMessage = []  # Seems to be necessary to have a placeholder for the message here
    actMessage = []
    last_message = []

    # Main Loop
    while True:
        stdoutdata = sp.getoutput("hcitool con") # hcitool check status of bluetooth devices

        # check bluetooth controller is connected if not then estop
        if controllerMAC not in stdoutdata.split():
            print("Bluetooth device is not connected")
            enable = False
            estopState = True
        else:
            enable = True

        # Check to see if there is new input from the controller
        try:
            newStates = controller.readInputs()
        except IOError:
            pass

        if newStates["dpad_y"] == -1:
            toolPos += 10
        elif newStates["dpad_y"] == 1:
            toolPos -= 10
        # Rescal the tool position. 100 is full up, 0 is full down. #'###CHECK THIS    
        commandTool = rescale(toolPos, 255, 0, 100, 0)
        
        # Check the enable state via the function
        if isEnabled: 
            # Calculate the final inputs rescaling the absolute value to between -100 and 100
            commandVel = rescale(newStates["left_y"], 65535, 0, 0, 255)
            commandAngle = rescale(newStates["right_x"], 0, 65535, 0, 255)
            # the angle needs to be in relatively real numbers
            # cmdVel = rescale(commandVel, 0, 255, -1, 1)
            # cmdAng = rescale(commandAngle, 0, 255, -1, 1)
            #print(cmdAng)
            #v1, v2, v3, v4 = calculateVelocities(vehicleLength, vehicleWidth ,cmdVel, cmdAng)
            v1, v2, v3, v4 = calculateSimpleVelocities(commandVel)
            #print(v1,v2,v3,v4)

        else:
            commandVel = 0
            commandAngle = rescale(newStates["right_x"], 0, 65535,0, 255)
            #cmdAng = rescale(commandAngle, 0, 255, -1, 1)
            #v1, v2, v3, v4 = calculateVelocities(vehicleLength, vehicleWidth, cmdAng, 0)
            v1, v2, v3, v4 = calculateSimpleVelocities(commandVel)

        # Build a new message with the correct sequence for the curtis Arduino
        newCurtisMessage = generateCurtisMessage(estopState, enable, v1, v2, v3, v4)
        print(newCurtisMessage)
        # Build new message for the actuators
        #print(enable, commandTool, commandAngle)
        newActMessage = generateActMessage(estopState, enable, commandTool, commandAngle)
        # Send the new message to the actuators and curtis arduinos
        send(newActMessage, 1)
        send(newCurtisMessage, 0)
        # send(newActMessage, 1, actData, curtisData)
        # send(newCurtisMessage, 0, actData, curtisData)
        # So that we don't keep spamming the Arduino....
        sleep(0.1)


if __name__ == "__main__":
    main()
