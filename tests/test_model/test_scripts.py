"""Test the model CLI."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner
import pandas as pd

from nbaspa.model.scripts.model import build, train

TODAY = datetime.now()

def test_build_cli(gamelocation):
    """Test creating build and holdout data."""
    runner = CliRunner()
    result = runner.invoke(
        build, [f"--data-dir={gamelocation}", f"--output-dir={gamelocation}"]
    )

    assert result.exit_code == 0
    assert Path(gamelocation, "models", "build.csv").is_file()
    assert Path(gamelocation, "models", "holdout.csv").is_file()

def test_train_xgboost_cli(gamelocation):
    """Test training an XGBoost model."""
    runner = CliRunner()
    result = runner.invoke(
        train,
        [
            f"--data-dir={gamelocation}",
            f"--output-dir={gamelocation}",
            "--splits=0.5",
            "--splits=0.25",
            "--splits=0.25",
            "--max-evals=5",
            "--model=xgboost"
        ]
    )

    assert result.exit_code == 0
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "model.pkl").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "tuning.pkl").is_file()
    assert Path(gamelocation, "models", TODAY.strftime("%Y-%m-%d"), "xgboost", "hyperparameter-tuning.png").is_file()

def test_train_lifelines_cli(gamelocation):
    """Test training a lifelines model."""
    # Drop null rows in the existing data because of weirdness in random nulls
    build = pd.read_csv(
        Path(gamelocation, "models", "build.csv"),
        sep="|",
        dtype={"GAME_ID": str}
    )
    holdout = pd.read_csv(
        Path(gamelocation, "models", "holdout.csv"),
        sep="|",
        dtype={"GAME_ID": str}
    )
    # Drop nulls because of the weirdness with random data
    build = build.dropna()
    build.to_csv(
        Path(gamelocation, "models", "build.csv"), sep="|"
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
