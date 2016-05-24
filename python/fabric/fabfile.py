from fabric.api import *
from fabric import state

def hello():
    print("hello world")


def prepare_deploy():
    local("ls")
    local("git status")


@parallel
@roles('server2')
def deploy():
    code_dir = '/opt/'
    s = run("ls /")
    print(dir(s))
    print(s.succeeded)

#env.passwords = {'root@192.168.52.141:22':'qwe123asd'}

@task
def dowork():
    env.roledefs.update({'server':['root@192.168.52.141']})
    host_list = ['192.168.52.141']
    execute(deploy, hosts = host_list, roles=['server'])

dowork()

