#!/usr/bin/env python3
"""
pytest tests for sacloud inventory plugin.
"""

from pathlib import Path

import pytest


def test_basic_inventory(mock_server, run_inventory):
    """Test basic inventory functionality."""
    inventory_file = Path(__file__).parent / "test_inventory_basic_sacloud.yml"
    data = run_inventory(inventory_file)

    # Check expected hosts
    expected_hosts = {
        "web-server-01",
        "db-server-01",
        "test-instance",
        "fumidai.test-server",
    }
    actual_hosts = set(data["_meta"]["hostvars"].keys())
    assert expected_hosts.issubset(actual_hosts), f"Missing hosts: {expected_hosts - actual_hosts}"

    # Check that skipped tag groups are not created
    skipped_groups = {"@auto-reboot", "__with_sacloud_inventory"}
    actual_groups = set(data.keys())
    assert not any(skipped in actual_groups for skipped in skipped_groups), f"Skipped tag groups were created: {skipped_groups & actual_groups}"


def test_constructed_inventory(mock_server, run_inventory):
    """Test inventory with constructed features."""
    inventory_file = Path(__file__).parent / "test_inventory_constructed_sacloud.yml"
    data = run_inventory(inventory_file)

    hostvars = data["_meta"]["hostvars"]

    # Check compose feature (ansible_host)
    fumidai_host = hostvars["fumidai.test-server"]
    ansible_host = fumidai_host["ansible_host"]

    # Handle Ansible's unsafe data wrapping
    if isinstance(ansible_host, dict) and "__ansible_unsafe" in ansible_host:
        ansible_host = ansible_host["__ansible_unsafe"]

    assert ansible_host == "203.0.113.104", f"ansible_host compose failed: expected '203.0.113.104', got {ansible_host}"

    # Check groups feature (production_hosts)
    production_hosts = set(data.get("production_hosts", {}).get("hosts", []))
    expected_production = {"web-server-01", "db-server-01"}
    assert expected_production.issubset(production_hosts), f"production_hosts group incorrect: expected {expected_production}, got {production_hosts}"

    # Check for keyed_groups
    keyed_groups = [k for k in data.keys() if k.startswith("os_type_")]
    assert len(keyed_groups) > 0, "No keyed_groups created"


def test_single_zone(mock_server, run_inventory):
    """Test single zone configuration."""
    inventory_file = Path(__file__).parent / "test_inventory_empty_sacloud.yml"
    data = run_inventory(inventory_file)

    hosts = set(data["_meta"]["hostvars"].keys())
    expected_hosts = {
        "web-server-01",
        "db-server-01",
        "test-instance",
        "fumidai.test-server",
    }
    assert hosts == expected_hosts, f"Single zone hosts incorrect: expected {expected_hosts}, got {hosts}"


@pytest.mark.parametrize(
    "inventory_file",
    [
        "test_inventory_basic_sacloud.yml",
        "test_inventory_constructed_sacloud.yml",
        "test_inventory_empty_sacloud.yml",
    ],
)
def test_all_inventory_files_valid(mock_server, run_inventory, inventory_file):
    """Test that all inventory files are valid and produce results."""
    inventory_path = Path(__file__).parent / inventory_file
    data = run_inventory(inventory_path)

    # Basic structure checks
    assert "_meta" in data, "Missing _meta section"
    assert "hostvars" in data["_meta"], "Missing hostvars in _meta section"
    assert "all" in data, "Missing 'all' group"
