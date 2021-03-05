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
    segdata = seg.run(data=df, splits=[0.6, 0.2], keys=["train", "tune", "stop"])

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
        tune_data=tune,
        max_evals=10,
    )

    assert isinstance(output, dict)
    assert len(output["trials"].trials) <= 10
    assert "l1_ratio" in output["best"]
    assert "penalizer" in output["best"]
    assert output["best"]["l1_ratio"] >= 0.0
    assert output["best"]["l1_ratio"] <= 1.0
    assert output["best"]["penalizer"] >= 0.0
    assert output["best"]["penalizer"] <= 1.0

def test_xgboost_tuning(survivaldata):
    """Test running hyperparameter tuning with XGBoost."""
    train, tune, stop = survivaldata
    tsk = XGBoostTuning()
    output = tsk.run(
        train_data=train,
        tune_data=tune,
        stopping_data=stop,
        max_evals=10,
    )

    assert isinstance(output, dict)
    assert len(output["trials"].trials) <= 10
    assert output["best"]["learning_rate"] >= 0.05
    assert output["best"]["learning_rate"] <= 0.5
    assert output["best"]["subsample"] >= 0.8
    assert output["best"]["subsample"] <= 1.0
    assert output["best"]["max_delta_step"] >= 0
    assert output["best"]["max_delta_step"] <= 10
    assert output["best"]["max_depth"] >= 2
    assert output["best"]["max_depth"] <= 20
    assert output["best"]["gamma"] >= 5
    assert output["best"]["gamma"] <= 9
    assert output["best"]["reg_alpha"] >= 0
    assert output["best"]["reg_alpha"] <= 50
    assert output["best"]["reg_lambda"] >= 0.0
    assert output["best"]["reg_lambda"] <= 1
    assert output["best"]["colsample_bytree"] >= 0.2
    assert output["best"]["colsample_bytree"] <= 0.6
    assert output["best"]["min_child_weight"] >= 0
    assert output["best"]["min_child_weight"] <= 10
