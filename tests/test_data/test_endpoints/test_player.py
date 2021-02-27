"""Test player endpoints."""

from nbaspa.data.endpoints.player import (
    PlayerDashboardGeneral,
    PlayerDashboardShooting,
    AllPlayers,
)

def test_all_players(output_dir):
    """Test loading all players."""
    players = AllPlayers(Season="2018-19", output_dir=output_dir)
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
    players.get()

    for dataset in players.datasets:
        assert players.get_data(dataset).empty
