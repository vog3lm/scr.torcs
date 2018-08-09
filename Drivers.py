import logging, math

def get(name,modus):
    driver = None
    logging.info('try to get %s driver'%name) 
    if('keyboard' == name):driver = KeyboardDriver().create()
    elif('gamepad' == name):driver = GamepadDriver().create()
    elif('default' == name):driver = DefaultDriver()
    else: # search in directory
        stopper = False

        from glob import glob
        files = glob('%s.py'%name)
        if 0 < len(files):
            from pydoc import locate
            driver = check(locate('%s'%(name)),modus)
            stopper = True

        if not stopper:
            from sys import modules
            from inspect import getmembers, isclass
            for n, o in getmembers(modules[__name__],isclass):
                if n == name:
                    driver = check(o(),modus)
                    stopper = True
                    break

    if(driver):
        return driver
    else:
        logging.info('%s driver not found. use default driver instead.'%name)
        return DefaultDriver()

def check(driver,modus):
    errors = []
    if not hasattr(driver,'name'):
        errors.append('name not found')
    if not hasattr(driver,'angles'):
        errors.append('angles not found')

    if 'extended' == modus:
        if not hasattr(driver,'accelerate'):
            errors.append('no acceleration method found, extended mode requires accelerate(sensors)')
        if not hasattr(driver,'brake'):
            errors.append('no braking method found, extended mode requires brake(sensors)')
        if not hasattr(driver,'steer'):
            errors.append('no steering method found, extended mode requires steer(sensors)')
        if not hasattr(driver,'shift'):
            errors.append('no shifting method found, extended mode requires shift(sensors)')
        if not hasattr(driver,'focus'):
            errors.append('no focus method found, extended mode requires focus(sensors)')  
        if not hasattr(driver,'meta'):
            errors.append('no meta method found, extended mode requires meta(sensors)')
    else:
        if not hasattr(driver,'drive'):
            errors.append('no driving method found')


    if 0 < len(errors):
        logging.error('driver error. %s'%' '.join(errors))
        return None
    return driver

# SimpleExponentialFunctionDriver
class DefaultDriver(object):
    def __init__(self):
        self.name = 'default-driver'
        self.angles = ['-90','-75','-60','-45','-30','-20','-15','-10','-5','0','5','10','15','20','30','45','60','75','90'] # len = 19

    # available sensors
        # focus...........[]
        # pitch...........[]
        # distFromStart...[]....in dieser runde zurueckgelegter weg bezogen auf start ziel linie
        # rpm.............[0,++]....motordrehzahl in umdrehungen pro minute
        # opponents.......[]....abstand zu gegner in richtung der initial winkel o[0] 90 links o[9] 0 o[18] 90 rechts
        # angle...........[-pi,+pi].winkel zur fahrbahn mittellinie
        # trackPos........[-1,1]....abstand zur fahrbahnmitte, -+200 wenn raus
        # distRaced.......[]....gesamte zurueckgelegte strecke
        # yaw.............[]....
        # damage..........[]....aktueller schaden am auto
        # curLapTime......[]....aktuelle rundenzeit
        # fuel............[]....aktuelle menge sprit im tank
        # roll............[]....steigung der fahrban ?
        # speedGlobalX....[]....
        # speedGlobalY....[]....
        # gear............[-1,6].....aktueller gang
        # track...........[-1,+1]....abstand zum fahrbahn rand in richtung der initial winkel track[0] 90 links track[9] 0 track[18] 90 rechts
        # wheelSpinVel....[0,++].....reifen drehgeschwindigketi
        # speedX..........[--,++]....geschwindikeit vorwaerts rueckwarts
        # speedY..........[--,++]....geschwindikeit links rechts
        # speedZ..........[--,++]....geschwindikeit rauf runter
        # racePos.........[]....platzierun im fahrerfeld
        # lastLapTime.....[]....letzte rundenzeit
        # y...............[]....
        # x...............[]....
        # z...............abstand von der fahrbahn nach oben
    def drive(self,sensors):
        abstandMitte = float(sensors.get('trackPos')[0])
        speedx = float(sensors['speedX'][0])
        steer = 0
        accel = 0.3
        if 0 > abstandMitte: # -1 = rechter rand
            steer = self.steering(abstandMitte)
        elif 0 < abstandMitte: # 1 = linker rand rechts lenken
            steer = self.steering(abstandMitte)
        return {'accel':accel
               ,'brake':0
               ,'steer':steer
               ,'gear':self.shifter(int(sensors.get('gear')[0]),float(sensors.get('rpm')[0]))
               ,'clutch':0
               ,'focus':0.0
               ,'meta':0}

    def steering(self,abstand):
    	return  -math.exp(-abstand*abstand)+1

    def shifter(self,gear,rpm):
    	if 0 == gear:
    		return 1
        if 8000 < rpm:
            return gear+1
        elif 8000 < rpm and 1000 < rmp:
            return gear-1
        elif 0 > rpm:
            return 1
        else:
            return gear

class KeyboardDriver(object):
    def __init__(self):
        self.name = 'keyboard-driver'
        self.angles = ['-90','-75','-60','-45','-30','-20','-15','-10','-5','0','5','10','15','20','30','45','60','75','90'] # len = 19
        self.keymap = {}
        self.keys = []
        self.thread = None
        self.running = False
        self.state = {'accel':0,'brake':0,'steer':0,'gear':0,'clutch':0,'focus':0.0,'meta':0}

    def create(self):
        from pynput.keyboard import Controller, Listener, Key, KeyCode
        Controller()
        self.keymap = {Key.left:self.steer_left
                      ,Key.up:self.accelerator
                      ,Key.right:self.steer_right
                      ,Key.down:self.dummy
                      ,Key.space:self.braker
                      ,'w':self.shift_up
                      ,'s':self.shift_down}
        self.keys = self.keymap.keys()
        self.thread = Listener(on_press=self.press,on_release=self.release)
        self.running = True
        self.thread.start()
        #self.thread.join()
        return self

    # available keys in Key
        # ,'f1','f10','f11','f12','f13','f14','f15','f16','f17','f18','f19','f2','f20','f3','f4','f5','f6','f7','f8','f9'
        # ,'alt_gr','alt_l','alt_r','backspace','caps_lock','cmd','cmd_r' ,'ctrl','ctrl_r','delete','end','enter','esc'
        # ,'home','insert','menu','num_lock','page_down','page_up','pause','print_screen','scroll_lock','shift','shift_r','space','tab'
        # ,'left','right','down','up','space'
        # ,'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'
        # ,'a,'b,'c,'d,'e,'f,'g,'h,'i,'j,'k,'l,'m,'n,'o,'p,'q,'r,'s,'t,'u,'v,'w,'x,'y,'z'
    def press(self,key):
        if key in self.keys:
            self.keymap.get(key)(True)
        elif hasattr(key,'char'):
            if(key.char in self.keys):
                self.keymap.get(key.char)(True)            
        return self.running

    def release(self,key):
        if key in self.keys:
            self.keymap.get(key)(False)
        elif hasattr(key,'char'):
            if(key.char in self.keys):
                self.keymap.get(key.char)(False)  
        return self.running

    def kill(self,data=[]):
        self.running = False
        return self

    def accelerator(self,pressed):
        if(pressed):
            self.state['accel'] = 1
        else:
            self.state['accel'] = 0

    def braker(self,pressed):
        if(pressed):
            self.state['brake'] = 1
        else:
            self.state['brake'] = 0

    def steer_left(self,pressed):
        if(pressed):
            self.state['steer'] = 1
        else:
            self.state['steer'] = 0

    def steer_right(self,pressed):
        if(pressed):
            self.state['steer'] = -1
        else:
            self.state['steer'] = 0

    def shift_up(self,pressed):
        self.state['gear'] = self.state['gear']+1

    def shift_down(self,pressed):
        self.state['gear'] = self.state['gear']-1

    def dummy(self,pressed):
        print 'dummy'

class GamepadDriver(object):
    def __init__(self):
        self.args = {'lib':'inputs'}
        self.name = 'gamepad-driver'
        self.angles = ['-90','-75','-60','-45','-30','-20','-15','-10','-5','0','5','10','15','20','30','45','60','75','90'] # len = 19
        self.keymap = {}
        self.keys = []
        self.thread = None
        self.running = False
        self.interfaces = [self]
        self.state = {'accel':0,'brake':0,'steer':0,'gear':0,'clutch':0,'focus':0.0,'meta':0}

    def create(self):
        self.keymap = {'BTN_TL':self.shoot
                      ,'BTN_TR':self.shoot
                      ,'ABS_GAS':self.accelerator
                      ,'ABS_BRAKE':self.braker
                      ,'ABS_Z':self.steering
                      ,'ABS_HAT0Y':self.shifter}
        self.keys = self.keymap.keys()
        from threading import Thread
        self.thread = Thread(target=self.inputs)
        # modus = self.args.get('lib') # support different libs
        # if 'inputs' == modus:
        #     self.thread = Thread(target=self.inputs)
        # elif 'pygame' == modus:
        #     self.thread = Thread(target=self.pygame)
        self.thread.setDaemon(True) # self.args.get('deamon')
        self.thread.start()
        return self

    def inputs(self):
        from inputs import get_gamepad, devices
        if 0 == len(devices.gamepads):
            logging.error('inputs found no gamepads. no driver available')
            return
        self.running = True
        while self.running:
            events = get_gamepad()
            for event in events:
                # stick actions
                    # ABS_X = left x [0,128,255] left to right
                    # ABS_Y = left y [0,128,255] up to down
                    # ABS_Z = right x [0,128,255] left to right
                    # ABS_RZ = right y [0,128,255] up to down
                # hat actions
                    # ABS_HAT0X == cross x [-1,1] left, right
                    # ABS_HAT0Y == cross y [-1,1] up, down
                # button actions
                    # BTN_SOUTH == a
                    # BTN_EAST == b
                    # BTN_NORTH == x
                    # BTN_WEST == y
                    # BTN_TL == l1 [0,1]
                    # BTN_TR == r1
                    # BTN_TL2 == l2b [0,1]
                    # BTN_TR2 == r2b [0,1]
                    # ABS_BRAKE == l2m [0,255]
                    # ABS_GAS == r2m [0,255]
                    # BTN_THUMBL == l3 [0,1]
                    # BTN_THUMBR == r3 [0,1]
                    # ABS_SELECT == select
                    # ABS_START == start
                self.running = self.handler(event.code,event.state)

    # pygame example keymap
        # self.keymap = {100:self.shoot # a
        #               ,109:self.accelerator # r2
        #               ,108:self.braker # l2
        #               ,72:self.steering
        #               ,93:self.shift_up
        #               ,92:self.shift_down}
    def pygame(self): # obsolete, lags maybe due to graphical stuff needed
        from os import environ
        environ["SDL_VIDEODRIVER"] = "dummy" # no window needed
        from pygame import init, joystick, display
        init()
        display.set_mode((1,1)) # starts a mini widow
        joystick.init()
        count = joystick.get_count()
        for jno in range(0,count): # initialize them all
            js = joystick.Joystick(jno)
            js.init()
        # assign to multi player interfaces
        from pygame.event import get
        from pygame.locals import JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP, QUIT
        self.running = True
        while self.running:
            for event in get():
                if QUIT == event.type:
                    self.kill()
                elif hasattr(event,'joy'): # not a gamepad
                    interface = self.interfaces[event.joy]
                    # stick actions
                        # 0 == left stick x
                        # 1 == left stick y
                        # 2 == right stick x
                        # 3 == right stick y
                        # 5 == l2m
                        # 4 == r2m
                    if JOYAXISMOTION == event.type: # 7
                        self.running = interface.handler(event.type*10+event.axis,event.value)
                    # cross actions
                        # (-1,0) == left
                        # ( 1,0) == right
                        # (0, 1) == up
                        # (0,-1) == down
                    elif JOYHATMOTION == event.type: # 9
                        if((-1,0)== event.value):self.running = interface.handler(90,1)
                        elif((1,0)== event.value):self.running = interface.handler(91,1)
                        elif((0,-1)== event.value):self.running = interface.handler(92,1)
                        elif((0,1)== event.value):self.running = interface.handler(93,1)
                        else:self.running = interface.handler(94,0)
                    # button actions
                        # 0 == a
                        # 1 == b
                        # 3 == x
                        # 4 == y
                        # 6 == l1
                        # 7 == r1
                        # 8 == l2b
                        # 9 == r2b
                        # 10 == select
                        # 11 == start
                        # 13 == l3
                        # 14 == r3
                    elif JOYBUTTONUP == event.type: # 11 no value !
                        self.running = interface.handler(100+event.button,0)
                    elif JOYBUTTONDOWN == event.type: # 10 no value !
                        self.running = interface.handler(100+event.button,1)
        self.display.quit()

    def kill(self,data=[]):
        self.running = False
        return self

    def handler(self,key,value):
        if key in self.keys:
            self.keymap.get(key)(value)
        return self.running

    def accelerator(self,value):
        self.state['accel'] = float(value)/255

    def braker(self,value):
        self.state['brake'] = float(value)/255

    def steering(self,value):
        self.state['steer'] = -float(value-128)/128

    def shifter(self,value):
        self.state['gear'] = self.state['gear']-value

    def shoot(self,value):
        if(value):
            print 'shoot'