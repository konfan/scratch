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

from BaseHTTPServer import BaseHTTPRequestHandler

NetWorkIOError = (socket.error, ssl.SSLError, OSError)

current_path = os.path.dirname(os.path.abspath(__file__))

class LocalServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

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

        index_path = os.path.join(current_path, 'web_ui', "index.html")
        with open(index_path, "r") as f:
            index_content = f.read()

        data = index_content.decode('utf-8').encode('utf-8')
        self.send_response('text/html', data)

    def do_POST(self):
        refer = self.headers.getheader('Referer')
        if refer:
            refer_loc = urlparse.urlparse(refer).netloc
            host = self.headers.getheader('host')
            if refer_loc != host:
                # TODO: add log
                #launcher_log.warn("web control ref:%s host:%s", refer_loc, host)
                return

        url_path_list = self.path.split('/')
        # parse request and do work
        return


    def do_GET(self):
        refer = self.headers.getheader('Referer')
        if refer:
            refer_loc = urlparse.urlparse(refer).netloc
            host = self.headers.getheader('host')
            if refer_loc != host:
                #launcher_log.warn("web control ref:%s host:%s", refer_loc, host)
                # logging
                return

        # check for '..', which will leak file
        if re.search(r'(\.{2})', self.path) is not None:
            self.wfile.write(b'HTTP/1.1 404\r\n\r\n')
            #launcher_log.warn('%s %s %s haking', self.address_string(), self.command, self.path )
            return

        url_path = urlparse.urlparse(self.path).path
        print(self.path)
        print(url_path)
        if url_path == '/':
            return self.req_index_handler()

        else:
            file_path = os.path.join(current_path, 'web_ui' + url_path)

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
    host_port = 80

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

    #launcher_log.info("begin to exit web control")
    server.shutdown()
    server.server_close()
    process.join()
    #launcher_log.info("launcher web control exited.")
    process = 0

def main():
    start()
    print("waitting input")
    ln = sys.stdin.readline()
    stop()



if __name__ == '__main__':
    main()
