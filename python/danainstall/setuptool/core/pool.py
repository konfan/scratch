#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import threading
import Queue



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
                #print('running pool.run')
                plan = self.queue.get(timeout = 2)
                plan.run()
                self.queue.task_done()
            except Queue.Empty:
                if not self.run:
                    return


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
