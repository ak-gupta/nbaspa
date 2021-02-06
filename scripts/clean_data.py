"""Clean game-level data."""

import sys
import datetime
import logging
from typing import List, Dict

from nba_survival.data.pipeline import gen_pipeline, run_pipeline

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

START = datetime.datetime.strptime("2018-10-16", "%Y-%m-%d")
END = datetime.datetime.strptime("2019-04-10", "%Y-%m-%d")

PIPELINE = gen_pipeline()

def generate_calls() -> List[Dict]:
    """Generate the list of game dates.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    calls: List[Dict] = []
    for n in range(int((END - START).days) + 1):
        game_date = START + datetime.timedelta(n)
        calls.append(
            {
                "flow": PIPELINE,
                "output_dir": "nba-data/2018-19",
                "save_data": True,
                "Season": "2018-19",
                "GameDate": game_date.strftime("%m/%d/%Y")
            }
        )
    
    return calls

if __name__ == "__main__":
    CALLS = generate_calls()
    for call in CALLS:
        run_pipeline(**call)
