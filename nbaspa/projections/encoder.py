"""Bayesian target encoder."""

import logging
from typing import Callable, Dict, List, Tuple, Union

import numpy as np
import scipy.stats
from sklearn.preprocessing._encoders import _BaseEncoder
from sklearn.utils.validation import check_is_fitted

LOG = logging.getLogger(__name__)


def _init_bernoulli(y) -> Tuple:
    """Initialize a prior distribution for bernoulli likelihood.

    With a bernoulli likelihood, the common interpretation is that
    the conjugate prior beta distribution should be initialized with
    :math:`\alpha` representing the proportion of successes and :math:`\beta`
    representing the proportion of failures in the training set.
    
    Parameters
    ----------
    y : array-like of shape (n_samples,)
        Target values.
    
    Returns
    -------
    tuple
        The initialization parameters.
    """
    return np.average(y), 1 - np.average(y)

_LIKELIHOOD_PRIOR_MAPPING: Dict[str, Callable] = {
    "bernoulli": _init_bernoulli
}

def _posterior_bernoulli(y, mask, *params) -> Tuple:
    """Generate the posterior distribution for a bernoulli likelihood.

    According to Fink, the posterior distribution is parameterized by

    .. math::

        \alpha^{\prime} = \alpha + \sum_{i = 1}^{n} y_{i}
    
    and

    .. math::

        \beta^{\prime} = \beta + n - \sum_{i = 1}^{n} y_{i}
    
    Parameters
    ----------
    y : array-like of shape (n_samples,)
        Target values.
    mask : array-like of shape (n_samples,)
        A boolean array indicating the observations in ``y`` that should
        be used to generate the posterior distribution.
    *params
        The prior distribution parameters.
    
    Returns
    -------
    tuple
        Parameters for the posterior distribution.

    References
    ----------
    .. [1] A compendium of conjugate priors, from https://www.johndcook.com/CompendiumOfConjugatePriors.pdf
    """
    success = np.sum(y[mask])

    return params[0] + success, params[1] + np.sum(mask) - success

_POSTERIOR_UPDATE: Dict[str, Callable] = {
    "bernoulli": _posterior_bernoulli
}

_POSTERIOR_DISPATCHER: Dict[str, Callable] = {
    "bernoulli": scipy.stats.beta
}

class BayesianTargetEncoder(_BaseEncoder):
    """Bayesian target encoder.

    This encoder will

    1. Derive the prior distribution from the supplied ``dist``,
    2. Initialize the prior distribution hyperparameters using the training data,
    3. For each level in each categorical,
        * Generate the posterior distribution,
        * Set the encoding value(s) as a sample or the mean from the posterior distribution
    
    Parameters
    ----------
    dist : str
        The likelihood for the target. This must be a distribution
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
    prior_params_ : tuple
        The estimated hyperparameters for the prior distribution.
    posterior_params_ : list
        A list of arrays. Each entry in the list corresponds to the categorical
        feature in ``categories_``. Each index in the underlying array contains
        the parameters for the posterior distribution for the given level.
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
        # Initialize the prior distribution parameters
        try:
            self.prior_params_ = _LIKELIHOOD_PRIOR_MAPPING[self.dist](y)
        except KeyError:
            raise NotImplementedError(f"{self.dist} has not been implemented.")
        
        # Loop through each categorical
        self.posterior_params_: List[np.ndarray] = []
        for index, cat in enumerate(self.categories_):
            # Loop through each level
            catparams = []
            for level in cat:
                # Get a mask
                mask = (X[:, index] == level)
                # Update the posterior distribution
                catparams.append(_POSTERIOR_UPDATE[self.dist](y, mask, *self.prior_params_))
            
            self.posterior_params_.append(np.array(catparams))

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

        X_int, _ = self._transform(
            X,
            handle_unknown=self.handle_unknown,
            force_all_finite=True,
        )

        X_out = np.zeros(X.shape)
        # Loop through each categorical
        for idx, cat in enumerate(self.categories_):
            # Loop through each level and sample or evaluate the mean from the posterior
            for levelno in range(cat.shape[0]):
                mask = (X_int[:, idx] == levelno)
                rv = _POSTERIOR_DISPATCHER[self.dist](*self.posterior_params_[idx][levelno, :])
                if self.sample:
                    X_out[mask, idx] = rv.rvs(size=np.sum(mask))
                else:
                    X_out[mask, idx] = rv.moment(n=1)

        return X_out
