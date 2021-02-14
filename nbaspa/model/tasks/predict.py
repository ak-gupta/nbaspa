"""Create a task for getting the survival probability."""

from lifelines import CoxTimeVaryingFitter
from lifelines.utils import interpolate_at_times
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from prefect import Task
import seaborn as sns

from .meta import META


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
        data[META["probability"]] = 1 - np.exp(-(c0 * vals.values))

        return data


class PlotProbability(Task):
    """Plot the survival probability against the margin of the game."""
    def run(self, data: pd.DataFrame):
        """Plot the survival probability against the margin.

        Parameters
        ----------
        data : pd.DataFrame
            The output from ``SurvivalProbability.run()``.
        
        Returns
        -------
        """
        with sns.axes_style("dark"):
            fig, ax = plt.subplots(figsize=(10, 10))
            probplot = sns.scatterplot(
                x="SCOREMARGIN",
                y=META["probability"],
                hue=META["event"],
                data=data,
                legend=True,
                ax=ax
            )
            probplot.set(
                title=f"Survival probability versus game margin",
                xlabel="Margin (positive value means home team is winning)",
                ylabel="Survival Probability"
            )
            probplot.legend().set_title("Home team win")
        
        return fig
