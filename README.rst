=====================
NBA Survival Analysis
=====================


.. image:: https://img.shields.io/pypi/v/nba_survival.svg
        :target: https://pypi.python.org/pypi/nba_survival

.. image:: https://img.shields.io/travis/ak-gupta/nba_survival.svg
        :target: https://travis-ci.com/ak-gupta/nba_survival

.. image:: https://readthedocs.org/projects/nba-survival/badge/?version=latest
        :target: https://nba-survival.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Survival analysis-based win percentage


* Free software: MIT license
* Documentation: https://nba-survival.readthedocs.io.

Purpose
-------

The purpose of the ``nba_survival`` package is to develop a Survival Analysis-based
methodology for estimating Win Probability. This package will build and analyze a
dataset with the following variables:

+----------------------------------+--------------+---------------------------------------------------------+
| Variable                         | Time-Varying | Description                                             |
|                                  |              |                                                         |
+==================================+==============+=========================================================+
| ``WIN``                          | Yes          | | A boolean indicator of whether or not the home team   |
|                                  |              | | won the game. This is the "event" that the survival   |
|                                  |              | | analysis model will predict.                          |
+----------------------------------+--------------+---------------------------------------------------------+
| ``TIME``                         | Yes          | | Elapsed game time, in seconds. This is the time       |
|                                  |              | | variable for the survival analysis model.             |
+----------------------------------+--------------+---------------------------------------------------------+
| ``SCOREMARGIN``                  | Yes          | | The scoring margin at time ``TIME`` in the game. For  |
|                                  |              | | example, if the home team is leading 2-0, the value   |
|                                  |              | | of this variable is 2.                                |
+----------------------------------+--------------+---------------------------------------------------------+
| ``HOME_LINEUP_PLUS_MINUS``       | Yes          | The plus minus of the current lineup for the home team. |
+----------------------------------+--------------+---------------------------------------------------------+
| ``VISITOR_LINEUP_PLUS_MINUS``    | Yes          | | The plus minus of the current lineup for the visiting |
|                                  |              | | team.                                                 |
+----------------------------------+--------------+---------------------------------------------------------+
| ``HOME_NET_RATING``              | No           | The net rating of the home team entering the game.      |
+----------------------------------+--------------+---------------------------------------------------------+
| ``VISITOR_NET_RATING``           | No           | The net rating of the visiting team entering the game.  |
+----------------------------------+--------------+---------------------------------------------------------+
| ``HOME_W_PCT``                   | No           | The win percentage of the home team entering the game.  |
+----------------------------------+--------------+---------------------------------------------------------+
| ``VISITOR_W_PCT``                | No           | | The win percentage of the visiting team entering the  |
|                                  |              | | game.                                                 |
+----------------------------------+--------------+---------------------------------------------------------+
| ``LAST_GAME_WIN``                | No           | | A boolean indicator of whether or not the current     |
|                                  |              | | home team won the last meeting between these two      |
|                                  |              | | teams.                                                |
+----------------------------------+--------------+---------------------------------------------------------+
| ``HOME_GAMES_IN_LAST_3_DAYS``    | No           | | The number of games the home team has played in the   |
|                                  |              | | last 3 days.                                          |
+----------------------------------+--------------+---------------------------------------------------------+
| ``VISITOR_GAMES_IN_LAST_3_DAYS`` | No           | | The number of games the visiting team has played in   |
|                                  |              | | the last 3 days.                                      |
+----------------------------------+--------------+---------------------------------------------------------+
| ``HOME_GAMES_IN_LAST_5_DAYS``    | No           | | The number of games the home team has played in the   |
|                                  |              | | last 5 days.                                          |
+----------------------------------+--------------+---------------------------------------------------------+
| ``VISITOR_GAMES_IN_LAST_5_DAYS`` | No           | | The number of games the visiting team has played in   |
|                                  |              | | last 5 days.                                          |
+----------------------------------+--------------+---------------------------------------------------------+
| ``HOME_GAMES_IN_LAST_7_DAYS``    | No           | | The number of games the home team has played in the   |
|                                  |              | | last 7 days.                                          |
+----------------------------------+--------------+---------------------------------------------------------+
| ``VISITOR_GAMES_IN_LAST_7_DAYS`` | No           | | The number of games the visiting team has played in   |
|                                  |              | | the last 7 days.                                      |
+----------------------------------+--------------+---------------------------------------------------------+

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

Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
