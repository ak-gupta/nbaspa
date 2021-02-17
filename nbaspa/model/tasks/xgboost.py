"""Tasks for XGBoost."""

import logging
from typing import Dict, Tuple

import jax
import jax.numpy as jnp
import numpy as np
import pandas as pd
from prefect import Task
import xgboost as xgb

from .meta import META

LOG = logging.getLogger(__name__)

def _coxloglik(
    predt: jnp.ndarray,
    start: jnp.ndarray,
    stop: jnp.ndarray,
    event: jnp.ndarray,
    group: jnp.ndarray
) -> np.ndarray:
    """Get the cox partial log-likelihood.

    This will produce an array with one entry per subject.
    
    Parameters
    ----------
    predt : jnp.ndarray
        The predicted partial hazard value for each event.
    start : jnp.ndarray
        The start (exclusive) for the covariate values within the subject.
    stop : jnp.ndarray
        The end (inclusive) for the covariate values within the subject.
    event : jnp.ndarray
        A boolean column indicating whether or not the row is associated with an event.
    group : jnp.ndarray
        A categorical array indicating the subject
    
    Returns
    -------
    np.ndarray
        An array of the partial log likelihood values for each subject
    """
    LOG.info("Calculating the partial likelihood...")
    subjects = jnp.unique(group)
    # Get the failure times
    failuretimes = jnp.array(
        [jnp.argwhere(group == subject)[-1][0] for subject in subjects]
    )
    loglik = jnp.zeros(len(subjects))
    # Loop through each subject and assign
    counter = 0
    for index in range(len(subjects)):
        # Keep the partial log likelihood at 0 for censored subjects
        if event[failuretimes[index]] == 0:
            counter += 1
            continue
        # Get the log likelihood
        ftime_predt: float = 0
        for subindex in range(len(subjects)):
            if stop[failuretimes[subindex]] < stop[failuretimes[index]]:
                continue
            # Get the min time
            predt_idx = jnp.argwhere(
                (start > failuretimes[index]) & (group == subjects[subindex])
            )[0][0]
            ftime_predt += predt[predt_idx]
        
        jax.ops.index_update(
            loglik,
            counter,
            jnp.log(predt[failuretimes[index]]) - jnp.log(ftime_predt)
        )

        counter += 1
    
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
        # Define the gradient and hessian
        self.logger.info("Using ``jax`` to get the gradient and hessian...")
        gradfunc = jax.grad(_coxloglik)
        hessfunc = jax.grad(gradfunc)

        # Define the objective function internally
        def objective(
            predt: np.ndarray, dtrain: xgb.DMatrix
        ) -> Tuple[np.ndarray, np.ndarray]:
            event = jnp.array(dtrain.get_label())
            start = jnp.array(dtrain.get_float_info("label_lower_bound"))
            stop = jnp.array(dtrain.get_float_info("label_upper_bound"))

            gradient = gradfunc(
                jnp.array(predt), start=start, stop=stop, event=event, group=jnp.array(group)
            )
            hess = hessfunc(
                jnp.array(predt), start=start, stop=stop, event=event, group=jnp.array(group)
            )

            return gradient, hess
        
        # Define the metric to use for evaluation
        def nloglik(predt: np.ndarray, dtrain: xgb.DMatrix) -> Tuple[str, float]:
            event = dtrain.get_label()
            start = dtrain.get_float_info("label_lower_bound")
            stop = dtrain.get_float_info("label_upper_bound") 

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
