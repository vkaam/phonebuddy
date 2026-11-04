"""Small, secret-free release verification endpoint."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import time

VERSION = os.environ.get('RELEASE_VERSION', 'unknown')


class ReleaseServer(ThreadingHTTPServer):
    request_timeout = 5


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(self.server.request_timeout)

    def log_message(self, _format, *_args):
        """Suppress the base handler's request-line and client-address logs."""

    def do_GET(self):
        started = time.monotonic()
        if self.path not in ('/', '/ready'):
            self.send_response(404)
            self.end_headers()
            self.log_health_request(404, started)
            return
        body = json.dumps({'version': VERSION, 'ready': True}).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.log_health_request(200, started)

    def log_health_request(self, status, started):
        """Emit bounded synthetic-health telemetry without request data."""
        event = {
            'event': 'health_request',
            'version': VERSION,
            'status': status,
            'duration_ms': round((time.monotonic() - started) * 1000, 3),
        }
        print(json.dumps(event, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    ReleaseServer(('0.0.0.0', 8080), Handler).serve_forever()
