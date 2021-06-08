"""Tasks for model calibration."""

import numpy as np
import pandas as pd
from prefect import Task
from sklearn.isotonic import IsotonicRegression

from .meta import META


class CalibrateClassifier(Task):
    """Calibrate the classifier with ``IsotonicRegression``."""

    def run(self, train_data: pd.DataFrame) -> IsotonicRegression:  # type: ignore
        """Calibrate the classifier.

        Parameters
        ----------
        train_data : pd.DataFrame
            The training data with the additional ``SURV_PROB`` column.
        
        Returns
        -------
        IsotonicRegression
            The fitted calibrator.
        """
        iso = IsotonicRegression(y_min=0, y_max=1, out_of_bounds="clip")
        iso.fit(train_data[META["survival"]], train_data[META["event"]])

        return iso
