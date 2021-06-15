"""Test attributing compound impact."""

import pandas as pd

from nbaspa.data.endpoints.pbp import EventTypes
from nbaspa.player_rating.tasks import CompoundPlayerImpact


def test_fga():
    """Test attributing impact for a field goal attempt + rebound."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.FIELD_GOAL_MISSED,
                EventTypes.REBOUND,
                EventTypes.FIELD_GOAL_MISSED,
                EventTypes.REBOUND
            ],
            "NBA_WIN_PROB_CHANGE": [0.1, 0.1, -0.1, -0.1],
            "HOMEDESCRIPTION": ["DESCRIPTION", None, None, None],
            "VISITORDESCRIPTION": [None, "DESCRIPTION", "DESCRIPTION", None],
            "PLAYER1_ID": [123, 456, 0, 0],
            "PLAYER2_ID": [0, 0, 123, 456],
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": [1, 1, 2, 2],
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.1, 0.0, 0.1, 0.0]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))


def test_off_foul():
    """Test attributing impact for an offensive foul."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.FOUL,
                EventTypes.TURNOVER,
                EventTypes.FOUL,
                EventTypes.TURNOVER
            ],
            "NBA_WIN_PROB_CHANGE": [0.1, 0.1, -0.1, -0.1],
            "HOMEDESCRIPTION": [None, "DESCRIPTION", None, None],
            "VISITORDESCRIPTION": [None, None, None, "DESCRIPTION"],
            "PLAYER1_ID": [123, 456, 0, 0],
            "PLAYER2_ID": [0, 0, 123, 456],
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": [1, 1, 2, 2],
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.0, 0.1, 0.0, 0.1]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))


def test_foul_2pt():
    """Test attributing impact for a shooting foul."""


def test_foul_2pt_missed_ft():
    """Test attributing impact for a shooting foul with missed free throw."""


def test_foul_3pt():
    """Test attributing impact for a 3 point shooting foul."""


def test_foul_3pt_missed_ft():
    """Test attributing impact for a 3 point shooting foul with missed free throw."""


def test_and1():
    """Test attributing impact for an and-one."""


def test_and1_missed_ft():
    """Test attributing impact for an and-one with missed free throw."""


def test_putback():
    """Test attributing impact for a putback."""


def test_putback():
    """Test attributing impact for a missed putback."""


def test_foul_putback_and1():
    """Test attributing impact for an and-one putback."""


def test_foul_putback():
    """Test attributing impact for a foul and missed putback."""


def test_foul_putback_and1_missed_ft():
    """Test attributing impact for an and-one putback with missed free throw."""


def test_foul_putback_missed_ft():
    """Test attributing imapct for a foul, missed putback, and missed free throw."""
