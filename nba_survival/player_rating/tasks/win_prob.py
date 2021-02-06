"""Add win probability to the play-by-play data."""

import pandas as pd
from prefect import Task


class ConvertNBAWinProbability(Task):
    """Convert the NBA win probability to a series."""
    def run(self, win_prob: pd.DataFrame) -> pd.Series:
        """Convert the NBA win probability to a series.

        Parameters
        ----------
        win_prob : pd.DataFrame
            The output from ``WinProbability.get_data("WinProbPBP")``.
        
        Returns
        -------
        pd.Series
            A pandas series containing the win probability at a given event
            in the play-by-play data. Indexed first by the game identifier
            and the event number second.
        """
        df = win_prob[~pd.isnull(win_prob["EVENT_NUM"])].copy()
        df.set_index(["GAME_ID", "EVENT_NUM"], inplace=True)

        return df["HOME_PCT"]


class ConvertSurvivalWinProbability(Task):
    """Convert NBA survival win probability."""
    def run(self, win_prob: pd.DataFrame) -> pd.Series:
        """Convert NBA survival win probability.

        Parameters
        ----------
        win_prob : pd.DataFrame
            Ignored.
        
        Returns
        -------
        pd.Series
            Ignored.
        """
        pass

class AddWinProbability(Task):
    """Add win probability to the data."""
    def run(self, pbp: pd.DataFrame, win_prob: pd.Series) -> pd.DataFrame:
        """Add win probability to the data.

        Adds the following columns:

        * ``WIN_PROBABILITY``
        * ``WIN_PROBABILITY_CHANGE``

        Parameters
        ----------
        pbp : pd.DataFrame
            The cleaned output data from ``nba_survival.data.gen_pipeline``.
        win_prob : pd.Series
            A pandas series containing the win probability at a given event
            in the play-by-play data. Must be indexed by the game identifier
            first and the event number second.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Add the win probability to the play-by-play data
        pbp["WIN_PROBABILITY"] = pbp.merge(
            win_prob,
            left_on=("GAME_ID", "EVENTNUM"),
            right_index=True,
            how="left"
        )[win_prob.name]
        # Create a variable that represents the change in win probability over events
        pbp["WIN_PROBABILITY_CHANGE"] = pbp.groupby("GAME_ID")["WIN_PROBABILITY"].diff()

        return pbp
