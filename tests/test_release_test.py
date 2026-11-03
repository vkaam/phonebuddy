"""Exercise the release-test HTTP contract without an Azure deployment."""
import importlib.util
import json
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
    def test_ready_returns_version_and_unknown_path_fails(self):
        server.VERSION = 'test-revision'
        httpd = server.HTTPServer(('127.0.0.1', 0), server.Handler)
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
