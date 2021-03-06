"""Loaders."""

from pathlib import Path

import fsspec
import pandas as pd
from prefect import Task

from ...data.endpoints import BoxScoreTraditional


class LoadRatingData(Task):
    """Load the clean NBA play-by-play data."""

    def run(  # type: ignore
        self, GameID: str, output_dir: str, filesystem: str = "file"
    ) -> pd.DataFrame:
        """Load the clean NBA play-by-play data.

        Parameters
        ----------
        GameID : str
            The game identifier.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        pd.DataFrame
            The clean play-by-play data.
        """
        fpath = Path(output_dir, "rating-data", f"data_{GameID}.csv")
        fs = fsspec.filesystem(filesystem)
        if fs.exists(fpath):
            with fs.open(fpath, "rb") as infile:
                data = pd.read_csv(infile, sep="|", dtype={"GAME_ID": str}, index_col=0)
        else:
            raise ValueError(f"File {str(fpath)} does not exist")

        return data


class BoxScoreLoader(Task):
    """Load the boxscore data."""

    def run(  # type: ignore
        self, GameID: str, output_dir: str, filesystem: str = "file"
    ) -> pd.DataFrame:
        """Load the boxscore data.

        Parameters
        ----------
        GameID : str
            The game identifier.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        pd.DataFrame
            The player-level boxscore data.
        """
        box = BoxScoreTraditional(
            GameID=GameID, output_dir=output_dir, filesystem=filesystem
        )
        box.load()

        return box.get_data("PlayerStats")
