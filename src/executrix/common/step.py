"""Module with base classes for steps and their registration."""


class StepType:
    """Base class for steps."""

    def run(self, timeout, **kwargs):
        """Run the step."""
        raise NotImplementedError

    @staticmethod
    def match(options):
        """Figure out of this StepType matches step in job metadata."""
        raise NotImplementedError


class StepTypes:
    """Registry for step types."""

    def __init__(self):
        """Registry initialization."""
        self._step_types = set()

    def register(self, step_type):
        """Register new step type."""
        self._step_types.add(step_type)

    def resolve(self, options):
        """Get matching StepType."""
        for step_type in self._step_types:
            if step_type.match(options):
                return step_type(options)
        return None


step_types = StepTypes()
