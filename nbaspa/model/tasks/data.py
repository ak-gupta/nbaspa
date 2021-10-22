"""Data tasks."""

from typing import Dict, List, Optional

from lifelines.utils import add_covariate_to_timeline, to_long_format
import numpy as np
import pandas as pd
from prefect import Task
from sklearn.model_selection import StratifiedShuffleSplit

from .meta import META


class SurvivalData(Task):
    """Create time-varying data in the ``lifelines`` format."""

    def run(self, data: pd.DataFrame, swap: bool = False) -> pd.DataFrame:  # type: ignore
        """Create time-varying data in the ``lifelines`` format.

        Parameters
        ----------
        data : pd.DataFrame
            The cleaned play-by-play data.
        swap : bool, optional (default False)
            Whether the input data includes exogenous variables or not

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
            data, left_on=("GAME_ID", "stop"), right_on=("GAME_ID", "TIME"), how="left"
        )[META["benchmark"]]

        # If for swap purposes, remove exogenous variables
        if swap:
            for col in META["dynamic"]:
                if col == "SCOREMARGIN":
                    continue
                longform[col] = 0.0
            for col in META["static"]:
                longform[col] = 0.0

        return longform


class SegmentData(Task):
    """Split up the longform data."""

    def run(  # type: ignore
        self,
        data: pd.DataFrame,
        splits: List[float] = [0.8, 0.2],
        keys: List[str] = ["train", "test"],
        seed: int = 42,
    ) -> Dict[str, pd.DataFrame]:
        """Split the longform data for model training.

        Splits the data by ``GAME_ID`` value using stratified sampling to ensure
        each dataset adequately represents the entire input data.

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
        games = data[[META["id"], META["event"]]].copy()
        games[META["event"]] = games[META["event"]].astype(int)
        games = games.groupby(META["id"]).tail(n=1)
        games["indicator"] = games[META["id"]].str[2:5] + games[META["event"]].astype(
            str
        )
        # Split
        if isinstance(splits, tuple):
            splits = list(splits)
        split_arrays = []
        while len(splits) > 1:
            # Create the splitter
            splitter = StratifiedShuffleSplit(
                n_splits=1, test_size=np.sum(splits[1:]) / np.sum(splits)
            )
            self.logger.info(f"Retrieving {splits[0]} proportion from the data")
            # Split the data
            train_games, test_games = next(splitter.split(games, games["indicator"]))
            split_arrays.append(games.iloc[train_games][META["id"]].to_numpy())
            # Remove the first set for the next iteration
            games = games.iloc[test_games].reset_index(drop=True)
            splits.pop(0)
        split_arrays.append(games[META["id"]].to_numpy())

        output: Dict = {}
        for index, value in enumerate(keys):
            output[value] = data[data[META["id"]].isin(split_arrays[index])].copy()
            self.logger.info(
                f"Dataset ``{value}`` has {len(split_arrays[index])} games with "
                f"{len(output[value])} rows"
            )

        return output


class CollapseData(Task):
    """Collapse data for evaluation."""

    def run(  # type: ignore
        self,
        data: pd.DataFrame,
        timestep: Optional[int] = None,
        pregame: bool = False,
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
        pregame : bool, optional (default False)
            Whether or not to create pregame predictions.

        Returns
        -------
        pd.DataFrame
            The collapsed data.
        """
        if pregame:
            self.logger.info("Creating pregame data")
            first_row = data.groupby(META["id"]).head(n=1).copy()
            first_row["start"] = 0
            first_row["stop"] = 0
            
            return first_row
        elif timestep is None:
            final_row = data.groupby(META["id"]).tail(n=1).copy()

            return final_row
        else:
            self.logger.info(f"Collapsing the data to time {timestep}")
            shortform = data[data["start"] <= timestep].copy()
            shortform = shortform.groupby(META["id"]).tail(n=1).copy()
            # Add the final win predictor
            shortform.set_index(META["id"], inplace=True)
            shortform["WIN"] = data.groupby(META["id"])["WIN"].sum()
            shortform.reset_index(inplace=True)

            return shortform
