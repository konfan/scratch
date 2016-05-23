#-*- coding: utf-8
import SocketServer
import urlparse
import os

from BaseHTTPServer import BaseHTTPRequestHandler


class SetKeyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print(self.path)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", len(self.path))
        self.end_headers()
        self.wfile.write(self.path)

    def do_POST(self):
        dlen = int(self.headers.get("Content-Length", 0))

        basepath = ''.join(['.',urlparse.urlparse(self.path).path])


        #print(dir(self.rfile))
        with open(basepath, 'w') as f:
            f.write(self.rfile.read(dlen))

        print('write %d bytes'%dlen)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", len(self.path))
        self.end_headers()
        self.wfile.write(self.path)




def main():
    port = 8999
    SocketServer.TCPServer.allow_reuse_address = True
    httpd = SocketServer.TCPServer(('',port), SetKeyHandler)
    print('serving at ', port)
    httpd.serve_forever()



if __name__ == '__main__':
    main()
