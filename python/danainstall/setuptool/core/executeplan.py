#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from fabric.api import settings, run
import sys


def DefaultHook(runret):
    return runret.return_code, runret



class Command(object):
    def __init__(self, cmd, hookmethod = DefaultHook, title = None, 
            stdout = sys.stdout, stderr = sys.stderr):
        self.title = title or ("Command: %s"%cmd)
        self.cmd = cmd
        self.hookmethod = hookmethod
        self.retcode = None
        self.stdout = stdout
        self.stderr = stderr

    #def execute(self, host):
    #    return execute(self.__run, host = host)
    def start(self, host):
        with settings(host_string = host, warn_only = True):
            v = run(self.cmd, stdout = self.stdout, stderr = self.stderr)

        return self.hookmethod(v)
        

class ExecutePlan(object):
    def __init__(self, commands):
        self.commands = commands

    def execute(self):
        l = [command.start() for command in commands]

        return l
