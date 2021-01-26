"""BoxScoreBase.

Create various classes for retrieving BoxScore data.
"""

from typing import Dict, List, Optional

from nba_survival.data.endpoints.base import BaseRequest
from nba_survival.data.endpoints.parameters import DefaultParameters

class BoxScoreBase(BaseRequest):
    """Get boxscore data.

    Parameters
    ----------
    GameID : str
        The game identifier.
    **params
        Parameters for ``BaseRequest``.
    
    Attributes
    ----------
    """
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
            "StartRange": DefaultParameters.StartRange,
            "EndRange": DefaultParameters.EndRange,
            "RangeType": DefaultParameters.RangeType
        }
    
    @property
    def datasets(self) -> List[str]:
        """Datasets returned by the API.

        Returns
        -------
        List
            Datasets returned by the API.
        """
        return ["PlayerStats", "TeamStats", "TeamStarterBenchStats"]

class BoxScoreTraditional(BoxScoreBase):
    """Get traditional boxscore data."""
    endpoint: str = "boxscoretraditionalv2"

class BoxScoreAdvanced(BoxScoreBase):
    """Get the advanced boxscore data."""
    endpoint: str = "boxscoreadvancedv2"

class BoxScoreFourFactors(BoxScoreBase):
    """Get the four factors data."""
    endpoint: str = "boxscorefourfactorsv2"

class BoxScoreMisc(BoxScoreBase):
    """Get miscellaneous boxscore data."""
    endpoint: str = "boxscoremiscv2"

class BoxScoreScoring(BoxScoreBase):
    """Get boxscore scoring data."""
    endpoint: str = "boxscorescoringv2"

class BoxScoreUsage(BoxScoreBase):
    """Get boxscore usage data."""
    endpoint: str = "boxscoreusagev2"
