"""Pull team data."""

import sys
import logging
from typing import List, Tuple

from nbaspa.data import NBADataFactory
from nbaspa.data.endpoints.parameters import ParameterValues

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def generate_calls() -> List[Tuple]:
    """Generate the list of calls

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    calls: List[str] = [
        ("TeamStats", {"Season": "2018-19"})
    ]
    teams = ParameterValues().TeamID
    for team in teams:
        if not str(team).startswith("16"):
            continue

        calls += [
            (
                "TeamLineups",
                {
                    "TeamID": team,
                    "Season": "2018-19"
                }
            ),
            (
                "TeamGameLog",
                {
                    "TeamID": team,
                    "Season": "2018-19"
                }
            )
        ]
    
    return calls

if __name__ == "__main__":
    CALLS = generate_calls()

    FACTORY = NBADataFactory(calls=CALLS, output_dir="nba-data/2018-19")
    FACTORY.get()
