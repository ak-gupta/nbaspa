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

+-------------------------------+--------------+------------------------------------------------------------+
| Variable                      | Time-Varying | Description                                                |
|                               |              |                                                            |
+===============================+==============+============================================================+
| ``WIN``                       | Yes          | | A boolean indicator of whether or not the home team won  |
|                               |              | | the game. This is the "event" that the survival analysis |
|                               |              | | model will predict.                                      |
+-------------------------------+--------------+------------------------------------------------------------+
| ``TIME``                      | Yes          | | Elapsed game time, in seconds. This is the time variable |
|                               |              | | for the survival analysis model.                         |
+-------------------------------+--------------+------------------------------------------------------------+
| ``SCOREMARGIN``               | Yes          | | The scoring margin at time ``TIME`` in the game. For     |
|                               |              | | example, if the home team is leading 2-0, the value of   |
|                               |              | | this variable is 2.                                      |
+-------------------------------+--------------+------------------------------------------------------------+
| ``HOME_LINEUP_PLUS_MINUS``    | Yes          | The plus minus of the current lineup for the home team.    |
+-------------------------------+--------------+------------------------------------------------------------+
| ``VISITOR_LINEUP_PLUS_MINUS`` | Yes          | | The plus minus of the current lineup for the visiting    |
|                               |              | | team.                                                    |
+-------------------------------+--------------+------------------------------------------------------------+
| ``HOME_NET_RATING``           | No           | The net rating of the home team entering the game.         |
+-------------------------------+--------------+------------------------------------------------------------+
| ``VISITOR_NET_RATING``        | No           | The net rating of the visiting team entering the game.     |
+-------------------------------+--------------+------------------------------------------------------------+
| ``HOME_W_PCT``                | No           | The win percentage of the home team entering the game.     |
+-------------------------------+--------------+------------------------------------------------------------+
| ``VISITOR_W_PCT``             | No           | The win percentage of the visiting team entering the game. |
+-------------------------------+--------------+------------------------------------------------------------+
| ``LAST_GAME_WIN``             | No           | | A boolean indicator of whether or not the current home   |
|                               |              | | team won the last meeting between these two teams.       |
+-------------------------------+--------------+------------------------------------------------------------+

Still need to be implemented:

* Days since last game
* Games in past 7 days

After establishing an effective model for win probability, we will investigate a player impact metric based
on the change in win probability on a play-by-play basis.

Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
