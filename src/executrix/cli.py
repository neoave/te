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

"""executrix default CLI tool."""

import argparse
import logging
import os
import re
import sys
import tempfile

import requests
from requests.exceptions import RequestException

from executrix.config import config
from executrix.te import DEFAULT_PHASE_TIMEOUT, run_phases
from executrix.utils.log import ColorHandler
from executrix.utils.yml import read_yaml

logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(message)s", "%Y-%m-%dT%H:%M:%S%z")
file_handler = logging.FileHandler("runner.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(ColorHandler())


def is_url(path):
    """Check if `path` starts with http(s)://"""
    return bool(re.match("(http|https)://", path))


def get_metadata_path(original_path):
    """Check if `original_path` exists or it's an URL to be downloaded.

    Exit program if file cannot be found or downloaded.
    """
    if not is_url(original_path):
        metadata_path = os.path.join(os.getcwd(), original_path)

        if not os.path.isfile(metadata_path):
            logger.error("Unable to find metadata file: %s", metadata_path)
            sys.exit(1)
    else:
        try:
            response = requests.get(original_path)
            response.raise_for_status()
        except RequestException:
            logger.error("Unable to download metadata file: %s", original_path)
            sys.exit(1)

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_f:
            temp_f.write(response.text)
            metadata_path = temp_f.name

    return metadata_path


def get_phase(metadata, phase_name):
    """Get phase from metadata by name.

    :param metadata: metadata object
    :phase_name: predefined phase name (e.g. 'init', 'prep', 'test')
    :return: phase object
    """
    phases = metadata.get("phases", [])
    match = [p for p in phases if p.get("name") == phase_name]

    if len(match):
        return match[0]
    return None


def get_phases_upto(metadata, upto):
    if not get_phase(metadata, upto):
        return []

    match = []
    phases = metadata.get("phases", [])
    for phase in phases:
        match.append(phase)
        if phase.get("name") == upto:
            break

    return match


def run():
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

    if not len(phases):
        logger.error("No phase to run found")
        sys.exit(1)

    rc = run_phases(phases, metadata, metadata_path, args.phase_timeout)
    sys.exit(rc)


if __name__ == "__main__":
    run()
