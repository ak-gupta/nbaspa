"""I/O tasks for the model fitting/evaluation pipelines."""

from pathlib import Path
from typing import Optional, Tuple

import cloudpickle
import fsspec
import pandas as pd
from prefect import Task, task

from .meta import META


@task
def load_df(data_dir: str, dataset: str = "build.csv") -> pd.DataFrame:
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

    def run(  # type: ignore
        self,
        data_dir: str,
        season: Optional[str] = None,
        gameid: Optional[str] = None,
    ) -> pd.DataFrame:
        """Load clean data to a DataFrame.

        Parameters
        ----------
        data_dir : str
            The directory containing multiple seasons of data.
        season : str, optional (default None)
            The season for the data. If not provided, all seasons will be searched
        gameid : str, optional (default None)
            The game to read. If not provided, all games will be searched.

        Returns
        -------
        pd.DataFrame
            The output dataframe.
        """
        fileglob = f"{season or '*'}/model-data/data_{gameid or '*'}.csv"
        self.logger.info(f"Reading clean data from {data_dir}")
        basedata = pd.concat(
            pd.read_csv(fpath, sep="|", dtype={"GAME_ID": str}, index_col=0)
            for fpath in Path(data_dir).glob(fileglob)
        ).reset_index(drop=True)

        return basedata


class LoadModel(Task):
    """Load model object using ``cloudpickle``."""

    def run(self, filepath: str) -> Tuple:  # type: ignore
        """Load model object using ``cloudpickle``.

        Parameters
        ----------
        filepath : str
            The path to the ``.pkl`` object.

        Returns
        -------
        xgb.Booster or CoxTimeVaryingFitter
            The trained model object.
        IsotonicRegression
            The fitted calibrator
        """
        self.logger.info(f"Reading model object from {filepath}")
        with open(Path(filepath), "rb") as infile:
            model = cloudpickle.load(infile)
        self.logger.info("Reading model calibrator")
        with open(Path(filepath).parent / "calibrator.pkl", "rb") as infile:
            calibrator = cloudpickle.load(infile)

        return model, calibrator


class SavePredictions(Task):
    """Save the game data."""

    def run(  # type: ignore
        self,
        data: pd.DataFrame,
        output_dir: str,
        filesystem: Optional[str] = "file",
        swap: bool = False,
    ):
        """Save the game data.

        Parameters
        ----------
        data : pd.DataFrame
            The clean data.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.
        swap : bool, optional (default False)
            Whether the input data is a swap probability (no exogenous variables).

        Returns
        -------
        None
        """
        # Get the filesystem
        fs = fsspec.filesystem(filesystem)
        grouped = data.groupby(META["id"])
        for name, group in grouped:
            if not name.startswith("002"):
                self.logger.warning(f"{name} is not a regular season game. Skipping...")
                continue
            if int(name[3:5]) + 1 < 10:
                season = name[2] + "0" + name[3:5] + "-0" + str(int(name[3:5]) + 1)
            else:
                season = name[2] + "0" + name[3:5] + "-" + str(int(name[3:5]) + 1)
            if swap:
                fdir = Path(output_dir, season, "swap-prediction")
            else:
                fdir = Path(output_dir, season, "survival-prediction")
            fs.mkdirs(fdir, exist_ok=True)
            fpath = fdir / f"data_{name}.csv"
            self.logger.info(f"Writing data for game {name} to {str(fpath)}")
            with fs.open(fpath, "wb") as buf:
                group.rename(columns={"start": META["duration"]}, inplace=True)
                group[
                    [META["id"], META["duration"], META["survival"]]
                    + META["static"]
                    + META["dynamic"]
                ].to_csv(buf, sep="|", mode="wb")


class SavePreGamePredictions(Task):
    """Save pre-game predictions."""

    def run(  # type: ignore
        self,
        pregame: pd.DataFrame,
        output_dir: str,
        filesystem: Optional[str] = "file",
    ):
        """Save pre-game predictions.

        Parameters
        ----------
        pregame : pd.DataFrame
            Standard pre-game prediction data.
        output_dir : str
            The directory containing the data.
        filesystem : str, optional (default "file")
            The name of the ``fsspec`` filesystem to use.

        Returns
        -------
        None
        """
        fs = fsspec.filesystem(filesystem)
        # Save the data
        pregame["SEASON"] = (
            pregame[META["id"]].str[2] + "0" + pregame[META["id"]].str[3:5] + "-"
        )
        pregame.loc[
            pregame[META["id"]].str[3:5].astype(int) + 1 < 10, "SEASON"
        ] += "0" + (pregame[META["id"]].str[3:5].astype(int) + 1).astype(str)
        pregame.loc[pregame[META["id"]].str[3:5].astype(int) + 1 >= 10, "SEASON"] += (
            pregame[META["id"]].str[3:5].astype(int) + 1
        ).astype(str)
        for name, group in pregame.groupby("SEASON"):
            fpath = Path(output_dir, name, "pregame-predictions.csv")
            self.logger.info(f"Writing pre-game predictions to {str(fpath)}")
            with fs.open(fpath, "wb") as buf:
                group.to_csv(buf, sep="|", mode="wb")
