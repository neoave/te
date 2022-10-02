"""Module with core te functionality."""

import logging
import os
import signal
import subprocess
import threading
import time

from executrix.base import iter_ci_data_dirs
from executrix.config import config

logger = logging.getLogger(__name__)

DEFAULT_PHASE_TIMEOUT = 4 * 60 * 60
INVENTORY = "config/test.inventory.yaml"
PRIV_KEY_PATH = "config/id_rsa"


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


class PlaybookNotFound(Exception):
    """Raised when Playbook file is not found."""

    def __init__(self, playbook):
        super().__init__()
        self.playbook = playbook


class TimeoutException(Exception):
    """Raised when step or phase time-outs."""

    def __init__(self, timeout):
        super().__init__()
        self.msg = f"Timed out after {timeout}s."


class StepType:
    """Base class for steps."""

    def run(self, timeout, **kwargs):
        """Run the step."""
        raise NotImplementedError

    @staticmethod
    def match(options):
        """Figure out of this StepType matches step in job metadata."""
        raise NotImplementedError


class StepTypes:
    """Registry for step types."""

    def __init__(self):
        self._step_types = set()

    def register(self, step_type):
        """Register new step type."""
        self._step_types.add(step_type)

    def resolve(self, options):
        """Get matching StepType."""
        for step_type in self._step_types:
            if step_type.match(options):
                return step_type(options)
        return None


def command_output(text):
    """Wrapper for printing command outputs."""
    logging.LoggerAdapter(logger, {"color": None}).debug(text)


def common_popen_args():
    """Common arguments for popen calls."""
    return {
        "cwd": test_dir(),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
    }


def run(cmd, run_args, timeout=None):
    """Run subprocess command.

    :param cmd: command name
    :param run_args: dict of Popen kwargs
    :param timeout: seconds for the process to timeout

    :return: exit code of the command
    """
    if config["dry_run"]:
        logger.debug(cmd)
        logger.debug(run_args)
        return 0

    if timeout is not None and timeout <= 0:
        raise TimeoutException(0)

    pinfo = {}

    def target():
        # TODO: remove the pylint exception
        process = subprocess.Popen(cmd, **run_args)  # pylint: disable=R1732
        pinfo["process"] = process
        for line in iter(process.stdout.readline, b""):
            command_output(line.decode("utf-8").rstrip("\n"))
        process.wait()

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        pid = pinfo["process"].pid
        pgid = os.getpgid(pid)
        logger.info(f"timeout happened, killing {pgid}/{pid}")
        os.killpg(pgid, signal.SIGKILL)
        thread.join()
        raise TimeoutException(timeout)
    return pinfo["process"].returncode


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


def run_phases(phases, metadata, metadata_path, timeout=DEFAULT_PHASE_TIMEOUT):
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


step_types = StepTypes()
