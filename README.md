# scr.torcs
Torcs Simulated Car Racing Driver Client in Python.

### Features

* Custom Robot Drivers
* Human Keyboard Driver
* Human Gamepad Driver
* Sensor Data Recorder
* Action Data Recorder
* Realtime Car Monitor
* 
### Get Started
##### Dependencies

At first you will have to install Torcs - The Open Race Car Simulator and patch it. To do this stick to this [manual](https://github.com/vog3lm/torcs-1.3.7). Tested under Debian 4.16.16-2kali2 64it.

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







