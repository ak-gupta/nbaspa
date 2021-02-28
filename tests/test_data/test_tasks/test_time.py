"""Test the ``time.py`` module."""

import pandas as pd

from nbaspa.data.tasks import DeDupeTime, SurvivalTime

def test_survival_time():
    """Test calculating the survival time."""
    df = pd.DataFrame(
        {
            "PCTIMESTRING": [
                "12:00",
                "11:45",
                "0:00",
                "12:00",
                "11:45",
                "0:00",
                "12:00",
                "11:45",
                "0:00",
                "12:00",
                "11:45",
                "0:00",
                "2:30",
                "2:30",
            ],
            "PERIOD": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 6]
        }
    )
    tsk = SurvivalTime()
    output = tsk.run(df)

    assert output["TIME"].equals(
        pd.Series(
            [
                0.0,
                15.0,
                720.0,
                720.0,
                735.0,
                1440.0,
                1440.0,
                1455.0,
                2160.0,
                2160.0,
                2175.0,
                2880.0,
                3030.0,
                3330.0
            ],
        )
    )

def test_dedupe():
    """Test de-duping time."""
    df = pd.DataFrame(
        {
            "GAME_ID": [
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY1",
                "00218DUMMY2",
                "00218DUMMY2",
                "00218DUMMY2"
            ],
            "TIME": [0, 0, 10, 0, 0, 10],
            "EVENTNUM": [2, 3, 4, 2, 3, 4],
        }
    )
    tsk = DeDupeTime()
    output = tsk.run(df)

    assert output.equals(
        pd.DataFrame(
            {
                "GAME_ID": ["00218DUMMY1", "00218DUMMY1", "00218DUMMY2", "00218DUMMY2"],
                "TIME": [0, 10, 0, 10],
                "EVENTNUM": [3, 4, 3, 4]
            },
            index=[1, 2, 4, 5]
        )
    )
