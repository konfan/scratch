# -*- coding: utf-8 -*-
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import grp
import os
import pwd
import paramiko
import subprocess
import socket
from StringIO import StringIO


def host_iter(config):
    for key, value in config.iteritems():
        if key.endswith("_HOST"):
            host = value.split('/')[0]
            if host:
                yield key, host
        if key.endswith("_HOSTS"):
            for i in value.split(","):
                host = i.strip().split('/')[0]
                if host:
                    yield key, host


def hosts(config):
    result = set()
    for key, host in host_iter(config):
        result.add(host)
    return result


def get_current_user():
    try:
        user = pwd.getpwnam(os.getlogin())
        uid, gid = user.pw_uid, user.pw_gid
    except OSError:
        # in case program is run by a script
        uid, gid = os.getuid(), os.getgid()
    return uid, gid


def get_current_username():
    uid, gid = get_current_user()
    user = pwd.getpwuid(uid).pw_name
    group = grp.getgrgid(gid).gr_name
    return user, group


def split_hosts(hosts_string):
    hosts = set()
    for host in hosts_string.split(','):
        shost = host.strip()
        if shost:
            hosts.add(shost)
    return hosts


def makescript(name, command):
    return {
            'name':name,
            'type':'script',
            'command':command
            }

def makecopy(name, src, dst):
    return {
            'name':name,
            'type':'copy',
            'source':src,
            'dest':dst
            }

def sed_set_opt(label, value, filo):
    return r'sed -i "s/\(^\s*%(label)s\s*=\).*/\1 %(value)s/" %(file)s'%{
            'label':label, 'value':value, 'file':filo}

SSH_OK = 1
SSH_NOAUTH = 2
SSH_FAILED = 3

def testssh(host):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username='root', timeout=2 )
        return SSH_OK 
    except paramiko.ssh_exception.AuthenticationException:
        return SSH_NOAUTH
    except (paramiko.ssh_exception.SSHException, 
            paramiko.ssh_exception.NoValidConnectionsError,
            socket.timeout):
        return SSH_FAILED
    finally:
        client.close()


def ssh_key_gen(keyfile=os.path.expanduser("~/.ssh/id_rsa")):
    """
    local
    """
    cmd = "/usr/bin/ssh-keygen -q -f %s -t rsa -N"%keyfile
    args = cmd.split()
    args.append("")
    
    p = subprocess.Popen(args, stdout = subprocess.PIPE, stdin = subprocess.PIPE, 
            close_fds = True, bufsize=0)
    p.communicate()
    return keyfile, '%s.pub'%keyfile



def ssh_key_copy(pkey, host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username='root', password = password, timeout=2)
    i,o,e = client.exec_command("mkdir -p ~/.ssh && chmod 700 ~/.ssh")
    o.read(), e.read()
    cmd = "echo \"%s\" >> ~/.ssh/authorized_keys"%pkey
    i,o,e = client.exec_command(cmd)
    o.read(), e.read()
    i,o,e = client.exec_command("chmod 600 ~/.ssh/authorized_keys")
    o.read(), e.read()

def ssh_read_key(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username='root', password = password, timeout=2)
    i,o,e = client.exec_command("cat ~/.ssh/id_rsa.pub")
    if e.read():
        i,o,e = client.exec_command("ssh-keygen -q -f ~/.ssh/id_rsa -t rsa -N ''")
    i,o,e = client.exec_command("cat ~/.ssh/id_rsa.pub")
    return o.read()




def baseconfigfile(fpath):
    basefile = """
[common]
clustername = myname
installuser = root
nodes = 192.168.40.130
#nodes = 192.168.40.137, 192.168.40.138
adminpwd = 999999



[danacenter]
centernodes = 192.168.40.130
managenodes = 192.168.40.130


[eagles]
hosts = 192.168.40.130

[crab]
hosts = 192.168.3.98

[stork]
hosts = 192.168.3.22

[leopard]
hosts = 192.168.1.95

[dodo]
hosts = 192.168.1.22
"""
    with open(fpath, 'w') as f:
        f.write(basefile)

