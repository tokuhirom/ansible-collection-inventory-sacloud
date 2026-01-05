#!/usr/bin/env python3
"""
Mock HTTP server for testing Sakura Cloud API calls.
"""

import http.server
import json
import socketserver
import sys
from pathlib import Path
from urllib.parse import urlparse


class MockSakuraAPIHandler(http.server.BaseHTTPRequestHandler):
    """Mock handler for Sakura Cloud API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)

        # Extract zone from path and handle server endpoint
        path_parts = parsed_url.path.split("/")
        if len(path_parts) >= 5:
            zone = path_parts[1]
            if "cloud" in path_parts and "1.1" in path_parts and "server" in path_parts:
                self._handle_server_request(zone, parsed_url.query)
                return

        self.send_error(404, f"Path not found: {parsed_url.path}")

    def _handle_server_request(self, zone, query):
        """Handle server list requests."""
        # Return mock data for all zones
        mock_file = Path(__file__).parent / "data" / "mock_api_response.json"
        if mock_file.exists():
            with open(mock_file, "r") as f:
                response = json.load(f)
        else:
            response = {"Servers": []}

        # Handle the {From:0,To:0} pagination parameter
        # The real Sakura Cloud API uses this to get server count information
        # For our tests, we'll return the full server list regardless of pagination
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        """Log requests for debugging."""
        print(f"[MOCK] {self.address_string()} - {format % args}")


def start_mock_server(port=8765):
    """Start the mock HTTP server."""

    def create_handler(*args, **kwargs):
        MockSakuraAPIHandler(*args, **kwargs)

    with socketserver.TCPServer(("", port), create_handler) as httpd:
        print(f"Mock server started on port {port}")
        print(f"Test URL: http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    port = 8765
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    start_mock_server(port)
