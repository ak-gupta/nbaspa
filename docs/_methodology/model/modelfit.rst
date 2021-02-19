==========================
Model types and evaluation
==========================

------
Models
------

We will investigate two models for estimating within-game win probability:

* The ``lifelines`` time-varying Cox proportional hazards model
  (see `here <https://lifelines.readthedocs.io/en/latest/Time%20varying%20survival%20regression.html>`_), and
* An XGBoost regression model with the ``survival:cox`` objective function.

---------------------
Hyperparameter tuning
---------------------

Both models have hyperparameters that we will tune using `hyperopt <http://hyperopt.github.io/hyperopt/>`_.

~~~~~~~~~
Lifelines
~~~~~~~~~

Details coming soon.

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
