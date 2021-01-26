"""PlayByPlay.

Create a class for reading data from the play-by-play endpoint.
"""

from typing import Dict, Optional

from nba_survival.data.endpoints.base import BaseRequest
from nba_survival.data.endpoints.parameters import DefaultParameters

EVENT_TYPES: Dict = {
    1: "FIELD_GOAL_MADE",
    2: "FIELD_GOAL_MISSED",
    3: "FREE_THROW",
    4: "REBOUND",
    5: "TURNOVER",
    6: "FOUL",
    7: "VIOLATION",
    8: "SUBSTITUTION",
    9: "TIMEOUT",
    10: "JUMP_BALL",
    11: "EJECTION",
    12: "PERIOD_BEGIN",
    13: "UNKNOWN"
}

class PlayByPlay(BaseRequest):
    """Get the play by play data for a game.
    
    Parameters
    ----------
    GameID : str
        The game identifier.
    **params
        Parameters for the API call.
    
    Attributes
    ----------
    """

    endpoint: str = "playbyplayv2"
    filename: str = "data_{GameID}.json"

    def __init__(
        self,
        GameID: str,
        output_dir: Optional[str] = None,
        filesystem: Optional[str] = "file",
        **params
    ):
        super().__init__(
            output_dir=output_dir, filesystem=filesystem, GameID=GameID, **params
        )

    @property
    def defaults(self) -> Dict:
        """Default parameter values for the endpoint.

        Returns
        -------
        Dict
            The default parameter values.
        """
        return {
            "StartPeriod": DefaultParameters.StartPeriod,
            "EndPeriod": DefaultParameters.EndPeriod,
        }
