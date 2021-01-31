"""Calculate player impact."""

import pandas as pd
from prefect import Task

from nba_survival.data.endpoints.pbp import EventTypes

class PlayerImpact(Task):
    """Add player impact to the data."""
    def run(self, pbp: pd.DataFrame) -> pd.DataFrame:
        """Add player impact to the data.

        Adds the following columns:

        * ``PLAYER1_IMPACT``
        * ``PLAYER2_IMPACT``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``AddWinProbability``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        types = EventTypes()
        # Initialize the column
        pbp["PLAYER1_IMPACT"] = 0
        pbp["PLAYER2_IMPACT"] = 0

        # Add impacts
        # Rebounds
        pbp = self._basic_impact(pbp=pbp, eventmsgtype=types.REBOUND)
        # Free throws
        pbp = self._basic_impact(pbp=pbp, eventmsgtype=types.FREE_THROW)
        # Violations
        pbp = self._basic_impact(pbp=pbp, eventmsgtype=types.VIOLATION)
        # Fouls
        pbp = self._foul_impact(pbp=pbp, eventmsgtype=types.FOUL)
        # Turnovers
        pbp = self._dead_ball_turnovers(pbp=pbp, eventmsgtype=types.TURNOVER)

        # Loop through each game
        grouped = pbp.groupby("GAME_ID")
        for name, game in grouped:
            # Loop through each row
            self.logger.info(f"Processing impact for game {name}")
            for index, row in game.iterrows():
                if row["EVENTMSGTYPE"] == types.FIELD_GOAL_MADE:
                    continue

        return pbp
    
    @staticmethod
    def _basic_impact(pbp: pd.DataFrame, eventmsgtype: int) -> pd.DataFrame:
        """Add basic impacts.

        Valid for the following event types:

        * ``REBOUND``
        * ``FIELD_GOAL_MISSED``
        * ``FREE_THROW``
        * ``VIOLATION``

        Parameters
        ----------
        pbp : pd.DataFrame
            The play-by-play dataset.
        eventmsgtype : int
            The value for ``EVENTMSGTYPE``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        pbp.loc[
            (
                (pbp["EVENTMSGTYPE"] == eventmsgtype)
                & (~pd.isnull(pbp["HOMEDESCRIPTION"]))
            ),
            "PLAYER1_IMPACT"
        ] = pbp["WIN_PROBABILITY_CHANGE"]
        # Negate for visiting team since probability is in terms of home team
        pbp.loc[
            (
                (pbp["EVENTMSGTYPE"] == eventmsgtype)
                & (~pd.isnull(pbp["VISITORDESCRIPTION"]))
            ),
            "PLAYER1_IMPACT"
        ] = -pbp["WIN_PROBABILITY_CHANGE"]

        return pbp
    
    @staticmethod
    def _foul_impact(pbp: pd.DataFrame, eventmsgtype: int) -> pd.DataFrame:
        """Add the impact of fouls.

        In this case, ``PLAYER1_ID`` is the player committing the foul
        and ``PLAYER2_ID`` is the player that drew the foul.

        Parameters
        ----------
        pbp : pd.DataFrame
            The play-by-play dataset.
        eventmsgtype : int
            The value for ``EVENTMSGTYPE``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Home team fouls
        pbp.loc[
            (
                (pbp["EVENTMSGTYPE"] == eventmsgtype)
                & (~pd.isnull(pbp["HOMEDESCRIPTION"]))
            ),
            "PLAYER1_IMPACT"
        ] = pbp["WIN_PROBABILITY_CHANGE"]
        pbp.loc[
            (
                (pbp["EVENTMSGTYPE"] == eventmsgtype)
                & (~pd.isnull(pbp["HOMEDESCRIPTION"]))
            ),
            "PLAYER2_IMPACT"
        ] = -pbp["WIN_PROBABILITY_CHANGE"]
        # Visiting team foul
        # Negate the impacts since win probability is in terms of home team
        pbp.loc[
            (
                (pbp["EVENTMSGTYPE"] == eventmsgtype)
                & (~pd.isnull(pbp["VISITORDESCRIPTION"]))
            ),
            "PLAYER1_IMPACT"
        ] = -pbp["WIN_PROBABILITY_CHANGE"]
        pbp.loc[
            (
                (pbp["EVENTMSGTYPE"] == eventmsgtype)
                & (~pd.isnull(pbp["VISITORDESCRIPTION"]))
            ),
            "PLAYER2_IMPACT"
        ] = pbp["WIN_PROBABILITY_CHANGE"]

        return pbp
    
    @staticmethod
    def _dead_ball_turnovers(pbp: pd.DataFrame, eventmsgtype: int) -> pd.DataFrame:
        """Add impact for non-steal turnovers.

        Parameters
        ----------
        pbp : pd.DataFrame
            The play-by-play data.
        eventmsgtype : int
            The value for ``EVENTMSGTYPE``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Home turnovers
        pbp.loc[
            (
                (pbp["EVENTMSGTYPE"] == eventmsgtype)
                & (~pd.isnull(pbp["HOMEDESCRIPTION"]))
                & (pbp["PLAYER2_ID"] != 0)
            ),
            "PLAYER1_IMPACT"
        ] = pbp["WIN_PROBABILITY_CHANGE"]
        # Visiting turnovers
        pbp.loc[
            (
                (pbp["EVENTMSGTYPE"] == eventmsgtype)
                & (~pd.isnull(pbp["VISITORDESCRIPTION"]))
                & (pbp["PLAYER2_ID"] != 0)
            ),
            "PLAYER1_IMPACT"
        ] = -pbp["WIN_PROBABILITY_CHANGE"]

        return pbp
