#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import http_server
import launcher
import install_control
from optparse import OptionParser


def initCmdLineParser():
    """
    Initiate the optparse object, add all the groups and general command line flags
    and returns the optparse object
    """

    # Init parser and all general flags
    usage = "usage: %prog [options] [--help]"
    parser = OptionParser(usage=usage, version="0.1")

    parser.add_option("-d", "--debug", action="store_true", default=False, help="Enable debug in logging")
    parser.add_option("-c", "--config", help="install config file", default = 'test.conf')


    return parser


def printOptions():
    """
    print and document the available options to the answer file (rst format)
    """

    # For each group, create a group option
    print("default")



def main():
    import sys
    opt = initCmdLineParser()
    if (len(sys.argv) == 1):
        opt.print_help()
        return 1

    options, args = opt.parse_args()

    install_control.initlogger(options.debug)
    conffile = options.config
    
    lau = launcher.load(conffile)

    ctl = install_control.InstallControl(lau)
    ctl.start()
    ctl.wait()

    #server = http_server()

    #server.setctl(ctl)
    #server.start()

    #ctl.wait()
    #server.stop()
    #launcher.danainstall.setup()
    #http_server.start()
    ln = sys.stdin.readline()
    http_server.stop()
    ctl.stop()



if __name__ == '__main__':
    main()
