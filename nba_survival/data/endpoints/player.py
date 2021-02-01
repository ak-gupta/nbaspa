"""PlayerDashboard.

Create a class for getting a player dashboard.
"""

from typing import Dict, List, Optional

from nba_survival.data.endpoints.base import BaseRequest
from nba_survival.data.endpoints.parameters import DefaultParameters


class PlayerDashboardBase(BaseRequest):
    """Get the player shooting dashboard.

    Parameters
    ----------
    PlayerID : int
        The player identifier
    **params
        Parameters for ``BaseRequest``
    
    Attributes
    ----------
    """

    endpoint: str = "default"
    filename: str = "data_{PlayerID}.json"

    def __init__(
        self,
        PlayerID: int,
        output_dir: Optional[str] = None,
        filesystem: Optional[str] = "file",
        **params
    ):
        super().__init__(
            output_dir=output_dir,
            filesystem=filesystem,
            PlayerID=PlayerID,
            **params
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
            "VsDivision": DefaultParameters.VsDivision,
            "VsConference": DefaultParameters.VsConference,
            "ShotClockRange": DefaultParameters.ShotClockRange,
            "SeasonSegment": DefaultParameters.SeasonSegment,
            "PORound": DefaultParameters.PORound,
            "Outcome": DefaultParameters.Outcome,
            "Location": DefaultParameters.Location,
            "LeagueID": DefaultParameters.LeagueID,
            "GameSegment": DefaultParameters.GameSegment,
            "DateTo": DefaultParameters.DateTo,
            "DateFrom": DefaultParameters.DateFrom
        }


class PlayerDashboardGeneral(PlayerDashboardBase):
    """Get the general dashboard."""
    endpoint: str = "playerdashboardbygeneralsplits"

    @property
    def datasets(self) -> List[str]:
        """Datasets returned by the API.

        Parameters
        ----------
        List
            Datasets returned by the API.
        """
        return [
            "OverallPlayerDashboard",
            "LocationPlayerDashboard",
            "WinsLossesPlayerDashboard",
            "MonthPlayerDashboard",
            "PrePostAllStarPlayerDashboard",
            "StartingPosition",
            "DaysRestPlayerDashboard"
        ]

class PlayerDashboardShooting(PlayerDashboardBase):
    """Get the shooting dashboard."""
    endpoint: str = "playerdashboardbyshootingsplits"

    @property
    def datasets(self) -> List[str]:
        """Datasets returned by the API.

        Returns
        -------
        List
            Datasets returned by the API.
        """
        return [
            "OverallPlayerDashboard",
            "Shot5FTPlayerDashboard",
            "Shot8FTPlayerDashboard",
            "ShotAreaPlayerDashboard",
            "AssitedShotPlayerDashboard",
            "ShotTypeSummaryPlayerDashboard",
            "ShotTypePlayerDashboard",
            "AssistedBy"
        ]
