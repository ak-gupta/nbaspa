"""SurvivalTime.

Define the survival time based on Play by play data.
"""

import pandas as pd
from prefect import Task

class SurvivalTime(Task):
    """Get the survival time."""
    def run(self, pbp: pd.DataFrame) -> pd.DataFrame:
        """Add survival time.

        Adds the following column:

        * ``TIME``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``PlayByPlay.get_data()``.
        
        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # First, split the play clock into minutes and seconds
        pbp_time = pbp["PCTIMESTRING"].str.split(":", expand=True).astype(int)
        # Create the new column
        # First add time for regulation
        pbp.loc[pbp["PERIOD"] <= 4, "TIME"] = ((pbp["PERIOD"] - 1) * 720) + 720 - (pbp_time[0] * 60) - pbp_time[1]
        # Then add for overtime
        pbp.loc[pbp["PERIOD"] > 4, "TIME"] = (4 * 720) + ((pbp["PERIOD"] - 5) * 300) + 720 - (pbp_time[0] * 60) - pbp_time[1]

        return pbp
