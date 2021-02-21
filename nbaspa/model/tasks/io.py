"""I/O tasks for the model fitting/evaluation pipelines."""

from pathlib import Path
from typing import Optional, Tuple

import cloudpickle
import pandas as pd
from prefect import Task, task


@task
def load_df(data_dir: str, dataset: Optional[str] = "build.csv") -> pd.DataFrame:
    """Load the pandas dataframe.

    Parameters
    ----------
    data_dir : str
        The data directory
    dataset : str, optional (default "build.csv")
        The filename in the directory

    Returns
    -------
    pd.DataFrame
        The dataframe.
    """
    return pd.read_csv(
        Path(data_dir, "models", dataset), sep="|", index_col=0, dtype={"GAME_ID": str}
    )


class LoadData(Task):
    """Load clean data to a DataFrame."""

    def run(self, data_dir: str) -> pd.DataFrame:
        """Load clean data to a DataFrame.

        Parameters
        ----------
        data_dir : str
            The directory containing multiple seasons of data.

        Returns
        -------
        pd.DataFrame
            The output dataframe.
        """
        self.logger.info(f"Reading clean data from {data_dir}")
        basedata = pd.concat(
            pd.read_csv(fpath, sep="|", dtype={"GAME_ID": str}, index_col=0)
            for fpath in Path(data_dir).glob("*/model-data/data_*.csv")
        ).reset_index(drop=True)

        return basedata


class LoadModel(Task):
    """Load model object using ``cloudpickle``."""

    def run(self, filepath: str) -> Tuple:
        """Load model object using ``cloudpickle``.

        Parameters
        ----------
        filepath : str
            The path to the ``.pkl`` object.

        Returns
        -------
        Dict
            A dictionary with the matching key in ``**kwargs``. The value is
            the model object.
        """
        self.logger.info(f"Reading model object from {filepath}")
        with open(Path(filepath), "rb") as infile:
            model = cloudpickle.load(infile)

        return model
