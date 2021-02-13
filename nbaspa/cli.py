"""Define CLI endpoints."""

import datetime
import json
import logging
from pathlib import Path
import sys
from typing import Dict, List

import click

from .data.endpoints import AllPlayers, Scoreboard
from .data.endpoints.parameters import ParameterValues
from .data.factory import NBADataFactory
from .data.pipeline import gen_pipeline, run_pipeline

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

SEASONS: Dict = {
    "2017-18": {
        "START": datetime.datetime.strptime("2017-10-17", "%Y-%m-%d"),
        "END": datetime.datetime.strptime("2018-04-11", "%Y-%m-%d")
    },
    "2018-19": {
        "START": datetime.datetime.strptime("2018-10-16", "%Y-%m-%d"),
        "END": datetime.datetime.strptime("2019-04-10", "%Y-%m-%d")
    }
}

@click.group()
def download():
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
        calls.append(
            ("Scoreboard", {"GameDate": game_date.strftime("%m/%d/%Y")})
        )
    
    factory = NBADataFactory(calls=calls, output_dir=Path(output_dir, season))
    factory.get()

@download.command()
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
def game(output_dir, season):
    """Download the game data."""
    calls: List[str] = []
    for n in range(int((SEASONS[season]["END"] - SEASONS[season]["START"]).days) + 1):
        game_date = SEASONS[season]["START"] + datetime.timedelta(n)
        # Get the scoreboard data
        score = Scoreboard(
            GameDate=game_date.strftime("%m/%d/%Y"),
            output_dir=Path(output_dir, season)
        )
        score.get()
        df = score.get_data("GameHeader")
        for index, row in df.iterrows():
            calls += [
                ("PlayByPlay", {"GameID": row["GAME_ID"]}),
                ("ShotChart", {"GameID": row["GAME_ID"], "Season": season}),
                ("GameRotation", {"GameID": row["GAME_ID"]}),
                ("WinProbability", {"GameID": row["GAME_ID"]}),
                ("BoxScoreTraditional", {"GameID": row["GAME_ID"]})
            ]
    
    factory = NBADataFactory(calls=calls, output_dir=Path(output_dir, season))
    factory.get()

@download.command()
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
def teams(output_dir, season):
    """Download team-level data."""
    calls: List[str] = [
        ("TeamStats", {"Season": season})
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
                    "Season": season
                }
            ),
            (
                "TeamGameLog",
                {
                    "TeamID": team,
                    "Season": season
                }
            )
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
        Season=season,
        IsOnlyCurrentSeason="0",
        output_dir=Path(output_dir, season)
    )
    players.get()
    players_df = players.get_data()
    # Get the shooting
    calls: List[str] = []
    for _, row in players_df.iterrows():
        if int(row["TO_YEAR"]) >= int(season[0:4]):
            calls += [
                ("PlayerDashboardShooting", {"PlayerID": row["PERSON_ID"], "Season": season}),
                ("PlayerDashboardGeneral", {"PlayerID": row["PERSON_ID"], "Season": season})
            ]
    
    factory = NBADataFactory(calls=calls, output_dir=Path(output_dir, season))
    factory.get()

@click.group()
def clean():
    pass

@clean.command()
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
def model(output_dir, season):
    """Clean model data."""
    calls: List[Dict] = []
    flow = gen_pipeline()
    for n in range(int((SEASONS[season]["END"] - SEASONS[season]["START"]).days) + 1):
        game_date = SEASONS[season]["START"] + datetime.timedelta(n)
        calls.append(
            {
                "flow": flow,
                "output_dir": Path(output_dir, season),
                "save_data": True,
                "mode": "model",
                "Season": season,
                "GameDate": game_date.strftime("%m/%d/%Y")
            }
        )
    
    report: List = []
    try:
        for call in calls:
            output = run_pipeline(**call)
            if not output.is_successful():
                scoreboard = output.result[
                    flow.get_tasks(name="Load scoreboard data")[0]
                ].result
                if scoreboard["GameHeader"].empty:
                    report.append(
                        {
                            "GameDate": call["GameDate"],
                            "mode": call["mode"],
                            "reason": "No games"
                        }
                    )
                else:
                    report.append(
                        {
                            "GameDate": call["GameDate"],
                            "mode": call["mode"],
                            "reason": "Unknown"
                        }
                    )
    except KeyboardInterrupt:
        pass
    finally:
        with open(Path(output_dir, season, "model-cleaning-report.json"), "w") as outfile:
            json.dump(report, outfile, indent=4)

@clean.command()
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
def rating(output_dir, season):
    """Clean the rating input data."""
    calls: List[Dict] = []
    flow = gen_pipeline()
    for n in range(int((SEASONS[season]["END"] - SEASONS[season]["START"]).days) + 1):
        game_date = SEASONS[season]["START"] + datetime.timedelta(n)
        calls.append(
            {
                "flow": flow,
                "output_dir": Path(output_dir, season),
                "save_data": True,
                "mode": "rating",
                "Season": season,
                "GameDate": game_date.strftime("%m/%d/%Y")
            }
        )

    report: List = []
    try:
        for call in calls:
            output = run_pipeline(**call)
            if not output.is_successful():
                scoreboard = output.result[
                    flow.get_tasks(name="Load scoreboard data")[0]
                ].result
                if scoreboard["GameHeader"].empty:
                    report.append(
                        {
                            "GameDate": call["GameDate"],
                            "mode": call["mode"],
                            "reason": "No games"
                        }
                    )
                else:
                    report.append(
                        {
                            "GameDate": call["GameDate"],
                            "mode": call["mode"],
                            "reason": "Unknown"
                        }
                    )
    except KeyboardInterrupt:
        pass
    finally:
        with open(Path(output_dir, season, "rating-cleaning-report.json"), "w") as outfile:
            json.dump(report, outfile, indent=4)
