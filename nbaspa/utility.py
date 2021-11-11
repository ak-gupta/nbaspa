"""Utility functions."""

from datetime import datetime

from .data.endpoints.parameters import SEASONS


def season_from_date(date: datetime) -> str:
    """Get the season from the date.

    Parameters
    ----------
    date : datetime
        The date.

    Returns
    -------
    str
        The season string.
    """
    for season, cfg in SEASONS.items():
        if date >= cfg["START"] and date <= cfg["END"]:
            out = season
            break
    else:
        raise ValueError(
            f"Unable to find the season associated with {date.strftime('%Y-%m-%d')}"
        )

    return out
