#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import collections
import pshell
import logging
from ringbuffer import FifoFileBuffer


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
        self.state = self.RUNNING
        self.retcode, self.msg, self.err = self.function(*args)
        self.state = self.FINISHED


class Sequence(object):
    class StreamDup(object):
        def __init__(self, stream):
            self.stream = stream
            self.buf = FifoFileBuffer()

        def write(self, buf):
            #print('writing************************%s'%buf)
            self.buf.write(buf)
            self.stream.write(buf)

        def flush(self):
            pass

        def read(self, size = None):
            #print('reading ---------------------------------')
            return self.buf.read(size)
    
    def __init__(self, name, commands, target = "", priority = 0, 
            stdout = sys.stdout, stderr = sys.stderr):
        self.name = name
        self.target = target
        self.priority =  priority
        self.steps = collections.OrderedDict()
        self.stdout = Sequence.StreamDup(stdout)
        self.stderr = Sequence.StreamDup(stderr)
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

    def __str__(self):
        return str({'name':self.name,
            'commands':[x.name for x in self.steps.values()]})


    def setTarget(self, target):
        self.target = target

    def stat(self):
        ret = {'host':self.target,
                'output':self.stdout.read(),
                'error':self.stderr.read(),
                'title':self.name,
                'success':[],
                'failed':[]
                }
        r = []
        for n, o in self.steps.items():
            #tmp = {'name':n, 'state':Step.strcode(o.state)}
            if hasattr(o, 'retcode'):
                if o.retcode == 0:
                    ret['success'].append(n)
                else:
                    ret['failed'].append(n)

        return ret

    def finished(self):
        unfinished = filter(lambda x: x != Step.FINISHED, 
                [step.state for step in self.steps.values()])
        return len(unfinished) == 0



    def run(self):
        if not self.target:
            raise RuntimeError("invalid target")

        for name, step in self.steps.items():
            #print('running %s'%self.name)
            if step.state == Step.PREPARED:
                step.run(self.target)
                #print('%s %d %s'%(name, step.retcode, step.msg))


class PlanLogger(object):
    def __init__(self, logger, loglevel = logging.INFO):
        self.logger = logger
        #self.logger.setLevel(logging.DEBUG)
        self.level = loglevel

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line)
        #self.logger.log(self.level, buf)

    def flush(self):
        pass



class ExecutePlan(object):
    DEFAULT_PRIORITY = 99999
    def __init__(self, name, seqtemplate, targets = [], priority = DEFAULT_PRIORITY):
        self.seqs = []
        self.name = name
        self.priority = priority
        self.targets = targets
        for t in targets:
            logger = PlanLogger(logging.getLogger('%s:%s'%(name, t)), logging.INFO)
            self.seqs.append(Sequence(seqtemplate.name, seqtemplate.commands, t,
                priority = self.priority, stdout = logger, stderr = logger))

    def sequences(self):
        return self.seqs


    def stats(self):
        return [seq.stat() for seq in self.seqs]

    def finished(self):
        for seq in self.seqs:
            if not seq.finished():
                return False
        return True
                


    def __str__(self):
        import json
        return json.dumps([(x.target, str(x)) for x in self.sequences()], indent = 2)

        



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
