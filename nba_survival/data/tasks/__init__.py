"""Import the cleaning tasks."""

from typing import List

from nba_survival.data.tasks.gamelog import AddWinPercentage, GamesInLastXDays
from nba_survival.data.tasks.io import (
    GenericLoader,
    PlayByPlayLoader,
    GameLogLoader,
    LineupLoader,
    RotationLoader,
    ShotChartLoader,
    BoxScoreLoader,
    ShotZoneLoader,
    GeneralShootingLoader,
    SaveData,
)
from nba_survival.data.tasks.lineup import AddLineupPlusMinus
from nba_survival.data.tasks.margin import FillMargin
from nba_survival.data.tasks.net_rating import AddNetRating
from nba_survival.data.tasks.scoreboard import AddLastMeetingResult, AddTeamID
from nba_survival.data.tasks.shotchart import AddExpectedShotValue, AddShotDetail
from nba_survival.data.tasks.target import CreateTarget
from nba_survival.data.tasks.time import DeDupeTime, SurvivalTime

__all__: List[str] = [
    "AddWinPercentage",
    "GenericLoader",
    "PlayByPlayLoader",
    "GameLogLoader",
    "LineupLoader",
    "RotationLoader",
    "ShotChartLoader",
    "BoxScoreLoader",
    "ShotZoneLoader",
    "GeneralShootingLoader",
    "SaveData",
    "GamesInLastXDays",
    "AddLineupPlusMinus",
    "FillMargin",
    "AddNetRating",
    "AddLastMeetingResult",
    "AddTeamID",
    "AddExpectedShotValue",
    "AddShotDetail",
    "CreateTarget",
    "DeDupeTime",
    "SurvivalTime"
]
