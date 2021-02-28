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
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
            ],
            "PCTIMESTRING": ["12:00", "12:00", "11:50", "12:00", "11:55", "11:50"],
            "PERIOD": [1, 1, 1, 1, 1, 1],
            "EVENTNUM": [2, 3, 4, 2, 3, 4],
            "SCOREMARGIN": ["TIE", None, "-2", "TIE", "2", None]
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
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2"
            ],
            "EVENT_NUM": [
                2, 3, np.nan, 4, 2, np.nan, 3, 4
            ],
            "HOME_PCT": [
                0.5, 0.51, 0.52, 0.48, 0.6, 0.61, 0.65, 0.65
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
