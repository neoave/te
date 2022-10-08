"""Pytest step module."""

import logging

from executrix.common.process import common_popen_args, run
from executrix.common.step import StepType

logger = logging.getLogger(__name__)


class PytestsStep(StepType):
    """Step for executing pytest tests."""

    def __init__(self, options):
        """Initialize pytest step."""
        self.suite = options["pytests"]
        self.git = options.get("git", None)
        self.args = options.get("args")
        self.version = options.get("version")
        self.ssh_transport = options.get("ssh_transport")

    def run(self, timeout, **kwargs):
        """Run pytest for the suite.

        :param suite: relative path to test suite
        :param git: folder with a repository
        :param args: additional pytests arguments
        :param version: pytest version, one of 2 or 3, defaults to 3
        :param timeout: seconds for step to timeout

        :return: pytest exit code
        """
        logger.info(f"UPSTREAM TESTS STEP START: {self.suite}")

        cmd = ["run-pytests.py", self.suite]

        if self.git:
            cmd.append(f"--git-dir={self.git}")
        if self.version:
            cmd.append(f"--version={self.version}")
        if self.args:
            cmd.append(f'--args="{self.args}"')
        if self.ssh_transport:
            cmd.append(f'--ssh-transport="{self.ssh_transport}"')

        returncode = run(cmd, common_popen_args(), timeout)

        logger.info(f"RETURN CODE: {returncode}")
        logger.info(f"UPSTREAM TESTS STEP END: {self.suite}")
        return returncode

    @staticmethod
    def match(options):
        """Match options with 'pytest'."""
        return "pytests" in options
