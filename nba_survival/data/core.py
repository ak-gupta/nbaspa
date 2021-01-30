"""Core data pipeline."""

import pandas as pd
from prefect import Flow

from nba_survival.data.pipeline import (
    AddLineupPlusMinus,
    FillMargin,
    AddNetRating,
    AddLastMeetingResult,
    AddTeamID,
    AddWinPercentage,
    CreateTarget,
    SurvivalTime
)

def gen_pipeline(
    pbp: pd.DataFrame,
    header: pd.DataFrame,
    stats: pd.DataFrame,
    last_meeting: pd.DataFrame,
    gamelog: pd.DataFrame,
    lineup_stats: pd.DataFrame,
    home_rotation: pd.DataFrame,
    away_rotation: pd.DataFrame,
) -> Flow:
    """Generate the prefect flow.

    Parameters
    ----------
    pbp : pd.DataFrame
        The output from ``PlayByPlay.get_data()``.
    header : pd.DataFrame
        The output from ``Scoreboard.get_data("GameHeader")``.
    stats : pd.DataFrame
        The output from ``TeamStats.get_data()``.
    last_meeting : pd.DataFrame
        The output from ``Scoreboard.get_data("LastMeeting")``.
    gamelog : pd.DataFrame
        The output from ``TeamGameLog.get_data()``.
    lineup_stats : pd.DataFrame
        The output from ``TeamLineups.get_data("Lineups")``.
    home_rotation : pd.DataFrame
        The output from ``GameRotation.get_data("HomeTeam")``.
    away_rotation : pd.DataFrame
        The output from ``GameRotation.get_data("AwayTeam")``.

    Returns
    -------
    Flow
        The generated flow.
    """
    # Initialize the tasks
    survtime_task = SurvivalTime(name="Add surival time")
    margin_task = FillMargin(name="Backfill margin")
    target_task = CreateTarget(name="Add target label")
    team_id_task = AddTeamID(name="Add team ID and game date")
    rating_task = AddNetRating(name="Add net rating")
    meeting_task = AddLastMeetingResult(name="Add last meeting result")
    w_pct_task = AddWinPercentage(name="Add last meeting result")
    lineup_task = AddLineupPlusMinus(name="Add lineup plus minus")

    with Flow(name="Transform raw NBA data") as flow:
        survtime = survtime_task(pbp=pbp)
        margin = margin_task(pbp=survtime)
        target = target_task(pbp=margin)
        team_id = team_id_task(pbp=target, header=header)
        rating = rating_task(pbp=team_id, stats=stats)
        meeting = meeting_task(pbp=rating, last_meeting=last_meeting)
        w_pct = w_pct_task(pbp=meeting, gamelog=gamelog)
        lineup = lineup_task(pbp=w_pct, lineup_stats=lineup_stats, home_rotation=home_rotation, away_rotation=away_rotation)
    
    return flow
