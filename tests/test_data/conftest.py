"""Define some fixtures."""

import json
from pathlib import Path

import pandas as pd
import pytest

CURR_DIR = Path(__file__).resolve().parent

@pytest.fixture
def pbp():
    """Dummy play-by-play data."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "playbyplayv2").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][0]["rowSet"],
                columns=rawdata["resultSets"][0]["headers"]
            )
        )
    
    return pd.concat(dfs).reset_index(drop=True)

@pytest.fixture
def header():
    """Dummy header data."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "scoreboardv2").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][0]["rowSet"],
                columns=rawdata["resultSets"][0]["headers"]
            )
        )
    
    return pd.concat(dfs).reset_index(drop=True)

@pytest.fixture
def last_meeting():
    """Dummy last meeting data."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "scoreboardv2").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][3]["rowSet"],
                columns=rawdata["resultSets"][3]["headers"]
            )
        )
    
    return pd.concat(dfs).reset_index(drop=True)

@pytest.fixture
def win_prob():
    """Dummy NBA win probability."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "winprobabilitypbp").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][0]["rowSet"],
                columns=rawdata["resultSets"][0]["headers"]
            )
        )
    
    return pd.concat(dfs).reset_index(drop=True)
