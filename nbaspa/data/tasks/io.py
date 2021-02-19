"""Simple tasks for loading data from the ``BaseRequest`` API."""

from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import fsspec
import pandas as pd
from prefect import Task

from ..factory import NBADataFactory
import nbaspa.data.endpoints as endpoints
from ..endpoints.parameters import ParameterValues


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

    def run(
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


class PlayByPlayLoader(Task):
    """Load the play-by-data for a given day."""

    def run(
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
        calls: List[str] = []
        for _, row in header.iterrows():
            calls.append(("PlayByPlay", {"GameID": row["GAME_ID"]}))

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data()


class WinProbabilityLoader(Task):
    """Load the NBA win probability for each game in a day."""

    def run(
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
        calls: List[str] = []
        for _, row in header.iterrows():
            calls.append(("WinProbability", {"GameID": row["GAME_ID"]}))

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data("WinProbPBP")


class GameLogLoader(Task):
    """Get team game logs."""

    teams: Set = ParameterValues().TeamID

    def run(
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
        calls: List[str] = []
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
    """Get team lineup stats."""

    teams: Set = ParameterValues().TeamID

    def run(
        self,
        season: str,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ) -> pd.DataFrame:
        """Get team lineup stats.

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
        calls: List[str] = []
        for team in self.teams:
            if not str(team).startswith("16"):
                continue

            calls.append(("TeamLineups", {"TeamID": team, "Season": season}))

        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data("Lineups")


class RotationLoader(Task):
    """Load the team rotations for all games in a given day."""

    def run(
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
        calls: List[str] = []
        for _, row in header.iterrows():
            calls.append(("GameRotation", {"GameID": row["GAME_ID"]}))

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

    def run(
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
        calls: List[str] = []
        for _, row in header.iterrows():
            calls.append(("ShotChart", {"GameID": row["GAME_ID"], "Season": season}))

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data()


class BoxScoreLoader(Task):
    """Load all boxscores for games in in a given day."""

    def run(
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
        calls: List[str] = []
        for _, row in header.iterrows():
            calls.append(("BoxScoreTraditional", {"GameID": row["GAME_ID"]}))

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data("PlayerStats")


class ShotZoneLoader(Task):
    """Load the shot zone data for each player in each game."""

    def run(
        self,
        boxscore: pd.DataFrame,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ) -> pd.DataFrame:
        """Load the shot zone data for each player in each game.

        Parameters
        ----------
        boxscore : pd.DataFrame
            The output from ``BoxScoreTraditional.get_data("PlayerStats")``.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        pd.DataFrame
            The output dataset.
        """
        calls: List[str] = []
        for _, row in boxscore.iterrows():
            if pd.isnull(row["MIN"]):
                continue
            calls.append(
                (
                    "PlayerDashboardShooting",
                    {"PlayerID": row["PLAYER_ID"], "Season": "2018-19"},
                )
            )

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data("ShotAreaPlayerDashboard")


class GeneralShootingLoader(Task):
    """Load the general shooting data for each player in each game."""

    def run(
        self,
        boxscore: pd.DataFrame,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ) -> pd.DataFrame:
        """Load the general shooting data for each player in each game.

        Parameters
        ----------
        boxscore : pd.DataFrame
            The output from ``BoxScoreTraditional.get_data("PlayerStats")``.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        pd.DataFrame
            The output dataset.
        """
        calls: List[str] = []
        for _, row in boxscore.iterrows():
            if pd.isnull(row["MIN"]):
                continue
            calls.append(
                (
                    "PlayerDashboardGeneral",
                    {"PlayerID": row["PLAYER_ID"], "Season": "2018-19"},
                )
            )

        # Create the factory and load the data
        factory = NBADataFactory(
            calls=calls, output_dir=output_dir, filesystem=filesystem
        )
        factory.load()

        return factory.get_data("OverallPlayerDashboard")


class SaveData(Task):
    """Save the game data."""

    def run(
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
