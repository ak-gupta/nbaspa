"""Test player endpoints."""

from pathlib import Path

from nbaspa.data.endpoints.player import (
    PlayerDashboardGeneral,
    PlayerDashboardShooting,
    AllPlayers,
)

def test_all_players(output_dir):
    """Test loading all players."""
    players = AllPlayers(Season="2018-19", output_dir=output_dir)

    assert players.fpath == output_dir / Path("commonallplayers", "data_2018-19.json")
    assert players.exists()

    players.get()

    for dataset in players.datasets:
        assert players.get_data(dataset).empty

def test_load_general_dashboard(output_dir):
    """Test loading the general dashboard."""
    players = PlayerDashboardGeneral(
        PlayerID=1,
        Season="2018-19",
        output_dir=output_dir
    )

    assert players.fpath == output_dir / Path("playerdashboardbygeneralsplits", "data_1.json")
    assert players.exists()

    players.get()

    for dataset in players.datasets:
        assert players.get_data(dataset).empty

def test_load_shooting_dashboard(output_dir):
    """Test loading shooting dashboard."""
    players = PlayerDashboardShooting(
        PlayerID=1,
        Season="2018-19",
        output_dir=output_dir
    )

    assert players.fpath == output_dir / Path("playerdashboardbyshootingsplits", "data_1.json")
    assert players.exists()

    players.get()

    for dataset in players.datasets:
        assert players.get_data(dataset).empty
