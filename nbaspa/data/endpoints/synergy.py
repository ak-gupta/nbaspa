"""SynergyPlayType.

Retrieve Synergy play types.
"""

from typing import Dict, Optional

from .base import BaseRequest
from .parameters import DefaultParameters


class SynergyPlayType(BaseRequest):
    """Get the synergy play types.

    Parameters
    ----------
    TypeGrouping : str
        The type of plays, either ``offensive`` or ``defensive``.
    PlayType : str
        The type of play to retrieve. See the ``ParameterValues`` class
        for all options.
    **params
        Keyword parameters for ``BaseRequest``.
    """

    endpoint: str = "synergyplaytypes"
    filename: str = "data_{PlayType}_{TypeGrouping}_{SeasonYear}.json"

    def __init__(
        self,
        TypeGrouping: str,
        PlayType: str,
        output_dir: Optional[str] = None,
        filesystem: Optional[str] = "file",
        **params
    ):
        """Init method."""
        super().__init__(
            output_dir=output_dir,
            filesystem=filesystem,
            TypeGrouping=TypeGrouping,
            PlayType=PlayType,
            **params
        )

    @property
    def defaults(self) -> Dict:
        return {
            "LeagueID": DefaultParameters.LeagueID,
            "PerMode": DefaultParameters.PerMode,
            "PlayerOrTeam": DefaultParameters.PlayerOrTeam,
            "SeasonType": DefaultParameters.SeasonType,
            "SeasonYear": DefaultParameters.SeasonYear,
            "TypeGrouping": DefaultParameters.TypeGrouping,
            "PlayType": DefaultParameters.PlayType,
        }
