"""Test the CLI for data download and cleaning."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from nbaspa.data.endpoints.parameters import SEASONS
from nbaspa.data.scripts.clean import model, rating
from nbaspa.data.scripts.download import scoreboard, games, teams, players

def test_model_cli(data_dir, tmpdir):
    """Test running the model data cleaning pipeline."""
    location = tmpdir.mkdir("model-data")
    runner = CliRunner()
    with patch.dict(
        SEASONS,
        {
            "2018-19": {
                "START": datetime(2018, 12, 25),
                "END": datetime(2018, 12, 26)
            }
        }
    ):
        result = runner.invoke(
            model,
            [
                f"--data-dir={str(data_dir)}",
                f"--output-dir={str(location)}",
                "--season=2018-19"
            ]
        )
    assert result.exit_code == 0
    assert Path(
        str(location),
        "2018-19",
        "model-data",
        "data_00218DUMMY1.csv"
    ).is_file()
    assert Path(
        str(location),
        "2018-19",
        "model-data",
        "data_00218DUMMY2.csv"
    ).is_file()

def test_rating_cli(data_dir, tmpdir):
    """Test running the rating data cleaning pipeline."""
    location = tmpdir.mkdir("rating-data")
    runner = CliRunner()
    with patch.dict(
        SEASONS,
        {
            "2018-19": {
                "START": datetime(2018, 12, 25),
                "END": datetime(2018, 12, 26)
            }
        }
    ):
        result = runner.invoke(
            rating,
            [
                f"--data-dir={str(data_dir)}",
                f"--output-dir={str(location)}",
                "--season=2018-19"
            ]
        )
    
    assert result.exit_code == 0
    assert Path(
        str(location),
        "2018-19",
        "rating-data",
        "data_00218DUMMY1.csv"
    ).is_file()
    assert Path(
        str(location),
        "2018-19",
        "rating-data",
        "data_00218DUMMY2.csv"
    ).is_file()

@patch("nbaspa.data.scripts.download.NBADataFactory")
def test_scoreboard_cli(mock_factory, tmpdir):
    """Test running the CLI for downloading scoreboard data."""
    location = tmpdir.mkdir("rating-data")
    runner = CliRunner()
    with patch.dict(
        SEASONS,
        {
            "2018-19": {
                "START": datetime(2018, 12, 25),
                "END": datetime(2018, 12, 26)
            }
        }
    ):
        result = runner.invoke(
            scoreboard, [f"--output-dir={str(location)}", "--season=2018-19"]
        )

    mock_factory.assert_called_with(
        calls=[
            ("Scoreboard", {"GameDate": "12/25/2018"}),
            ("Scoreboard", {"GameDate": "12/26/2018"})
        ],
        output_dir=Path(str(location), "2018-19")
    )
    mock_factory.return_value.get.call_count == 1
    
    assert result.exit_code == 0

@patch("nbaspa.data.scripts.download.NBADataFactory")
def test_games_cli(mock_factory, data_dir):
    """Test running the CLI for downloading games."""
    runner = CliRunner()
    with patch.dict(
        SEASONS,
        {
            "2018-19": {
                "START": datetime(2018, 12, 25),
                "END": datetime(2018, 12, 26)
            }
        }
    ):
        result = runner.invoke(
            games, [f"--output-dir={str(data_dir)}", "--season=2018-19"]
        )
    
    mock_factory.assert_called_with(
        calls=[
            ("PlayByPlay", {"GameID": "00218DUMMY1"}),
            ("ShotChart", {"GameID": "00218DUMMY1", "Season": "2018-19"}),
            ("GameRotation", {"GameID": "00218DUMMY1"}),
            ("WinProbability", {"GameID": "00218DUMMY1"}),
            ("BoxScoreTraditional", {"GameID": "00218DUMMY1"}),
            ("PlayByPlay", {"GameID": "00218DUMMY2"}),
            ("ShotChart", {"GameID": "00218DUMMY2", "Season": "2018-19"}),
            ("GameRotation", {"GameID": "00218DUMMY2"}),
            ("WinProbability", {"GameID": "00218DUMMY2"}),
            ("BoxScoreTraditional", {"GameID": "00218DUMMY2"}),
        ],
        output_dir=Path(data_dir, "2018-19")
    )
    mock_factory.return_value.get.call_count == 1

    assert result.exit_code == 0

@patch("nbaspa.data.scripts.download.NBADataFactory")
def test_teams_cli(mock_factory, data_dir):
    """Test running the CLI for downloading teams data."""
    runner = CliRunner()
    result = runner.invoke(
        teams, [f"--output-dir={str(data_dir)}", "--season=2018-19"]
    )

    mock_factory.assert_called_with(
        calls=[
            ("TeamStats", {"Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612737,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612737, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612737, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612738,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612738, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612738, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612739,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612739, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612739, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612740,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612740, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612740, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612741,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612741, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612741, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612742,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612742, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612742, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612743,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612743, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612743, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612744,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612744, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612744, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612745,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612745, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612745, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612746,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612746, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612746, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612747,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612747, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612747, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612748,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612748, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612748, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612749,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612749, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612749, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612750,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612750, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612750, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612751,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612751, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612751, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612752,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612752, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612752, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612753,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612753, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612753, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612754,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612754, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612754, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612755,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612755, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612755, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612756,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612756, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612756, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612757,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612757, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612757, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612758,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612758, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612758, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612759,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612759, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612759, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612760,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612760, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612760, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612761,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612761, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612761, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612762,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612762, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612762, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612763,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612763, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612763, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612764,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612764, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612764, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612765,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612765, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612765, "Season": "2018-19"}),
            (
                "TeamLineups",
                {
                    "TeamID": 1610612766,
                    "Season": "2018-19",
                    "MeasureType": "Advanced"
                }
            ),
            ("TeamGameLog", {"TeamID": 1610612766, "Season": "2018-19"}),
            ("TeamRoster", {"TeamID": 1610612766, "Season": "2018-19"}),
        ],
        output_dir=Path(data_dir, "2018-19")
    )
    mock_factory.return_value.get.call_count == 1
    
    assert result.exit_code == 0

@patch("nbaspa.data.scripts.download.NBADataFactory")
def test_players_cli(mock_factory, data_dir):
    """Test running the CLI for downloading player data."""
    runner = CliRunner()
    result = runner.invoke(
        players, [f"--output-dir={str(data_dir)}", "--season=2018-19"]
    )
    
    mock_factory.assert_called_with(
        calls=[
            ("PlayerInfo", {"PlayerID": 1, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 1, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 1, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 1, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 2, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 2, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 2, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 2, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 3, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 3, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 3, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 3, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 4, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 4, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 4, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 4, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 5, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 5, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 5, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 5, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 6, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 6, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 6, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 6, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 7, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 7, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 7, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 7, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 8, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 8, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 8, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 8, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 9, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 9, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 9, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 9, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 10, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 10, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 10, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 10, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 11, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 11, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 11, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 11, "Season": "2018-19"}),
            ("PlayerInfo", {"PlayerID": 12, "output_dir": str(data_dir)}),
            ("PlayerGameLog", {"PlayerID": 12, "Season": "2018-19"}),
            ("PlayerDashboardShooting", {"PlayerID": 12, "Season": "2018-19"}),
            ("PlayerDashboardGeneral", {"PlayerID": 12, "Season": "2018-19"}),
        ],
        output_dir=Path(data_dir, "2018-19")
    )
    mock_factory.return_value.get.call_count == 1

    assert result.exit_code == 0
