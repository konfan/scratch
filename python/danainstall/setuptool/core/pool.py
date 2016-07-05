import threading
import Queue



class Pool(object):
    poolsize = 10
    def __init__(self):
        self.run = True
        self.queue = Queue.PriorityQueue()
        self.threads = [threading.Thread(target = self._run) for i in range(self.poolsize)]
        for th in self.threads:
            th.start()

    def _run(self):
        while True:
            try:
                plan = self.queue.get(timeout = 1)
                plan.install()
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
    def __init__(self, level = 0):
        self.level = level

    def __lt__(self, other):
        return self.level < other.level

    def install(self):
        print(self.level)


def test():
    from random import randint
    vl = [ Tmppaln(i) for i in [randint(0,100) for ii in range(100)]]
    u = Pool()
    u.poolsize = 10
    [u.add(v) for v in vl]
    u.stop()



if __name__ == '__main__':
    test()
