"""Create player ratings."""

import click

from ..pipeline import gen_pipeline, run_pipeline
from ...utility import season_from_date


@click.command()
@click.option("--data-dir", help="Path to the data directory.")
@click.option("--output-dir", help="Path to the output directory")
@click.option("--season", default=None, help="The season")
@click.option("--game-id", default=None, help="The Game ID")
@click.option("--game-date", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option(
    "--mode",
    type=click.Choice(["nba", "survival", "survival-plus"], case_sensitive=True),
    default="survival",
    help="Whether to generate NBA win probability or survival",
)
def rate(data_dir, output_dir, season, game_id, game_date, mode):
    """Create impact ratings."""
    if season is None:
        season = season_from_date(date=game_date)
    flow = gen_pipeline()
    run_pipeline(
        flow=flow,
        data_dir=data_dir,
        output_dir=output_dir,
        Season=season,
        GameID=game_id,
        mode=mode,
    )
