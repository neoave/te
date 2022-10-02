import json
import logging
import os
from tempfile import NamedTemporaryFile

from executrix.base import get_ci_data_dir
from executrix.te import (
    INVENTORY,
    PRIV_KEY_PATH,
    StepType,
    common_popen_args,
    get_playbook_path,
    run,
    test_dir,
)

logger = logging.getLogger(__name__)


class PlaybookStep(StepType):
    def __init__(self, options):
        self.playbook = options["playbook"]
        self.extra_vars = options.get("extra_vars", {})
        self.extra_args = options.get("extra_args", {})
        self.inventory = options.get("inventory", None)

    def run(self, timeout, **kwargs):
        """Prepare and run ansible playbook.

        :param playbook: path to playbook, can be absolute or relative
        :param extra_vars: dict with ansible extra vars (-e option)
        :param extra_args: list of additional ansible-playbook options
        :param inventory: a specific inventory for the playbook (optional)
        :param metadata_path: path to metadata file
        :param timeout: seconds for step to timeout

        :return: ansible-playbook exit code
        """
        dynamic_playbook = len(self.playbook.splitlines()) > 1
        name = self.playbook
        if dynamic_playbook:
            name = "Dynamic playbook"
        logger.info("PLAYBOOK START: {}".format(name))
        ansible_extra_vars = {
            "twd": test_dir(),
            "metadata": kwargs["metadata_path"],
            "ci_data_dir": get_ci_data_dir(),
        }
        ansible_extra_vars.update(self.extra_vars)

        if dynamic_playbook:
            #  Playbook is not path but actually a playbook text which can be
            #  saved and used directly.
            with NamedTemporaryFile(mode="w+", delete=False) as temp_f:
                temp_f.write(self.playbook)
                temp_f.flush()
                playbook_path = temp_f.name
        else:
            playbook_path = get_playbook_path(self.playbook)

        key_path = os.path.join(test_dir(), PRIV_KEY_PATH)
        if not self.inventory:
            inventory = INVENTORY
        inventory_path = os.path.join(test_dir(), inventory)

        cmd = [
            "ansible-playbook",
            '--ssh-extra-args="-o StrictHostKeyChecking=no"',
            '--ssh-extra-args="-o UserKnownHostsFile=/dev/null"',
            "--private-key={}".format(key_path),
            "--inventory={}".format(inventory_path),
            playbook_path,
        ]
        add_extra_vars_option(cmd, ansible_extra_vars, 4)
        if self.extra_args:
            cmd.append(self.extra_args)

        run_args = common_popen_args()
        run_args["env"] = ansible_env()
        logger.info("CMD: {}".format(cmd))

        returncode = run(cmd, run_args, timeout)
        if dynamic_playbook:
            os.remove(playbook_path)

        logger.info("RETURN CODE: {}".format(returncode))
        logger.info("PLAYBOOK END: {}".format(name))
        return returncode

    @staticmethod
    def match(options):
        return "playbook" in options


def add_extra_vars_option(cmd, extra_vars, position):
    cmd[position:position] = ["-e", json.dumps(extra_vars, separators=(",", ":"))]


def ansible_env():
    my_env = os.environ.copy()
    my_env["ANSIBLE_STDOUT_CALLBACK"] = "yaml"
    my_env["ANSIBLE_HOST_KEY_CHECKING"] = "False"
    return my_env
