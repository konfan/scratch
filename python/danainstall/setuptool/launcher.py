#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from core import *
from utils.exceptions import *
import ConfigParser
import basedefs
import sys
import os
import logging
import traceback


config = ConfigParser.SafeConfigParser()

modules = []


def loadplugins(sec):
    sys.path.append(basedefs.DIR_PLUGINS)
    mod = os.path.join(basedefs.DIR_PLUGINS, "%s.py"%sec)    
    if not os.path.isfile(mod):
        raise InstallError("failed load plugin for %s"%sec)

    module = __import__(sec)
    module.__file__ = mod
    globals()[sec] = module
    return module


def load(conf):
    """ load py files in plugins dir and in config file
    """
    global modules, config

    config.read(conf)
    flist = [f[:-3] for f in os.listdir(basedefs.DIR_PLUGINS) if f[-3:] == ".py"]
    sections = [s for s in config.sections() if s in flist]

    for sec in sections:
        try:
            modules.append(loadplugins(sec))
        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_exc())
            raise InstallError("failed when load plugins")

    #generate executeplan
    #print(globals().keys())
    return modules

def makescript(module):
    return modules[module].makescript(config)


# generate engine plan

# generate node command

