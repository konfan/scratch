#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import fabric


class Command(object):
    def __init__(self, cmd, hookmethod = None, title = None):
        self.title = title or ("Command: %s"%cmd)
        self.cmd = cmd
        self.callback = callback
        self.retcode = None

    #def execute(self, host):
    #    return execute(self.__run, host = host)

    def exec(self, host):
        with settings(host_string = host):
            v = run(self.cmd)

        hook = hookmethod(v)
        return hook()
        


class DefaultHook(object):
    def __init__(self, runret):
        self.ret = runret

    def __call__(self):
        if self.ret.succeeded:
            return self.ret

        else:
            return ''
#class Target(object):
#    """
#    save host ip
#    """
#    def __init__(self, hosts = None, roles = []):
#        self.host = ip
#        self.roles = roles



class ExecutePlan(object):
    def __init__(self, commands):
        self.commands = commands
        pass

    def run():
        pass
