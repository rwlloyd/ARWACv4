from evdev import InputDevice, categorize, ecodes
controller = InputDevice('/dev/input/event0')

print(controller)



def readInput():
    events = controller.read()
    try: 
        for event in events:
            print(event)
    except IOError:
        pass
    #return state


while (True):
    readInput()