"""Gamelog data.

This module creates tasks for retrieving

* team win percentage,
* days since last game, and
* games in last 7 days.
"""

import pandas as pd
from prefect import Task


class AddWinPercentage(Task):
    """Add team win percentage."""
    def run(self, pbp: pd.DataFrame, gamelog: pd.DataFrame) -> pd.DataFrame:
        """Add team win percentage entering the game.

        Adds the following columns:

        * ``HOME_W_PCT``
        * ``VISITOR_W_PCT``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``AddTeamID``.
        gamelog : pd.DataFrame
            The output from ``TeamGameLog.get_data()``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Sort the game logs
        gamelog["GAME_DATE"] = pd.to_datetime(gamelog["GAME_DATE"])
        gamelog.sort_values(by="GAME_DATE", ascending=True, inplace=True)
        # Shift the win percentage by a day and add it to the play by play
        gamelog["PREV_W_PCT"] = gamelog.groupby("Team_ID")["W_PCT"].shift(1)
        # Norm in the NBA data is to use win percentage of 0 with no games
        gamelog["PREV_W_PCT"] = gamelog["PREV_W_PCT"].fillna(0)
        # Add the home team win percentage to the play by play
        pbp["HOME_W_PCT"] = pbp.merge(
            gamelog[["GAME_DATE", "Team_ID", "PREV_W_PCT"]],
            left_on=("GAME_DATE_EST", "HOME_TEAM_ID"),
            right_on=("GAME_DATE", "Team_ID"),
            how="left"
        )["PREV_W_PCT"]
        # Add the visitor team win percentage
        pbp["VISITOR_W_PCT"] = pbp.merge(
            gamelog[["GAME_DATE", "Team_ID", "PREV_W_PCT"]],
            left_on=("GAME_DATE_EST", "VISITOR_TEAM_ID"),
            right_on=("GAME_DATE", "Team_ID"),
            how="left"
        )["PREV_W_PCT"]

        return pbp
