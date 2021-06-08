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
dataset into two pieces: **build** (80%) and **holdout** (20%). The build dataset will be used for
model training and hyperparameter tuning while the holdout dataset will be used for comparing the
models. The **build** dataset will be broken down for each model:

+---------------+----------------+-----------------------------+----------------------------------+
| Model         | Build datasets | Proportion of build (total) | Description                      |
|               |                |                             |                                  |
+===============+================+=============================+==================================+
| ``lifelines`` | Train          | 75% (60%)                   | Model training data.             |
|               +----------------+-----------------------------+----------------------------------+
|               | Tune           | 25% (20%)                   | Hyperparameter tuning data.      |
+---------------+----------------+-----------------------------+----------------------------------+
| ``xgboost``   | Train          | 75% (60%)                   | Model training data.             |
|               +----------------+-----------------------------+----------------------------------+
|               | Stopping/Tune  | 25% (20%)                   | | Data for tuning and early      |
|               |                |                             | | stopping [*]_                  |
+---------------+----------------+-----------------------------+----------------------------------+

The datasets will be stratified by season and by the target to ensure that the models are being
built on representative data.

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

+----------------+--------------------+
| Hyperparameter | Search space       |
|                |                    |
+================+====================+
| ``penalizer``  | :math:`Unif(0, 1)` |
+----------------+--------------------+
| ``l1_ratio``   | :math:`Unif(0, 1)` |
+----------------+--------------------+

To maximize the tuning search, we limited to the following space after some trials:

+----------------+-----------------------+
| Hyperparameter | Search space          |
|                |                       |
+================+=======================+
| ``penalizer``  | :math:`Unif(0, 0.3)`  |
+----------------+-----------------------+
| ``l1_ratio``   | :math:`Unif(0, 0.01)` |
+----------------+-----------------------+

~~~~~~~
XGBoost
~~~~~~~

Based on discussions with `heytheredli <https://github.com/heytheredli/>`_ and
iteratively limiting the range for each parameter to maximize the effectiveness
of the search, we used the following space to start:

+-----------------------+-----------------------------+
| Hyperparameter        | Search space                |
|                       |                             |
+=======================+=============================+
| ``learning_rate``     | :math:`Unif(0, 0.01)`       |
+-----------------------+-----------------------------+
| ``subsample``         | :math:`Unif(0, 1)`          |
+-----------------------+-----------------------------+
| ``max_delta_step``    | :math:`Unif(0, 1)`          |
+-----------------------+-----------------------------+
| ``max_depth``         | :math:`QUnif(2, 15, 1)`     |
+-----------------------+-----------------------------+
| ``gamma``             | :math:`Unif(0, 1)`          |
+-----------------------+-----------------------------+
| ``reg_alpha``         | :math:`Unif(0, 1)`          |
+-----------------------+-----------------------------+
| ``reg_lambda``        | :math:`Unif(0, 1)`          |
+-----------------------+-----------------------------+
| ``colsample_bytree``  | :math:`Unif(0, 1)`          |
+-----------------------+-----------------------------+
| ``colsample_bylevel`` | :math:`Unif(0, 1)`          |
+-----------------------+-----------------------------+
| ``colsample_bynode``  | :math:`Unif(0, 1)`          |
+-----------------------+-----------------------------+
| ``min_child_weight``  | :math:`QUnif(100, 600, 10)` |
+-----------------------+-----------------------------+

After iteration, we used the following space:

+-----------------------+-----------------------------+
| Hyperparameter        | Search space                |
|                       |                             |
+=======================+=============================+
| ``learning_rate``     | 0.01                        |
+-----------------------+-----------------------------+
| ``subsample``         | :math:`Unif(0.75, 0.9)`     |
+-----------------------+-----------------------------+
| ``max_delta_step``    | 1                           |
+-----------------------+-----------------------------+
| ``max_depth``         | :math:`QUnif(5, 15, 1)`     |
+-----------------------+-----------------------------+
| ``gamma``             | :math:`Unif(0.6, 0.9)`      |
+-----------------------+-----------------------------+
| ``reg_alpha``         | :math:`Unif(0, 0.1)`        |
+-----------------------+-----------------------------+
| ``reg_lambda``        | :math:`Unif(0.1, 0.3)`      |
+-----------------------+-----------------------------+
| ``colsample_bytree``  | :math:`Unif(0.3, 0.7)`      |
+-----------------------+-----------------------------+
| ``colsample_bylevel`` | :math:`Unif(0.4, 0.6)`      |
+-----------------------+-----------------------------+
| ``colsample_bynode``  | :math:`Unif(0.7, 1)`        |
+-----------------------+-----------------------------+
| ``min_child_weight``  | :math:`QUnif(450, 480, 1)`  |
+-----------------------+-----------------------------+

We also added a `monotonic constraint <https://xgboost.readthedocs.io/en/latest/tutorials/monotonic.html>`_
to ensure that the model output is monotonic in scoring margin.

-----------
Calibration
-----------

We will use `isotonic regression <https://scikit-learn.org/stable/modules/generated/sklearn.isotonic.IsotonicRegression.html#sklearn.isotonic.IsotonicRegression>`_
to calibrate the output probabilities from each model to ensure that we have interpretable outputs.

----------------
Model evaluation
----------------

We will compare each survival model with the NBA win probability output using AUROC. Specifically, we will generate a plot
describing the AUROC at each time step from 0 to 2880 seconds (48 minutes); this metric is based on a similar concept introduced
in `scikit-survival <https://scikit-survival.readthedocs.io/en/latest/user_guide/evaluating-survival-models.html>`_.
