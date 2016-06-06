#-*- coding: utf-8
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import SocketServer
import urlparse
import os
import tempfile

from BaseHTTPServer import BaseHTTPRequestHandler


def readAuthorizedKeys():
    home = os.path.expanduser("~")
    authfile = '%s/.ssh/authorized_keys'%home
    keys = set()
    if os.path.exists(authfile):
        with open(authfile, 'r') as f:
            for x in f.readlines():
                schema, pubkey, host = x.split()
                keys.add(pubkey)
    return keys




def addSSHKey(pubkeyfile):
    keys = readAuthorizedKeys()
    with open(pubkeyfile, 'r') as f:
        text = f.read()
        schema, pubkey, host = text.split()
        if schema != "ssh-rsa":
            raise ValueErr("wrong pub key schema")
        home = os.path.expanduser("~")
        if not home:
            raise IOError("cant't open user's home dir")

        home = '%s/.ssh'%home
        if not os.path.exists(home):
            os.mkdir(home, 0700)

        if pubkey not in keys:
            with open('%s/authorized_keys'%home, "a+") as sshfile:
                if text[-1] != '\n':
                    text += '\n'
                sshfile.write(text)



class SetKeyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        msg = "Forbidden method: GET\n"
        self.sendError(401, msg)

    def do_POST(self):
        basepath = urlparse.urlparse(self.path).path
        dispatch = { '/addkey': self.addKey,
                    '/shutdown': self.stop }
        try:
            dispatch[basepath]()
        except KeyError:
            self.sendError(401, "invalid path")


    def sendError(self, code, msg):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length",len(msg))
        self.end_headers()
        self.wfile.write(msg)

    def addKey(self):
        dlen = int(self.headers.get("Content-Length", 0))
        fd,tmpfile = tempfile.mkstemp()
        os.write(fd, self.rfile.read(dlen))
        os.close(fd)
        try:
            addSSHKey(tmpfile)
            self.send_response(200)
        except Exception as e:
            self.sendError(500, str(e))
        finally:
            os.remove(tmpfile)

    def stop(self):
        import thread
        self.send_response(200)
        thread.start_new_thread(shutdown, tuple())

httpd_ins = None

def shutdown():
    global httpd_ins
    httpd_ins.shutdown()


def main():
    global httpd_ins
    port = 8999
    SocketServer.TCPServer.allow_reuse_address = True
    httpd = SocketServer.TCPServer(('',port), SetKeyHandler)
    httpd_ins = httpd
    print('serving at ', port)
    httpd.serve_forever()



if __name__ == '__main__':
    main()
    #addSSHKey('/root/.ssh/id_rsa.pub')
