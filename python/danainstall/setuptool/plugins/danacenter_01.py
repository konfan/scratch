#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import core
import basedefs
import os
from utils.shortcuts import *



#TODO: gen conf file from basedefs & check
package_dest = os.path.join(basedefs.INSTALL_CACHE_DIR, 'danacenter')
installtool = os.path.join(package_dest, 'installhelper.py')

common_package = "other.tar.gz"
common_conf_file = "/etc/dt.d/yakagent.conf"


master_package = "master.tar.gz"
master_conf_file = "/etc/dt.d/yak_common.conf"

manage_package = "manage.tar.gz"
manage_conf_file = "/opt/dana/zookeeper/conf/zoo.cfg"
manage_id_file = "/opt/dana/zookeeper/data/myid"



redis_slave = "/etc/init.d/redis-slave"
redis_master = "/etc/init.d/redis-master"
yakagent = "/etc/init.d/yakagentsvrdaemon"
yakmanage = "/etc/init.d/yakmanager"
yakmanagedaemon = "/etc/init.d/yakmanagersvrdaemon"
danastork = "/etc/init.d/danastork"
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
    dana_config['password'] = config.get('common', 'adminpwd', '123456')




def tooloptions():
    m = ','.join(dana_config['managehosts'])
    c = ','.join(dana_config['centerhosts'])
    n = ','.join(dana_config['hosts'])
    d = package_dest
    return "-m %s -c %s -n %s -d %s"%(m, c, n, d)




prepare_template = {
        'prepare':makescript("prepare", "mkdir -p %s"%package_dest),
        'copy tool':makecopy('install_tool', 
            os.path.join(basedefs.DIR_PROJECT_DIR, 'utils', 'installhelper.py'), 
            installtool),
        #'sysinfo':makescript('sysinfo',
        #    'python %s %s %s'%(installtool, tooloptions(), dana_config['centerhosts'][0]))
        }

def prepare_commands():
    commands = [prepare_template['prepare'], prepare_template['copy tool']]
    commands.append(makescript('sysinfo',
        'python %s %s %s'%(installtool, tooloptions(), dana_config['centerhosts'][0])))
    return commands




common_template = {
        'copy files':makecopy("copy files", os.path.join(basedefs.PACKAGE_DIR,'danacenter', common_package),
            os.path.join(package_dest, common_package)),
        'unpack':makescript('unpack', 'cd %s && tar zxf %s'%(package_dest, common_package)),

        'install':makescript('install', "chmod a+x {0} && cd {1} && ./install.sh"),
        }

def common_commands():
    commands = [common_template['copy files'], common_template['unpack']]
    install = common_template['install']
    target = os.path.join(package_dest,'other', 'install.sh')
    install['command'] = install['command'].format(target, os.path.join(package_dest, 'other'))
    commands.append(install)

    # gen localip, nodetype
    commands.append(makecopy('install_tools', 
        os.path.join(basedefs.DIR_PROJECT_DIR, 'utils', 'installhelper.py'), 
        installtool))

    commands.append(makescript('prepare config', 
        'python %s %s %s'%(installtool, tooloptions(), dana_config['centerhosts'][0])))

    # clustername
    #cfg_command = sed_set_opt('clustername', dana_config['clustername'], common_conf_file)
    #commands.append(makescript('modify clustername', cfg_command))

    # zookeeper host
    zhosts = ','.join(["%s:10301"%zk for zk in dana_config['managehosts']])
    cfg_command = sed_set_opt('zookeeper_host', zhosts, common_conf_file)
    commands.append(makescript('set zookeeper host', cfg_command))

    # master ip
    cfg_command = sed_set_opt('master_ip', dana_config['centerhosts'][0], common_conf_file)
    commands.append(makescript('set master ip', cfg_command))

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




master_template = {
        'copy files':makecopy("copy files", 
            os.path.join(basedefs.PACKAGE_DIR,'danacenter', master_package),
            os.path.join(package_dest, master_package)),
        'unpack':makescript('unpack', 'cd %s && tar zxf %s'%(package_dest, master_package)),

        'install':makescript('install', "chmod a+x {0} && cd {1} && ./install.sh"),
        }

def master_commands():
    commands = [master_template['copy files'], master_template['unpack']]

    install = master_template['install']
    target = os.path.join(package_dest,'master', 'install.sh')
    install['command'] = install['command'].format(target, os.path.join(package_dest, 'master'))
    commands.append(install)

    # gen localip, nodetype
    commands.append(makecopy('install_tools', 
        os.path.join(basedefs.DIR_PROJECT_DIR, 'utils', 'installhelper.py'), 
        installtool))

    commands.append(makescript('prepare config', 
        'python %s %s %s'%(installtool, tooloptions(), dana_config['centerhosts'][0])))

    # config master 

    # clustername
    cfg_command = sed_set_opt('cluster_name', dana_config['clustername'], master_conf_file)
    commands.append(makescript('modify clustername', cfg_command))

    # zookeeper host
    zhosts = ','.join(["%s:10301"%zk for zk in dana_config['managehosts']])
    cfg_command = sed_set_opt('zoo_host', zhosts, master_conf_file)
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
    #cfg_command = sed_set_opt('ip', localip, master_conf_file)
    commands.append(makescript('set local ip', cfg_command))

    # start service
    commands.append(makescript('start redis-master', '%s start'%redis_master))
    commands.append(makescript('start danastork', '%s start'%danastork))
    commands.append(makescript('start yakmanage', '%s start'%yakmanage))
    commands.append(makescript('start daemon', '%s start'%yakmanagedaemon))
    commands.append(makescript('reset admin', 
        'sleep 5 && curl -s -d "name=%s&passwd=%s" "http://%s:10400/user/pwd/reset"'%('admin',
        dana_config['password'], dana_config['centerhosts'][0])))
    return commands




manage_template = {
        'copy files':makecopy("copy files", os.path.join(basedefs.PACKAGE_DIR, 'danacenter', manage_package),
            os.path.join(package_dest, manage_package)),
        'unpack':makescript('unpack', 'cd %s && tar zxf %s'%(package_dest, manage_package)),

        'install':makescript('install', "chmod a+x {0} && cd {1} && ./install.sh")
        }


def manage_commands():
    commands = [manage_template['copy files'], manage_template['unpack']]
    install = manage_template['install']
    target = os.path.join(package_dest,'manage', 'install.sh')
    install['command'] = install['command'].format(target, os.path.join(package_dest, 'manage'))
    commands.append(install)

    # config zookeeper
    num = 1
    serveropt = ""
    for host in dana_config['managehosts']:
        serveropt += "server.%d=%s:10302:10303\n"%(num, host)
        num +=1
    
    commands.append(makescript("make zoocfg", "echo -e \"%s\" > %s"%(
        zoocfg%serveropt, manage_conf_file)))

    #set myid
    ipfile = os.path.join(package_dest, "localip")
    localip = "$(cat %s)"%ipfile
    getid = r"grep %s %s|sed -e 's/server\.\(.*\)=.*/\1/' > %s"%(localip, manage_conf_file,
            manage_id_file)
    commands.append(makescript("set myid", getid))

    #start service
    commands.append(makescript('start danaeagles', '%s start'%danaeagles))
    commands.append(makescript('start zookeeper', '%s start'%zookeeper))

    return commands




def buildplan(config):
    parseconfig(config)
    common_cmds = common_commands()
    master_cmds = master_commands()
    manage_cmds = manage_commands()

    common_seq = core.SequenceTemplate('common_nodes', common_cmds)
    master_seq = core.SequenceTemplate('master_nodes', master_cmds)
    manage_seq = core.SequenceTemplate('manage_nodes', manage_cmds)

    
    hosts = ['%s@%s'%(dana_config['user'], x.strip()) for x in dana_config['hosts']] 
    chosts = ['%s@%s'%(dana_config['user'], x.strip()) for x in dana_config['centerhosts']]
    mhosts = ['%s@%s'%(dana_config['user'], x.strip()) for x in dana_config['managehosts']]
    
    
    mplan = core.ExecutePlan('manage_nodes', manage_seq, mhosts, 1)
    oplan = core.ExecutePlan('common_nodes', common_seq, hosts, 2)
    cplan = core.ExecutePlan('master_nodes', master_seq, chosts, 3)

    return [mplan, oplan, cplan]
    #return [manage_cmds, master_cmds, common_cmds]
