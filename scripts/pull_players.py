"""Pull player shooting dashboards."""

import sys
import logging
from typing import List, Tuple

from nba_survival.data import NBADataFactory
from nba_survival.data.endpoints import AllPlayers

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

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
    # Get the list of players
    players = AllPlayers(
        Season="2018-19",
        IsOnlyCurrentSeason="0",
        output_dir="nba-data/2018-19"
    )
    players.get()
    players_df = players.get_data()
    # Get the shooting
    calls: List[str] = []
    for _, row in players_df.iterrows():
        if int(row["TO_YEAR"]) >= 2017:
            calls += [
                ("PlayerDashboardShooting", {"PlayerID": row["PERSON_ID"], "Season": "2018-19"}),
                ("PlayerDashboardGeneral", {"PlayerID": row["PERSON_ID"], "Season": "2018-19"})
            ]
    
    return calls

if __name__ == "__main__":
    CALLS = generate_calls()

    FACTORY = NBADataFactory(calls=CALLS, output_dir="nba-data/2018-19")
    FACTORY.get()
