"""DefaultParameters.

Define default parameters for the endpoints.
"""

from dataclasses import dataclass
import datetime
from typing import Any, Dict, Set

# Get some system date-based variables
TODAY = datetime.datetime.now()

if TODAY.month > 8:
    CURRENT_SEASON = str(TODAY.year) + "-" + str(TODAY.year + 1)[2:]
    CURRENT_SEASON_YEAR = str(TODAY.year)
else:
    CURRENT_SEASON = str(TODAY.year - 1) + "-" + str(TODAY.year)[2:]
    CURRENT_SEASON_YEAR = str(TODAY.year - 1)

SEASONS: Dict = {
    "2012-13": {
        "START": datetime.datetime(year=2012, month=10, day=30),
        "END": datetime.datetime(year=2013, month=4, day=17)
    },
    "2013-14": {
        "START": datetime.datetime(year=2013, month=10, day=29),
        "END": datetime.datetime(year=2014, month=4, day=16)
    },
    "2014-15": {
        "START": datetime.datetime(year=2014, month=10, day=28),
        "END": datetime.datetime(year=2015, month=4, day=15)
    },
    "2015-16": {
        "START": datetime.datetime(year=2015, month=10, day=27),
        "END": datetime.datetime(year=2016, month=4, day=13),
    },
    "2016-17": {
        "START": datetime.datetime(year=2016, month=10, day=25),
        "END": datetime.datetime(year=2017, month=4, day=12),
    },
    "2017-18": {
        "START": datetime.datetime(year=2017, month=10, day=17),
        "END": datetime.datetime(year=2018, month=4, day=11),
    },
    "2018-19": {
        "START": datetime.datetime(year=2018, month=10, day=16),
        "END": datetime.datetime(year=2019, month=4, day=10),
    },
    "2019-20": {
        "START": datetime.datetime(year=2019, month=10, day=22),
        "END": datetime.datetime(year=2020, month=3, day=10),
    },
}


@dataclass
class DefaultParameters:
    """Default parameters for the endpoints."""

    # No need to adjust League ID
    LeagueID: str = "00"
    # Datetime variables
    GameDate: str = TODAY.strftime("%m/%d/%Y")
    Season: str = CURRENT_SEASON
    SeasonYear: str = CURRENT_SEASON_YEAR
    SeasonType: str = "Regular Season"
    DayOffset: int = 0
    IsOnlyCurrentSeason: str = "1"
    Month: int = 0
    SeasonSegment: str = ""
    DateFrom: str = ""
    DateTo: str = ""
    LastNGames: int = 0
    PORound: int = 0
    GameScope: str = "Season"
    RookieYear: str = ""
    # Within game time variables
    Period: int = 0
    StartPeriod: int = 0
    EndPeriod: int = 0
    GameSegment: str = ""
    ShotClockRange: str = ""
    ClutchTime: str = ""
    AheadBehind: str = ""
    PointDiff: str = ""
    ContextFilter: str = ""
    # What is this for
    StartRange: int = 0
    EndRange: int = 0
    RangeType: int = 0
    RunType: str = "each second"
    # Type of data to retrieve
    MeasureType: str = "Base"
    PerMode: str = "PerGame"
    ContextMeasure: str = "FG_PCT"
    PlusMinus: str = "N"
    PaceAdjust: str = "N"
    Rank: str = "N"
    Outcome: str = ""
    Location: str = ""
    TeamID: int = 0
    GameID: str = ""
    OpponentTeamID: int = 0
    Conference: str = ""
    Division: str = ""
    VsConference: str = ""
    VsDivision: str = ""
    Scope: str = "S"
    PlayerID: int = 0
    PlayerExperience: str = ""
    Position: str = ""
    PlayerPosition: str = ""
    StarterBench: str = ""
    PlayerOrTeam: str = "T"
    TypeGrouping: str = ""
    PlayType: str = ""
    GroupQuantity: str = "5"


class ParameterValues:
    """Define the possible parameter values."""

    @property
    def LeagueID(self) -> Set[str]:
        """The league ID.

        This package is specific to the NBA, so only enable NBA.
        """
        return {
            "00",
        }

    # DATETIME VARIABLES

    @property
    def GameDate(self) -> Any:
        """Game date."""
        pass

    @property
    def Season(self) -> Any:
        """The season."""
        pass

    @property
    def SeasonYear(self) -> Any:
        """The year.

        Allow all values.
        """
        pass

    @property
    def SeasonType(self) -> Set[str]:
        """Season type to retrieve."""
        return {"Regular Season", "Playoffs"}

    @property
    def DayOffset(self) -> Any:
        """Offset the game date."""
        pass

    @property
    def IsOnlyCurrentSeason(self) -> Set[str]:
        """Restrict to the current season."""
        pass

    @property
    def Month(self) -> Set[str]:
        """Get the month.

        Values range from 0-12, with 0 retrieving all months, 1 retrieving October,
        2 retrieving November, etc.
        """
        return set(str(i) for i in range(0, 13))

    @property
    def SeasonSegment(self) -> Set[str]:
        """Whether to retrieve the entire season or segment using the All-star break."""
        return {"", "Pre All-Star", "Post All-Star"}

    @property
    def DateFrom(self) -> Any:
        """Start of the data pull."""
        pass

    @property
    def DateTo(self) -> Any:
        """End of the data pull."""
        pass

    @property
    def LastNGames(self) -> Any:
        """Number of games to consider."""
        pass

    @property
    def PORound(self) -> Set[int]:
        """The playoff round.

        0 indicates all rounds, 1 retrieves the first round, etc.
        """
        return {0, 1, 2, 3, 4}

    @property
    def GameScope(self) -> Set[str]:
        """General datetime restriction."""
        return {"Season", "Last 10", "Yesterday", "Finals"}

    @property
    def RookieYear(self) -> Any:
        """Unknown."""
        pass

    # WITHIN GAME RESTRICTIONS

    @property
    def Period(self) -> Set[int]:
        """The period of the game to retrieve.

        0 indicates the entire game, 1 indicates the first quarter, etc.
        """
        return {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

    @property
    def StartPeriod(self) -> Set[int]:
        """Restrict the start of the data pull."""
        return self.Period

    @property
    def EndPeriod(self) -> Set[int]:
        """Restrict the end of the data pull."""
        return self.Period

    @property
    def GameSegment(self) -> Set[str]:
        """The portion of the game to retrieve."""
        return {"", "First Half", "Second Half", "Overtime"}

    @property
    def ShotClockRange(self) -> Set[str]:
        """Restrict to shot clock situations."""
        return {
            "",
            "24-22",
            "22-18 Very Early",
            "18-15 Early",
            "15-7 Average",
            "7-4 Late",
            "4-0 Very Late",
        }

    @property
    def ClutchTime(self) -> Set[str]:
        """Get data for clutch time."""
        return {
            "",
            "Last 10 Seconds",
            "Last 30 Seconds",
            "Last 1 Minute",
            "Last 2 Minutes",
            "Last 3 Minutes",
            "Last 4 Minutes",
            "Last 5 Minutes",
        }

    @property
    def AheadBehind(self) -> Set[str]:
        """Restrict based on score status."""
        return {"", "Ahead or Behind", "Ahead or Tied", "Behind or Tied"}

    @property
    def PointDiff(self) -> Any:
        """Unknown."""
        pass

    @property
    def ContextFilter(self) -> Any:
        """Unknown."""
        pass

    # UNKNOWN

    @property
    def StartRange(self) -> Any:
        """Unknown."""
        pass

    @property
    def EndRange(self) -> Any:
        """Unknown."""
        pass

    @property
    def RangeType(self) -> Any:
        """Unknown."""
        pass

    @property
    def RunType(self) -> Any:
        """Unknown."""
        pass

    @property
    def MeasureType(self) -> Set[str]:
        """The type of team or player data to retrieve."""
        return {
            "Base",
            "Advanced",
            "Misc",
            "Four Factors",
            "Scoring",
            "Opponent",
            "Usage",
        }

    @property
    def PerMode(self) -> Set[str]:
        """The type of team or player data to retrieve."""
        return {
            "Totals",
            "PerGame",
            "MinutesPer",
            "Per48",
            "Per40",
            "Per36",
            "PerMinute",
            "PerPossession",
            "PerPlay",
            "Per100Possessions",
            "Per100Plays",
        }

    @property
    def ContextMeasure(self) -> Set[str]:
        """Context measure for selectors."""
        return {
            "PTS",
            "EFG_PCT",
            "FG3_PCT",
            "FG3A",
            "FG3M",
            "FG_PCT",
            "FGA",
            "FGM",
            "PF",
            "PTS_2ND_CHANCE",
            "PTS_FB",
            "PTS_OFF_TOV",
            "TS_PCT",
        }

    @property
    def PlusMinus(self) -> Any:
        """Unknown."""
        pass

    @property
    def PaceAdjust(self) -> Any:
        """Unknown."""
        pass

    @property
    def Rank(self) -> Any:
        """Unknown."""
        pass

    @property
    def Outcome(self) -> Set[str]:
        """Segment call on game outcome."""
        return {"", "W", "L"}

    @property
    def Location(self) -> Set[str]:
        """Segment call on game location."""
        return {"", "Home", "Away"}

    @property
    def GameID(self) -> Any:
        """Game identifier."""
        pass

    @property
    def TeamID(self) -> Set[int]:
        """Unique team-level identifier."""
        return set([0] + [idval for idval in range(1610612737, 1610612767)])

    @property
    def OpponentTeamID(self) -> Set[int]:
        """Opponent TeamID."""
        return self.TeamID

    @property
    def VsConference(self) -> Set[str]:
        """The conference of the opposing team."""
        return {"", "East", "West"}

    @property
    def Conference(self) -> Set[str]:
        """The conference."""
        return self.VsConference

    @property
    def VsDivision(self) -> Set[str]:
        """The division of the opposing team."""
        return {
            "",
            "Atlantic",
            "Central",
            "Northwest",
            "Pacific",
            "Southeast",
            "Southwest",
        }

    @property
    def Division(self) -> Set[str]:
        """Which division to retrieve."""
        return self.VsDivision

    @property
    def Scope(self) -> Set[str]:
        """Get all players or just rookies."""
        return {"S", "Rookies"}

    @property
    def PlayerID(self) -> Any:
        """Get a specific player."""
        pass

    @property
    def PlayerExperience(self) -> Set[str]:
        """General filter for player experience."""
        return {"", "Rookie", "Sophomore", "Veteran"}

    @property
    def Position(self) -> Any:
        """Filter for position."""
        return {"", "F", "C", "G"}

    @property
    def PlayerPosition(self) -> Set[str]:
        """Filter for position."""
        return self.Position

    @property
    def StarterBench(self) -> Set[str]:
        """Filter for starters and bench players."""
        return {"", "Starters", "Bench"}

    @property
    def PlayerOrTeam(self) -> Set[str]:
        """Filter to return player or team."""
        return {"T", "P"}

    @property
    def TypeGrouping(self) -> Set[str]:
        """Choose offensive or defensive possessions."""
        return {"", "defensive", "offensive"}

    @property
    def PlayType(self) -> Set[str]:
        """Choose a play type."""
        return {
            "",
            "Cut",
            "Handoff",
            "Isolation",
            "Misc",
            "Offscreen",
            "Postup",
            "PRBallHandler",
            "PRRollman",
            "OffRebound",
            "Spotup",
            "Transition",
        }

    @property
    def GroupQuantity(self) -> Any:
        """Number of players to include."""
        pass
