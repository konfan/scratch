#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import core
import basedefs
import os
from utils.shortcuts import *


package_dest = basedefs.INSTALL_CACHE_DIR

common_config = {
        "hosts":[]
        }
#common_package = 'common.tar.gz'
common_package, verison = basedefs.findpackage(basedefs.PACKAGE_DIR,'common')


def baseconfig(config):
    global common_config
    l = config.get('common', 'nodes')
    common_config['hosts'] = filter(lambda x:x, l.split(','))
    common_config['user'] = config.get('common', 'installuser', 'root')



flimit_tuning = """*    soft    nofile  90000
*   hard    nofile  1000000
*   soft    nproc   65535
*   hard    nproc   65535
"""




tcp_tuning = """net.ipv4.tcp_syn_retries=2
net.ipv4.tcp_keepalive_time=600
net.ipv4.tcp_keepalive_probes=5
net.ipv4.tcp_fin_timeout=30
net.ipv4.tcp_max_syn_backlog=4096
net.ipv4.tcp_syncookies=1
"""



install_template = {
        "prepare":{
            "name":"prepare",
            "type":"script",
            "command":"mkdir -p %s"%package_dest
            },
        "copy files":{
            "name":"copy files",
            "type":"copy",
            "source":"%s",
            "dest":"%s",
            },
        "unpack":{
            "name":"unpack",
            "type":"script",
            "command":"cd %s && tar zxf %s"%(package_dest, common_package)
            },
        "install":{
            "name":"install",
            "type":"script",
            "command":"chmod a+x {0} && cd {1} && ./install.sh"
            },

        "tuning":{}
        }



def maketemplate():
    commands = [install_template['prepare']]
    copy_file = install_template['copy files']
    copy_file['source'] = os.path.join(basedefs.PACKAGE_DIR, common_package)
    copy_file['dest'] = os.path.join(package_dest, common_package)
    commands.append(copy_file)

    unpack = install_template['unpack']
    commands.append(unpack)

    install = install_template['install']
    target = os.path.join(package_dest,'common', 'install.sh')
    install['command'] = install['command'].format(target, os.path.join(package_dest, 'common'))
    commands.append(install)

    commands.append(makescript("tuning limit", "echo -e \"%s\" > /etc/security/limits.d/10-dana_limit_tuning.conf"%flimit_tuning))
    commands.append(makescript("tuning network", "echo -e \"%s\" > /etc/sysctl.d/dana_tcp_tuning.conf"%tcp_tuning))
    commands.append(makescript("apply tuning", "sysctl --system"))

    return core.SequenceTemplate('common', commands)




def buildplan(config):
    baseconfig(config)
    seqtemplate = maketemplate()
    hosts = ['%s@%s'%(common_config['user'], x.strip()) for x in common_config['hosts']]
    return [core.ExecutePlan('common', seqtemplate, hosts)]
