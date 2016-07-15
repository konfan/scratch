#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import core
import basedefs
import os


package_dest = "/opt/dana/tmpinstall"
common_config = {
        "hosts":""
        }
common_package = 'common.tar.gz'


def baseconfig(config):
    global common_config
    l = config.get('common', 'nodelist')
    common_config['hosts'] = l.split(',')
    common_config['user'] = config.get('common', 'installuser')


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
            "command":"cd %s && tar zxf %s"
            },
        "install":{
            "name":"install",
            "type":"script",
            "command":"chmod a+x %s && %s"
            },
        "config":{
            "name":"config",
            "type":"script",
            "command":r"sed -i %(name)s"
            }
        }

def maketemplate():
    commands = [install_template['prepare']]
    copy_file = install_template['copy files']
    copy_file['source'] = os.path.join(basedefs.PACKAGE_DIR, common_package)
    copy_file['dest'] = os.path.join(package_dest, common_package)
    commands.append(copy_file)

    unpack = install_template['unpack']
    unpack['command'] = unpack['command']%(package_dest, common_package)
    commands.append(unpack)

    install = install_template['install']
    target = os.path.join(package_dest,'common', 'install.sh')
    install['command'] = install['command']%(target, target)
    commands.append(install)

    return core.SequenceTemplate('common', commands)

def makecentertemplate():
    pass




def buildplan(config):
    baseconfig(config)
    seqtemplate = maketemplate()
    hosts = ['%s@%s'%(common_config['user'], x.strip()) for x in common_config['hosts']]
    return [core.ExecutePlan('common', seqtemplate, hosts)]

