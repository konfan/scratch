
class Foo(object):

    def __init__(self, i):
        self._data = i

    def warning(f):
        print "warning"
        return f


    def calc(self, i):
        return self._data + i

    @warning
    def wcalc(self, i):
        return self._data + i



if __name__ == '__main__':
    f = Foo(10)
    f.calc(1)
    f.wcalc(1)




