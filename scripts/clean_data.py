"""Clean game-level data."""

import sys
import datetime
import json
import logging
from pathlib import Path
from typing import List, Dict

from nbaspa.data.pipeline import gen_pipeline, run_pipeline

LOG = logging.getLogger(__name__)

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
        calls += [
            {
                "flow": PIPELINE,
                "output_dir": "nba-data/2018-19",
                "save_data": True,
                "mode": "model",
                "Season": "2018-19",
                "GameDate": game_date.strftime("%m/%d/%Y")
            },
            {
                "flow": PIPELINE,
                "output_dir": "nba-data/2018-19",
                "save_data": True,
                "mode": "rating",
                "Season": "2018-19",
                "GameDate": game_date.strftime("%m/%d/%Y")
            }
        ]
    
    return calls

if __name__ == "__main__":
    CALLS = generate_calls()
    REPORT: List = []
    try:
        for call in CALLS:
            output = run_pipeline(**call)
            if not output.is_successful():
                scoreboard = output.result[
                    PIPELINE.get_tasks(name="Load scoreboard data")[0]
                ].result
                if scoreboard["GameHeader"].empty:
                    REPORT.append(
                        {
                            "GameDate": call["GameDate"],
                            "mode": call["mode"],
                            "reason": "No games"
                        }
                    )
                else:
                    REPORT.append(
                        {
                            "GameDate": call["GameDate"],
                            "mode": call["mode"],
                            "reason": "Unknown"
                        }
                    )
    except KeyboardInterrupt:
        pass
    finally:
        LOG.info("Creating cleaning report...")
        with open(Path("nba-data", "2018-19", "cleaning-report.json"), "w") as outfile:
            json.dump(REPORT, outfile, indent=4)
