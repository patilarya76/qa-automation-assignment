"""
Local Mock Server for both DaveAI website and Reqres API endpoints.
Enables running the full test suite (UI + API) in isolated, offline, or CI/CD
environments when external network connectivity or public API rate limits (e.g. Reqres 40 reqs/day cap)
affect live third-party testing.
"""

import http.server
import socketserver
import json
import os

PORT = int(os.getenv("MOCK_PORT", "5000"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOCK_DIR = os.path.join(BASE_DIR, "mock_site")


class MockServerHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler routing DaveAI UI and Reqres REST API mock endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=MOCK_DIR, **kwargs)

    def do_GET(self):
        # --- API Endpoints ---
        if self.path.startswith("/api/users?page="):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = {
                "page": 2,
                "per_page": 6,
                "total": 12,
                "total_pages": 2,
                "data": [
                    {
                        "id": 7,
                        "email": "michael.lawson@reqres.in",
                        "first_name": "Michael",
                        "last_name": "Lawson",
                        "avatar": "https://reqres.in/img/faces/7-image.jpg"
                    },
                    {
                        "id": 8,
                        "email": "lindsay.ferguson@reqres.in",
                        "first_name": "Lindsay",
                        "last_name": "Ferguson",
                        "avatar": "https://reqres.in/img/faces/8-image.jpg"
                    }
                ]
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        elif self.path == "/api/users/2":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = {
                "data": {
                    "id": 2,
                    "email": "janet.weaver@reqres.in",
                    "first_name": "Janet",
                    "last_name": "Weaver",
                    "avatar": "https://reqres.in/img/faces/2-image.jpg"
                }
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        elif self.path == "/api/users/23":
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"{}")
            return

        # --- UI Endpoints (DaveAI) ---
        elif self.path in ("/", "/index.html"):
            self.path = "/index.html"
            return super().do_GET()
        elif "/book-demo" in self.path:
            self.path = "/book-demo.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if self.path == "/api/users":
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response_data = {
                "name": payload.get("name", "Test User"),
                "job": payload.get("job", "QA Engineer"),
                "id": "100",
                "createdAt": "2026-11-19T10:00:00.000Z"
            }
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            return

        elif self.path == "/api/register":
            if "password" not in payload:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing password"}).encode("utf-8"))
                return
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"id": 4, "token": "QpwL5tke4Pnpja7X4"}).encode("utf-8"))
                return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        # Suppress verbose terminal access logs
        pass


def run_mock_server():
    """Starts the local mock server."""
    with socketserver.TCPServer(("", PORT), MockServerHandler) as httpd:
        print(f"[Mock Server] Serving at http://localhost:{PORT}")
        print("Press Ctrl+C to terminate.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Mock Server] Stopped.")


if __name__ == "__main__":
    run_mock_server()
