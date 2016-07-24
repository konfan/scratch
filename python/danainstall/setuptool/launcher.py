#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from core import *
from utils.exceptions import *
import ConfigParser
import basedefs
import sys
import os
import re
import logging
import traceback
import collections


config = ConfigParser.SafeConfigParser()

modules = collections.OrderedDict()

pattern = re.compile(r"(\S+)_(\d+)")


def loadplugins(fname):
    sys.path.append(basedefs.DIR_PLUGINS)

    mod = os.path.join(basedefs.DIR_PLUGINS, "%s.py"%fname)
    if not os.path.isfile(mod):
        raise InstallError("failed load plugin for %s"%fname)

    module = __import__(fname)
    module.__file__ = mod
    module.__level__ = re.match(pattern, fname).groups()[1]
    globals()[fname] = module
    return module



def sortmodule(filelist):
    """
    return [(name, name_seq)]
    """
    filtered = []
    for f in filelist:
        g = re.match(pattern, f)
        if g:
            # plugin, num, plugin_num
            filtered.append((g.groups()[0], g.groups()[1], f))

    return map(lambda y:(y[0], y[2]), sorted(filtered, key = lambda x:x[1]))



def load(conf):
    """ 
    list plugin modules
    load config settings
    """
    global modules, config

    config.read(conf)
    flist = sortmodule([f[:-3] for f in os.listdir(basedefs.DIR_PLUGINS) if f[-3:] == ".py"])
    
    for sec, fname in flist:
        try:
            #modules.append(loadplugins(sec))
            modules[sec] = loadplugins(fname)
        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_exc())
            raise InstallError("failed when load plugins")

    return modules

def buildplan(module):
    plans = modules[module].buildplan(config)
    for plan in plans:
        if plan.priority == plan.DEFAULT_PRIORITY:
            plan.priority = modules[module].__level__

    return plans



# generate engine plan

# generate node command



def test():
    v = load('test.conf')
    for n,v in v.items():
        print(n, v.__file__)
    plan = buildplan('common')
    print(plan)

def testplugins(pfile):
    load('test.conf')
    sys.path.append(basedefs.DIR_PLUGINS)
    #mod = os.path.join(basedefs.DIR_PLUGINS, "%s.py"%pfile)
    module = __import__(pfile)
    module.parseconfig(config)

    for cmds in module.buildplan(config):
        print('****************************************************')
        for cmd in cmds:
            print cmd


if __name__ == '__main__':
    #test()
    #print(sortmodule(['ff_05', 'yy_08','cc_03', 'dd_03']))
    testplugins('danacenter')

