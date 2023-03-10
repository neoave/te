"""Restraint step module."""

import logging
import os

from te.common.paths import test_dir
from te.common.process import common_popen_args, run
from te.common.step import StepType

logger = logging.getLogger(__name__)


class RestraintStep(StepType):
    """Step for executing beakerlib tests via restraint."""

    def __init__(self, options):
        """Initialize Restraint step."""
        self.restraint_file = options["restraint"]
        self.git = options.get("git", None)

    def run(self, timeout, **kwargs):
        """Run restraint test.

        :param restraint_file: path to restraint.xml configuration file
        :param timeout: seconds for step to timeout
        :return: 'restraint' command exit code
        """
        logger.info(f"RESTRAINT JOB STEP START: {self.restraint_file}")
        if self.git:
            restraint_file = os.path.join(self.git, self.restraint_file)
        elif not os.path.isabs(restraint_file):
            restraint_file = os.path.join(test_dir(), restraint_file)
        cmd = [
            "run-restraint2.py",
            restraint_file,
        ]
        returncode = run(cmd, common_popen_args(), timeout)

        logger.info(f"RETURN CODE: {returncode}")
        logger.info(f"RESTRAINT JOB STEP END: {restraint_file}")
        return returncode

    @staticmethod
    def match(options):
        """Match options with 'restraint'."""
        return "restraint" in options
