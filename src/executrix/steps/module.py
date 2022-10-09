"""Module for 'module' step."""

import logging
import os

from executrix.common.ansible import add_extra_vars_option, ansible_env
from executrix.common.config import config
from executrix.common.inventory import INVENTORY
from executrix.common.paths import test_dir
from executrix.common.process import common_popen_args, run
from executrix.common.step import StepType

ANSIBLE = "ansible"
logger = logging.getLogger(__name__)


class ModuleStep(StepType):
    """Step for executing individual Ansible module."""

    def __init__(self, options):
        """Initialize playbook step."""
        self.module = options["module"]
        self.arguments = options.get("arguments", "")
        self.host_pattern = options.get("hosts", "all")
        self.extra_vars = options.get("extra_vars", {})
        self.extra_args = options.get("extra_args", [])
        self.inventory = options.get("inventory", INVENTORY)

    def run(self, timeout, **kwargs):
        """Run single ansible module via ansible command.

        :param module: path to playbook, can be absolute or relative
        :param argument: dict with ansible extra vars (-e option)
        :param host_pattern: host pattern argument for ansible command
        :param extra_vars: dict with ansible extra vars (-e option)
        :param extra_args: list of additional ansible-playbook options
        :param inventory: a specific inventory for the playbook (optional)
        :param metadata_path: path to metadata file
        :param timeout: seconds for step to timeout

        :return: ansible-playbook exit code
        """
        logger.info(f"MODULE START: {self.module}: {self.arguments}")
        ansible_extra_vars = {
            "twd": test_dir(),
            "metadata": kwargs["metadata_path"],
        }
        ansible_extra_vars.update(self.extra_vars)
        key_path = os.path.join(test_dir(), config["private_key_path"])

        inventory_path = os.path.join(test_dir(), self.inventory)

        cmd = [
            ANSIBLE,
            self.host_pattern,
            "-b",
            '--ssh-extra-args="-o StrictHostKeyChecking=no"',
            '--ssh-extra-args="-o UserKnownHostsFile=/dev/null"',
            f"--private-key={key_path}",
            f"--inventory={inventory_path}",
        ]
        add_extra_vars_option(cmd, ansible_extra_vars, 4)
        cmd.extend(self.extra_args)
        cmd.extend(["-m", self.module])
        if self.arguments:
            cmd.extend(["-a", f"{self.arguments}"])
        run_args = common_popen_args()
        run_args["env"] = ansible_env()
        cmd_str = " ".join(cmd)
        logger.info(f"CMD: {cmd_str}")

        returncode = run(cmd, run_args, timeout)

        logger.info(f"RETURN CODE: {returncode}")
        logger.info(f"MODULE END: {self.module}")
        return returncode

    @staticmethod
    def match(options):
        """Match options containing 'module'."""
        return "module" in options
