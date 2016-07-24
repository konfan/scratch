#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import socket
import sys
import os
from optparse import OptionParser

dana_config = {}


def get_localhost_ip(beacon = None):
    if not beacon:
        return _get_innet_ip()

    target = (beacon)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((target, 0))
        loc_ip = s.getsockname()[0]
        return loc_ip
    except Exception as e:
        raise IOError('Local IP address discovery failed: %s'%e)
    finally:
        s.close()


def get_nodetype(ip):
    iscenter = lambda i: i in dana_config['centerhosts']
    ismanage = lambda i: i in dana_config['managehosts']
    typecheck = {
            1:lambda x: iscenter(x) and x == dana_config['centerhosts'][0],
            2:lambda x: iscenter(x) and x != dana_config['centerhosts'][0],
            3:lambda x: ismanage(x) and not typecheck[1](x) and not typecheck[2](x),
            4:lambda x: ismanage(x) and typecheck[1](x),
            5:lambda x: ismanage(x) and typecheck[2](x)
            }
    for typo, func in typecheck.items():
        if func(ip):
            return typo

    return 6 #not 1~5


def initParser():
    usage = "usage: %prog [options] [--help]"
    parser = OptionParser(usage=usage, version="0.1")

    parser.add_option("-m", "--manage",  help="manage nodes", default = "")
    parser.add_option("-c", "--center", help="center nodes", default = "")
    parser.add_option("-n", "--nodes", help="common nodes", default = "")
    parser.add_option("-d", "--dir", help = "temp file directory", default = ".")


    return parser



def main():
    global dana_config
    opt = initParser()
    options, args = opt.parse_args()

    dana_config['centerhosts'] = options.center.split(',')
    dana_config['managehosts'] = options.manage.split(',')
    dana_config['hosts'] = options.nodes.split(',')

    print(dana_config)
    path = options.dir
    if not os.path.exists(path):
        os.mkdir(path, 0o700)
    ipbase = args[0]
    myip = get_localhost_ip(ipbase)
    nodetype = str(get_nodetype(myip))

    ipfile = os.path.join(path, "localip")
    typefile = os.path.join(path, "nodetype")
    with open(ipfile, 'w') as f:
        f.write(myip)

    with open(typefile, 'w') as f:
        f.write(str(nodetype))

    return 0



if __name__ == '__main__':
    main()
