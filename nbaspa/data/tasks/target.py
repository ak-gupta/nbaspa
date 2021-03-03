"""CreateTarget.

Creates the win indicator.
"""

import pandas as pd
from prefect import Task


class CreateTarget(Task):
    """Create the target boolean."""

    def run(self, pbp: pd.DataFrame) -> pd.DataFrame: # type: ignore
        """Create the target boolean.

        Adds the following column:

        * ``WIN``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``FillMargin``.

        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        pbp.sort_values(by=["TIME", "EVENTNUM"], ascending=True, inplace=True)
        pbp["WIN"] = pbp.groupby("GAME_ID").tail(1)["SCOREMARGIN"] > 0
        pbp["WIN"] = pbp["WIN"].fillna(False)
        pbp["WIN"] = pbp["WIN"].astype(int)

        return pbp
