"""Exercise the release-test HTTP contract without an Azure deployment."""
import importlib.util
from contextlib import redirect_stdout
from io import StringIO
import json
import socket
from pathlib import Path
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen


spec = importlib.util.spec_from_file_location(
    'release_test', Path(__file__).resolve().parents[1] / 'infra/release-test/server.py'
)
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class ReleaseTestContract(unittest.TestCase):
    def test_health_telemetry_is_structured_and_contains_no_request_data(self):
        original_version = server.VERSION
        server.VERSION = 'synthetic-release'
        httpd = server.ReleaseServer(('127.0.0.1', 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        output = StringIO()
        thread.start()
        self.addCleanup(setattr, server, 'VERSION', original_version)
        self.addCleanup(httpd.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(httpd.shutdown)
        with redirect_stdout(output):
            with urlopen(f'http://127.0.0.1:{httpd.server_port}/ready', timeout=5) as response:
                self.assertEqual(response.status, 200)
            with self.assertRaises(HTTPError):
                urlopen(f'http://127.0.0.1:{httpd.server_port}/ready?token=hidden', timeout=5)
        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([event['event'] for event in events], ['health_request', 'health_request'])
        self.assertEqual([event['version'] for event in events],
                         ['synthetic-release', 'synthetic-release'])
        self.assertEqual([event['status'] for event in events], [200, 404])
        for event in events:
            self.assertIn('duration_ms', event)
            self.assertNotIn('path', event)
            self.assertNotIn('client_address', event)
        self.assertNotIn('token', output.getvalue())

    def test_ready_returns_version_and_unknown_path_fails(self):
        server.VERSION = 'test-revision'
        httpd = server.ReleaseServer(('127.0.0.1', 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(httpd.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(httpd.shutdown)
        url = f'http://127.0.0.1:{httpd.server_port}'
        with urlopen(url + '/ready', timeout=5) as response:
            self.assertEqual(json.load(response), {'version': 'test-revision', 'ready': True})
        with self.assertRaises(HTTPError) as error:
            urlopen(url + '/missing', timeout=5)
        self.assertEqual(error.exception.code, 404)

    def test_incomplete_request_does_not_block_readiness_and_times_out(self):
        httpd = server.ReleaseServer(('127.0.0.1', 0), server.Handler)
        httpd.request_timeout = 0.5
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(httpd.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(httpd.shutdown)
        with socket.create_connection(httpd.server_address, timeout=2) as stalled:
            stalled.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n')
            url = f'http://127.0.0.1:{httpd.server_port}/ready'
            with urlopen(url, timeout=2) as response:
                self.assertTrue(json.load(response)['ready'])
            stalled.settimeout(2)
            self.assertEqual(stalled.recv(1), b'')
