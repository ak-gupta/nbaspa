"""Lifelines training and prediction tasks."""

from typing import Dict, Optional

from hyperopt import fmin, hp, STATUS_OK, tpe, Trials
from lifelines import CoxTimeVaryingFitter
from lifelines.utils import concordance_index
import numpy as np
import pandas as pd
from prefect import Task

from .meta import META

DEFAULT_PARAM_SPACE: Dict = {
    "penalizer": hp.uniform("penalizer", 0, 1),
    "l1_ratio": hp.uniform("l1_ratio", 0, 1)
}

class InitializeLifelines(Task):
    """Initialize a new ``lifelines`` model."""
    def run(self, params: Optional[Dict] = None) -> CoxTimeVaryingFitter:
        """Initialize a new ``lifelines`` model.

        Parameters
        ----------
        params : dict, optional (default None)
            Keyword arguments for ``CoxTimeVaryingFitter``
        
        Returns
        -------
        CoxTimeVaryingFitter
            The initialized model.
        """
        return CoxTimeVaryingFitter(**params or {})


class FitLifelinesModel(Task):
    """Fit the lifelines model."""
    def run(
        self,
        model: CoxTimeVaryingFitter,
        data: pd.DataFrame,
        **kwargs
    ) -> CoxTimeVaryingFitter:
        """Fit the lifelines model.

        Parameters
        ----------
        model : CoxTimeVaryingFitter
            The initialized model.
        data : pd.DataFrame
            The ``lifelines`` format data.
        **kwargs
            Keyword arguments for the ``fit`` method.
        
        Returns
        -------
        CoxTimeVaryingFitter
            The fitted model.
        """
        model = model.fit(
            data,
            id_col=META["id"],
            event_col=META["event"],
            start_col="start",
            stop_col="stop",
            show_progress=True,
            **kwargs
        )
        model.print_summary()

        return model


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


class HyperparameterTuning(Task):
    """Use ``hyperopt`` to choose ``lifelines`` hyperparameters."""
    def run(
        self,
        train_data: pd.DataFrame,
        tune_data: pd.DataFrame,
        param_space: Dict = DEFAULT_PARAM_SPACE,
        max_evals: Optional[int] = 100,
    ) -> Dict:
        """Hyperparameter tuning.

        Parameters
        ----------
        train_data : pd.DataFrame
            The training data.
        tune_data : pd.DataFrame
            Tuning data, generated using ``CollapseData``.
        param_space : Dict, optional (default DEFAULT_PARAM_SPACE)
            The space for the hyperparameters
        max_exals : int, optional (default 100)
            The number of evaluations for hyperparameter tuning.
        
        Returns
        -------
        Dict
            A dictionary with two keys: ``best`` and ``trials``. Best contains the
            best hyperparameter value and trials has the ``hyperopt.Trials`` object.
        """
        # Create an internal function for fitting, training, evaluating
        def func(params):
            model = CoxTimeVaryingFitter(**params)
            model.fit(
                train_data,
                id_col=META["id"],
                event_col=META["event"],
                start_col="start",
                stop_col="stop",
                show_progress=True,
            )
            predt = model.predict_partial_hazard(tune_data)

            return {
                "loss": -concordance_index(
                    tune_data["start"],
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
        self.logger.info(
            f"The best model uses a ``penalizer`` value of {np.round(best['penalizer'], 3)} "
            f"and a ``l1_ratio`` value of {np.round(best['l1_ratio'], 3)}"
        )

        return {"best": best, "trials": trials}
