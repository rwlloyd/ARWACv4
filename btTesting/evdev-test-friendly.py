#import evdev
from evdev import InputDevice, categorize, ecodes
controller = InputDevice('/dev/input/event2')

print(controller)
print(controller.capabilities(verbose=True))



def readInput():
    events = controller.read()
    try: 
        for event in events:
            print(event.code, event.type, event.value)
            #print(event.type, event.code, event.value)
            #print(event.ecode)
    except IOError:
        pass
    #return state


while (True):
    readInput()
