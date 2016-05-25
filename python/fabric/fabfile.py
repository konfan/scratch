from fabric.api import *
from fabric import state

def hello():
    print("hello world")


def prepare_deploy():
    local("ls")
    local("git status")

class Install(object):
    def __call__(self):
        with settings(warn_only = True):
            s = run("ls %s"%self.path)
            #print(dir(s))
            print(s.failed)

    def __init__(self, path):
        self.path = path

@parallel
def deploy(path):
    code_dir = '/opt/'
    ins = Install(path)
    ins()

#env.passwords = {'root@192.168.52.141:22':'qwe123asd'}
env.passwords = {'root@192.168.1.93:22':'cayman', 'root@192.168.1.95:22':'server'}

@task
def dowork(path):
    env.roledefs.update({'server':['192.168.1.93'], 'meta':['192.168.1.95']})
    #host_list = ['192.168.52.141']
    #host_list = ['192.168.1.93', '192.168.1.95']
    
    #execute(deploy, hosts = host_list, roles=['server'])
    execute(deploy, path, roles=['meta', 'server'])

if __name__ == '__main__':
    import sys
    dowork(sys.argv[1])

