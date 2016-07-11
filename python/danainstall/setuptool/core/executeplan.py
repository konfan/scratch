#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


class Step(object):
    def __init__(self, name, function):
        self.name = name
        if function and not callable(function):
            raise RuntimeError("object % is not callable"%function)
        self.function = function


    def run(self, *args):
        self.function(args)


class Sequence(object):
    def __init__(self, steps, target, priority):
        pass




class ExecutePlan(object):
    def __init__(self, sequences, targets):
        pass

