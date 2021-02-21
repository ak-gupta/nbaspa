"""Train and evaluate models."""

import click

from ..pipeline import (
    gen_data_pipeline,
    gen_lifelines_pipeline,
    gen_xgboost_pipeline,
    gen_evaluate_pipeline,
    run_pipeline
)

@click.group()
def model():
    """CLI group."""
    pass

@model.command()
@click.option("--data-dir", help="Path to the data directory.")
@click.option(
    "--splits",
    type=click.Tuple([float, float]),
    default=(0.85, 0.15),
    help="Percentage splits for build and holdout data",
)
@click.option(
    "--seed", default=42, type=int, help="Random seed for segmentation"
)
def build(data_dir, splits, seed):
    """Split the entire dataset into build and holdout sets.

    Saves the data to ``build.csv`` and ``holdout.csv`` within the ``models``
    subfolder in ``data_dir``.
    """
    flow = gen_data_pipeline()
    run_pipeline(
        flow=flow,
        data_dir=data_dir,
        splits=splits,
        seed=seed
    )

@model.command()
@click.option("--data-dir", help="Path to the data directory.")
@click.option(
    "--splits",
    type=float,
    multiple=True,
    default=(0.7, 0.3),
    help="Percentage splits for train, stopping, and tune data",
)
@click.option(
    "--max-evals",
    default=100,
    type=int,
    help="Number of hyperparameter tuning iterations",
)
@click.option(
    "--seed", default=42, type=int, help="Random seed for segmentation"
)
@click.option(
    "--model",
    type=click.Choice(["xgboost", "lifelines"], case_sensitive=True),
    default="lifelines",
    help="Whether to fit an XGBoost or lifelines model"
)
def train(data_dir, splits, max_evals, seed, model):
    """Train the survival analysis model.

    The model training involves

    \b
    * Loading the ``build.csv`` data,
    * Segment the data,
    * Tune the parameters using ``hyperopt``, and
    * Fit the model using the best parameters.

    The following object will be saved:

    \b
    * ``tuning.pkl``: The output from hyperparameter tuning,
    * ``model.pkl``: The fitted model object, and
    * ``hyperparameter-tuning.png``: A visualization of the hyperparameter tuning
    """
    if model == "lifelines":
        flow = gen_lifelines_pipeline()
    else:
        if len(splits) < 3:
            click.secho(
                "Please provide 3 values for split (one for train, stop, and tune)", fg="red"
            )
            raise ValueError
        flow = gen_xgboost_pipeline()
    
    run_pipeline(
        flow=flow,
        data_dir=data_dir,
        splits=splits,
        max_evals=max_evals,
        seed=seed,
    )

@model.command()
@click.option("--data-dir", help="Path to the data directory.")
@click.option(
    "--model",
    multiple=True,
    type=click.Tuple([str, str]),
    help="Alias and location for model pickle files",
)
def evaluate(data_dir, model):
    """Evaluate the models using AUROC over time."""
    flow = gen_evaluate_pipeline(
        **{name: location for name, location in model}
    )
    run_pipeline(flow, data_dir=data_dir)
