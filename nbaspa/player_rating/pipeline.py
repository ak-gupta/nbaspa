"""Create a player rating pipeline."""

from typing import Optional

from prefect import case, Flow, Parameter
from prefect.engine.state import State
from prefect.tasks.control_flow import merge

import pandas as pd

from .tasks import (
    AggregateImpact,
    BoxScoreLoader,
    CompoundPlayerImpact,
    LoadRatingData,
    SimplePlayerImpact,
)


def gen_pipeline() -> Flow:
    """Generate the prefect flow.

    Parameters
    ----------
    None

    Returns
    -------
    Flow
        The generated flow.
    """
    # Initialize the tasks
    # Loader tasks
    pbp_loader = LoadRatingData(name="Load clean data")
    box_loader = BoxScoreLoader(name="Load boxscore data")
    # Calculation tasks
    addsimpleimpact = SimplePlayerImpact(name="Calculate simple player impact")
    compoundimpact = CompoundPlayerImpact(name="Calculate sequence player impact")
    combineimpact = AggregateImpact(name="Aggregate player impact")

    with Flow(name="Calculate player impact") as flow:
        # Parameter
        game_id = Parameter("GameID", "default")
        output_dir = Parameter("output_dir", "nba-data")
        filesystem = Parameter("filesystem", "file")
        # Load data
        pbp = pbp_loader(GameID=game_id, output_dir=output_dir, filesystem=filesystem)
        box = box_loader(
            GameID=game_id,
            output_dir=output_dir,
            filesystem=filesystem,
        )
        calculatesimple = addsimpleimpact(pbp=pbp)
        sequence = compoundimpact(pbp=calculatesimple)
        combineimpact(pbp=sequence, boxscore=box)

    return flow


def run_pipeline(
    flow: Flow,
    output_dir: str,
    GameID: str,
    filesystem: Optional[str] = "file",
) -> State:
    """Run the pipeline.

    Parameters
    ----------
    flow : Flow
        The generated flow.
    output_dir : str
        The directory containing the data.
    GameID : str
        The game identifier.
    filesystem : str, optional (default "file")
        The name of the ``fsspec`` filesystem to use.

    Returns
    -------
    State
        The output of ``flow.run``.
    """
    output = flow.run(
        parameters={
            "output_dir": output_dir,
            "GameID": GameID,
            "filesystem": filesystem,
        }
    )

    return output
