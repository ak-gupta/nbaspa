=====
Usage
=====

-----------------------------
Pulling data from the NBA API
-----------------------------

For this model, we are pulling data from the public, undocumented NBA Stats API. The data
loader is built on excellent work by `swar <https://github.com/swar/nba_api>`_ and
`seemethere <https://github.com/seemethere/nba_py/>`_.

Each endpoint has an associated class (see :doc:`the API reference <api/nba.data.endpoints>`_).
Let's focus on :py:class:`nbaspa.data.endpoints.boxscore.BoxScoreTraditional`. First,
we need to initialize the class:

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

    $ nbaspa-download scoreboard --output-dir path/to/data --season 2018-19

The call above will download the metadata for the 2018-19 NBA season. The data will be
saved to ``path/to/data/2018-19``. Next, we can download the player-level data, including
shooting dashboards with

.. code-block:: console

    $ nbaspa-download players --output-dir path/to/data --season 2018-19

Again, this will download the data to ``path/to/data/2018-19``. Then, let's download team
data,

.. code-block:: console

    $ nbaspa-download teams --output-dir path/to/data --season 2018-19

Finally, we can download the game data:

.. code-block:: console

    $ nbaspa-download games --output-dir path/to/data --season 2018-19

-------------
Cleaning data
-------------

-------------------
Training the models
-------------------

-----------------------
Generate player ratings
-----------------------
