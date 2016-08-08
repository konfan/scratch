#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import core
import basedefs
import os
from utils import network
from utils.shortcuts import *


package_dest = basedefs.INSTALL_CACHE_DIR


eagles_config = {
        "hosts":""

        }

eagles_package = "eagles.tar.gz"




def baseconfig(config):
    global eagles_config
    l = config.get('eagles', 'hosts')
    eagles_config['hosts'] = [s.strip() for s in l.split(',')]
    #TODO check ip list
    l = config.get('danacenter', 'centernodes')
    eagles_config['centerhosts'] = [s.strip() for s in l.split(',')]



install_template = {
        "prepare":{
            "name":"prepare",
            "type":"script",
            "command":"mkdir -p %s"%package_dest
            },
        "copy files":makecopy('copy files', os.path.join(basedefs.PACKAGE_DIR, eagles_package),
           os.path.join(package_dest, eagles_package)),
        "unpack":makescript('unpack', 'cd %s && tar zxf %s'%(package_dest, eagles_package)),

        'install':makescript('install', "chmod a+x {0} && cd {1} && ./install.sh".format(
            os.path.join(package_dest, 'eagles', 'install.sh'),
            os.path.join(package_dest, 'eagles')))
        }

def maketemplate():
    commands = [install_template['prepare'], 
        install_template['copy files'],
        install_template['unpack'],
        install_template['install']]

    return commands



def buildplan(config):
    baseconfig(config)
    install_seq = core.SequenceTemplate('eagles_nodes', maketemplate())
    hosts = ['%s@%s'%(config.get('common', 'installuser'), x.strip()) for x in eagles_config['hosts']]
    return [core.ExecutePlan('eagles', install_seq, hosts)]
