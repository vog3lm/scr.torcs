import logging

class ApplicationDispatcher(object):
    def __init__(self):
        self.events = {}
        self.args = {'trace':False}
        self.flag = True
        from queue import Queue
        self.queue = Queue()
        from threading import Thread, Event
        self.lock = Event()
        self.thread = Thread(target=self.thread,args=[self.queue])
        self.thread.setDaemon(True)
        self.thread.start()

    def decorate(self,arguments):
        from Util import decorate
        return Util.decorate(self,arguments)

    def attach(self,evts):
        keys = self.events.keys()
        for key in evts.keys():
            if not key in keys:
                self.events[key] = []
            self.events[key].append(evts.get(key))
        return self

    def emits(self,evts):
        for evt in evts:
            self.emit(evt.get('id'),evt)
        return self

    def emit(self,call,data):
        evtIds = self.events.keys();
        if call in evtIds:
            try:
                for evt in self.events.get(call):
                    evt(data)
            except Exception as e:
                if self.args.get('trace'):
                    logging.exception("emit error! %s not reachable due to %s"%(call,e))
                else:
                    logging.error("emit error! %s not reachable due to %s"%(call,e))
        else:
            logging.debug('%s event not found. known events are %s'%(call,', '.join(evtIds)))
        return self

    def threaded(self,call,data):
        data['call'] = call
        self.queue.put(data)
        self.lock.set()

    def thread(self,queue):
        while self.flag:
            self.lock.wait()
            data = queue.get()
            self.emit(data.get('call'),data)
            queue.task_done()


class ProcessStop(Exception):
    pass

class ProcessEngine(object):
    def __init__(self):
        self.events = {'kill-process':self.kill,'process-options':self.decorate}
        self.args = {'emitter':None,'oops':None,'process-services':[]}
        self.flag = True
        self.emitter = None
        self.services = ['create-logger','connect-client'] # start always
        #import threading
        #self.lock = threading.Event()
        from signal import signal, SIGTERM, SIGINT
        signal(SIGINT,self.killer) # SIG_IGN|SIG_DFL
        signal(SIGTERM,self.killer)
        from os import getpid
        self.pid = getpid()

    def decorate(self,arguments):
        return decorate(self,arguments)

    def create(self):
        self.emitter = self.args.get('emitter')
        if None == self.emitter:
            logging.error('no event dispatcher set')
            return self
        for service in self.args.get('process-services'): # attach optionals
            self.services.append(service)
        for service in self.services:
            self.emitter.emit(service,{'call':service,'id':'create-process'})
        logging.info('Process Engine %s Started.'%(self.pid))
        try:
            from signal import pause
            from time import sleep
            while self.flag:
                pause() # stop thread, signal handler keeps reacting
            #    self.lock.wait() # stop thread, signal handler not reacting
            #    sleep(3600) # stop thread, signal handler keeps reacting
        except self.args['oops'] as e:
            logging.info('Process Engine %s Exception. %s'%(self.pid,e.toString()))
        except ProcessStop as e:
            logging.exception('Engine Kill Exception Interrupt. %s'%str(e))
        logging.info('Process Engine %s Stopped.'%(self.pid))
        return self

    def killer(self,signum,frame):
        logging.info('kill application')
        self.emitter.emit('client-disconnect',{})
        self.kill()

    def kill(self,data={}):
        self.flag = False
        #self.lock.set() # unlock thread
        from os import system
        system('kill -9 %s'%self.pid)
        return self

class ProcessLogger(object):
    def __init__(self):
        # log levels
            # CRITICAL  50
            # ERROR     40
            # WARNING   30
            # INFO      20
            # DEBUG     10
            # NOTSET     0
        self.events = {'logger-options':self.decorate,'create-logger':self.create}
        self.args = {'emitter':None,'path':'unset','level':20,'newfile':True,'shell':True
                    ,'format':'%(asctime)18s %(levelname)7s >> %(process)6s %(module)s.%(funcName)s():%(lineno)d >> %(message)s'
                    ,'date':'%Y-%m-%d %H:%M:%S'}
        self.logger = logging.getLogger()
        self.file = None
        self.shell = None

    def decorate(self,arguments):
        return decorate(self,arguments)

    def create(self,data={}):
        self.logger.setLevel(self.args.get('level'))
        if(self.logger.handlers):
            self.logger.handlers.pop()
        formatter = logging.Formatter(fmt=self.args.get('format'),datefmt=self.args.get('date'))
        if(self.args.get('shell')):
            import sys
            self.shell = logging.StreamHandler(sys.stdout)
            self.shell.setFormatter(formatter)
            self.logger.addHandler(self.shell)
        path = self.args.get('path')
        if(path and not 'unset' == path):
            if(self.args.get('newfile')):
                try:
                    from os import remove
                    remove(path)
                except OSError:
                    pass
            self.file = logging.FileHandler(path)
            self.file.setFormatter(formatter)
            self.logger.addHandler(self.file)
        return self

class DataRecorder(object):
    def __init__(self):
        self.events = {'start-recorder':self.create,'recorder-options':self.decorate,'publish-sensors':self.sensors,'publish-actions':self.actions}
        self.args = {'path':'unset.log','mode':'override','listen':False}
        from json import dumps
        self.json = dumps

    def decorate(self,arguments):
        return decorate(self,arguments)

    def create(self,data={}):
        mode = self.args.get('mode')
        path = self.args.get('path')
        if 'override' == mode:
            open(path,"w").close()
        else:
            open(path,"a").close()
        logging.info('data recorder online, write to %s, %s mode'%(path,mode))
        return self

    def sensors(self,data):
        if self.args.get('listen'):
            with open(self.args.get('path'), 'a') as f:
                f.write('%s\n'%self.json(data))

    def actions(self,data):
        if self.args.get('listen'):
            with open(self.args.get('path'), 'a') as f:
                f.write('%s\n'%self.json(data))

class ShellArguments(object):
    def __init__(self):
        self.args = {'emitter':None
                    ,'host=':'h:','port:':'p:','driver=':'d:','human':'' # torcs opts
                    ,'record=':'r:' # recorder opts
                    ,'verbose=':'','logfile=':'','noshell':'' # logging opts
                    ,'monitor':'m'}
        self.logOpt = {}
        self.monOpt = {}
        self.recOpt = {}
        self.prcOpt = {'process-services':[]}
        self.scrOpt = {'driver':'default'}
        self.emitter = None

    def decorate(self,arguments): # register new cmd line args
        return decorate(self,arguments)

    def create(self):
        self.emitter = self.args.get('emitter')
        if None == self.emitter:
            logging.error('no event dispatcher set')
            return self
        del self.args['emitter']
        from sys import exit, argv
        from getopt import getopt, GetoptError
        try:
            opts, args = getopt(argv[1:],shortopts=''.join(self.args.values()),longopts=self.args.keys())
            for o, a in opts: # must be at the beginning of input
                if '-h' == o:self.scrOpt['host'] = a
                elif '--host' == o:self.scrOpt['host'] = a
                elif '-p' == o:self.scrOpt['port'] = int(a)
                elif '--port' == o:self.scrOpt['port'] = int(a)
                elif '-d' == o:self.scrOpt['driver'] = a
                elif '--driver' == o:self.scrOpt['driver'] = a
                elif '--human' == o:self.scrOpt['modus'] = 'human'
                elif '--verbose' == o:self.logOpts['level'] = a
                elif '--logfile' == o:self.logOpts['path'] = a
                elif '--noshell' == o:self.logOpts['shell'] = False
                elif '-r' == o:
                    self.scrOpt['publish'] = True
                    self.recOpt['listen'] = True
                    self.recOpt['path'] = a
                    self.prcOpt.get('process-services').append('start-recorder')
                elif '--record' == o:
                    self.scrOpt['publish'] = True
                    self.recOpt['listen'] = True
                    self.recOpt['path'] = a
                    self.prcOpt.get('process-services').append('start-recorder')
                elif '-m' == o:
                    self.scrOpt['publish'] = True
                    self.monOpt['listen'] = True
                    self.prcOpt.get('process-services').append('start-monitor')
                elif '--monitor' == o:
                    self.scrOpt['publish'] = True
                    self.monOpt['listen'] = True
                    self.prcOpt.get('process-services').append('start-monitor')
            return self
        except GetoptError as e:
            logging.error(e.msg)
            exit(2)

    def deliver(self):
        self.emitter.emit('logger-options',self.logOpt)
        self.emitter.emit('torcs-options',self.scrOpt)
        self.emitter.emit('monitor-options',self.monOpt)
        self.emitter.emit('recorder-options',self.recOpt)
        self.emitter.emit('process-options',self.prcOpt)
        return self

def decorate(clazz,arguments):
    if 'emitter' in arguments.keys() and hasattr(clazz,'events'):
        arguments.get('emitter').attach(clazz.events)
    keys = clazz.args.keys()
    for key in arguments:
        if key in keys:
            clazz.args[key] = arguments[key]
    return clazz