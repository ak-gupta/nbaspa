"""Test adding shotchart data."""

import numpy as np
import pandas as pd

from nbaspa.data.tasks import AddExpectedShotValue, AddShotDetail

def test_add_shot_detail(pbp, shotchart):
    """Test adding shotchart details."""
    tsk = AddShotDetail()
    output = tsk.run(pbp=pbp, shotchart=shotchart)

    print(output)

    assert output["SHOT_VALUE"].equals(
        pd.Series(
            [np.nan, np.nan, 1, np.nan, np.nan, 2], name="SHOT_VALUE"
        )
    )
    assert output["SHOT_ZONE_BASIC"].equals(
        pd.Series(
            [np.nan, np.nan, np.nan, np.nan, np.nan, "Restricted Area"], name="SHOT_ZONE_BASIC"
        )
    )

def test_add_expected_value(pbp, shotzonedashboard, overallshooting, shotchart):
    """Test adding expected shot value."""
    pre = AddShotDetail()
    df = pre.run(pbp=pbp, shotchart=shotchart)
    tsk = AddExpectedShotValue()
    output = tsk.run(pbp=df, shotzonedashboard=shotzonedashboard, overallshooting=overallshooting)

    assert output["SHOT_VALUE"].equals(
        pd.Series(
            [np.nan, np.nan, 0.85, np.nan, np.nan, 1.30], name="SHOT_VALUE"
        )
    )
    assert output["FG_PCT"].equals(
        pd.Series(
            [np.nan, np.nan, 0.85, np.nan, np.nan, 0.65], name="FG_PCT"
        )
    )
