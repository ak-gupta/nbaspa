"""Add lineup plus minus."""

from typing import Set, Tuple

import numpy as np
import pandas as pd
from prefect import Task

from nba_survival.data.endpoints.pbp import EventTypes


class AddLineupPlusMinus(Task):
    """Add lineup plus minus."""

    def run(
        self,
        pbp: pd.DataFrame,
        lineup_stats: pd.DataFrame,
        home_rotation: pd.DataFrame,
        away_rotation: pd.DataFrame
    ) -> pd.DataFrame:
        """Add lineup plus minus.

        Adds the following columns:

        * ``HOME_LINEUP_PLUS_MINUS``
        * ``VISITOR_LINEUP_PLUS_MINUS``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``SurvivalTime``
        lineup_stats : pd.DataFrame
            The output from ``TeamLineups.get_data("Lineups")``.
        home_rotation : pd.DataFrame
            The output from ``GameRotation.get_data("HomeTeam")``.
        away_rotation : pd.DataFrame
            The output from ``GameRotation.get_data("AwayTeam")``.
        
        Returns
        -------
        pd.DataFrame
            The updated datsets.
        """
        # Split and reorder the group id column
        lineup_stats = self._fix_group_id(lineup_stats)

        # Fix the time values for the rotation data
        home_rotation = self._fix_rotation_time(home_rotation)
        away_rotation = self._fix_rotation_time(away_rotation)

        # Initialize the plus minus value
        pbp["HOME_LINEUP_PLUS_MINUS"] = np.nan
        pbp["VISITOR_LINEUP_PLUS_MINUS"] = np.nan
        # Ensure the event type is an integer
        pbp["EVENTMSGTYPE"] = pbp["EVENTMSGTYPE"].astype(int)
        # Group the play by play data by game
        grouped = pbp.groupby("GAME_ID")

        # Loop through each game in the play by play dataset
        for name, game in grouped:
            # Set an empty lineup to start
            home_lineup = set()
            away_lineup = set()
            # Loop through each event in the game
            self.logger.info(f"Looping through each event in game {name}")

            for index, row in game.iterrows():
                if row["EVENTMSGTYPE"] == EventTypes().SUBSTITUTION:
                    if not pd.isnull(row["HOMEDESCRIPTION"]):
                        self.logger.debug(
                            f"Home team substitution at {row['PCTIMESTRING']} ({row['TIME']}) in "
                            f"period {row['PERIOD']}: {row['HOMEDESCRIPTION']}"
                        )
                        # Get the updated lineup and plus minus value
                        try:
                            home_lineup, plusminus = self._substitution_event(
                                lineup=home_lineup,
                                lineup_stats=lineup_stats,
                                rotation=home_rotation,
                                row=row,
                            )
                            pbp.loc[index, "HOME_LINEUP_PLUS_MINUS"] = plusminus
                        except (ValueError, KeyError):
                            self.logger.warning("Setting the lineup plus minus to the net rating")
                            pbp.loc[index, "HOME_LINEUP_PLUS_MINUS"] = pbp.loc[
                                index, "HOME_NET_RATING"
                            ]
                    else:
                        self.logger.debug(
                            f"Visiting team substitution at {row['PCTIMESTRING']} ({row['TIME']}) in "
                            f"period {row['PERIOD']}: {row['VISITORDESCRIPTION']}"
                        )
                        # Get the updated lineup and plus minus value
                        try:
                            away_lineup, plusminus = self._substitution_event(
                                lineup=away_lineup,
                                lineup_stats=lineup_stats,
                                rotation=away_rotation,
                                row=row
                            )
                            pbp.loc[index, "VISITOR_LINEUP_PLUS_MINUS"] = plusminus
                        except (ValueError, KeyError):
                            self.logger.warning("Setting the lineup plus minus to the net rating")
                            pbp.loc[index, "VISITOR_LINEUP_PLUS_MINUS"] = pbp.loc[
                                index, "VISITOR_NET_RATING"
                            ]

                elif row["EVENTMSGTYPE"] == EventTypes().PERIOD_BEGIN:
                    self.logger.debug(
                        f"Looking for substitutions at the beginning of {row['PERIOD']} for the "
                        "home team..."
                    )
                    try:
                        home_lineup, plusminus = self._period_begin_substitutions(
                            gametime=row["TIME"],
                            gameid=name,
                            rotation=home_rotation,
                            lineup=home_lineup,
                            lineup_stats=lineup_stats,
                        )
                        pbp.loc[index, "HOME_LINEUP_PLUS_MINUS"] = plusminus
                    except (ValueError, KeyError):
                        self.logger.warning("Setting the lineup plus minus to the net rating")
                        pbp.loc[index, "HOME_LINEUP_PLUS_MINUS"] = pbp.loc[
                            index, "HOME_NET_RATING"
                        ]

                    self.logger.debug(
                        f"Looking for substitutions at the beginning of {row['PERIOD']} for the "
                        "visiting team..."
                    )
                    try:
                        away_lineup, plusminus = self._period_begin_substitutions(
                            gametime=row["TIME"],
                            gameid=name,
                            rotation=away_rotation,
                            lineup=away_lineup,
                            lineup_stats=lineup_stats,
                        )
                        pbp.loc[index, "VISITOR_LINEUP_PLUS_MINUS"] = plusminus
                    except (ValueError, KeyError):
                        self.logger.warning("Setting the lineup plus minus to the net rating")
                        pbp.loc[index, "VISITOR_LINEUP_PLUS_MINUS"] = pbp.loc[
                            index, "VISITOR_NET_RATING"
                        ]

                else:
                    continue
        
        # Fill the ratings
        pbp["HOME_LINEUP_PLUS_MINUS"] = pbp.groupby("GAME_ID")["HOME_LINEUP_PLUS_MINUS"].ffill()
        pbp["VISITOR_LINEUP_PLUS_MINUS"] = pbp.groupby("GAME_ID")["VISITOR_LINEUP_PLUS_MINUS"].ffill()

        return pbp
    
    def _fix_group_id(self, lineup_stats: pd.DataFrame) -> pd.DataFrame:
        """Fix the lineup group ID.

        Parameters
        ----------
        lineup_stats : pd.DataFrame
            The output from ``TeamLineups.get_data("Lineups")``.
        
        Returns
        -------
        pd.DataFrame
            The original dataset with a sorted and trimmed ``GROUP_ID``.
        """
        # Split and reorder the group id column
        split_id = lineup_stats["GROUP_ID"].str.split("-").str[1:6]
        split_id = split_id.apply(sorted)
        lineup_stats["GROUP_ID"] = split_id.str.join("-")

        return lineup_stats
    
    def _fix_rotation_time(self, rotation: pd.DataFrame) -> pd.DataFrame:
        """Fix the rotation time value.

        Parameters
        ----------
        rotation : pd.DataFrame
            The output from ``GameRotation.get_data("AwayTeam")`` or
            ``GameRotation.get_data("HomeTeam")``.
        
        Returns
        -------
        pd.DataFrame
            The original dataset with fixed ``IN_TIME_REAL`` and ``OUT_TIME_REAL``
            values.
        """
        rotation["IN_TIME_REAL"] = np.ceil(rotation["IN_TIME_REAL"] / 10)
        rotation["OUT_TIME_REAL"] = np.ceil(rotation["OUT_TIME_REAL"] / 10)

        return rotation
    
    def _substitution_event(
        self,
        lineup: Set,
        lineup_stats: pd.DataFrame,
        rotation: pd.DataFrame,
        row: pd.Series
    ) -> Tuple[Set, float]:
        """Adjust the lineup and get the plus minus.

        Parameters
        ----------
        lineup : set
            The current set of players on the floor.
        lineup_stats: pd.DataFrame
            The 5-man lineup stats.
        rotation : pd.DataFrame
            The output from ``GameRotation.get_data("AwayTeam")`` or
            ``GameRotation.get_data("HomeTeam")``.
        row : pd.Series
            Current substitution event in the play by play data.
        
        Returns
        -------
        Set
            The updated set of players on the floor
        float
            The updated lineup plus minus value
        """
        plusminus = 0
        # Remove PLAYER1_ID
        self.logger.debug(f"Removing {row['PLAYER1_ID']}")
        lineup.remove(row["PLAYER1_ID"])

        # Add PLAYER2_ID
        self.logger.debug(f"Adding {row['PLAYER2_ID']}")
        lineup.add(row["PLAYER2_ID"])

        # Look for the lineup group in the lineup stats
        linestr = "-".join(sorted(str(item) for item in lineup))
        self.logger.debug(
            f"Looking for the following lineup group: {linestr}"
        )
        if len(lineup) != 5:
            self.logger.error(f"Lineup has {len(lineup)} players instead of 5.")
            raise ValueError(f"Lineup has {len(lineup)} players instead of 5.")
        if not lineup_stats.loc[lineup_stats["GROUP_ID"] == linestr].empty:
            self.logger.debug(f"Found data for lineup group {linestr}")
            plusminus = lineup_stats.loc[
                lineup_stats["GROUP_ID"] == linestr, "PLUS_MINUS"
            ].values[0]
        
        return lineup, plusminus
    
    def _period_begin_substitutions(
        self,
        gametime: int,
        gameid: str,
        rotation: pd.DataFrame,
        lineup: Set,
        lineup_stats: pd.DataFrame
    ) -> Tuple[Set, float]:
        """Update the lineup for period begin events.

        Parameters
        ----------
        gametime : int
            The current ``TIME`` value from the play by play data.
        gameid : str
            The game ID.
        rotation : pd.DataFrame
            The output from ``GameRotation.get_data("AwayTeam")`` or
            ``GameRotation.get_data("HomeTeam")``.
        lineup : Set
            The current set of players on the floor.
        lineup_stats : pd.DataFrame
            The 5-man lineup stats.
        
        Returns
        -------
        Set
            The updated set of players on the floor
        float
            The updated lineup plus minus value
        """
        new_players = rotation.loc[
            (rotation["GAME_ID"] == gameid) & (rotation["IN_TIME_REAL"] == gametime)
        ]
        if not new_players.empty:
            self.logger.debug(f"New players at time {gametime}")
            self.logger.debug(
                "Substituting the following players in: "
                f"{', '.join(str(itm) for itm in new_players['PERSON_ID'].values)}"
            )
            # Add new players
            lineup.update(new_players["PERSON_ID"].values.tolist())
            # Remove players
            subout = rotation.loc[
                (rotation["GAME_ID"] == gameid) & (rotation["OUT_TIME_REAL"] == gametime),
                "PERSON_ID"
            ].values.tolist()
            if subout:
                self.logger.debug(
                    "Substituting the following players out: "
                    f"{', '.join(str(itm) for itm in subout)}"
                )
                lineup = lineup.difference(set(subout))

        # Look for the lineup group in the lineup stats
        linestr = "-".join(sorted(str(item) for item in lineup))
        self.logger.debug(
            f"Looking for the following lineup group: {linestr}"
        )
        if len(lineup) != 5:
            self.logger.error(f"Lineup has {len(lineup)} players instead of 5.")
            raise ValueError(f"Lineup has {len(lineup)} players instead of 5.")
        plusminus = 0
        if not lineup_stats.loc[lineup_stats["GROUP_ID"] == linestr].empty:
            self.logger.debug(f"Found data for lineup group {linestr}")
            plusminus = lineup_stats.loc[
                lineup_stats["GROUP_ID"] == linestr, "PLUS_MINUS"
            ].values[0]
        
        return lineup, plusminus
