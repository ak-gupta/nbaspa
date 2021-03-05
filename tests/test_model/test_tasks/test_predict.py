"""Test prediction functions."""

from lifelines import CoxTimeVaryingFitter
import pytest

from nbaspa.model.tasks import (
    FitLifelinesModel,
    FitXGBoost,
    WinProbability,
    SegmentData,
    SurvivalData
)

@pytest.fixture(scope="module")
def survivaldata(data):
    """Create survival data for the prediction testing."""
    pre = SurvivalData()
    df = pre.run(data)
    seg = SegmentData()
    segdata = seg.run(data=df)

    return segdata["train"], segdata["test"]

def test_predict_proba_lifelines(survivaldata):
    """Test prediction with a lifelines model."""
    train_data, test_data = survivaldata
    # Dropping null rows because of the weirdness with randomly generated data
    train_data = train_data.dropna()
    test_data = test_data.dropna()
    # Fit the model
    fitter = FitLifelinesModel()
    trained = fitter.run(model=CoxTimeVaryingFitter(), data=train_data)
    # Predict
    tsk = WinProbability()
    output = tsk.run(model=trained, data=test_data)

    assert output["WIN_PROB"].max() <= 1.0
    assert output["WIN_PROB"].min() >= 0.0

def test_predict_proba_xgboost(survivaldata):
    """Test prediction with an XGBoost model."""
    train_data, test_data = survivaldata
    # Fit the model
    fitter = FitXGBoost()
    trained = fitter.run(
        train_data=train_data,
        stopping_data=test_data,
        early_stopping_rounds=5
    )
    # Predict
    tsk = WinProbability()
    output = tsk.run(model=trained, data=test_data)

    assert output["WIN_PROB"].max() <= 1.0
    assert output["WIN_PROB"].min() >= 0.0
