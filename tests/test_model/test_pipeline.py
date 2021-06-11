"""Test pipeline tasks."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from nbaspa.model.pipeline import (
    gen_data_pipeline,
    gen_lifelines_pipeline,
    gen_xgboost_pipeline,
    gen_evaluate_pipeline,
    gen_predict_pipeline,
    run_pipeline
)

TODAY = datetime.now()

def test_data_pipeline(gamelocation):
    """Test game location."""
    flow = gen_data_pipeline()
    output = run_pipeline(
        flow=flow, data_dir=gamelocation, output_dir=gamelocation, seed=42
    )

    assert output.is_successful()
    assert Path(gamelocation, "models", "train.csv").is_file()
    assert Path(gamelocation, "models", "tune.csv").is_file()
    assert Path(gamelocation, "models", "holdout.csv").is_file()

    train = pd.read_csv(
        Path(gamelocation, "models", "train.csv"),
        sep="|",
        dtype={"GAME_ID": str}
    )
    tune = pd.read_csv(
        Path(gamelocation, "models", "tune.csv"),
        sep="|",
        dtype={"GAME_ID": str}
    )
    holdout = pd.read_csv(
        Path(gamelocation, "models", "holdout.csv"),
        sep="|",
        dtype={"GAME_ID": str}
    )

    assert len(np.unique(train["GAME_ID"].values)) == 120
    assert len(np.unique(tune["GAME_ID"].values)) == 40
    assert len(np.unique(holdout["GAME_ID"].values)) == 40

@patch("nbaspa.model.tasks.tuning.roc_auc_score")
def test_lifelines_pipelines(mock_auc, gamelocation):
    """Test fitting a lifelines model."""
    mock_auc.return_value = 0.5
    # Create and run the flow
    train = pd.read_csv(
        Path(gamelocation, "models", "train.csv"),
        sep="|",
        dtype={"GAME_ID": str}
    )
    tune = pd.read_csv(
        Path(gamelocation, "models", "tune.csv"),
        sep="|",
        dtype={"GAME_ID": str}
    )
    holdout = pd.read_csv(
        Path(gamelocation, "models", "holdout.csv"),
        sep="|",
        dtype={"GAME_ID": str}
    )
    # Drop nulls because of the weirdness with random data
    train = train.dropna()
    train.to_csv(
        Path(gamelocation, "models", "train.csv"), sep="|"
    )
    tune = tune.dropna()
    tune.to_csv(
        Path(gamelocation, "models", "tune.csv"), sep="|"
    )
    holdout = holdout.dropna()
    holdout.to_csv(
        Path(gamelocation, "models", "holdout.csv"), sep="|"
    )

    # Create and run the lifelines flow
    flow = gen_lifelines_pipeline()
    output = run_pipeline(
        flow=flow,
        data_dir=gamelocation,
        output_dir=gamelocation,
        max_evals=5,
        seed=42
    )

    assert output.is_successful()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "lifelines", "model.pkl").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "lifelines", "tuning.pkl").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "lifelines", "hyperparameter-tuning.png").is_file()

@patch("nbaspa.model.tasks.tuning.roc_auc_score")
def test_xgboost_pipeline(mock_auc, gamelocation):
    """Test fitting XGBoost model."""
    mock_auc.return_value = 0.5
    # Create and run the XGBoost flow
    flow = gen_xgboost_pipeline()
    output = run_pipeline(
        flow=flow,
        data_dir=gamelocation,
        output_dir=gamelocation,
        max_evals=5,
        seed=42
    )

    assert output.is_successful()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "model.pkl").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "tuning.pkl").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "hyperparameter-tuning.png").is_file()

@patch("nbaspa.model.tasks.AUROC.run")
def test_evaluate_pipeline(mock_auc, gamelocation):
    """Test evaluate pipeline."""
    mock_auc.return_value = 0.5
    flow = gen_evaluate_pipeline(
        step=288,
        xgboost=Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "model.pkl"),
    )
    output = run_pipeline(
        flow=flow, data_dir=gamelocation, output_dir=gamelocation
    )

    assert output.is_successful()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "auroc.png").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "auroc_lift.png").is_file()


@patch("lifelines.CoxTimeVaryingFitter.predict_partial_hazard")
def test_predict_pipeline(mock_pred, gamelocation):
    """Test the prediction pipeline."""
    mock_pred.return_value = pd.Series([0.5])
    flow = gen_predict_pipeline()
    output = run_pipeline(
        flow=flow,
        data_dir=gamelocation,
        output_dir=gamelocation,
        filesystem="file",
        model=str(
            Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "lifelines", "model.pkl")
        )
    )

    assert output.is_successful()
    assert Path(gamelocation, "2018-19", "survival-prediction").is_dir()
    assert len(list(Path(gamelocation, "2018-19", "survival-prediction").glob("data_*.csv"))) == 200
