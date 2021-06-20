"""Create a player rating pipeline."""

from typing import Optional

from prefect import Flow, Parameter, unmapped
from prefect.engine.state import State
from prefect.executors import LocalDaskExecutor

from .tasks import (
    AggregateImpact,
    BoxScoreLoader,
    CompoundPlayerImpact,
    GetGamesList,
    LoadRatingData,
    ScoreboardLoader,
    LoadSurvivalPredictions,
    AddSurvivalProbability,
    SimplePlayerImpact,
    SaveImpactData,
    SavePlayerTimeSeries,
    SaveTopPlayers,
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
    games = GetGamesList(name="Get games list")
    pbp_loader = LoadRatingData(name="Load clean data")
    box_loader = BoxScoreLoader(name="Load boxscore data")
    surv_loader = LoadSurvivalPredictions(name="Load survival predictions")
    score_loader = ScoreboardLoader(name="Load header data")
    # Calculation tasks
    addsurv = AddSurvivalProbability(name="Join survival probability")
    addsimpleimpact = SimplePlayerImpact(name="Calculate simple player impact")
    compoundimpact = CompoundPlayerImpact(name="Calculate sequence player impact")
    combineimpact = AggregateImpact(name="Aggregate player impact")
    # Persist
    savesimple = SaveImpactData(name="Save play-by-play impact data", pbp=True)
    saveagg = SaveImpactData(name="Save aggregated impact data", pbp=False)
    savetime = SavePlayerTimeSeries(name="Save player timeseries")
    savesummary = SaveTopPlayers(name="Save season summary")

    with Flow(name="Calculate player impact") as flow:
        # Parameters
        data_dir = Parameter("data_dir", "nba-data")
        output_dir = Parameter("output_dir", "nba-data")
        filesystem = Parameter("filesystem", "file")
        mode = Parameter("mode", "survival")
        season = Parameter("Season", None)
        gameid = Parameter("GameID", None)
        # Load data
        gamelist = games(
            data_dir=data_dir,
            Season=season,
            GameID=gameid,
        )
        header = score_loader(data_dir=data_dir, filelist=gamelist)
        pbp = pbp_loader.map(data_dir=unmapped(data_dir), filelocation=gamelist)
        survprob = surv_loader.map(data_dir=unmapped(data_dir), filelocation=gamelist)
        box = box_loader.map(filelocation=gamelist, output_dir=unmapped(data_dir))
        # Add the survival probability and calculate impact
        pbpfinal = addsurv.map(pbp=pbp, survprob=survprob)
        calculatesimple = addsimpleimpact.map(pbp=pbpfinal, mode=unmapped(mode))
        sequence = compoundimpact.map(pbp=calculatesimple, mode=unmapped(mode))
        agg = combineimpact.map(pbp=sequence, boxscore=box)
        # Save data
        _ = savesimple.map(
            data=sequence,
            output_dir=unmapped(output_dir),
            filesystem=unmapped(filesystem),
            filelocation=gamelist,
        )
        _ = saveagg.map(
            data=agg,
            output_dir=unmapped(output_dir),
            filesystem=unmapped(filesystem),
            filelocation=gamelist,
        )
        _ = savetime(
            data=agg, header=header, output_dir=output_dir, filesystem=filesystem
        )
        _ = savesummary(data=agg, output_dir=output_dir)

    return flow


def run_pipeline(
    flow: Flow, data_dir: str, output_dir: str, **kwargs
) -> Optional[State]:
    """Run the pipeline.

    Parameters
    ----------
    flow : Flow
        The generated flow.
    data_dir : str
        The directory containing the data.
    output_dir : str
        The output location for the data.
    **kwargs
        Additional parameters

    Returns
    -------
    State
        The output of ``flow.run``.
    """
    output = flow.run(
        parameters={"data_dir": data_dir, "output_dir": output_dir, **kwargs},
        executor=LocalDaskExecutor(scheduler="processes"),
    )

    return output
