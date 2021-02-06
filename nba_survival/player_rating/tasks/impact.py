"""Calculate player impact."""

from typing import Tuple

import pandas as pd
from prefect import Task

from nba_survival.data.endpoints.pbp import EventTypes

class PlayerImpact(Task):
    """Add player impact to the data."""

    event_types = EventTypes()

    def run(self, pbp: pd.DataFrame) -> pd.DataFrame:
        """Add player impact to the data.

        Adds the following columns:

        * ``PLAYER1_IMPACT``
        * ``PLAYER2_IMPACT``
        * ``PLAYER3_IMPACT``

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
        pbp["PLAYER3_IMPACT"] = 0

        # Add basic impacts
        for event in ["REBOUND", "FREE_THROW", "VIOLATION"]:
            self.logger.info(f"Adding the impact for the following event type: {event}")
            home, visitor = self._basic_filter(df=pbp, event_type=event)
            pbp.loc[home, "PLAYER1_IMPACT"] += pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
            pbp.loc[visitor, "PLAYER1_IMPACT"] -= pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]

        # Fouls
        self.logger.info("Adding the impact of fouls...")
        home, visitor = self._basic_filter(df=pbp, event_type="FOUL")
        pbp.loc[home, "PLAYER1_IMPACT"] += pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
        pbp.loc[home, "PLAYER2_IMPACT"] -= pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
        pbp.loc[visitor, "PLAYER1_IMPACT"] -= pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]
        pbp.loc[visitor, "PLAYER2_IMPACT"] += pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]
        # Dead ball turnovers
        self.logger.info("Adding the impact of dead ball turnovers...")
        home, visitor = self._dead_ball_turnover_filter(df=pbp)
        pbp.loc[home, "PLAYER1_IMPACT"] += pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
        pbp.loc[visitor, "PLAYER1_IMPACT"] -= pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]
        # Steals
        self.logger.info("Adding the impact of steals...")
        home, visitor = self._steal_filter(df=pbp)
        pbp.loc[home, "PLAYER2_IMPACT"] += pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
        pbp.loc[home, "PLAYER1_IMPACT"] -= pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
        pbp.loc[visitor, "PLAYER2_IMPACT"] -= pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]
        pbp.loc[visitor, "PLAYER1_IMPACT"] += pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]
        # Missed field goals
        self.logger.info("Adding the impact of missed field goals...")
        home, visitor = self._basic_filter(df=pbp, event_type="FIELD_GOAL_MISSED")
        pbp.loc[home, "PLAYER1_IMPACT"] += pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
        pbp.loc[visitor, "PLAYER1_IMPACT"] -= pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]
        # Blocked field goals -- encoded in PLAYER3_ID
        self.logger.info("Adding the impact of blocks...")
        home, visitor = self._block_filter(df=pbp)
        pbp.loc[home, "PLAYER3_IMPACT"] += pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
        pbp.loc[visitor, "PLAYER3_IMPACT"] -= pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]
        # Unassisted field goal makes
        self.logger.info("Adding the impact of unassisted field goals...")
        home, visitor = self._uast_filter(df=pbp)
        pbp.loc[home, "PLAYER1_IMPACT"] += pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
        pbp.loc[visitor, "PLAYER2_IMPACT"] -= pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]
        # Assisted field goal makes
        self.logger.info("Adding the impact of assisted field goals...")
        home, visitor = self._ast_filter(df=pbp)
        # Get the assist percentage
        home_assist_factor = (
            ((pbp.loc[home, "SHOT_VALUE"] * 100) / pbp.loc[home, "HOME_OFF_RATING"]) - 1
        ).clip(lower=0)
        pbp.loc[home, "PLAYER1_IMPACT"] += (
            (1 - home_assist_factor) * pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
        )
        pbp.loc[home, "PLAYER2_IMPACT"] += (
            home_assist_factor * pbp.loc[home, "WIN_PROBABILITY_CHANGE"]
        )
        # Visitor assist percentage
        visitor_assist_factor = (
            ((pbp.loc[visitor, "SHOT_VALUE"] * 100) / pbp.loc[visitor, "VISITOR_OFF_RATING"]) - 1
        ).clip(lower=0)
        pbp.loc[visitor, "PLAYER1_IMPACT"] -= (
            (1 - visitor_assist_factor) * pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]
        )
        pbp.loc[visitor, "PLAYER2_IMPACT"] -= (
            visitor_assist_factor * pbp.loc[visitor, "WIN_PROBABILITY_CHANGE"]
        )

        return pbp
    
    def _basic_filter(self, df: pd.DataFrame, event_type: str) -> Tuple[pd.Series, pd.Series]:
        """Return a basic filter.

        Parameters
        ----------
        df : pd.DataFrame
            The play-by-play data.
        event_type : str
            The event type to get from ``EventTypes``.
        
        Returns
        -------
        pd.Series
            A boolean filter for the home team events.
        pd.Series
            A boolean filter for the visiting team events.
        """
        eventmsgtype = getattr(self.event_types, event_type)

        homefilter = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (~pd.isnull(df["HOMEDESCRIPTION"]))
        )
        visitorfilter = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (~pd.isnull(df["VISITORDESCRIPTION"]))
        )

        return homefilter, visitorfilter
    
    def _dead_ball_turnover_filter(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Impact of non-steal turnovers.

        Parameters
        ----------
        df : pd.DataFrame
            The play-by-play dataset.
        
        Returns
        -------
        pd.Series
            A boolean filter for the home team events.
        pd.Series
            A boolean fitler for the visiting team events.
        """
        home = (
            (df["EVENTMSGTYPE"] == self.event_types.TURNOVER)
            & (~pd.isnull(df["HOMEDESCRIPTION"]))
            & (df["PLAYER2_ID"] == 0)
        )
        visitor = (
            (df["EVENTMSGTYPE"] == self.event_types.TURNOVER)
            & (~pd.isnull(df["VISITORDESCRIPTION"]))
            & (df["PLAYER2_ID"] == 0)
        )

        return home, visitor
    
    def _steal_filter(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Add impact of steals.

        Parameters
        ----------
        df : pd.DataFrame
            The play-by-play data.
        
        Returns
        -------
        pd.Series
            A boolean filter for the home team events.
        pd.Series
            A boolean filter for the visiting team events.
        """
        home = (
            (df["EVENTMSGTYPE"] == self.event_types.TURNOVER)
            & (df["HOMEDESCRIPTION"].str.contains("STL", na=False))
            & (df["PLAYER2_ID"] != 0)
        )
        visitor = (
            (df["EVENTMSGTYPE"] == self.event_types.TURNOVER)
            & (df["VISITORDESCRIPTION"].str.contains("STL", na=False))
            & (df["PLAYER2_ID"] != 0)
        )

        return home, visitor
    
    def _block_filter(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Add the impact of blocks.

        Parameters
        ----------
        df : pd.DataFrame
            The play-by-play data.
        
        Returns
        -------
        pd.Series
            A boolean filter for the home team events.
        pd.Series
            A boolean filter for the visiting team events.
        """
        home = (
            (df["EVENTMSGTYPE"] == self.event_types.FIELD_GOAL_MISSED)
            & (df["HOMEDESCRIPTION"].str.contains("BLK", na=False))
        )
        visitor = (
            (df["EVENTMSGTYPE"] == self.event_types.FIELD_GOAL_MISSED)
            & (df["VISITORDESCRIPTION"].str.contains("BLK", na=False)) 
        )

        return home, visitor
    
    def _uast_filter(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Add the impact of unassisted field goal makes.

        Parameters
        ----------
        df : pd.DataFrame
            The play-by-play data.
        
        Returns
        -------
        pd.Series
            A boolean filter for the home team events.
        pd.Series
            A boolean filter for the visiting team events.
        """
        home = (
            (df["EVENTMSGTYPE"] == self.event_types.FIELD_GOAL_MADE)
            & (~pd.isnull(df["HOMEDESCRIPTION"]))
            & (df["PLAYER2_ID"] == 0)
        )
        visitor = (
            (df["EVENTMSGTYPE"] == self.event_types.FIELD_GOAL_MADE)
            & (~pd.isnull(df["VISITORDESCRIPTION"]))
            & (df["PLAYER2_ID"] == 0)
        )

        return home, visitor


    def _ast_filter(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Add the impact of assisted field goal makes.

        Parameters
        ----------
        df : pd.DataFrame
            The play-by-play data.
        
        Returns
        -------
        pd.Series
            A boolean filter for the home team events.
        pd.Series
            A boolean filter for the visiting team events.
        """
        home = (
            (df["EVENTMSGTYPE"] == self.event_types.FIELD_GOAL_MADE)
            & (~pd.isnull(df["HOMEDESCRIPTION"]))
            & (df["PLAYER2_ID"] != 0)
        )
        visitor = (
            (df["EVENTMSGTYPE"] == self.event_types.FIELD_GOAL_MADE)
            & (~pd.isnull(df["VISITORDESCRIPTION"]))
            & (df["PLAYER2_ID"] != 0)
        )

        return home, visitor


class AggregateImpact(Task):
    """Aggregate player impact for a game."""
    def run(self, pbp: pd.DataFrame, boxscore: pd.DataFrame) -> pd.DataFrame:
        """Aggregate player impact for a game.

        Parameters
        ----------
        pbp : pd.DataFrame
            The output of ``PlayerImpact``.
        boxscore : pd.DataFrame
            The output of ``BoxScoreTraditional.get_data("PlayerStats")``.
        
        Returns
        -------
        pd.DataFrame
            The output DataFrame
        """
        impact = boxscore[["GAME_ID", "PLAYER_ID"]].copy()
        impact.set_index("PLAYER_ID", inplace=True)
        # Merge
        impact = pd.merge(
            impact,
            pbp.groupby("PLAYER1_ID")["PLAYER1_IMPACT"].sum(),
            left_index=True,
            right_index=True,
            how="left"
        )
        impact = pd.merge(
            impact,
            pbp.groupby("PLAYER2_ID")["PLAYER2_IMPACT"].sum(),
            left_index=True,
            right_index=True,
            how="left"
        )
        impact = pd.merge(
            impact,
            pbp.groupby("PLAYER3_ID")["PLAYER3_IMPACT"].sum(),
            left_index=True,
            right_index=True,
            how="left"
        )
        impact.fillna(0, inplace=True)
        impact["IMPACT"] = (
            impact["PLAYER1_IMPACT"] + impact["PLAYER2_IMPACT"] + impact["PLAYER3_IMPACT"]
        )
        # Reset the index
        impact.reset_index(inplace=True)

        return impact[["GAME_ID", "PLAYER_ID", "IMPACT"]].copy()
