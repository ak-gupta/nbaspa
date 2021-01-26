"""DefaultParameters.

Define default parameters for the endpoints.
"""

from dataclasses import dataclass
import datetime
from typing import Any, Set

# Get some system date-based variables
TODAY = datetime.datetime.now()

if TODAY.month > 8:
    CURRENT_SEASON = str(TODAY.year) + "-" + str(TODAY.year + 1)[2:]
    CURRENT_SEASON_YEAR = str(TODAY.year)
else:
    CURRENT_SEASON = str(TODAY.year - 1) + "-" + str(TODAY.year)[2:]
    CURRENT_SEASON_YEAR = str(TODAY.year - 1)

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
    DayOffset: str = "0"
    IsOnlyCurrentSeason: str = "1"
    Month: str = "0"
    SeasonSegment: str = ""
    DateFrom: str = ""
    DateTo: str = ""
    LastNGames: str = "0"
    PORound: str = "0"
    GameScope: str = "Season"
    RookieYear: str = ""
    # Within game time variables
    Period: str = "0"
    StartPeriod: str = "0"
    EndPeriod: str = "0"
    GameSegment: str = ""
    ShotClockRange: str = ""
    ClutchTime: str = ""
    AheadBehind: str = ""
    PointDiff: str = ""
    ContextFilter: str = ""
    # What is this for
    StartRange: str = "0"
    EndRange: str = "0"
    RangeType: str = "0"
    # Type of data to retrieve
    MeasureType: str = "Base"
    PerMode: str = "PerGame"
    ContextMeasure: str = "FG_PCT"
    PlusMinus: str = "N"
    PaceAdjust: str = "N"
    Rank: str = "N"
    Outcome: str = ""
    Location: str = ""
    TeamID: str = "0"
    GameID: str = ""
    OpponentTeamID: str = "0"
    Conference: str = ""
    Division: str = ""
    VsConference: str = ""
    VsDivision: str = ""
    Scope: str = "S"
    PlayerID: str = "0"
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
        return {"00",}

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
        return {
            "Regular Season",
            "Playoffs"
        }
    
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
        return {
            "", "Pre All-Star", "Post All-Star"
        }

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
        pass
    
    @property
    def PORound(self) -> Set[str]:
        """The playoff round.

        0 indicates all rounds, 1 retrieves the first round, etc.
        """
        return {"0", "1", "2", "3", "4"}
    
    @property
    def GameScope(self) -> Set[str]:
        """General datetime restriction."""
        return {
            "Season",
            "Last 10",
            "Yesterday",
            "Finals"
        }
    
    @property
    def RookieYear(self) -> Any:
        pass

    # WITHIN GAME RESTRICTIONS

    @property
    def Period(self) -> Set[str]:
        """The period of the game to retrieve.

        0 indicates the entire game, 1 indicates the first quarter, etc.
        """
        return {
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"
        }
    
    @property
    def StartPeriod(self) -> Set[str]:
        """Restrict the start of the data pull."""
        return self.Period
    
    @property
    def EndPeriod(self) -> Set[str]:
        """Restrict the end of the data pull."""
        return self.Period

    @property
    def GameSegment(self) -> Set[str]:
        return {
            "",
            "First Half",
            "Second Half",
            "Overtime"
        }
    
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
            "4-0 Very Late"
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
        return {
            "",
            "Ahead or Behind",
            "Ahead or Tied",
            "Behind or Tied"
        }
    
    @property
    def PointDiff(self) -> Any:
        pass

    @property
    def ContextFilter(self) -> Any:
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
            "TS_PCT"
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
        return {
            "", "W", "L"
        }
    
    @property
    def Location(self) -> Set[str]:
        return {
            "", "Home", "Away"
        }
    
    @property
    def GameID(self) -> Any:
        pass

    @property
    def TeamID(self) -> Set[str]:
        """Unique team-level identifier."""
        return set(["", "0"] + [
            f"16106127{idval}" for idval in range(37, 67)
        ])
    
    @property
    def OpponentTeamID(self) -> Set[str]:
        """Opponent TeamID."""
        return self.TeamID
    
    @property
    def VsConference(self) -> Set[str]:
        return {
            "", "East", "West"
        }
    
    @property
    def Conference(self) -> Set[str]:
        """The conference."""
        return self.VsConference
    
    @property
    def VsDivision(self) -> Set[str]:
        return {
            "",
            "Atlantic",
            "Central",
            "Northwest",
            "Pacific",
            "Southeast",
            "Southwest"
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
        return {
            "", "Rookie", "Sophomore", "Veteran"
        }
    
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
        return {
            "", "Starters", "Bench"
        }
    
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
            "Transition"
        }
    
    @property
    def GroupQuantity(self) -> Any:
        pass
