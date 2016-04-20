# -*- coding:utf-8 -*-
# python 奇怪的 closure 现象
# 下面第一个函数是可以正常运行的
# 但是第二个会报错, 貌似在 = 后 n 就不是 closure 而是被解释为一个新的变量

def fibonacci(n):
    def ret():
        return n+1
    return ret


def fibonacci2(n):
    def ret():
        n += 1
        return n
    return ret




def main():
    x = fibonacci(0)
    x()
    y = fibonacci2(0)
    y()

if __name__ == '__main__':
    main()
