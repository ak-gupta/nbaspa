"""Hyperparameter tuning tasks."""

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

class LifelinesTuning(Task):
    """Use ``hyperopt`` to choose ``lifelines`` hyperparameters."""
    def run(
        self,
        train_data: pd.DataFrame,
        tune_data: pd.DataFrame,
        param_space: Dict = DEFAULT_PARAM_SPACE,
        max_evals: Optional[int] = 100,
        seed: Optional[int] = 42,
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
        seed : int, optional (default 42)
            The random seed for hyperparameter tuning.
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
            trials=trials,
            rstate=np.random.RandomState(42)
        )
        best = {**best, **kwargs}
        self.logger.info(
            f"The best model uses a ``penalizer`` value of {np.round(best['penalizer'], 3)} "
            f"and a ``l1_ratio`` value of {np.round(best['l1_ratio'], 3)}"
        )

        return {"best": best, "trials": trials}
