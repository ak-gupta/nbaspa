=====================
NBA survival analysis
=====================


.. image:: https://img.shields.io/pypi/v/nba_survival.svg
        :target: https://pypi.python.org/pypi/nbaspa

.. image:: https://readthedocs.org/projects/nbaspa/badge/?version=latest
        :target: https://nbaspa.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


Survival analysis-based win percentage


* Free software: MIT license
* Documentation: https://nbaspa.readthedocs.io.

Purpose
-------

Win probability
~~~~~~~~~~~~~~~

The purpose of the ``nba_survival`` package is to develop a Survival Analysis-based
methodology for estimating Win Probability. This package will build and analyze a
dataset with the following variables:

+------------------------------------+--------------+-------------------------------------------------------+
| Variable                           | Time-Varying | Description                                           |
|                                    |              |                                                       |
+====================================+==============+=======================================================+
| ``WIN``                            | Yes          | | A boolean indicator of whether or not the home team |
|                                    |              | | won the game. This is the "event" that the survival |
|                                    |              | | analysis model will predict.                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``TIME``                           | Yes          | | Elapsed game time, in seconds. This is the time     |
|                                    |              | | variable for the survival analysis model.           |
+------------------------------------+--------------+-------------------------------------------------------+
| ``SCOREMARGIN``                    | Yes          | | The scoring margin at time ``TIME`` in the game.    |
|                                    |              | | For example, if the home team is leading 2-0, the   |
|                                    |              | | value of this variable is 2.                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_LINEUP_PLUS_MINUS`` [*]_    | Yes          | | The plus minus of the current lineup for the home   |
|                                    |              | | team.                                               |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_LINEUP_PLUS_MINUS`` [*]_ | Yes          | | The plus minus of the current lineup for the        |
|                                    |              | | visiting team.                                      |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_NET_RATING``                | No           | The net rating of the home team entering the game.    |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_NET_RATING``             | No           | | The net rating of the visiting team entering the    |
|                                    |              | | game.                                               |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_W_PCT``                     | No           | | The win percentage of the home team entering the    |
|                                    |              | | game.                                               |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_W_PCT``                  | No           | | The win percentage of the visiting team entering    |
|                                    |              | | the game.                                           |
+------------------------------------+--------------+-------------------------------------------------------+
| ``LAST_GAME_WIN``                  | No           | | A boolean indicator of whether or not the current   |
|                                    |              | | home team won the last meeting between these two    |
|                                    |              | | teams.                                              |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_GAMES_IN_LAST_3_DAYS``      | No           | | The number of games the home team has played in the |
|                                    |              | | last 3 days.                                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_GAMES_IN_LAST_3_DAYS``   | No           | | The number of games the visiting team has played in |
|                                    |              | | the last 3 days.                                    |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_GAMES_IN_LAST_5_DAYS``      | No           | | The number of games the home team has played in the |
|                                    |              | | last 5 days.                                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_GAMES_IN_LAST_5_DAYS``   | No           | | The number of games the visiting team has played in |
|                                    |              | | last 5 days.                                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_GAMES_IN_LAST_7_DAYS``      | No           | | The number of games the home team has played in the |
|                                    |              | | last 7 days.                                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_GAMES_IN_LAST_7_DAYS``   | No           | | The number of games the visiting team has played in |
|                                    |              | | the last 7 days.                                    |
+------------------------------------+--------------+-------------------------------------------------------+

.. [*] For any rows where the lineup can't be parsed, the value will be the home team's net rating.
.. [*] For any rows where the lineup can't be parsed, the value will be the visiting team's net rating.

Model types
+++++++++++

* The ``lifelines`` time-varying Cox proportional hazards model (see `here <https://lifelines.readthedocs.io/en/latest/Time%20varying%20survival%20regression.html>`_),
* An XGBoost classification model with a `custom objective function <https://xgboost.readthedocs.io/en/latest/tutorials/custom_metric_obj.html>`_
  using `groups <https://discuss.xgboost.ai/t/customized-cox-proportional-hazard-loss-function-in-xgboost/891>`_ to mark individual games.

Both models have hyperparameters that we will tune using `hyperopt <http://hyperopt.github.io/hyperopt/>`_.

Evaluating the models
+++++++++++++++++++++

To evaluate the survival model, we will follow the advice of the `lifelines <https://lifelines.readthedocs.io/en/latest/Survival%20Regression.html#model-selection-based-on-predictive-power-and-fit>`_
author. That is, we will evaluate the model efficacy using **Log-likelihood** and
**Concordance index**. Additionally, we will layer in a time-dependent Concordance index
based on the concept introduced in `scikit-survival <https://scikit-survival.readthedocs.io/en/latest/user_guide/evaluating-survival-models.html>`_.

We will benchmark the models against the NBA's win probability.

Player impact metric
~~~~~~~~~~~~~~~~~~~~

After establishing an effective model for win probability, we will investigate a player impact metric based
on the change in win probability on a play-by-play basis. For many events in a game, we can attribute the
impact to a single player:

+-------------------+--------------------------------------------+------------------------------------------+
| Event             | Primary player impact                      | Secondary player impact                  |
|                   |                                            |                                          |
+===================+============================================+==========================================+
| Free throw        | | The player shooting the free throws is   | N/A                                      |
|                   | | attributed with the change in win        |                                          |
|                   | | probability.                             |                                          |
+-------------------+--------------------------------------------+------------------------------------------+
| Rebound           | | The player that rebounded the ball is    | N/A                                      |
|                   | | attributed with the change in win        |                                          |
|                   | | probability.                             |                                          |
+-------------------+--------------------------------------------+------------------------------------------+
| Turnover          | | The player that turned the ball over is  | | If a live-ball turnover, the player    |
|                   | | attributed with the change in win        | | that stole the ball is attributed with |
|                   | | probability.                             | | an equal change in win probability.    |
+-------------------+--------------------------------------------+------------------------------------------+
| Foul              | | The player that committed the foul is    | | The player that drew the foul is       |
|                   | | attributed with the change in win        | | attributed with an equal change in win |
|                   | | probability.                             | | probability.                           |
+-------------------+--------------------------------------------+------------------------------------------+
| Missed field goal | | The player that missed the shot is       | N/A                                      |
|                   | | attributed with the change in win        |                                          |
|                   | | probability.                             |                                          |
+-------------------+--------------------------------------------+------------------------------------------+

There is one key event that is missing from the table above: made field goals.
That's because determining credit for a field goal can be a bit tricker. To
simplify it let's split all field goals into two buckets: assisted and unassisted.
Unassisted field goals are simple: the player that made the shot is given credit.
However, we need to determine what share of the change in win probability should be
attributed to an assisting player. For this metric, we will use the following
system for attributing credit:

.. math::

        A = \frac{P \cdot FG_PCT \cdot 100}{ORTG} - 1

where

* :math:`A` is the percentage of the change in win probability attributed to the
  assisting player,
* :math:`P` is the number of points associated with the field goal attempt,
* :math:`FG_PCT` is the shooter's field goal percentage from the area of the shot, and
* :math:`ORTG` is the team's offensive rating.

Essentially, we are giving the assisting player the credit for the percentage
change in the points per 100 possessions driven by the shot that they created.

Sequences
+++++++++

There is another corner case we need to address: sequences. Here, we will define a sequence
as a combination of events that occur in the same time period. For instance, a shooting foul
has a foul and free throws associated with a single timestamp. We need to firmly define how
much impact each player in the sequence should get. Below we've defined some common sequences:

+-----------------------------------------+-----------------------+-----------------------------------------+
| Sequence                                | Events                | Attribution                             |
|                                         |                       |                                         |
+=========================================+=======================+=========================================+
| Offensive foul                          | | * Foul              | | Offensive foul row dropped, player    |
|                                         | | * Turnover          | | committing the foul given blame.      |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (2PT FGA)                 | | * Foul              | | Player committing the foul given      |
|                                         | | * Free throw        | | blame. Player shooting free throws    |
|                                         | | * Free throw        | | given credit.                         |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (2PT FGA - Missed FT)     | | * Foul              | | Player committing the foul given      |
|                                         | | * Free throw        | | blame. Player shooting free throws    |
|                                         | | * Free throw        | | given credit. Unknown effect for      |
|                                         | | * Rebound           | | rebound.                              |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (3PT FGA)                 | | * Foul              | | Player committing the foul given      |
|                                         | | * Free throw        | | blame. Player shooting free throws    |
|                                         | | * Free throw        | | given credit.                         |
|                                         | | * Free throw        |                                         |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (3PT FGA - Missed FT)     | | * Foul              | | Player committing the foul given      |
|                                         | | * Free throw        | | blame. Player shooting free throws    |
|                                         | | * Free throw        | | given credit. Unknown effect for      |
|                                         | | * Free throw        | | rebound.                              |
|                                         | | * Rebound           |                                         |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (FGM)                     | | * Field goal made   | | Player committing the foul given      |
|                                         | | * Foul              | | blame. Player shooting the free throw |
|                                         | | * Free throw        | | given credit.                         |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (FGM - Missed FT)         | | * Field goal made   | | Player committing the foul given      |
|                                         | | * Foul              | | blame. Player shooting the free throw |
|                                         | | * Free throw        | | given credit. Unknown effect for      |
|                                         | | * Rebound           | | rebound.                              |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Putback FGM                             | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Field goal made   | | credit proportional to the quality    |
|                                         |                       | | of the shot taken (similar to         |
|                                         |                       | | assist). Player making the shot given |
|                                         |                       | | rest of credit.                       |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Putback FGA                             | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Field goal missed | | credit proportional to the quality of |
|                                         |                       | | shot taken (similar to assist).       |
|                                         |                       | | Player taking the shot given rest of  |
|                                         |                       | | credit.                               |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (Putback FGM)             | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Field goal made   | | credit proportional to the quality of |
|                                         | | * Foul              | | the shot. Quality of shot includes    |
|                                         | | * Free throw        | | expected value from free throw.       |
|                                         |                       | | Player that made the shot and shoots  |
|                                         |                       | | the free throw given rest of credit.  |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (Putback FGA)             | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Foul              | | credit proportional to the expected   |
|                                         | | * Free throw        | | value from free throws. Player taking |
|                                         | | * Free throw        | | free throws given rest of credit.     |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (Putback FGM - Missed FT) | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Field goal made   | | credit proportional to the quality of |
|                                         | | * Foul              | | the shot. Quality of shot includes    |
|                                         | | * Free throw        | | expected value from free throw.       |
|                                         | | * Rebound           | | Player that made the shot and shoots  |
|                                         |                       | | the free throw given rest of credit.  |
|                                         |                       | | Unknown effect for following rebound. |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (Putback FGA - Missed FT) | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Foul              | | credit proportional to the expected   |
|                                         | | * Free throw        | | value from free throws. Player taking |
|                                         | | * Free throw        | | free throws given rest of credit.     |
|                                         | | * Rebound           | | Unknown effect for following rebound. |
+-----------------------------------------+-----------------------+-----------------------------------------+

.. note::

        In the table above, we're defining "proportional" credit similarly to assists.

Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
