"""Create simple visualizations."""

from typing import List, Optional

from hyperopt import Trials
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from prefect import Task
import seaborn as sns
import shap
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression

from .meta import META


class PlotProbability(Task):
    """Plot the survival probability against the margin of the game."""

    def run(self, data: pd.DataFrame, mode: Optional[str] = "survival"):  # type: ignore
        """Plot the survival probability against the margin.

        Parameters
        ----------
        data : pd.DataFrame
            The output from ``SurvivalProbability.run()``.
        mode : str, optional (default "survival")
            The mode, either ``survival`` or ``benchmark``

        Returns
        -------
        Figure
            The matplotlib figure object.
        """
        with sns.axes_style("darkgrid"):
            fig, ax = plt.subplots(figsize=(10, 10))
            probplot = sns.scatterplot(
                x="SCOREMARGIN",
                y=META[mode],
                hue=META["event"],
                data=data,
                legend=True,
                ax=ax,
            )
            probplot.set(
                title="Survival probability versus game margin",
                xlabel="Margin (positive value means home team is winning)",
                ylabel="Survival Probability",
            )
            probplot.legend().set_title("Home team win")

        return fig


class PlotMetric(Task):
    """Use seaborn to plot a metric over time."""

    def run(  # type: ignore
        self,
        times: List[int],
        metric: str,
        percentage: Optional[bool] = False,
        **kwargs: List[float]
    ):
        """Use ``seaborn`` to plot a metric over time.

        Parameters
        ----------
        times : list
            The list of time steps for each metric sequence.
        metric : str
            The metric name.
        percentage : bool, optional (default False)
            Whether or not the metric is a percentage.
        **kwargs
            Each model type to plot. The value is a list of float
            values repesenting the metric values.

        Returns
        -------
        Figure
            The matplotlib figure object.
        """
        data = pd.concat(
            pd.DataFrame({"time": times, "value": value, "model": key})
            for key, value in kwargs.items()
        ).reset_index(drop=True)
        # Plot the line
        with sns.axes_style("darkgrid"):
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.lineplot(x="time", y="value", hue="model", data=data, ax=ax).set(
                title=f"{metric} value over game-time", xlabel="Time", ylabel=metric
            )
            if percentage:
                ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))

        return fig


class PlotTuning(Task):
    """Create ``matplotlib`` plots to visualize hyperparameter tuning."""

    def run(self, trials: Trials):  # type: ignore
        """Create ``matplotlib`` plots to visualize hyperparameter tuning.

        Parameters
        ----------
        trials : Trials
            The ``hyperopt.Trials`` object.

        Returns
        -------
        Figure
            The matplotlib figure object.
        """
        # Get the parameters
        params = set(trials.trials[0]["misc"]["vals"].keys())
        # Parse trials object
        data = {
            "trial": [
                trial["tid"]
                for trial in trials.trials
                if "loss" in trial.get("result", {})
            ],
            "loss": [
                trial["result"]["loss"]
                for trial in trials.trials
                if "loss" in trial.get("result", {})
            ],
        }
        for param in params:
            data[param] = [
                trial["misc"]["vals"][param][0]
                for trial in trials.trials
                if "loss" in trial.get("result", {})
            ]

        df = pd.DataFrame(data)
        df["best"] = False
        df.loc[df["loss"] == df["loss"].min(), "best"] = True

        # Create the plotting object
        fig = plt.figure(figsize=(18, 12))
        # Create a grid
        numplots = len(params) + 1
        gridsize = (int(np.ceil(np.sqrt(numplots))), int(np.ceil(np.sqrt(numplots))))
        gs = fig.add_gridspec(*gridsize)
        with sns.axes_style("darkgrid"):
            ax = fig.add_subplot(gs[0, 0])
            sns.scatterplot(
                x="trial", y="loss", hue="best", legend=False, data=df, ax=ax
            )
            # Create an index array
            idxarray = np.arange(gridsize[0] * gridsize[1])
            idxarray = idxarray.reshape(*gridsize)
            for idx, param in enumerate(params):
                # Get the matrix location in the index array
                rowidx, colidx = np.argwhere(idxarray == idx + 1)[0]
                ax = fig.add_subplot(gs[rowidx, colidx])
                sns.scatterplot(
                    x=param, y="loss", hue="best", legend=False, data=df, ax=ax
                )
        fig.tight_layout()

        return fig

class PlotShapSummary(Task):
    """Plot the SHAP Values for a model."""

    def run(self, shap_values: List):  # type: ignore
        """Create a summary plot for the SHAP values.

        Parameters
        ----------
        shap_values : List
            The SHAP values.
        
        Returns
        -------
        Figure
            The matplotlib Figure object.
        """
        shap.plots.beeswarm(
            shap_values, show=False, log_scale=True
        )
        fig = plt.gcf()

        return fig


class PlotCalibration(Task):
    """Create a calibration plot."""

    def run(  # type: ignore
        self,
        data: pd.DataFrame,
        calibrator: IsotonicRegression,
    ):
        """Create a calibration curve.

        Parameters
        ----------
        data : pd.DataFrame
            The data with the additional ``SURV_PROB`` column.
        calibrator : IsotonicRegression
            The fitted calibrator object.
        
        Returns
        -------
        Figure
            The matplotlib Figure object.
        """
        # Get the calibration curve for the raw model
        uncal_x, uncal_y = calibration_curve(data[META["event"]], data[META["survival"]], n_bins=10)
        # Calibrated data
        cal_x, cal_y = calibration_curve(
            data[META["event"]],
            calibrator.predict(data[META["survival"]]),
            n_bins=10
        )
        # Create the plot
        udf = pd.DataFrame(
            {
                "x": uncal_x, "y": uncal_y, "Model": "Uncalibrated"
            }
        )
        cdf = pd.DataFrame(
            {
                "x": cal_x, "y": cal_y, "Model": "Calibrated"
            }
        )
        plotting_data = pd.concat([udf, cdf])
        with sns.axes_style("darkgrid"):
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.lineplot(
                x="x",
                y="y",
                hue="Model",
                data=plotting_data,
                ax=ax
            ).set(
                title="Calibration Curve",
                xlabel="Predicted Probability",
                ylabel="True Probability"
            )
        
        return fig
