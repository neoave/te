"""Module with core te functionality."""

import logging
import subprocess
import time

from executrix.common.config import config
from executrix.common.exceptions import TimeoutException
from executrix.common.step import step_types

logger = logging.getLogger(__name__)


def run_step(step, metadata_path, timeout):
    """Run one specific step from metadata configuration.

    Step can have one of 'playbook', 'pytests', 'restraint' or 'command'
    attribute depending on the test type.
    :param metadata_path: provided metadata path
    :param timeout: seconds for step to timeout
    """
    step_runner = step_types.resolve(step)

    if step_runner:
        return step_runner.run(timeout, metadata_path=metadata_path)
    raise RuntimeError(f"Unsupported step type {str(step)}")


def run_phases(phases, metadata, metadata_path, timeout=config["phase_timeout"]):
    """Run discovered phases in sequence."""
    for phase in phases:
        timeout = phase.get("timeout", timeout)

        name = phase.get("name", "<no name>")

        if name == "init":
            logger.info("INSTALLING EXTENSIONS")
            rc = install_extensions(metadata.get("extensions", []))
            if rc:
                return rc

        logger.info(f"PHASE START: {name}")
        logger.info(f"Phase timeout: {timeout}s")
        failed = False
        for step in phase.get("steps", []):
            logger.info("")
            step_start = int(time.time())
            # metadata can override step timeout - so it can run longer
            # then a phase timeout but in such case it should time-out
            # if there is some next step after it.
            step_timeout = step.get("timeout", timeout)
            try:
                rc = run_step(step, metadata_path, step_timeout)
            except TimeoutException as ex:
                logger.error(ex.msg)
                logger.error("PREMATURE STEP END - timeout")
                rc = 2
            if rc != 0:
                failed = True
                if step.get("stop-on-error", "True") != "False":
                    logger.error("STOPPING EXECUTION")
                    return rc
            step_end = int(time.time())
            timeout -= step_end - step_start
        logger.info("PHASE END: %s\n", name)
        if failed:
            logger.error("PHASE: Some step in phase failed")
            logger.error("STOPPING EXECUTION")
            return 1
    return 0


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

    for ext_module in pkg_resources.iter_entry_points("executrix_extensions"):
        logger.info(f"LOAD EXTENSION: {ext_module.name}")
        ext_module.load()

    return 0
