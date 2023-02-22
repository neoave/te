"""Module for te exceptions."""


class BrokenInstallation(Exception):
    """Broken Installation exception."""

    pass


class PlaybookNotFound(Exception):
    """Raised when Playbook file is not found."""

    def __init__(self, playbook):
        """Exception initialization."""
        super().__init__()
        self.playbook = playbook


class TimeoutException(Exception):
    """Raised when step or phase time-outs."""

    def __init__(self, timeout):
        """Exception initialization."""
        super().__init__()
        self.msg = f"Timed out after {timeout}s."
