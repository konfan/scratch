#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import launcher
import logging
import traceback
import core
from utils.exceptions import *


LOGFILE = 'install.log'

controller = None


def initlogger(debug = False):
    import sys
    logging.getLogger('paramiko').setLevel(logging.ERROR)
    try:
        logfile = LOGFILE
        lfhandle = logging.FileHandler(filename=logfile, mode='w')
        stdhandle = logging.StreamHandler(sys.stdout)
        fmts = '%(asctime)s\t%(levelname)s\t%(module)s::%(name)s\t%(message)s'
        dfmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter(fmts, dfmt)
        lfhandle.setFormatter(fmt)
        stdhandle.setFormatter(fmt)
        logging.root.handlers = []
        logging.root.addHandler(lfhandle)
        logging.root.addHandler(stdhandle)
        if debug:
            logging.root.setLevel(logging.DEBUG)
        else:
            logging.root.setLevel(logging.INFO)
    except:
        logging.error(traceback.format_exc())
        raise LogRuntimeError("log error")

    return logfile






class InstallControl(object):

    def __init__(self, modules):
        self.modules = modules
        self.runner = core.Pool()
        self.planlist = self.genExecPlan()


    def start(self):
        import threading
        def _start():
            for plan in self.planlist:
                map(self.runner.add, plan.sequences())
        self.th = threading.Thread(target = _start)
        self.th.daemon = True
        self.th.start()

    def stop(self):
        self.runner.stop()

    def wait(self):
        self.runner.queue.join()


    def getAllPlugins(self):
        return self.modules.keys()

    def genExecPlan(self):
        # module sequence
        planlist = []

        for v in self.modules.values():
            planlist.append(v.buildplan(launcher.config))

        return planlist

    def status(self):
        return [plan.stats() for plan in self.planlist]


        


if __name__ == '__main__':
    import test
    initlogger(True)
    test.seqtest()
