"""Create simple visualizations."""

from typing import List, Optional

from hyperopt import Trials
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from prefect import Task
import seaborn as sns

from .meta import META

class PlotProbability(Task):
    """Plot the survival probability against the margin of the game."""
    def run(self, data: pd.DataFrame, mode: Optional[str] = "survival"):
        """Plot the survival probability against the margin.

        Parameters
        ----------
        data : pd.DataFrame
            The output from ``SurvivalProbability.run()``.
        mode : str, optional (default "survival")
            The mode, either ``survival`` or ``benchmark``

        Returns
        -------
        """
        with sns.axes_style("dark"):
            fig, ax = plt.subplots(figsize=(10, 10))
            probplot = sns.scatterplot(
                x="SCOREMARGIN",
                y=META[mode],
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


class PlotTuning(Task):
    """Create ``matplotlib`` plots to visualize hyperparameter tuning."""
    def run(self, trials: Trials):
        """Create ``matplotlib`` plots to visualize hyperparameter tuning.

        Parameters
        ----------
        trials : Trials
            The ``hyperopt.Trials`` object.
        
        Returns
        -------
        """
        # Get the parameters
        params = set(trials.trials[0]["misc"]["vals"].keys())
        # Parse trials object
        data = {
            "trial": [trial["tid"] for trial in trials.trials],
            "loss": [trial["result"]["loss"] for trial in trials.trials]
        }
        for param in params:
            data[param] = [trial["misc"]["vals"][param][0] for trial in trials.trials]
        
        df = pd.DataFrame(data)
        df["best"] = False
        df.loc[df["loss"] == df["loss"].min(), "best"] = True
        
        # Create the plotting object
        fig = plt.figure(figsize=(10, 10))
        gridsize = int(np.ceil(np.sqrt(len(params))))
        gs = fig.add_gridspec(gridsize, gridsize)
        with sns.axes_style("dark"):
            ax = fig.add_subplot(gs[0, 0])
            sns.scatterplot(x="trial", y="loss", hue="best", legend=False, data=df, ax=ax)
            for idx, param in enumerate(params):
                if idx < gridsize - 1:
                    rowidx = 0
                else:
                    rowidx = idx % gridsize
                ax = fig.add_subplot(gs[rowidx, (idx + 1) % gridsize])
                sns.scatterplot(x="trial", y=param, hue="best", legend=False, data=df, ax=ax)
        fig.tight_layout()

        return fig