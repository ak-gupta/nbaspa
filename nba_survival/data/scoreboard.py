"""Scoreboard.

Create a class for reading scoreboard data from the NBA API.
"""

from datetime import datetime
from typing import Dict, List

from .base import BaseRequest
from .parameters import DefaultParameters

class Scoreboard(BaseRequest):
    """Get the scoreboard for a given date."""

    endpoint: str = "scoreboardv2"

    @property
    def filename(self) -> str:
        """The output JSON filename.

        Returns
        -------
        str
            The filename.
        """
        fmt = datetime.strptime(self.params["GameDate"], "%m/%d/%Y")

        return f"data_{fmt.strftime('%Y%m%d')}.json"

    @property
    def defaults(self) -> Dict:
        """Default parameter values for the endpoint.

        Returns
        -------
        Dict
            The default parameter values.
        """
        return {
            "GameDate": DefaultParameters.GameDate,
            "LeagueID": DefaultParameters.LeagueID,
            "DayOffset": DefaultParameters.DayOffset,
        }
    
    @property
    def datasets(self) -> List[str]:
        """Datasets returned by the API.

        Returns
        -------
        List
            Datasets returned by the API.
        """
        return [
            "GameHeader",
            "LineScore",
            "SeriesStandings",
            "LastMeeting",
            "EastConfStandingsByDay",
            "WestConfStandingsByDay",
            "Available",
            "TeamLeaders",
            "TicketLinks",
            "WinProbability"
        ]
