"""Test fitting an XGBoost model."""

from unittest.mock import patch

import numpy as np
import xgboost as xgb

from nbaspa.model.tasks import FitXGBoost, SurvivalData, SegmentData

@patch("xgboost.Booster")
@patch("xgboost.DMatrix")
@patch("xgboost.train")
def test_fit_xgboost(mock_train, mock_dmatrix, mock_boos, data):
    """Test fitting an XGBoost model."""
    pre = SurvivalData()
    df = pre.run(data)
    train = df.copy()
    train.loc[train["WIN"] == 0, "stop"] = -train["stop"]

    mock_train.return_value = mock_boos
    mock_boos.predict.return_value = np.zeros(len(df))

    tsk = FitXGBoost()
    _ = tsk.run(train_data=df)

    assert mock_dmatrix.call_count == 1
    assert mock_train.call_count == 1
    assert mock_boos.predict.call_count == 1

    args, kwargs = mock_dmatrix.call_args_list[0]

    assert args[0].equals(
        train[
            [
                "HOME_NET_RATING",
                "VISITOR_NET_RATING",
                "HOME_W_PCT",
                "VISITOR_W_PCT",
                "LAST_GAME_WIN",
                "HOME_GAMES_IN_LAST_3_DAYS",
                "HOME_GAMES_IN_LAST_5_DAYS",
                "HOME_GAMES_IN_LAST_7_DAYS",
                "VISITOR_GAMES_IN_LAST_3_DAYS",
                "VISITOR_GAMES_IN_LAST_5_DAYS",
                "VISITOR_GAMES_IN_LAST_7_DAYS",
                "SCOREMARGIN",
                "HOME_LINEUP_PLUS_MINUS",
                "VISITOR_LINEUP_PLUS_MINUS"
            ]
        ]
    )
    assert args[1].equals(train["stop"])

    args, kwargs = mock_train.call_args_list[0]

    assert args[0] == {"objective": "survival:cox", "seed": 42}
    assert args[1] == mock_dmatrix.return_value
    assert kwargs["evals"] == [(mock_dmatrix.return_value, "train")]

@patch("xgboost.Booster")
@patch("xgboost.DMatrix")
@patch("xgboost.train")
def test_fit_xgboost_stopping(mock_train, mock_dmatrix, mock_boos, data):
    """Test fitting an XGBoost model."""
    ranged = SurvivalData()
    df = ranged.run(data)
    segs = SegmentData()
    segdata = segs.run(data=df, splits=[0.8, 0.2], keys=["train", "stop"])
    train = segdata["train"].copy()
    train.loc[train["WIN"] == 0, "stop"] = -train["stop"]
    stop = segdata["stop"].copy()
    stop.loc[stop["WIN"] == 0, "stop"] = -stop["stop"]

    mock_train.return_value = mock_boos
    mock_boos.predict.return_value = np.zeros(len(train))

    tsk = FitXGBoost()
    _ = tsk.run(
        params={"learning_rate": 0.3},
        train_data=segdata["train"],
        stopping_data=segdata["stop"],
        early_stopping_rounds=10
    )

    assert mock_dmatrix.call_count == 2
    assert mock_train.call_count == 1
    assert mock_boos.predict.call_count == 1

    targs, _ = mock_dmatrix.call_args_list[0]

    assert targs[0].equals(
        train[
            [
                "HOME_NET_RATING",
                "VISITOR_NET_RATING",
                "HOME_W_PCT",
                "VISITOR_W_PCT",
                "LAST_GAME_WIN",
                "HOME_GAMES_IN_LAST_3_DAYS",
                "HOME_GAMES_IN_LAST_5_DAYS",
                "HOME_GAMES_IN_LAST_7_DAYS",
                "VISITOR_GAMES_IN_LAST_3_DAYS",
                "VISITOR_GAMES_IN_LAST_5_DAYS",
                "VISITOR_GAMES_IN_LAST_7_DAYS",
                "SCOREMARGIN",
                "HOME_LINEUP_PLUS_MINUS",
                "VISITOR_LINEUP_PLUS_MINUS"
            ]
        ]
    )
    assert targs[1].equals(train["stop"])

    sargs, _ = mock_dmatrix.call_args_list[1]

    assert sargs[0].equals(
        stop[
            [
                "HOME_NET_RATING",
                "VISITOR_NET_RATING",
                "HOME_W_PCT",
                "VISITOR_W_PCT",
                "LAST_GAME_WIN",
                "HOME_GAMES_IN_LAST_3_DAYS",
                "HOME_GAMES_IN_LAST_5_DAYS",
                "HOME_GAMES_IN_LAST_7_DAYS",
                "VISITOR_GAMES_IN_LAST_3_DAYS",
                "VISITOR_GAMES_IN_LAST_5_DAYS",
                "VISITOR_GAMES_IN_LAST_7_DAYS",
                "SCOREMARGIN",
                "HOME_LINEUP_PLUS_MINUS",
                "VISITOR_LINEUP_PLUS_MINUS"
            ]
        ]
    )
    assert sargs[1].equals(stop["stop"])

    args, kwargs = mock_train.call_args_list[0]

    assert args[0] == {"objective": "survival:cox", "seed": 42, "learning_rate": 0.3}
    assert args[1] == mock_dmatrix.return_value
    assert kwargs["evals"] == [
        (mock_dmatrix.return_value, "train"),
        (mock_dmatrix.return_value, "stopping")
    ]
