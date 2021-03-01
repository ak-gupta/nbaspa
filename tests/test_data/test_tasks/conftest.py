"""Define some fixtures."""

import numpy as np
import pandas as pd
import pytest

@pytest.fixture
def pbp():
    """Dummy play-by-play data."""
    return pd.DataFrame(
        {
            "GAME_ID": [
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
            ],
            "PCTIMESTRING": [
                "12:00",
                "12:00",
                "11:50",
                "11:40",
                "11:40",
                "12:00",
                "11:55",
                "11:50"
            ],
            "PERIOD": 1,
            "EVENTNUM": [2, 3, 4, 5, 6, 2, 3, 4],
            "EVENTMSGTYPE": [12, 9, 3, 8, 8, 12, 2, 1],
            "HOMEDESCRIPTION": [
                None,
                None,
                None,
                "HOME SUBSTITUTION",
                None,
                None,
                None,
                None,
            ],
            "VISITORDESCRIPTION": [
                None,
                None,
                "FREE THROW MADE",
                None,
                "VISITOR SUBSTITUTION",
                None,
                None,
                None,
            ],
            "PLAYER1_ID": [np.nan, np.nan, 7, 5, 9, np.nan, np.nan, 1],
            "PLAYER2_ID": [np.nan, np.nan, np.nan, 6, 12, np.nan, np.nan, np.nan],
            "SCOREMARGIN": ["TIE", None, "-1", None, None, "TIE", "2", None]
        }
    )

@pytest.fixture
def header():
    """Dummy header data."""
    return pd.DataFrame(
        {
            "GAME_ID": ["00218DUMMY1", "00218DUMMY2"],
            "GAME_DATE_EST": ["2018-12-25T00:00:00", "2018-12-26T00:00:00"],
            "HOME_TEAM_ID": [1610612761, 1610612760],
            "VISITOR_TEAM_ID": [1610612760, 1610612761],
        }
    )

@pytest.fixture
def last_meeting():
    """Dummy last meeting data."""
    return pd.DataFrame(
        {
            "GAME_ID": ["00218DUMMY1", "00218DUMMY2"],
            "LAST_GAME_HOME_TEAM_POINTS": [100, 100],
            "LAST_GAME_VISITOR_TEAM_POINTS": [120, 120],
            "LAST_GAME_HOME_TEAM_ID": [1610612761, 1610612761],
            "LAST_GAME_VISITOR_TEAM_ID": [1610612760, 1610612760],
        }
    )

@pytest.fixture
def win_prob():
    """Dummy NBA win probability."""
    return pd.DataFrame(
        {
            "GAME_ID": [
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2"
            ],
            "EVENT_NUM": [
                2, 3, np.nan, 4, np.nan, 6, 2, np.nan, 3, 4
            ],
            "HOME_PCT": [
                0.5, 0.51, 0.52, 0.48, 0.49, 0.49, 0.6, 0.61, 0.65, 0.65
            ]
        }
    )

@pytest.fixture
def gamelog():
    """Dummy gamelog data."""
    return pd.DataFrame(
        {
            "Team_ID": [
                1610612761,
                1610612761,
                1610612761,
                1610612760,
                1610612760,
                1610612760
            ],
            "Game_ID": [
                "00218DUMMY0",
                "00218DUMMY1",
                "00218DUMMY2",
                "00218DUMMY0",
                "00218DUMMY1",
                "00218DUMMY2"
            ],
            "GAME_DATE": [
                "2018-12-23T00:00:00",
                "2018-12-25T00:00:00",
                "2018-12-26T00:00:00",
                "2018-12-20T00:00:00",
                "2018-12-25T00:00:00",
                "2018-12-26T00:00:00"
            ],
            "W_PCT": [
                1.0,
                0.5,
                0.33,
                0.0,
                0.5,
                0.66
            ]
        }
    )

@pytest.fixture
def stats():
    """Dummy team stats data."""
    return pd.DataFrame(
        {
            "TEAM_ID": [1610612761, 1610612760],
            "E_OFF_RATING": [110.5, 120.5],
            "E_NET_RATING": [-3.5, 6.5],
        }
    )

@pytest.fixture
def shotchart():
    """Create a dummy shotchart."""
    return pd.DataFrame(
        {
            "GAME_ID": ["00218DUMMY2"],
            "TEAM_ID": [1610612761],
            "GAME_EVENT_ID": [4],
            "PLAYER_ID": [1],
            "SHOT_TYPE": ["2PT Field Goal"],
            "SHOT_ZONE_BASIC": ["Restricted Area"],
        }
    )

@pytest.fixture
def shotzonedashboard():
    """Dummy shooting dashboard."""
    return pd.DataFrame(
        {
            "PLAYER_ID": [1],
            "GROUP_VALUE": ["Restricted Area"],
            "FG_PCT": [0.65]
        }
    )

@pytest.fixture
def overallshooting():
    """Dummy general dashboard."""
    return pd.DataFrame(
        {
            "PLAYER_ID": [7],
            "FT_PCT": [0.85],
        }
    )

@pytest.fixture
def homerotation():
    """Dummy home rotation data."""
    return pd.DataFrame(
        {
            "GAME_ID": [
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
            ],
            "TEAM_ID": [
                1610612761,
                1610612761,
                1610612761,
                1610612761,
                1610612761,
                1610612761,
                1610612760,
                1610612760,
                1610612760,
                1610612760,
                1610612760,
            ],
            "PERSON_ID": [
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
            ],
            "IN_TIME_REAL": [
                0.0, 0.0, 0.0, 0.0, 0.0, 200.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            "OUT_TIME_REAL": [
                28800.0,
                28800.0,
                28800.0,
                28800.0,
                200.0,
                28800.0,
                28800.0,
                28800.0,
                28800.0,
                28800.0,
                28800.0,
            ],
        }
    )

@pytest.fixture
def awayrotation():
    """Dummy away rotation data."""
    return pd.DataFrame(
        {
            "GAME_ID": [
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
            ],
            "TEAM_ID": [
                1610612760,
                1610612760,
                1610612760,
                1610612760,
                1610612760,
                1610612760,
                1610612761,
                1610612761,
                1610612761,
                1610612761,
                1610612761,
            ],
            "PERSON_ID": [
                7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5
            ],
            "IN_TIME_REAL": [
                0.0, 0.0, 0.0, 0.0, 0.0, 200.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            "OUT_TIME_REAL": [
                28800.0,
                28800.0,
                28800.0,
                28800.0,
                200.0,
                28800.0,
                28800.0,
                28800.0,
                28800.0,
                28800.0,
                28800.0,
            ],
        }
    )

@pytest.fixture
def lineup_stats():
    """Dummy lineup stats."""
    return pd.DataFrame(
        {
            "GROUP_ID": [
                "-2-1-3-5-4-",
                "-2-4-3-1-6-",
                "-7-9-8-10-11"
            ],
            "E_NET_RATING": [4.5, 6.0, 1.5]
        }
    )
