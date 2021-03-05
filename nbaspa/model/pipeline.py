"""Generate model build/evaluation framework."""

from typing import Dict, Optional

import numpy as np
import prefect
from prefect import Flow, Parameter, unmapped
from prefect.engine.results import LocalResult
from prefect.engine.serializers import PandasSerializer
from prefect.engine.state import State
from prefect.tasks.core.operators import GetItem

from ..serializers import Plot
from .tasks import (
    CollapseData,
    FitLifelinesModel,
    FitXGBoost,
    InitializeLifelines,
    LifelinesTuning,
    LoadData,
    load_df,
    PlotTuning,
    SurvivalData,
    SegmentData,
    XGBoostTuning,
    LoadModel,
    WinProbability,
    AUROC,
    AUROCLift,
    MeanAUROCLift,
    PlotMetric,
)


def gen_data_pipeline() -> Flow:
    """Split the enire input set into build and holdout.

    Saves the ``build.csv`` and ``holdout.csv`` data to the ``models``
    subfolder within ``data_dir``.

    Parameters
    ----------
    None

    Returns
    -------
    Flow
        Generated pipeline.
    """
    # Initialize tasks
    load = LoadData(name="Load clean model data")
    format_data = SurvivalData(name="Convert input data to ranged form")
    segdata = SegmentData(name="Split data")
    retrieve_build = GetItem(
        name="Get build data",
        checkpoint=True,
        result=LocalResult(
            dir=".",
            location="{output_dir}/models/build.csv",
            serializer=PandasSerializer(file_type="csv", serialize_kwargs={"sep": "|"}),
        ),
    )
    retrieve_hold = GetItem(
        name="Get holdout data",
        checkpoint=True,
        result=LocalResult(
            dir=".",
            location="{output_dir}/models/holdout.csv",
            serializer=PandasSerializer(file_type="csv", serialize_kwargs={"sep": "|"}),
        ),
    )
    # Generate the flow
    with Flow(name="Split data into build and holdout") as flow:
        # Set up parameters
        data_dir = Parameter("data_dir", "nba-data")
        splits = Parameter("splits", [0.8, 0.2])
        seed = Parameter("seed", 42)
        # Load the data
        basedata = load(data_dir=data_dir)
        # Format the data
        alldata = format_data(basedata)
        data = segdata(alldata, splits=splits, keys=["build", "holdout"], seed=seed)
        _ = retrieve_build(task_result=data, key="build")
        _ = retrieve_hold(task_result=data, key="holdout")

    return flow


def gen_lifelines_pipeline() -> Flow:
    """Generate a ``lifelines`` model fit pipeline.

    Parameters
    ----------
    None

    Returns
    -------
    Flow
        The generated pipeline.
    """
    # Initialize tasks
    segdata = SegmentData(name="Split data")
    tune_data = CollapseData(name="Create tuning data")
    tuning = LifelinesTuning(
        name="Run lifelines hyperparameter tuning",
        checkpoint=True,
        result=LocalResult(
            dir=".", location="{output_dir}/models/{today}/lifelines/tuning.pkl"
        ),
    )
    tuneplots = PlotTuning(
        name="Plot lifelines hyperparameter tuning",
        checkpoint=True,
        result=LocalResult(
            serializer=Plot(),
            dir=".",
            location="{output_dir}/models/{today}/lifelines/hyperparameter-tuning.png",
        ),
    )
    model = InitializeLifelines(name="Initialize lifelines model")
    trained = FitLifelinesModel(
        name="Train lifelines model",
        checkpoint=True,
        result=LocalResult(
            dir=".", location="{output_dir}/models/{today}/lifelines/model.pkl"
        ),
    )

    # Generate the flow
    with Flow(name="Train Cox model") as flow:
        # Define some parameters
        data_dir = Parameter("data_dir", "nba-data")
        splits = Parameter("splits", [0.75, 0.25])
        max_evals = Parameter("max_evals", 100)
        seed = Parameter("seed", 42)
        # Load the data
        build = load_df(data_dir=data_dir, dataset="build.csv")
        # Segment the data
        data = segdata(build, splits=splits, keys=["train", "tune"], seed=seed)
        # Collapse the data to the final row for Concordance calculations
        tune = tune_data(data["train"])
        # Run hyperparameter tuning
        params = tuning(
            train_data=data["train"], tune_data=tune, max_evals=max_evals, seed=seed
        )
        tuneplots(params["trials"])
        model_obj = model(params["best"])
        _ = trained(model=model_obj, data=data["train"])

    return flow


def gen_xgboost_pipeline() -> Flow:
    """Generate a ``xgboost`` fit pipeline.

    Parameters
    ----------
    None

    Returns
    -------
    Flow
        Generated pipeline.
    """
    # Initialize tasks
    segdata = SegmentData(name="Split data")
    train_data = CollapseData(name="Create training data")
    tune_data = CollapseData(name="Create tuning data")
    stop_data = CollapseData(name="Create stopping data")
    tuning = XGBoostTuning(
        name="Run XGBoost hyperparameter tuning",
        checkpoint=True,
        result=LocalResult(
            dir=".",
            location="{output_dir}/models/{today}/xgboost/tuning.pkl",
        ),
    )
    tuneplots = PlotTuning(
        name="Plot XGBoost hyperparameter tuning",
        checkpoint=True,
        result=LocalResult(
            serializer=Plot(),
            dir=".",
            location="{output_dir}/models/{today}/xgboost/hyperparameter-tuning.png",
        ),
    )
    trained = FitXGBoost(
        name="Train XGBoost model",
        checkpoint=True,
        result=LocalResult(
            dir=".", location="{output_dir}/models/{today}/xgboost/model.pkl"
        ),
    )

    # Generate the flow
    with Flow(name="Train Cox model") as flow:
        # Define some parameters
        data_dir = Parameter("data_dir", "nba-data")
        splits = Parameter("splits", [0.5, 0.25, 0.25])
        max_evals = Parameter("max_evals", 100)
        seed = Parameter("seed", 42)
        # Load the data
        build = load_df(data_dir=data_dir, dataset="build.csv")
        # Segment data into train, stop, tune
        data = segdata(build, splits=splits, keys=["train", "stop", "tune"], seed=seed)
        # Collapse data to the final row
        train = train_data(data["train"])
        tune = tune_data(data["tune"])
        stop = stop_data(data["stop"])
        # Run hyperparameter tuning
        params = tuning(
            train_data=train,
            tune_data=tune,
            stopping_data=stop,
            early_stopping_rounds=10,
            num_boost_round=1000,
            max_evals=max_evals,
            seed=seed,
        )
        tuneplots(params["trials"])
        # Fit the model
        _ = trained(
            params=params["best"],
            train_data=train,
            stopping_data=stop,
            early_stopping_rounds=10,
            num_boost_round=1000,
        )

    return flow


def gen_evaluate_pipeline(**kwargs) -> Flow:
    """Generate pipeline for evaluating models.

    Parameters
    ----------
    **kwargs
        Each key will be the name of a model. The value is the location
        of the model pickle.

    Returns
    -------
    Flow
        The generated pipeline.
    """
    # Create a time range for AUROC calculation -- start to the end of the fourth quarter
    times = np.arange(2880, step=10)
    # Initialize the tasks
    modelobjs: Dict = {}
    calc_sprob: Dict = {}
    sprob_auc: Dict = {}
    calc_lift: Dict = {}
    average_lift: Dict = {}
    for key in kwargs:
        modelobjs[key] = LoadModel(name=f"Load model {key}")
        calc_sprob[key] = WinProbability(
            name=f"Calculate survival probability for model {key}"
        )
        sprob_auc[key] = AUROC(name=f"Calculate Cox PH AUROC for model {key}")
        calc_lift[key] = AUROCLift(name=f"Calculate AUROC life for model {key}")
        average_lift[key] = MeanAUROCLift(
            name=f"Calculate average AUROC lift for model {key}"
        )

    auc_data = CollapseData(name="Create AUROC input data")
    nba_wprob = WinProbability(name="Retrieve NBA win probability")
    wprob_auc = AUROC(name="Calculate NBA AUROC")
    aucplot = PlotMetric(
        name="AUROC over gametime",
        checkpoint=True,
        result=LocalResult(
            dir=".", serializer=Plot(), location="{output_dir}/models/{today}/auroc.png"
        ),
    )
    liftplot = PlotMetric(
        name="AUROC lift over gametime",
        checkpoint=True,
        result=LocalResult(
            dir=".",
            serializer=Plot(),
            location="{output_dir}/models/{today}/auroc_lift.png",
        ),
    )

    # Generate the pipeline
    with Flow(name="Evaluate models") as flow:
        # Define some parameters
        data_dir = Parameter("data_dir", "nba-data")
        # Load the models
        models = {key: modelobjs[key](filepath=value) for key, value in kwargs.items()}
        # Load the holdout data
        holdout = load_df(data_dir=data_dir, dataset="holdout.csv")
        # Collapse the data to each timestamp
        test = auc_data.map(data=unmapped(holdout), timestep=times)
        # Get the predicted probabilities at each time step
        wprob = nba_wprob.map(model=unmapped("nba"), data=test)
        sprob = {
            key: calc_sprob[key].map(model=unmapped(models[key]), data=test)
            for key in kwargs
        }
        # Get the AUROC based on the model outputs
        metric_benchmark = wprob_auc.map(data=wprob, mode=unmapped("benchmark"))
        metric = {key: sprob_auc[key].map(data=sprob[key]) for key in kwargs}
        # Get the AUROC lift
        lift = {
            key: calc_lift[key](benchmark=metric_benchmark, test=metric[key])
            for key in kwargs
        }
        # Plot the AUROC over game-time
        aucplot(times=times, metric="AUROC", nba=metric_benchmark, **metric)
        liftplot(times=times, metric="AUROC Lift", **lift)
        _ = {key: average_lift[key](lift=lift[key], timestep=times) for key in kwargs}

    return flow


def run_pipeline(
    flow: Flow, data_dir: str, output_dir: str, **kwargs
) -> Optional[State]:
    """Run a pipeline.

    Parameters
    ----------
    flow : Flow
        The generated flow.
    data_dir : str
        The directory containing the data.
    output_dir : str
        The output location for the data.
    **kwargs
        Parameter values.

    Returns
    -------
    State
        The output of ``flow.run``.
    """
    with prefect.context(data_dir=data_dir, output_dir=output_dir):
        output = flow.run(parameters={"data_dir": data_dir, **kwargs})

    return output
