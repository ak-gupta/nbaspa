"""Calculate player impact."""

from typing import Callable, Dict, List, Tuple

import pandas as pd
from prefect import Task

from nba_survival.data.endpoints.pbp import EventTypes

def _num_events_at_time(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Get the number of events at each time.

    Parameters
    ----------
    pbp : pd.DataFrame
        The clean player-rating play-by-play data.
    
    Returns
    -------
    pd.Series
        A series indexed by the time period with the number
        of play-by-play events associated with that time.
    pd.Series
        The row-level filter applied to the dataset before aggregation
    """
    # Filter out player-independent events
    teamevents = [
        EventTypes().SUBSTITUTION,
        EventTypes().TIMEOUT,
        EventTypes().JUMP_BALL,
        EventTypes().PERIOD_BEGIN,
        EventTypes().UNKNOWN
    ]
    rowfilter = (
        (df["PLAYER1_ID"] != df["HOME_TEAM_ID"])
        & (df["PLAYER1_ID"] != df["VISITOR_TEAM_ID"])
        & (~df["EVENTMSGTYPE"].isin(teamevents))
    )
    sizes = df[rowfilter].groupby("TIME").size()

    return sizes, rowfilter

class SimplePlayerImpact(Task):
    """Add player impact to the data.
    
    This class will only calculate player impact for time periods in the game
    with a single event.
    """

    event_types = EventTypes()

    def run(self, pbp: pd.DataFrame) -> pd.DataFrame:
        """Add player impact to the data.

        This class will only calculate player impact for time periods in the game
        with a single event. Adds the following columns:

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
    
    def _single_event_times(self, df: pd.DataFrame) -> List[int]:
        """Get the time stamps with one event.

        Parameters
        ----------
        df : pd.DataFrame
            The play-by-play data.
        event_type : str
            The event type to get from ``EventTypes``.
        
        Returns
        -------
        List
            The list of time stamps
        """
        sizes, _ = _num_events_at_time(df)

        return sizes[sizes == 1].index.tolist()

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
            & (df["TIME"].isin(self._single_event_times(df=df)))
        )
        visitorfilter = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (~pd.isnull(df["VISITORDESCRIPTION"]))
            & (df["TIME"].isin(self._single_event_times(df=df)))
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
        eventmsgtype = self.event_types.TURNOVER
        home = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (~pd.isnull(df["HOMEDESCRIPTION"]))
            & (df["PLAYER2_ID"] == 0)
            & (df["TIME"].isin(self._single_event_times(df=df)))
        )
        visitor = (
            (df["EVENTMSGTYPE"] == self.event_types.TURNOVER)
            & (~pd.isnull(df["VISITORDESCRIPTION"]))
            & (df["PLAYER2_ID"] == 0)
            & (df["TIME"].isin(self._single_event_times(df=df)))
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
        eventmsgtype = self.event_types.TURNOVER
        home = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (df["HOMEDESCRIPTION"].str.contains("STL", na=False))
            & (df["PLAYER2_ID"] != 0)
            & (df["TIME"].isin(self._single_event_times(df=df)))
        )
        visitor = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (df["VISITORDESCRIPTION"].str.contains("STL", na=False))
            & (df["PLAYER2_ID"] != 0)
            & (df["TIME"].isin(self._single_event_times(df=df)))
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
        eventmsgtype = self.event_types.FIELD_GOAL_MISSED
        home = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (df["HOMEDESCRIPTION"].str.contains("BLK", na=False))
            & (df["TIME"].isin(self._single_event_times(df=df)))
        )
        visitor = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (df["VISITORDESCRIPTION"].str.contains("BLK", na=False))
            & (df["TIME"].isin(self._single_event_times(df=df)))
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
        eventmsgtype = self.event_types.FIELD_GOAL_MADE
        home = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (~pd.isnull(df["HOMEDESCRIPTION"]))
            & (df["PLAYER2_ID"] == 0)
            & (df["TIME"].isin(self._single_event_times(df=df)))
        )
        visitor = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (~pd.isnull(df["VISITORDESCRIPTION"]))
            & (df["PLAYER2_ID"] == 0)
            & (df["TIME"].isin(self._single_event_times(df=df)))
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
        eventmsgtype = self.event_types.FIELD_GOAL_MADE
        home = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (~pd.isnull(df["HOMEDESCRIPTION"]))
            & (df["PLAYER2_ID"] != 0)
            & (df["TIME"].isin(self._single_event_times(df=df)))
        )
        visitor = (
            (df["EVENTMSGTYPE"] == eventmsgtype)
            & (~pd.isnull(df["VISITORDESCRIPTION"]))
            & (df["PLAYER2_ID"] != 0)
            & (df["TIME"].isin(self._single_event_times(df=df)))
        )

        return home, visitor


class CompoundPlayerImpact(Task):
    """Define player impact for time periods with multiple events."""

    event_types = EventTypes()

    def run(self, pbp: pd.DataFrame) -> pd.DataFrame:
        """Define player impact for time periods with multiple events.

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``SimplePlayerImpact``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        sizes, rowfilter = _num_events_at_time(pbp)
        # Get compound events
        compound = sizes[sizes > 1].index.tolist()
        incomplete_times = []
        for timeperiod in compound:
            # Get the sequence
            sequence = pbp.loc[(pbp["TIME"] == timeperiod) & (rowfilter)]
            try:
                sequence_type = self.identify_sequence(sequence["EVENTMSGTYPE"].tolist())
                self.logger.info(f"Found following sequence at {timeperiod}: {sequence_type}")
                # Assign the impact
                pbp = self.dispatcher[sequence_type](
                    df=pbp, event_indices=(pbp["TIME"] == timeperiod).index
                )
            except ValueError:
                self.logger.warning(
                    "Unexpected sequence at {timeperiod}:\n{df_sample}\n".format(
                        timeperiod=timeperiod,
                        df_sample=sequence[
                            [
                                "EVENTNUM",
                                "EVENTMSGTYPE",
                                "HOMEDESCRIPTION",
                                "VISITORDESCRIPTION",
                                "PLAYER1_NAME",
                                "PLAYER2_NAME",
                                "PLAYER3_NAME"
                            ]
                        ]
                    )
                )
    
    def identify_sequence(self, eventlist: List) -> str:
        """Identify the event sequence.

        Parameters
        ----------
        eventlist : list
            A list of event types.
        
        Returns
        -------
        str
            The event type
        """
        for key, value in self.common_sequences.items():
            if eventlist == value:
                event_type = key
                break
        else:
            raise ValueError("Unknown event type")

        return event_type
    
    @property
    def common_sequences(self) -> Dict[str, List[int]]:
        """Common sequences.

        Returns
        -------
        Dict
            The defined sequences.
        """
        return {
            "Offensive foul": [
                self.event_types.FOUL,
                self.event_types.TURNOVER
            ],
            "Shooting foul (2PT FGA)": [
                self.event_types.FOUL,
                self.event_types.FREE_THROW,
                self.event_types.FREE_THROW
            ],
            "Shooting foul (2PT FGA - Missed FT)": [
                self.event_types.FOUL,
                self.event_types.FREE_THROW,
                self.event_types.FREE_THROW,
                self.event_types.REBOUND
            ],
            "Shooting foul (3PT FGA)": [
                self.event_types.FOUL,
                self.event_types.FREE_THROW,
                self.event_types.FREE_THROW,
                self.event_types.FREE_THROW
            ],
            "Shooting foul (3PT FGA - Missed FT)": [
                self.event_types.FOUL,
                self.event_types.FREE_THROW,
                self.event_types.FREE_THROW,
                self.event_types.FREE_THROW,
                self.event_types.REBOUND                
            ],
            "Shooting foul (FGM)": [
                self.event_types.FIELD_GOAL_MADE,
                self.event_types.FOUL,
                self.event_types.FREE_THROW,
            ],
            "Shooting foul (FGM - Missed FT)": [
                self.event_types.FIELD_GOAL_MADE,
                self.event_types.FOUL,
                self.event_types.FREE_THROW,
                self.event_types.REBOUND,
            ],
            "Putback FGM": [
                self.event_types.REBOUND,
                self.event_types.FIELD_GOAL_MADE
            ],
            "Putback FGA": [
                self.event_types.REBOUND,
                self.event_types.FIELD_GOAL_MISSED
            ],
            "Shooting foul (Putback FGM)": [
                self.event_types.REBOUND,
                self.event_types.FIELD_GOAL_MADE,
                self.event_types.FOUL,
                self.event_types.FREE_THROW,
            ],
            "Shooting foul (Putback FGA)": [
                self.event_types.REBOUND,
                self.event_types.FOUL,
                self.event_types.FREE_THROW,
                self.event_types.FREE_THROW
            ],
            "Shooting foul (Putback FGM - Missed FT)": [
                self.event_types.REBOUND,
                self.event_types.FIELD_GOAL_MADE,
                self.event_types.FOUL,
                self.event_types.FREE_THROW,
                self.event_types.REBOUND,
            ],
            "Shooting foul (Putback FGA - Missed FT)": [
                self.event_types.REBOUND,
                self.event_types.FOUL,
                self.event_types.FREE_THROW,
                self.event_types.FREE_THROW,
                self.event_types.REBOUND
            ],
        }
    
    @property
    def dispatcher(self) -> Dict[str, Callable]:
        """Return the appropriate calculation function.

        Returns
        -------
        Dict
            A dictionary with the appropriate calculation function.
        """
        return {
            "Offensive foul": self._offensive_foul_impact,
            "Shooting foul (2PT FGA)": self._shooting_foul_impact,
            "Shooting foul (2PT FGA - Missed FT)": self._shooting_foul_impact,
            "Shooting foul (3PT FGA)": self._shooting_foul_impact,
            "Shooting foul (3PT FGA - Missed FT)": self._shooting_foul_impact,
            "Shooting foul (FGM)": self._shooting_foul_impact,
            "Shooting foul (FGM - Missed FT)": self._shooting_foul_impact,
            "Putback FGM": self._putback_impact,
            "Putback FGA": self._putback_impact,
            "Shooting foul (Putback FGM)": self._putback_impact,
            "Shooting foul (Putbcak FGA)": self._putback_impact,
            "Shooting foul (Putback FGM - Missed FT)": self._putback_impact,
            "Shooting foul (Putback FGA - Missed FT)": self._putback_impact,
        }
    
    def _offensive_foul_impact(self, df: pd.DataFrame, event_indices: List[int]) -> pd.DataFrame:
        """Calculate the impact of an offensive foul.

        We will drop the offensive foul row and give the player committing the foul
        credit/blame.

        Parameters
        ----------
        df : pd.DataFrame
            The complete play-by-play data.
        event_indices : list
            The list of indices in the play-by-play data associated with the sequence.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Attribute blame for the second row (the turnover)
        if not pd.isnull(df.loc[event_indices[1], "HOMEDESCRIPTION"]):
            df.loc[event_indices[1], "PLAYER1_IMPACT"] += df.loc[
                event_indices[1], "WIN_PROBABILITY_CHANGE"
            ]
        else:
            df.loc[event_indices[1], "PLAYER1_IMPACT"] -= df.loc[
                event_indices[1], "WIN_PROBABILITY_CHANGE"
            ]
        
        return df

    def _shooting_foul_impact(self, df: pd.DataFrame, event_indices: List[int]) -> pd.DataFrame:
        """Calculate the impact of a shooting foul (non-putback).

        The player committing the foul is given blame and the player shooting free throws
        will be given credit.

        Parameters
        ----------
        df : pd.DataFrame
            The complete play-by-play data.
        event_indices : list
            The list of indices in the play-by-play data associated with the sequence.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Assign blame for the foul
        # If the player made the shot, the second event is the foul
        if df.loc[event_indices[0], "EVENTMSGTYPE"] == self.event_types.FIELD_GOAL_MADE:
            idx = event_indices[1]
        else:
            idx = event_indices[0]
        if not pd.isnull(df.loc[idx, "HOMEDESCRIPTION"]):
            df.loc[idx, "PLAYER1_IMPACT"] += df.loc[
                idx, "WIN_PROBABILITY_CHANGE"
            ]
        else:
            df.loc[event_indices[0], "PLAYER1_IMPACT"] -= df.loc[
                event_indices[0], "WIN_PROBABILITY_CHANGE"
            ]
        
        # Give credit for the free throw
        if df.loc[event_indices[-1], "EVENTMSGTYPE"] == self.event_types.REBOUND:
            # Defensive rebound is the final event -- give credit in second last row
            idx = event_indices[-2]
        else:
            idx = event_indices[-1]
        if not pd.isnull(df.loc[idx, "HOMEDESCRIPTION"]):
            df.loc[idx, "PLAYER1_IMPACT"] += df.loc[
                idx, "WIN_PROBABILITY_CHANGE"
            ]
        else:
            df.loc[event_indices[-1], "PLAYER1_IMPACT"] -= df.loc[
                idx, "WIN_PROBABILITY_CHANGE"
            ]
        
        return df

    def _putback_impact(self, df: pd.DataFrame, event_indices: List[int]) -> pd.DataFrame:
        """Calculate the impact of a putback.

        Player getting the rebound will be given credit proportional to the quality
        of the shot taken. Quality of the shot will include the expected value from the
        free throw, if applicable.

        Parameters
        ----------
        df : pd.DataFrame
            The complete play-by-play data.
        event_indices : list
            The list of indices in the play-by-play data associated with the sequence.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Get the shot value
        shotval = df.loc[event_indices, "SHOT_VALUE"].sum()
        if df.loc[event_indices[-1], "EVENTMSGTYPE"] == self.event_types.REBOUND:
            # Second last event was the field goal or free throw attempt
            idx = event_indices[-2]
        else:
            idx = event_indices[-1]
        if pd.isnull(df.loc[event_indices[0], "HOMEDESCRIPTION"]):
            # Get the credit for the rebounder
            reb_factor = max(
                ((shotval * 100) / df.loc[event_indices[0], "HOME_OFF_RATING"]) - 1, 0
            )
            # Assign credit for the rebounder
            df.loc[event_indices[0], "PLAYER1_IMPACT"] += (
                reb_factor * df.loc[event_indices[0], "WIN_PROBABILITY_CHANGE"]
            )
            # Assign credit for the player who took the shot/free throws
            df.loc[idx, "PLAYER1_IMPACT"] += (
                (1 - reb_factor) * df.loc[idx, "WIN_PROBABILITY_CHANGE"]
            )
            # Assign blame for the person fouling -- either the second or third event
            if df.loc[event_indices[1], "EVENTMSGTYPE"] == self.event_types.FOUL:
                # Home team scored -> visiting player is ``PLAYER1_ID`` and they committed the foul
                df.loc[event_indices[1], "PLAYER1_IMPACT"] -= df.loc[
                    event_indices[1], "WIN_PROBABILITY_CHANGE"
                ]
            elif df.loc[event_indices[2], "EVENTMSGTYPE"] == self.event_types.FOUL:
                df.loc[event_indices[2], "PLAYER1_IMPACT"] -= df.loc[
                    event_indices[2], "WIN_PROBABILITY_CHANGE"
                ]
        else:
            # Get the credit for the rebounder
            reb_factor = (
                ((shotval * 100) / df.loc[event_indices[0], "VISITOR_OFF_RATING"]) - 1, 0
            )
            # Assign credit for the rebounder
            df.loc[event_indices[0], "PLAYER1_IMPACT"] -= (
                reb_factor * df.loc[event_indices[0], "WIN_PROBABILITY_CHANGE"]
            )
            # Assign credit for the player who took the shot/free throws
            df.loc[idx, "PLAYER1_IMPACT"] -= (
                (1 - reb_factor) * df.loc[idx, "WIN_PROBABILITY_CHANGE"]
            )
            # Assign blame for the person fouling -- either the second or third event
            if df.loc[event_indices[1], "EVENTMSGTYPE"] == self.event_types.FOUL:
                # Visiting team score -> home player is ``PLAYER1_ID`` and they committed the foul
                df.loc[event_indices[1], "PLAYER1_IMPACT"] += df.loc[
                    event_indices[1], "WIN_PROBABILITY_CHANGE"
                ]
            elif df.loc[event_indices[2], "EVENTMSGTYPE"] == self.event_types.FOUL:
                df.loc[event_indices[2], "PLAYER1_IMPACT"] += df.loc[
                    event_indices[2], "WIN_PROBABILITY_CHANGE"
                ]

        return df


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
