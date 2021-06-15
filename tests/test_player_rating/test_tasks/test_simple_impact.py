"""Test attributing simple impact."""

import numpy as np
import pandas as pd
import pytest

from nbaspa.data.endpoints.pbp import EventTypes
from nbaspa.player_rating.tasks import SimplePlayerImpact


@pytest.mark.parametrize(
    "evt",
    [
        EventTypes.REBOUND,
        EventTypes.FREE_THROW,
        EventTypes.VIOLATION,
        EventTypes.FIELD_GOAL_MISSED
    ]
)
def test_basic_impact(evt):
    """Test attributing simple impact."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": evt,
            "NBA_WIN_PROB_CHANGE": [0.1, 0.1],
            "HOMEDESCRIPTION": ["DESCRIPTION", None],
            "VISITORDESCRIPTION": [None, "DESCRIPTION"],
            "PLAYER1_ID": [123, 456],
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": [161, 161],
            "VISITOR_TEAM_ID": [162, 162],
            "SHOT_VALUE": np.nan,
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "TIME": [1, 2]
        }
    )
    tsk = SimplePlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.1, -0.1]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0]))


def test_foul_impact():
    """Test attributing foul impact."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": EventTypes.FOUL,
            "NBA_WIN_PROB_CHANGE": [0.1, 0.1],
            "HOMEDESCRIPTION": ["DESCRIPTION", None],
            "VISITORDESCRIPTION": [None, "DESCRIPTION"],
            "PLAYER1_ID": [123, 456],
            "PLAYER2_ID": [456, 123],
            "HOME_TEAM_ID": [161, 161],
            "VISITOR_TEAM_ID": [162, 162],
            "SHOT_VALUE": np.nan,
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "TIME": [1, 2]
        }
    )
    tsk = SimplePlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.1, -0.1]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([-0.1, 0.1]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0]))


def test_deadball_impact():
    """Test attributing deadball turnover impact."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": EventTypes.TURNOVER,
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": ["DESCRIPTION", None],
            "VISITORDESCRIPTION": [None, "DESCRIPTION"],
            "PLAYER1_ID": [123, 456],
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": [161, 161],
            "VISITOR_TEAM_ID": [162, 162],
            "SHOT_VALUE": np.nan,
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "TIME": [1, 2]
        }
    )

    tsk = SimplePlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.1, -0.1]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0]))


def test_steal_impact():
    """Test attributing steal impact."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": EventTypes.TURNOVER,
            "NBA_WIN_PROB_CHANGE": [0.1, 0.1],
            "HOMEDESCRIPTION": ["STL", None],
            "VISITORDESCRIPTION": [None, "STL"],
            "PLAYER1_ID": [123, 456],
            "PLAYER2_ID": [456, 123],
            "HOME_TEAM_ID": [161, 161],
            "VISITOR_TEAM_ID": [162, 162],
            "SHOT_VALUE": np.nan,
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "TIME": [1, 2]
        }
    )

    tsk = SimplePlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([-0.1, 0.1]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.1, -0.1]))


def test_block_impact():
    """Test attributing block impact."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": EventTypes.FIELD_GOAL_MISSED,
            "NBA_WIN_PROB_CHANGE": [0.1, 0.1],
            "HOMEDESCRIPTION": ["BLK", None],
            "VISITORDESCRIPTION": [None, "BLK"],
            "PLAYER1_ID": [123, 456],
            "PLAYER2_ID": [456, 123],
            "HOME_TEAM_ID": [161, 161],
            "VISITOR_TEAM_ID": [162, 162],
            "SHOT_VALUE": np.nan,
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "TIME": [1, 2]
        }
    )

    tsk = SimplePlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.0, 0.0]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.1, -0.1]))


def test_uast():
    """Test attributing unassisted field goals."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": EventTypes.FIELD_GOAL_MADE,
            "NBA_WIN_PROB_CHANGE": [0.1, -0.1],
            "HOMEDESCRIPTION": ["DESCRIPTION", None],
            "VISITORDESCRIPTION": [None, "DESCRIPTION"],
            "PLAYER1_ID": [123, 456],
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": [161, 161],
            "VISITOR_TEAM_ID": [162, 162],
            "SHOT_VALUE": np.nan,
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "TIME": [1, 2]
        }
    )

    tsk = SimplePlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.1, 0.1]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0]))


def test_ast():
    """Test attributing the impact of assisted field goals."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": EventTypes.FIELD_GOAL_MADE,
            "NBA_WIN_PROB_CHANGE": [0.1, -0.1],
            "HOMEDESCRIPTION": ["DESCRIPTION", None],
            "VISITORDESCRIPTION": [None, "DESCRIPTION"],
            "PLAYER1_ID": [123, 456],
            "PLAYER2_ID": [456, 123],
            "HOME_TEAM_ID": [161, 161],
            "VISITOR_TEAM_ID": [162, 162],
            "SHOT_VALUE": [1.0, 1.5],
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "TIME": [1, 2]
        }
    )

    tsk = SimplePlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.1, 0.05]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.05]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0]))
