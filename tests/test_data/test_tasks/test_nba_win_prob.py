"""Test adding NBA win probability."""

import numpy as np
import pandas as pd

from nbaspa.data.tasks import AddNBAWinProbability, SurvivalTime

def test_adding_win_prob(pbp, win_prob):
    """Test joining NBA win probability to PBP data."""
    pre = SurvivalTime()
    df = pre.run(pbp)
    tsk = AddNBAWinProbability()
    output = tsk.run(pbp=df, winprob=win_prob)
    output["NBA_WIN_PROB_CHANGE"] = np.round(output["NBA_WIN_PROB_CHANGE"], 2)

    assert output["NBA_WIN_PROB"].equals(
        pd.Series([0.51, 0.51, 0.48, 0.49, 0.49, 0.6, 0.65, 0.65], name="NBA_WIN_PROB")
    )
    assert output["NBA_WIN_PROB_CHANGE"].equals(
        pd.Series([0.0, 0.0, -0.03, 0.01, 0.01, 0.0, 0.05, 0.0])
    )
