from evdev import InputDevice, categorize, ecodes

print("Bluetooth Gamepad 8710 - pad mapping")

#creates object 'gamepad' to store the data
gamepad = InputDevice('/dev/input/event0')

#button code variables (change to suit your device)
aBtn = 304
bBtn = 305
up = 115
down = 114
left = 165
right = 163
playpause = 164
xAxis = 254/2
yAxis = 254/2

#loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            if event.code == aBtn:
                print("A")
            elif event.code == bBtn:
                print("B")
            # elif event.code == playpause:
            #     print("Play/Pause")
            # elif event.code == up:
            #     print("up")
            # elif event.code == down:
            #     print("down")
            # elif event.code == left:
            #     print("left")
            # elif event.code == right:
            #     print("right")
            elif event.code == 17:
                #print("D_v")
                print(event)
            # elif event.code == 16:
            #     print("D_down")
    if event.type == ecodes.EV_ABS:
        # if event.code == 0:
        #     xAxis = event.value
        #     print("l_x: " + xAxis)
        if event.code == 1:
            lyAxis = event.value
            print(lyAxis)
        # if event.code == 2:
        #     xAxis = event.value
        #     print(xAxis)
        if event.code == 3:
            rxAxis = event.value
            print(rxAxis)
        # if event.code == 4:
        #     ryAxis = event.value
        #     print(ryAxis)
