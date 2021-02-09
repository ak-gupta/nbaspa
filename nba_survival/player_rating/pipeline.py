"""Create a player rating pipeline."""

from typing import Optional, Tuple

from prefect import case, Flow, Parameter
from prefect.tasks.control_flow import merge

import pandas as pd

from nba_survival.player_rating.tasks import (
    AddWinProbability,
    AggregateImpact,
    BoxScoreLoader,
    CompoundPlayerImpact,
    ConvertNBAWinProbability,
    ConvertSurvivalWinProbability,
    LoadRatingData,
    SimplePlayerImpact,
    WinProbabilityLoader,
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
    winprob_loader = WinProbabilityLoader(name="Load NBA win probability loader")
    box_loader = BoxScoreLoader(name="Load boxscore data")
    # Calculation tasks
    convertwinprob = ConvertNBAWinProbability(name="Convert NBA win probability")
    convertsurvprob = ConvertSurvivalWinProbability(name="Convert survival win probability")
    addwin = AddWinProbability(name="Add win probability")
    addsimpleimpact = SimplePlayerImpact(name="Calculate simple player impact")
    compoundimpact = CompoundPlayerImpact(name="Calculate sequence player impact")
    combineimpact = AggregateImpact(name="Aggregate player impact")

    with Flow(name="Calculate player impact") as flow:
        # Parameter
        mode = Parameter("Win Probability Mode", "nba")
        game_id = Parameter("GameID", "default")
        output_dir = Parameter("output_dir", "nba-data")
        filesystem = Parameter("filesystem", "file")
        # Load data
        pbp = pbp_loader(
            GameID=game_id, output_dir=output_dir, filesystem=filesystem
        )
        box = box_loader(
            GameID=game_id, output_dir=output_dir, filesystem=filesystem,
        )
        with case(mode, "nba"):
            win_prob = winprob_loader(
                GameID=game_id, output_dir=output_dir, filesystem=filesystem
            )
            nbawinprob = convertwinprob(win_prob=win_prob)
        with case(mode, "survival"):
            survivalprob = convertsurvprob(win_prob=win_prob)
        winprob = merge(nbawinprob, survivalprob)
        win = addwin(pbp=pbp, win_prob=winprob)
        calculatesimple = addsimpleimpact(pbp=win)
        sequence = compoundimpact(pbp=calculatesimple)
        combineimpact(pbp=sequence, boxscore=box)
    
    return flow


def run_pipeline(
    flow: Flow,
    output_dir: str,
    GameID: str,
    filesystem: Optional[str] = "file",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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
    pd.DataFrame
        The play-by-play dataset.
    pd.DataFrame
        The player-level boxscore.
    pd.DataFrame
        The aggregated player impact scores.
    """
    output = flow.run(
        parameters={
            "output_dir": output_dir,
            "GameID": GameID,
            "filesystem": filesystem,
        }
    )
    pbp = output.result[flow.get_tasks(name="Calculate sequence player impact")[0]].result
    box = output.result[flow.get_tasks(name="Load boxscore data")[0]].result
    agg = output.result[flow.get_tasks(name="Aggregate player impact")[0]].result

    return pbp, box, agg
