from pynput import keyboard, mouse
from datetime import datetime
from threading import Thread
from time import sleep

# BASIC VARIABLE
createScript = (input("Submit 't' to enable scripts> ") == 't')
recordAction = False
runAction = False
terminate = False
resoMultiplier = float(input("Submit resolution multiplier> "))
defaultRepeat = 100000000
# BASIC VARIABLE
print("\n[F7] to import an action script." if createScript else "", end = '\n')
print("[F8] to start/stop recording actions.", end = '\n')
print("[F9] to start/stop running actions.", end = '\n')
print("[F10] to terminate this program.", end = '\n')
print("[F11] to pause on current action.", end = '\n')
# INPUT MANAGEMENT
mouse_listener = mouse.Listener
mouseController = mouse.Controller()
mouseButton = mouse.Button
key_listener = keyboard.Listener
keyController = keyboard.Controller()
# INPUT MANAGEMENT

# INTERVAL MANAGEMENT 
get_time = datetime.now
defaultWait = 1
prevTime = None
def get_difference():
    global defaultWait
    global prevTime
    global get_time
    curTime = get_time()
    if (prevTime == None):
        prevTime = curTime
        return defaultWait
    diffTime = (curTime - prevTime).total_seconds()
    prevTime = curTime
    return diffTime
def generate_name():
    global get_time
    return "KenEmu-{0}.txt".format(get_time().strftime("%Y-%m-%d-%H-%M-%S-%f"))
# INTERVAL MANAGEMENT
    
# ACTIONS
class Action:
    def __init__(self, interval, command, startSince = 0, repeatFor = defaultRepeat):
        self.action = [ interval, command, startSince, repeatFor ]
        self.defRF = repeatFor
    def get_begin(self):
        return self.action[2]
    def get_repeat(self):
        return self.action[3]
    def get_interval(self):
        return self.action[0]
    def get_command(self):
        return self.action[1]
    def export_action(self, fileName):
        with open(fileName, 'a') as outputFile:
            outputFile.write("[{0},\"{1}\",{2},{3}]\n".format(self.get_interval(), self.get_command(), 
                             self.get_begin(), self.get_repeat()))
            print(".", end = '')
class ActionList:
    def __init__(self):
        self.actionList = []
        self.actionIterator = 0
        self.actionCount = 0
        self.startOfTime = get_time()
        self.elapseTime = 0
    def add_action(self, interval, command, startSince = 0, repeatFor = defaultRepeat):
        self.actionList.append(Action(interval, command, startSince, repeatFor))
        self.actionCount += 1
    def export_actions(self):
        global generate_name
        fileName = generate_name()
        for action in self.actionList:
            action.export_action(fileName)
        print("\nTotal of {0} actions exported to {1}".format(self.actionCount, fileName), end = '\n')
    def import_actions(self):
        try:
            fileName = input("Script name> ")
            print("Reading {0}".format(fileName), end = '\n')
            with open(fileName, 'r') as inputFile:
                for line in inputFile:
                    if not (line == ''):
                        try:
                            data = eval(line)
                            self.add_action(data[0], data[1], data[2], data[3])
                        except:
                            pass
            print("\nImport Success.", end = '\n')
        except:
            print("\nAn error occurred while opening the file.", end = '\n')
    def adj_iterator(self):
        global get_time
        if (self.actionIterator == (self.actionCount - 1)):
            self.reset_iterator()
            self.elapseTime = (get_time() - self.startOfTime).total_seconds()
        else:
            self.actionIterator += 1
    def reset_iterator(self):
        self.actionIterator = 0
    def reset_SOT(self):
        global get_time
        self.startOfTime = get_time()
        self.elapseTime = 0
    def reset_DF(self):
        for action in self.actionList:
            action.action[3] = action.defRF
    def reset_IT(self):
        self.actionList[self.actionIterator].action[3] -= 1
        self.actionIterator = self.actionCount - 1
        self.actionList[self.actionIterator].action[3] += 1
    def run_action(self):
        #print(self.actionIterator)
        #curAction = self.actionList[self.actionIterator]
        if ((self.actionList[self.actionIterator].get_begin() <= self.elapseTime) \
                and (self.actionList[self.actionIterator].get_repeat() >= 1)):
            sleep(self.actionList[self.actionIterator].get_interval())
            #print("repeat:", self.actionList[self.actionIterator].get_repeat(), end = '\n')
            try:
                exec(self.actionList[self.actionIterator].get_command())
                print("\nExecuted Line {0}: \"{1}\"".format(self.actionIterator + 1, self.actionList[self.actionIterator].get_command()), end = '\n')
                print("Remaining: {0}".format(self.actionList[self.actionIterator].get_repeat()), end = '\n')
            except:
                print("\nLine {0}: \"{1}\" could not be executed properly.".format(self.actionIterator + 1, 
                      self.actionList[self.actionIterator].get_command()), end = '\n')
            self.actionList[self.actionIterator].action[3] -= 1
        self.adj_iterator()
actionList = ActionList()
# ACTIONS
        
# FUNCT
class MouseFunct:
    def get_button_name(button):
        global mouseButton
        if (button == mouseButton.left):
            return "mouse.Button.left"
        elif (button == mouseButton.right):
            return "mouse.Button.right"
        else:
            return "mouse.Button.middle"
    def get_pressed_string(pressed):
        return (("mouse.Controller().press") if (pressed) else ("mouse.Controller().release"))
    def get_coord_command(x, y):
        return "mouse.Controller().position = ({0},{1})".format(x, y)
    def get_action_command(button, pressed):
        return "{0}({1})".format(MouseFunct.get_pressed_string(pressed), MouseFunct.get_button_name(button))
    def on_move(x, y):
        pass
    def on_scroll(x, y, dx, dy):
        pass
    def on_click(x, y, button, pressed):
        global createScript
        global recordAction
        global resoMultiplier
        global get_difference
        global actionList
        if (recordAction):
            actionList.add_action(get_difference(), MouseFunct.get_coord_command(x / resoMultiplier, y / resoMultiplier))
            print("Time: {0}; Mouse: ({1},{2}); Command: {3}".format(actionList.actionList[-1].get_interval(), x, y, 
                  actionList.actionList[-1].get_command()), end = '\n')
            sleep(0.001)
            actionList.add_action(get_difference(), MouseFunct.get_action_command(button, pressed))
            print("Time: {0}; Mouse: {1}; Button: {2}; Command: {3}".format(actionList.actionList[-1].get_interval(), 
                  "{0}".format("Pressed" if pressed else "Released"), MouseFunct.get_button_name(button), actionList.actionList[-1].get_command()), end = '\n')
class KeyFunct:
    def reserved_key(key):
        return ((key == keyboard.Key.f7) or (key == keyboard.Key.f8) or (key == keyboard.Key.f9) or (key == keyboard.Key.f10) or (key == keyboard.Key.f11))
    def get_key_name(key):
        return (("keyboard.KeyCode(char = {0})".format(key)) if (len("{0}".format(key)) == 3) else ("keyboard.{0}".format(key)))
    def on_press(key):
        global recordAction
        global actionList
        if ((not KeyFunct.reserved_key(key)) and recordAction):
            actionList.add_action(get_difference(), "keyboard.Controller().press({0})".format(KeyFunct.get_key_name(key)))
            print("Time: {0}; Key: Pressed; Button: {1}; Command: {2}".format(actionList.actionList[-1].get_interval(), 
                  KeyFunct.get_key_name(key), actionList.actionList[-1].get_command()), end = '\n')
    def on_release(key):
        global recordAction
        global actionList
        global runAction
        global terminate
        global createScript
        if (key == keyboard.Key.f7):
            if (createScript):
                actionList.import_actions()
        elif (key == keyboard.Key.f8):
            if (recordAction and createScript):
                actionList.export_actions()
            recordAction = not recordAction
        elif ((key == keyboard.Key.f9) or (key == keyboard.Key.f11)):
            if ((not runAction) and (key == keyboard.Key.f9)):
                actionList.reset_SOT()
            print("Time elapsed: {0}".format(actionList.elapseTime), end = '\n')
            runAction = not runAction
        elif (key == keyboard.Key.f10):
            terminate = True
        elif (recordAction):
            actionList.add_action(get_difference(), "keyboard.Controller().release({0})".format(KeyFunct.get_key_name(key)))
            print("Time: {0}; Key: Released; Button: {1}; Command: {2}".format(actionList.actionList[-1].get_interval(),
                  KeyFunct.get_key_name(key), actionList.actionList[-1].get_command()), end = '\n')
def run_commands():
    global actionList
    global terminate
    global runAction
    while not terminate:
        sleep(0.005)
        if (runAction):
            actionList.run_action()
#FUNCT
MListener = mouse_listener(on_click = MouseFunct.on_click, on_scroll = MouseFunct.on_scroll, on_move = MouseFunct.on_move)
KListener = key_listener(on_press = KeyFunct.on_press, on_release = KeyFunct.on_release)
MListener.start()
KListener.start()
execLoop = Thread(target = run_commands)
execLoop.start()
execLoop.join()
MListener.stop()
KListener.stop()
print("\nProgram Terminated.", end = '\n')

