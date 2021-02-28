"""Test target creation."""

import pandas as pd

from nbaspa.data.tasks import CreateTarget, FillMargin, SurvivalTime

def test_target_creation(pbp):
    """Test creating the target variable."""
    timetask = SurvivalTime()
    timedf = timetask.run(pbp)
    margintask = FillMargin()
    df = margintask.run(timedf)
    tsk = CreateTarget()
    output = tsk.run(df)
    output.sort_values(by="GAME_ID", ascending=True, inplace=True)

    assert output["WIN"].equals(
        pd.Series([0, 0, 0, 0, 0, 1], name="WIN")
    )
