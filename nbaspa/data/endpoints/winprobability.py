"""WinProbability.

Get the NBA Win probability metric.
"""

from typing import List, Dict, Optional

from .base import BaseRequest
from .parameters import DefaultParameters


class WinProbability(BaseRequest):
    """Get the NBA win probability metric.

    Parameters
    ----------
    GameID : str
        The game identifier
    **params
        Parameters for ``BaseRequest``

    Attributes
    ----------
    None
    """

    endpoint: str = "winprobabilitypbp"
    filename: str = "data_{GameID}.json"

    def __init__(
        self,
        GameID: str,
        output_dir: Optional[str] = None,
        filesystem: Optional[str] = "file",
        **params
    ):
        """Init method."""
        super().__init__(
            output_dir=output_dir, filesystem=filesystem, GameID=GameID, **params
        )

    @property
    def datasets(self) -> List[str]:
        """Datasets returned by the API.

        Returns
        -------
        List
            Datasets returned by the API.
        """
        return ["WinProbPBP", "GameInfo"]

    @property
    def defaults(self) -> Dict:
        """Default parameters for the endpoint.

        Returns
        -------
        Dict
            The default parameter values.
        """
        return {
            "RunType": DefaultParameters.RunType,
        }
