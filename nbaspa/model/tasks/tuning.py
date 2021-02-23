"""Hyperparameter tuning tasks."""

from typing import Dict, Optional

from hyperopt import fmin, hp, STATUS_OK, tpe, Trials
from lifelines import CoxTimeVaryingFitter
from lifelines.utils import concordance_index
import numpy as np
import pandas as pd
from prefect import Task
import xgboost as xgb

from .meta import META

DEFAULT_LIFELINES_SPACE: Dict = {
    "penalizer": hp.uniform("penalizer", 0, 1),
    "l1_ratio": hp.uniform("l1_ratio", 0, 1),
}

DEFAULT_XGBOOST_SPACE: Dict = {
    "max_depth": hp.quniform("max_depth", 2, 20, 1),
    "gamma": hp.uniform("gamma", 1, 9),
    "reg_alpha": hp.quniform("reg_alpha", 40, 180, 1),
    "reg_lambda": hp.uniform("reg_lambda", 0, 1),
    "colsample_bytree": hp.uniform("colsample_bytree", 0.5, 1),
    "min_child_weight": hp.quniform("min_child_weight", 0, 10, 1),
}


class LifelinesTuning(Task):
    """Use ``hyperopt`` to choose ``lifelines`` hyperparameters."""

    def run(
        self,
        train_data: pd.DataFrame,
        tune_data: pd.DataFrame,
        param_space: Optional[Dict] = DEFAULT_LIFELINES_SPACE,
        max_evals: Optional[int] = 100,
        seed: Optional[int] = 42,
        **kwargs,
    ) -> Dict:
        """Hyperparameter tuning.

        Parameters
        ----------
        train_data : pd.DataFrame
            The training data.
        tune_data : pd.DataFrame
            Tuning data.
        param_space : Dict, optional (default DEFAULT_LIFELINES_SPACE)
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
                train_data[
                    [META["id"], META["event"]]
                    + ["start", "stop"]
                    + META["static"]
                    + META["dynamic"]
                ],
                id_col=META["id"],
                event_col=META["event"],
                start_col="start",
                stop_col="stop",
            )
            predt = model.predict_partial_hazard(tune_data)

            return {
                "loss": -concordance_index(
                    tune_data["stop"], -predt, tune_data[META["event"]]
                ),
                "status": STATUS_OK,
            }

        # Run the hyperparameter tuning
        trials = Trials()
        best = fmin(
            func,
            param_space,
            algo=tpe.suggest,
            max_evals=max_evals,
            trials=trials,
            rstate=np.random.RandomState(seed),
        )
        best = {**best, **kwargs}
        self.logger.info(
            f"The best model uses a ``penalizer`` value of {np.round(best['penalizer'], 3)} "
            f"and a ``l1_ratio`` value of {np.round(best['l1_ratio'], 3)}"
        )

        return {"best": best, "trials": trials}


class XGBoostTuning(Task):
    """Use ``hyperopt`` to choose ``xgboost`` hyperparameters."""

    def run(
        self,
        train_data: pd.DataFrame,
        tune_data: pd.DataFrame,
        param_space: Optional[Dict] = DEFAULT_XGBOOST_SPACE,
        stopping_data: Optional[pd.DataFrame] = None,
        max_evals: Optional[int] = 100,
        seed: Optional[int] = 42,
        **kwargs,
    ) -> Dict:
        """Hyper parameter tuning.

        Parameters
        ----------
        train_data : pd.DataFrame
            The training data.
        tune_data : pd.DataFrame
            Tuning data.
        param_space : dict, optional (default DEFAULT_XGBOOST_SPACE)
            The space for the hyperparameters.
        stopping_data : pd.DataFrame, optional (default None)
            Optional early stopping data for the model.
        max_evals : int, optional (default 100)
            The random seed for hyperparameter tuning.
        seed : int, optional (default 42)
            Any constant keyword arguments to pass to ``xgb.train``.

        Returns
        -------
        Dict
            A dictionary with two keys: ``best`` and ``trials``. Best contains the
            best hyperparameter value and trials has the ``hyperopt.Trials`` object.
        """
        # Convert training, tuning, and stopping data to the XGBoost format
        self.logger.info("Converting training data to ``xgb.DMatrix``")
        train = train_data.copy()
        train.loc[train[META["event"]] == 0, "stop"] = -train["stop"]
        dtrain = xgb.DMatrix(train[META["static"] + META["dynamic"]], train["stop"])
        evals = [
            (dtrain, "train"),
        ]
        if stopping_data is not None:
            self.logger.info("Converting stopping data to ``xgb.DMatrix``")
            stop = stopping_data.copy()
            stop.loc[stop[META["event"]] == 0, "stop"] = -stop["stop"]
            dstop = xgb.DMatrix(stop[META["static"] + META["dynamic"]], stop["stop"])
            evals.append((dstop, "stopping"))

        tune = tune_data.copy()
        tune.loc[tune[META["event"]] == 0, "stop"] = -tune["stop"]
        dtune = xgb.DMatrix(tune[META["static"] + META["dynamic"]], tune["stop"])

        # Create an internal function for fitting, trainin, evaluating
        def func(params):
            model = xgb.train(
                {
                    "max_depth": int(params["max_depth"]),
                    "gamma": params["gamma"],
                    "reg_alpha": int(params["reg_alpha"]),
                    "reg_lambda": params["reg_lambda"],
                    "colsample_bytree": params["colsample_bytree"],
                    "min_child_weight": int(params["min_child_weight"]),
                    "objective": "survival:cox",
                },
                dtrain,
                evals=evals,
                **kwargs,
            )
            predt = model.predict(dtune)

            return {
                "loss": -concordance_index(
                    tune_data["stop"], -predt, tune_data[META["event"]]
                ),
                "status": STATUS_OK,
            }

        # Run the hyperparameter tuning
        trials = Trials()
        best = fmin(
            func,
            param_space,
            algo=tpe.suggest,
            max_evals=max_evals,
            trials=trials,
            rstate=np.random.RandomState(seed),
        )
        for param in ["max_depth", "reg_alpha", "min_child_weight"]:
            best[param] = int(best[param])

        return {"best": best, "trials": trials}
