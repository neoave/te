import logging

from executrix.te import StepType, common_popen_args, run

logger = logging.getLogger(__name__)


class PytestsStep(StepType):
    def __init__(self, options):
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
        logger.info("UPSTREAM TESTS STEP START: {}".format(self.suite))

        cmd = ["run-pytests.py", self.suite]

        if self.git:
            cmd.append("--git-dir={}".format(self.git))
        if self.version:
            cmd.append("--version={}".format(self.version))
        if self.args:
            cmd.append('--args="{}"'.format(self.args))
        if self.ssh_transport:
            cmd.append('--ssh-transport="{}"'.format(self.ssh_transport))

        returncode = run(cmd, common_popen_args(), timeout)

        logger.info("RETURN CODE: {}".format(returncode))
        logger.info("UPSTREAM TESTS STEP END: {}".format(self.suite))
        return returncode

    @staticmethod
    def match(options):
        return "pytests" in options
