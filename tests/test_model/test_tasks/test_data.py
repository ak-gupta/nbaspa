"""Test data segmentation tasks."""

import numpy as np
import pandas as pd

from nbaspa.model.tasks import SurvivalData, SegmentData

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

def test_segment_data():
    """Test creating dataset splits."""
    gamelist = []
    for i in range(10):
        gamelist += [f"00218DUMMY{i}"] * 10
    df = pd.DataFrame({"GAME_ID": gamelist})
    tsk = SegmentData()
    output = tsk.run(data=df, splits=[0.6], keys=["train", "test"])

    assert len(output) == 2
    assert len(output["train"]) == 60
    assert len(output["test"]) == 40
    assert len(np.unique(output["train"]["GAME_ID"])) == 6
    assert len(np.unique(output["test"]["GAME_ID"])) == 4

    tsk = SegmentData()
    output = tsk.run(data=df, splits=[0.6, 0.2, 0.2], keys=["train", "tune", "stop"])

    assert len(output) == 3
    assert len(output["train"]) == 60
    assert len(output["tune"]) == 20
    assert len(output["stop"]) == 20
    assert len(np.unique(output["train"]["GAME_ID"])) == 6
    assert len(np.unique(output["tune"]["GAME_ID"])) == 2
    assert len(np.unique(output["stop"]["GAME_ID"])) == 2
