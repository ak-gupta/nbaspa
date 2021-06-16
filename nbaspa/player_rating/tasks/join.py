"""This module defines a task for adding survival probability to the data."""

import numpy as np
import pandas as pd
from prefect import Task


class AddSurvivalProbability(Task):
    """Add the survival probability to the play-by-play dataset."""

    def run(  # type: ignore
        self, pbp: pd.DataFrame, survprob: pd.DataFrame
    ) -> pd.DataFrame:
        """Add the survival probability to the play-by-play dataset.

        Adds the following columns:

        * ``WIN_PROB``
        * ``WIN_PROB_CHANGE``

        Parameters
        ----------
        pbp : pd.DataFrame
            The clean rating data.
        survprob : pd.DataFrame
            The survival prediction data.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        survprob["TIME"] = survprob["TIME"].astype(int)
        survprob = survprob.set_index(["GAME_ID", "TIME"])
        # Get the last row for each gametime step
        pbp["TIME"] = pbp["TIME"].astype(int)
        filtered = pbp.sort_values(
            by=["GAME_ID", "TIME", "EVENTNUM"], ascending=True
        ).duplicated(subset=["GAME_ID", "TIME"], keep="last")
        # Add the survival probability for each time step
        pbp["SURV_PROB"] = np.nan
        pbp.loc[~filtered, "SURV_PROB"] = pbp[~filtered].merge(
            survprob,
            left_on=("GAME_ID", "TIME"),
            right_index=True,
            how="left"
        )["WIN_PROB"]
        pbp["SURV_PROB"] = pbp.groupby("GAME_ID")["SURV_PROB"].bfill()
        # Create a variable representing the change in win probability
        pbp["SURV_PROB_CHANGE"] = pbp.groupby("GAME_ID")["SURV_PROB"].diff()
        pbp["SURV_PROB_CHANGE"] = pbp.groupby("GAME_ID")[
            "SURV_PROB_CHANGE"
        ].bfill()

        return pbp
