"""Tasks for XGBoost."""

from typing import Dict, Optional

import numpy as np
import pandas as pd
from prefect import Task
import xgboost as xgb

from .meta import META


class FitXGBoost(Task):
    """Fit the XGBoost model."""

    def run(  # type: ignore
        self,
        train_data: pd.DataFrame,
        params: Optional[Dict] = None,
        stopping_data: Optional[pd.DataFrame] = None,
        seed: Optional[int] = 42,
        **kwargs
    ) -> xgb.Booster:
        """Fit the XGBoost model.

        This model will be fitted using a custom objective function.

        Parameters
        ----------
        params : dict
            The parameters for the model.
        train_data : pd.DataFrame
            The training data, from ``SurvivalData.run()``.
        stopping_data : pd.DataFrame, optional (default None)
            Early stopping data, from ``SurvivalData.run()``.
        seed : int, optional (default 42)
            Seed.
        **kwargs
            Keyword arguments for ``xgb.train``.

        Returns
        -------
        xgb.Booster
            The fitted model
        """
        # Create datasets
        self.logger.info("Converting training data to ``xgb.DMatrix``")
        dtrain = _convert_data(data=train_data)
        evals = [
            (dtrain, "train"),
        ]
        if stopping_data is not None:
            self.logger.info("Converting stopping data to ``xgb.DMatrix``")
            dstop = _convert_data(data=stopping_data)
            evals.append((dstop, "stopping"))

        self.logger.info("Training the model...")
        initial_params = {"objective": "survival:cox", "seed": seed}
        if params is not None:
            if "early_stopping_rounds" in params:
                params.pop("early_stopping_rounds")
            if "num_boost_round" in params:
                params.pop("num_boost_round")
            initial_params.update(params)
        model = xgb.train(initial_params, dtrain, evals=evals, **kwargs)
        self.logger.info("Model training complete...")
        # Get the cumulative hazard using ``lifelines``
        model.cumulative_hazard_ = _generate_cumulative_hazard(
            model=model, train_data=train_data, dtrain=dtrain
        )

        return model


def _convert_data(data: pd.DataFrame) -> xgb.DMatrix:
    """Convert the input dataframe to the format expected by XGBoost.

    Parameters
    ----------
    data : pd.DataFrame
        The input data.
    
    Returns
    -------
    xgb.DMatrix
        The output object for XGBoost.
    """
    df = data.copy()
    df.loc[df[META["event"]] == 0, "stop"] = -df["stop"]
    dmat = xgb.DMatrix(df[META["static"] + META["dynamic"]], df["stop"])

    return dmat

def _generate_cumulative_hazard(
    model: xgb.Booster,
    train_data: pd.DataFrame,
    dtrain: xgb.DMatrix,
) -> np.ndarray:
    """Generate the cumulative hazard.

    Parameters
    ----------
    model : xgb.Booster
        The trained model.
    train_data : pd.DataFrame
        The training dataset.
    dtrain : xgb.DMatrix
        The training dataset.

    Returns
    -------
    np.ndarray
        The array output.
    """
    # First, get the partial hazard values
    hazard = model.predict(dtrain)
    # Get the unique failure times
    unique_death_times = np.unique(
        train_data.loc[train_data[META["event"]] == 1, "stop"].values
    )
    baseline_hazard_ = pd.DataFrame(
        np.zeros_like(unique_death_times),
        index=unique_death_times,
        columns=["baseline hazard"],
    )

    for t in unique_death_times:
        ix = (train_data["start"].values < t) & (t <= train_data["stop"].values)

        events_at_t = train_data[META["event"]].values[ix]
        stops_at_t = train_data["stop"].values[ix]
        hazards_at_t = hazard[ix]

        deaths = events_at_t & (stops_at_t == t)

        death_counts = deaths.sum()
        baseline_hazard_.loc[t] = death_counts / hazards_at_t.sum()

    return baseline_hazard_.cumsum()
