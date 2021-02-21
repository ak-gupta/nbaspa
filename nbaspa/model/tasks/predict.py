"""Create a task for getting the survival probability."""

from pandas.core.algorithms import isin
from lifelines import CoxTimeVaryingFitter
from lifelines.utils import interpolate_at_times
import numpy as np
import pandas as pd
from prefect import Task
import xgboost as xgb

from .meta import META


class Predict(Task):
    """Get the partial hazard for an observation."""

    def run(self, model, data: pd.DataFrame) -> np.ndarray:
        """Get the partial hazard for an observation.

        Parameters
        ----------
        model
            The fitted model.
        data : pd.DataFrame
            The input dataframe.

        Returns
        -------
        np.ndarray
            The predicted values.
        """
        if isinstance(model, CoxTimeVaryingFitter):
            return self._run_lifelines(model, data)
        elif isinstance(model, xgb.Booster):
            return self._run_xgboost(model, data)
        else:
            self.logger.error("No method specified for this model type")
            raise NotImplementedError("No method specified for this model type")

    @staticmethod
    def _run_lifelines(model: CoxTimeVaryingFitter, data: pd.DataFrame) -> np.ndarray:
        """Get the partial hazard for an observation.

        Parameters
        ----------
        model : CoxTimeVaryingFitter
            The fitted model.
        data : pd.DataFrame
            The input dataframe.

        Returns
        -------
        np.ndarray
            The predicted values.
        """
        return model.predict_partial_hazard(data)

    @staticmethod
    def _run_xgboost(model: xgb.Booster, data: pd.DataFrame) -> np.ndarray:
        """Get the partial hazard for an observation.

        Parameters
        ----------
        model : xgb.Booster
            The fitted model.
        data : pd.DataFrame
            The input dataframe.

        Returns
        -------
        np.ndarray
            The predicted values.
        """
        dmat = xgb.DMatrix(data[META["static"] + META["dynamic"]])

        return model.predict(dmat)


class WinProbability(Task):
    """Retrieve the win probability."""

    def run(self, model, data: pd.DataFrame) -> pd.DataFrame:
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
        vals = model.predict_partial_hazard(data)
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
        # Get the cumulative hazard using ``lifelines``
        # First, get the partial hazard values
        hazard = model.predict(xgb.DMatrix(data[META["static"] + META["dynamic"]]))
        # Get the unique failure times
        unique_death_times = np.unique(
            data.loc[data[META["event"]] == 1, "stop"].values
        )
        baseline_hazard_ = pd.DataFrame(
            np.zeros_like(unique_death_times),
            index=unique_death_times,
            columns=["baseline hazard"],
        )

        for t in unique_death_times:
            ix = (data["start"].values < t) & (t <= data["stop"].values)

            events_at_t = data[META["event"]].values[ix]
            stops_at_t = data["stop"].values[ix]
            hazards_at_t = hazard[ix]

            deaths = events_at_t & (stops_at_t == t)

            death_counts = deaths.sum()
            baseline_hazard_.loc[t] = death_counts / hazards_at_t.sum()

        cumulative_hazard_ = baseline_hazard_.cumsum()

        # Get the cumulative probability
        c0 = interpolate_at_times(cumulative_hazard_, data["stop"].values)
        new = data.copy()
        new[META["survival"]] = 1 - np.exp(-(c0 * hazard))

        return new
