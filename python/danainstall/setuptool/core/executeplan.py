#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import collections
import pshell
import logging


class Step(object):
    UNINIT = -1
    PREPARED = 0
    RUNNING = 1
    FINISHED = 2

    @classmethod
    def strcode(cls, code):
        if code == cls.PREPARED:
            return 'prepared'
        elif code == cls.RUNNING:
            return 'running'
        elif code == cls.FINISHED:
            return 'finished'
        elif code == cls.UNINIT:
            return 'uninit'
        raise RuntimeError('invalid code %d'%code)

    def __init__(self, name, function):
        self.name = name
        if function and not callable(function):
            raise RuntimeError("object % is not callable"%function)
        self.function = function
        self.state = Step.UNINIT


    def run(self, *args):
        self.retcode, self.msg, self.err = self.function(*args)
        self.FINISHED


class Sequence(object):
    def __init__(self, name, commands, target = "", priority = 0, 
            stdout = sys.stdout, stderr = sys.stderr):
        self.name = name
        self.target = target
        self.priority =  priority
        self.steps = collections.OrderedDict()
        self.stdout = stdout
        self.stderr = stderr
        for command in commands:
            name, typo = command['name'], command['type']
            if typo == 'script':
                cmd = command['command']
                obj = pshell.RemoteCommand(cmd, stdout = self.stdout, stderr = self.stderr)
            elif typo == 'copy':
                src, dst = command['source'], command['dest']
                obj = pshell.FileTransfer(src, dst, self.stdout, self.stderr)
            else:
                raise RuntimeError("command type incorrect")
            self.steps[name]  = Step(name, obj)
            self.steps[name].state = Step.PREPARED

    def __lt__(self, other):
        return self.priority < other.priority

    def setTarget(self, target):
        self.target = target

    def stat(self):
        r = []
        for n, o in self.steps.items():
            tmp = {'name':n, 'state':Sequence.strcode(o.state)}
            if hasattr(o, 'retcode'):
                tmp['retcode'] = o.retcode
            r.append(tmp)

        return r

    def run(self):
        if not self.target:
            raise RuntimeError("invalid target")

        for name, step in self.steps.items():
            print('running %s'%self.name)
            if step.state == Step.PREPARED:
                step.run(self.target)
                #print('%s %d %s'%(name, step.retcode, step.msg))

class PlanLogger(object):
    def __init__(self, logger, loglevel = logging.INFO):
        self.logger = logger
        self.logger.setLevel(logging.DEBUG)
        self.level = loglevel

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line)
        #self.logger.log(self.level, buf)

    def flush(self):
        pass



class ExecutePlan(object):
    def __init__(self, name, seqtemplate, targets = []):
        self.seqs = []
        self.name = name
        for t in targets:
            logger = PlanLogger(logging.getLogger('%s:%s'%(name, t)), logging.DEBUG)
            self.seqs.append(Sequence(seqtemplate.name, seqtemplate.commands, t,
                stdout = logger, stderr = logger))

    def sequences(self):
        return self.seqs


    def stats(self):
        return [seq.stat() for seq in self.seqs]



class SequenceTemplate(object):
    def __init__(self, name, commands):
        self.name = name
        self.commands = commands
        self.check()

    @staticmethod
    def __check_command(cmd):
        """
        cmd = {'name':"$name", 'type':"script", 'command':"shell command"}
        or
        cmd = {'name':"$name", 'type':"copy", 'source':"$source path", 'dest':"$destpath"}
        """
        assert(cmd['name'])
        assert(cmd['type'] == 'script' or cmd['type'] == 'copy')
        if cmd['type'] == 'script':
            assert(cmd['command'])
        elif cmd['type'] == 'copy':
            assert(cmd['source'] and cmd['dest'])

    def check(self):
        map(self.__check_command, self.commands)
        return True



if __name__ == '__main__':
    cmd = [{'name':'test', 'type':'copy', 'source':'/opt','dest':'/opt'}]
    s = SequenceTemplate('test', cmd)
    #s = Sequence('tier1', cmd, 'fff')
    #print(s.stat())
