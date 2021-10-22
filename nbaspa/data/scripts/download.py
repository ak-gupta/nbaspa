"""Define CLI endpoints for downloading data."""

import datetime
import logging
from pathlib import Path
import sys
from typing import List

import click
import numpy as np
import pandas as pd

from ..endpoints import AllPlayers, Scoreboard
from ..endpoints.parameters import ParameterValues, SEASONS
from ..factory import NBADataFactory

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

LOG = logging.getLogger(__name__)

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
            ("TeamRoster", {"TeamID": team, "Season": season}),
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
        if int(row["TO_YEAR"]) >= 2005:
            calls.append(
                ("PlayerInfo", {"PlayerID": row["PERSON_ID"], "output_dir": output_dir})
            )
        if int(row["TO_YEAR"]) >= int(season[0:4]) and int(row["FROM_YEAR"]) <= int(
            season[0:4]
        ):
            calls += [
                (
                    "PlayerGameLog",
                    {"PlayerID": row["PERSON_ID"], "Season": season}
                ),
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

@download.command()
@click.option("--output-dir", help="Path to the output directory")
@click.option("--season", type=str, help="The season to download")
@click.option("--game-date", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option("--re-run", is_flag=True, help="Whether to overwrite existing data")
def daily(output_dir, season, game_date, re_run):
    """Download daily data."""
    # Add the scoreboard
    score = Scoreboard(
        output_dir=Path(output_dir, season),
        GameDate=game_date.strftime("%m/%d/%Y")
    )
    score.get()
    # Add calls for the game data
    df = score.get_data("GameHeader")
    gamecalls: List[str] = []
    LOG.info(f"Reading in the game data for all games on {game_date.strftime('%b %d, %Y')}")
    for _, row in df.iterrows():
        gamecalls += [
            ("PlayByPlay", {"GameID": row["GAME_ID"]}),
            ("ShotChart", {"GameID": row["GAME_ID"], "Season": season}),
            ("GameRotation", {"GameID": row["GAME_ID"]}),
            ("WinProbability", {"GameID": row["GAME_ID"]}),
            ("BoxScoreTraditional", {"GameID": row["GAME_ID"]}),
        ]
    game_factory = NBADataFactory(calls=gamecalls, output_dir=Path(output_dir, season))
    game_factory.get()
    # Refresh the team data
    teams = score.get_data("LineScore")["TEAM_ID"].values
    teamcalls: List[str] = []
    LOG.info("Refreshing team data")
    for team in teams:
        if not str(team).startswith("16"):
            continue

        teamcalls += [
            (
                "TeamLineups",
                {"TeamID": team, "Season": season, "MeasureType": "Advanced"},
            ),
            ("TeamGameLog", {"TeamID": team, "Season": season}),
            ("TeamRoster", {"TeamID": team, "Season": season}),
        ]
    team_factory = NBADataFactory(calls=teamcalls, output_dir=Path(output_dir, season))
    team_factory.get(overwrite=not re_run)
    # Refresh the player data
    boxloader = NBADataFactory(
        calls=[("BoxScoreTraditional", {"GameID": game}) for game in np.unique(df["GAME_ID"])],
        output_dir=Path(output_dir, season)
    )
    boxloader.load()
    playerstats = boxloader.get_data("PlayerStats")
    players = playerstats[~pd.isnull(playerstats["MIN"])]["PLAYER_ID"].values
    playercalls: List[str] = []
    LOG.info("Refreshing player data")
    for player in players:
        playercalls += [
            ("PlayerGameLog", {"PlayerID": player, "Season": season}),
            ("PlayerDashboardShooting", {"PlayerID": player, "Season": season}),
            ("PlayerDashboardGeneral", {"PlayerID": player, "Season": season}),
        ]
    
    info_factory = NBADataFactory(
        calls=[("PlayerInfo", {"PlayerID": player, "Season": season}) for player in players],
        output_dir=Path(output_dir, season)
    )
    info_factory.get()

    player_factory = NBADataFactory(calls=playercalls, output_dir=Path(output_dir, season))
    player_factory.get(overwrite=not re_run)
