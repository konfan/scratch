#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import launcher
import logging
import traceback

LOGFILE = 'install.log'


def initlogger(debug):
    try:
        logfile = LOGFILE
        lfhandle = logging.FileHandler(filename=logfile, mode='w')
        fmts = '%(asctime)s\t%(levelname)s\t%(module)::%(name)s:: %message)s'
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
        raise Exception("log error")

    return logfile


def start(launcherobj):
    """
    create a control object

    launcherobj: laucher object create by launcher
    """
    pass



class InstallControl(object):

    def __init__(self):
        #load modules 
        for modules in installlist:
            # load modules
            pass
        pass


    def startAll(self):
        pass

    def addPlugin(self, plugin):
        pass


    def getAllPlugins(self):
        pass


    def addExecPlan(self, plan):
        pass
