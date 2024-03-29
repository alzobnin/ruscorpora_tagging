# -*- Encoding: utf-8 -*-

import codecs
import sys
import time
import BaseHTTPServer
import urlparse
import search


# Workaround for using IPv4
import socket
origGetAddrInfo = socket.getaddrinfo

def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
        return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)

# replace the original socket.getaddrinfo by our version
socket.getaddrinfo = getAddrInfoWrapper


from_win1251 = codecs.getdecoder("windows-1251")

class ServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        start = time.time()
        out = codecs.getwriter("utf-8")(self.wfile, 'xmlcharrefreplace')

        self.send_response(200, "OK")
        self.send_header("Content-Type", "text/xml")
        self.end_headers()

        out.write('<?xml version="1.0" encoding="utf-8" ?>')

        query = urlparse.urlparse(self.path).query
        params = urlparse.parse_qs(query)

        search.search(params, self.wfile)
        end = time.time()
        print >>sys.stderr, "Elapsed:", end - start


def main():
    stime = time.time()
    serv = None
    while time.time() - stime < 100:
        try:
            serv = BaseHTTPServer.HTTPServer(('', 8001), ServerHandler)
            break
        except BaseException:
            pass
        except Exception:
            pass
        time.sleep(1)
    if serv == None:
        output.write("Failed to bind.\nClosing...\n")
        exit(1)

    serv.halt = False
    while True:
        serv.handle_request()
        if serv.halt:
            break
    serv.server_close()
    exit(0)

if __name__ == "__main__":
    main()
