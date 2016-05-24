from fabric.api import *
from fabric import state

def hello():
    print("hello world")


def prepare_deploy():
    local("ls")
    local("git status")


@parallel
def deploy():
    code_dir = '/opt/'
    with cd(code_dir):
        run("ls")

env.passwords = {'root@192.168.1.95:22':'server', 'root@192.168.1.93:22':'cayman'}

@task
def dowork():
    host_list = ['192.168.1.95', '192.168.1.93']
    execute(deploy, hosts = host_list)



dowork()

