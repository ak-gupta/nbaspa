"""Test generating the scoring margin."""

import pandas as pd

from nbaspa.data.tasks import FillMargin

def test_margin():
    """Test filling the margin."""
    df = pd.DataFrame(
        {
            "GAME_ID": [
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2",
            ],
            "TIME": [0, 0, 10, 0, 5, 10],
            "EVENTNUM": [2, 3, 4, 2, 3, 4],
            "SCOREMARGIN": ["TIE", None, "-2", "TIE", "2", None]
        }
    )
    tsk = FillMargin()
    output = tsk.run(df)
    output.sort_values("GAME_ID", ascending=True, inplace=True)

    assert output.equals(
        pd.DataFrame(
            {
                "GAME_ID": [
                    "00218DUMMY1",
                    "00218DUMMY1",
                    "00218DUMMY1",
                    "00218DUMMY2",
                    "00218DUMMY2",
                    "00218DUMMY2",
                ],
                "TIME": [0, 0, 10, 0, 5, 10],
                "EVENTNUM": [2, 3, 4, 2, 3, 4],
                "SCOREMARGIN": [0, 0, -2, 0, 2, 2]
            }
        )
    )
