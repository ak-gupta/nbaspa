"""Tasks for model calibration."""

from typing import Union, List

import pandas as pd
from prefect import Task
from sklearn.isotonic import IsotonicRegression

from .meta import META


class CalibrateClassifier(Task):
    """Calibrate the classifier with ``IsotonicRegression``."""

    def run(  # type: ignore
        self, train_data: Union[List[pd.DataFrame], pd.DataFrame]
    ) -> IsotonicRegression:
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
        if isinstance(train_data, list):
            train_data = pd.concat(train_data, ignore_index=True)
        iso = IsotonicRegression(y_min=0, y_max=1, out_of_bounds="clip")
        iso.fit(train_data[META["survival"]], train_data[META["event"]])

        return iso


class CalibrateProbability(Task):
    """Calibrate the output probabilities from a model."""

    def run(  # type: ignore
        self, data: pd.DataFrame, calibrator: IsotonicRegression
    ) -> pd.DataFrame:
        """Calibrate the output probabilities from a model.

        Parameters
        ----------
        data : pd.DataFrame
            The data with the raw output probabilities.
        calibrator : IsotonicRegression
            The fitted calibrator.

        Returns
        -------
        pd.DataFrame
            The original data with modified probabilities.
        """
        data[META["survival"]] = calibrator.predict(data[META["survival"]])

        return data
