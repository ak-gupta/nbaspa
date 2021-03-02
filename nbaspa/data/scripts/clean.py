"""Define CLI endpoints for cleaning data."""

import datetime
import json
import logging
from pathlib import Path
import sys
from typing import Dict, List

import click

from ..endpoints.parameters import SEASONS
from ..pipeline import gen_pipeline, run_pipeline

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


@click.group()
def clean():
    """CLI group."""
    pass


@clean.command()
@click.option("--data-dir", help="Path to the directory containing the raw data.")
@click.option("--output-dir", help="Path to the output directory.")
@click.option("--season", type=str, help="The season to download")
def model(data_dir, output_dir, season):
    """Clean model data."""
    calls: List[Dict] = []
    flow = gen_pipeline()
    for n in range(int((SEASONS[season]["END"] - SEASONS[season]["START"]).days) + 1):
        game_date = SEASONS[season]["START"] + datetime.timedelta(n)
        calls.append(
            {
                "flow": flow,
                "data_dir": Path(data_dir, season),
                "output_dir": Path(output_dir, season),
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
def rating(data_dir, output_dir, season):
    """Clean the rating input data."""
    calls: List[Dict] = []
    flow = gen_pipeline()
    for n in range(int((SEASONS[season]["END"] - SEASONS[season]["START"]).days) + 1):
        game_date = SEASONS[season]["START"] + datetime.timedelta(n)
        calls.append(
            {
                "flow": flow,
                "data_dir": Path(data_dir, season),
                "output_dir": Path(output_dir, season),
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
