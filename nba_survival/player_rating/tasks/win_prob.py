"""Add win probability to the play-by-play data."""

import pandas as pd
from prefect import Task

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
        # Store the index names for the series
        idx_names = win_prob.index.names
        prob_variable = win_prob.name
        win_prob = win_prob.reset_index()
        # Remove all null event rows
        win_prob = win_prob.loc[~pd.isnull(win_prob[idx_names[1]])].copy()
        # Add the win probability to the play-by-play data
        pbp["WIN_PROBABILITY"] = pbp.merge(
            win_prob,
            left_on=("GAME_ID", "EVENTNUM"),
            right_on=idx_names,
            how="left"
        )[prob_variable]
        # Create a variable that represents the change in win probability over events
        pbp["WIN_PROBABILITY_CHANGE"] = pbp.groupby("GAME_ID")["WIN_PROBABILITY"].diff()

        return pbp
