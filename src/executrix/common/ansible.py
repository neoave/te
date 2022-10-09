"""Module for Ansible related helper functions."""

import json
import os


def add_extra_vars_option(cmd, extra_vars, position):
    """Add extra vars option in command list on given position."""
    cmd[position:position] = ["-e", json.dumps(extra_vars, separators=(",", ":"))]


def ansible_env():
    """Get default environment for Ansible playbook based on current os env."""
    my_env = os.environ.copy()
    my_env["ANSIBLE_STDOUT_CALLBACK"] = "yaml"
    my_env["ANSIBLE_HOST_KEY_CHECKING"] = "False"
    return my_env
