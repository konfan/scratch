#-*- coding: utf-8

#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import SocketServer
import threading
import urlparse
import os,sys
import tempfile
import errno
import re
import socket, ssl
import datetime
import traceback
import cgi
import json
import paramiko
import basedefs
import ConfigParser
import signal
import launcher
import install_control
import http_server
from BaseHTTPServer import BaseHTTPRequestHandler
from json import *
from utils import shell
from utils import shortcuts

NetWorkIOError = (socket.error, ssl.SSLError, OSError)

current_path = os.path.dirname(os.path.abspath(__file__))

ipadder = ['192.168.1.232', '192.168.1.233', '192.168.1.234', '192.168.1.235', '192.168.1.236', '192.168.1.237', '192.168.1.238', '192.168.1.239', '192.168.1.240']

controller = None


def setctl(installctl):
    global controller 
    controller = installctl


def getparam(item, params):
    """
    for cgi.parse
    """
    return params[item][0]


class LocalServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True
    global ipadder
    def close_request(self, request):
        try:
            request.close()
        except Exception:
            pass

    def finish_request(self, request, client_address):
        try:
            self.RequestHandlerClass(request, client_address, self)
        except NetWorkIOError as e:
            if e[0] not in (errno.ECONNABORTED, errno.ECONNRESET, errno.EPIPE):
                raise
    def handle_error(self, *args):
        """make ThreadingTCPServer happy"""
        etype, value = sys.exc_info()[:2]
        if isinstance(value, NetWorkIOError) and 'bad write retry' in value.args[1]:
            etype = value = None
        else:
            del etype, value
            SocketServer.ThreadingTCPServer.handle_error(self, *args)



class Http_Handler(BaseHTTPRequestHandler):
    deploy_proc = None
    
    def address_string(self):
        return '%s:%s' % self.client_address[:2]

    def send_response(self, mimetype, data):
        self.wfile.write(('HTTP/1.1 200\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: %s\r\nContent-Length: %s\r\n\r\n' % (mimetype, len(data))).encode())
        self.wfile.write(data)

    def send_not_found(self):
        self.wfile.write(b'HTTP/1.1 404\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n404 Not Found')

    def send_file(self, filename, mimetype):
        try:
            with open(filename, 'rb') as fp:
                data = fp.read()
            tme = (datetime.datetime.today()+datetime.timedelta(minutes=330)).strftime('%a, %d %b %Y %H:%M:%S GMT')
            self.wfile.write(('HTTP/1.1 200\r\nAccess-Control-Allow-Origin: *\r\nCache-Control:public, max-age=31536000\r\nExpires: %s\r\nContent-Type: %s\r\nContent-Length: %s\r\n\r\n' % (tme, mimetype, len(data))).encode())
            self.wfile.write(data)
        except:
            self.wfile.write(b'HTTP/1.1 404\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n404 Open file fail')

    def req_index_handler(self):
        req = urlparse.urlparse(self.path).query
        reqs = urlparse.parse_qs(req, keep_blank_values=True)

        index_path = os.path.join(current_path, 'install_ui', "index.html")
        with open(index_path, "r") as f:
            index_content = f.read()

        data = index_content.decode('utf-8').encode('utf-8')
        self.send_response('text/html', data)

    def parse_POST(self):
        try:
            mtype, pdict = cgi.parse_header(self.headers['content-type'])
            if mtype == 'multipart/form-data':
                params = cgi.parse_multipart(self.rfile, pdict)
            elif mtype == 'application/x-www-form-urlencoded':
                l = int(self.headers['content-length'])
                params = cgi.parse_qs(self.rfile.read(l), keep_blank_values = 1)
            elif mtype == 'application/json':         
                l = int(self.headers['content-length'])
                data = self.rfile.read(l)
                params = json.loads(data)
            else:
                params = {}
        except KeyError:
            return {}
        return params



    def checkip(self, params):
        try:
            host = getparam('ip', params)
        except KeyError:
            self.send_response("application/json", json.dumps({'code':400, "msg":"bad request"}))
            return

        code, out = shell.execute("ping -q -W 1 -c 1 %s"%host,
                can_fail=False, use_shell=True, log=False)
        if code != 0:
            self.send_response("application/json", json.dumps({'code':403, "msg":"host unreachable"}))
            return

        # test ssh
        code =  shortcuts.testssh(host)
        if code == shortcuts.SSH_OK:
            self.send_response('application/json', json.dumps({'code':200, 'msg':'host ready'}))
        elif code == shortcuts.SSH_NOAUTH:
            self.send_response("application/json", json.dumps({'code':401, 'msg':'need login'}))
        elif code == shortcuts.SSH_FAILED:
            self.send_response("application/json", json.dumps({'code':403, 'msg':'ssh service exception'}))
        return


    def login(self, params):
        try:
            host = getparam('ip', params)
            user = getparam('username',params)
            pwd = getparam('password',params)
        except KeyError:
            self.send_response("application/json", json.dumps({'code':400, "msg":"bad request"}))
            return

        try:
            pri, pub = shortcuts.ssh_key_gen()
            with open(pub, 'r') as f:
                shortcuts.ssh_key_copy(f.read(), host, user, pwd)
        except:
            self.send_response("application/json", json.dumps({'code':500, "msg":"set ssh-id failed"}))
            return

        self.send_response('application/json', json.dumps({'code':200, 'ret':[host, user, pwd]}))



    def progress(self, params):
        status = controller.status()
        output = {}
        for pst in status:
            for seqst in pst:
                ip = seqst['host'][seqst['host'].find('@')+1:]
                msg = seqst['output']
                err = len(seqst['failed']) > 0
                if not output.has_key(ip):
                    output[ip] = {"msg":msg, "err":err}
                else:
                    output[ip]['msg'] = ''.join([output[ip]['msg'], msg])
                    output[ip]['err'] = output[ip]['err'] and err

        #msg = json.dumps(output, indent=2)
        #msg = json.dumps(status, indent=2)
        f = [plan for plan in controller.planlist if not plan.finished()]
        finished = len(f) == 0

        resp = {'info':output, 'finished':finished}

        self.send_response('application/json',json.dumps(resp, indent = 2))

    def install(self, params):
        try:
            master = [ s.strip() for s in getparam('master', params).split(';')]
            manage = [ s.strip() for s in getparam('zoo', params).split(';')]
            other = [ s.strip() for s in getparam('other',params).split(';')]
            engine = [ s.strip() for s in getparam('engine',params).split(';')]
            user = getparam('uname', params)
            pwd = getparam('pwd', params)
            clustername = getparam('clusterName', params)
        except KeyError:
            self.send_response("application/json", json.dumps({'code':400, "msg":"bad request"}))
            return


        # save to config file
        conffile = os.path.join(basedefs.DIR_PROJECT_DIR, 'install.conf')
        shortcuts.baseconfigfile(conffile)
        config = ConfigParser.SafeConfigParser()
        config.read(conffile)

        allnodes = list(set(filter(lambda x:x, master + manage + other)))
        #common
        config.set('common', 'clustername', clustername)
        config.set('common', 'nodes', ','.join(allnodes))
        config.set('common', 'adminpwd', pwd)
        #danacenter
        config.set('danacenter', 'centernodes', ','.join(master))
        config.set('danacenter', 'managenodes', ','.join(manage))

		#engine
        for e in engine:
            config.set(e, 'hosts', ','.join(allnodes))

        with open(conffile, 'w') as f:
            config.write(f)

        lau = launcher.load(conffile)

        ctl = install_control.InstallControl(lau)
        http_server.setctl(ctl)
        ctl.start()


        self.send_response('application/json', json.dumps({'code':200, 'ret':[master, manage, other, engine, user, pwd, clustername]}))

       
 
    def do_POST(self):
        api_map = {
                "install":{
                    "check":self.checkip,
                    "login":self.login,
                    "progress":self.progress,
                    "doInstall":self.install,
                    }
                }

        def seekapi(urlpath):
            while urlpath and urlpath[-1] == '/': 
                urlpath = urlpath[:-1]
            url_path_list = urlpath.split('/')[1:]
            url_path_list.append('')
            directory = api_map
            for k in url_path_list:
                try:
                    obj = directory[k]
                    if callable(obj):
                        return obj
                    else:
                        directory = obj
                except (KeyError, AttributeError) as e:
                    return self.send_not_found
            assert(False)



        refer = self.headers.getheader('Referer')
        if refer:
            refer_loc = urlparse.urlparse(refer).netloc
            host = self.headers.getheader('host')
            if refer_loc != host:
                # TODO: add log
                return
        params = self.parse_POST()      
        f = seekapi(self.path)
        f(params)
        return 




    #接受get请求
    def do_GET(self):
        refer = self.headers.getheader('Referer')
        if refer:
            refer_loc = urlparse.urlparse(refer).netloc
            host = self.headers.getheader('host')
            if refer_loc != host:
                # logging
                return

        # check for '..', which will leak file
        if re.search(r'(\.{2})', self.path) is not None:
            self.wfile.write(b'HTTP/1.1 404\r\n\r\n')
            return

        url_path = urlparse.urlparse(self.path).path
        if url_path == '/':
            return self.req_index_handler()

        else:
            file_path = os.path.join(current_path, 'install_ui' + url_path)

            if os.path.isfile(file_path):
                if file_path.endswith('.js'):
                    mimetype = 'application/javascript'
                elif file_path.endswith('.css'):
                    mimetype = 'text/css'
                elif file_path.endswith('.html'):
                    mimetype = 'text/html'
                elif file_path.endswith('.jpg'):
                    mimetype = 'image/jpeg'
                elif file_path.endswith('.png'):
                    mimetype = 'image/png'
                else:
                    mimetype = 'text/plain'

                self.send_file(file_path, mimetype)

            else:
                self.wfile.write(b'HTTP/1.1 404\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n404 Not Found')


process = 0
server = 0
def start():
    global process, server
    # should use config.yaml to bing ip
    allow_remote = True
    host_port = 8999

    if allow_remote:
        host_addr = "0.0.0.0"
    else:
        host_addr = "127.0.0.1"

    server = LocalServer((host_addr, host_port), Http_Handler)
    process = threading.Thread(target=server.serve_forever)
    process.setDaemon(True)
    process.start()

def stop():
    global process, server
    if process == 0:
        return

    server.shutdown()
    server.server_close()
    process.join()
    process = 0

def wait():
    while process and process.isAlive():
        try:
            process.join(1)
        except KeyboardInterrupt:
            print("shutting down server...")
            stop()




def main():
    start()
    print("waitting input")
    ln = sys.stdin.readline()
    stop()



if __name__ == '__main__':
    main()
