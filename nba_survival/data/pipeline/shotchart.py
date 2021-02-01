"""Add shotchart detail."""

import numpy as np
import pandas as pd
from prefect import Task

class AddShotDetail(Task):
    """Add shotchart details."""
    def run(self, pbp: pd.DataFrame, shotchart: pd.DataFrame) -> pd.DataFrame:
        """Add shotchart detail.

        Adds the following columns:

        * ``SHOT_ZONE_BASIC``
        * ``SHOT_VALUE``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``PlayByPlay.get_data()``
        shotchart : pd.DataFrame
            The output from ``ShotChart.get_data()``
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Add shot value to the shotchart data
        shotchart["SHOT_VALUE"] = np.nan
        shotchart.loc[shotchart["SHOT_TYPE"] == "2PT Field Goal", "SHOT_VALUE"] = 2
        shotchart.loc[shotchart["SHOT_TYPE"] == "3PT Field Goal", "SHOT_VALUE"] = 3
        # Join the play by play data with the shotchart
        joined = pbp.merge(
            shotchart,
            left_on=("PLAYER1_ID", "EVENTNUM", "GAME_ID"),
            right_on=("PLAYER_ID", "GAME_EVENT_ID", "GAME_ID"),
            how="left"
        )
        # Add the variables
        pbp["SHOT_ZONE_BASIC"] = joined["SHOT_ZONE_BASIC"]
        pbp["SHOT_VALUE"] = joined["SHOT_VALUE"]

        return pbp
