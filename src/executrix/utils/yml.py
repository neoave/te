"""Utility for working with yaml files."""

import contextlib
import sys

import yaml


def read_yaml(path):
    """Read yaml file on provided path."""
    with open(path, "r", encoding="utf-8") as file_data:
        data = yaml.safe_load(file_data)
    return data


@contextlib.contextmanager
def fd_open(filename=None):
    """File descriptor wrapper to work either with defined file or stdout."""
    if filename:
        fd = open(filename, "w", encoding="utf-8")
    else:
        fd = sys.stdout

    try:
        yield fd
    finally:
        if fd is not sys.stdout:
            fd.close()


def save_yaml(path, data):
    """
    Writes data with yaml.dump() to file specified by path.
    If path is not specified use stdout.
    """
    with fd_open(path) as yaml_file:
        yaml_file.write(yaml.dump(data, default_flow_style=False))


def save_data(path, data):
    """
    Writes data with file.write() to file specified by path.
    if path is not specified use stdout.
    """
    with open(path, "w", encoding="utf-8") as file:
        file.write(data)
