"""Scoreboard data.

This module creates Prefect tasks for retrieving

* team identifiers,
* game date,
* last meeting result, and
* team win percentage.
"""

import pandas as pd
from prefect import Task

class AddTeamID(Task):
    """Add the team identifiers and game date."""
    def run(self, pbp: pd.DataFrame, header: pd.DataFrame) -> pd.DataFrame:
        """Add the team identifiers and game date.

        Adds the following columns:

        * ``HOME_TEAM_ID``,
        * ``VISITOR_TEAM_ID``, and
        * ``GAME_DATE_EST``.

        Parameters
        ----------
        pbp : pd.DataFrame
            The output of ``PlayByPlay.get_data()``.
        header : pd.DataFrame
            The output of ``Scoreboard.get_data("GameHeader")``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        pbp = pbp.merge(
            header[["GAME_ID", "GAME_DATE_EST", "HOME_TEAM_ID", "VISITOR_TEAM_ID"]],
            on="GAME_ID",
            how="left"
        )
        pbp["GAME_DATE_EST"] = pd.to_datetime(pbp["GAME_DATE_EST"])

        return pbp


class AddLastMeetingResult(Task):
    """Add the last meeting result."""
    def run(self, pbp: pd.DataFrame, last_meeting: pd.DataFrame) -> pd.DataFrame:
        """Add an indicator to show who won the last meeting.

        Adds the following column:

        * ``LAST_GAME_WIN``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``AddTeamID``.
        last_meeting : pd.DataFrame
            The output from ``Scoreboard.get_data("LastMeeting")``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
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


class AddWinPercentage(Task):
    """Add team win percentage."""
    def run(self, pbp: pd.DataFrame, east_standings: pd.DataFrame, west_standings: pd.DataFrame) -> pd.DataFrame:
        """Add team win percentage.

        Adds the following columns:

        * ``HOME_W_PCT``
        * ``VISITOR_W_PCT``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``AddTeamID``.
        east_standings : pd.DataFrame
            The output from ``Scoreboard.get_data("EastConfStandingsByDay")``.
        west_standings : pd.DataFrame
            The output from ``Scoreboard.get_data("WestConfStandingsByDay")``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
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
