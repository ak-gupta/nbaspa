"""Define some metrics for evaluating the model."""

from lifelines import CoxTimeVaryingFitter
from lifelines.utils import concordance_index
import numpy as np
import pandas as pd
from prefect import Task

from .meta import META

class ConcordanceIndex(Task):
    """Calculate the C-index."""
    def run(
        self,
        model: CoxTimeVaryingFitter,
        data: pd.DataFrame
    ) -> float:
        """Calculate the C-index.

        For this calculation, we will truncate the input data to one row per
        game with the initial data.

        Parameters
        ----------
        model : CoxTimeVaryingFitter
            The fitted model.
        data : pd.DataFrame
            The test data.
        
        Returns
        -------
        float
            The Concordance index.
        """
        self.logger.info("Collapsing the data")
        shortform = data.groupby(META["id"]).head(n=1).copy()
        self.logger.info("Removing time-varying effects")
        for col in META["dynamic"]:
            shortform[col] = 0
        # Adding the final win indicator
        shortform.set_index(META["id"], inplace=True)
        shortform["WIN"] = data.groupby(META["id"])["WIN"].sum()

        cind = concordance_index(
            shortform["start"],
            -model.predict_partial_hazard(shortform),
            shortform[META["event"]]
        )
        self.logger.info(f"Model has a C-index of {np.round(cind, 3)}")

        return cind
