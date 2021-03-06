"""Test visualization methods."""

from unittest.mock import patch, PropertyMock

from hyperopt import Trials
import pandas as pd

from nbaspa.model.tasks import PlotProbability, PlotMetric, PlotTuning

@patch("seaborn.scatterplot", autospec=True)
def test_plot_proba(mock_sns, data):
    """Test plotting probability."""
    tsk = PlotProbability()
    tsk.run(data=data, mode="benchmark")

    _, kwargs = mock_sns.call_args_list[0]

    assert kwargs["x"] == "SCOREMARGIN"
    assert kwargs["y"] == "NBA_WIN_PROB"
    assert kwargs["hue"] == "WIN"
    assert kwargs["data"].equals(data)
    assert kwargs["legend"]

@patch("seaborn.lineplot", autospec=True)
def test_plot_metric(mock_sns):
    """Test plotting a metric."""
    tsk = PlotMetric()
    tsk.run(
        times=[0, 10, 20],
        metric="Best Metric",
        lifelines=[0.5, 0.6, 0.7],
        xgboost=[0.6, 0.7, 0.8]
    )
    _, kwargs = mock_sns.call_args_list[0]

    df = pd.DataFrame(
        {
            "time": [0, 10, 20, 0, 10, 20],
            "value": [0.5, 0.6, 0.7, 0.6, 0.7, 0.8],
            "model": ["lifelines", "lifelines", "lifelines", "xgboost", "xgboost", "xgboost"]
        }
    )

    assert kwargs["x"] == "time"
    assert kwargs["y"] == "value"
    assert kwargs["hue"] == "model"
    assert kwargs["data"].equals(df)

@patch("seaborn.scatterplot", autospec=True)
def test_plot_tuning(mock_sns):
    """Test plotting tuning."""
    with patch("hyperopt.Trials.trials", new_callable=PropertyMock) as mock_trials:
        mock_trials.return_value = [
            {
                "tid": 0,
                "result": {"loss": 1.0},
                "misc": {
                    "vals": {
                        "param1": [0.0],
                        "param2": [0.5],
                        "param3": [0.6],
                        "param4": [0.7]
                    }
                }
            },
            {
                "tid": 1,
                "result": {"loss": 0.5},
                "misc": {
                    "vals": {
                        "param1": [0.1],
                        "param2": [0.2],
                        "param3": [0.4],
                        "param4": [0.0]
                    }
                }
            }
        ]

        trials = Trials()
        tsk = PlotTuning()
        tsk.run(trials=trials)
    
    df = pd.DataFrame(
        {
            "trial": [0, 1],
            "loss": [1.0, 0.5],
            "param1": [0.0, 0.1],
            "param2": [0.5, 0.2],
            "param3": [0.6, 0.4],
            "param4": [0.7, 0.0],
            "best": [False, True]
        }
    )

    assert len(mock_sns.call_args_list) == 5

    # Check each call
    _, kwargs = mock_sns.call_args_list[0]

    assert kwargs["x"] == "trial"
    assert kwargs["y"] == "loss"
    assert kwargs["hue"] == "best"
    assert not kwargs["legend"]
    assert kwargs["data"][
        ["trial", "best", "loss", "param1", "param2", "param3", "param4"]
    ].equals(
        df[["trial", "best", "loss", "param1", "param2", "param3", "param4"]]
    )

    _, kwargs = mock_sns.call_args_list[1]

    assert kwargs["y"] == "loss"
    assert not kwargs["legend"]
    assert kwargs["data"][
        ["trial", "best", "loss", "param1", "param2", "param3", "param4"]
    ].equals(
        df[["trial", "best", "loss", "param1", "param2", "param3", "param4"]]
    )
