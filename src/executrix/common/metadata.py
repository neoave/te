"""Module for job metadata file operations."""

import logging
import os
import re
import sys
import tempfile

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


def is_url(path):
    """Check if `path` starts with 'http(s)://'."""
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
    """Select all phases from start upto a given phase (including)."""
    if not get_phase(metadata, upto):
        return []

    match = []
    phases = metadata.get("phases", [])
    for phase in phases:
        match.append(phase)
        if phase.get("name") == upto:
            break

    return match
