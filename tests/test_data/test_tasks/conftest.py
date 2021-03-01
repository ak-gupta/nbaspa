"""Define some fixtures."""

import numpy as np
import pandas as pd
import pytest

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
