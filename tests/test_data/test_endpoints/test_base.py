"""Test BaseRequest."""

import json
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from nbaspa.data.endpoints.base import BaseRequest

@patch("requests.Session.get")
def test_call_api(mock_sess):
    """Test calling from the API."""
    req = BaseRequest(GameID="00218DUMMY")
    req.get()

    mock_sess.assert_called_with(
        "https://stats.nba.com/stats/default",
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
        params={"GameID": "00218DUMMY"},
        timeout=(10, 15),
    )

@patch("requests.Session.get")
def test_persist_data(mock_sess, tmpdir):
    """Test persisting data."""
    location = tmpdir.mkdir("data")
    # Define some dummy request data
    dummy = {
        "resultSets": [{"headers": ["dummy_col"], "rowSet": []}]
    }
    mock_sess.return_value.json.return_value = dummy
    req = BaseRequest(GameID="00218DUMMY", output_dir=str(location))

    assert not req.exists()

    req.get()

    assert req._raw_data == dummy
    assert req.get_data().equals(pd.DataFrame(columns=["dummy_col"]))
    with pytest.raises(ValueError):
        req.get_data("second dataset")

    with open(Path(location, "default", "default.json")) as infile:
        assert req._raw_data == json.load(infile)
