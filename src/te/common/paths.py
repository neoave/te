"""Module for working with paths and file discoveries."""

import os
import site

from te.common.exceptions import BrokenInstallation, PlaybookNotFound


def iter_ci_data_dirs():
    """Iterate over te data dirs to get all shared directories."""
    for prefix in site.PREFIXES + [site.USER_BASE]:
        path = os.path.join(prefix, "share/te")
        if os.path.isdir(path):
            yield path


def get_ci_data_dir():
    """Get first CI data dir."""
    try:
        return next(iter_ci_data_dirs())
    except StopIteration as exc:
        raise BrokenInstallation(exc) from exc


def test_dir():
    """Get test working directory (twd) path."""
    return os.getcwd()


def get_playbook_path(playbook):
    """Find absolute path of playbook."""
    if os.path.isabs(playbook):
        if os.path.isfile(playbook):
            return playbook
    else:
        # Assuming playbooks relative to twd, e.g. in checked-out test dir
        # are more specific than in general project dir. Thus prefer those in
        # case of name/path conflict.
        path = os.path.join(test_dir(), playbook)
        if os.path.isfile(path):
            return path
        for ci_data_dir in iter_ci_data_dirs():
            path = os.path.join(ci_data_dir, "playbooks", playbook)
            if os.path.isfile(path):
                return path
    raise PlaybookNotFound(playbook)
