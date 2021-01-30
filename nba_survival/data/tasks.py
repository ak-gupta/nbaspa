"""Data pipeline tasks.

Create tasks for creating the survival analysis data.
"""

import logging
from typing import List

import numpy as np
import pandas as pd
from prefect import task

from nba_survival.data.endpoints.pbp import EventTypes

LOG = logging.getLogger(__name__)

#@task(name="Add survival time")
def get_survival_time(pbp: pd.DataFrame) -> pd.DataFrame:
    """Get the survival time.

    Adds the following column:

    * TIME

    Parameters
    ----------
    pbp : pd.DataFrame
        The output ``pd.DataFrame`` from ``PlayByPlay.get_data()``.
    
    Returns
    -------
    pd.DataFrame
        The original dataset with a new column, ``TIME``.
    """
    # First, split the play clock into minutes and seconds
    pbp_time = pbp["PCTIMESTRING"].str.split(":", expand=True).astype(int)
    # Create the new column
    # First add time for regulation
    pbp.loc[pbp["PERIOD"] <= 4, "TIME"] = ((pbp["PERIOD"] - 1) * 720) + 720 - (pbp_time[0] * 60) - pbp_time[1]
    # Then add for overtime
    pbp.loc[pbp["PERIOD"] > 4, "TIME"] = (4 * 720) + ((pbp["PERIOD"] - 5) * 300) + 720 - (pbp_time[0] * 60) - pbp_time[1]

    return pbp

@task(name="Backfill margin")
def fill_margin(pbp: pd.DataFrame) -> pd.DataFrame:
    """Make sure the margin value is always non-null.

    Parameters
    ----------
    pbp : pd.DataFrame
        The output from ``get_survival_time``
    
    Returns
    -------
    pd.DataFrame
        The original dataframe with a non-null ``SCOREMARGIN`` column.
    """
    # Sort by the ``TIME`` variable
    pbp.sort_values(by="TIME", ascending=True, inplace=True)
    pbp.loc[pbp["SCOREMARGIN"] == "TIE", "SCOREMARGIN"] = 0
    pbp["SCOREMARGIN"] = pbp.groupby("GAME_ID")["SCOREMARGIN"].ffill()
    pbp["SCOREMARGIN"] = pbp["SCOREMARGIN"].fillna(0)
    pbp["SCOREMARGIN"] = pbp["SCOREMARGIN"].astype(int)

    return pbp

@task(name="Add target label")
def create_target(pbp: pd.DataFrame) -> pd.DataFrame:
    """Create the target boolean.

    Adds the following column:

    * WIN

    Parameters
    ----------
    pbp : pd.DataFrame
        The output from ``fill_margin``.
    
    Returns
    -------
    pd.DataFrame
        The updated DataFrame.
    """
    pbp.sort_values(by="TIME", ascending=True, inplace=True)
    pbp["WIN"] = pbp.groupby("GAME_ID").tail(1)["SCOREMARGIN"] > 0
    pbp["WIN"] = pbp["WIN"].fillna(False)
    pbp["WIN"] = pbp["WIN"].astype(int)

    return pbp

@task(name="Add Team ID and game date")
def get_team_id(
    pbp: pd.DataFrame,
    header: pd.DataFrame,
) -> pd.DataFrame:
    """Add the home and visitor team ID to the play by play data.

    Adds the following columns:

    * HOME_TEAM_ID
    * VISITOR_TEAM_ID
    * GAME_DATE_EST

    Parameters
    ----------
    pbp : pd.DataFrame
        The output of ``PlayByPlay.get_data()``.
    header : pd.DataFrame
        The output of ``Scoreboard.get_data("GameHeader")``.
    
    Returns
    -------
    pd.DataFrame
        The output DataFrame with new columns.
    """
    pbp = pbp.merge(
        header[["GAME_ID", "GAME_DATE_EST", "HOME_TEAM_ID", "VISITOR_TEAM_ID"]],
        on="GAME_ID",
        how="left"
    )
    pbp["GAME_DATE_EST"] = pd.to_datetime(pbp["GAME_DATE_EST"])

    return pbp

@task(name="Add net rating")
def get_net_rating(
    pbp: pd.DataFrame,
    stats: pd.DataFrame
) -> pd.DataFrame:
    """Add the net rating for each team.

    This function will add the following data to the PlayByPlay data:

    * HOME_NET_RATING
    * VISITOR_NET_RATING

    Parameters
    ----------
    pbp : pd.DataFrame
        The output ``pd.DataFrame`` from ``get_team_id``.
    stats : pd.DataFrame
        The output ``pd.DataFrame`` from ``TeamStats.get_data()``.
    
    Returns
    -------
    pd.DataFrame
        A new dataframe with the net rating for each team.
    """
    pbp["HOME_NET_RATING"] = pbp.merge(
        stats[["TEAM_ID", "E_NET_RATING"]],
        left_on="HOME_TEAM_ID",
        right_on="TEAM_ID",
        how="left"
    )["E_NET_RATING"]
    pbp["VISITOR_NET_RATING"] = pbp.merge(
        stats[["TEAM_ID", "E_NET_RATING"]],
        left_on="VISITOR_TEAM_ID",
        right_on="TEAM_ID",
        how="left"
    )["E_NET_RATING"]

    return pbp

@task(name="Add last meeting result")
def get_last_meeting_result(
    pbp: pd.DataFrame,
    last_meeting: pd.DataFrame,
) -> pd.DataFrame:
    """Add an indicator to show who won the last meeting.

    Adds the following column:

    * LAST_GAME_WIN

    Parameters
    ----------
    pbp : pd.DataFrame
        The output ``pd.DataFrame`` from ``get_team_id``.
    last_meeting : pd.DataFrame
        The output ``pd.DataFrame`` from ``Scoreboard.get_data("LastMeeting")``.
    
    Returns
    -------
    pd.DataFrame
        The updated DataFrame.
    """
    # Assign a new variable with the winning team ID from the last meeting
    last_meeting.loc[
        last_meeting["LAST_GAME_HOME_TEAM_POINTS"] > last_meeting["LAST_GAME_VISITOR_TEAM_POINTS"],
        "LAST_GAME_TEAM_ID"
    ] = last_meeting["LAST_GAME_HOME_TEAM_ID"]
    last_meeting.loc[
        last_meeting["LAST_GAME_HOME_TEAM_POINTS"] < last_meeting["LAST_GAME_VISITOR_TEAM_POINTS"],
        "LAST_GAME_TEAM_ID"
    ] = last_meeting["LAST_GAME_VISITOR_TEAM_ID"]
    last_meeting["LAST_GAME_TEAM_ID"] = last_meeting["LAST_GAME_TEAM_ID"].astype(int)
    # Merge with the pbp dataframe
    pbp = pbp.merge(
        last_meeting[["GAME_ID", "LAST_GAME_TEAM_ID"]], on="GAME_ID", how="left"
    )
    pbp.loc[pbp["HOME_TEAM_ID"] == pbp["LAST_GAME_TEAM_ID"], "LAST_GAME_WIN"] = 1
    pbp["LAST_GAME_WIN"] = pbp["LAST_GAME_WIN"].fillna(0)
    pbp["LAST_GAME_WIN"] = pbp["LAST_GAME_WIN"].astype(int)
    # Drop the extra column
    pbp.drop(columns="LAST_GAME_TEAM_ID", inplace=True)

    return pbp


@task(name="Add current win percentage")
def get_win_percentage(
    pbp: pd.DataFrame,
    east_standings: pd.DataFrame,
    west_standings: pd.DataFrame
) -> pd.DataFrame:
    """Get each team's win percentage entering the game.

    Adds the following columns:

    * HOME_W_PCT
    * VISITOR_W_PCT

    Parameters
    ----------
    pbp : pd.DataFrame
        The output ``pd.DataFrame`` from ``get_team_id``.
    east_standings : pd.DataFrame
        The output from ``Scoreboard.get_data("EastConfStandingsByDay")``.
    west_standings : pd.DataFrame
        The output from ``Scoreboard.get_data("WestConfStandingsbyDay")``.
    
    Returns
    -------
    pd.DataFrame
        The updated DataFrame.
    """
    # Concatenate and sort
    standings = pd.concat([east_standings, west_standings]).reset_index(drop=True)
    standings["STANDINGSDATE"] = pd.to_datetime(standings["STANDINGSDATE"])
    standings.sort_values(by="STANDINGSDATE", ascending=True, inplace=True)
    # Add a previous win percentage column to the standings
    standings["PREV_W_PCT"] = standings.groupby("TEAM_ID")["W_PCT"].shift(1)
    # The norm in the NBA data is to have a win percentage of 0 with no games
    standings["PREV_W_PCT"] = standings["PREV_W_PCT"].fillna(0)
    # Now, add the home team win percentage to the play by play data
    pbp["HOME_W_PCT"] = pbp.merge(
        standings[["STANDINGSDATE", "TEAM_ID", "PREV_W_PCT"]],
        left_on=("GAME_DATE_EST", "HOME_TEAM_ID"),
        right_on=("STANDINGSDATE", "TEAM_ID"),
        how="left"
    )["PREV_W_PCT"]
    # Add the visitor team win percentage
    pbp["VISITOR_W_PCT"] = pbp.merge(
        standings[["STANDINGSDATE", "TEAM_ID", "PREV_W_PCT"]],
        left_on=("GAME_DATE_EST", "VISITOR_TEAM_ID"),
        right_on=("STANDINGSDATE", "TEAM_ID"),
        how="left"
    )["PREV_W_PCT"]

    return pbp


def get_lineup_rating(
    pbp: pd.DataFrame,
    lineup: pd.DataFrame,
    home_rotation: pd.DataFrame,
    away_rotation: pd.DataFrame
) -> pd.DataFrame:
    """Get the lineup net rating.

    Adds the following columns:

    * HOME_LINEUP_PLUS_MINUS
    * VISITOR_LINEUP_PLUS_MINUS

    Parameters
    ----------
    pbp : pd.DataFrame
        The output ``pd.DataFrame`` from ``get_survival_time``.
    lineup : pd.DataFrame
        The output ``pd.DataFrame` from ``TeamLineups.get_data("Lineups")``.
    home_rotation : pd.DataFrame
        The output ``pd.DataFrame`` from ``GameRotation.get_data("HomeTeam")``.
    away_rotation : pd.DataFrame
        The output ``pd.DataFrame`` from ``GameRotation.get_data("AwayTeam")``.
    
    Returns
    -------
    pd.DataFrame
        The updated DataFrame
    """
    # Split and reorder the group id column
    split_id = lineup["GROUP_ID"].str.split("-").str[1:6]
    split_id = split_id.apply(sorted)
    lineup["GROUP_ID"] = split_id.str.join("-")
    # Loop through each game in the play by play dataset
    pbp["HOME_LINEUP_PLUS_MINUS"] = np.nan
    pbp["VISITOR_LINEUP_PLUS_MINUS"] = np.nan
    pbp["EVENTMSGTYPE"] = pbp["EVENTMSGTYPE"].astype(int)
    grouped = pbp.groupby("GAME_ID")
    for name, game in grouped:
        # Establish the starting lineup for each team
        LOG.info(f"Adding starting lineup plus minus for {name}")
        home_lineup = set(
            home_rotation.loc[
                (home_rotation["IN_TIME_REAL"] == 0) & (home_rotation["GAME_ID"] == name),
                "PERSON_ID"
            ].values.tolist()
        )
        away_lineup = set(
            away_rotation.loc[
                (away_rotation["IN_TIME_REAL"] == 0) & (away_rotation["GAME_ID"] == name),
                "PERSON_ID"
            ].values.tolist()
        )
        # Add the starting lineup data
        homestr = "-".join(sorted(str(item) for item in home_lineup))
        awaystr = "-".join(sorted(str(item) for item in away_lineup))
        pbp.loc[pbp.index == game.index.min(), "HOME_LINEUP_PLUS_MINUS"] = lineup.loc[
            lineup["GROUP_ID"] == homestr, "PLUS_MINUS"
        ]
        pbp.loc[pbp.index == game.index.min(), "VISITOR_LINEUP_PLUS_MINUS"] = lineup.loc[
            lineup["GROUP_ID"] == awaystr, "PLUS_MINUS"
        ]
        # Loop through each event in the game
        LOG.info(f"Looping through each event in game {name}")
        for index, row in game.iterrows():
            if row["EVENTMSGTYPE"] == EventTypes().SUBSTITUTION:
                if not pd.isnull(row["HOMEDESCRIPTION"]):
                    LOG.info(
                        f"At {row['PCTIMESTRING']} in period {row['PERIOD']}: {row['HOMEDESCRIPTION']}"
                    )
                    # Remove PLAYER1_ID and add PLAYER2_ID to the lineup
                    LOG.debug(f"Removing {row['PLAYER1_ID']}")
                    home_lineup.remove(row["PLAYER1_ID"])
                    LOG.debug(f"Adding {row['PLAYER2_ID']}")
                    home_lineup.add(row["PLAYER2_ID"])
                    homestr = "-".join(sorted(str(item) for item in home_lineup))
                    pbp.loc[index, "HOME_LINEUP_PLUS_MINUS"] = 0
                    if not lineup.loc[lineup["GROUP_ID"] == homestr].empty:
                        pbp.loc[index, "HOME_LINEUP_PLUS_MINUS"] = lineup.loc[
                            lineup["GROUP_ID"] == homestr, "PLUS_MINUS"
                        ]
                else:
                    LOG.info(
                        f"At {row['PCTIMESTRING']} in period {row['PERIOD']}: {row['VISITORDESCRIPTION']}"
                    )
                    # Remove PLAYER1_ID and add PLAYER2_ID  to the lineup
                    LOG.debug(f"Removing {row['PLAYER1_ID']}")
                    away_lineup.remove(row["PLAYER1_ID"])
                    LOG.debug(f"Adding {row['PLAYER2_ID']}")
                    away_lineup.add(row["PLAYER2_ID"])
                    awaystr = "-".join(sorted(str(item) for item in away_lineup))
                    pbp.loc[index, "VISITOR_LINEUP_PLUS_MINUS"] = 0
                    if not lineup.loc[lineup["GROUP_ID"] == awaystr].empty:
                        pbp.loc[index, "VISITOR_LINEUP_PLUS_MINUS"] = lineup.loc[
                            lineup["GROUP_ID"] == awaystr, "PLUS_MINUS"
                        ]
            elif row["EVENTMSGTYPE"] == EventTypes().PERIOD_BEGIN:
                # Look in the home and visitor rotations for substitutions
                LOG.info(f"Looking for substitutions at the beginning of {row['PERIOD']}...")
                new_home = home_rotation.loc[
                    (home_rotation["GAME_ID"] == name) & (home_rotation["IN_TIME_REAL"] == 10 * row["TIME"])
                ]
                new_visitor = home_rotation.loc[
                    (away_rotation["GAME_ID"] == name) & (away_rotation["IN_TIME_REAL"] == 10 * row["TIME"])
                ]
                # at this time
                if not new_home.empty:
                    LOG.info(f"New home team players at the start of period {row['PERIOD']}")
                    # Look for players that left at this time
                    home_lineup = home_lineup.difference(
                        set(
                            home_rotation.loc[
                                (home_rotation["GAME_ID"] == name) & (home_rotation["OUT_TIME_REAL"] == 10 * row["TIME"]),
                                "PERSON_ID"
                            ].values.tolist()
                        )
                    )
                    home_lineup.update(new_home["PERSON_ID"].values.tolist())
                    homestr = "-".join(sorted(str(item) for item in home_lineup))
                    if not lineup.loc[lineup["GROUP_ID"] == homestr].empty:
                        pbp.loc[index, "HOME_LINEUP_PLUS_MINUS"] = lineup.loc[
                            lineup["GROUP_ID"] == homestr, "PLUS_MINUS"
                        ]
                if not new_visitor.empty:
                    LOG.info(f"New visiting team  players at the start of period {row['PERIOD']}")
                    # Look for players that left at this time
                    away_lineup = away_lineup.difference(
                        set(
                            away_rotation.loc[
                                (away_rotation["GAME_ID"] == name) & (away_rotation["OUT_TIME_REAL"] == 10 * row["TIME"]),
                                "PERSON_ID"
                            ].values.tolist()
                        )
                    )
                    away_lineup.update(new_visitor["PERSON_ID"].values.tolist())
                    awaystr = "-".join(sorted(str(item) for item in away_lineup))
                    if not lineup.loc[lineup["GROUP_ID"] == awaystr].empty:
                        pbp.loc[index, "VISITOR_LINEUP_PLUS_MINUS"] = lineup.loc[
                            lineup["GROUP_ID"] == awaystr, "PLUS_MINUS"
                        ]
            else:
                continue
    
    return pbp

@task(name="Select final features")
def select_features(df: pd.DataFrame, features: List[str]) -> pd.DataFrame:
    """Select the final features.

    Parameters
    ----------
    features : list
        The list of features to include.
    
    Returns
    -------
    pd.DataFrame
        The limited dataframe
    """
    return df[features].copy()
