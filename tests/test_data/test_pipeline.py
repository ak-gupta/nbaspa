"""Test the data cleaning pipeline."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from nbaspa.data.pipeline import gen_pipeline, run_pipeline

@pytest.fixture
def modeldata():
    """Define the output model data."""
    real = pd.DataFrame(
        {
            "GAME_ID": "00218DUMMY1",
            "PCTIMESTRING": ["12:00", "11:50", "11:40"],
            "PERIOD": 1,
            "EVENTNUM": [3, 4, 6],
            "EVENTMSGTYPE": [9, 3, 8],
            "HOMEDESCRIPTION": None,
            "VISITORDESCRIPTION": [None, "FREE THROW MADE", "VISITOR SUBSTITUTION"],
            "PLAYER1_ID": [np.nan, 7, 9],
            "PLAYER2_ID": [np.nan, np.nan, 12],
            "SCOREMARGIN": [0, -1, -1],
            "TIME": [0, 10, 20],
            "NBA_WIN_PROB": [0.51, 0.48, 0.49],
            "NBA_WIN_PROB_CHANGE": [0.0, -0.03, 0.01],
            "WIN": 0,
            "GAME_DATE_EST": "2018-12-25",
            "HOME_TEAM_ID": 1610612761,
            "VISITOR_TEAM_ID": 1610612760,
            "HOME_NET_RATING": -3.5,
            "HOME_OFF_RATING": 110.5,
            "VISITOR_NET_RATING": 6.5,
            "VISITOR_OFF_RATING": 120.5,
            "LAST_GAME_WIN": 0,
            "HOME_W_PCT": 1.0,
            "VISITOR_W_PCT": 0.0,
            "HOME_GAMES_IN_LAST_3_DAYS": 1.0,
            "VISITOR_GAMES_IN_LAST_3_DAYS": 0.0,
            "HOME_GAMES_IN_LAST_5_DAYS": 1.0,
            "VISITOR_GAMES_IN_LAST_5_DAYS": 1.0,
            "HOME_GAMES_IN_LAST_7_DAYS": 1.0,
            "VISITOR_GAMES_IN_LAST_7_DAYS": 1.0,
            "HOME_LINEUP": [
                "1-2-3-4-5",
                "1-2-3-4-5",
                "1-2-3-4-6"
            ],
            "HOME_LINEUP_PLUS_MINUS": [4.5, 4.5, 6.0],
            "VISITOR_LINEUP": [
                "10-11-7-8-9",
                "10-11-7-8-9",
                "10-11-12-7-8"
            ],
            "VISITOR_LINEUP_PLUS_MINUS": [1.5, 1.5, 6.5],
        },
        index=[1, 2, 4]
    )
    real["GAME_DATE_EST"] = pd.to_datetime(real["GAME_DATE_EST"])

    return real

@pytest.fixture
def ratingdata():
    """Define the output rating data."""
    real = pd.DataFrame(
        {
            "GAME_ID": "00218DUMMY1",
            "PCTIMESTRING": ["12:00", "12:00", "11:50", "11:40", "11:40"],
            "PERIOD": 1,
            "EVENTNUM": [2, 3, 4, 5, 6],
            "EVENTMSGTYPE": [12, 9, 3, 8, 8],
            "HOMEDESCRIPTION": [None, None, None, "HOME SUBSTITUTION", None],
            "VISITORDESCRIPTION": [None, None, "FREE THROW MADE", None, "VISITOR SUBSTITUTION"],
            "PLAYER1_ID": [np.nan, np.nan, 7, 5, 9],
            "PLAYER2_ID": [np.nan, np.nan, np.nan, 6, 12],
            "SCOREMARGIN": [0, 0, -1, -1, -1],
            "TIME": [0, 0, 10, 20, 20],
            "NBA_WIN_PROB": [0.51, 0.51, 0.48, 0.49, 0.49],
            "NBA_WIN_PROB_CHANGE": [0.0, 0.0, -0.03, 0.01, 0.01],
            "WIN": 0,
            "GAME_DATE_EST": "2018-12-25",
            "HOME_TEAM_ID": 1610612761,
            "VISITOR_TEAM_ID": 1610612760,
            "HOME_NET_RATING": -3.5,
            "HOME_OFF_RATING": 110.5,
            "VISITOR_NET_RATING": 6.5,
            "VISITOR_OFF_RATING": 120.5,
            "SHOT_ZONE_BASIC": None,
            "SHOT_VALUE": [np.nan, np.nan, 0.85, np.nan, np.nan],
            "FG_PCT": [np.nan, np.nan, 0.85, np.nan, np.nan]
        },
    )
    real["GAME_DATE_EST"] = pd.to_datetime(real["GAME_DATE_EST"])

    return real

def test_model_cleaning_pipeline_nosave(data_dir, modeldata):
    """Test model cleaning pipeline."""
    flow = gen_pipeline()
    output = run_pipeline(
        flow=flow,
        data_dir=str(data_dir / "2018-19"),
        output_dir=str(data_dir / "2018-19"),
        save_data=False,
        mode="model",
        Season="2018-19",
        GameDate="12/25/2018"
    )
    output_df = output.result[flow.get_tasks(name="Merge")[0]].result
    output_df["NBA_WIN_PROB_CHANGE"] = np.round(output_df["NBA_WIN_PROB_CHANGE"], 3)

    assert output_df.equals(modeldata)

def test_model_cleaning_pipeline_save(data_dir, modeldata, tmpdir):
    """Test persisting model save data."""
    location = tmpdir.mkdir("data")
    flow = gen_pipeline()
    run_pipeline(
        flow=flow,
        data_dir=str(data_dir / "2018-19"),
        output_dir=str(location),
        save_data=True,
        mode="model",
        Season="2018-19",
        GameDate="12/25/2018"
    )
    df = pd.read_csv(
        Path(str(location), "model-data", "data_00218DUMMY1.csv"),
        sep="|",
        index_col=0,
        dtype={
            "GAME_ID": str,
            "HOMEDESCRIPTION": str,
            "VISITORDESCRIPTION": str
        }
    )
    df["GAME_DATE_EST"] = pd.to_datetime(df["GAME_DATE_EST"])

    assert df.equals(modeldata)

def test_rating_data_pipeline_nosave(data_dir, ratingdata):
    """Test creating clean rating data."""
    flow = gen_pipeline()
    output = run_pipeline(
        flow=flow,
        data_dir=str(data_dir / "2018-19"),
        output_dir=str(data_dir / "2018-19"),
        save_data=False,
        mode="rating",
        Season="2018-19",
        GameDate="12/25/2018"
    )
    output_df = output.result[flow.get_tasks(name="Merge")[0]].result
    output_df["NBA_WIN_PROB_CHANGE"] = np.round(output_df["NBA_WIN_PROB_CHANGE"], 3)

    assert output_df.equals(ratingdata)

def test_rating_data_pipeline_save(data_dir, ratingdata, tmpdir):
    """Test persisting rating data."""
    location = tmpdir.mkdir("rating-data")
    flow = gen_pipeline()
    run_pipeline(
        flow=flow,
        data_dir=str(data_dir / "2018-19"),
        output_dir=str(location),
        save_data=True,
        mode="rating",
        Season="2018-19",
        GameDate="12/25/2018"
    )
    df = pd.read_csv(
        Path(str(location), "rating-data", "data_00218DUMMY1.csv"),
        sep="|",
        index_col=0,
        dtype={
            "GAME_ID": str,
            "HOMEDESCRIPTION": str,
            "VISITORDESCRIPTION": str,
            "SHOT_ZONE_BASIC": str
        }
    )
    df["GAME_DATE_EST"] = pd.to_datetime(df["GAME_DATE_EST"])

    assert df.equals(ratingdata)
