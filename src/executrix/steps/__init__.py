"""Build-in steps."""

from executrix.common.step import step_types
from executrix.steps.command import CommandStep
from executrix.steps.module import ModuleStep
from executrix.steps.playbook import PlaybookStep
from executrix.steps.pytests import PytestsStep
from executrix.steps.restraint import RestraintStep


def register_steps():
    """Register common steps."""
    step_types.register(CommandStep)
    step_types.register(ModuleStep)
    step_types.register(PlaybookStep)
    step_types.register(PytestsStep)
    step_types.register(RestraintStep)
