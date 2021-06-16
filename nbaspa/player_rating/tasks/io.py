"""Loaders."""

from pathlib import Path
import re
from typing import Dict, List, Optional

import fsspec
import pandas as pd
from prefect import Task

from ...data.endpoints import BoxScoreTraditional


class GetGamesList(Task):
    """Get the list of games for the glob."""

    def run(
        self, data_dir: str, Season: Optional[str] = None, GameID: Optional[str] = None,
    ) -> List[Dict]:
        """Get the list of games for the glob.

        The list of files will be limited to the available rating data.

        Parameters
        ----------
        data_dir : str
            The directory containing the data.
        Season : str, optional (default None)
            The season for the data. If not provided, all seasons will be loaded.
        GameID : str, optional (default None)
            The game identifier. If not provided, all games will be loaded.
        
        Returns
        -------
        List
            A list of dictionaries, with each object containing the Season and the GameID.
        """
        fileglob = f"{Season or '*'}/rating-data/data_{GameID or '*'}.csv"
        files = list(Path(data_dir).glob(fileglob))
        pattern = re.compile(r"^data_(?P<game>[0-9]*).csv")

        return [
            {
                "Season": game.parts[1],
                "GameID": pattern.match(game.parts[-1]).group("game")
            } for game in files
        ]

class LoadRatingData(Task):
    """Load the clean NBA play-by-play data."""

    def run(  # type: ignore
        self, data_dir: str, filelocation: Dict
    ) -> pd.DataFrame:
        """Load the clean NBA play-by-play data.

        Parameters
        ----------
        data_dir : str
            The directory containing the data.
        filelocation : dict
            The season and GameID of the game.

        Returns
        -------
        pd.DataFrame
            The clean play-by-play data.
        """
        self.logger.info(f"Reading in game {filelocation['GameID']} from {data_dir}")
        basedata = pd.read_csv(
            Path(data_dir, filelocation["Season"], "rating-data", f"data_{filelocation['GameID']}.csv"),
            sep="|",
            dtype={"GAME_ID": str},
            index_col=0
        )

        return basedata


class BoxScoreLoader(Task):
    """Load the boxscore data."""

    def run(  # type: ignore
        self, filelocation: Dict, output_dir: str, filesystem: str = "file"
    ) -> pd.DataFrame:
        """Load the boxscore data.

        Parameters
        ----------
        filelocation : dict
            The season and GameID of the game.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        pd.DataFrame
            The player-level boxscore data.
        """
        loader = BoxScoreTraditional(
            output_dir=Path(output_dir, filelocation["Season"]),
            GameID=filelocation["GameID"],
            filesystem=filesystem,
        )
        loader.load()

        return loader.get_data("PlayerStats")


class LoadSurvivalPredictions(Task):
    """Load the survival probability predictions."""

    def run(  # type: ignore
        self, data_dir: str, filelocation: Dict
    ) -> pd.DataFrame:
        """Load the survival prediction data.

        Parameters
        ----------
        data_dir : str
            The directory containing multiple seasons of data.
        filelocation : dict
            The season and GameID of the game.
        
        Returns
        -------
        pd.DataFrame
            The output DataFrame.
        """
        self.logger.info(f"Reading in {filelocation['GameID']} from {data_dir}")
        basedata = pd.read_csv(
            Path(data_dir, filelocation["Season"], "survival-prediction", f"data_{filelocation['GameID']}.csv"),
            sep="|",
            dtype={"GAME_ID": str},
            index_col=0
        )

        return basedata


class SaveImpactData(Task):
    """Save the impact data.
    
    Parameters
    ----------
    pbp : bool
        Whether to save the data as play-by-play or aggregated.
    **kwargs
        Prefect keyword arguments.
    """

    def __init__(self, pbp: bool, **kwargs):
        """Init method."""
        self._subdir = "pbp-impact" if pbp else "game-impact"
        super().__init__(**kwargs)
    

    def run(  # type: ignore
        self,
        data: pd.DataFrame,
        output_dir: str,
        filelocation: Dict,
        filesystem: str = "file"
    ):
        """Save the impact data.

        Parameters
        ----------
        data : pd.DataFrame
            The impact data.
        output_dir : str
            The directory for the data.
        filelocation : dict
            The season and GameID of the game.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.
        
        Returns
        -------
        None
        """
        # Get the filesystem
        fs = fsspec.filesystem(filesystem)
        fdir = Path(output_dir, filelocation["Season"], self._subdir)
        fs.mkdir(fdir)
        fpath = fdir / f"data_{filelocation['GameID']}.csv"
        self.logger.info(f"Writing data for game {filelocation['GameID']} to {str(fpath)}")
        with fs.open(fpath, "wb") as buf:
            data.to_csv(buf, sep="|", mode="wb")
