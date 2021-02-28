"""Test the NBADataFactory."""

import datetime
from unittest.mock import call, patch

from nbaspa.data.endpoints import BoxScoreTraditional
from nbaspa.data.factory import NBADataFactory

def test_initialize():
    """Test initializing the factory."""
    calls = [
        ("BoxScoreTraditional", {"GameID": "00218DUMMY1"}),
        ("BoxScoreTraditional", {"GameID": "00218DUMMY2"})
    ]
    factory = NBADataFactory(calls=calls)

    assert isinstance(factory.calls[0], BoxScoreTraditional)
    assert factory.calls[0].params == {
        "GameID": "00218DUMMY1",
        "StartPeriod": 0,
        "EndPeriod": 0,
        "StartRange": 0,
        "EndRange": 0,
        "RangeType": 0
    }
    assert isinstance(factory.calls[1], BoxScoreTraditional)
    assert factory.calls[1].params == {
        "GameID": "00218DUMMY2",
        "StartPeriod": 0,
        "EndPeriod": 0,
        "StartRange": 0,
        "EndRange": 0,
        "RangeType": 0
    }

@patch("requests.Session.get")
def test_get(mock_sess):
    """Test running the get method."""
    calls = [
        ("BoxScoreTraditional", {"GameID": "00218DUMMY1"}),
        ("BoxScoreTraditional", {"GameID": "00218DUMMY2"})
    ]
    factory = NBADataFactory(calls=calls)
    start = datetime.datetime.now()
    factory.get()
    end = datetime.datetime.now()

    assert (end - start).seconds >= 55

    mock_sess.assert_has_calls(
        [
            call(
                "https://stats.nba.com/stats/boxscoretraditionalv2",
                headers={
                    "Host": "stats.nba.com",
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"
                    ),
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": "https://stats.nba.com/",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "x-nba-stats-origin": "stats",
                    "x-nba-stats-token": "true",
                },
                params={
                    "StartPeriod": 0,
                    "EndPeriod": 0,
                    "StartRange": 0,
                    "EndRange": 0,
                    "RangeType": 0,
                    "GameID": "00218DUMMY1",
                },
                timeout=(10, 15),
            ),
            call().raise_for_status(),
            call().json(),
            call(
                "https://stats.nba.com/stats/boxscoretraditionalv2",
                headers={
                    "Host": "stats.nba.com",
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"
                    ),
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": "https://stats.nba.com/",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "x-nba-stats-origin": "stats",
                    "x-nba-stats-token": "true",
                },
                params={
                    "StartPeriod": 0,
                    "EndPeriod": 0,
                    "StartRange": 0,
                    "EndRange": 0,
                    "RangeType": 0,
                    "GameID": "00218DUMMY2",
                },
                timeout=(10, 15),
            ),
            call().raise_for_status(),
            call().json()
        ]
    )

@patch("nbaspa.data.endpoints.BoxScoreTraditional")
def test_load_data_factory(mock_bs):
    """Test loading data through the factory."""
    calls = [
        ("BoxScoreTraditional", {"GameID": "00218DUMMY1"}),
        ("BoxScoreTraditional", {"GameID": "00218DUMMY2"})
    ]
    factory = NBADataFactory(calls=calls, output_dir="dummy")
    factory.load()

    assert mock_bs.return_value.load.call_count == 2

@patch("pandas.concat")
@patch("nbaspa.data.endpoints.BoxScoreTraditional")
def test_get_data_factory(mock_bs, mock_concat):
    """Test get data through the factory."""
    calls = [
        ("BoxScoreTraditional", {"GameID": "00218DUMMY1"}),
        ("BoxScoreTraditional", {"GameID": "00218DUMMY2"})
    ]
    factory = NBADataFactory(calls=calls, output_dir="dummy")
    factory.get_data()

    assert mock_bs.return_value.get_data.call_count == 2
    assert mock_concat.call_count == 1
