#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import paramiko
import sys, StringIO
import os
import re
import select
import time
import logging
import ringbuffer


def DefaultHook(runret):
    return runret.return_code, runret

regex = re.compile(r'(\S*)@(\S+)')


def parse_hoststring(hoststr):
    match = regex.match(hoststr)
    if not match:
        raise RuntimeError('invalid host string')
    return match.groups()



class RemoteCommand(object):
    def __init__(self, cmd, hookmethod = DefaultHook, title = None, 
            stdout = sys.stdout, stderr = sys.stderr):
        self.title = title or ("Command: %s"%cmd)
        self.cmd = cmd
        self.hookmethod = hookmethod
        self.retcode = None
        self.stdout = stdout
        self.stderr = stderr

        self.obuf = ringbuffer.FifoFileBuffer()
        self.ebuf = ringbuffer.FifoFileBuffer()


        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __call__(self, host):
        """
        call remote command
        return retcode, output, err
        """
        user, ip = parse_hoststring(host)
        self.ssh.connect(ip, username = user, timeout = 3)
        channel = self.ssh.get_transport().open_session()
        #logging.info('[%s]\t%s', host, self.cmd)
        self.stdout.write('[%s]\t%s\n'%(host, self.cmd))
        channel.exec_command(self.cmd)
        inputs = [channel.makefile(), channel.makefile_stderr()]
        output = ""
        err = ""
        while True:
            if channel.exit_status_ready():
                #print('exit code is %d'%channel.recv_exit_status())
                if channel.recv_exit_status() == 0:
                    #logging.info('[%s]\t%s Succeeded', host, self.cmd)
                    self.stdout.write('[%s]\t%s Succeeded\n'%(host, self.cmd))
                    #logging.info("Succeed")
                else:
                    logging.error('[%s]\t%s Failed, return %d', host, self.cmd, channel.recv_exit_status())
                    self.stdout.write('[%s]\t%s Failed, return %d\n'%(host, self.cmd, channel.recv_exit_status()))
                break
            rl, wl, xl = select.select([channel], [], [])
            for r in rl:
                if channel.recv_ready():
                    tmp = channel.recv(256)
                    while len(tmp) > 0:
                        self.obuf.write(tmp)
                        lines = self.obuf.readlines()
                        output = output + ''.join(lines)
                        map(self.stdout.write, lines)
                        tmp = channel.recv(256)

                if channel.recv_stderr_ready():
                    tmp = channel.recv_stderr(256)
                    while len(tmp) > 0:
                        self.ebuf.write(tmp)
                        lines = self.ebuf.readlines()
                        err = err + ''.join(lines)
                        map(self.stderr.write, lines)
                        tmp = channel.recv_stderr(256)

        return channel.recv_exit_status(), output, err


class FileTransfer(object):
    def __init__(self, localpath, remotepath, stdout = sys.stdout, stderr = sys.stderr):
        self.localpath = localpath
        self.remotepath = remotepath
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.stdout = stdout
        self.stderr = stderr

    def __call__(self, host):
        user, ip = parse_hoststring(host)
        if not os.path.isfile(self.localpath):
            raise RuntimeError('%s is no a file'%self.localpath)
        self.ssh.connect(ip, username = user, timeout = 3)
        try:
            sftp = self.ssh.open_sftp()
            self.stdout.write('[local]%s -> [%s]%s'%(self.localpath, ip, self.remotepath))
            time.sleep(2)
            trans = sftp.put(self.localpath, self.remotepath, confirm = True)
            logging.info("Succeed")
            return 0, trans.st_size, ""
        except Exception as e:
            logging.error("Failed")
            self.stderr.write(e)
            return -1, None,""


def test():
    c = RemoteCommand('yum')
    o,e = c('root@192.168.40.137')
    print o
    print e



if __name__ == '__main__':
    test()
