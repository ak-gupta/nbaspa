"""Define CLI endpoints for downloading data."""

import datetime
import logging
from pathlib import Path
import sys
from typing import List

import click

from ..endpoints import AllPlayers, Scoreboard
from ..endpoints.parameters import ParameterValues, SEASONS
from ..factory import NBADataFactory

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


@click.group()
def download():
    """CLI group."""
    pass


@download.command()
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
def scoreboard(output_dir, season):
    """Download the scoreboard data."""
    # Generate the list of calls
    calls: List[str] = []
    for n in range(int((SEASONS[season]["END"] - SEASONS[season]["START"]).days) + 1):
        game_date = SEASONS[season]["START"] + datetime.timedelta(n)
        calls.append(("Scoreboard", {"GameDate": game_date.strftime("%m/%d/%Y")}))

    factory = NBADataFactory(calls=calls, output_dir=Path(output_dir, season))
    factory.get()


@download.command()
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
def games(output_dir, season):
    """Download the game data."""
    calls: List[str] = []
    for n in range(int((SEASONS[season]["END"] - SEASONS[season]["START"]).days) + 1):
        game_date = SEASONS[season]["START"] + datetime.timedelta(n)
        # Get the scoreboard data
        score = Scoreboard(
            GameDate=game_date.strftime("%m/%d/%Y"), output_dir=Path(output_dir, season)
        )
        score.get()
        df = score.get_data("GameHeader")
        for _, row in df.iterrows():
            calls += [
                ("PlayByPlay", {"GameID": row["GAME_ID"]}),
                ("ShotChart", {"GameID": row["GAME_ID"], "Season": season}),
                ("GameRotation", {"GameID": row["GAME_ID"]}),
                ("WinProbability", {"GameID": row["GAME_ID"]}),
                ("BoxScoreTraditional", {"GameID": row["GAME_ID"]}),
            ]

    factory = NBADataFactory(calls=calls, output_dir=Path(output_dir, season))
    factory.get()


@download.command()
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
def teams(output_dir, season):
    """Download team-level data."""
    calls: List[str] = [("TeamStats", {"Season": season})]
    teams = ParameterValues().TeamID
    for team in teams:
        if not str(team).startswith("16"):
            continue

        calls += [
            (
                "TeamLineups",
                {"TeamID": team, "Season": season, "MeasureType": "Advanced"},
            ),
            ("TeamGameLog", {"TeamID": team, "Season": season}),
        ]

    factory = NBADataFactory(calls=calls, output_dir=Path(output_dir, season))
    factory.get()


@download.command()
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
def players(output_dir, season):
    """Download all player-level data."""
    # Get the list of players
    players = AllPlayers(
        Season=season, IsOnlyCurrentSeason="0", output_dir=Path(output_dir, season)
    )
    players.get()
    players_df = players.get_data()
    # Get the shooting
    calls: List[str] = []
    for _, row in players_df.iterrows():
        if int(row["TO_YEAR"]) >= int(season[0:4]) and int(row["FROM_YEAR"]) <= int(
            season[0:4]
        ):
            calls += [
                (
                    "PlayerDashboardShooting",
                    {"PlayerID": row["PERSON_ID"], "Season": season},
                ),
                (
                    "PlayerDashboardGeneral",
                    {"PlayerID": row["PERSON_ID"], "Season": season},
                ),
            ]

    factory = NBADataFactory(calls=calls, output_dir=Path(output_dir, season))
    factory.get()
