"""Define some metrics for evaluating the model."""

from typing import List, Optional

from lifelines.utils import concordance_index
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from prefect import Task
from sklearn.metrics import roc_auc_score
import seaborn as sns

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
        cind = concordance_index(
            data["stop"],
            -predt,
            data[META["event"]]
        )
        self.logger.info(f"Model has a C-index of {np.round(cind, 3)}")

        return cind


class AUROC(Task):
    """Calculate the AUROC score."""
    def run(self, data: pd.DataFrame) -> float:
        """Calculate the AUROC score.

        Parameters
        ----------
        data : pd.DataFrame
            The output of ``WinProbability.run()``.
        
        Returns
        -------
        float
            The AUROC score from ``scikit-learn``.
        """
        output = roc_auc_score(y_true=data[META["event"]], y_score=data[META["probability"]])
        self.logger.info(f"Model has a AUROC value of {np.round(output, 3)}")

        return output

class PlotMetric(Task):
    """Use seaborn to plot a metric over time."""
    def run(
        self,
        times: List[int],
        metric: str,
        **kwargs: List[float]
    ):
        """Use ``seaborn`` to plot a metric over time.

        Parameters
        ----------
        times : list
            The list of time steps for each metric sequence.
        metric : str
            The metric name.
        **kwargs
            Each model type to plot. The value is a list of float
            values repesenting the metric values.
        
        Returns
        -------
        """
        data = pd.concat(
            pd.DataFrame({"time": times, "value": value, "model": key})
            for key, value in kwargs.items()
        ).reset_index(drop=True)
        # Plot the line
        with sns.axes_style("dark"):
            fig, ax = plt.subplots(figsize=(10, 10))
            sns.lineplot(
                x="time",
                y="value",
                hue="model",
                data=data,
                ax=ax
            ).set(
                title=f"{metric} value over game-time",
                xlabel="Time",
                ylabel=metric
            )

        return fig
