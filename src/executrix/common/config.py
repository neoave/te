"""Configuration module."""

DEFAULT_PHASE_TIMEOUT = 4 * 60 * 60


config = {
    "dry_run": False,
    "print_timestamp": False,
    "phase_timeout": DEFAULT_PHASE_TIMEOUT,
    "private_key_path": "config/id_rsa",
}
