"""Test adding lineup plus minus."""

import pandas as pd

from nbaspa.data.tasks import (
    AddLineupPlusMinus,
    AddTeamID,
    AddNetRating,
    SurvivalTime
)

def test_add_lineup_net_rating(pbp, header, stats, homerotation, awayrotation, lineup_stats):
    """Test adding lineup net rating."""
    timetask = SurvivalTime()
    timed = timetask.run(pbp=pbp)
    addteamtask = AddTeamID()
    team = addteamtask.run(pbp=timed, header=header)
    net = AddNetRating()
    df = net.run(pbp=team, stats=stats)
    tsk = AddLineupPlusMinus()
    output = tsk.run(
        pbp=df,
        lineup_stats=lineup_stats,
        home_rotation=homerotation,
        away_rotation=awayrotation
    )

    print(output[["HOME_LINEUP", "VISITOR_LINEUP"]])

    assert output["HOME_LINEUP"].equals(
        pd.Series(
            [
                "1-2-3-4-5",
                "1-2-3-4-5",
                "1-2-3-4-5",
                "1-2-3-4-6",
                "1-2-3-4-6",
                "10-11-7-8-9",
                "10-11-7-8-9",
                "10-11-7-8-9",
            ],
            name="HOME_LINEUP"
        )
    )
    assert output["HOME_LINEUP_PLUS_MINUS"].equals(
        pd.Series(
            [4.5, 4.5, 4.5, 6.0, 6.0, 1.5, 1.5, 1.5], name="HOME_LINEUP_PLUS_MINUS"
        )
    )
    assert output["VISITOR_LINEUP"].equals(
        pd.Series(
            [
                "10-11-7-8-9",
                "10-11-7-8-9",
                "10-11-7-8-9",
                "10-11-7-8-9",
                "10-11-12-7-8",
                "1-2-3-4-5",
                "1-2-3-4-5",
                "1-2-3-4-5",
            ],
            name="VISITOR_LINEUP"
        )
    )
    assert output["VISITOR_LINEUP_PLUS_MINUS"].equals(
        pd.Series(
            [1.5, 1.5, 1.5, 1.5, 6.5, 4.5, 4.5, 4.5], name="VISITOR_LINEUP_PLUS_MINUS"
        )
    )
