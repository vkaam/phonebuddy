"""Small, secret-free release verification endpoint."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.environ.get('RELEASE_VERSION', 'unknown')


class ReleaseServer(ThreadingHTTPServer):
    request_timeout = 5


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(self.server.request_timeout)

    def do_GET(self):
        if self.path not in ('/', '/ready'):
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps({'version': VERSION, 'ready': True}).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    ReleaseServer(('0.0.0.0', 8080), Handler).serve_forever()
