#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import http_server
import launcher
import install_control





def main():
    import sys
    conffile = "test.conf"
    
    lau = launcher.load(conffile)
    print(lau)

    ctl = install_control.InstallControl(lau)

    #server = http_server()

    #server.setctl(ctl)
    #server.start()

    #ctl.wait()
    #server.stop()
    launcher.danainstall.setup()
    http_server.start()
    ln = sys.stdin.readline()
    http_server.stop()


if __name__ == '__main__':
    main()
