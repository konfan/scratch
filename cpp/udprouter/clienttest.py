# coding: utf-8
# !/usr/bin/python
import socket
import sys



def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    l = 0
    for arg in sys.argv:
        u = s.sendto(arg, ('127.0.0.1',9934))
        l += u
    print l
    

if __name__ == '__main__':
    main()
