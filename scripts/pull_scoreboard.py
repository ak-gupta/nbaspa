"""Pull the scoreboard information for a range of dates."""

import sys
import datetime
import logging
from typing import List, Tuple

from nbaspa.data import NBADataFactory

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

START = datetime.datetime.strptime("2018-10-16", "%Y-%m-%d")
END = datetime.datetime.strptime("2019-04-10", "%Y-%m-%d")

def generate_calls() -> List[Tuple]:
    """Generate the list of calls.

    Parameters
    ----------
    None

    Returns
    -------
    """
    calls: List[str] = []
    for n in range(int((END - START).days) + 1):
        game_date = START + datetime.timedelta(n)
        calls.append(
            ("Scoreboard", {"GameDate": game_date.strftime("%m/%d/%Y")})
        )
    
    return calls

if __name__ == "__main__":
    CALLS = generate_calls()

    FACTORY = NBADataFactory(calls=CALLS, output_dir="nba-data")
    FACTORY.get()
