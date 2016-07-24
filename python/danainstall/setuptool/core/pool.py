#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import threading
import Queue
import logging
import traceback



class Pool(object):
    poolsize = 10
    def __init__(self):
        self.run = True
        self.queue = Queue.PriorityQueue()
        self.threads = [threading.Thread(target = self._run) for i in range(self.poolsize)]
        for th in self.threads:
            th.daemon = True
            th.start()

    def _run(self):
        while self.run:
            try:
                seq = self.queue.get(timeout = 2)
            except Queue.Empty:
                if self.run:
                    continue
                else:
                    return
            try:
                #print("executeing %s %s %s"%(seq.name, seq.target, seq))
                seq.run()
                #print("seq %s %s %s done"%(seq.name, seq.target, seq))
            except Exception as e:
                logging.getLogger("pool").error(e)
                logging.getLogger('pool').error(traceback.format_exc())
                return
            finally:
                self.queue.task_done()


    def add(self, execplan):
        self.queue.put(execplan)

    def stop(self):
        self.queue.join()
        self.run = False


class Tmppaln(object):
    """ for test """
    def __init__(self, level = 0):
        self.level = level

    def __lt__(self, other):
        return self.level < other.level

    def run(self):
        import time
        print(self.level)
        time.sleep(10)


def test():
    from random import randint
    vl = [ Tmppaln(i) for i in range(20)]
    u = Pool()
    u.poolsize = 10
    [u.add(v) for v in vl]
    u.stop()


def test2():
    t = ExecutePlan(seqs, hosts)
    p = Pool()
    for seq in t.sequences():
        p.add(seq)


if __name__ == '__main__':
    test()
