"""Team data.

Create a class for reading team-level data from the API.
"""

from typing import Dict, Optional

import pandas as pd

from .base import BaseRequest
from .parameters import DefaultParameters


class TeamStats(BaseRequest):
    """Get team stats."""

    endpoint: str = "teamestimatedmetrics"
    filename: str = "data_{Season}.json"

    @property
    def defaults(self) -> Dict:
        """Default parameter values for the endpoint.

        Returns
        -------
        Dict
            The default parameter values.
        """
        return {
            "Season": DefaultParameters.Season,
            "SeasonType": DefaultParameters.SeasonType,
            "LeagueID": DefaultParameters.LeagueID,
        }

    def get_data(self, dataset_type: Optional[str] = "default") -> pd.DataFrame:
        """Get a tabular dataset.

        Parameters
        ----------
        dataset_type : str, optional (default "default")
            The dataset type.

        Returns
        -------
        pd.DataFrame
            The tabular dataframe.
        """
        return pd.DataFrame.from_records(
            self._raw_data["resultSet"]["rowSet"],
            columns=self._raw_data["resultSet"]["headers"],
        )


class TeamGameLog(BaseRequest):
    """Get team game logs.

    Parameters
    ----------
    TeamID : int
        The team identifier.
    **params
        Parameters for ``BaseRequest``
    """

    endpoint: str = "teamgamelog"
    filename: str = "data_{TeamID}.json"

    def __init__(
        self,
        TeamID: int,
        output_dir: Optional[str] = None,
        filesystem: Optional[str] = "file",
        **params
    ):
        """Init method."""
        super().__init__(
            output_dir=output_dir, filesystem=filesystem, TeamID=TeamID, **params
        )

    @property
    def defaults(self) -> Dict:
        """Default parameters for the endpoint.

        Returns
        -------
        Dict
            The default parameter values.
        """
        return {
            "Season": DefaultParameters.Season,
            "SeasonType": DefaultParameters.SeasonType,
            "LeagueID": DefaultParameters.LeagueID,
            "DateTo": DefaultParameters.DateTo,
            "DateFrom": DefaultParameters.DateFrom,
        }
