"""Core data pipeline."""

from typing import Optional

from prefect import case, Flow, Parameter
from prefect.engine.state import State
from prefect.tasks.control_flow import merge

from .tasks import (
    AddWinPercentage,
    GenericLoader,
    FactoryGetter,
    PlayByPlayLoader,
    WinProbabilityLoader,
    GameLogLoader,
    LineupLoader,
    RotationLoader,
    ShotChartLoader,
    BoxScoreLoader,
    ShotZoneLoader,
    GeneralShootingLoader,
    SaveData,
    GamesInLastXDays,
    AddLineupPlusMinus,
    FillMargin,
    AddNBAWinProbability,
    AddNetRating,
    AddLastMeetingResult,
    AddTeamID,
    AddExpectedShotValue,
    AddShotDetail,
    CreateTarget,
    DeDupeTime,
    SurvivalTime,
)
from .endpoints.parameters import DefaultParameters


def gen_pipeline() -> Flow:
    """Generate the prefect flow.

    Returns
    -------
    Flow
        The generated flow.
    """
    # Initialize the tasks
    # Loader tasks
    scoreboard_loader = GenericLoader(loader="Scoreboard", name="Load scoreboard data")
    pbp_loader = PlayByPlayLoader(name="Load play-by-play data")
    wprob_loader = WinProbabilityLoader(name="Load NBA win probability")
    getter = FactoryGetter(name="Get dataset from the Factory")
    log_loader = GameLogLoader(name="Load gamelog data")
    lineup_loader = LineupLoader(name="Load lineup data")
    rota_loader = RotationLoader(name="Load rotation data")
    shotchart_loader = ShotChartLoader(name="Load shotchart data")
    box_loader = BoxScoreLoader(name="Load boxscore data")
    shotzone_loader = ShotZoneLoader(name="Load player-level shot zone dashboards")
    gshooting_loader = GeneralShootingLoader(
        name="Load player-level overall shooting dashboards"
    )
    # Transformation tasks
    survtime_task = SurvivalTime(name="Add survival time")
    wprob_task = AddNBAWinProbability(name="Add NBA win probability")
    margin_task = FillMargin(name="Backfill margin")
    target_task = CreateTarget(name="Add target label")
    team_id_task = AddTeamID(name="Add team ID and game date")
    rating_task = AddNetRating(name="Add net rating")
    meeting_task = AddLastMeetingResult(name="Add last meeting result")
    w_pct_task = AddWinPercentage(name="Add win percentage")
    last3_task = GamesInLastXDays(period=3, name="Games in last 3 days")
    last5_task = GamesInLastXDays(period=5, name="Games in last 5 days")
    last7_task = GamesInLastXDays(period=7, name="Games in last 7 days")
    lineup_task = AddLineupPlusMinus(name="Add lineup plus minus")
    dedupe_task = DeDupeTime(name="De-dupe time")
    # Add shotchart data for player rating
    shotdetail = AddShotDetail(name="Add shotchart zone")
    shotvalue = AddExpectedShotValue(name="Add shot value")
    # Persisting clean data
    persist = SaveData()

    with Flow(name="Transform raw NBA data") as flow:
        # Set some parameters
        data_dir = Parameter("data_dir", "nba-data")
        output_dir = Parameter("output_dir", "nba-data")
        filesystem = Parameter("filesystem", "file")
        season = Parameter("Season", DefaultParameters.Season)
        gamedate = Parameter("GameDate", DefaultParameters.GameDate)
        save_data = Parameter("save_data", True)
        mode = Parameter("mode", "model")
        # Load data
        scoreboard = scoreboard_loader(
            output_dir=data_dir,
            filesystem=filesystem,
            dataset_type=None,
            GameDate=gamedate,
        )
        pbp = pbp_loader(
            header=scoreboard["GameHeader"],
            output_dir=data_dir,
            filesystem=filesystem,
        )
        wprob = wprob_loader(
            header=scoreboard["GameHeader"],
            output_dir=data_dir,
            filesystem=filesystem,
        )
        lineupdata = lineup_loader(
            season=season, GameDate=gamedate, linescore=scoreboard["LineScore"]
        )
        stats = getter(factory=lineupdata, dataset_type="Overall")
        boxscore = box_loader(
            header=scoreboard["GameHeader"],
            output_dir=data_dir,
            filesystem=filesystem,
        )
        # Base transformations
        survtime = survtime_task(pbp=pbp)
        nbawin = wprob_task(pbp=survtime, winprob=wprob)
        margin = margin_task(pbp=nbawin)
        target = target_task(pbp=margin)
        team_id = team_id_task(pbp=target, header=scoreboard["GameHeader"])
        rating = rating_task(pbp=team_id, stats=stats)
        with case(mode, "rating"):  # type: ignore
            # Load shotchart and shot zone data
            shotchart = shotchart_loader(
                header=scoreboard["GameHeader"],
                season=season,
                output_dir=data_dir,
                filesystem=filesystem,
            )
            shotzonedashboard = shotzone_loader(
                boxscore=boxscore,
                season=season,
                GameDate=gamedate,
                output_dir=data_dir,
                filesystem=filesystem
            )
            shooting = gshooting_loader(
                boxscore=boxscore,
                season=season,
                output_dir=output_dir,
                filesystem=filesystem
            )
            # Add variables for the player rating
            shotzone = shotdetail(pbp=rating, shotchart=shotchart)
            expected_val = shotvalue(
                pbp=shotzone,
                shotzonedashboard=shotzonedashboard,
                overallshooting=shooting,
            )
        with case(mode, "model"):  # type: ignore
            # Load data
            gamelog = log_loader(
                season=season,
                output_dir=data_dir,
                filesystem=filesystem,
            )
            lineup_stats = getter(factory=lineupdata, dataset_type="Lineups")
            rotation = rota_loader(
                header=scoreboard["GameHeader"],
                output_dir=data_dir,
                filesystem=filesystem,
            )
            # Transform data for the survival model
            meeting = meeting_task(pbp=rating, last_meeting=scoreboard["LastMeeting"])
            w_pct = w_pct_task(pbp=meeting, gamelog=gamelog)
            last3 = last3_task(pbp=w_pct, gamelog=gamelog)
            last5 = last5_task(pbp=last3, gamelog=gamelog)
            last7 = last7_task(pbp=last5, gamelog=gamelog)
            lineup = lineup_task(
                pbp=last7,
                lineup_stats=lineup_stats,
                home_rotation=rotation["HomeTeam"],
                away_rotation=rotation["AwayTeam"],
            )
            deduped = dedupe_task(pbp=lineup)
        # Save
        final = merge(expected_val, deduped)
        with case(save_data, True):  # type: ignore
            persist(data=final, output_dir=output_dir, filesystem=filesystem, mode=mode)

    return flow


def run_pipeline(
    flow: Flow,
    data_dir: str,
    output_dir: str,
    save_data: bool = True,
    filesystem: Optional[str] = "file",
    mode: Optional[str] = "model",
    Season: Optional[str] = None,
    GameDate: Optional[str] = None,
) -> Optional[State]:
    """Run the pipeline.

    Parameters
    ----------
    data_dir : str
        The directory containing the data.
    output_dir : str
        The output location for the clean data.
    filesystem : str, optional (default "file")
        The name of the ``fsspec`` filesystem to use.
    mode : str, optional (default "model")
        The type of clean data to save. If ``model``, the time will be de-duped
        and the output will be saved to the directory ``model-data``. If ``rating``,
        the time will not be de-duped and the output will be saved to ``rating-data``.
    save_data : bool, optional (default True)
        Whether or not to save the output data.
    Season : str, optional (default None)
        The ``Season`` value to use.
    GameDate : str, optional (default None)
        The ``GameDate`` value to use, in MM/DD/YYYY format.

    Returns
    -------
    State
        The output of ``flow.run``.
    """
    params = {
        "data_dir": data_dir,
        "output_dir": output_dir,
        "filesystem": filesystem,
        "save_data": save_data,
        "mode": mode,
    }
    if Season is not None:
        params["Season"] = Season
    if GameDate is not None:
        params["GameDate"] = GameDate

    output = flow.run(parameters=params)

    return output
