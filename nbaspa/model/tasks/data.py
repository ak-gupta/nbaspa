"""Data tasks."""

from typing import Dict, List, Optional

from lifelines.utils import add_covariate_to_timeline, to_long_format
import numpy as np
import pandas as pd
from prefect import Task

from .meta import META


class SurvivalData(Task):
    """Create time-varying data in the ``lifelines`` format."""

    def run(self, data: pd.DataFrame) -> pd.DataFrame: # type: ignore
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
        self.logger.info(
            f"Dropping {sum(pd.isnull(data[META['benchmark']]))} rows with null "
            "benchmark probabilities"
        )
        data = data[~pd.isnull(data[META["benchmark"]])].copy()
        # Create the short form data
        shortform = (
            data.groupby(META["id"])
            .tail(1)[
                [META["id"]] + [META["duration"]] + [META["event"]] + META["static"]
            ]
            .copy()
        )
        base = to_long_format(shortform, duration_col=META["duration"])
        # Create the longform data
        longform = add_covariate_to_timeline(
            base,
            data[[META["id"]] + [META["duration"]] + META["dynamic"]],
            duration_col=META["duration"],
            id_col=META["id"],
            event_col=META["event"],
        )
        # Drop any rows with the same start and stop time
        longform.drop(
            longform[longform["start"] == longform["stop"]].index, inplace=True
        )
        # Add the NBA win probability to the dataset
        longform[META["benchmark"]] = longform.merge(
            data,
            left_on=("GAME_ID", "stop"),
            right_on=("GAME_ID", "TIME"),
            how="left"
        )[META["benchmark"]]

        return longform


class SegmentData(Task):
    """Split up the longform data."""

    def run( # type: ignore
        self,
        data: pd.DataFrame,
        splits: List[float] = [0.85],
        keys: List[str] = ["train", "test"],
        seed: int = 42,
    ) -> Dict[str, pd.DataFrame]:
        """Split the longform data for model training.

        Splits the data by ``GAME_ID`` value.

        Parameters
        ----------
        data : pd.DataFrame
            The initial dataframe.
        splits : list, optional (default [0.85])
            The percentage of games that should be included in each output
            dataset. The length of this array should be one less than the
            number of keys
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
        np.random.shuffle(games)
        # Split
        splits = np.split(
            games,
            [
                int(len(games) * np.sum(splits[: (index + 1)]))
                for index in range(len(splits))
            ],
        )
        output: Dict = {}
        for index, value in enumerate(keys):
            output[value] = data[data[META["id"]].isin(splits[index])].copy()
            self.logger.info(
                f"Dataset ``{value}`` has {len(splits[index])} games with {len(output[value])} rows"
            )

        return output


class CollapseData(Task):
    """Collapse data for evaluation."""

    def run( # type: ignore
        self,
        data: pd.DataFrame,
        timestep: Optional[int] = None,
    ) -> pd.DataFrame:
        """Collapse data for evaluation.

        We will take the input data from time value ``timestep`` but evaluate
        the metric using the final time to event.

        Parameters
        ----------
        data : pd.DataFrame
            The ouptut of ``SurvivalData``.
        timestep : int, optional (default None)
            The time step to use to create unique rows. If ``None``, the final row
            for each game will be used.

        Returns
        -------
        pd.DataFrame
            The collapsed data.
        """
        if timestep is None:
            final_row = data.groupby(META["id"]).tail(n=1).copy()

            return final_row
        else:
            self.logger.info(f"Collapsing the data to time {timestep}")
            shortform = data[data["start"] <= timestep].copy()
            shortform = shortform.groupby(META["id"]).tail(n=1).copy()
            if timestep == 0:
                self.logger.info("Removing time-varying effects")
                for col in META["dynamic"]:
                    shortform[col] = 0
            # Add the final win predictor
            shortform.set_index(META["id"], inplace=True)
            shortform["WIN"] = data.groupby(META["id"])["WIN"].sum()
            shortform.reset_index(inplace=True)

            return shortform
