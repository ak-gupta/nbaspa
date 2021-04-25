===========
Performance
===========

--------
Overview
--------

* Both models perform better (on average) than the NBA's model, with a particular advantage in
  early game prediction.
* The Lifelines model far outperforms the XGBoost model.

For generating player ratings, we will use the Lifelines model.

-----------
Performance
-----------

.. important::

    At this time the models have been trained on data from the 2010-11 through the 2019-20 seasons
    (pre-bubble).

Figure 1 shows the AUROC over game-time for each model.

.. image:: ../_static/auroc.png
    :align: center
    :alt: Figure 1

Figure 2 directly shows the AUROC lift of each survival model against the NBA win probability
model.

.. image:: ../_static/auroc_lift.png
    :align: center
    :alt: Figure 2

Overall, the average AUROC lift for each model is summarized below:

+-----------+---------------+--------------------------------+
| Model     | Average AUROC | Percentage lift over NBA model |
|           |               |                                |
+===========+===============+================================+
| XGBoost   | 0.822         | 3.974%                         |
+-----------+---------------+--------------------------------+
| Lifelines | 0.845         | 6.888%                         |
+-----------+---------------+--------------------------------+

---------------------
Hyperparameter tuning
---------------------

Figure 3 shows the hyperparameter tuning results for the ``lifelines`` model. The tuning was done
using 5 000 evaluations.

.. image:: ../_static/lifelines-tuning.png
    :align: center
    :alt: Figure 3

Figure 4 shows the hyperparameter tuning results for the ``xgboost`` model. The tuning was done
using 5 000 evaluations.

.. image:: ../_static/xgboost-tuning.png
    :align: center
    :alt: Figure 4
