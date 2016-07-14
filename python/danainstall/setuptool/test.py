#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from core import *
import sys
import time
import tty
from utils import shell


class Tmppaln(object):
    def __init__(self, level, plan):
        self.level = level
        self.plan = plan

    def __lt__(self, other):
        return self.level < other.level

    def install(self):
        for t in self.plan.tasks():
            print(
                "%s:%s"%(t.target, t.output()[0]))


class mod(object):
    pass


def seqtest():
    import collections
    i,o,e = shell.savetty()
    Pool.poolsize = 3
    p = Pool()
    cmd = [{'name':'test', 'type':'script', 'command':'ls /root'},
            {'name':'copyfile', 'type':'copy', 'source':'/root/get-pip.py', 'dest':'/root/get-pip.py'}]

    a = SequenceTemplate('tier1', cmd)

    plan = ExecutePlan('test', a, ['root@192.168.1.95', 'root@192.168.1.92'])
    print(plan.sequences())
    for sl in plan.sequences():
        p.add(sl)

    sys.stdin.readline()
    p.stop()
    shell.loadtty(i,o,e)









def test():
    commands = [
            "python /root/test.py"
            ]

    pool = Pool()
    testplan = ExecutePlan(commands,
            ['root@192.168.1.95','root@192.168.1.92'],
            0)

    for t in testplan.tasks():
        pool.add(t)

    while True:
        pool.add(Tmppaln(0, testplan))
        time.sleep(5)
    

    sys.stdin.readline() 
    pool.stop()
    for r in testplan.status():
        print r




def test_old_main():
    import termios
    oldsettings = (termios.tcgetattr(sys.stdin),
            termios.tcgetattr(sys.stdout),
            termios.tcgetattr(sys.stderr))
    try:
        test()
    except KeyboardInterrupt:
        raise
    finally:
        print('restore tty')
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldsettings[0])
        termios.tcsetattr(sys.stdout, termios.TCSADRAIN, oldsettings[1])
        termios.tcsetattr(sys.stderr, termios.TCSADRAIN, oldsettings[2])
    

if __name__ == '__main__':
    import logging
    logging.basicConfig(format = '%(asctime)s\t%(levelname)s\t%(module)s::%(name)s::%(message)s')
    seqtest()
