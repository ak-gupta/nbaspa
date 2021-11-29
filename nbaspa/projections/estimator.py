"""BayesianTargetEstimator.

Meta-estimator that creates multiple models through sampling.
"""

from typing import List, Union

from alive_progress import alive_bar
import numpy as np
import pandas as pd
from pandas.api.types import is_categorical_dtype
from sklearn.base import BaseEstimator, MetaEstimatorMixin, clone
from sklearn.utils.metaestimators import available_if
from sklearn.utils.validation import check_array, check_is_fitted

from .encoder import BayesianTargetEncoder


def _estimator_has(attr):
    """Check if we can delegate a method to the underlying estimators."""
    def check(self):
        if hasattr(self, "estimators_"):
            getattr(self.estimators_[0], attr)

            return True
        
        getattr(self.estimators_[0], attr)

        return True
    
    return check

class BayesianTargetEstimator(MetaEstimatorMixin, BaseEstimator):
    """Encode and estimate using a bayesian target encoder.
    
    Parameters
    ----------
    estimator : estimator object
        This is assumed to implement the scikit-learn estimator interface.
    dist : {"bernoulli", "exponential", "gamma", "invgamma"}
        The likelihood for the target.
    samples : int, optional (default 10)
        The number of times to sample. Each sample will create a new copy of
        the underlying dataset.
    
    Attributes
    ----------
    estimators_ : list
        A list ``samples`` long with the submodels trained on each sample.
    encoder_ : estimator object
        The ``BayesianTargetEncoder`` used to encode all samples.
    """

    _required_parameters = ["estimator", "dist"]

    def __init__(self, estimator, dist: str, samples: int = 10):
        """Init method."""
        self.estimator = estimator
        self.dist = dist
        self.samples = samples
    

    def fit(
        self,
        X,
        y,
        feature_name: Union[str, List[str]] = "auto",
        categorical_feature: Union[List[Union[int, str]], str] = "auto",
        **fit_params
    ):
        """Fit the estimator.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data to determine the categories of each feature and the posterior
            distributions.
        y : array-like of shape (n_samples,) or (n_samples, n_targets)
            Target values. Will be cast to X's dtype if necessary.
        feature_name : list or str, optional (default "auto")
            Feature names. If "auto" and data is a pandas DataFrame, data column
            names are used.
        categorical_feature : list or str, optional (default "auto")
            Categorical features. If a list of int, it will be interpreted as indices.
            If a list of string, it will be interpreted as feature names (this requires
            ``feature_name``). If "auto" and data is pandas DataFrame, any columns using
            the ``pd.Categorical`` dtype will be used.
        **fit_params
            Parameters to be passed to the underlying estimator.
        
        Returns
        -------
        self
            The trained estimator.
        """
        # Get the categorical columns
        if feature_name == "auto":
            if not isinstance(X, pd.DataFrame):
                raise ValueError(
                    "If using ``feature_name == 'auto'``, please supply a pandas DataFrame"
                )
            else:
                feature_name = X.columns
        if categorical_feature == "auto":
            # Get all categoricals
            self.categorical_features_ = [
                index for index, col in enumerate(feature_name) if is_categorical_dtype(X[col])
            ]
        elif isinstance(categorical_feature[0], str):
            self.categorical_features_ = [
                index for index, col in enumerate(feature_name) if col in categorical_feature
            ]
        else:
            self.categorical_features_ = categorical_feature
        
        X, y = self._validate_data(X, y, dtype=None)

        # Fit the encoder
        self.encoder_ = BayesianTargetEncoder(dist=self.dist, sample=True)
        self.encoder_.fit(X[:, self.categorical_features_], y)
        # Loop and fit models on the samples
        self.estimators_ = []
        with alive_bar(self.samples) as bar:
            for _ in range(self.samples):
                # Generate a sample
                X_sample = X.copy()
                X_encoded = self.encoder_.transform(X_sample[:, self.categorical_features_])
                for idx, col in enumerate(self.categorical_features_):
                    X_sample[:, col] = X_encoded[:, idx]
                # Fit
                estimator = clone(self.estimator)
                estimator.fit(X_sample, y, **fit_params)
                self.estimators_.append(estimator)

                bar()

        return self


    @available_if(_estimator_has("predict"))
    def predict(self, X) -> np.ndarray:
        """Call predict on the estimators.
        
        The output of this function is the average prediction from all submodels.
        
        Parameters
        ----------
        X : indexable, length n_samples
            Must fulfill the input assumptions of the encoder.
        
        Returns
        -------
        np.ndarray of shape (n_samples,)
            The predicted labels or values for ``X`` based on the average from each
            submodel.
        """
        check_is_fitted(self)
        # Clone the encoder and set sample to False
        encoder = clone(self.encoder_)
        encoder.set_params(sample=False)
        # Transform the input array
        X_copy = check_array(X, dtype=None)
        X_encoded = self.encoder_.transform(X_copy[:, self.categorical_features_])
        for idx, col in enumerate(self.categorical_features_):
            X_copy[:, col] = X_encoded[:, idx]
        # Run predict on all submodels
        y_out = np.zeros((X.shape[0], self.samples))
        for index, submodel in enumerate(self.estimators_):
            y_out[:, index] = submodel.predict(X_copy)

        return np.average(y_out, axis=1)


    @available_if(_estimator_has("predict_proba"))
    def predict_proba(self, X) -> np.ndarray:
        """Call predict_proba on the estimators.
        
        The output of this function is the average predicted probability from
        all submodels.
        
        Parameters
        ----------
        X : indexable, length n_samples
            Must fulfill the input assumptions of the encoder.
        
        Returns
        -------
        np.ndarray of shape (n_samples,)
            The predicted class probability for ``X`` based on the average
            from each submodel.
        """
        # Clone the encoder and set sample to False
        # Transform the input array
        # Run predict_proba on all submodels
        # Stack and average
    
    @available_if(_estimator_has("predict_log_proba"))
    def predict_log_proba(self, X) -> np.ndarray:
        """Call predict_log_proba on the estimators.
        
        The output of this function is the average predicted probability from
        all submodels.
        
        Parameters
        ----------
        X : indexable, length n_samples
            Must fulfill the input assumptions of the encoder.
        
        Returns
        -------
        np.ndarray of shape (n_samples,)
            Predicted class log-probabilities for ``X`` based on the average
            from each submodel.
        """
        # Clone the encoder and set sample to False
        # Transform the input array
        # Run predict_log_proba on all submodels
        # Stack and average
