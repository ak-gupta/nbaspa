"""Train and evaluate the XGBoost model."""

import logging
from pathlib import Path
import sys

import click
import numpy as np
import pandas as pd
import prefect
from prefect import Flow, unmapped
from prefect.engine.results import LocalResult
from prefect.engine.serializers import JSONSerializer

from ...serializers import Plot
from ..tasks import (
    SurvivalData,
    SegmentData,
    CollapseData,
    XGBoostTuning,
    PlotTuning,
    FitXGBoost,
    Predict,
    ConcordanceIndex,
    WinProbability,
    AUROC,
    PlotMetric,
)

LOG = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


@click.group()
def build():
    """CLI group."""
    pass


@build.command()
@click.option("--data-dir", help="Path to the data directory.")
@click.option(
    "--splits",
    nargs=3,
    type=click.Tuple([float, float, float]),
    default=(0.6, 0.2, 0.1),
    help="Percentage splits for training, tuning, stopping, and test data",
)
@click.option(
    "--max-evals",
    default=100,
    type=int,
    help="Number of hyperparameter tuning iterations",
)
@click.option(
    "--seed", default=42, type=int, help="Random seed for segmentation and tuning"
)
def train(data_dir, splits, max_evals, seed):
    """Train the survival analysis model.

    The model training will involve

    \b
    * Loading the ``model-data`` from ``data_dir``,
    * Segmenting the data into ``train``, ``stopping``, ``test``, and ``tune``,
    * Tuning the data using ``hyperopt``,
    * Fitting the model using the best parameters from hyperparameter tuning,
    * Calculate the Concordance index for the model with the test data,
    * Calculate the AUROC for the model and the NBA win probability using various
      time values, and
    * Plot the AUROC over game-time.

    The following objects will be saved to the ``models/xgboost`` folder within ``data_dir``:

    \b
    * ``tuning.pkl``: The output from hyperparameter tuning,
    * ``model.pkl``: The fitted model object,
    * ``train.csv``: The training data for the model,
    * ``test.csv``: The test data for the model,
    * ``tune.csv``: The tune data for the model,
    * ``hyperparameter-tuning.png``: A visualization of the hyperparameter tuning output, and
    * ``AUROC over gametime.png``: A visualization of AUROC over gametime.
    """
    # First, read in the model data
    LOG.info(f"Reading the model data from {data_dir}")
    basedata = pd.concat(
        pd.read_csv(fpath, sep="|", dtype={"GAME_ID": str}, index_col=0)
        for fpath in Path(data_dir).glob("*/model-data/data_*.csv")
    ).reset_index(drop=True)
    # Create a time range for AUROC calculation -- start to the end of the fourth quarter
    times = np.linspace(0, 2880, 25)
    # Initialize tasks
    format_data = SurvivalData(name="Convert input data to ranged form")
    segdata = SegmentData(name="Split data")
    train_data = CollapseData(name="Create training data")
    tune_data = CollapseData(name="Create tuning data")
    stop_data = CollapseData(name="Create stopping data")
    test_data = CollapseData(name="Create test data")
    test_auc_data = CollapseData(name="Create AUROC test data")
    tuning = XGBoostTuning(
        name="Run Hyperparameter tuning",
        checkpoint=True,
        result=LocalResult(
            dir=".",
            location="{data_dir}/models/xgboost/{today}/tuning.pkl",
        ),
    )
    tuneplots = PlotTuning(
        name="Hyperparameter tuning visualization",
        checkpoint=True,
        result=LocalResult(
            serializer=Plot(),
            dir=".",
            location="{data_dir}/models/xgboost/{today}/hyperparameter-tuning.png",
        ),
    )
    trained = FitXGBoost(
        name="Train Cox PH model",
        checkpoint=True,
        result=LocalResult(
            dir=".", location="{data_dir}/models/xgboost/{today}/model.pkl"
        ),
    )
    hazpred = Predict(name="Calculate partial hazard function")
    concordance = ConcordanceIndex(name="Calculate C-index")
    calc_sprob = WinProbability(name="Calculate win probability")
    nba_wprob = WinProbability(name="Calculate NBA win probability")
    sprob_auc = AUROC(name="Calculate Cox PH AUROC")
    wprob_auc = AUROC(name="Calculate NBA AUROC")
    metricplot = PlotMetric(
        name="AUROC over gametime",
        checkpoint=True,
        result=LocalResult(
            serializer=Plot(),
            dir=".",
            location="{data_dir}/models/xgboost/{today}/auroc.png",
        ),
    )
    # Generate the flow
    with Flow(name="Train Cox model") as flow:
        # Format the data and segment into train, tune, test
        alldata = format_data(basedata)
        data = segdata(
            alldata, splits=splits, keys=["train", "tune", "stop", "test"], seed=seed
        )
        # Collapse data to the final row so we can calculate Concordance
        train = train_data(data["train"])
        tune = tune_data(data["tune"])
        stop = stop_data(data["stop"])
        test = test_data(data["test"])
        test_auc = test_auc_data.map(data=unmapped(data["test"]), timestep=times)
        # Run hyperparameter tuning
        params = tuning(
            train_data=train,
            tune_data=tune,
            stopping_data=stop,
            early_stopping_rounds=5,
            num_boost_round=1000,
            max_evals=max_evals,
            seed=seed,
        )
        tuneplots(params["trials"])
        # Fit the model
        fitted = trained(
            params=params["best"],
            train_data=train,
            stopping_data=stop,
            early_stopping_rounds=5,
            num_boost_round=1000,
        )
        # Get the final Concordance
        predt = hazpred(model=fitted, data=test)
        concordance(data=test, predt=predt)
        # Calculate win probability at various times in the game -- benchmark with NBA
        sprob = calc_sprob.map(model=unmapped(fitted), data=test_auc)
        wprob = nba_wprob.map(model=unmapped("nba"), data=test_auc)
        # Get the AUROC based on Cox PH model output -- benchmark with NBA
        metric = sprob_auc.map(data=sprob)
        metric_benchmark = wprob_auc.map(data=wprob, mode=unmapped("benchmark"))
        # Plot the AUROC over game-time
        metricplot(times=times, metric="AUROC", survival=metric, nba=metric_benchmark)

    with prefect.context(data_dir=data_dir):
        flow.run()
