"""Import the cleaning tasks."""

from typing import List

from .gamelog import AddWinPercentage, GamesInLastXDays
from .io import (
    GenericLoader,
    FactoryGetter,
    PlayByPlayLoader,
    WinProbabilityLoader,
    GameLogLoader,
    LineupLoader,
    RotationLoader,
    ShotChartLoader,
    BoxScoreLoader,
    ShotZoneLoader,
    GeneralShootingLoader,
    SaveData,
)
from .lineup import AddLineupPlusMinus
from .margin import FillMargin
from .nba_win_prob import AddNBAWinProbability
from .net_rating import AddNetRating
from .scoreboard import AddLastMeetingResult, AddTeamID
from .shotchart import AddExpectedShotValue, AddShotDetail
from .target import CreateTarget
from .time import DeDupeTime, SurvivalTime

__all__: List[str] = [
    "AddWinPercentage",
    "GenericLoader",
    "FactoryGetter",
    "PlayByPlayLoader",
    "WinProbabilityLoader",
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
    "AddNBAWinProbability",
    "AddNetRating",
    "AddLastMeetingResult",
    "AddTeamID",
    "AddExpectedShotValue",
    "AddShotDetail",
    "CreateTarget",
    "DeDupeTime",
    "SurvivalTime",
]
