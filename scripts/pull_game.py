"""Pull game data."""

import sys
import datetime
import logging
from typing import List, Tuple

from nba_survival.data import NBADataFactory
from nba_survival.data.endpoints import Scoreboard

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
    List
        The list of calls for ``NBADataFactory``
    """
    calls: List[str] = []
    for n in range(int((END - START).days) + 1):
        game_date = START + datetime.timedelta(n)
        # Get the scoreboard data
        score = Scoreboard(
            GameDate=game_date.strftime("%m/%d/%Y"),
            output_dir="nba-data/2018-19"
        )
        score.get()
        df = score.get_data("GameHeader")
        for index, row in df.iterrows():
            calls += [
                ("PlayByPlay", {"GameID": row["GAME_ID"]}),
                ("ShotChart", {"GameID": row["GAME_ID"]}),
                ("GameRotation", {"GameID": row["GAME_ID"]}),
                ("WinProbability", {"GameID": row["GAME_ID"]}),
                ("BoxScoreTraditional", {"GameID": row["GAME_ID"]})
            ]
    
    return calls

if __name__ == "__main__":
    CALLS = generate_calls()

    FACTORY = NBADataFactory(calls=CALLS, output_dir="nba-data/2018-19")
    FACTORY.get()
