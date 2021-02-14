"""Hyperparameter tuning tasks."""

from typing import Dict, Optional

from hyperopt import fmin, hp, STATUS_OK, tpe, Trials
from lifelines import CoxTimeVaryingFitter
from lifelines.utils import concordance_index
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from prefect import Task
import seaborn as sns

from .meta import META

DEFAULT_PARAM_SPACE: Dict = {
    "penalizer": hp.uniform("penalizer", 0, 1),
    "l1_ratio": hp.uniform("l1_ratio", 0, 1)
}

class LifelinesTuning(Task):
    """Use ``hyperopt`` to choose ``lifelines`` hyperparameters."""
    def run(
        self,
        train_data: pd.DataFrame,
        tune_data: pd.DataFrame,
        param_space: Dict = DEFAULT_PARAM_SPACE,
        max_evals: Optional[int] = 100,
        **kwargs
    ) -> Dict:
        """Hyperparameter tuning.

        Parameters
        ----------
        train_data : pd.DataFrame
            The training data.
        tune_data : pd.DataFrame
            Tuning data.
        param_space : Dict, optional (default DEFAULT_PARAM_SPACE)
            The space for the hyperparameters
        max_exals : int, optional (default 100)
            The number of evaluations for hyperparameter tuning.
        **kwargs
            Any constant keyword arguments to pass to the ``CoxTimeVaryingFitter``
            initialization
        
        Returns
        -------
        Dict
            A dictionary with two keys: ``best`` and ``trials``. Best contains the
            best hyperparameter value and trials has the ``hyperopt.Trials`` object.
        """
        # Create an internal function for fitting, training, evaluating
        def func(params):
            model = CoxTimeVaryingFitter(**params, **kwargs)
            model.fit(
                train_data,
                id_col=META["id"],
                event_col=META["event"],
                start_col="start",
                stop_col="stop",
            )
            predt = model.predict_partial_hazard(tune_data)

            return {
                "loss": -concordance_index(
                    tune_data["stop"],
                    -predt,
                    tune_data[META["event"]]
                ),
                "status": STATUS_OK
            }
        
        # Run the hyperparameter tuning
        trials = Trials()
        best = fmin(
            func,
            param_space,
            algo=tpe.suggest,
            max_evals=max_evals,
            trials=trials
        )
        best = {**best, **kwargs}
        self.logger.info(
            f"The best model uses a ``penalizer`` value of {np.round(best['penalizer'], 3)} "
            f"and a ``l1_ratio`` value of {np.round(best['l1_ratio'], 3)}"
        )

        return {"best": best, "trials": trials}


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
