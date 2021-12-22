#!/usr/bin/env python3

"""
Current status

steering - working 
tool - working 
wheels - working
enable - not working, but everything is enabled....
Connect ESTOP buttons
"""


import serial
import math
from time import sleep
import eightbitdo as bt
import subprocess as sp



print("    Transaxle Drive Remote Control for Serial-Curtis Bridge v1.3 and Generic Bluetooth Controller")
print("    Transaxle Drive with ackermann steering via linear actuator and ancilliary lift")
print("    Usage: Left or Right Trigger = Toggle Enable")
print("    Usage: Left Joystick for forward and reverse motion")
print("    Usage: Right Joystick for steering left and right")
print("    Usage: DPad up/down to raise/lower tool")
print("    Usage: estop enable = either joystick buttons, cancel estop = both bumper buttons")
print("     - Rob Lloyd. 02/2021")

# change to unique MAC address of bluetooth controller
controllerMAC = "E4:17:D8:9A:F7:7B" 

sleep(5)

# create an object for the bluetooth control
try:
    controller = bt.eightbitdo("/dev/input/event0")
except:
    print("Failed to create controller object")
    pass
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
        for i in range(len(vels)):
            vels[i] = int(0)

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
    
    print("Sending MOT: %s" % str(messageToSend))
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
    
    print("Sending ACT: %s" % str(messageToSend))
    return messageToSend

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

def socket_receive_camera():
     ############################################
    # socket communication - dom
    # Check to see if there is new input from the external, TX2
    msg = {}
    try:

        msg = m_CJetCom.RasReceive_data()       
        
        print('Recieved data: ', msg)
        return msg        
        

        """
        msg = m_CJetCom.RasReceive()
        if msg[0]['L']==1:
            return msg[0]['L']
        elif msg[0]['R']==1:
            return msg[0]['L']

        else:
            return msg[0]['L']        

        print('Recieved data: ', msg[0]['L'])
        """
        # plt.pause(0.25)
    except IOError:
        return msg.clear() # error so return empty message
        pass
    ############################################
    ############################################

def isEnabled(newStates, enable, estopState):
    """ 
    Function to handle enable and estop states. it was getting annoying to look at.
    """
    # to reset after estop left and right bumper buttons - press together to cancel estop
    if newStates["trigger_l_1"] == 1 and newStates["trigger_r_1"] == 1:
        estopState = False

    # left and right joystick buttons trigger estop
    if newStates["button_left_xy"] == 1 or newStates["button_right_xy"] == 1:
        estopState = True 
    
    # Obviously, if we're in an estop state, things shouldnt be enabled
    if estopState == True:
        enable = False 

    # dead mans switch left or right trigger button
    if newStates["trigger_l_2"] >= 1 or newStates["trigger_r_2"] >= 1:
        if estopState == False:
            enable = True
    else:
        enable = False

    return enable

def calculateSimpleVelocities(inputVel: float):
    velocity = rescale(inputVel, 0, 255, -100, 100) #### THIS IS FUDGED
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

    # So the global direction of the vehicle can be reversed
    direction = False               ###### THIS IS OLD. Check it does something

    # Initialise  values for enable and estop
    estopState = False
    enable = False
    left_y = 32768
    right_x = 32768                 # Steering input centrepoint
    toolPos = 255                   # Default tool position. should be raised position
    toolStep = 10                   # Size of steps between positions
    # Seems to be necessary to have a placeholder for the message here
    curtisMessage = []  
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

        # Check to see if there is new input from the controller. Most of the time there isn't, so handle the error
        try:
            newStates = controller.readInputs()
        except IOError:
            pass

        #Check Enables and ESTOP
        enable = isEnabled(newStates, enable, estopState)
        
        # Handle the input for the raising and lowering of the tool. Don't let the tool go too high or low (0-255)
        if newStates["dpad_y"] == -1 and toolPos < 255 - toolStep:
            # move up
            toolPos += toolStep 
        elif newStates["dpad_y"] == 1 and toolPos > toolStep:
            #move down
            toolPos += -1 * toolStep 
        else:
            #print("Tool it too close to its limits")
            a = 1
                       
        commandTool = rescale(toolPos, 255, 0, 100, 0) # Rescale the tool position. 100 is full up, 0 is full down. 

        ## ok, lets convert this to angles
        # Imperically, steering range is approx 54 deg
        degpertick = 54 / 125
        tickperdeg = 125 / 54

        # Check the enable state via the function
        if isEnabled:  
            if newStates["button_b"] == 1: # if enabled and B button pressed enter row rollowing mode
                try:
                    message = socket_receive_camera()
                    print("row following mode")
                    if bool(message): # if message is not empty drive, else stop
                        commandAngle = rescale(float(message), -1, 1, 65, 190) # JC 14/04/21 65 to 190 safe wheel angles
                        v1 = v2 = v3 = v4 = 50
                    else: # no message so stop   
                        commandAngle = 127
                        v1 = v2 = v3 = v4 = 0
                except:
                    print("Didn't connect to remote computer.")
                    pass
            else:
                #print("manual mode")
                commandAngle = rescale(newStates["right_x"], 0, 65535, 65, 190) # JC 14/04/21 65 to 190 safe wheel angles
                # Calculate the final inputs rescaling the absolute value to between -100 and 100
                commandVel = rescale(newStates["left_y"], 65535, 0, 0, 255)                   
                
                ###### THIS IS THE STUPID KINEMATIC MODEL ########
                v1, v2, v3, v4 = calculateSimpleVelocities(commandVel)
                #print(v1,v2,v3,v4)

        else: # not enabled so stop
            commandAngle = 127
            commandVel = 0
            #v1, v2, v3, v4 = calculateVelocities(vehicleLength, vehicleWidth, cmdAng, 0)
            v1, v2, v3, v4 = calculateSimpleVelocities(commandVel)
   
        newCurtisMessage = generateCurtisMessage(estopState, enable, v1, v2, v3, v4)        # Build a new message with the correct sequence for the curtis Arduino
        #print(newCurtisMessage)
        #print(enable, commandTool, commandAngle)
        newActMessage = generateActMessage(estopState, enable, commandTool, commandAngle)   # Build new message for the actuators    
        send(newActMessage, 1)                                                              # Send the new message to the actuators and curtis arduinos
        send(newCurtisMessage, 0)
        
        sleep(0.2)                                                                          # So that we don't keep spamming the Arduino....


if __name__ == "__main__":
    main()
