"""Tasks for XGBoost."""

from typing import Dict, Tuple

import numpy as np
import pandas as pd
from prefect import Task
import xgboost as xgb

from .meta import META

def _ncox_loglik(
    predt: np.ndarray,
    label: np.ndarray,
    stop: np.ndarray,
    group: np.ndarray,
) -> np.ndarray:
    """Get the negative log-likelihood.

    Parameters
    ----------
    predt : np.ndarray
        The array of predicted values from the model.
    label : np.ndarray
        A boolean array of event labels.
    stop : np.ndarray
        A array of the right (inclusive) time range value for covariate values.
    group : np.ndarray
        The game indicator for each observation.
    
    Returns
    -------
    np.ndarray
        The observation-level negative log likelihood values.
    """
    # Get the unique games
    games = np.unique(group)
    # Get the array index for every failure time (last row with game value)
    ftimes = np.array(
        [np.argwhere(group == game)[-1][0] for game in games]
    )
    # Get the sum -- each entry in the array has to be the sum of exponentiated predicted
    # values for the game at the failure time.
    exp_sum = np.ones(len(predt))
    for index, ftime in enumerate(ftimes):
        # Get the predicted value at failure time
        exp_sum[index] = np.sum(np.exp(predt[stop == stop[ftime]]))
    
    return label * (predt - np.log(exp_sum))

def _ncox_gradient(
    predt: np.ndarray,
    label: np.ndarray,
    stop: np.ndarray,
    group: np.ndarray,
) -> np.ndarray:
    """Get the negative gradient.

    Parameters
    ----------
    predt : np.ndarray
        The array of predicted values from the model.
    label : np.ndarray
        A boolean array of event labels.
    stop : np.ndarray
        A array of the right (inclusive) time range value for covariate values.
    group : np.ndarray
        The game indicator for each observation.
    
    Returns
    -------
    np.ndarray
        The observation-level negative gradient values.
    """
    # Get the unique games
    games = np.unique(group)
    # Get the array index for every failure time (last row with game value)
    ftimes = np.array(
        [np.argwhere(group == game)[-1][0] for game in games]
    )
    # Get the sum -- each entry in the array has to be the sum of exponentiated predicted
    # values for the game at the failure time.
    exp_sum = np.ones(len(predt))
    for index, ftime in enumerate(ftimes):
        # Get the predicted value at failure time
        exp_sum[index] = np.sum(np.exp(predt[stop == stop[ftime]]))
    
    return label * ((np.exp(predt) / exp_sum) - 1)

def _ncox_hessian(
    predt: np.ndarray,
    label: np.ndarray,
    stop: np.ndarray,
    group: np.ndarray,
) -> np.ndarray:
    """Get the negative hessian.

    Parameters
    ----------
    predt : np.ndarray
        The array of predicted values from the model.
    label : np.ndarray
        A boolean array of event labels.
    stop : np.ndarray
        A array of the right (inclusive) time range value for covariate values.
    group : np.ndarray
        The game indicator for each observation.
    
    Returns
    -------
    np.ndarray
        The observation-level negative hessian values.
    """
    # Get the unique games
    games = np.unique(group)
    # Get the array index for every failure time (last row with game value)
    ftimes = np.array(
        [np.argwhere(group == game)[-1][0] for game in games]
    )
    # Get the sum -- each entry in the array has to be the sum of exponentiated predicted
    # values for the game at the failure time.
    exp_sum = np.ones(len(predt))
    for index, ftime in enumerate(ftimes):
        # Get the predicted value at failure time
        exp_sum[index] = np.sum(np.exp(predt[stop == stop[ftime]]))
    
    return (
        label * ((np.exp(predt) / exp_sum) - ((np.exp(predt) ** 2) / (exp_sum ** 2)))
    )

class FitXGBoost(Task):
    """Fit the XGBoost model."""
    def run(self, params: Dict, train_data: pd.DataFrame, **kwargs):
        """Fit the XGBoost model.

        This model will be fitted using a custom objective function.

        Parameters
        ----------
        params : dict
            The parameters for the model.
        train_data : pd.DataFrame
            The training data, from ``SurvivalData.run()``.
        **kwargs
            Keyword arguments for ``xgb.train``.
        
        Returns
        -------
        """
        # Get the game identifiers since they aren't easily defined in ``xgb.DMatrix``
        group = pd.get_dummies(train_data[META["id"]]).values.argmax(1)

        # Define a custom objective
        def objective(predt: np.ndarray, dtrain: xgb.DMatrix) -> np.ndarray:
            """Cox custom objective function."""
            label = dtrain.get_label()
            stop = dtrain.get_float_info("label_upper_bound")

            grad = _ncox_gradient(predt=predt, label=label, stop=stop, group=group)
            hess = _ncox_hessian(predt=predt, label=label, stop=stop, group=group)

            return grad, hess
        
        # Define the evaluation metric
        def eval_metric(predt: np.ndarray, dtrain: xgb.DMatrix) -> np.ndarray:
            """Cox custom evaluation metric."""
            label = dtrain.get_label()
            stop = dtrain.get_float_info("label_upper_bound")

            return "cox-nloglik", np.sum(_ncox_loglik(predt=predt, label=label, stop=stop, group=group))
        
        # Train the model
        params.update(
            {"disable_default_eval_metric": 1}
        )
        dtrain = xgb.DMatrix(
            train_data[META["static"] + META["dynamic"]], train_data[META["event"]]
        )
        dtrain.set_float_info("label_lower_bound", train_data["start"])
        dtrain.set_float_info("label_upper_bound", train_data["stop"])
        self.logger.info("Training the model...")
        model = xgb.train(
            params,
            dtrain,
            obj=objective,
            feval=eval_metric,
            evals=[(dtrain, "train")],
            **kwargs
        )

        return model
