#!/usr/bin/env python3
"""
pytest fixtures for sacloud inventory plugin tests.
"""

import os
import socketserver
import threading
import time
from pathlib import Path

import pytest
from mock_server import MockSakuraAPIHandler


@pytest.fixture(scope="session")
def mock_server():
    """Start mock server and return server URL."""

    def create_handler(*args, **kwargs):
        MockSakuraAPIHandler(*args, **kwargs)

    # Use port 0 to get automatically assigned port
    server = socketserver.TCPServer(("", 0), create_handler)
    port = server.server_address[1]

    # Set environment variable for inventory configs
    os.environ["SAKURA_API_ROOT_URL"] = f"http://localhost:{port}"

    # Start server in background thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Give server time to start
    time.sleep(0.5)

    yield f"http://localhost:{port}"

    # Cleanup
    server.shutdown()
    server.server_close()
    if "SAKURA_API_ROOT_URL" in os.environ:
        del os.environ["SAKURA_API_ROOT_URL"]


@pytest.fixture
def run_inventory():
    """Helper function to run ansible-inventory command."""

    def _run_inventory(inventory_file):
        import json
        import subprocess

        cmd = ["ansible-inventory", "-i", str(inventory_file), "--list"]

        try:
            result = subprocess.run(
                cmd,
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Command failed: {result.stderr}")

            return json.loads(result.stdout)
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("Command timed out") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON: {e}") from e

    return _run_inventory
