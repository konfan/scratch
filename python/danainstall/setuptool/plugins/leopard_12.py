#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import core
import basedefs
import os
from utils import network
from utils.shortcuts import *


package_dest = basedefs.INSTALL_CACHE_DIR


leopard_config = {
        "hosts":""

        }

leopard_package, version = basedefs.findpackage(basedefs.PACKAGE_DIR, "leopard")




def baseconfig(config):
    global leopard_config
    l = config.get('leopard', 'hosts')
    leopard_config['hosts'] = filter(lambda x:x, [s.strip() for s in l.split(',')])
    #TODO check ip list
    l = config.get('danacenter', 'centernodes')
    leopard_config['centerhosts'] = filter(lambda x:x, [s.strip() for s in l.split(',')])



install_template = {
        "prepare":{
            "name":"prepare",
            "type":"script",
            "command":"mkdir -p %s"%package_dest
            },
        "copy files":makecopy('copy files', os.path.join(basedefs.PACKAGE_DIR, leopard_package),
           os.path.join(package_dest, leopard_package)),
        "unpack":makescript('unpack', 'cd %s && tar zxf %s'%(package_dest, leopard_package)),

        'install':makescript('install', "chmod a+x {0} && cd {1} && ./install.sh".format(
            os.path.join(package_dest, 'leopard', 'install.sh'),
            os.path.join(package_dest, 'leopard')))
        }

def maketemplate():
    commands = [install_template['prepare'], 
        install_template['copy files'],
        install_template['unpack'],
        install_template['install']]

    return commands



def buildplan(config):
    baseconfig(config)
    install_seq = core.SequenceTemplate('leopard_nodes', maketemplate())
    hosts = ['%s@%s'%(config.get('common', 'installuser'), x.strip()) for x in leopard_config['hosts']]
    return [core.ExecutePlan('leopard', install_seq, hosts)]
