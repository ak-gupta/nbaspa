"""PlayByPlay.

Create a class for reading data from the play-by-play endpoint.
"""

from typing import Dict, Optional

from nba_survival.data.endpoints.base import BaseRequest
from nba_survival.data.endpoints.parameters import DefaultParameters

class EventTypes:
    """Play-by-play event types."""

    FIELD_GOAL_MADE: int = 1
    FIELD_GOAL_MISSED: int = 2
    FREE_THROW: int = 3
    REBOUND: int = 4
    TURNOVER: int = 5
    FOUL: int = 6
    VIOLATION: int = 7
    SUBSTITUTION: int = 8
    TIMEOUT: int = 9
    JUMP_BALL: int = 10
    EJECTION: int = 11
    PERIOD_BEGIN: int = 12
    UNKNOWN: int = 13
    REPLAY: int = 18

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
