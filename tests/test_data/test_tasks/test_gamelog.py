"""Test adding current win percentage and games in last X days."""

import pandas as pd

from nbaspa.data.tasks import (
    AddTeamID,
    AddWinPercentage,
    GamesInLastXDays
)

def test_add_win_perc(pbp, header, gamelog):
    """Test adding win percentage."""
    pre = AddTeamID()
    df = pre.run(pbp=pbp, header=header)
    tsk = AddWinPercentage()
    output = tsk.run(pbp=df, gamelog=gamelog)

    assert output["HOME_W_PCT"].equals(
        pd.Series(
            [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5], name="HOME_W_PCT"
        )
    )
    assert output["VISITOR_W_PCT"].equals(
        pd.Series(
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5], name="VISITOR_W_PCT"
        )
    )

def test_games_in_3_days(pbp, header, gamelog):
    """Test adding number of games in last 3 days."""
    pre = AddTeamID()
    df = pre.run(pbp=pbp, header=header)
    tsk = GamesInLastXDays(period=3)
    output = tsk.run(pbp=df, gamelog=gamelog)

    assert output["HOME_GAMES_IN_LAST_3_DAYS"].equals(
        pd.Series(
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], name="HOME_GAMES_IN_LAST_3_DAYS"
        )
    )
    assert  output["VISITOR_GAMES_IN_LAST_3_DAYS"].equals(
        pd.Series(
            [0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0, 2.0], name="VISITOR_GAMES_IN_LAST_3_DAYS"
        )
    )

def test_games_in_5_days(pbp, header, gamelog):
    """Test adding nmber of games in last 5 days."""
    pre = AddTeamID()
    df = pre.run(pbp=pbp, header=header)
    tsk = GamesInLastXDays(period=5)
    output = tsk.run(pbp=df, gamelog=gamelog)

    assert output["HOME_GAMES_IN_LAST_5_DAYS"].equals(
        pd.Series(
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], name="HOME_GAMES_IN_LAST_5_DAYS"
        )
    )
    assert output["VISITOR_GAMES_IN_LAST_5_DAYS"].equals(
        pd.Series(
            [1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0]
        )
    )
