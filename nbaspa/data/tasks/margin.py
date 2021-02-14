"""FillMargin.

Ensures the margin value is non-null.
"""

import pandas as pd
from prefect import Task

class FillMargin(Task):
    """Ensure the margin is non-null."""
    def run(self, pbp: pd.DataFrame) -> pd.DataFrame:
        """Ensure the margin is non-null.

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``SurvivalTime``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Sort by the game event identifier
        pbp.sort_values(by=["WCTIMESTRING", "EVENTNUM"], ascending=True, inplace=True)
        pbp.loc[pbp["SCOREMARGIN"] == "TIE", "SCOREMARGIN"] = 0
        pbp["SCOREMARGIN"] = pbp.groupby("GAME_ID")["SCOREMARGIN"].ffill()
        pbp["SCOREMARGIN"] = pbp["SCOREMARGIN"].fillna(0)
        pbp["SCOREMARGIN"] = pbp["SCOREMARGIN"].astype(int)

        return pbp
