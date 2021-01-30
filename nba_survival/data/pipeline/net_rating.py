"""Add the net rating for each team."""

import pandas as pd
from prefect import Task

class AddNetRating(Task):
    """Add the net rating for each team."""
    def run(self, pbp: pd.DataFrame, stats: pd.DataFrame) -> pd.DataFrame:
        """Add the net rating for each team.

        Adds the following columns:

        * ``HOME_NET_RATING``
        * ``VISITOR_NET_RATING``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``AddTeamID``
        stats : pd.DataFrame
            The output from ``TeamStats.get_data()``.
        
        Returns
        -------
        pd.DataFrame
            The updated datasets.
        """
        pbp["HOME_NET_RATING"] = pbp.merge(
            stats[["TEAM_ID", "E_NET_RATING"]],
            left_on="HOME_TEAM_ID",
            right_on="TEAM_ID",
            how="left"
        )["E_NET_RATING"]
        pbp["VISITOR_NET_RATING"] = pbp.merge(
            stats[["TEAM_ID", "E_NET_RATING"]],
            left_on="VISITOR_TEAM_ID",
            right_on="TEAM_ID",
            how="left"
        )["E_NET_RATING"]

        return pbp
