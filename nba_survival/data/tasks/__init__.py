"""Import the cleaning tasks."""

from typing import List

from nba_survival.data.pipeline.gamelog import AddWinPercentage, GamesInLastXDays
from nba_survival.data.pipeline.io import (
    GenericLoader,
    PlayByPlayLoader,
    GameLogLoader,
    LineupLoader,
    RotationLoader,
    ShotChartLoader,
    BoxScoreLoader,
    ShotZoneLoader,
    SaveData,
)
from nba_survival.data.pipeline.lineup import AddLineupPlusMinus
from nba_survival.data.pipeline.margin import FillMargin
from nba_survival.data.pipeline.net_rating import AddNetRating
from nba_survival.data.pipeline.scoreboard import AddLastMeetingResult, AddTeamID
from nba_survival.data.pipeline.shotchart import AddExpectedShotValue, AddShotDetail
from nba_survival.data.pipeline.target import CreateTarget
from nba_survival.data.pipeline.time import SurvivalTime

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
    "SurvivalTime"
]
