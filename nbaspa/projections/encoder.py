"""Bayesian target encoder."""

import logging
from typing import Callable, Dict, List, Union

import numpy as np
import scipy.stats
from sklearn.preprocessing._encoders import _BaseEncoder
from sklearn.utils.validation import check_is_fitted

LOG = logging.getLogger(__name__)

class BayesianTargetEncoder(_BaseEncoder):
    """Bayesian target encoder.
    
    Parameters
    ----------
    dist : str
        The posterior distribution for the target. This must be a distribution
        accessible through ``scipy.stats``. The parameters will be estimated
        using the distribution's ``.fit`` method and stored as ``posterior_params_``.
    sample : bool, optional (default False)
        Whether or not to encode the categorical values as a sample from the posterior
        distribution or the mean.
    categories : 'auto' or list of array-like, optional (default 'auto')
        Categories (unique values) per feature:

        - 'auto' : Determine categories automatically from the training data.
        - list : ``categories[i]`` holds the categories expected in the ith
          column. The passed categories should not mix strings and numeric
          values within a single feature, and should be sorted in case of
          numeric values.

        The used categories can be found in the ``categories_`` attribute.
    dtype : number type, optional (default float)
        Desired dtype of output.
    handle_unknown : {'error', 'ignore'}, default='error'
        Whether to raise an error or ignore if an unknown categorical feature
        is present during transform (default is to raise). When this parameter
        is set to 'ignore' and an unknown category is encountered during
        transform, the resulting one-hot encoded columns for this feature
        will be all zeros. In the inverse transform, an unknown category
        will be denoted as None.

    Attributes
    ----------

    References
    ----------
    .. [1] A compendium of conjugate priors, from https://www.johndcook.com/CompendiumOfConjugatePriors.pdf
    """

    _required_parameters = ["dist"]

    def __init__(
        self,
        dist: str,
        sample: bool = False,
        categories: Union[str, List] = "auto",
        dtype=np.float64,
        handle_unknown: str = "error",
    ):
        """Init method."""
        self.dist = dist
        self.sample = sample
        self.categories = categories
        self.dtype = dtype
        self.handle_unknown = handle_unknown

    
    def fit(self, X, y):
        """Fit the bayesian target encoder.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data to determine the categories of each feature and the posterior
            distributions.
        y : array-like of shape (n_samples,) or (n_samples, n_targets)
            Target values. Will be cast to X's dtype if necessary.
        
        Returns
        -------
        self : object
            Fitted encoder.
        """
        self._fit(X, handle_unknown=self.handle_unknown, force_all_finite=True)
        # First, save the parameters for the posterior distribution of the target

        return self
    

    def transform(self, X):
        """Transform the input dataset.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data to encode.
        
        Returns
        -------
        ndarray
            Transformed input.
        """
        check_is_fitted(self)

        X_int, X_mask = self._transform(
            X,
            handle_unknown=self.handle_unknown,
            force_all_finite=True,
            warn_on_unknown=(self.handle_unknown == "ignore")
        )
