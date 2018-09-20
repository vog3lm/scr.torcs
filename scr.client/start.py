
if __name__ == "__main__":


    # auto start torcs server
        # -l list the dynamically linked libraries
        # -d run under gdb and print stack trace on exit, makes most sense when compile with --enable-debug
        # -e display the commands to issue when you want to run under gdb
        # -s disable multitexturing, important for older graphics cards
        # -m use X mouse cursor and do not hide it during races

    # torcs -r ~/.torcs/config/raceman/champ.xml
    # torcs -r ~/.torcs/config/raceman/dtmrace.xml
    # torcs -r ~/.torcs/config/raceman/endrace.xml
    # torcs -r ~/.torcs/config/raceman/ncrace.xml
    # torcs -r ~/.torcs/config/raceman/practice.xml
    # torcs -r ~/.torcs/config/raceman/quickrace.xml


    from Util import ProcessLogger, ProcessEngine, ApplicationDispatcher, ShellArguments, DataRecorder
    application = ApplicationDispatcher()
    eng = ProcessEngine().decorate({'emitter':application})
    log = ProcessLogger().decorate({'emitter':application})
    DataRecorder().decorate({'emitter':application})
    from Monitor import Monitor, MonitorSocket, MonitorRoutes
    Monitor().decorate({'emitter':application,'logger':log.logger,'namespace':'monitor'})
    from Torcs import TorcsClient
    TorcsClient().decorate({'emitter':application})
    ShellArguments().decorate({'emitter':application}).create().deliver()
    eng.create()
