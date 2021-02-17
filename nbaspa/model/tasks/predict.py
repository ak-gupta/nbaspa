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
        else:
            return self._run_xgboost(model, data)

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
    def _run_xgboost(model, data: pd.DataFrame) -> np.ndarray:
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
        else:
            self.logger.error("No method specified for this model type")
            raise NotImplementedError("No method specified for this model type")

    @staticmethod
    def _run_lifelines(
        model: CoxTimeVaryingFitter,
        data: pd.DataFrame
    ) -> np.ndarray:
        """Retrieve the win probability.

        Parameters
        ----------
        model : CoxTimeVaryingFitter
            The fitted model.
        data : pd.DataFrame
            The input dataset to be evaluated.
        
        Returns
        -------
        """
        # Get the cumulative hazard -- copying from ``lifelines.fitters.SemiParametericPHFitter``
        vals = model.predict_partial_hazard(data)
        c0 = interpolate_at_times(model.baseline_cumulative_hazard_, data["stop"].values)
        # Survival is the negative exponent of the cumulative hazard
        data[META["survival"]] = 1 - np.exp(-(c0 * vals.values))

        return data
