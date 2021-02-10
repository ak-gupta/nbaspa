"""Clean game-level data."""

import sys
import datetime
import json
import logging
from pathlib import Path
from typing import List, Dict

from nba_survival.data.pipeline import gen_pipeline, run_pipeline

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
    ERRORS: int = 0
    try:
        for call in CALLS:
            output = run_pipeline(**call)
            if not output.is_successful():
                REPORT.append(
                    {"GameDate": call["GameDate"], "mode": call["mode"]}
                )
            elif call["mode"] == "model":
                df = output.result[PIPELINE.get_tasks(name="Merge")[0]].result
                grouped = df.groupby("GAME_ID")
                for _, game in grouped:
                    if (
                        sum(game["HOME_LINEUP_PLUS_MINUS"] == game["HOME_NET_RATING"]) > 0
                    ) or (
                        sum(game["VISITOR_LINEUP_PLUS_MINUS"] == game["VISITOR_NET_RATING"]) > 0
                    ):
                        ERRORS += 1
    except KeyboardInterrupt:
        pass
    finally:
        LOG.warning(f"There were {ERRORS} games with errors in lineup plus minus generation")
        with open(Path("nba-data", "2018-19", "cleaning-report.json"), "w") as outfile:
            json.dump(REPORT, outfile, indent=4)
