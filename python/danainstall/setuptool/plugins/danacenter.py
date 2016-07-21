#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import core
import basedefs
import os
from utils.shortcuts import *



"""
install danacenter:
    get center node list
    get manage node list
    get common node list

    for center node:
        install
        config yak_common.conf
        start service

    for manage node:
        install
        config zookeeper
        config danaeagles
        create myid file for zookeeper


    for common node:
        install
        config yakagent
"""

package_dest = basedefs.INSTALL_CACHE_DIR

common_package = "other.tar.gz"
common_conf_file = "/etc/dt.d/yakagent.conf"

dana_config = {
        "hosts":[],
        "centerhosts":[],
        "managehosts":[]
        }


def parseconfig(config):
    global dana_config
    l =  config.get('common', 'nodes')
    dana_config['hosts'] = [s.strip() for s in l.split(',')]

    l = config.get('danacenter', 'centernodes')
    dana_config['centerhosts'] = [s.strip() for s in l.split(',')]

    l = config.get('danacenter', 'managenodes')
    dana_config['managehosts'] = [s.strip() for s in l.split(',')]

    dana_config['clustername'] = config.get('common', 'clustername')



common_template = {
        'prepare':makescript("prepare", "mkdir -p %s"%package_dest),
        
        'copy files':makecopy("copy files", os.path.join(basedefs.PACKAGE_DIR, common_package),
            os.path.join(package_dest, common_package)),

        'install':makescript('install', "chmod a+x {0} && {1}")
        }




def common_plan(config):
    commands = [common_template['prepare'],common_template['copy files']]
    install = common_template['install']
    target = os.path.join(package_dest,'danacenter','other', 'install.sh')
    install['command'] = install['command'].format(target, target)

    commands.append(install)

    #gen config

    # clustername
    cfg_command = sed_set_opt('clustername', dana_config['clustername'], common_conf_file)
    commands.append(makescript('modify clustername', cfg_command))

    cfg_command = sed_set_opt('zookeeper_host', 
            '%s:10301'%dana_config['centerhosts'][0], 
            common_conf_file)
    commands.append(makescript('set zookeeper host', cfg_command))

    cfg_command = sed_set_opt('eagles_host', dana_config['managehosts'][0], common_conf_file)
    commands.append(makescript('set eagles host', cfg_command))

    return cfg_command


def master_plan(config):
    pass


def manage_plan(config):
    pass



def buildplan(config):
    baseconfig(config)
