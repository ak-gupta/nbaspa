"""Scoreboard.

Create a class for reading scoreboard data from the NBA API.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

from .base import BaseRequest
from .parameters import DefaultParameters


class Scoreboard(BaseRequest):
    """Get the scoreboard for a given date."""

    endpoint: str = "scoreboardv2"
    filename: str = "data_{GameDate}.json"

    @property
    def fpath(self) -> Union[None, Path]:
        """Define the filepath.

        Returns
        -------
        Path
            The path object.
        """
        if self.output_dir is None:
            return None
        else:
            fmt = datetime.strptime(self.params["GameDate"], "%m/%d/%Y")

            return Path(
                self.output_dir,
                self.endpoint,
                self.filename.format(GameDate=fmt.strftime("%Y%m%d"))
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
        ]
