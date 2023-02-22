from te.common.step import StepTypes, step_types


def test_smoke():
    """Smoke test of Step registration."""
    assert type(step_types) == StepTypes
