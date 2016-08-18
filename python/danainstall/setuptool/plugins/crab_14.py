#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import core
import basedefs
import os
from utils import network
from utils.shortcuts import *


package_dest = basedefs.INSTALL_CACHE_DIR


crab_config = {
        "hosts":""

        }

crab_package = "crab.tar.gz"




def baseconfig(config):
    global crab_config
    l = config.get('crab', 'hosts')
    crab_config['hosts'] = [s.strip() for s in l.split(',')]
    #TODO check ip list
    l = config.get('danacenter', 'centernodes')
    crab_config['centerhosts'] = [s.strip() for s in l.split(',')]



install_template = {
        "prepare":{
            "name":"prepare",
            "type":"script",
            "command":"mkdir -p %s"%package_dest
            },
        "copy files":makecopy('copy files', os.path.join(basedefs.PACKAGE_DIR, crab_package),
           os.path.join(package_dest, crab_package)),
        "unpack":makescript('unpack', 'cd %s && tar zxf %s'%(package_dest, crab_package)),

        'install':makescript('install', "chmod a+x {0} && cd {1} && ./install.sh".format(
            os.path.join(package_dest, 'crab', 'install.sh'),
            os.path.join(package_dest, 'crab')))
        }

def maketemplate():
    commands = [install_template['prepare'], 
        install_template['copy files'],
        install_template['unpack']
       #install_template['install']
		]

    return commands



def buildplan(config):
    baseconfig(config)
    install_seq = core.SequenceTemplate('crab_nodes', maketemplate())
    hosts = ['%s@%s'%(config.get('common', 'installuser'), x.strip()) for x in crab_config['hosts']]
    return [core.ExecutePlan('crab', install_seq, hosts)]
