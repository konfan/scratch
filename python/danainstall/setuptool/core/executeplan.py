#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4



class Command(object):
    def __init__(self, cmd, callback = None, title = None):
        self.title = title or ("Command: %s"%cmd)
        self.cmd = cmd
        self.callback = callback
        self.retcode = None

    def run(self, target):
        pass


class Target(object):
    pass



class ExecutePlan(object):
    def __init__(self, commands):
        self.commands = commands
        pass

    
    def run():
        pass
