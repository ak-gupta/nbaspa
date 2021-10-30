"""Test the loader methods."""

from datetime import datetime
from pathlib import Path
from unittest.mock import call, patch

import pandas as pd

from nbaspa.data.tasks import (
    GenericLoader,
    PlayByPlayLoader,
    WinProbabilityLoader,
    GameLogLoader,
    LineupLoader,
    RotationLoader,
    ShotChartLoader,
    BoxScoreLoader,
    ShotZoneLoader,
    GeneralShootingLoader,
)

pd.options.display.max_columns = 35

def test_load_scoreboard(data_dir, header, last_meeting):
    """Test loading scoreboard data."""
    for game, gamedate in [
        ("00218DUMMY1", datetime(2018, 12, 25)),
        ("00218DUMMY2", datetime(2018, 12, 26))
    ]:
        loader = GenericLoader(loader="Scoreboard")
        output = loader.run(
            output_dir=data_dir / Path("2018-19"),
            GameDate=gamedate.strftime("%m/%d/%Y")
        )

        assert output["GameHeader"].equals(
            header[
                header["GAME_DATE_EST"] == gamedate.strftime("%Y-%m-%dT%H:%M:%S")
            ].reset_index(drop=True)
        )
        assert output["LastMeeting"].equals(
            last_meeting[last_meeting["GAME_ID"] == game].reset_index(drop=True)
        )

def test_load_pbp(data_dir, header, pbp):
    """Test loading play-by-play data."""
    loader = PlayByPlayLoader()
    output = loader.run(
        header=header,
        output_dir=data_dir / Path("2018-19")
    )
    output.sort_values(by=["GAME_ID", "EVENTNUM"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)

    assert output.equals(pbp)

def test_win_probability_loader(data_dir, header, win_prob):
    """Test loading NBA win probability data."""
    loader = WinProbabilityLoader()
    output = loader.run(
        header=header,
        output_dir=data_dir / Path("2018-19")
    )
    output.sort_values(by=["GAME_ID", "EVENT_NUM"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)
    
    assert output.equals(win_prob)

def test_gamelog_loader(data_dir, gamelog):
    """Test loading gamelogs."""
    loader = GameLogLoader()
    output = loader.run(
        season="2018-19",
        output_dir=data_dir / Path("2018-19")
    )
    output.sort_values(by=["Team_ID", "GAME_DATE"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)
    
    assert output.equals(gamelog)

@patch("nbaspa.data.tasks.io.NBADataFactory")
def test_lineup_loader(mock_factory, linescore):
    """Test loading lineup stats."""
    loader = LineupLoader()
    _ = loader.run(
        season="2018-19",
        GameDate="12/25/2018",
        linescore=linescore
    )

    mock_factory.assert_called_with(
        calls=[
            (
                "TeamLineups",
                {
                    "TeamID": 1610612760,
                    "Season": "2018-19",
                    "MeasureType": "Advanced",
                    "DateFrom": "10/16/2018",
                    "DateTo": "12/24/2018"
                }
            ),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612761,
                    "Season": "2018-19",
                    "MeasureType": "Advanced",
                    "DateFrom": "10/16/2018",
                    "DateTo": "12/24/2018"
                }
            )
        ]
    )
    assert mock_factory.return_value.get.call_count == 1

def test_rotation_loader(data_dir, header, homerotation, awayrotation):
    """Test loading the rotation data."""
    loader = RotationLoader()
    output = loader.run(
        header=header,
        output_dir=data_dir / Path("2018-19"),
    )
    output["AwayTeam"].sort_values(
        by=["GAME_ID", "PERSON_ID"], ascending=True, inplace=True
    )
    output["AwayTeam"].reset_index(drop=True, inplace=True)
    output["HomeTeam"].sort_values(
        by=["GAME_ID", "PERSON_ID"], ascending=True, inplace=True
    )
    output["HomeTeam"].reset_index(drop=True, inplace=True)

    assert output["AwayTeam"].equals(awayrotation)
    assert output["HomeTeam"].equals(homerotation)

def test_shotchart_loader(data_dir, header, shotchart):
    """Test loading the shotchart data."""
    loader = ShotChartLoader()
    output = loader.run(
        header=header,
        season="2018-19",
        output_dir=data_dir / Path("2018-19")
    )
    assert output.sort_values(by=["GAME_ID", "GAME_EVENT_ID"], ascending=True).equals(
        shotchart.sort_values(by=["GAME_ID", "GAME_EVENT_ID"], ascending=True)
    )

def test_boxscore_loader(data_dir, header, boxscore):
    """Test loading boxscore data."""
    loader = BoxScoreLoader()
    output = loader.run(
        header=header,
        output_dir=data_dir / Path("2018-19")
    )
    output.sort_values(by=["GAME_ID", "PLAYER_ID"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)

    assert output.equals(boxscore)

@patch("nbaspa.data.tasks.io.NBADataFactory")
def test_shotzone_loader(mock_factory, data_dir, boxscore, playergamelog, shotchart):
    """Test loading shotzone data."""
    # Only test one game of data since we have repeated games
    loader = ShotZoneLoader()
    mock_factory.return_value.get_data.side_effect = [playergamelog, shotchart]
    _ = loader.run(
        season="2018-19",
        GameDate="12/25/2018",
        boxscore=boxscore[boxscore["GAME_ID"] == "00218DUMMY1"],
        output_dir=data_dir / Path("2018-19")
    )

    assert mock_factory.call_count == 2
    assert mock_factory.return_value.load.call_count == 2
    assert mock_factory.return_value.get_data.call_count == 2
    mock_factory.assert_has_calls(
        [
            call(
                calls=[
                    (
                        "PlayerGameLog",
                        {
                            "PlayerID": i,
                            "Season": "2018-19"
                        }
                    )
                    for i in range(1, 13)
                ],
                output_dir=data_dir / "2018-19",
                filesystem="file"
            ),
            call().load(),
            call().get_data(),
            call(
                calls=[
                    (
                        "ShotChart", {"GameID": "00218DUMMY0", "Season": "2018-19"}
                    )
                ],
                output_dir=data_dir / "2018-19",
                filesystem="file"
            ),
            call().load(),
            call().get_data()
        ]
    )

def test_overall_shooting_loader(data_dir, boxscore, overallshooting):
    """Test loading overall shooting data."""
    loader = GeneralShootingLoader()
    output = loader.run(
        season="2018-19",
        boxscore=boxscore[boxscore["GAME_ID"] == "00218DUMMY1"],
        output_dir=data_dir / Path("2018-19")
    )
    assert output.equals(overallshooting)
