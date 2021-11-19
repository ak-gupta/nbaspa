=============
Package Usage
=============

-----------------------------
Pulling data from the NBA API
-----------------------------

For this model, we are pulling data from the public, undocumented NBA Stats API. The data
loader is built on excellent work by `swar <https://github.com/swar/nba_api>`_ and
`seemethere <https://github.com/seemethere/nba_py/>`_.

~~~~~~
Python
~~~~~~

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

++++++++++++++
Multiple calls
++++++++++++++

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
    NBA API. The ratelimiting is **very** conservative and limits to 1 call every minute.

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

If you want to bundle these calls into a single CLI command, use the ``season`` endpoint:

.. code-block:: console

    $ nbaspa-download season --output-dir nba-data --season 2018-19

-------------
Cleaning data
-------------

Our `prefect <https://docs.prefect.io/core/>`_ data cleaning pipeline iterates through all
games on a given day. The pipeline produces two types of data: ``model`` and ``rating``. The
``model`` dataset will be an input for the survival analysis model while the ``rating`` dataset
will be used for generating SPA ratings.

~~~~~~
Python
~~~~~~

To clean a given day in python,

.. code-block:: python

    from nbaspa.data.pipeline import gen_pipeline, run_pipeline

    flow = gen_pipeline()
    output = run_pipeline(
        flow=flow,
        data_dir="nba-data/2018-19",
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

    $ nbaspa-clean model --data-dir nba-data --output-dir nba-data --season 2018-19

and for ratings data:

.. code-block:: console

    $ nbaspa-clean rating --data-dir nba-data --output-dir nba-data --season 2018-19

Both of these calls will save data to ``nba-data/2018-19``.

----------------------------------
Training and evaluating the models
----------------------------------

.. important::

    The outputs for the following pipelines will be saved using Prefect
    `checkpointing <https://docs.prefect.io/core/concepts/persistence.html#persisting-output>`_.
    For this to work you must set the following environment variable:

    .. code-block:: console

        $ export PREFECT__FLOWS__CHECKPOINTING=true

~~~~~~
Python
~~~~~~

+++++++++++++++++++++
Building the datasets
+++++++++++++++++++++

To create the **build** and **holdout** CSV files,

.. code-block:: python

    from nbaspa.model.pipeline import gen_data_pipeline, run_pipeline

    flow = gen_data_pipeline()
    output = run_pipeline(
        flow=flow, data_dir="nba-data", output_dir="nba-data", splits=(0.6, 0.2, 0.2), seed=42
    )

This flow will save ``build.csv`` and ``holdout.csv`` to ``nba-data/models``.

+++++++++++++++++++
Training the models
+++++++++++++++++++

To train a ``lifelines`` model,

.. code-block:: python

    from nbaspa.model.pipeline import gen_lifelines_pipeline, run_pipeline

    flow = gen_lifelines_pipeline()
    output = run_pipeline(
        flow=flow, data_dir="nba-data", output_dir="nba-data", max_evals=5000, seed=42
    )

If you ran the flow on 2021-02-21, the ``lifelines`` model artifacts will be saved to the
``nba-data/models/2021-02-21/lifelines`` folder. To train a ``xgboost`` model,

.. code-block:: python

    from nbaspa.model.pipeline import gen_xgboost_pipeline, run_pipeline

    flow = gen_xgboost_pipeline()
    output = run_pipeline(
        flow=flow, data_dir="nba-data", output_dir="nba-data", max_evals=5000, seed=42
    )

If you ran the flow on 2021-02-21, the ``xgboost`` model artifacts will be saved to the
``nba-data/models/2021-02-21/xgboost`` folder.

+++++++++++++++++
Evaluating models
+++++++++++++++++

To evaluate a set of models,

.. code-block:: python

    from nbaspa.model.pipeline import gen_evaluate_pipeline, run_pipeline

    flow = gen_evaluate_pipeline(
        lifelines="nba-data/models/2021-02-21/lifelines/model.pkl",
        xgboost="nba-data/models/2021-02-21/xgboost/model.pkl"
    )
    output = run_pipeline(flow=flow, data_dir="nba-data", output_dir="nba-data")

This flow will read in the ``model.pkl`` files, create the AUROC visualizations, and
save the visualizations to ``nba-data/models/2021-02-21``.

++++++++++++++++++++++
Game-level predictions
++++++++++++++++++++++

To run game-level predictions for all of your data, run

.. code-block:: python

    from nbaspa.model.pipeline import gen_predict_pipeline, run_pipeline

    flow = gen_predict_pipeline()
    output = run_pipeline(
        flow=flow,
        data_dir="nba-data",
        output_dir="nba-data",
        filesystem="file",
        model="nba-data/models/2021-02-21/lifelines/model.pkl",
    )

To restrict to a single season, supply the ``season`` parameter:

.. code-block:: python
    :emphasize-lines: 7

    output = run_pipeline(
        flow=flow,
        data_dir="nba-data",
        output_dir="nba-data",
        filesystem="file",
        model="nba-data/models/2021-02-21/lifelines/model.pkl",
        Season="2018-19"
    )

Similarly, you can run the predictions for a single game:

.. code-block:: python
    :emphasize-lines: 7

    output = run_pipeline(
        flow=flow,
        data_dir="nba-data",
        output_dir="nba-data",
        filesystem="file",
        model="nba-data/models/2021-02-21/lifelines/model.pkl",
        GameID="0021800001"
    )

~~~~~~~~~~~~~~~~~~~~~~
Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

+++++++++++++++++++++
Building the datasets
+++++++++++++++++++++

First, we need to split the initial dataset into **build** and **holdout**:

.. code-block:: console

    $ nbaspa-model build --data-dir nba-data --output-dir nba-data

This CLI call will save two CSV files to ``nba-data/models``: ``build.csv`` and ``holdout.csv``.

+++++++++++++++++++
Training the models
+++++++++++++++++++

Next, we can fit a model

.. code-block:: console

    $ nbaspa-model train --data-dir nba-data --output-dir nba-data --model lifelines

This CLI call will train a ``lifelines`` model with

* a 75-25 train-tune split within the build dataset, and
* a maximum of 100 ``hyperopt`` evaluations.

You can modify these parameters with ``--splits`` and ``--max-evals``, respectively.
To train an ``xgboost`` model,

.. code-block:: console

    $ nbaspa-model train --data-dir nba-data --output-dir nba-data --model xgboost

For the ``xgboost`` model, our tuning dataset will double as the early stopping data.

After you call the ``train`` endpoint you will see a new subfolder within ``nba-data/models``
corresponding to the system date. The ``lifelines`` artifacts will be saved to a ``lifelines``
subfolder; the ``xgboost`` artifacts will be saved to a ``xgboost`` subfolder.

+++++++++++++++++
Evaluating models
+++++++++++++++++

To evaluate your models, use the ``evaluate`` endpoint. Suppose you trained your model on 2021-02-21:

.. code-block:: console

    $ nbaspa-model evaluate \
        --data-dir nba-data \
        --output-dir nba-data \
        --model lifelines nba-data/models/2021-02-21/lifelines/model.pkl \
        --model xgboost nba-data/models/2021-02-21/xgboost/model.pkl

This endpoint will read in the model ``.pkl`` files, create the AUROC visualizations, and
save them to the ``nba-data/models/2021-02-21`` folder.

++++++++++++++++++++++
Game-level predictions
++++++++++++++++++++++

To run game-level predictions, use the ``predict`` endpoint. Suppose you trained your model on 2021-02-21:

.. code-block:: console

    $ nbaspa-model predict \
        --data-dir nba-data \
        --output-dir nba-data \
        --model nba-data/models/2021-02-21/lifelines/model.pkl \

The above call will create game-level predictions for all cleaned game data available in ``nba-data``.

.. important::

    The predictions can be found in ``nba-data/<Season>/survival-prediction/data_<GameID>.csv``.

To restrict to a season or game, supply ``--season`` or ``--game-id``:

.. code-block:: console

    $ nbaspa-model predict \
        --data-dir nba-data \
        --output-dir nba-data \
        --model nba-data/models/2021-02-21/lifelines/model.pkl \
        --season 2018-19 \
        --game-id 0021800001

-----------------------
Generate player ratings
-----------------------

~~~~~~
Python
~~~~~~

To generate player ratings for all of your data, run

.. code-block:: python

    from nbaspa.player_ratings.pipeline import gen_pipeline, run_pipeline

    flow = gen_pipeline()
    output = run_pipeline(
        flow=flow,
        data_dir="nba-data",
        output_dir="nba-data",
        filesystem="file"
    )

To restrict to a given season, supply ``Season``

.. code-block:: python
    :emphasize-lines: 6

    output = run_pipeline(
        flow=flow,
        data_dir="nba-data",
        output_dir="nba-data",
        filesystem="file",
        Season="2018-19"
    )

and to restrict to a game, supply ``GameID``

.. code-block:: python
    :emphasize-lines: 6

    output = run_pipeline(
        flow=flow,
        data_dir="nba-data",
        output_dir="nba-data",
        filesystem="file",
        GameID="0021800001"
    )

To remove contextual information like team quality and schedule, (see :doc:`here <notebooks/casestudy>`)
supply ``mode``:

.. code-block:: python

    output = run_pipeline(
        flow=flow,
        data_dir="nba-data",
        output_dir="nba-data",
        filesystem="file",
        GameID="0021800001",
        mode="survival-plus"
    )

.. important::

    You can find the play-by-play impact data at ``<output_dir>/<Season>/pbp-impact/data_<GameID>.csv``.
    The aggregated game-level data can be found at ``<output_dir>/<Season>/game-impact/data_<GameID>/csv``.
    This call will also save a season summary CSV with total and average impact for each player to
    ``<output_dir>/<Season>/impact-summary.csv``, as well as player timeseries data to
    ``<output_dir>/<Season>/impact-timeseries/data_<PlayerID>.csv``.

~~~~~~~~~~~~~~~~~~~~~~
Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

To run game-level player ratings,

.. code-block:: console

    $ nbaspa-rate \
        --data-dir nba-data \
        --output-dir nba-data

The above call will create ratings for all cleaned game data available in ``nba-data``. To restrict
to a season or game, supply ``--season`` or ``--game-id``:

.. code-block:: console

    $ nbaspa-rate \
        --data-dir nba-data \
        --output-dir nba-data \
        --season 2018-19 \
        --game-id 0021800001

To generate ratings that remove contextual information like team quality and schedule , change the ``mode`` parameter

.. code-block:: console

    $ nbaspa-rate \
        --data-dir nba-data \
        --output-dir nba-data \
        --season 2018-19 \
        --game-id 0021800001 \
        --mode survival-plus

--------------
Daily snapshot
--------------

If you want to analyze the data for a single day's worth of games (maybe to prevent a large batch
at the end of the season), you can use the set of ``daily`` CLI endpoints. For Christmas 2018, use

.. code-block:: console

    $ nbaspa-download daily \
        --output-dir nba-data \
        --game-date 2018-12-25
    $ nbaspa-clean daily \
        --data-dir nba-data \
        --output-dir nba-data \
        --game-date 2018-12-25
    $ nbaspa-model daily \
        --data-dir nba-data \
        --output-dir nba-data \
        --model nba-data/models/2021-02-21/lifelines/model.pkl \
        --game-date 2018-12-25
    $ nbaspa-rate \
        --data-dir nba-data \
        --output-dir nba-data \
        --game-date 2018-12-25
    $ nbaspa-rate \
        --data-dir nba-data \
        --output-dir nba-data \
        --game-date 2018-12-25 \
        --mode survival-plus

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Using docker and gcs to push daily updates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    This documentation is adapted from the `Google Cloud SDK <https://github.com/GoogleCloudPlatform/cloud-sdk-docker#usage>`_.

First, pull the ``gcloud`` image

.. code-block:: console

    $ docker pull gcr.io/google.com/cloudsdktool/cloud-sdk:latest

and authenticate ``gcloud`` with service account credentials:

.. code-block:: console

    $ docker run \
        --name gcloud-config \
        gcr.io/google.com/cloudsdktool/cloud-sdk gcloud auth activate-service-account SERVICE_ACCOUNT@DOMAIN.COM --key-file=/path/key.json --project=PROJECT_ID

.. important::

    If you want to authenticate with user credentials, call

    .. code-block:: console

        $ docker run \
            -ti \
            --name gcloud-config \
            gcr.io/google.com/cloudsdktool/cloud-sdk gcloud auth login

Then, build the ``nbaspa`` docker image

.. code-block:: console

    $ docker build --tag nbaspa .

and run the container. We will

* include the authentication container ``gcloud-config`` as a volume,
* update the application default credentials (ADC), and
* mount our local ``nba-data`` directory to the container.

Run the target container with the following script (``snapshot.sh``)

.. code-block:: bash

    DATE=$(date -d "yesterday 13:00" +"%Y-%m-%d")

    nbaspa-download daily --output-dir $DATA_DIR --game-date $DATE
    nbaspa-clean daily --data-dir $DATA_DIR --output-dir $DATA_DIR --game-date $DATE
    nbaspa-model daily --data-dir $DATA_DIR --output-dir $DATA_DIR --model $MODEL_PATH--game-date $DATE
    nbaspa-rate --data-dir $DATA_DIR --output-dir $DATA_DIR --game-date $DATE
    nbaspa-rate --data-dir $DATA_DIR --output-dir $DATA_DIR --game-date $DATE --mode survival-plus

    gsutil -m rsync -r $DATA_DIR $GCS_PATH

.. code-block:: console

    $ docker run \
        --rm \
        --volumes-from gcloud-config \
        --mount type=bind,src=<PATH_TO_LOCAL_DATA_DIRECTORY>,target=/opt \
        -e DATA_DIR=/opt/<PATH_TO_LOCAL_DATA_DIRECTORY> \
        -e MODEL_PATH=/opt/<PATH_TO_MODEL_PKL> \
        -e GCS_PATH=<TARGET_DIRECTORY> \
        nbaspa snapshot.sh

for example, if you're using docker on Windows Subsystem for Linux and the ``nba-data`` directory
exists in your local branch of ``nbaspa``.

.. code-block:: console

    $ docker run \
        --rm \
        --volumes-from gcloud-config \
        --mount type=bind,src=/mnt/c/Users/UserName/Documents/GitHub/nbaspa,target=/opt \
        -e DATA_DIR=/opt/nba-data \
        -e MODEL_PATH=/opt/nba-data/models/2021-02-21/lifelines/model.pkl \
        -e GCS_PATH=gs://mybucket/nba-data \
        nbaspa snapshot.sh
