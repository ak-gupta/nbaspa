"""Define some metrics for evaluating the model."""

from typing import List, Optional, Union

from lifelines.utils import concordance_index
import numpy as np
import pandas as pd
from prefect import Task
from sklearn.metrics import roc_auc_score

from .meta import META


class ConcordanceIndex(Task):
    """Calculate the C-index."""

    def run(
        self,
        data: pd.DataFrame,
        predt: np.ndarray,
    ) -> float:
        """Calculate the C-index.

        Parameters
        ----------
        data : pd.DataFrame
            The test data.
        predt : np.ndarray
            The partial hazard prediction.

        Returns
        -------
        float
            The Concordance index.
        """
        cind = concordance_index(data["stop"], -predt, data[META["event"]])
        self.logger.info(f"Model has a C-index of {np.round(cind, 3)}")

        return cind


class AUROC(Task):
    """Calculate the AUROC score."""

    def run(self, data: pd.DataFrame, mode: Optional[str] = "survival") -> float:
        """Calculate the AUROC score.

        Parameters
        ----------
        data : pd.DataFrame
            The output of ``WinProbability.run()``.
        mode : str, optional (default "survival")
            The mode, either ``survival`` or ``benchmark``

        Returns
        -------
        float
            The AUROC score from ``scikit-learn``.
        """
        output = roc_auc_score(y_true=data[META["event"]], y_score=data[META[mode]])
        self.logger.info(f"Model has a AUROC value of {np.round(output, 3)}")

        return output


class AUROCLift(Task):
    """Calculate the lift in AUROC between two sequences."""
    def run(
        self,
        benchmark: Union[List[float], np.ndarray],
        test: Union[List[float], np.ndarray]
    ) -> np.ndarray:
        """Calculate the lift in AUROC between two sequences.

        For our purposes, we will be calculating the AUROC across the entire game. This
        task will help produce a series comparing the survival model to the benchmark NBA
        win probability model.

        Parameters
        ----------
        benchmark : np.ndarray
            The benchmark series.
        test : np.ndarray
            The test series.
        
        Returns
        -------
        np.ndarray
            The output lift series.
        """
        if isinstance(test, list):
            test = np.array(test)
        if isinstance(benchmark, list):
            benchmark = np.array(benchmark)

        return test - benchmark
