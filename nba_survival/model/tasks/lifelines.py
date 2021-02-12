"""Lifelines training and prediction tasks."""

from lifelines import CoxTimeVaryingFitter
import numpy as np
import pandas as pd
from prefect import Task

from .meta import META

class InitializeLifelines(Task):
    """Initialize a new ``lifelines`` model."""
    def run(self, **kwargs) -> CoxTimeVaryingFitter:
        """Initialize a new ``lifelines`` model.

        Parameters
        ----------
        **kwargs
            Keyword arguments for ``CoxTimeVaryingFitter``
        
        Returns
        -------
        CoxTimeVaryingFitter
            The initialized model.
        """
        return CoxTimeVaryingFitter(**kwargs)


class FitLifelinesModel(Task):
    """Fit the lifelines model."""
    def run(
        self,
        model: CoxTimeVaryingFitter,
        data: pd.DataFrame,
        **kwargs
    ) -> CoxTimeVaryingFitter:
        """Fit the lifelines model.

        Parameters
        ----------
        model : CoxTimeVaryingFitter
            The initialized model.
        data : pd.DataFrame
            The ``lifelines`` format data.
        **kwargs
            Keyword arguments for the ``fit`` method.
        
        Returns
        -------
        CoxTimeVaryingFitter
            The fitted model.
        """
        return model.fit(
            data,
            id_col=META["id"],
            event_col=META["event"],
            start_col="start",
            stop_col="stop",
            show_progress=True,
            **kwargs
        )


class PredictLifelines(Task):
    """Get the partial hazard for an observation."""
    def run(self, model: CoxTimeVaryingFitter, data: pd.DataFrame) -> np.ndarray:
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
