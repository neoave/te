# Copyright 2022 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""te default CLI tool."""

import argparse
import logging
import sys

from te.common.config import DEFAULT_PHASE_TIMEOUT, config
from te.common.exceptions import BrokenInstallation, PlaybookNotFound, TimeoutException
from te.common.log import ColorHandler
from te.common.metadata import get_metadata_path, get_phase, get_phases_upto
from te.common.runner import run_phases
from te.common.yml import read_yaml
from te.steps import register_steps

logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(message)s", "%Y-%m-%dT%H:%M:%S%z")
file_handler = logging.FileHandler("runner.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(ColorHandler())


def run():
    """Run the te's CLI."""
    parser = argparse.ArgumentParser(
        description="""
    Run steps as defined in metadata.

    Should be executed in test execution (working) directory.

    By default runs all phases in a row as defined in metadata file.
    """
    )
    parser.add_argument("metadata", help="A path or an URL to metadata file.")

    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Only print commands to execute",
    )
    parser.add_argument(
        "-t",
        "--timestamp",
        dest="timestamp",
        action="store_true",
        help="Prepend output with timestamp",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--upto", help="Run all phases up to defined phase")
    group.add_argument("--phase", help="Run only this phase")

    parser.add_argument(
        "--phase-timeout",
        dest="phase_timeout",
        type=int,
        help=f"Default phase timeout is " f"{DEFAULT_PHASE_TIMEOUT} seconds",
        default=DEFAULT_PHASE_TIMEOUT,
    )

    args = parser.parse_args()

    config["dry_run"] = args.dry_run
    config["print_timestamp"] = args.timestamp
    config["phase_timeout"] = args.phase_timeout

    metadata_path = get_metadata_path(args.metadata)

    metadata = read_yaml(metadata_path)

    if args.upto:
        phases = get_phases_upto(metadata, args.upto)
    elif args.phase:
        phase = get_phase(metadata, args.phase)
        if phase:
            phases = [phase]
        else:
            phases = []
    else:
        phases = metadata.get("phases", [])

    if len(phases) <= 0:
        logger.error("No phase to run found")
        sys.exit(1)

    register_steps()

    rc = 1  # Default for most errors
    try:
        rc = run_phases(phases, metadata, metadata_path, args.phase_timeout)
    except PlaybookNotFound as e:
        logger.error(f"Ansible playbook not found: {e.playbook}")
    except RuntimeError as e:
        logger.error(e)
    except TimeoutException as e:
        logger.error(e)
    except BrokenInstallation as e:
        logger.error(e, exc_info=True)
    except Exception as e:  # pylint: disable=W0703
        logger.error(e, exc_info=True)

    sys.exit(rc)


if __name__ == "__main__":
    run()
