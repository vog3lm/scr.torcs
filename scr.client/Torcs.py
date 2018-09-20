import logging

class TorcsException(Exception):
    pass

class TorcsProcessor(object):
    def __init__(self):
        self.args = {'emitter':None,'publish':False,'modus':'simple','driver':None}
        self.name = 'torcs-default'
        self.emitter = None
        self.thread = None
        self.modus = self.simple
        self.driver = None
        self.publish = False

    def decorate(self,arguments):
        from Util import decorate
        return decorate(self,arguments)

    def create(self):
        self.emitter = self.args.get('emitter')
        if None == self.emitter:
            logging.error('no event dispatcher set')
            return self
        return self
    
    def start(self):
        from Drivers import get
        self.driver = get(self.args.get('driver'),self.args.get('modus'))
        if self.args.get('publish'):
            from threading import Thread
            self.thread = Thread(target=self.publish)
        modus = self.args.get('modus')
        if 'extended' == modus:
            self.modus = self.extended
        elif 'human' == modus:
            self.modus = self.human
        else:
            self.modus = self.simple
        self.publish = self.args.get('publish')
        logging.info('torcs-processor runs in %s mode with %s driver'%(modus,self.driver.name))

    def initialize(self,port):
        return 'SCR-%s(init %s)'%(port,' '.join(self.driver.angles))

    # income = (angle -0.00547808)(curLapTime 2.424)(damage 0)(distFromStart 5759.1)(distRaced 0)(fuel 94)(gear 1)(lastLapTime 0)
        #      (opponents 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200)
        #      (racePos 1)(rpm 942.478)(speedX -0.0156955)(speedY 0.0223032)(speedZ 0.000104696)
        #      (track 7.33362 7.57994 8.43488 10.29 14.418 20.6779 26.566 37.154 62.5649 200 64.6741 23.2032 14.7667 10.9974 7.43192 5.22011 4.24884 3.80188 3.6665)
        #      (trackPos -0.333363)(wheelSpinVel 1.72549 -1.37321 3.32057 -2.73145)(z 0.345255)(focus -1 -1 -1 -1 -1)(x 602.857)(y 1167.06)(roll -3.22103e-07)
        #      (pitch 0.00539061)(yaw 0.0390692)(speedGlobalX -0.00459876)(speedGlobalY 0.00602011)
    # output = (accel 0.1)(brake 0.0)(gear 1)(steer 0.0)(clutch 0)(focus 0.0)(meta 0)      
    def process(self,message):
        pos = 1
        sensors = {}
        while len(message) > pos:
            idx = message.find(')',pos)
            tmp = message[pos:idx].split(' ')
            sensors[tmp[0]] = tmp[1:]
            pos = idx+2
        if self.publish:
            self.emitter.threaded('publish-sensors',sensors)
        # normalize values int|float|angle|spin
            #    angle = angle * 180 / math.pi (halber kreis)
            #    speedX = speedX * 1000 / 3600 (mps nach kmh)
            #    speedY = speedY * 1000 / 3600
            #    speedZ = speedZ * 1000 / 3600
            #    wheelSpinVel = wheelSpinVel * 180 / math.pi (grad pre radiant)
        actions = self.modus(sensors)
        if self.publish:
            self.emitter.threaded('publish-actions',actions)
        message = ''
        for action in actions.keys():
            message = '%s(%s %s)'%(message,action,actions[action])
        # validate actions
            #  0 <= accel <= 1 and float
            #  0 <= brake <= 1 and float
            # -1 <= steer <= 1 and float
            # -90 <= focus <= 90 and float
            #  0 <= clutch <= and float
            #  0 <= gear <= 6 and int
            #  ? <= meta <= ? and int
        return message

    def simple(self,sensors):
        return self.driver.drive(sensors)

    def extended(self,sensors):
        return {'accel':self.driver.accelerate(sensors)
               ,'brake':self.driver.brake(sensors)
               ,'steer':self.driver.steer(sensors)
               ,'clutch':self.driver.shift(sensors)
               ,'focus':self.driver.focus(sensors)
               ,'meta':self.driver.meta(sensors)}

    def human(self,sensors):
        return self.driver.state

    def network(self,data={}): # drive with netowrk events
        message = data.get('sensors')
        actions = self.process(message)
        data.get('promise')(actions)

    def publish(self,sensors,actions):
        # check changed values
        self.emitter.emit('publish-sensors',{'data':sensors})
        self.emitter.emit('publish-actions',{'data':actions})

class TorcsClient(object):
    def __init__(self):
        self.args = {'emitter':None,'host':'localhost','port':3001,'framesize':1024,'tryouts':5,'timeout':3,'deamon':True,'reconnect':False}
        self.events = {'torcs-options':self.decorate,'connect-client':self.create,'disconnect-client':self.disconnect} # 'torcs-options':self.decorate
        self.connected = False
        self.client = None
        self.thread = None
        self.processor = TorcsProcessor()

    def decorate(self,arguments):
        from Util import decorate
        self.processor.decorate(arguments)
        return decorate(self,arguments)

    def create(self,data={}):
        self.emitter = self.args.get('emitter')
        if None == self.emitter:
            logging.error('no event dispatcher set')
            return self
        self.connected = False
        self.processor.create()
        from socket import socket, AF_INET, SOCK_DGRAM
        self.client = socket(AF_INET, SOCK_DGRAM)
        self.client.settimeout(self.args.get('timeout'))
        from threading import Thread
        self.thread = Thread(target=self.connect)
        self.thread.setDaemon(self.args.get('deamon'))
        self.thread.start()
        return self

    def connect(self):
        timeout = self.args.get('timeout')
        address = (self.args.get('host'),self.args.get('port'))
        framesize = self.args.get('framesize')
        tryouts = self.args.get('tryouts')*timeout
        logging.info('torcs-client runs on %s:%s with %s processor'%(address[0],address[1],self.processor.name))
        self.processor.start()
        message = self.processor.initialize(self.args.get('port')).encode()
        counter = 0
        from socket import error
        while not self.connected:
            try:
                self.client.sendto(message,address)
                message, a = self.client.recvfrom(framesize)
                if '***identified***\x00' == message: # 17 bytes
                    logging.debug('connection established to %s:%d'%a)
                    break
            except error as e:
                logging.info('wait for connection. timeout in %s seconds (%s).'%(tryouts-counter,e))
                if(counter >= tryouts):
                    return self
                counter = counter+timeout
        logging.debug('start data listener. connected to %s:%d'%address)
        self.connected = True
        try:
            while self.connected:
                message, a = self.client.recvfrom(framesize)
                if not message:
                    continue
                elif '***shutdown***\x00' == message: # 15 bytes
                    logging.info('Server requested shutdown.')
                    break
                elif '***restart***\x00' == message: # 14 bytes
                    logging.info('Server requested restart.')
                    self.disconnect()
                    self.start()
                else: # 
                    self.client.sendto(self.processor.process(message.decode()).encode(),address)
                    # emit('sensors-recorded',{'message':message.decode(),'promise':self.promise}) # nicht so cool glaub
        except error as e:
            logging.error('torcs client error. client %s'%e)
        logging.info('client disconnected from %s:%s'%address)
        self.client.close()

        # experimental
        if self.args.get('reconnect'):
            logging.info('try to reconnect')
            self.thread = Thread(target=self.connect)
            self.thread.setDaemon(self.args.get('deamon'))
            self.thread.start()
        else:
            logging.info('reconnect off, shutdown')
            self.emitter.emit('kill-process',{})
        return self

    def promise(self,actions):
        self.client.sendto(actions.encode(),( self.args.get('host'),self.args.get('port') ))

    def disconnect(self,data={}):
        self.connected = not self.connected
        self.connected = False
        return self
