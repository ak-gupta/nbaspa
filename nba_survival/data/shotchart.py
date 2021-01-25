"""ShotChart.

Create a class for getting shot chart data.
"""

from typing import Dict, Optional

from .base import BaseRequest
from .parameters import DefaultParameters

class ShotChart(BaseRequest):
    """Retrieve shot chart data for a player/game.

    Parameters
    ----------
    GameID : str
        The game identifier
    **params
        Parameters for ``BaseRequest``
    
    Attributes
    ----------
    """

    endpoint: str = "shotchartdetail"
    filename: str = "data_{GameID}.json"

    def __init__(
        self,
        GameID: str,
        output_dir: Optional[str] = None,
        filesystem: Optional[str] = "file",
        **params
    ):
        super().__init__(
            output_dir=output_dir,
            filesystem=filesystem,
            GameID=GameID,
            **params
        )
    
    @property
    def defaults(self) -> Dict:
        """Default parameters values for the endpoint.

        Returns
        -------
        Dict
            The default parameters values.
        """
        return {
            "ContextMeasure": DefaultParameters.ContextMeasure,
            "LastNGames": DefaultParameters.LastNGames,
            "LeagueID": DefaultParameters.LeagueID,
            "Month": DefaultParameters.Month,
            "Period": DefaultParameters.Period,
            "SeasonType": DefaultParameters.SeasonType,
            "VsDivision": DefaultParameters.VsDivision,
            "VsConference": DefaultParameters.VsConference,
            "StartRange": DefaultParameters.StartRange,
            "StartPeriod": DefaultParameters.StartPeriod,
            "SeasonSegment": DefaultParameters.SeasonSegment,
            "Season": DefaultParameters.Season,
            "RookieYear": DefaultParameters.RookieYear,
            "RangeType": DefaultParameters.RangeType,
            "Position": DefaultParameters.Position,
            "PointDiff": DefaultParameters.PointDiff,
            "PlayerPosition": DefaultParameters.PlayerPosition,
            "Outcome": DefaultParameters.Outcome,
            "Location": DefaultParameters.Location,
            "GameSegment": DefaultParameters.GameSegment,
            "EndRange": DefaultParameters.EndRange,
            "EndPeriod": DefaultParameters.EndPeriod,
            "DateTo": DefaultParameters.DateTo,
            "DateFrom": DefaultParameters.DateFrom,
            "ContextFilter": DefaultParameters.ContextFilter,
            "ClutchTime": DefaultParameters.ClutchTime,
            "AheadBehind": DefaultParameters.AheadBehind,
            "PlayerID": DefaultParameters.PlayerID,
            "TeamID": DefaultParameters.TeamID,
            "OpponentTeamID": DefaultParameters.OpponentTeamID,
        }
