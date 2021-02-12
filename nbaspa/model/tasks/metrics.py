"""Define some metrics for evaluating the model."""

from lifelines.utils import concordance_index
import numpy as np
import pandas as pd
from prefect import Task

from .meta import META

class ConcordanceIndex(Task):
    """Calculate the C-index."""
    def run(
        self,
        data: pd.DataFrame,
        predt: np.ndarray
    ) -> float:
        """Calculate the C-index.

        Parameters
        ----------
        data : pd.DataFrame
            The test data.
        predt : np.ndarray
            The output of ``CoxTimeVaryingFitter.predict_partial_hazard()`
        
        Returns
        -------
        float
            The Concordance index.
        """
        cind = concordance_index(
            data["start"],
            -predt,
            data[META["event"]]
        )
        self.logger.info(f"Model has a C-index of {np.round(cind, 3)}")

        return cind
