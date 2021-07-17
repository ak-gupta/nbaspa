"""Simple tasks for loading data from the ``BaseRequest`` API."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import fsspec
import numpy as np
import pandas as pd
from prefect import Task

from ..factory import NBADataFactory
import nbaspa.data.endpoints as endpoints
from ..endpoints.parameters import ParameterValues, SEASONS


class GenericLoader(Task):
    """Load the data from a given endpoint.

    Parameters
    ----------
    loader : str
        The name of a class in the ``nba_survival.data.endpoints``
        subpackage.
    **kwargs
        Keyword arguments for ``prefect.Task``.

    Attributes
    ----------
    _loader : BaseRequest
        The object that will load the data.
    """

    def __init__(self, loader: str, **kwargs):
        """Init method."""
        self._loader = getattr(endpoints, loader)

        super().__init__(**kwargs)

    def run(  # type: ignore
        self,
        output_dir: str,
        filesystem: Optional[str] = "file",
        dataset_type: Optional[str] = None,
        **kwargs,
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Retrieve the data.

        Parameters
        ----------
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.
        **kwargs
            Keyword arguments for initializating the ``_loader``.

        Returns
        -------
        Dict
            A dictionary with one key per dataset in the output.
        """
        loader = self._loader(output_dir=output_dir, filesystem=filesystem, **kwargs)
        loader.load()
        if dataset_type is None:
            return {key: loader.get_data(key) for key in loader.datasets}
        else:
            return loader.get_data(dataset_type=dataset_type)


class FactoryGetter(Task):
    """Retrieve a dataset from ``NBADataFactory``."""

    def run(  # type: ignore
        self,
        factory: NBADataFactory,
        dataset_type: str = "default"
    ) -> pd.DataFrame:
        """Retrieve a dataset from ``NBADataFactory``.
        
        Parameters
        ----------
        factory : NBADataFactory
            The loaded factory class.
        dataset_type : str, optional (default "default")
            The dataset type.
        
        Returns
        -------
        pd.DataFrame
            The concatenated data.
        """
        return factory.get_data(dataset_type=dataset_type)

class PlayByPlayLoader(Task):
    """Load the play-by-data for a given day."""

    def run(  # type: ignore
        self,
        header: pd.DataFrame,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ) -> pd.DataFrame:
        """Load the play-by-play data for a given day.

        Parameters
        ----------
        header : pd.DataFrame
            The output of ``Scoreboard.get_data("GameHeader")``.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        pd.DataFrame
            The output dataset.
        """
        calls: List[Tuple[str, Dict]] = []
        games = np.unique(header["GAME_ID"])
        for game in games:
            calls.append(("PlayByPlay", {"GameID": game}))

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()
        data = factory.get_data()
        data["PLAYER1_ID"] = data["PLAYER1_ID"].astype(float)
        data["PLAYER2_ID"] = data["PLAYER2_ID"].astype(float)

        return data


class WinProbabilityLoader(Task):
    """Load the NBA win probability for each game in a day."""

    def run(  # type: ignore
        self,
        header: pd.DataFrame,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ) -> pd.DataFrame:
        """Load the NBA win probability for each game in a day.

        Parameters
        ----------
        header : pd.DataFrame
            The output of ``Scoreboard.get_data("GameHeader")``.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` implementation to use.

        Returns
        -------
        pd.DataFrame
            The output dataset.
        """
        calls: List[Tuple[str, Dict]] = []
        games = np.unique(header["GAME_ID"])
        for game in games:
            calls.append(("WinProbability", {"GameID": game}))

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data("WinProbPBP")


class GameLogLoader(Task):
    """Get team game logs."""

    teams: Set = ParameterValues().TeamID

    def run(  # type: ignore
        self,
        season: str,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ) -> pd.DataFrame:
        """Get team game logs.

        Parameters
        ----------
        season : str
            The season string.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        pd.DataFrame
            The output dataset.
        """
        calls: List[Tuple[str, Dict]] = []
        for team in self.teams:
            if not str(team).startswith("16"):
                continue

            calls.append(("TeamGameLog", {"TeamID": team, "Season": season}))

        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data()


class LineupLoader(Task):
    """Get team lineup stats.
    
    For lineup and overall team statistics we need to get rolling data over the season.
    """

    def run(  # type: ignore
        self,
        season: str,
        GameDate: str,
        linescore: pd.DataFrame,
    ) -> NBADataFactory:
        """Get team lineup stats.

        Parameters
        ----------
        season : str
            The season string.
        GameDate : str
            The game date.
        linescore : pd.DataFrame
            The output of ``Scoreboard.get_data("LineScore")``. We will use this to only
            pull the rolling data we need.

        Returns
        -------
        NBADataFactory
            Loaded data factory
        """
        GameDate = datetime.strptime(GameDate, "%m/%d/%Y")
        if (GameDate - SEASONS[season]["START"]).days < 14:
            self.logger.info("Pulling previous season data")
            if int(season[2:4]) - 1 < 10:
                season = "200" + str(int(season[2:4]) - 1) + "-" + season[2:4]
            else:
                season = "20" + str(int(season[2:4]) - 1) + "-" + season[2:4]
        GameDate = GameDate + timedelta(days=-1)
        calls: List[Tuple[str, Dict]] = []
        teams = np.unique(linescore["TEAM_ID"])
        for team in teams:
            params = {
                "TeamID": team,
                "Season": season,
                "MeasureType": "Advanced",
                "DateFrom": SEASONS[season]["START"].strftime("%m/%d/%Y"),
                "DateTo": GameDate.strftime("%m/%d/%Y")
            }

            calls.append(("TeamLineups", params))

        factory = NBADataFactory(calls=calls)
        factory.get()

        return factory


class RotationLoader(Task):
    """Load the team rotations for all games in a given day."""

    def run(  # type: ignore
        self,
        header: pd.DataFrame,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ) -> Dict[str, pd.DataFrame]:
        """Load the team rotations for all games in a given day.

        Parameters
        ----------
        header : pd.DataFrame
            The output of ``Scoreboard.get_data("GameHeader")``.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        Dict
            A dictionary with two keys: ``HomeTeam`` and ``AwayTeam``.
        """
        calls: List[Tuple[str, Dict]] = []
        games = np.unique(header["GAME_ID"])
        for game in games:
            calls.append(("GameRotation", {"GameID": game}))

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return {
            "HomeTeam": factory.get_data(dataset_type="HomeTeam"),
            "AwayTeam": factory.get_data(dataset_type="AwayTeam"),
        }


class ShotChartLoader(Task):
    """Load the shotcharts for all games in a given day."""

    def run(  # type: ignore
        self,
        header: pd.DataFrame,
        season: str,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ) -> Dict[str, pd.DataFrame]:
        """Load the shotcharts for all games in a given day.

        Parameters
        ----------
        header : pd.DataFrame
            The output of ``Scoreboard.get_data("GameHeader")``.
        season : str
            The season string.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        pd.DataFrame
            The shotcharts
        """
        calls: List[Tuple[str, Dict]] = []
        games = np.unique(header["GAME_ID"])
        for game in games:
            calls.append(("ShotChart", {"GameID": game, "Season": season}))

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data()


class BoxScoreLoader(Task):
    """Load all boxscores for games in in a given day."""

    def run(  # type: ignore
        self,
        header: pd.DataFrame,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ) -> pd.DataFrame:
        """Load all boxscores for games in a given day.

        Parameters
        ----------
        header : pd.DataFrame
            The output of ``Scoreboard.get_data("GameHeader")``.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        pd.DataFrame
            The output dataset.
        """
        calls: List[Tuple[str, Dict]] = []
        games = np.unique(header["GAME_ID"])
        for game in games:
            calls.append(("BoxScoreTraditional", {"GameID": game}))

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data("PlayerStats")


class ShotZoneLoader(Task):
    """Load the shot zone data for each player in each game."""

    def run(  # type: ignore
        self,
        season: str,
        GameDate: str,
        boxscore: pd.DataFrame,
    ) -> pd.DataFrame:
        """Load the shot zone data for each player in each game.

        Parameters
        ----------
        season : str
            The season string.
        GameDate : str
            The game date.
        boxscore : pd.DataFrame
            The output from ``BoxScoreTraditional.get_data("PlayerStats")``.

        Returns
        -------
        pd.DataFrame
            The output dataset.
        """
        GameDate = datetime.strptime(GameDate, "%m/%d/%Y")
        if (GameDate - SEASONS[season]["START"]).days < 14:
            self.logger.info("Pulling previous season data")
            if int(season[2:4]) - 1 < 10:
                season = "200" + str(int(season[2:4]) - 1) + "-" + season[2:4]
            else:
                season = "20" + str(int(season[2:4]) - 1) + "-" + season[2:4]
        GameDate = GameDate + timedelta(days=-1)
        calls: List[Tuple[str, Dict]] = []
        for _, row in boxscore.iterrows():
            if pd.isnull(row["MIN"]):
                continue
            calls.append(
                (
                    "PlayerDashboardShooting",
                    {
                        "PlayerID": row["PLAYER_ID"],
                        "Season": season,
                        "DateFrom": SEASONS[season]["START"].strftime("%m/%d/%Y"),
                        "DateTo": GameDate.strftime("%m/%d/%Y")
                    },
                )
            )

        # Create the factory and load the data
        factory = NBADataFactory(calls=calls)
        factory.get()

        return factory.get_data("ShotAreaPlayerDashboard")


class GeneralShootingLoader(Task):
    """Load the general shooting data for each player in each game."""

    def run(  # type: ignore
        self,
        season: str,
        GameDate: str,
        boxscore: pd.DataFrame,
    ) -> pd.DataFrame:
        """Load the general shooting data for each player in each game.

        Parameters
        ----------
        season : str
            The season string.
        GameDate : str
            The game date.
        boxscore : pd.DataFrame
            The output from ``BoxScoreTraditional.get_data("PlayerStats")``.

        Returns
        -------
        pd.DataFrame
            The output dataset.
        """
        GameDate = datetime.strptime(GameDate, "%m/%d/%Y")
        if (GameDate - SEASONS[season]["START"]).days < 14:
            self.logger.info("Pulling previous season data")
            season = "20" + str(int(season[2:4]) - 1) + "-" + season[2:4]
        GameDate = GameDate + timedelta(days=-1)
        calls: List[Tuple[str, Dict]] = []
        for _, row in boxscore.iterrows():
            if pd.isnull(row["MIN"]):
                continue
            calls.append(
                (
                    "PlayerDashboardGeneral",
                    {
                        "PlayerID": row["PLAYER_ID"],
                        "Season": season,
                        "DateFrom": SEASONS[season]["START"].strftime("%m/%d/%Y"),
                        "DateTo": GameDate.strftime("%m/%d/%Y")
                    },
                )
            )

        # Create the factory and load the data
        factory = NBADataFactory(calls=calls)
        factory.get()

        return factory.get_data("OverallPlayerDashboard")


class SaveData(Task):
    """Save the game data."""

    def run(  # type: ignore
        self,
        data: pd.DataFrame,
        output_dir: str,
        filesystem: Optional[str] = "file",
        mode: Optional[str] = "model",
    ):
        """Save the game data.

        Saves the data to ``output_dir/data_{GameID}.csv``

        Parameters
        ----------
        data : pd.DataFrame
            The clean data.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.
        mode : str, optional (default "model")
            The type of clean data to save. If ``model``, save to the directory
            ``model-data``. If ``rating``, save to ``rating-data``.

        Returns
        -------
        None
        """
        # Define subdirectory
        if mode == "model":
            subdir = "model-data"
        elif mode == "rating":
            subdir = "rating-data"
        else:
            raise ValueError("Please supply a valid value for ``mode``")
        # Get the filesystem
        fs = fsspec.filesystem(filesystem)
        fs.mkdir(Path(output_dir, subdir))
        grouped = data.groupby("GAME_ID")
        for name, group in grouped:
            if not name.startswith("002"):
                self.logger.warning(f"{name} is not a regular season game. Skipping...")
                continue
            fpath = Path(output_dir, subdir, f"data_{name}.csv")
            self.logger.info(f"Writing data for game {name} to {str(fpath)}")
            with fs.open(fpath, "wb") as buf:
                group.to_csv(buf, sep="|", mode="wb")
