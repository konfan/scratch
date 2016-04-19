import os


def coroutine(f):
    data = yield
    while True:
        data = yield f()


def 



