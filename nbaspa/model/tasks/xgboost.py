"""Tasks for XGBoost."""

from typing import Dict, Tuple

import jax
import jax.numpy as jnp
import numpy as np
import pandas as pd
from prefect import Task
import xgboost as xgb

from .meta import META

def _cox_obs_loglik(
    predt: jnp.ndarray,
    stop: jnp.ndarray,
    failuretime: jnp.ndarray
) -> float:
    """Get the cox partial log-likelihood for an observation.

    Parameters
    ----------
    predt : jnp.ndarray
        The predicted partial hazard value for each event.
    stop : jnp.ndarray
        The end (inclusive) for the covariate values within the subject.
    failuretime : int
        The index of the failure time in each array.
    
    Returns
    -------
    float
        The partial likelihood for each observation.
    """
    if predt[stop == stop[failuretime]].shape[0] > 0:
        return jnp.log(predt[failuretime]) - jnp.log(jnp.sum(predt[stop == stop[failuretime]]))
    else:
        return jnp.array([0], dtype=float)

# Define the gradient and hessian
_cox_obs_gradient = jax.grad(_cox_obs_loglik)
_cox_obs_hessian = jax.grad(_cox_obs_gradient)

def _cox_gradient(
    predt: jnp.ndarray,
    stop: jnp.ndarray,
    event: jnp.ndarray,
    group: jnp.ndarray,
    games: jnp.ndarray,
) -> np.ndarray:
    """Get the cox partial log-likelihood.

    This will produce an array with one entry per subject.
    
    Parameters
    ----------
    predt : jnp.ndarray
        The predicted partial hazard value for each event.
    stop : jnp.ndarray
        The end (inclusive) for the covariate values within the subject.
    event : jnp.ndarray
        A boolean column indicating whether or not the row is associated with an event.
    group : jnp.ndarray
        A categorical array indicating the subject
    games : jnp.ndarray
        The unique games
    
    Returns
    -------
    np.ndarray
        An array of the partial log likelihood values for each subject
    """
    # Get the failure times
    loglik = np.zeros(len(predt))
    # Loop through each subject and assign
    for subject in games:
        ftime = np.argwhere(group == subject)[-1][0]
        if event[ftime] == 0:
            continue
        loglik += np.array(_cox_obs_gradient(predt, stop=stop, failuretime=ftime))
    
    return loglik

def _cox_hessian(
    predt: jnp.ndarray,
    stop: jnp.ndarray,
    event: jnp.ndarray,
    group: jnp.ndarray,
    games: jnp.ndarray,
) -> np.ndarray:
    """Get the cox partial log-likelihood.

    This will produce an array with one entry per subject.
    
    Parameters
    ----------
    predt : jnp.ndarray
        The predicted partial hazard value for each event.
    stop : jnp.ndarray
        The end (inclusive) for the covariate values within the subject.
    event : jnp.ndarray
        A boolean column indicating whether or not the row is associated with an event.
    group : jnp.ndarray
        A categorical array indicating the subject
    games : jnp.ndarray
        The unique games
    
    Returns
    -------
    np.ndarray
        An array of the partial log likelihood values for each subject
    """
    # Get the failure times
    loglik = np.zeros(len(predt))
    # Loop through each subject and assign
    for subject in games:
        ftime = np.argwhere(group == subject)[-1][0]
        if event[ftime] == 0:
            continue
        loglik += np.array(_cox_obs_hessian(predt, stop=stop, failuretime=ftime))
    
    return loglik

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
        games = np.unique(group)

        # Define the objective function internally
        def objective(
            predt: np.ndarray, dtrain: xgb.DMatrix
        ) -> Tuple[np.ndarray, np.ndarray]:
            event = jnp.array(dtrain.get_label())
            stop = jnp.array(dtrain.get_float_info("label_upper_bound"))

            self.logger.info("Calculating the gradient...")
            gradient = _cox_gradient(
                predt=jnp.array(predt),
                stop=stop,
                event=event,
                group=group,
                games=games,
            )
            self.logger.info("Calculating the Hessian...")
            hess = _cox_hessian(
                predt=jnp.array(predt),
                stop=stop,
                event=event,
                group=group,
                games=games,
            )

            return gradient, hess
        
        # Define the metric to use for evaluation
        def nloglik(predt: np.ndarray, dtrain: xgb.DMatrix) -> Tuple[str, float]:
            event = dtrain.get_label()
            start = dtrain.get_float_info("label_lower_bound")
            stop = dtrain.get_float_info("label_upper_bound")

            self.logger.info("Calculating the partial log-likelihood...")

            return (
                "partial-nloglik",
                -np.sum(
                    _coxloglik(
                        predt=predt, start=start, stop=stop, event=event, group=group
                    )
                )
            )
        
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
            feval=nloglik,
            evals=[(dtrain, "train")],
            **kwargs
        )

        return model
