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
        pbp.loc[pbp["PERIOD"] <= 4, "TIME"] = (
            ((pbp["PERIOD"] - 1) * 720) + 720 - (pbp_time[0] * 60) - pbp_time[1]
        )
        # Then add for overtime
        pbp.loc[pbp["PERIOD"] > 4, "TIME"] = (
            (4 * 720)
            + ((pbp["PERIOD"] - 5) * 300)
            + 720
            - (pbp_time[0] * 60)
            - pbp_time[1]
        )

        return pbp


class DeDupeTime(Task):
    """De-dupe time for model fitting."""

    def run(self, pbp: pd.DataFrame) -> pd.DataFrame:
        """De-dupe time for model fitting.

        Parameters
        ----------
        pbp : pd.DataFrame
            The (mostly) clean play-by-play data.

        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        grouped = pbp.groupby("GAME_ID")
        # Loop through each game
        for name, group in grouped:
            self.logger.info(f"De-duping ``TIME`` for game {name}")
            dupes = group.sort_values(
                by=["TIME", "EVENTNUM"], ascending=True
            ).duplicated(subset="TIME", keep="last")
            pbp.drop(dupes[dupes == True].index, inplace=True)

        return pbp
