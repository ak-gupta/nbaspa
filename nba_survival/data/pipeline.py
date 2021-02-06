"""Core data pipeline."""

from typing import Optional

import pandas as pd
from prefect import case, Flow, Parameter

from nba_survival.data.tasks import (
    AddWinPercentage,
    GenericLoader,
    PlayByPlayLoader,
    GameLogLoader,
    LineupLoader,
    RotationLoader,
    ShotChartLoader,
    BoxScoreLoader,
    ShotZoneLoader,
    SaveData,
    GamesInLastXDays,
    AddLineupPlusMinus,
    FillMargin,
    AddNetRating,
    AddLastMeetingResult,
    AddTeamID,
    AddExpectedShotValue,
    AddShotDetail,
    CreateTarget,
    SurvivalTime
)
from nba_survival.data.endpoints.parameters import DefaultParameters


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
    scoreboard_loader = GenericLoader(
        loader="Scoreboard", name="Load scoreboard data"
    )
    pbp_loader = PlayByPlayLoader(name="Load play-by-play data")
    teamstats_loader = GenericLoader(
        loader="TeamStats", name="Load team estimated metrics"
    )
    log_loader = GameLogLoader(name="Load gamelog data")
    lineup_loader = LineupLoader(name="Load lineup data")
    rota_loader = RotationLoader(name="Load rotation data")
    shotchart_loader = ShotChartLoader(name="Load shotchart data")
    box_loader = BoxScoreLoader(name="Load boxscore data")
    shotzone_loader = ShotZoneLoader(name="Load player-level shot zone dashboards")
    # Transformation tasks
    survtime_task = SurvivalTime(name="Add survival time")
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
    # Add shotchart data for player rating
    shotdetail = AddShotDetail(name="Add shotchart zone")
    shotvalue = AddExpectedShotValue(name="Add shot value")
    # Persisting clean data
    persist = SaveData()

    with Flow(name="Transform raw NBA data") as flow:
        # Set some parameters
        output_dir = Parameter("output_dir", "nba-data")
        filesystem = Parameter("filesystem", "file")
        season = Parameter("Season", DefaultParameters.Season)
        gamedate = Parameter("GameDate", DefaultParameters.GameDate)
        save_data = Parameter("save_data", True)
        # Load data
        scoreboard = scoreboard_loader(
            output_dir=output_dir,
            filesystem=filesystem,
            dataset_type=None,
            GameDate=gamedate
        )
        pbp = pbp_loader(
            header=scoreboard["GameHeader"],
            output_dir=output_dir,
            filesystem=filesystem,
        )
        stats = teamstats_loader(
            output_dir=output_dir,
            filesystem=filesystem,
            Season=season,
        )
        gamelog = log_loader(
            season=season,
            output_dir=output_dir,
            filesystem=filesystem,
        )
        lineup_stats = lineup_loader(
            season=season,
            output_dir=output_dir,
            filesystem=filesystem,
        )
        rotation = rota_loader(
            header=scoreboard["GameHeader"],
            output_dir=output_dir,
            filesystem=filesystem,
        )
        shotchart = shotchart_loader(
            header=scoreboard["GameHeader"],
            season=season,
            output_dir=output_dir,
            filesystem=filesystem,
        )
        boxscore = box_loader(
            header=scoreboard["GameHeader"],
            output_dir=output_dir,
            filesystem=filesystem
        )
        shotzonedashboard = shotzone_loader(
            boxscore=boxscore,
            output_dir=output_dir,
            filesystem=filesystem
        )
        # Transform data
        survtime = survtime_task(pbp=pbp)
        margin = margin_task(pbp=survtime)
        target = target_task(pbp=margin)
        team_id = team_id_task(pbp=target, header=scoreboard["GameHeader"])
        rating = rating_task(pbp=team_id, stats=stats["default"])
        meeting = meeting_task(pbp=rating, last_meeting=scoreboard["LastMeeting"])
        w_pct = w_pct_task(pbp=meeting, gamelog=gamelog)
        last3 = last3_task(pbp=w_pct, gamelog=gamelog)
        last5 = last5_task(pbp=last3, gamelog=gamelog)
        last7 = last7_task(pbp=last5, gamelog=gamelog)
        lineup = lineup_task(
            pbp=last7,
            lineup_stats=lineup_stats,
            home_rotation=rotation["HomeTeam"],
            away_rotation=rotation["AwayTeam"]
        )
        # Add variables for the player rating
        shotzone = shotdetail(pbp=lineup, shotchart=shotchart)
        expected_val = shotvalue(pbp=shotzone, shotzonedashboard=shotzonedashboard)
        with case(save_data, True):
            persist(data=expected_val, output_dir=output_dir, filesystem=filesystem)
    
    return flow


def run_pipeline(
    flow: Flow,
    output_dir: str,
    save_data: bool = True,
    filesystem: Optional[str] = "file",
    Season: Optional[str] = None,
    GameDate: Optional[str] = None
) -> pd.DataFrame:
    """Run the pipeline.

    Parameters
    ----------
    output_dir : str
        The directory containing the data.
    filesystem : str, optional (default "file")
        The name of the ``fsspec`` filesystem to use.
    save_data : bool, optional (default True)
        Whether or not to save the output data.
    Season : str, optional (default None)
        The ``Season`` value to use.
    GameDate : str, optional (default None)
        The ``GameDate`` value to use, in MM/DD/YYYY format.
    
    Returns
    -------
    None
    """
    params = {
        "output_dir": output_dir,
        "filesystem": filesystem,
        "save_data": save_data
    }
    if Season is not None:
        params["Season"] = Season
    if GameDate is not None:
        params["GameDate"] = GameDate
    
    output = flow.run(parameters=params)
    final = output.result[flow.get_tasks(name="Add shot value")[0]].result

    return final
