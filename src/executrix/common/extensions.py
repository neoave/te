"""Module extensions functionality."""

import logging
import subprocess

logger = logging.getLogger(__name__)


def install_extensions(extensions, user=False):
    """Install extension projects defined in job metadata file."""
    pip_cmd = ["pip3", "install"]
    if user:
        # add --user option to have a permission to install packages outside of
        # virtual environment
        pip_cmd.append("--user")

    for extension in extensions:
        result = subprocess.run(pip_cmd + [extension["package"]], check=False)
        if result.returncode:
            if user:
                return result.returncode
            # retry installation using local user environment
            return install_extensions(extensions, user=True)

    import pkg_resources  # pylint: disable=C0415

    for ext_module in pkg_resources.iter_entry_points("te_extensions"):
        logger.info(f"LOAD EXTENSION: {ext_module.name}")
        ext_module.load()

    return 0
