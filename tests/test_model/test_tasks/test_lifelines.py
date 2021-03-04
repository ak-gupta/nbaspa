"""Test the lifelines model methods."""

from unittest.mock import patch

from lifelines import CoxTimeVaryingFitter

from nbaspa.model.tasks import (
    InitializeLifelines,
    FitLifelinesModel,
    SurvivalData
)

def test_initialize_lifelines():
    """Test initializing a lifelines model."""
    tsk = InitializeLifelines()
    output = tsk.run()

    assert isinstance(output, CoxTimeVaryingFitter)

@patch("lifelines.CoxTimeVaryingFitter", autospec=True)
def test_fit_lifelines(mock_ll, data):
    """Test fitting a lifelines model."""
    pre = SurvivalData()
    df = pre.run(data)

    model = mock_ll.return_value
    tsk = FitLifelinesModel()
    _ = tsk.run(model=model, data=df)

    assert model.fit.call_count == 1
    
    args, kwargs = model.fit.call_args_list[0]

    assert args[0].equals(
        df[
            [
                "GAME_ID",
                "WIN",
                "start",
                "stop",
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
    assert kwargs["id_col"] == "GAME_ID"
    assert kwargs["event_col"] == "WIN"
    assert kwargs["start_col"] == "start"
    assert kwargs["stop_col"] == "stop"
