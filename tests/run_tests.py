#!/usr/bin/env python3
"""
Test runner for sacloud inventory plugin.
"""

import json
import os
import signal
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path

from mock_server import MockSakuraAPIHandler


class InventoryTester:
    """Test runner for inventory plugin."""

    def __init__(self):
        self.port = None
        self.server_thread = None
        self.mock_server = None
        self.test_dir = Path(__file__).parent

    def start_mock_server(self):
        """Start mock server in background."""

        def create_handler(*args, **kwargs):
            MockSakuraAPIHandler(*args, **kwargs)

        # Use port 0 to get automatically assigned port
        self.mock_server = socketserver.TCPServer(("", 0), create_handler)
        self.port = self.mock_server.server_address[1]

        # Set environment variable for inventory configs
        os.environ["SAKURA_API_ROOT_URL"] = f"http://localhost:{self.port}"

        # Start server in background thread
        self.server_thread = threading.Thread(target=self.mock_server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Give server time to start
        time.sleep(0.5)
        print(f"Mock server started on port {self.port}")
        print(f"SAKURA_API_ROOT_URL={os.environ['SAKURA_API_ROOT_URL']}")

    def stop_mock_server(self):
        """Stop mock server."""
        if self.mock_server:
            self.mock_server.shutdown()
            self.mock_server.server_close()
            if self.server_thread:
                self.server_thread.join(timeout=1)
        # Clean up environment variable
        if "SAKURA_API_ROOT_URL" in os.environ:
            del os.environ["SAKURA_API_ROOT_URL"]

    def run_inventory_command(self, inventory_file):
        """Run ansible-inventory command and return JSON output."""
        cmd = [
            "ansible-inventory",
            "-i",
            str(inventory_file),
            "--list",
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir.parent,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "returncode": result.returncode,
                }

            return {"success": True, "data": json.loads(result.stdout)}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse JSON: {e}",
                "raw_output": result.stdout if "result" in locals() else "",
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {e}"}

    def test_basic_inventory(self):
        """Test basic inventory functionality."""
        print("\n=== Testing Basic Inventory ===")

        inventory_file = self.test_dir / "test_inventory_basic_sacloud.yml"
        result = self.run_inventory_command(inventory_file)

        if not result["success"]:
            print(f"❌ Basic inventory test failed: {result['error']}")
            return False

        data = result["data"]

        # Check expected hosts
        expected_hosts = {
            "web-server-01",
            "db-server-01",
            "test-instance",
            "fumidai.test-server",
        }
        actual_hosts = set(data.get("_meta", {}).get("hostvars", {}).keys())

        if not expected_hosts.issubset(actual_hosts):
            missing = expected_hosts - actual_hosts
            print(f"❌ Missing hosts: {missing}")
            return False

        # Check groups (should not include skipped tags)
        actual_groups = set(data.keys())

        # Ensure skipped tag groups are not created
        skipped_groups = {"@auto-reboot", "__with_sacloud_inventory"}
        if any(skipped in actual_groups for skipped in skipped_groups):
            print(f"❌ Skipped tag groups were created: {skipped_groups & actual_groups}")
            return False

        print("✅ Basic inventory test passed")
        return True

    def test_constructed_inventory(self):
        """Test inventory with constructed features."""
        print("\n=== Testing Constructed Inventory ===")

        inventory_file = self.test_dir / "test_inventory_constructed_sacloud.yml"
        result = self.run_inventory_command(inventory_file)

        if not result["success"]:
            print(f"❌ Constructed inventory test failed: {result['error']}")
            return False

        data = result["data"]
        hostvars = data.get("_meta", {}).get("hostvars", {})

        # Check compose feature (ansible_host)
        fumidai_host = hostvars.get("fumidai.test-server", {})
        ansible_host = fumidai_host.get("ansible_host")
        # Handle Ansible's unsafe data wrapping
        if isinstance(ansible_host, dict) and "__ansible_unsafe" in ansible_host:
            ansible_host = ansible_host["__ansible_unsafe"]

        if ansible_host != "203.0.113.104":
            print(f"❌ ansible_host compose failed for fumidai.test-server: {ansible_host}")
            return False

        # Check groups feature (production_hosts)
        production_hosts = set(data.get("production_hosts", {}).get("hosts", []))
        expected_production = {"web-server-01", "db-server-01"}
        if not expected_production.issubset(production_hosts):
            print(f"❌ production_hosts group incorrect: {production_hosts}")
            return False

        # Check for keyed_groups
        keyed_groups = [k for k in data.keys() if k.startswith("os_type_")]
        if not keyed_groups:
            print("❌ No keyed_groups created")
            return False

        print("✅ Constructed inventory test passed")
        return True

    def test_error_cases(self):
        """Test error handling scenarios."""
        print("\n=== Testing Error Cases ===")

        # Test basic functionality with single zone
        error_inventory = self.test_dir / "test_inventory_empty_sacloud.yml"
        result = self.run_inventory_command(error_inventory)

        if not result["success"]:
            print(f"❌ Empty zones test failed: {result['error']}")
            return False

        data = result["data"]
        hosts = set(data.get("_meta", {}).get("hostvars", {}).keys())

        # Should have servers from tk1b
        expected_hosts = {
            "web-server-01",
            "db-server-01",
            "test-instance",
            "fumidai.test-server",
        }
        if hosts != expected_hosts:
            print(f"❌ Empty zones hosts incorrect: got {hosts}, expected {expected_hosts}")
            return False

        print("✅ Error cases test passed")
        return True

    def run_all_tests(self):
        """Run all test cases."""
        print("Starting sacloud inventory plugin tests...")

        try:
            self.start_mock_server()

            tests = [
                self.test_basic_inventory,
                self.test_constructed_inventory,
                self.test_error_cases,
            ]

            passed = 0
            total = len(tests)

            for test in tests:
                if test():
                    passed += 1

            print("\n=== Test Results ===")
            print(f"Passed: {passed}/{total}")

            if passed == total:
                print("🎉 All tests passed!")
                return True
            else:
                print("❌ Some tests failed")
                return False

        finally:
            self.stop_mock_server()


def main():
    """Main test runner."""
    tester = InventoryTester()

    # Handle cleanup on Ctrl+C
    def signal_handler(sig, frame):
        print("\nStopping tests...")
        tester.stop_mock_server()
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
