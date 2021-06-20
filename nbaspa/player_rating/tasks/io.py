"""Loaders."""

import datetime
from pathlib import Path
import re
from typing import Dict, List, Optional

import fsspec
import pandas as pd
from prefect import Task

from ...data.endpoints import BoxScoreTraditional
from ...data.endpoints.parameters import SEASONS
from ...data.factory import NBADataFactory


class GetGamesList(Task):
    """Get the list of games for the glob."""

    def run(  # type: ignore
        self,
        data_dir: str,
        Season: Optional[str] = None,
        GameID: Optional[str] = None,
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

        filelist = []
        for game in files:
            gameinfo = {"Season": game.parts[1]}
            match = pattern.match(game.parts[-1])
            if match is not None:
                gameinfo["GameID"] = match.group("game")

            filelist.append(gameinfo)

        return filelist


class LoadRatingData(Task):
    """Load the clean NBA play-by-play data."""

    def run(self, data_dir: str, filelocation: Dict) -> pd.DataFrame:  # type: ignore
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
            Path(
                data_dir,
                filelocation["Season"],
                "rating-data",
                f"data_{filelocation['GameID']}.csv",
            ),
            sep="|",
            dtype={"GAME_ID": str},
            index_col=0,
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
            output_dir=str(Path(output_dir, filelocation["Season"])),
            GameID=filelocation["GameID"],
            filesystem=filesystem,
        )
        loader.load()

        return loader.get_data("PlayerStats")


class ScoreboardLoader(Task):
    """Load the scoreboard data."""

    def run(self, data_dir: str, filelist: List[Dict]):  # type: ignore
        """Load the scoreboard data.

        Parameters
        ----------
        data_dir : str
            The directory containing multiple seasons of data.
        filelist : list
            The output from ``GetGamesList``

        Returns
        -------
        pd.DataFrame
            The ``GameHeader`` dataset from ``nbaspa.data.endpoints.Scoreboard``
        """
        unq_seasons = set(game["Season"] for game in filelist)
        calls = []
        for season in unq_seasons:
            for n in range(
                int((SEASONS[season]["END"] - SEASONS[season]["START"]).days) + 1
            ):
                game_date = SEASONS[season]["START"] + datetime.timedelta(n)
                calls.append(
                    (
                        "Scoreboard",
                        {
                            "GameDate": game_date.strftime("%m/%d/%Y"),
                            "output_dir": str(Path(data_dir, season)),
                        },
                    )
                )
        loader = NBADataFactory(calls=calls)
        loader.load()

        return loader.get_data("GameHeader")


class LoadSurvivalPredictions(Task):
    """Load the survival probability predictions."""

    def run(self, data_dir: str, filelocation: Dict) -> pd.DataFrame:  # type: ignore
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
            Path(
                data_dir,
                filelocation["Season"],
                "survival-prediction",
                f"data_{filelocation['GameID']}.csv",
            ),
            sep="|",
            dtype={"GAME_ID": str},
            index_col=0,
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
        filesystem: str = "file",
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
        self.logger.info(
            f"Writing data for game {filelocation['GameID']} to {str(fpath)}"
        )
        with fs.open(fpath, "wb") as buf:
            data.to_csv(buf, sep="|", mode="wb")


class SavePlayerTimeSeries(Task):
    """Save player-level time-series data."""

    def run(  # type: ignore
        self,
        data: List[pd.DataFrame],
        header: pd.DataFrame,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ):
        """Save player-level time-series data.

        Parameters
        ----------
        data : list
            The list of game-level impact.
        header : pd.DataFrame
            The header data.
        output_dir : str
            The directory for the output data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        None
        """
        data = pd.concat(data, ignore_index=True)
        data["SEASON"] = (
            data["GAME_ID"].str[2]
            + "0"
            + data["GAME_ID"].str[3:5]
            + "-"
            + (data["GAME_ID"].str[3:5].astype(int) + 1).astype(str)
        )
        # Add the game date
        data["GAME_DATE"] = pd.merge(
            data, header, left_on="GAME_ID", right_on="GAME_ID", how="left"
        )["GAME_DATE_EST"]
        # Loop through each player/season
        fs = fsspec.filesystem(filesystem)
        for name, group in data.groupby(["PLAYER_ID", "SEASON"]):
            fdir = Path(output_dir, name[1], "impact-timeseries")
            fs.mkdir(fdir)
            fpath = fdir / f"data_{name[0]}.csv"
            with fs.open(fpath, "wb") as buf:
                group.to_csv(buf, sep="|", mode="wb")


class SaveTopPlayers(Task):
    """Save a summary of player performance over multiple games."""

    def run(self, data: List[pd.DataFrame], output_dir: str):  # type: ignore
        """Save a summary of player performance.

        Parameters
        ----------
        data : list
            A list of dataframes to save.
        output_dir : str
            The directory for the data.
        filelist : list
            A list of file locations.
        """
        data = pd.concat(data, ignore_index=True)
        data["SEASON"] = (
            data["GAME_ID"].str[2]
            + "0"
            + data["GAME_ID"].str[3:5]
            + "-"
            + (data["GAME_ID"].str[3:5].astype(int) + 1).astype(str)
        )
        for name, group in data.groupby("SEASON"):
            avg = group.groupby("PLAYER_ID")["IMPACT"].agg(["sum", "mean"])
            avg.rename(
                columns={"sum": "TOTAL_IMPACT", "mean": "MEAN_IMPACT"}, inplace=True
            )
            avg.reset_index(inplace=True)
            self.logger.info(
                f"Saving {name} summary to {str(Path(output_dir, name, 'impact-summary.csv'))}"
            )
            avg.to_csv(
                Path(output_dir, name, "impact-summary.csv"),
                sep="|",
            )
