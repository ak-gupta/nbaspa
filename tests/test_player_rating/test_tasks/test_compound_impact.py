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
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.FOUL,
                EventTypes.FREE_THROW,
                EventTypes.FREE_THROW,
            ],
            "NBA_WIN_PROB_CHANGE": [0.1, 0.1, 0.1],
            "HOMEDESCRIPTION": [None, "FT", "FT"],
            "VISITORDESCRIPTION": ["FOUL", None, None],
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": 1,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([-0.1, 0.0, 0.1]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0]))


def test_foul_2pt_missed_ft():
    """Test attributing impact for a shooting foul with missed free throw."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.FOUL,
                EventTypes.FREE_THROW,
                EventTypes.FREE_THROW,
                EventTypes.REBOUND
            ],
            "NBA_WIN_PROB_CHANGE": [0.1, 0.1, 0.1, 0.1],
            "HOMEDESCRIPTION": [None, "FT", "FT", None],
            "VISITORDESCRIPTION": ["FOUL", None, None, None],
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": 1,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    print(output["PLAYER1_IMPACT"])

    assert output["PLAYER1_IMPACT"].equals(pd.Series([-0.1, 0.0, 0.1, 0.0]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))


def test_foul_3pt():
    """Test attributing impact for a 3 point shooting foul."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.FOUL,
                EventTypes.FREE_THROW,
                EventTypes.FREE_THROW,
                EventTypes.FREE_THROW
            ],
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": [None, "FT", "FT", "FT"],
            "VISITORDESCRIPTION": ["FOUL", None, None, None],
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": 1,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([-0.1, 0.0, 0.0, 0.1]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))


def test_foul_3pt_missed_ft():
    """Test attributing impact for a 3 point shooting foul with missed free throw."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.FOUL,
                EventTypes.FREE_THROW,
                EventTypes.FREE_THROW,
                EventTypes.FREE_THROW,
                EventTypes.REBOUND
            ],
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": [None, "FT", "FT", "FT", None],
            "VISITORDESCRIPTION": ["FOUL", None, None, None, None],
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": 1,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([-0.1, 0.0, 0.0, 0.1, 0.0]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0, 0.0]))


def test_and1():
    """Test attributing impact for an and-one."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.FIELD_GOAL_MADE,
                EventTypes.FOUL,
                EventTypes.FREE_THROW,
            ],
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": ["FGM", None, "FT"],
            "VISITORDESCRIPTION": ["FOUL", None, None],
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": 1,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.0, -0.1, 0.1]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0]))


def test_and1_missed_ft():
    """Test attributing impact for an and-one with missed free throw."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.FIELD_GOAL_MADE,
                EventTypes.FOUL,
                EventTypes.FREE_THROW,
                EventTypes.REBOUND
            ],
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": ["FGM", None, "FT", None],
            "VISITORDESCRIPTION": [None, "FOUL", None, None],
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": 1,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.0, -0.1, 0.1, 0.0]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))


def test_putback():
    """Test attributing impact for a putback."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.REBOUND,
                EventTypes.FIELD_GOAL_MADE,
            ],
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": ["REB", "FGM"],
            "VISITORDESCRIPTION": None,
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "SHOT_VALUE": [0.0, 1.5],
            "TIME": 1,
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.05, 0.05]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0]))


def test_putback_fga():
    """Test attributing impact for a missed putback."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.REBOUND,
                EventTypes.FIELD_GOAL_MISSED,
            ],
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": ["REB", "FGM"],
            "VISITORDESCRIPTION": None,
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "SHOT_VALUE": [0.0, 1.5],
            "TIME": 1,
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.05, 0.05]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0]))


def test_foul_putback_and1():
    """Test attributing impact for an and-one putback."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.REBOUND,
                EventTypes.FIELD_GOAL_MADE,
                EventTypes.FOUL,
                EventTypes.FREE_THROW
            ],
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": ["REB", "FGM", None, "FT"],
            "VISITORDESCRIPTION": [None, None, "FOUL", None],
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": 1,
            "SHOT_VALUE": [0.0, 1.5, 0.0, 0.0],
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.05, 0.0, -0.1, 0.05]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))

def test_foul_putback():
    """Test attributing impact for a foul and missed putback."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.REBOUND,
                EventTypes.FOUL,
                EventTypes.FREE_THROW,
                EventTypes.FREE_THROW
            ],
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": ["REB", None, "FT", "FT"],
            "VISITORDESCRIPTION": [None, "FOUL", None, None],
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": 1,
            "SHOT_VALUE": [0.0, 0.0, 0.75, 0.75],
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.05, -0.1, 0.0, 0.05]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0]))


def test_foul_putback_and1_missed_ft():
    """Test attributing impact for an and-one putback with missed free throw."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.REBOUND,
                EventTypes.FIELD_GOAL_MADE,
                EventTypes.FOUL,
                EventTypes.FREE_THROW,
                EventTypes.REBOUND
            ],
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": ["REB", "FGM", None, "FT", None],
            "VISITORDESCRIPTION": [None, None, "FOUL", None, None],
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": 1,
            "SHOT_VALUE": [0.0, 1.5, 0.0, 0.0, 0.0],
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.05, 0.0, -0.1, 0.05, 0.0]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0, 0.0]))


def test_foul_putback_missed_ft():
    """Test attributing imapct for a foul, missed putback, and missed free throw."""
    df = pd.DataFrame(
        {
            "EVENTMSGTYPE": [
                EventTypes.REBOUND,
                EventTypes.FOUL,
                EventTypes.FREE_THROW,
                EventTypes.FREE_THROW,
                EventTypes.REBOUND
            ],
            "NBA_WIN_PROB_CHANGE": 0.1,
            "HOMEDESCRIPTION": ["REB", None, "FT", "FT", None],
            "VISITORDESCRIPTION": [None, "FOUL", None, None, None],
            "PLAYER1_ID": 0,
            "PLAYER2_ID": 0,
            "HOME_TEAM_ID": 161,
            "VISITOR_TEAM_ID": 162,
            "TIME": 1,
            "SHOT_VALUE": [0.0, 0.0, 0.75, 0.75, 0.0],
            "HOME_OFF_RATING": 100,
            "VISITOR_OFF_RATING": 100,
            "PLAYER1_IMPACT": 0.0,
            "PLAYER2_IMPACT": 0.0,
            "PLAYER3_IMPACT": 0.0,
        }
    )

    tsk = CompoundPlayerImpact()
    output = tsk.run(pbp=df, mode="nba")

    assert output["PLAYER1_IMPACT"].equals(pd.Series([0.05, -0.1, 0.0, 0.05, 0.0]))
    assert output["PLAYER2_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0, 0.0]))
    assert output["PLAYER3_IMPACT"].equals(pd.Series([0.0, 0.0, 0.0, 0.0, 0.0]))
