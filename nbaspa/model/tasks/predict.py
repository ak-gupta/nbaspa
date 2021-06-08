"""Create a task for getting the survival probability."""

from lifelines import CoxTimeVaryingFitter
from lifelines.utils import interpolate_at_times
import numpy as np
import pandas as pd
from prefect import Task
import xgboost as xgb

from .meta import META


class WinProbability(Task):
    """Retrieve the win probability."""

    def run(self, model, data: pd.DataFrame) -> pd.DataFrame:  # type: ignore
        """Retrieve the win probability.

        Parameters
        ----------
        model
            The fitted model.
        data : pd.DataFrame
            The input dataset to be evaluated.

        Returns
        -------
        pd.DataFrame
            The input dataset with an additional column: ``SURV_PROB``.
        """
        if isinstance(model, CoxTimeVaryingFitter):
            return self._run_lifelines(model=model, data=data)
        elif isinstance(model, str) and model == "nba":
            return data
        elif isinstance(model, xgb.Booster):
            return self._run_xgboost(model=model, data=data)
        else:
            self.logger.error("No method specified for this model type")
            raise NotImplementedError("No method specified for this model type")

    @staticmethod
    def _run_lifelines(model: CoxTimeVaryingFitter, data: pd.DataFrame) -> pd.DataFrame:
        """Retrieve the win probability.

        Parameters
        ----------
        model : CoxTimeVaryingFitter
            The fitted model.
        data : pd.DataFrame
            The input dataset to be evaluated.

        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Get the cumulative hazard -- copying from ``lifelines.fitters.SemiParametericPHFitter``
        vals = model.predict_partial_hazard(data[META["static"] + META["dynamic"]])
        c0 = interpolate_at_times(
            model.baseline_cumulative_hazard_, data["stop"].values
        )
        # Survival is the negative exponent of the cumulative hazard
        new = data.copy()
        new[META["survival"]] = 1 - np.exp(-(c0 * vals.values))

        return new

    @staticmethod
    def _run_xgboost(model: xgb.Booster, data: pd.DataFrame) -> pd.DataFrame:
        """Retrieve the win probability.

        Parameters
        ----------
        model : xgb.Booster
            The fitted XGBoost model.
        data : pd.DataFrame
            The input dataset to be evaluated.

        Returns
        -------
        np.ndarray
            The updated dataset.
        """
        # First, get the partial hazard values
        hazard = model.predict(xgb.DMatrix(data[META["static"] + META["dynamic"]]))
        # Get the cumulative probability
        c0 = interpolate_at_times(model.cumulative_hazard_, data["stop"].values)
        new = data.copy()
        new[META["survival"]] = 1 - np.exp(-(c0 * hazard))

        return new
