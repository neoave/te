"""Command step module."""

import logging
import os
import tempfile
import uuid

from executrix.common.inventory import to_external_hostname
from executrix.common.paths import test_dir
from executrix.step import StepType
from executrix.te import PRIV_KEY_PATH, common_popen_args, run

logger = logging.getLogger(__name__)


class CommandStep(StepType):
    """Step for executing shell command on a remote or local machine."""

    def __init__(self, options):
        """Step initialization."""
        self.host = options.get("host", "localhost")
        self.cmd_text = options["command"].strip()
        self.cwd = options.get("cwd")
        self.user = options.get("user", "root")

    def run(self, timeout, **kwargs):
        """Execute command step."""
        if self.host == "localhost":
            return local_command(self.cmd_text, self.cwd, timeout)
        return remote_command(self.cmd_text, self.host, self.cwd, self.user, timeout)

    @staticmethod
    def match(options):
        """Match options with 'command'."""
        return "command" in options


def upload_script(script_code, host, user, key_path):
    """Upload shell script to remove host."""
    filename = f"{uuid.uuid4().hex}.sh"

    with tempfile.NamedTemporaryFile(mode="w+") as temp_f:
        temp_f.write(script_code)
        temp_f.flush()

        cmd = [
            "scp",
            "-i",
            f"{key_path}",
            "-o",
            "StrictHostKeyChecking=no",
            temp_f.name,
            f"{user}@{host}:~/{filename}",
        ]
        run(cmd, common_popen_args(), None)
    return filename


def local_command(cmd_text, cwd, timeout):
    """Run shell command on localhost."""
    logger.info("LOCAL COMMAND STEP START")
    logger.info(f"Command: {cmd_text}")
    args = common_popen_args()
    args["shell"] = True
    if cwd is not None:
        cwd = os.path.join(test_dir(), cwd)
        args["cwd"] = cwd

    returncode = run(cmd_text, args, timeout)

    logger.info(f"RETURN CODE: {returncode}")
    logger.info("LOCAL COMMAND STEP END")
    return returncode


def remote_command(cmd_text, host, cwd, user, timeout):
    """Run remote (SSH) command.

    :param cmd_text: a command string (including parameters)
    :param host: remote host
    :param cwd: working directory
    :param user: remote user
    :param timeout: seconds for step to timeout

    :return: remote command exit code
    """
    logger.info("REMOTE COMMAND STEP START")

    logger.debug(f"Host: {host}")
    logger.debug(f"User: {user}")
    if cwd:
        logger.debug(f"Working dir: {cwd}")

    real_host = to_external_hostname(host)
    if not real_host:
        raise RuntimeError(f"Host not found in inventory: {host}")
    logger.debug(f"Real host: {real_host}")

    key_path = os.path.join(test_dir(), PRIV_KEY_PATH)

    cmd = [
        "ssh",
        "-i",
        f"{key_path}",
        "-o",
        "StrictHostKeyChecking=no",
        f"{user}@{real_host}",
    ]

    if len(cmd_text.splitlines()) > 1:
        if cwd:
            cmd_text = f"cd {cwd}\n" + cmd_text
        cmd_text = "set -x\n" + cmd_text
        logger.debug("Command: uploading script")
        script_path = upload_script(cmd_text, real_host, user, key_path)
        cmd.append(f"bash ~/{script_path}")
        logger.debug("Command: executing")

    else:
        logger.debug(f"{user}@{host}# {cmd_text}")
        if cwd:
            cmd_text = f"cd {cwd} && {cmd_text}"
        cmd.append(cmd_text)

    returncode = run(cmd, common_popen_args(), timeout)

    logger.info(f"RETURN CODE: {returncode}")
    logger.info("REMOTE COMMAND STEP END")
    return returncode
