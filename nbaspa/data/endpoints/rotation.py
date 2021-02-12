"""GameRotation.

Create a class for retrieving the rotation data.
"""

from typing import Dict, List, Optional

from .base import BaseRequest
from .parameters import DefaultParameters

class GameRotation(BaseRequest):
    """Get rotation data.

    Parameters
    ----------
    GameID : str
        The game identifier.
    **params
        Parameters for ``BaseRequest``.
    
    Attributes
    ----------
    """

    endpoint: str = "gamerotation"
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
        """Default parameters for the endpoint.

        Returns
        -------
        Dict
            The default parameter values.
        """
        return {
            "GameID": DefaultParameters.GameID,
            "LeagueID": DefaultParameters.LeagueID
        }
    
    @property
    def datasets(self) -> List[str]:
        """Datasets returned by the API.

        Parameters
        ----------
        List
            Datasets returned by the API.
        """
        return ["AwayTeam", "HomeTeam"]
