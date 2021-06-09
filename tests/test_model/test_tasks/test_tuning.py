"""Test hyperparameter tuning."""

import pytest

from nbaspa.model.tasks import (
    LifelinesTuning,
    SegmentData,
    SurvivalData,
    XGBoostTuning,
)

@pytest.fixture(scope="module")
def survivaldata(data):
    """Create survival data for the hyperparameter tuning."""
    pre = SurvivalData()
    df = pre.run(data)
    seg = SegmentData()
    segdata = seg.run(data=df, splits=[0.6, 0.2, 0.2], keys=["train", "tune", "stop"], seed=42)

    return segdata["train"], segdata["tune"], segdata["stop"]

def test_lifelines_tuning(survivaldata):
    """Test running hyperparameter tuning with Lifelines."""
    train, tune, _ = survivaldata
    # Drop nulls because of weirdness with fitting lifelines on random data
    train = train.dropna()
    tune = tune.dropna()
    tsk = LifelinesTuning()
    output = tsk.run(
        train_data=train,
        tune_data=[tune],
        max_evals=10,
    )

    assert isinstance(output, dict)
    assert len(output["trials"].trials) <= 10
    assert "l1_ratio" in output["best"]
    assert "penalizer" in output["best"]
    assert hasattr(tsk, "best_")
    assert hasattr(tsk, "metric_")

def test_xgboost_tuning(survivaldata):
    """Test running hyperparameter tuning with XGBoost."""
    train, tune, stop = survivaldata
    tsk = XGBoostTuning()
    output = tsk.run(
        train_data=train,
        tune_data=[tune],
        stopping_data=stop,
        max_evals=10,
    )

    assert isinstance(output, dict)
    assert len(output["trials"].trials) <= 10
    assert hasattr(tsk, "best_")
    assert hasattr(tsk, "metric_")
    assert "learning_rate" in output["best"]
    assert "subsample" in output["best"]
    assert "max_delta_step" in output["best"]
    assert "max_depth" in output["best"]
    assert "gamma" in output["best"]
    assert "reg_alpha" in output["best"]
    assert "reg_lambda" in output["best"]
    assert "colsample_bytree" in output["best"]
    assert "min_child_weight" in output["best"]
