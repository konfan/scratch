#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import ConfigParser
from core import *

config = ConfigParser.SafeConfigParser()

modules = []

def has_plugins(sec):
    return True

def load(conffile):
    config.read(conffile)
    for sec in config.sections():
        if has_plugins(sec):
            modules.append(sec)

    #generate executeplan
    pass

