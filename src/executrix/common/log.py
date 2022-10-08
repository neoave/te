"""Utility module for logging."""

import logging
import sys
from datetime import datetime

from xtermcolor import colorize

from executrix.config import config


class ColorHandler(logging.Handler):
    """Log handler for colorizing log output."""

    level_output = {
        logging.INFO: (sys.stdout, 36),  # cyan
        logging.DEBUG: (sys.stdout, 32),  # green
        logging.ERROR: (sys.stderr, 31),  # red
        logging.WARNING: (sys.stdout, 33),  # yellow
    }

    def handle(self, record):
        """Colorize the record and print it to matching output."""
        output, color = self.level_output.get(record.levelno)
        color = getattr(record, "color", color)

        c_text = self._format_output(record.msg, ansi_color=color)
        print(c_text, file=output, flush=True)

    def _format_output(self, text, ansi_color=None):
        if ansi_color:
            text = colorize(text, ansi=ansi_color)
        if config["print_timestamp"]:
            time = datetime.now().isoformat(timespec="seconds")
            text = f"{time} {text}"
        return text
