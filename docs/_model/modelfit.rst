===========
Methodology
===========

------
Models
------

We will investigate two models for estimating within-game win probability:

* The ``lifelines`` time-varying Cox proportional hazards model
  (see `here <https://lifelines.readthedocs.io/en/latest/Time%20varying%20survival%20regression.html>`_), and
* An XGBoost regression model with the ``survival:cox`` objective function.

To accurately compare the models to each other and the NBA's own win probability, we will split the
dataset into two pieces: **build** (85%) and **holdout** (15%). The build dataset will be used for
model training and hyperparameter tuning while the holdout dataset will be used for comparing the
models. The **build** dataset will be broken down for each model:

+---------------+----------------+-----------------------------+----------------------------------+
| Model         | Build datasets | Proportion of build (total) | Description                      |
|               |                |                             |                                  |
+===============+================+=============================+==================================+
| ``lifelines`` | Train          | 70% (59.5%)                 | Model training data.             |
|               +----------------+-----------------------------+----------------------------------+
|               | Tune           | 30% (25.5%)                 | Hyperparameter tuning data.      |
+---------------+----------------+-----------------------------+----------------------------------+
| ``xgboost``   | Train          | 70% (59.5%)                 | Model training data.             |
|               +----------------+-----------------------------+----------------------------------+
|               | Stopping       | 15% (12.75%)                | Data for early stopping [*]_     |
|               +----------------+-----------------------------+----------------------------------+
|               | Tune           | 15% (12.75%)                | Hyperparameter tuning data.      |
+---------------+----------------+-----------------------------+----------------------------------+

.. [*] We will use `early stopping <https://xgboost.readthedocs.io/en/latest/python/python_intro.html#early-stopping>`_
       to determine the number of boosting rounds for the model.

---------------------
Hyperparameter tuning
---------------------

Both models have hyperparameters that we will tune using `hyperopt <http://hyperopt.github.io/hyperopt/>`_.

~~~~~~~~~
Lifelines
~~~~~~~~~

We will use the following hyperparameter search space for the ``lifelines`` model.

+----------------+---------------------+
| Hyperparameter | Search space        |
|                |                     |
+================+=====================+
| ``penalizer``  | :math:`Unif(0, 1)`. |
+----------------+---------------------+
| ``l1_ratio``   | :math:`Unif(0, 1)`. |
+----------------+---------------------+

~~~~~~~
XGBoost
~~~~~~~

Details coming soon.

----------------
Model evaluation
----------------

We will compare each survival model with the NBA win probability output using AUROC. Specifically, we will generate a plot
describing the AUROC at each time step from 0 to 2880 seconds (48 minutes); this metric is based on a similar concept introduced
in `scikit-survival <https://scikit-survival.readthedocs.io/en/latest/user_guide/evaluating-survival-models.html>`_.
Additionally, we will use Concordance Index to generally evaluate the predictive power of each model.
