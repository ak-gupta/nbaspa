"""Test data segmentation tasks."""

import numpy as np
import pandas as pd

from nbaspa.model.tasks import CollapseData, SurvivalData, SegmentData

def test_lifelines_data():
    """Test creating the lifelines data."""
    df = pd.DataFrame(
        {
            "GAME_ID": "00218DUMMY1",
            "HOME_NET_RATING": 3.5,
            "VISITOR_NET_RATING": 2.0,
            "HOME_W_PCT": 0.5,
            "VISITOR_W_PCT": 0.33,
            "LAST_GAME_WIN": 1.0,
            "HOME_GAMES_IN_LAST_3_DAYS": 0.0,
            "VISITOR_GAMES_IN_LAST_3_DAYS": 1.0,
            "HOME_GAMES_IN_LAST_5_DAYS": 1.0,
            "VISITOR_GAMES_IN_LAST_5_DAYS": 2.0,
            "HOME_GAMES_IN_LAST_7_DAYS": 3.0,
            "VISITOR_GAMES_IN_LAST_7_DAYS": 4.0,
            "SCOREMARGIN": [
                0, 0, 0, 0, 2, 2, 2, 0, 0, -3,
            ],
            "HOME_LINEUP_PLUS_MINUS": 4.5,
            "VISITOR_LINEUP_PLUS_MINUS": 6.0,
            "TIME": [
                0, 10, 40, 60, 75, 90, 105, 110, 125, 130
            ],
            "WIN": 0,
            "NBA_WIN_PROB": [
                0.5, 0.5, 0.5, 0.5, 0.6, 0.62, 0.58, 0.5, 0.5, 0.35
            ],
        }
    )
    tsk = SurvivalData()
    output = tsk.run(df)
    real = pd.DataFrame(
        {
            "GAME_ID": "00218DUMMY1",
            "HOME_NET_RATING": 3.5,
            "VISITOR_NET_RATING": 2.0,
            "HOME_W_PCT": 0.5,
            "VISITOR_W_PCT": 0.33,
            "LAST_GAME_WIN": 1.0,
            "HOME_GAMES_IN_LAST_3_DAYS": 0.0,
            "VISITOR_GAMES_IN_LAST_3_DAYS": 1.0,
            "HOME_GAMES_IN_LAST_5_DAYS": 1.0,
            "VISITOR_GAMES_IN_LAST_5_DAYS": 2.0,
            "HOME_GAMES_IN_LAST_7_DAYS": 3.0,
            "VISITOR_GAMES_IN_LAST_7_DAYS": 4.0,
            "SCOREMARGIN": [0, 2, 0],
            "start": [0, 75, 110],
            "stop": [75.0, 110.0, 130.0],
            "HOME_LINEUP_PLUS_MINUS": 4.5,
            "VISITOR_LINEUP_PLUS_MINUS": 6.0,
            "WIN": False,
            "NBA_WIN_PROB": [0.6, 0.5, 0.35]
        }
    )

    assert output.sort_index(
        axis=1, ascending=True
    ).equals(
        real.sort_index(axis=1, ascending=True)
    )

def test_segment_data(data):
    """Test creating dataset splits."""
    tsk = SegmentData()
    output = tsk.run(data=data, splits=[0.6, 0.4], keys=["train", "test"])

    assert len(output) == 2
    assert len(np.unique(output["train"]["GAME_ID"])) == 120
    assert len(np.unique(output["test"]["GAME_ID"])) == 80

    tsk = SegmentData()
    output = tsk.run(data=data, splits=[0.6, 0.2, 0.2], keys=["train", "tune", "stop"])

    assert len(output) == 3
    assert len(np.unique(output["train"]["GAME_ID"])) == 120
    assert len(np.unique(output["tune"]["GAME_ID"])) == 40
    assert len(np.unique(output["stop"]["GAME_ID"])) == 40

def test_collapse_data_lr(data):
    """Test collapsing the data."""
    pre = SurvivalData()
    df = pre.run(data)
    # Check collapsing the data to the final row
    tsk = CollapseData()
    output = tsk.run(data=df)

    assert len(output) == 150
    assert output.equals(
        df.groupby("GAME_ID").tail(n=1)
    )
