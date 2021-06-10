"""Train and evaluate models."""

import click

from ..pipeline import (
    gen_data_pipeline,
    gen_lifelines_pipeline,
    gen_xgboost_pipeline,
    gen_evaluate_pipeline,
    gen_predict_pipeline,
    run_pipeline,
)


@click.group()
def model():
    """CLI group."""
    pass


@model.command()
@click.option("--data-dir", help="Path to the data directory.")
@click.option("--output-dir", help="Path to the output directory.")
@click.option(
    "--splits",
    type=click.Tuple([float, float, float]),
    default=(0.6, 0.2, 0.2),
    help="Percentage splits for build and holdout data",
)
@click.option("--seed", default=42, type=int, help="Random seed for segmentation")
def build(data_dir, output_dir, splits, seed):
    """Split the entire dataset into train, tune, and holdout sets.

    Saves the data to ``train.csv``, ``tune.csv``, and ``holdout.csv`` within the ``models``
    subfolder in ``data_dir``.
    """
    flow = gen_data_pipeline()
    run_pipeline(
        flow=flow, data_dir=data_dir, output_dir=output_dir, splits=splits, seed=seed
    )


@model.command()
@click.option("--data-dir", help="Path to the data directory.")
@click.option("--output-dir", help="Path to the output directory.")
@click.option(
    "--max-evals",
    default=1000,
    type=int,
    help="Number of hyperparameter tuning iterations",
)
@click.option("--seed", default=42, type=int, help="Random seed for segmentation")
@click.option(
    "--model",
    type=click.Choice(["xgboost", "lifelines"], case_sensitive=True),
    default="lifelines",
    help="Whether to fit an XGBoost or lifelines model",
)
def train(data_dir, output_dir, max_evals, seed, model):
    """Train the survival analysis model.

    The model training involves

    \b
    * Loading the training and stopping/tuning data,
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
        flow = gen_xgboost_pipeline()

    run_pipeline(
        flow=flow,
        data_dir=data_dir,
        output_dir=output_dir,
        max_evals=max_evals,
        seed=seed,
    )


@model.command()
@click.option("--data-dir", help="Path to the data directory.")
@click.option("--output-dir", help="Path to the output directory.")
@click.option(
    "--model",
    multiple=True,
    type=click.Tuple([str, str]),
    help="Alias and location for model pickle files",
)
@click.option(
    "--step",
    type=int,
    default=10,
    help="Number of seconds between each measurement of AUROC",
)
def evaluate(data_dir, output_dir, model, step):
    """Evaluate the models using AUROC over time."""
    flow = gen_evaluate_pipeline(
        **{name: location for name, location in model}, step=step
    )
    run_pipeline(flow, data_dir=data_dir, output_dir=output_dir)


@model.command()
@click.option("--data-dir", help="Path to the data directory.")
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--model", help="Location for model pickle file")
@click.option("--season", default=None, help="The season")
@click.option("--game-id", default=None, help="The Game ID")
def predict(data_dir, output_dir, model, season, game_id):
    """Predict the survival probabilities for game(s)."""
    flow = gen_predict_pipeline()
    run_pipeline(
        flow=flow,
        data_dir=data_dir,
        output_dir=output_dir,
        model=model,
        Season=season,
        GameID=game_id,
    )
