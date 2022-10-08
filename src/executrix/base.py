"""Base module with some common function."""

import os
import site

from executrix.common.exceptions import BrokenInstallation


def iter_ci_data_dirs():
    """Iterate over executrix data dirs to get all shared directories."""
    for prefix in site.PREFIXES + [site.USER_BASE]:
        path = os.path.join(prefix, "share/executrix")
        if os.path.isdir(path):
            yield path


def get_ci_data_dir():
    """Get first CI data dir."""
    try:
        return next(iter_ci_data_dirs())
    except StopIteration as exc:
        raise BrokenInstallation(exc) from exc
