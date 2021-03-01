"""Test generating the scoring margin."""

import pandas as pd

from nbaspa.data.tasks import FillMargin, SurvivalTime

def test_margin(pbp):
    """Test filling the margin."""
    pre = SurvivalTime()
    df = pre.run(pbp)
    tsk = FillMargin()
    output = tsk.run(df)
    output.sort_values("GAME_ID", ascending=True, inplace=True)

    assert output["SCOREMARGIN"].equals(
        pd.Series([0, 0, -1, -1, -1, 0, 2, 2], name="SCOREMARGIN")
    )
