"""Build-in steps."""

from te.common.step import step_types
from te.steps.command import CommandStep
from te.steps.module import ModuleStep
from te.steps.playbook import PlaybookStep
from te.steps.pytests import PytestsStep
from te.steps.restraint import RestraintStep


def register_steps():
    """Register common steps."""
    step_types.register(CommandStep)
    step_types.register(ModuleStep)
    step_types.register(PlaybookStep)
    step_types.register(PytestsStep)
    step_types.register(RestraintStep)
