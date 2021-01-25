"""TeamLineups.

Create a class to pull lineup data.
"""

from typing import Dict, List, Optional

from .base import BaseRequest
from .parameters import DefaultParameters

class TeamLineups(BaseRequest):
    """Pull lineup data.

    Parameters
    ----------
    TeamID : str
        The team identifier
    **params
        Parameters for ``BaseRequest``

    Attributes
    ----------
    """

    endpoint: str = "teamdashlineups"
    filename: str = "data_{TeamID}.json"

    def __init__(
        self,
        TeamID: str,
        output_dir: Optional[str] = None,
        filesystem: Optional[str] = "file",
        **params
    ):
        super().__init__(
            output_dir=output_dir,
            filesystem=filesystem,
            TeamID=TeamID,
            **params
        )

    @property
    def datasets(self) -> List[str]:
        """Datasets returned by the API.

        Returns
        -------
        List
            Datasets returned by the API.
        """
        return ["Overall", "Lineups"]

    @property
    def defaults(self) -> Dict:
        """Default parameter values for the endpoint.

        Returns
        -------
        Dict
            The default parameter values.
        """
        return {
            "GroupQuantity": DefaultParameters.GroupQuantity,
            "LastNGames": DefaultParameters.LastNGames,
            "MeasureType": DefaultParameters.MeasureType,
            "Month": DefaultParameters.Month,
            "OpponentTeamID": DefaultParameters.OpponentTeamID,
            "PaceAdjust": DefaultParameters.PaceAdjust,
            "PerMode": DefaultParameters.PerMode,
            "Period": DefaultParameters.Period,
            "PlusMinus": DefaultParameters.PlusMinus,
            "Rank": DefaultParameters.Rank,
            "Season": DefaultParameters.Season,
            "SeasonType": DefaultParameters.SeasonType,
            "TeamID": DefaultParameters.TeamID,
            "VsDivision": DefaultParameters.VsDivision,
            "VsConference": DefaultParameters.VsConference,
            "ShotClockRange": DefaultParameters.ShotClockRange,
            "SeasonSegment": DefaultParameters.SeasonSegment,
            "PORound": DefaultParameters.PORound,
            "Outcome": DefaultParameters.Outcome,
            "Location": DefaultParameters.Location,
            "LeagueID": DefaultParameters.LeagueID,
            "GameSegment": DefaultParameters.GameSegment,
            "GameID": DefaultParameters.GameID,
            "DateTo": DefaultParameters.DateTo,
            "DateFrom": DefaultParameters.DateFrom
        }
