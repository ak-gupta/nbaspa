"""Data pipeline.


Create a function that generates a prefect flow.
"""

from typing import List

import pandas as pd
from prefect import Flow

from nba_survival.data.tasks import (
    get_survival_time,
    fill_margin,
    create_target,
    get_team_id,
    get_net_rating,
    get_last_meeting_result,
    get_win_percentage,
    select_features
)

def generate_pipeline(
    pbp: pd.DataFrame,
    header: pd.DataFrame,
    stats: pd.DataFrame,
    last_meeting: pd.DataFrame,
    east_standings: pd.DataFrame,
    west_standings: pd.DataFrame,
    features: List[str] = [
        "GAME_ID",
        "TIME",
        "WIN",
        "SCOREMARGIN",
        "HOME_NET_RATING",
        "VISITOR_NET_RATING",
        "LAST_GAME_WIN",
        "HOME_W_PCT",
        "VISITOR_W_PCT",
    ]
) -> Flow:
    """Generate a data pipeline.

    Parameters
    ----------
    pbp : pd.DataFrame
        The output from ``PlayByPlay.get_data()``.
    header : pd.DataFrame
        The output from ``Scoreboard.get_data("GameHeader")``.
    stats : pd.DataFrame
        The output from ``TeamStats.get_data()``
    last_meeting : pd.DataFrame
        The output from ``Scoreboard.get_data("LastMeeting")``.
    east_standings : pd.DataFrame
        The output from ``Scoreboard.get_data("EastConfStandingsByDay")``.
    west_standings : pd.DataFrame
        The output from ``Scoreboard.get_data("WestConfStandingsByDay")``.
    
    Returns
    -------
    Flow
        The generated flow
    """
    with Flow("NBA Survival Data Pipeline") as flow:
        stime = get_survival_time(pbp=pbp)
        margin = fill_margin(pbp=stime)
        target = create_target(pbp=margin)
        team_id = get_team_id(pbp=target, header=header)
        rating = get_net_rating(pbp=team_id, stats=stats)
        last = get_last_meeting_result(
            pbp=rating, last_meeting=last_meeting
        )
        wperc = get_win_percentage(
            pbp=last, east_standings=east_standings, west_standings=west_standings
        )
        final = select_features(df=wperc, features=features)
    
    return flow
