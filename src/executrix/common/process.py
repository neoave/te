"""Module for subprocess calls."""

import logging
import os
import signal
import subprocess
import threading

from te.common.config import config
from te.common.exceptions import TimeoutException
from te.common.paths import test_dir

logger = logging.getLogger(__name__)


def command_output(text):
    """Wrap printing command outputs."""
    logging.LoggerAdapter(logger, {"color": None}).debug(text)


def common_popen_args():
    """Get common arguments for popen calls."""
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

    # reset group id so that killing the newly spawn process and its child
    # won't kill also `te`
    run_args["preexec_fn"] = os.setpgrp

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
