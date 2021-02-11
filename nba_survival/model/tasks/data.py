"""Data tasks."""

from lifelines.utils import add_covariate_to_timeline, to_long_format
import pandas as pd
from prefect import Task

from nba_survival.model.tasks.meta import META

class LifelinesData(Task):
    """Create time-varying data in the ``lifelines`` format."""
    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create time-varying data in the ``lifelines`` format.

        Parameters
        ----------
        data : pd.DataFrame
            The cleaned play-by-play data.
        
        Returns
        -------
        pd.DataFrame
            The lifelines-compliant data.
        """
        # Create the short form data
        shortform = data.groupby(META["id"]).tail(1)[
            [META["id"]] + [META["duration"]] + [META["event"]] + META["static"]
        ]
        base = to_long_format(shortform, duration_col=META["duration"])
        # Create the longform data
        longform = add_covariate_to_timeline(
            base,
            data[[META["id"]] + [META["duration"]] + META["dynamic"]],
            duration_col=META["duration"],
            id_col=META["id"],
            event_col=META["event"]
        )

        return longform
