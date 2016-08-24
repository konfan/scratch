#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import core
import basedefs
import os
from utils import network
from utils.shortcuts import *


package_dest = basedefs.INSTALL_CACHE_DIR


stork_config = {
        "hosts":""

        }

stork_package, version = basedefs.findpackage(basedefs.PACKAGE_DIR, "stork")




def baseconfig(config):
    global stork_config
    l = config.get('stork', 'hosts')
    stork_config['hosts'] = filter(lambda x:x, [s.strip() for s in l.split(',')])
    #TODO check ip list
    l = config.get('danacenter', 'centernodes')
    stork_config['centerhosts'] = filter(lambda x:x, [s.strip() for s in l.split(',')])



install_template = {
        "prepare":{
            "name":"prepare",
            "type":"script",
            "command":"mkdir -p %s"%package_dest
            },
        "copy files":makecopy('copy files', os.path.join(basedefs.PACKAGE_DIR, stork_package),
           os.path.join(package_dest, stork_package)),
        "unpack":makescript('unpack', 'cd %s && tar zxf %s'%(package_dest, stork_package)),

        'install':makescript('install', "chmod a+x {0} && cd {1} && ./install.sh".format(
            os.path.join(package_dest, 'stork', 'install.sh'),
            os.path.join(package_dest, 'stork')))
        }

def maketemplate():
    commands = [install_template['prepare'], 
        install_template['copy files'],
        install_template['unpack'],
        install_template['install']]

    return commands



def buildplan(config):
    baseconfig(config)
    install_seq = core.SequenceTemplate('stork_nodes', maketemplate())
    hosts = ['%s@%s'%(config.get('common', 'installuser'), x.strip()) for x in stork_config['hosts']]
    return [core.ExecutePlan('stork', install_seq, hosts)]
