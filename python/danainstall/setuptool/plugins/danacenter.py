#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import core
import basedefs
import os
from utils.shortcuts import *
from utils import network



#TODO: gen conf file from basedefs & check
package_dest = basedefs.INSTALL_CACHE_DIR
installtool = os.path.join(package_dest, 'installhelper.py')

common_package = "other.tar.gz"
common_conf_file = "/etc/dt.d/yakagent.conf"


master_package = "master.tar.gz"
master_conf_file = "/etc/dt.d/yak_common.conf"

manage_package = "manage.tar.gz"
manage_conf_file = "/opt/dana/zookeeper/conf/zoo.cfg"



redis_slave = "/etc/init.d/redis-slave"
redis_master = "/etc/init.d/redis-master"
yakagent = "/etc/init.d/yakagentsvrdaemon"
yakmanage = "/etc/init.d/yakmanagersvrdaemon"
danastork = "/etc/init.d/stork"
danaeagles = "/etc/init.d/danaeagles"
zookeeper = "/opt/dana/zookeeper/bin/zkServer.sh"

dana_config = {
        "hosts":[],
        "centerhosts":[],
        "managehosts":[]
        }

zoocfg = """tickTime=2000
dataDir=/opt/dana/zookeeper/data
dataLogDir=/var/zookeeper
initLimit=5
syncLimit=2
clientPort=10301
%s
autopurge.snapRetainCount=10
autopurge.purgeInterval=24"""

def parseconfig(config):
    global dana_config
    l =  config.get('common', 'nodes')
    dana_config['hosts'] = [s.strip() for s in l.split(',')]

    l = config.get('danacenter', 'centernodes')
    dana_config['centerhosts'] = [s.strip() for s in l.split(',')]

    l = config.get('danacenter', 'managenodes')
    dana_config['managehosts'] = [s.strip() for s in l.split(',')]

    dana_config['clustername'] = config.get('common', 'clustername')

    dana_config['user'] = config.get('common', 'installuser', 'root')



common_template = {
        'prepare':makescript("prepare", "mkdir -p %s"%package_dest),

        'copy files':makecopy("copy files", os.path.join(basedefs.PACKAGE_DIR, common_package),
            os.path.join(package_dest, common_package)),

        'install':makescript('install', "chmod a+x {0} && {1}"),
        'copy tools':makecopy("prepare config", os.path.join(basedefs.DIR_PROJECT_DIR, 'util', 'installhelper.py'), installtool)
        }


master_template = {
        'prepare':makescript("prepare", "mkdir -p %s"%package_dest),

        'copy files':makecopy("copy files", os.path.join(basedefs.PACKAGE_DIR, master_package),
            os.path.join(package_dest, master_package)),

        'install':makescript('install', "chmod a+x {0} && {1}"),
        'copy tools':makecopy("prepare config", os.path.join(basedefs.DIR_PROJECT_DIR, 'util', 'installhelper.py'), installtool)
        }


manage_template = {
        'prepare':makescript("prepare", "mkdir -p %s"%package_dest),

        'copy files':makecopy("copy files", os.path.join(basedefs.PACKAGE_DIR, manage_package),
            os.path.join(package_dest, manage_package)),

        'install':makescript('install', "chmod a+x {0} && {1}")
        }

def get_nodetype(ip):
    iscenter = lambda i: i in dana_config['centerhosts']
    ismanage = lambda i: i in dana_config['managehosts']
    typecheck = {
            '1':lambda x: iscenter(x) and x == dana_config['centerhosts'][0],
            '2':lambda x: iscenter(x) and x != dana_config['centerhosts'][0],
            '3':lambda x: ismanage(x) and not typecheck[1](x) and not typecheck[2](x),
            '4':lambda x: ismanage(x) and typecheck[1](x),
            '5':lambda x: ismanage(x) and typecheck[2](x)
            }
    for typo, func in typecheck.items():
        if func(ip):
            return typo

    return '6' #not 1~5


def tooloptions():
    m = ','.join(dana_config['managehosts'])
    c = ','.join(dana_config['centerhosts'])
    n = ','.join(dana_config['hosts'])
    d = package_dest
    return "-m %s -c %s -n %s -d %s"%(m, c, n, d)



def common_commands(config):
    commands = [common_template['prepare'],common_template['copy files']]
    install = common_template['install']
    target = os.path.join(package_dest,'danacenter','other', 'install.sh')
    install['command'] = install['command'].format(target, target)
    commands.append(install)

    # gen localip, nodetype
    commands.append(common_template['copy tools'])
    commands.append(makescript('prepare config', 
        'python %s %s %s'%(installtool, tooloptions(), dana_config['centerhosts'][0])))



    # clustername
    cfg_command = sed_set_opt('clustername', dana_config['clustername'], common_conf_file)
    commands.append(makescript('modify clustername', cfg_command))

    # zookeeper host
    zhosts = ','.join(["%s:10301"%zk for zk in dana_config['managehosts']])
    cfg_command = sed_set_opt('zookeeper_host', zhosts, common_conf_file)
    commands.append(makescript('set zookeeper host', cfg_command))

    # eagles host
    ehosts = ','.join(dana_config['managehosts'])
    cfg_command = sed_set_opt('eagles_host', ehosts, common_conf_file)
    commands.append(makescript('set eagles host', cfg_command))

    # local ip
    ipfile = os.path.join(package_dest, "localip")
    localip = "$(cat %s)"%ipfile
    cfg_command = sed_set_opt('local_ip', localip, common_conf_file)
    commands.append(makescript('set local ip', cfg_command))

    # nodetype
    typefile = os.path.join(package_dest, "nodetype")
    nodetype = "$(cat %s)"%typefile
    cfg_command = sed_set_opt('node_type', nodetype, common_conf_file)
    commands.append(makescript('set node_type', cfg_command))

    #start service
    commands.append(makescript('start redis-slave', '%s start'%redis_slave))
    commands.append(makescript('start yakagent', '%s start'%yakagent))

    return commands


def master_commands(config):
    commands = [master_template['prepare'], master_template['copy files']]
    install = master_template['install']
    target = os.path.join(package_dest,'danacenter','master', 'install.sh')
    install['command'] = install['command'].format(target, target)
    commands.append(install)

    # gen localip, nodetype
    commands.append(master_template['copy tools'])
    commands.append(makescript('prepare config', 
        'python %s %s %s'%(installtool, tooloptions(), dana_config['centerhosts'][0])))

    # config master 

    # clustername
    cfg_command = sed_set_opt('clustername', dana_config['clustername'], master_conf_file)
    commands.append(makescript('modify clustername', cfg_command))

    # zookeeper host
    zhosts = ','.join(["%s:10301"%zk for zk in dana_config['managehosts']])
    cfg_command = sed_set_opt('zookeeper_host', zhosts, master_conf_file)
    commands.append(makescript('set zookeeper host', cfg_command))

    # eagles host
    ehosts = ','.join(dana_config['managehosts'])
    cfg_command = sed_set_opt('eagles_host', ehosts, master_conf_file)
    commands.append(makescript('set eagles host', cfg_command))

    # master ip
    cfg_command = sed_set_opt('master', dana_config['centerhosts'][0], master_conf_file)
    commands.append(makescript('set master ip', cfg_command))

    # local host
    ipfile = os.path.join(package_dest, "localip")
    localip = "$(cat %s)"%ipfile
    cfg_command = sed_set_opt('local_ip', localip, master_conf_file)
    commands.append(makescript('set local ip', cfg_command))

    # start service
    commands.append(makescript('start redis-master', '%s start'%redis_master))
    commands.append(makescript('start danastork', '%s start'%danastork))
    commands.append(makescript('start yakmanage', '%s start'%yakmanage))
    return commands


def manage_commands(config):
    commands = [manage_template['prepare'], manage_template['copy files']]
    install = master_template['install']
    target = os.path.join(package_dest,'danacenter','manage', 'install.sh')
    install['command'] = install['command'].format(target, target)
    commands.append(install)

    # config zookeeper
    num = 1
    serveropt = ""
    for host in dana_config['managehosts']:
        serveropt += "server.%d=%s:10302:10303\n"%(num, host)
        num +=1

    commands.append(makescript("make zoocfg", "echo -e \"%s\" > %s"%(
        zoocfg%serveropt, manage_conf_file)))

    #start service
    commands.append(makescript('start danaeagles', '%s start'%danaeagles))
    commands.append(makescript('start zookeeper', '%s start'%zookeeper))

    return commands




def buildplan(config):
    parseconfig(config)
    common_cmds = common_commands(config)
    master_cmds = master_commands(config)
    manage_cmds = manage_commands(config)

    common_seq = core.SequenceTemplate('common_nodes', common_cmds)
    master_seq = core.SequenceTemplate('master_nodes', master_cmds)
    manage_seq = core.SequenceTemplate('manage_nodes', manage_cmds)

    
    hosts = ['%s@%s'%(dana_config['user'], x.strip()) for x in dana_config['hosts']] 
    chosts = ['%s@%s'%(dana_config['user'], x.strip()) for x in dana_config['centerhosts']]
    mhosts = ['%s@%s'%(dana_config['user'], x.strip()) for x in dana_config['managehosts']]
    
    
    mplan = core.ExecutePlan('manage_nodes', manage_seq, mhosts, 1)
    cplan = core.ExecutePlan('master_nodes', master_seq, chosts, 2)
    oplan = core.ExecutePlan('common_nodes', common_seq, hosts, 3)

    #return [mplan, cplan, oplan]
    return [manage_cmds, master_cmds, common_cmds]



