"""Test scoreboard metadata tasks."""

import numpy as np
import pandas as pd

from nbaspa.data.tasks import AddTeamID, AddLastMeetingResult

def test_add_team_id(pbp, header):
    """Test adding the team ID."""
    tsk = AddTeamID()
    output = tsk.run(pbp=pbp, header=header)

    assert output["GAME_DATE_EST"].equals(
        pd.to_datetime(
            pd.Series(
                [
                    "2018-12-25T00:00:00",
                    "2018-12-25T00:00:00",
                    "2018-12-25T00:00:00",
                    "2018-12-26T00:00:00",
                    "2018-12-26T00:00:00",
                    "2018-12-26T00:00:00",
                ],
                name="GAME_DATE_EST"
            )
        )
    )
    assert output["HOME_TEAM_ID"].equals(
        pd.Series(
            [
                1610612761,
                1610612761,
                1610612761,
                1610612760,
                1610612760,
                1610612760,
            ],
            name="HOME_TEAM_ID"
        )
    )
    assert output["VISITOR_TEAM_ID"].equals(
        pd.Series(
            [
                1610612760,
                1610612760,
                1610612760,
                1610612761,
                1610612761,
                1610612761,
            ],
            name="VISITOR_TEAM_ID"
        )
    )

def test_last_meeting_result(pbp, header, last_meeting):
    """Test logging last team result."""
    pre = AddTeamID()
    precursor = pre.run(pbp=pbp, header=header)

    tsk = AddLastMeetingResult()
    output = tsk.run(pbp=precursor, last_meeting=last_meeting)

    assert output["LAST_GAME_WIN"].equals(
        pd.Series([0, 0, 0, 1, 1, 1], name="LAST_GAME_WIN")
    )
