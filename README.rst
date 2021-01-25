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

The purpose of the ``nba_survival`` package is to develop a Survival Analysis-based methodology for estimating Win Probability.
I will investigate the following time-varying covariates:

* Scoring margin
* Lineup net rating

as well as the following static covariates:

* Home team net rating
* Home team win percentage
* Away team net rating
* Away team win percentage
* Last meeting result (1 for current home team victory, 0 for current home team loss)
* Home team days since last game
* Away team days since last game

If I'm able to establish an effective model for win probability I will investigate a player impact metric based on the change
in survival probability based on play-by-play events.

Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
