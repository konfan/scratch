#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import launcher
import logging
import traceback
from utils.exceptions import *

LOGFILE = 'install.log'


def initlogger(debug = False):
    try:
        logfile = LOGFILE
        lfhandle = logging.FileHandler(filename=logfile, mode='w')
        fmts = '%(asctime)s\t%(levelname)s\t%(module)s::%(name)s\t%(message)s'
        dfmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter(fmts, dfmt)
        lfhandle.setFormatter(fmt)
        logging.root.handlers = []
        logging.root.addHandler(lfhandle)
        if debug:
            logging.root.setLevel(logging.DEBUG)
        else:
            logging.root.setLevel(logging.INFO)
    except:
        logging.error(traceback.format_exc())
        raise LogRuntimeError("log error")

    return logfile


def start(launcherobj):
    """
    create a control object

    launcherobj: laucher object create by launcher
    """
    pass



class InstallControl(object):

    def __init__(self, modules):
        #load modules 
        self.modules = dict([(m.__name__, m) for m in modules])
        self.manager = []


    def startAll(self):
        pass

    def addPlugin(self, plugin):
        self.modules.update(plugin.__name__, plugin)


    def getAllPlugins(self):
        return self.modules.keys()

    def genExecPlan(self):
        # module sequence
        modulestree = []
        planlist = []

        for v in modulestree:
            planlist.append(v.make(launcher.config))

        


if __name__ == '__main__':
    import test
    initlogger()
    test.seqtest()
