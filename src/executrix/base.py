import os
import site


class BrokenInstallation(Exception):
    pass


def iter_ci_data_dirs():
    for prefix in site.PREFIXES + [site.USER_BASE]:
        path = os.path.join(prefix, "share/executrix")
        if os.path.isdir(path):
            yield path


def get_ci_data_dir():
    try:
        return next(iter_ci_data_dirs())
    except StopIteration:
        raise BrokenInstallation()
