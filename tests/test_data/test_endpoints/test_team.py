"""Test loading team data."""

from nbaspa.data.endpoints import TeamGameLog, TeamStats

def test_team_stats(output_dir):
    """Test loading team statistics."""
    team = TeamStats(Season="2018-19", output_dir=output_dir)
    team.get()

    for dataset in team.datasets:
        assert team.get_data(dataset).empty

def test_gamelog(output_dir):
    """Test loading gamelog."""
    gamelog = TeamGameLog(TeamID=1610612761, Season="2018-19", output_dir=output_dir)
    gamelog.get()

    for dataset in gamelog.datasets:
        assert gamelog.get_data(dataset).empty
