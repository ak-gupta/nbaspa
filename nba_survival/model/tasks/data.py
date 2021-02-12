"""Data tasks."""

from typing import Dict, List, Optional

from lifelines.utils import add_covariate_to_timeline, to_long_format
import numpy as np
import pandas as pd
from prefect import Task

from .meta import META

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
        # Drop any rows with the same start and stop time
        longform.drop(
            longform[longform["start"] == longform["stop"]].index, inplace=True
        )

        return longform


class SegmentData(Task):
    """Split up the longform data."""
    def run(
        self,
        data: pd.DataFrame,
        splits: Optional[List[float]] = [0.8, 0.2],
        keys: Optional[List[str]] = ["train", "test"],
        seed: int = 42,
    ) -> Dict[str, pd.DataFrame]:
        """Split the longform data for model training.

        Splits the data by ``GAME_ID`` value.

        Parameters
        ----------
        data : pd.DataFrame
            The initial dataframe.
        splits : list, optional (default [0.8, 0.2])
            The percentage of games that should be included in each output
            dataset.
        keys : list, optional (default ["train", "test"])
            The dictionary keys for the output.
        seed : int, optional (default 42)
            The seed for sampling

        Returns
        -------
        Dict
            A dictionary with one key per split.
        """
        self.logger.info(f"Setting the seed to {seed}")
        np.random.seed(seed)

        # Get an array of the unique GAME_ID values
        games = np.unique(data[META["id"]])
        # Split
        splits = np.split(
            games, [int(len(games) * perc) for perc in splits]
        )
        output: Dict = {}
        for index, value in enumerate(keys):
            output[value] = data[data[META["id"]].isin(splits[index])].copy()
        
        return output
