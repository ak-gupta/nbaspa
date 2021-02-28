"""Test adding the net rating."""

import pandas as pd

from nbaspa.data.tasks import AddNetRating, AddTeamID

def test_add_net_rating(pbp, header, stats):
    """Test adding the net rating."""
    pre = AddTeamID()
    df = pre.run(pbp=pbp, header=header)
    tsk = AddNetRating()
    output = tsk.run(pbp=df, stats=stats)

    assert output["HOME_OFF_RATING"].equals(
        pd.Series(
            [110.5, 110.5, 110.5, 120.5, 120.5, 120.5], name="HOME_OFF_RATING"
        )
    )
    assert output["VISITOR_OFF_RATING"].equals(
        pd.Series(
            [120.5, 120.5, 120.5, 110.5, 110.5, 110.5], name="VISITOR_OFF_RATING"
        )
    )
    assert output["HOME_NET_RATING"].equals(
        pd.Series(
            [-3.5, -3.5, -3.5, 6.5, 6.5, 6.5], name="HOME_NET_RATING"
        )
    )
    assert output["VISITOR_NET_RATING"].equals(
        pd.Series(
            [6.5, 6.5, 6.5, -3.5, -3.5, -3.5], name="VISITOR_NET_RATING"
        )
    )