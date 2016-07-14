#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from fabric.api import settings, run, put
import sys, StringIO
import time


def DefaultHook(runret):
    return runret.return_code, runret



class RemoteCommand(object):
    def __init__(self, cmd, hookmethod = DefaultHook, title = None, 
            stdout = sys.stdout, stderr = sys.stderr):
        self.title = title or ("Command: %s"%cmd)
        self.cmd = cmd
        self.hookmethod = hookmethod
        self.retcode = None
        self.stdout = stdout
        self.stderr = stderr

    def __call__(self, host):
        with settings(host_string = host, warn_only = True ):
            v = run(self.cmd, shell = False, stdout = self.stdout, stderr = self.stderr)

        return self.hookmethod(v)

class FileTransfer(object):
    def __init__(self, localpath, remotepath):
        self.localpath = localpath
        self.remotepath = remotepath

    def __call__(self, host):
        with settings(host_string = host, warn_only = True ):
            time.sleep(2)
            v = put(local_path = self.localpath, remote_path = self.remotepath)
        return v,v


class Readbuffer(StringIO.StringIO):
    def __init__(self, buf = ''):
        StringIO.StringIO.__init__(self, buf)
        self.readpos = 0

    def readx(self):
        data = self.getvalue()
        start, end = self.readpos, len(data)
        self.readpos = end
        return data[start:end]

class PlanTask(object):
    def __init__(self, commands, target, level = 10):
        self.stdout = Readbuffer()
        self.stderr = Readbuffer()
        self.retcode = []
        self.commands = [RemoteCommand(cmd, stdout = self.stdout, stderr = self.stderr) \
                for cmd in commands]
        self.target = target
        self.level = level

    def __lt__(self, other):
        return self.level < other.level

    def run(self):
        for c in self.commands:
            self.retcode.append(c.start(self.target))
         

    def output(self):
        return self.stdout.readx(), self.stderr.readx()

    def status(self):
        return self.retcode


        

class ExecutePlan(object):
    def __init__(self, commands, targets, level):
        self.commands = commands
        self.level = level
        self.targets = targets
        self.rtable = {}

    def tasks(self):
        if not self.rtable:
            for target in self.targets:
                self.rtable[target] = PlanTask(self.commands, target, self.level)
        return self.rtable.values()

    def status(self):
        """ return all tasks running state 
        """
        return [task.status() for task in self.rtable.values()]



def testPlan(commands, targets):
    pass

def testCommand(cmd, target):
    from threading import Thread
    from StringIO import StringIO
    import os
    r,w = os.pipe()
    #infile = os.fdopen(r)
    #outfile= os.fdopen(w, 'w')
    outfile = Readbuffer()
    #outfile = StringIO()
    login = RemoteCommand('ls', stdout = None)
    login.start(target)
    c = RemoteCommand(cmd, stdout = outfile)
    th = Thread(target = c.start, args = (target,))
    th.start()
    for i in range(10):
        yield outfile.readx()
    th.join()
    print(outfile.readx())
    print('before return')
    print(outfile.getvalue())
    return


if __name__ == '__main__':
    import sys, os
    path = os.path.abspath(sys.argv[1])
    f = FileTransfer(path, '/home/%s'%sys.argv[1])
    print(f.start(sys.argv[2]))
