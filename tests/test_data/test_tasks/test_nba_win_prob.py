"""Test adding NBA win probability."""

import numpy as np
import pandas as pd

from nbaspa.data.tasks import AddNBAWinProbability

def test_adding_win_prob():
    """Test joining NBA win probability to PBP data."""
    pbp = pd.DataFrame(
        {
            "GAME_ID": [
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2"
            ],
            "TIME": [0.0, 0.0, 10.0, 0.0, 5.0, 10.0],
            "EVENTNUM": [2, 3, 4, 2, 3, 4]
        }
    )
    win = pd.DataFrame(
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
    tsk = AddNBAWinProbability()
    output = tsk.run(pbp=pbp, winprob=win)
    output["NBA_WIN_PROB_CHANGE"] = np.round(output["NBA_WIN_PROB_CHANGE"], 2)

    real = pd.DataFrame(
        {
            "GAME_ID": [
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2"
            ],
            "TIME": [0.0, 0.0, 10.0, 0.0, 5.0, 10.0],
            "EVENTNUM": [2, 3, 4, 2, 3, 4],
            "NBA_WIN_PROB": [0.51, 0.51, 0.48, 0.6, 0.65, 0.65],
            "NBA_WIN_PROB_CHANGE": [0.0, 0.0, -0.03, 0.0, 0.05, 0.0]
        },
        columns=["GAME_ID", "TIME", "EVENTNUM", "NBA_WIN_PROB", "NBA_WIN_PROB_CHANGE"],
    )

    assert output.equals(real)
