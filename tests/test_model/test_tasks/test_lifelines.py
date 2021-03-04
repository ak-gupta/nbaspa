"""Test the lifelines model methods."""

from unittest.mock import patch

from lifelines import CoxTimeVaryingFitter

from nbaspa.model.tasks import (
    InitializeLifelines,
    FitLifelinesModel,
    SurvivalData
)

def test_initialize_lifelines():
    """Test initializing a lifelines model."""
    tsk = InitializeLifelines()
    output = tsk.run()

    assert isinstance(output, CoxTimeVaryingFitter)

@patch("lifelines.CoxTimeVaryingFitter", autospec=True)
def test_fit_lifelines(mock_ll, data):
    """Test fitting a lifelines model."""
    pre = SurvivalData()
    df = pre.run(data)

    model = mock_ll.return_value
    tsk = FitLifelinesModel()
    _ = tsk.run(model=model, data=df)

    assert model.fit.call_count == 1
