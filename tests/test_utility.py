"""Test some utility functions."""

from datetime import datetime

import pytest

from nbaspa.utility import season_from_date

@pytest.mark.parametrize(
    "test_date,expected",
    [
        (datetime(year=2005, month=11, day=1), "2005-06"),
        (datetime(year=2005, month=12, day=10), "2005-06"),
        (datetime(year=2006, month=3, day=15), "2005-06")
    ]
)
def test_in_season_date(test_date, expected):
    """Test getting the season from a game date."""
    assert season_from_date(test_date) == expected

def test_out_of_season_error():
    """Test raising a value error when the date isn't in season."""
    with pytest.raises(ValueError):
        season_from_date(datetime(year=2019, month=7, day=15))
