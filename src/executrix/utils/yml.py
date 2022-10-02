import contextlib
import sys

import yaml


def read_yaml(path):
    with open(path, "r") as file_data:
        data = yaml.safe_load(file_data)
    return data


@contextlib.contextmanager
def fd_open(filename=None):
    if filename:
        fd = open(filename, "w")
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
    with open(path, "w") as file:
        file.write(data)
