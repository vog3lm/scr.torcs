# scr.torcs
Torcs Simulated Car Racing Driver Client in Python.

### Features

* Custom Robot Drivers
* Human Keyboard Driver
* Human Gamepad Driver
* Sensor Data Recorder
* Action Data Recorder
* Realtime Car Monitor

### Get Started
##### Dependencies

At first you will have to install Torcs - The Open Race Car Simulator and patch it. To do this stick to this [manual](https://github.com/vog3lm/torcs-1.3.7). Tested under Debian 4.16.16-2kali2 64it. Then install the following core dependencies.

```
pip install getopts
pip install inputs
pip install json
pip install pydoc
pip install pynput
```
The realtime car monitor is based on flask microframework.
```
pip install flask
pip install flask-socketio
```
##### Command Line Options

To start the application, navigate to the root directory and call `python start.py`. This will start the default client (`http://127.0.0.1:3001`) with a default driver. The following options can be passed.
```
[-h | --host ]...........: the servers host
[-p | --port ]...........: the servers port
[-d | --driver ].........: the driver to be used
                           if unused, a default driver will be used
[   | --logfile ]........: log to a file in app dir
[   | --verbose ]........: log output level
[   | --human ]..........: flag to use a human driver
[   | --noshell ]........: flag to kill shell output

[-r | --record ].........: acitvates the data recorder, pass a filename
[-m | --monitor ]........: flag to activate the realtime monitor
```

##### Custom Robot Drivers

To add a custom driver create a file in the application directory. Every driver has to have `name` and `angles` attributes as well as a driving method. Stick to the `Example.py` driver to see a minimal configuration for that. If you start the client with a call like this, `python start.py --driver Example`, your custom robot driver logic will be used.

##### Human Drivers

There are two human driving options, `gamepad` and `keyboard`. To use one of them add the `--human` to the client start command.

```
python start.py --human --driver=keyboard
python start.py --human --driver=gamepad
```

To change the input settings open `Drivers.py` and change it according to your personal demands.

##### Data Recorder

The internal data recorder is to by started by the `--record` or just `-r` option. The option needs a file name where the data will be written to. The record file will be created in die application root directory and contain sensor and actor values of the used driver.

```
python start.py --record=data.log
```

##### Realtime Monitor

To see how you driver does add the `--monitor` flag to the application start command. This will start a flask based background webserver access under `localhost:5000`. The monitor interface consist of a one file html document with a socket connection to the driver client. Open `monitor.html` according to change the interface to your personal demands.


# scr.torcs
Torcs Simulated Car Racing Driver Client in Python.

### Features

* Custom Robot Drivers
* Human Keyboard Driver
* Human Gamepad Driver
* Sensor Data Recorder
* Action Data Recorder
* Realtime Car Monitor

### Get Started
##### Dependencies

At first you will have to install Torcs - The Open Race Car Simulator and patch it. To do this stick to this [manual](https://github.com/vog3lm/torcs-1.3.7). Tested under Debian 4.16.16-2kali2 64it. Then install the following core dependencies.

```
pip install getopts
pip install inputs
pip install json
pip install pydoc
pip install pynput
```
The realtime car monitor is based on flask microframework.
```
pip install flask
pip install flask-socketio
```
##### Command Line Options

To start the application, navigate to the root directory and call `python start.py`. This will start the default client (`http://127.0.0.1:3001`) with a default driver. The following options can be passed.
```
[-h | --host ]...........: the servers host
[-p | --port ]...........: the servers port
[-d | --driver ].........: the driver to be used
                           if unused, a default driver will be used
[   | --logfile ]........: log to a file in app dir
[   | --verbose ]........: log output level
[   | --human ]..........: flag to use a human driver
[   | --noshell ]........: flag to kill shell output

[-r | --record ].........: acitvates the data recorder, pass a filename
[-m | --monitor ]........: flag to activate the realtime monitor
```

##### Custom Robot Drivers

To add a custom driver create a file in the application directory. Every driver has to have `name` and `angles` attributes as well as a driving method. Stick to the `Example.py` driver to see a minimal configuration for that. If you start the client with a call like this, `python start.py --driver Example`, your custom robot driver logic will be used.

##### Human Drivers

There are two human driving options, `gamepad` and `keyboard`. To use one of them add the `--human` to the client start command.

```
python start.py --human --driver=keyboard
python start.py --human --driver=gamepad
```

To change the input settings open `Drivers.py` and change it according to your personal demands.

##### Data Recorder

The internal data recorder is to by started by the `--record` or just `-r` option. The option needs a file name where the data will be written to. The record file will be created in die application root directory and contain sensor and actor values of the used driver.

```
python start.py --record=data.log
```

##### Realtime Monitor

To see how you driver does add the `--monitor` flag to the application start command. This will start a flask based background webserver access under `localhost:5000`. The monitor interface consist of a one file html document with a socket connection to the driver client. Open `monitor.html` according to change the interface to your personal demands.







### Create a robot
##### create source

```
cd pi.simulation/torcs/torcs-1.3.7/
./robotgen -n "name_of_car" -a "name_of_author" -c "type_of_car" --gp
```

All available types of cars are located in`$TORCS_BASE/data/cars/models/`. Your driver will crash if you select a type of car can not be found the directory.

```
static int InitFuncPt(int index, void *pt){
    tRobotItf *itf = (tRobotItf *)pt;
    itf->index      = index;
    itf->rbNewTrack = initTrack;  /* init new track */
    itf->rbNewRace  = newRace;    /* init new race */
    itf->rbDrive    = drive;      /* drive during race */
    itf->rbShutdown = shutdown;   /* called for cleanup per driver */
    itf->rbPitCmd   = pitcmd;     /* pit command */
    itf->rbEndRace  = NULL;       /* end of the current race */
    return 0;
}
```

##### compile source

```
export TORCS_BASE=/root/pi.simulation/torcs/torcs-1.3.7
export MAKE_DEFAULT=$TORCS_BASE/Make-default.mk
make
sudo make install
```

### Capture robot data

Navigate to the robot source directory (e.g. `cd $TORCS_BASE/src/drivers/berniw`) and find the main control file. It's the file with the `InitFuncPt` method. `InitFuncPt` assigns the driver interface methods that will be used during the simulation. To make changes working, recompile the driver.

```
...
#include "pirate.cpp"
...
static int InitFuncPt(int index, void *pt){
    ...
    itf->rbNewTrack = initTrack; /* init new track */
    itf->rbNewRace  = newRace;   /* init new race */
    itf->rbDrive = drive;        /* drive during race */
    itf->rbEndRace = kill;       /* stop data capturing */
    return 0;
}
...
static void initTrack(int index, tTrack* track, void *carHandle, void **carParmHandle, tSituation* s){
    ...
    create(track); /* create capturing file */
}
...
static void newRace(int index, tCarElt* car, tSituation *s){
    ...
    start(index,car,s,"name_of_driver")
}
...
static void drive(int index, tCarElt* car, tSituation* s){
    ...
    capture(index,car,s) /* capture race data */
}
```

### Extend `scr_server` Data

Navigate to `$TORCS_BASE/src/drivers/scr_server/scr_server.cpp`. To make changes working, recompile the driver.

```
/** Track structure 
    location: src/interfacex/car.h */
typedef struct{
    const char *name;        /* Name of the track */
    const char *author;      /* Author's name */
    char *filename;          /* Filename of the track description */
    void *params;            /* Parameters handle */
    char *internalname;      /* Internal name of the track */
    const char *category;    /* Category of the track */
    int nseg;                /* Number of segments */
    int version;             /* Version of the track type */
    tdble length;            /* main track length */
    tdble width;             /* main track width */
    tTrackPitInfo pits;      /* Pits information */
    tTrackSeg *seg;          /* Main track */
    tTrackSurface *surfaces; /* Segment surface list */
    t3Dd min;
    t3Dd max;
    tTrackGraphicInfo graphic;
} tTrack;
```

```
/** This is the main car structure.
    location: src/interfacex/car.h   */
typedef struct CarElt{
    int index;              /* car index */
    tInitCar info;          /* public */
    tPublicCar pub;         /* public */
    tCarRaceInfo race;      /* public */
    tPrivCar priv;          /* private */
    tCarCtrl ctrl;          /* private */
    tCarPitCmd pitcmd;      /* private */
    struct RobotItf *robot; /* private */
    struct CarElt *next;
    int RESTART;
    int RESET;    
} tCarElt;
```

```
/** cars situation used to inform the GUI and the drivers
    location: src/interfaces/racemen.h   */
typedef struct Situation {
    tRaceAdmInfo    raceInfo;
    double          deltaTime;
    double          currentTime; /* time in sec (start=0) */
    int             nbPlayers;   /* number of human players */
    tCarElt         **cars;      /* list of cars */
} tSituation;
```


### Capture Race Engine

Navigate to `$TORCS_BASE/src/libs/raceengineclient/raceengine.cpp` and add the following statements to this file. To make changes working, recompile the game.

###### Note: NOT TESTED, BETTER NOT TRY AT HOME.

```
...
#include "pirates.h"
...
void ReStart(void){
    ....
    create("track","drivers") /* create data sources */
}
...
static void ReOneStep(double deltaTimeIncrement){
    ...
    START_PROFILE("rbDrive*");
    if ((s->currentTime - ReInfo->_reLastTime) >= RCM_MAX_DT_ROBOTS) {
        s->deltaTime = s->currentTime - ReInfo->_reLastTime;
        for (i = 0; i < s->_ncars; i++) {
            if ((s->cars[i]->_state & RM_CAR_STATE_NO_SIMU) == 0) {
                robot = s->cars[i]->robot;
                robot->rbDrive(robot->index, s->cars[i], s);
                capture(robot->index, s->cars[i], s); /* start data capturing */
            }
        }
        ReInfo->_reLastTime = s->currentTime;
    }
    STOP_PROFILE("rbDrive*");
    ...
}
...
void ReStop(void){
    ...
    kill(); /* stop data capturing */
}

```
###### Note: NOT TESTED, BETTER NOT TRY AT HOME.
