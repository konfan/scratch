#-*- coding: utf-8 -*-
"""open file, read and split by lines"""
from cStringIO import StringIO


class SplitLine:
    def __init__(self, fobj, maxline, blocksize = 2**22):
        self.lines = []
        self.partnum = 1
        self.tail = ''
        self.src = fobj
        self.maxline = maxline
        self.blocksize = blocksize

    def savepart(self):
        pos = 0
        while True:
            l = self.lines[pos: pos+self.maxline]
            if len(l) == self.maxline:
                with open(self.curpart(), 'w') as f:
                    f.writelines(l)
                    self.partnum += 1
                pos += self.maxline
            else:
                break
        if len(l) < self.maxline:
            self.lines = l

    def curpart(self):
        return 'part%06d'%self.partnum

    def appendtail(self):
        if self.lines:
            with open(self.curpart(), 'w') as f:
                f.writelines(self.lines)
        if self.tail:
            # save to cur partfile
            with open(self.curpart(), 'a') as f:
                f.write(self.tail)

    def cut(self):
        for block in self.readblock():
            tmp = StringIO(block).readlines()
            #tmp = sio.readlines()
            if self.tail:
                tmp[0] = self.tail + tmp[0]
                self.tail = ''
            self.lines.extend(tmp[:-1])
            if tmp[-1].rfind('\n') != len(tmp[-1]) - 1:
                self.tail = tmp[-1]
            else:
                self.lines.append(tmp[-1])

            if len(self.lines) >= self.maxline:
                self.savepart()

        self.savepart()
        self.appendtail()


    def readblock(self):
        if not self.src:
            return 
        while True:
            data = self.src.read(self.blocksize)
            if data:
                yield data
            else:
                break

    def genname(self):
        pass

def split(fname, lines):
    with open(fname,'r') as f:
        s = SplitLine(f, lines)
        s.cut()

if __name__ == '__main__':
    import sys
    split(sys.argv[1], int(sys.argv[2]))
