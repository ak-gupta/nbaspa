"""Define some fixtures."""

import json
from pathlib import Path

import pandas as pd
import pytest

CURR_DIR = Path(__file__).resolve().parent

@pytest.fixture
def data_dir():
    """Data directory."""
    return CURR_DIR / Path("data")

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
        dfs[-1]["PLAYER1_ID"] = dfs[-1]["PLAYER1_ID"].astype(float)
        dfs[-1]["PLAYER2_ID"] = dfs[-1]["PLAYER2_ID"].astype(float)
    
    out = pd.concat(dfs)
    out.sort_values(by=["GAME_ID", "EVENTNUM"], ascending=True, inplace=True)
    out.reset_index(drop=True, inplace=True)
    
    return out

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
    
    out = pd.concat(dfs)
    out.sort_values(by=["GAME_ID", "EVENT_NUM"], ascending=True, inplace=True)
    out.reset_index(drop=True, inplace=True)
    
    return out

@pytest.fixture
def gamelog():
    """Dummy gamelog data."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "teamgamelog").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][0]["rowSet"],
                columns=rawdata["resultSets"][0]["headers"]
            )
        )
    
    out = pd.concat(dfs)
    out.sort_values(by=["Team_ID", "GAME_DATE"], ascending=True, inplace=True)
    out.reset_index(drop=True, inplace=True)
    
    return out

@pytest.fixture
def stats():
    """Dummy team stats."""
    with open(Path(CURR_DIR, "data", "2018-19", "teamestimatedmetrics", "data_2018-19.json")) as infile:
        rawdata = json.load(infile)
    
    return pd.DataFrame(
        rawdata["resultSet"]["rowSet"],
        columns=rawdata["resultSet"]["headers"]
    )

@pytest.fixture
def shotchart():
    """Dummy shotchart."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "shotchartdetail").glob("data_*.json"):
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
def boxscore():
    """Dummy boxscore."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "boxscoretraditionalv2").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][0]["rowSet"],
                columns=rawdata["resultSets"][0]["headers"]
            )
        )
    
    out = pd.concat(dfs)
    out.sort_values(by=["GAME_ID", "PLAYER_ID"], ascending=True, inplace=True)
    out.reset_index(drop=True, inplace=True)
    
    return out

@pytest.fixture
def shotzonedashboard():
    """Dummy shooting dashboard."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "playerdashboardbyshootingsplits").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][3]["rowSet"],
                columns=rawdata["resultSets"][3]["headers"]
            )
        )
        pid = str(fpath).split("data_")[-1].split(".json")[0]
        dfs[-1]["PLAYER_ID"] = int(pid)
    
    return pd.concat(dfs).reset_index(drop=True)

@pytest.fixture
def overallshooting():
    """Dummy general shooting dashboard."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "playerdashboardbygeneralsplits").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][0]["rowSet"],
                columns=rawdata["resultSets"][0]["headers"]
            )
        )
        pid = str(fpath).split("data_")[-1].split(".json")[0]
        dfs[-1]["PLAYER_ID"] = int(pid)
    
    return pd.concat(dfs).reset_index(drop=True)

@pytest.fixture
def homerotation():
    """Dummy home team rotation data."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "gamerotation").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][1]["rowSet"],
                columns=rawdata["resultSets"][1]["headers"]
            )
        )
    
    out = pd.concat(dfs)
    out.sort_values(by=["GAME_ID", "PERSON_ID"], ascending=True, inplace=True)
    out.reset_index(drop=True, inplace=True)
    
    return out

@pytest.fixture
def awayrotation():
    """Dummy away rotation data."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "gamerotation").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][0]["rowSet"],
                columns=rawdata["resultSets"][0]["headers"]
            )
        )
    
    out = pd.concat(dfs)
    out.sort_values(by=["GAME_ID", "PERSON_ID"], ascending=True, inplace=True)
    out.reset_index(drop=True, inplace=True)
    
    return out

@pytest.fixture
def lineup_stats():
    """Dummy lineup stats."""
    dfs = []
    for fpath in Path(CURR_DIR, "data", "2018-19", "teamdashlineups").glob("data_*.json"):
        with open(fpath) as infile:
            rawdata = json.load(infile)
        dfs.append(
            pd.DataFrame(
                rawdata["resultSets"][1]["rowSet"],
                columns=rawdata["resultSets"][1]["headers"]
            )
        )
    
    out = pd.concat(dfs)
    out.sort_values(by=["GROUP_ID"], ascending=True, inplace=True)
    out.reset_index(drop=True, inplace=True)
    
    return out
