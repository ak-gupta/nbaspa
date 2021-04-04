"""Hyperparameter tuning tasks."""

from pprint import pformat
from typing import Dict, List, Optional

from hyperopt import fmin, hp, STATUS_OK, atpe, Trials
from lifelines import CoxTimeVaryingFitter
from lifelines.utils import interpolate_at_times
import numpy as np
import pandas as pd
from prefect import Task
from sklearn.metrics import roc_auc_score
import xgboost as xgb

from .meta import META
from .xgboost import _generate_cumulative_hazard

DEFAULT_LIFELINES_SPACE: Dict = {
    "penalizer": hp.uniform("penalizer", 0, 1),
    "l1_ratio": hp.uniform("l1_ratio", 0, 1),
}

DEFAULT_XGBOOST_SPACE: Dict = {
    "learning_rate": hp.uniform("learning_rate", 0.000001, 0.01),
    "subsample": hp.uniform("subsample", 0.3, 0.5),
    "max_delta_step": hp.uniform("max_delta_step", 8, 10),
    "max_depth": hp.quniform("max_depth", 2, 10, 1),
    "gamma": hp.uniform("gamma", 12, 14),
    "reg_alpha": hp.uniform("reg_alpha", 0, 1),
    "reg_lambda": hp.uniform("reg_lambda", 0, 1),
    "colsample_bytree": hp.uniform("colsample_bytree", 0.001, 0.1),
    "colsample_bylevel": hp.uniform("colsample_bylevel", 0.5, 0.9),
    "colsample_bynode": hp.uniform("colsample_bynode", 0.001, 0.1),
    "min_child_weight": hp.quniform("min_child_weight", 0, 10, 1),
    "early_stopping_rounds": hp.quniform("early_stopping_rounds", 1, 25, 2),
}


class LifelinesTuning(Task):
    """Use ``hyperopt`` to choose ``lifelines`` hyperparameters."""

    best_: Dict = {}
    metric_: float = 1e20

    def run(  # type: ignore
        self,
        train_data: pd.DataFrame,
        tune_data: List[pd.DataFrame],
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
        tune_data : List[pd.DataFrame]
            A list of tuning dataframes at various timestamps.
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
            metric: List[float] = []
            for dataset in tune_data:
                predt = model.predict_partial_hazard(dataset)
                c0 = interpolate_at_times(
                    model.baseline_cumulative_hazard_, dataset["stop"].values
                )
                metric.append(
                    roc_auc_score(
                        y_true=dataset[META["event"]],
                        y_score=1 - np.exp(-(c0 * predt.values)),
                    )
                )
            metric = -np.average(np.array(metric))

            if metric < self.metric_:
                self.metric_ = metric
                self.best_.update(params)
                self.logger.info(
                    f"New best metric value of {self.metric_} with \n\n{pformat(self.best_)}\n"
                )

            return {
                "loss": metric,
                "status": STATUS_OK,
            }

        # Run the hyperparameter tuning
        trials = Trials()
        try:
            fmin(
                func,
                param_space,
                algo=atpe.suggest,
                max_evals=max_evals,
                trials=trials,
                rstate=np.random.RandomState(seed),
            )
        except KeyboardInterrupt:
            self.logger.warning("Interrupted... Returning current results.")
        finally:
            best = {**self.best_, **kwargs}
            self.logger.info(
                f"The best model has the following parameter values:\n\n{pformat(best)}\n"
            )

        return {"best": best, "trials": trials}


class XGBoostTuning(Task):
    """Use ``hyperopt`` to choose ``xgboost`` hyperparameters."""

    best_: Dict = {}
    metric_: float = 1e20

    def run(  # type: ignore
        self,
        train_data: pd.DataFrame,
        tune_data: List[pd.DataFrame],
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
        tune_data : List[pd.DataFrame]
            A list of tuning dataframes at various timestamps.
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

        evals = [(dtrain, "train")]

        if stopping_data is not None:
            self.logger.info("Converting stopping data to ``xgb.DMatrix``")
            stop = stopping_data.copy()
            stop.loc[stop[META["event"]] == 0, "stop"] = -stop["stop"]
            dstop = xgb.DMatrix(stop[META["static"] + META["dynamic"]], stop["stop"])
            evals.append((dstop, "stopping"))

        # Create an internal function for fitting, trainin, evaluating
        def func(params):
            # Train the model
            model = xgb.train(
                {
                    "learning_rate": params["learning_rate"],
                    "subsample": params["subsample"],
                    "max_delta_step": params["max_delta_step"],
                    "max_depth": int(params["max_depth"]),
                    "gamma": params["gamma"],
                    "reg_alpha": params["reg_alpha"],
                    "reg_lambda": params["reg_lambda"],
                    "colsample_bytree": params["colsample_bytree"],
                    "colsample_bylevel": params["colsample_bylevel"],
                    "colsample_bynode": params["colsample_bynode"],
                    "min_child_weight": int(params["min_child_weight"]),
                    "objective": "survival:cox",
                },
                dtrain,
                evals=evals,
                verbose_eval=False,
                early_stopping_rounds=int(params["early_stopping_rounds"]),
                **kwargs,
            )
            cumulative_hazard_ = _generate_cumulative_hazard(
                model=model, train_data=train_data, dtrain=dtrain
            )
            metric: List[float] = []
            for dataset in tune_data:
                tuning = dataset.copy()
                tuning.loc[tuning[META["event"]] == 0, "stop"] = -tuning["stop"]
                dtune = xgb.DMatrix(
                    tuning[META["static"] + META["dynamic"]], tuning["stop"]
                )

                predt = model.predict(dtune)
                c0 = interpolate_at_times(cumulative_hazard_, dataset["stop"].values)
                metric.append(
                    roc_auc_score(
                        y_true=tuning[META["event"]].values, y_score=1 - np.exp(-(c0 * predt))
                    )
                )

            metric = -np.average(np.array(metric))

            if metric < self.metric_:
                self.metric_ = metric
                self.best_.update(params)
                self.logger.info(
                    f"New best metric value of {self.metric_} with \n\n{pformat(self.best_)}\n"
                )

            return {
                "loss": metric,
                "status": STATUS_OK,
            }

        # Run the hyperparameter tuning
        trials = Trials()
        try:
            fmin(
                func,
                param_space,
                algo=atpe.suggest,
                max_evals=max_evals,
                trials=trials,
                rstate=np.random.RandomState(seed),
            )
        except KeyboardInterrupt:
            self.logger.warning("Interrupted... Returning current results.")
        finally:
            for param in [
                "max_depth",
                "min_child_weight",
                "early_stopping_rounds",
            ]:
                self.best_[param] = int(self.best_[param])
            self.logger.info(
                f"The best model has the following parameter values:\n\n{pformat(self.best_)}\n"
            )

        return {"best": self.best_, "trials": trials}
