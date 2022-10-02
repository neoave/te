"""Build-in steps."""

from executrix.steps.command import CommandStep
from executrix.steps.playbook import PlaybookStep
from executrix.steps.pytests import PytestsStep
from executrix.steps.restraint import RestraintStep
from executrix.te import step_types

step_types.register(CommandStep)
step_types.register(PlaybookStep)
step_types.register(PytestsStep)
step_types.register(RestraintStep)
