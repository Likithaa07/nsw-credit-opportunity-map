"""Tests for downloads and retries, using a tiny local web server that fails on purpose."""
# STEP 1: Imports and a fake data service
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from utils import (DownloadError, MissingInputError, download, get, get_json, make_session,
                   require_files)


class FlakyService(BaseHTTPRequestHandler):
    """/flaky fails twice with 503 then works; /broken always fails; /arcgis-error and
    /html send back an error page with '200 OK'; /empty sends an empty file."""
    calls = {}

    def do_GET(self):
        path = self.path.split("?")[0]
        n = self.calls[path] = self.calls.get(path, 0) + 1
        if path == "/flaky" and n <= 2 or path == "/broken":
            self.send_response(503)
            self.end_headers()
            return
        body = {"/arcgis-error": json.dumps({"error": {"code": 400, "message": "Invalid query"}}),
                "/html": "<html>Service unavailable</html>",
                "/empty": ""}.get(path, json.dumps({"value": [1, 2, 3]}))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def server():
    httpd = HTTPServer(("127.0.0.1", 0), FlakyService)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()


@pytest.fixture
def fast():
    return make_session(retries=3, backoff=0.01)


# STEP 2: Retries and error pages
def test_retries_until_the_service_answers(server, fast):
    FlakyService.calls.clear()
    assert get_json(f"{server}/flaky", session=fast) == {"value": [1, 2, 3]}
    assert FlakyService.calls["/flaky"] == 3


def test_gives_up_with_clear_error(server, fast):
    with pytest.raises(DownloadError, match="broken"):
        get(f"{server}/broken", session=fast)


def test_arcgis_error_inside_200_is_caught(server, fast):
    with pytest.raises(DownloadError, match="Invalid query"):
        get_json(f"{server}/arcgis-error", session=fast)


def test_html_error_page_is_not_treated_as_data(server, fast):
    with pytest.raises(DownloadError, match="did not send back JSON"):
        get_json(f"{server}/html", session=fast)


# STEP 3: File downloads
def test_download_saves_file_once(server, fast, tmp_path):
    path = download(f"{server}/data", tmp_path / "a.json", session=fast)
    assert json.loads(path.read_text()) == {"value": [1, 2, 3]}
    path.write_text("kept")
    download(f"{server}/data", path, session=fast)       # already there, so not downloaded again
    assert path.read_text() == "kept"


def test_failed_or_empty_download_leaves_no_broken_file(server, fast, tmp_path):
    for name in ["broken", "empty"]:
        with pytest.raises(DownloadError):
            download(f"{server}/{name}", tmp_path / f"{name}.zip", session=fast)
    assert list(tmp_path.iterdir()) == []


def test_require_files(tmp_path):
    with pytest.raises(MissingInputError, match="capad.zip"):
        require_files(tmp_path / "capad.zip", hint="Run download_layers.py first.")
