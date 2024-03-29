"""Define CLI endpoints for cleaning data."""

from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import sys
from typing import Dict, List

import click

from ..endpoints.parameters import CURRENT_SEASON, SEASONS
from ..pipeline import gen_pipeline, run_pipeline
from ...utility import season_from_date

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

LOG = logging.getLogger(__name__)


@click.group()
def clean():
    """CLI group."""
    pass


@clean.command()
@click.option("--data-dir", help="Path to the directory containing the raw data.")
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
@click.option("--re-run", is_flag=True, help="Whether to re run a previous pipeline")
def model(data_dir, output_dir, season, re_run):
    """Clean model data."""
    calls: List[Dict] = []
    flow = gen_pipeline()
    if re_run:
        with open(
            Path(output_dir, season, "model-cleaning-report.json"), "r"
        ) as infile:
            alldates = json.load(infile)
        daterange = [
            datetime.strptime(row["GameDate"], "%m/%d/%Y")
            for row in alldates
            if row["reason"] == "Unknown"
        ]
    else:
        if season == CURRENT_SEASON:
            end_date = datetime.today() + timedelta(days=-1)
        else:
            end_date = SEASONS[season]["END"]
        timelist = list(
            range(int((end_date - SEASONS[season]["START"]).days) + 1)
        )
        daterange = [SEASONS[season]["START"] + timedelta(n) for n in timelist]
    for game_date in daterange:
        calls.append(
            {
                "flow": flow,
                "data_dir": str(Path(data_dir, season)),
                "output_dir": str(Path(output_dir, season)),
                "save_data": True,
                "mode": "model",
                "Season": season,
                "GameDate": game_date.strftime("%m/%d/%Y"),
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
                            "reason": "No games",
                        }
                    )
                elif (
                    scoreboard["GameHeader"]["GAME_ID"].str.startswith("003").sum() >= 1
                ):
                    report.append(
                        {
                            "GameDate": call["GameDate"],
                            "mode": call["mode"],
                            "reason": "All-star game",
                        }
                    )
                else:
                    report.append(
                        {
                            "GameDate": call["GameDate"],
                            "mode": call["mode"],
                            "reason": "Unknown",
                        }
                    )
    except KeyboardInterrupt:
        pass
    finally:
        with open(
            Path(output_dir, season, "model-cleaning-report.json"), "w"
        ) as outfile:
            json.dump(report, outfile, indent=4)


@clean.command()
@click.option("--data-dir", help="Path to the directory containing the raw data.")
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
@click.option("--re-run", is_flag=True, help="Whether to re run a previous pipeline")
def rating(data_dir, output_dir, season, re_run):
    """Clean the rating input data."""
    calls: List[Dict] = []
    flow = gen_pipeline()
    if re_run:
        with open(
            Path(output_dir, season, "rating-cleaning-report.json"), "r"
        ) as infile:
            alldates = json.load(infile)
        daterange = [
            datetime.strptime(row["GameDate"], "%m/%d/%Y")
            for row in alldates
            if row["reason"] == "Unknown"
        ]
    else:
        if season == CURRENT_SEASON:
            end_date = datetime.today() + timedelta(days=-1)
        else:
            end_date = SEASONS[season]["END"]
        timelist = list(
            range(int((end_date - SEASONS[season]["START"]).days) + 1)
        )
        daterange = [SEASONS[season]["START"] + timedelta(n) for n in timelist]
    for game_date in daterange:
        calls.append(
            {
                "flow": flow,
                "data_dir": str(Path(data_dir, season)),
                "output_dir": str(Path(output_dir, season)),
                "save_data": True,
                "mode": "rating",
                "Season": season,
                "GameDate": game_date.strftime("%m/%d/%Y"),
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
                            "reason": "No games",
                        }
                    )
                elif (
                    scoreboard["GameHeader"]["GAME_ID"].str.startswith("003").sum() >= 1
                ):
                    report.append(
                        {
                            "GameDate": call["GameDate"],
                            "mode": call["mode"],
                            "reason": "All-star game",
                        }
                    )
                else:
                    report.append(
                        {
                            "GameDate": call["GameDate"],
                            "mode": call["mode"],
                            "reason": "Unknown",
                        }
                    )
    except KeyboardInterrupt:
        pass
    finally:
        with open(
            Path(output_dir, season, "rating-cleaning-report.json"), "w"
        ) as outfile:
            json.dump(report, outfile, indent=4)


@clean.command()
@click.option("--data-dir", help="Path to the directory containing the raw data.")
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, default=None, help="The season to download")
@click.option("--game-date", type=click.DateTime(formats=["%Y-%m-%d"]))
def daily(data_dir, output_dir, season, game_date):
    """Clean model and rating data for a given day."""
    # If no season provided, get it from the game date
    if season is None:
        season = season_from_date(date=game_date)
    flow = gen_pipeline()
    output = run_pipeline(
        flow=flow,
        data_dir=str(Path(data_dir, season)),
        output_dir=str(Path(output_dir, season)),
        save_data=True,
        mode="model",
        Season=season,
        GameDate=game_date.strftime("%m/%d/%Y"),
    )
    if not output.is_successful():
        LOG.error("Unable to clean the model data")
    else:
        output = run_pipeline(
            flow=flow,
            data_dir=str(Path(data_dir, season)),
            output_dir=str(Path(output_dir, season)),
            save_data=True,
            mode="rating",
            Season=season,
            GameDate=game_date.strftime("%m/%d/%Y"),
        )
        if not output.is_successful():
            LOG.error("Unable to clean the rating data")
