"""Import the cleaning tasks."""

from nba_survival.data.pipeline.lineup import AddLineupPlusMinus
from nba_survival.data.pipeline.margin import FillMargin
from nba_survival.data.pipeline.net_rating import AddNetRating
from nba_survival.data.pipeline.scoreboard import AddLastMeetingResult, AddTeamID, AddWinPercentage
from nba_survival.data.pipeline.target import CreateTarget
from nba_survival.data.pipeline.time import SurvivalTime
