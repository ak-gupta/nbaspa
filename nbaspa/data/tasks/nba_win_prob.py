"""Add NBA win probability to the clean data."""

import numpy as np
import pandas as pd
from prefect import Task

class AddNBAWinProbability(Task):
    """Add the NBA win probability to the play-by-play dataset."""
    def run(self, pbp: pd.DataFrame, winprob: pd.DataFrame) -> pd.DataFrame:
        """Add the NBA win probability to the play-by-play dataset.

        Adds the following columns:

        * ``NBA_WIN_PROB``
        * ``NBA_WIN_PROB_CHANGE``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output of ``SurvivalTime.run()``.
        winprob : pd.DataFrame
            The output of ``WinProbabilityLoader.run()``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Remove null event num rows from the win probability data
        filtered_wprob = winprob[~pd.isnull(winprob["EVENT_NUM"])].copy()
        filtered_wprob.set_index(["GAME_ID", "EVENT_NUM"], inplace=True)
        # Get the last row for each gametime step
        filtered = (
            pbp
            .sort_values(by=["GAME_ID", "TIME", "EVENTNUM"], ascending=True)
            .duplicated(subset=["GAME_ID", "TIME"], keep="last")
        )
        # Add the win probability for each unique time step
        pbp["NBA_WIN_PROB"] = np.nan
        pbp.loc[~filtered, "NBA_WIN_PROB"] = pbp[~filtered].merge(
            filtered_wprob,
            left_on=("GAME_ID", "EVENTNUM"),
            right_index=True,
            how="left"
        )[filtered_wprob.name]
        # Create a variable representing the change in win probability
        pbp.loc[
            ~pd.isnull(pbp["NBA_WIN_PROB"]), "NBA_WIN_PROB_CHANGE"
        ] = pbp.loc[
            ~pd.isnull(pbp["NBA_WIN_PROB"]), "NBA_WIN_PROB"
        ].diff()
        pbp["NBA_WIN_PROB"] = pbp["NBA_WIN_PROB"].bfill()
        pbp["NBA_WIN_PROB_CHANGE"] = pbp["NBA_WIN_PROB_CHANGE"].bfill()

        return pbp
