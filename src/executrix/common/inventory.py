"""Module for Ansible Inventory helper calls."""

import os

from executrix.common.paths import test_dir
from executrix.common.yml import read_yaml

INVENTORY = "config/test.inventory.yaml"


def to_external_hostname(hostname):
    """Get connectable hostname or IP address from job hostname."""
    inv_path = os.path.join(test_dir(), INVENTORY)
    inventory = read_yaml(inv_path)

    for group in inventory["all"]["children"].items():
        hosts = group[1].get("hosts")
        if not hosts:
            continue
        host = hosts.get(hostname)
        if host:
            return host.get("ansible_host")
    return None
