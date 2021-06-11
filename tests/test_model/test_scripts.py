"""Test the model CLI."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner
import pandas as pd

from nbaspa.model.scripts.model import build, train, predict

TODAY = datetime.now()

def test_build_cli(gamelocation):
    """Test creating build and holdout data."""
    runner = CliRunner()
    result = runner.invoke(
        build, [f"--data-dir={gamelocation}", f"--output-dir={gamelocation}"]
    )

    assert result.exit_code == 0
    assert Path(gamelocation, "models", "train.csv").is_file()
    assert Path(gamelocation, "models", "tune.csv").is_file()
    assert Path(gamelocation, "models", "holdout.csv").is_file()

def test_train_xgboost_cli(gamelocation):
    """Test training an XGBoost model."""
    runner = CliRunner()
    result = runner.invoke(
        train,
        [
            f"--data-dir={gamelocation}",
            f"--output-dir={gamelocation}",
            "--max-evals=5",
            "--model=xgboost"
        ]
    )

    assert result.exit_code == 0
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "model.pkl").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "tuning.pkl").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "hyperparameter-tuning.png").is_file()

@patch("nbaspa.model.tasks.tuning.roc_auc_score")
def test_train_lifelines_cli(mock_auc, gamelocation):
    """Test training a lifelines model."""
    mock_auc.return_value = 0.5
    # Drop null rows in the existing data because of weirdness in random nulls
    dftrain = pd.read_csv(
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
    dftrain = dftrain.dropna()
    dftrain.to_csv(
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

    runner = CliRunner()
    result = runner.invoke(
        train,
        [
            f"--data-dir={gamelocation}",
            f"--output-dir={gamelocation}",
            "--max-evals=5",
            "--model=lifelines"
        ]
    )

    assert result.exit_code == 0
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "lifelines", "model.pkl").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "lifelines", "tuning.pkl").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "lifelines", "hyperparameter-tuning.png").is_file()


def test_predict_xgboost_cli(gamelocation):
    """Test predicting the output for an XGBoost model."""
    runner = CliRunner()
    model = Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "model.pkl")
    result = runner.invoke(
        predict,
        [
            f"--data-dir={gamelocation}",
            f"--output-dir={gamelocation}",
            f"--model={str(model)}",
        ]
    )

    assert result.exit_code == 0
    assert len(list(Path(gamelocation, "2018-19", "survival-prediction").glob("data_*.csv"))) == 200


@patch("lifelines.CoxTimeVaryingFitter.predict_partial_hazard")
def test_predict_lifelines_cli(mock_pred, gamelocation):
    """Test predicting the output for a Lifelines model."""
    runner = CliRunner()
    mock_pred.return_value = pd.Series([0.5])
    model = Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "lifelines", "model.pkl")
    result = runner.invoke(
        predict,
        [
            f"--data-dir={gamelocation}",
            f"--output-dir={gamelocation}",
            f"--model={str(model)}"
        ]
    )

    assert result.exit_code == 0
    assert len(list(Path(gamelocation, "2018-19", "survival-prediction").glob("data_*.csv"))) == 200