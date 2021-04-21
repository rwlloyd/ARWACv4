from evdev import InputDevice, categorize, ecodes

#evdev reference https://python-evdev.readthedocs.io/en/latest/apidoc.html
class eightbitdo():
    def __init__(self, path):
        try:
            self.path = path
            self.controller = InputDevice(self.path)
            print("Connected to: ",self.controller)
            #ev keys (event.code) for buttons
            self.y_btn = 306
            self.x_btn = 307
            self.b_btn = 304
            self.a_btn = 305
            self.right_tr_1 = 309
            self.left_tr_1 = 308
            self.sel_btn = 310
            self.start_btn = 311
            self.dpad_x = 16
            self.dpad_y = 17
            self.left_xy_btn = 312
            self.right_xy_btn = 313
            #ev code for analogue ctrls
            self.left_x = 0
            self.left_y = 1
            self.right_x = 3
            self.right_y = 4
            self.right_tr_2 = 5
            self.left_tr_2 = 2

            self.states = {"left_x":32767
            ,"left_y":32767
            ,"right_x":32767
            ,"right_y":32767
            ,"dpad_x":0
            ,"dpad_y":0
            ,"button_a":0
            ,"button_b":0
            ,"button_x":0
            ,"button_y":0
            ,"trigger_l_1":0
            ,"trigger_l_2":0
            ,"trigger_r_1":0
            ,"trigger_r_2":0
            , "button_select":0
            , "button_start":0
            , "button_left_xy":0
            , "button_right_xy":0
            }
        except:
            print("Controller Failed Init. Check Connection")
            pass

    def readInputs(self):
        events = self.controller.read()
        try: 
            for event in events:
                # if event.type == ecodes.EV_ABS:
                #     #print(event.code)
                    # Analog Sticks
                if event.code == self.left_x and event.type == 3:
                    self.states["left_x"] = event.value
                elif event.code == self.left_y and event.type == 3:
                    self.states["left_y"] = event.value
                elif event.code == self.right_x and event.type == 3:
                    self.states["right_x"] = event.value
                elif event.code == self.right_y and event.type == 3:
                    self.states["right_y"] = event.value
                # D-Pad
                elif event.code == self.dpad_x and event.type == 3:
                    self.states["dpad_x"] = event.value
                elif event.code == self.dpad_y and event.type == 3:
                    self.states["dpad_y"] = event.value
                # #elif event.type == ecodes.EV_KEY:
                # elif event.type == 1:
                #     # Buttons
                elif event.code == self.a_btn and event.type == 1:
                    self.states["button_a"] = event.value
                elif event.code == self.b_btn and event.type == 1:
                    self.states["button_b"] = event.value
                elif event.code == self.x_btn and event.type == 1:
                    self.states["button_x"] = event.value
                elif event.code == self.y_btn and event.type == 1:
                    self.states["button_y"] = event.value
                elif event.code == self.left_tr_1 and event.type == 1:
                    self.states["trigger_l_1"] = event.value
                elif event.code == self.left_tr_2  and event.type == 3:
                    self.states["trigger_l_2"] = event.value
                elif event.code == self.right_tr_1  and event.type == 1:
                    self.states["trigger_r_1"] = event.value
                elif event.code == self.right_tr_2  and event.type == 3:
                    self.states["trigger_r_2"] = event.value
                elif event.code == self.sel_btn  and event.type == 1:
                    self.states["button_select"] = event.value
                elif event.code == self.start_btn  and event.type == 1:
                    self.states["button_start"] = event.value
                elif event.code == self.left_xy_btn  and event.type == 1:
                    self.states["button_left_xy"] = event.value
                elif event.code == self.right_xy_btn  and event.type == 1:
                    self.states["button_right_xy"] = event.value
        except IOError:
            pass
        return self.states

    def printStates(self):
        print(self.states["left_x"], self.states["left_y"],self.states["right_x"],self.states["right_y"]
        ,self.states["dpad_x"],self.states["dpad_y"],self.states["button_a"],self.states["button_b"]
        ,self.states["button_x"],self.states["button_y"],self.states["trigger_l_1"],self.states["trigger_l_2"]
        ,self.states["trigger_r_1"],self.states["trigger_r_2"],self.states["button_select"]
        ,self.states["button_start"],self.states["button_left_xy"],self.states["button_right_xy"])

# mycontroller = eightbitdo()
# while (True):
#    mycontroller.readInputs()
#    mycontroller.printStates()
