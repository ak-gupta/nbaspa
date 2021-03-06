=======================================
Survival analysis-powered player impact
=======================================

.. image:: https://img.shields.io/github/license/ak-gupta/nbaspa
        :alt: License

.. image:: https://readthedocs.org/projects/nbaspa/badge/?version=latest
        :target: https://nbaspa.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/travis/ak-gupta/nbaspa.svg?branch=master
        :target: https://travis-ci.com/ak-gupta/nbaspa
        :alt: Travis CI

.. image:: https://codecov.io/github/ak-gupta/nbaspa/coverage.svg?branch=master
        :target: https://codecov.io/github/ak-gupta/nbaspa?branch=master
        :alt: Test coverage

.. image:: https://api.codeclimate.com/v1/badges/eef4b080029d9f47cd5b/maintainability
        :target: https://codeclimate.com/github/ak-gupta/nbaspa/maintainability
        :alt: CodeClimate maintainability

* Free software: MIT license
* Documentation: https://nbaspa.readthedocs.io.

    Player impact metrics are supposed to help us understand one thing: how much does a player impact
    winning?

Survival Probability Added (SPA) is a new player impact metric based on allocating credit
to players based on how their actions change win probability. Our estimate of win probability
comes is based on `survival analysis <https://lifelines.readthedocs.io/en/latest/Survival%20Analysis%20intro.html>`_,
hence the "S" in SPA.

-------
Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
