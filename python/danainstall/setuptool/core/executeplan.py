#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import collections
import vshell


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
        self.retcode, self.msg = self.function(*args)
        self.FINISHED


class Sequence(object):

    def __init__(self, name, commands, target, priority = 0, 
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
                obj = vshell.RemoteCommand(cmd, stdout = self.stdout, stderr = self.stderr)
            elif typo == 'copy':
                src, dst = command['source'], command['dest']
                obj = vshell.FileTransfer(src, dst)
            else:
                raise RuntimeError("command type incorrect")
            self.steps[name]  = Step(name, obj)
            self.steps[name].state = Step.PREPARED

    def __lt__(self, other):
        return self.priority < other.priority

    def stat(self):
        r = []
        for n, o in self.steps.items():
            tmp = {'name':n, 'state':Sequence.strcode(o.state)}
            if hasattr(o, 'retcode'):
                tmp['retcode'] = o.retcode
            r.append(tmp)

        return r

    def run(self):
        for name, step in self.steps.items():
            if step.state == Step.PREPARED:
                step.run(self.target)
                print('%s %d %s'%(name, step.retcode, step.msg))






class ExecutePlan(object):
    def __init__(self, sequences, targets = []):
        self.seqs = sequences
        self.targets = targets

    def sequences(self):
        return self.seqs


    def stats(self):
        return [seq.stat() for seq in self.seqs]


if __name__ == '__main__':
    cmd = [{'name':'test', 'type':'copy', 'source':'/opt','dest':'/opt'}]
    s = Sequence('tier1', cmd, 'fff')
    print(s.stat())
