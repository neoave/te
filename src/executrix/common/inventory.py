"""Module for Ansible Inventory helper calls."""

import os

from executrix.common.paths import test_dir
from executrix.common.yml import read_yaml

INVENTORY = "config/test.inventory.yaml"


def to_external_hostname(hostname):
    """Get connectable hostname or IP address from job hostname."""
    inv_path = os.path.join(test_dir(), INVENTORY)
    inventory = read_yaml(inv_path)
    ansible_host = None

    # First try if host is defined in 'all' group
    hosts = inventory["all"].get("hosts", {})
    host = hosts.get(hostname, {})
    ansible_host = host.get("ansible_host")
    if ansible_host:
        return ansible_host

    # If not, try to find it in other groups
    for group in inventory["all"]["children"].items():
        hosts = group[1].get("hosts", {})
        host = hosts.get(hostname, {})
        ansible_host = host.get("ansible_host")
        if ansible_host:
            break
    return ansible_host
