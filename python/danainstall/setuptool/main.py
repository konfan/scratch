#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import http_server
import launcher
import install_control





def main():
    conffile = ""
    
    lau = launcher.load(conffile)

    ctl = install_control.start(lau)

    server = http_server()

    server.setctl(ctl)
    server.start()

    ctl.wait()
    server.stop()
