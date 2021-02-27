"""Test loading lineup data."""

from nbaspa.data.endpoints import TeamLineups

def test_lineup(output_dir):
    """Test loading lineup data."""
    lineup = TeamLineups(
        TeamID=1610612761,
        Season="2018-19",
        output_dir=output_dir
    )
    lineup.get()

    for dataset in lineup.datasets:
        assert lineup.get_data(dataset).empty
