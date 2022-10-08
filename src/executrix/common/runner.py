"""Module for executing phases and steps."""

import logging
import time

from executrix.common.config import config
from executrix.common.exceptions import TimeoutException
from executrix.common.extensions import install_extensions
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
        name = phase.get("name", "<no name>")

        if name == "init":
            logger.info("INSTALLING EXTENSIONS")
            rc = install_extensions(metadata.get("extensions", []))
            if rc:
                return rc

        phase_timeout = phase.get("timeout", timeout)
        logger.info(f"PHASE START: {name}")
        logger.info(f"Phase timeout: {phase_timeout}s")

        failed = False
        for step in phase.get("steps", []):
            logger.info("")
            step_start = int(time.time())
            # metadata can override step timeout - so it can run longer
            # then a phase timeout but in such case it should time-out
            # if there is some next step after it.
            step_timeout = step.get("timeout", phase_timeout)
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
            phase_timeout -= step_end - step_start
        logger.info(f"PHASE END: {name}\n")
        if failed:
            logger.error("PHASE: Some step in phase failed")
            logger.error("STOPPING EXECUTION")
            return 1
    return 0
