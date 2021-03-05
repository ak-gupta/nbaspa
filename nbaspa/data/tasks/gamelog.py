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

    def run(self, pbp: pd.DataFrame, gamelog: pd.DataFrame) -> pd.DataFrame:  # type: ignore
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
            how="left",
        )["PREV_W_PCT"]
        # Add the visitor team win percentage
        pbp["VISITOR_W_PCT"] = pbp.merge(
            gamelog[["GAME_DATE", "Team_ID", "PREV_W_PCT"]],
            left_on=("GAME_DATE_EST", "VISITOR_TEAM_ID"),
            right_on=("GAME_DATE", "Team_ID"),
            how="left",
        )["PREV_W_PCT"]

        return pbp


class GamesInLastXDays(Task):
    """Add the number of games in the last X days.

    Parameters
    ----------
    period : int
        The number of days to consider.
    **kwargs
        Keyword arguments for ``prefect.Task``

    Attributes
    ----------
    period : int
        The number of days to consider.
    """

    def __init__(self, period: int, **kwargs):
        """Init method."""
        self.period = period

        super().__init__(**kwargs)

    def run(self, pbp: pd.DataFrame, gamelog: pd.DataFrame) -> pd.DataFrame:  # type: ignore
        """Add the number of games in the last ``self.period`` days.

        Adds the following columns:

        * ``HOME_GAMES_IN_LAST_{self.period}_DAYS``
        * ``VISITOR_GAMES_IN_LAST_{self.period}_DAYS``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output of ``AddTeamID``.
        gamelog : pd.DataFrame
            The output of ``TeamGameLog.get_data()``.

        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Convert the ``GAME_DATE`` to a datetime
        gamelog["GAME_DATE"] = pd.to_datetime(gamelog["GAME_DATE"])
        # Get the rolling count
        rolling = (
            gamelog.set_index("GAME_DATE")
            .assign(count=1)
            .groupby("Team_ID")["count"]
            .rolling(f"{self.period + 1}D")
            .sum()
            - 1
        )
        # Add the rolling sum back to the PBP dataset
        pbp[f"HOME_GAMES_IN_LAST_{self.period}_DAYS"] = pbp.merge(
            rolling,
            left_on=("GAME_DATE_EST", "HOME_TEAM_ID"),
            right_on=("GAME_DATE", "Team_ID"),
            how="left",
        )["count"]
        pbp[f"VISITOR_GAMES_IN_LAST_{self.period}_DAYS"] = pbp.merge(
            rolling,
            left_on=("GAME_DATE_EST", "VISITOR_TEAM_ID"),
            right_on=("GAME_DATE", "Team_ID"),
            how="left",
        )["count"]

        return pbp
