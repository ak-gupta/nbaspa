"""Lifelines training and prediction tasks."""

from typing import Dict, Optional

from lifelines import CoxTimeVaryingFitter
import numpy as np
import pandas as pd
from prefect import Task

from .meta import META


class InitializeLifelines(Task):
    """Initialize a new ``lifelines`` model."""

    def run(self, params: Optional[Dict] = None) -> CoxTimeVaryingFitter:
        """Initialize a new ``lifelines`` model.

        Parameters
        ----------
        params : dict, optional (default None)
            Keyword arguments for ``CoxTimeVaryingFitter``

        Returns
        -------
        CoxTimeVaryingFitter
            The initialized model.
        """
        return CoxTimeVaryingFitter(**params or {})


class FitLifelinesModel(Task):
    """Fit the lifelines model."""

    def run(
        self, model: CoxTimeVaryingFitter, data: pd.DataFrame, **kwargs
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
        model = model.fit(
            data[
                [META["id"], META["event"]]
                + ["start", "stop"]
                + META["static"]
                + META["dynamic"]
            ],
            id_col=META["id"],
            event_col=META["event"],
            start_col="start",
            stop_col="stop",
            **kwargs
        )

        return model
