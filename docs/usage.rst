=============
Package Usage
=============

-----------------------------
Pulling data from the NBA API
-----------------------------

For this model, we are pulling data from the public, undocumented NBA Stats API. The data
loader is built on excellent work by `swar <https://github.com/swar/nba_api>`_ and
`seemethere <https://github.com/seemethere/nba_py/>`_.

Each endpoint has an associated class (see :doc:`the API reference <api/nbaspa.data.endpoints>`
for a complete list). Let's focus on :py:class:`nbaspa.data.endpoints.boxscore.BoxScoreTraditional`.
First, we need to initialize the class:

.. code-block:: python

    from nbaspa.data.endpoints import BoxScoreTraditional

    box = BoxScoreTraditional(GameID="0021800001", output_dir="nba-data/2018-19")

In this call, we're specifying the game identifier and the output directory for the downloaded
data. Then, we can download the data:

.. code-block:: python

    box.get()

You should see a new file, ``nba-data/2018-19/boxscoretraditionalv2/data_0021800001.json``. To
preview the data, you can choose a dataset from ``box.datasets`` and then select a
dataset type:

.. code-block:: python

    df = box.get_data("PlayerStats")

and that's it!

~~~~~~~~~~~~~~
Multiple calls
~~~~~~~~~~~~~~

Calling an individual endpoint for every game in a season is... tiring. So, we made a factory
class that will loop through multiple calls. First, define your list of calls.

.. code-block:: python

    calls = [
        ("BoxScoreTraditional", {"GameID": "0021800001"}),
        ("BoxScoreTraditional", {"GameID": "0021800002"})
    ]

Next, initialize :py:class:`nbaspa.data.factory.NBADataFactory` and download the data:

.. code-block:: python

    from nbaspa.data.factory import NBADataFactory

    factory = NBADataFactory(calls=calls, output_dir="nba-data/2018-19")
    factory.get()

.. important::

    We use `ratelimit <https://github.com/tomasbasham/ratelimit>`_ to prevent overloading the
    NBA API. The ratelimiting is **very** conservative and limits to 5 calls every 10 minutes.

~~~~~~~~~~~~~~~~~~~~~~
Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

The simplest way to retrieve the data used for this model build is to use the CLI.

.. code-block:: console

    $ nbaspa-download scoreboard --output-dir nba-data --season 2018-19

The call above will download the metadata for the 2018-19 NBA season. The data will be
saved to ``nba-data/2018-19``. Next, we can download the player-level data, including
shooting dashboards with

.. code-block:: console

    $ nbaspa-download players --output-dir nba-data --season 2018-19

Again, this will download the data to ``nba-data/2018-19``. Then, let's download team
data,

.. code-block:: console

    $ nbaspa-download teams --output-dir nba-data --season 2018-19

Finally, we can download the game data:

.. code-block:: console

    $ nbaspa-download games --output-dir nba-data --season 2018-19

-------------
Cleaning data
-------------

Our `prefect <https://docs.prefect.io/core/>`_ data cleaning pipeline iterates through all
games on a given day. The pipeline produces two types of data: ``model`` and ``rating``. The
``model`` dataset will be an input for the survival analysis model while the ``rating`` dataset
will be used for generating SPA ratings. To clean a given day in python,

.. code-block:: python

    from nbaspa.data.pipeline import gen_pipeline, run_pipeline

    flow = gen_pipeline()
    output = run_pipeline(
        flow=flow,
        output_dir="nba-data/2018-19",
        save_data=True,
        mode="model",
        Season="2018-19",
        GameDate="10/16/2018"
    )

This flow will save each game as a CSV in ``nba-data/2018-19/model-data``. To read the CSV back
into python,

.. code-block:: python

    import pandas as pd

    df = pd.read_csv(
        "nba-data/2018-19/model-data/data_0021800001.csv",
        sep="|",
        index_col=0,
        dtype={"GAME_ID": str}
    )

~~~~~~~~~~~~~~~~~~~~~~
Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

As with downloading data, the CLI is the best way to clean data. For model data:

.. code-block:: console

    $ nbaspa-clean model --output-dir nba-data --season 2018-19

and for ratings data:

.. code-block:: console

    $ nbaspa-clean rating --output-dir nba-data --season 2018-19

Both of these calls will save data to ``nba-data/2018-19``.

-------------------
Training the models
-------------------

Documentation coming soon.

-----------------------
Generate player ratings
-----------------------

Documentation coming soon.
