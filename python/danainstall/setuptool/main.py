#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import http_server
import launcher
import install_control
import signal
from optparse import OptionParser


def initCmdLineParser():
    """
    Initiate the optparse object, add all the groups and general command line flags
    and returns the optparse object
    """

    # Init parser and all general flags
    usage = "usage: %prog [options] [--help]"
    parser = OptionParser(usage=usage, version="0.1")

    parser.add_option("-d", "--daemon", action="store_true", default=False, help="daemon mode")
    parser.add_option("-c", "--config", help="install config file", default = 'test.conf')
    parser.add_option("-D", "--debug", action="store_true", help="debug mode", default = False)


    return parser


def printOptions():
    """
    print and document the available options to the answer file (rst format)
    """

    # For each group, create a group option
    print("default")


def daemon_mode():
    http_server.start()
    http_server.wait()


def command_mode(conffile, debug = False):
    install_control.initlogger(debug)
    lau = launcher.load(conffile)

    ctl = install_control.InstallControl(lau)
    http_server.setctl(ctl)
    ctl.start()
    http_server.start()
    ctl.wait()

    http_server.wait()
    ctl.stop()
    http_server.stop()

    


def main():
    import sys
    opt = initCmdLineParser()
    if (len(sys.argv) == 1):
        opt.print_help()
        return 1

    options, args = opt.parse_args()

    install_control.initlogger(options.debug)

    if options.daemon:
        daemon_mode()
    else:
        conffile = options.config
        command_mode(conffile, options.debug)






if __name__ == '__main__':
    main()
    #daemon_mode()
