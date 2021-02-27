"""Test scoreboard endpoint."""

from nbaspa.data.endpoints import Scoreboard

def test_scoreboard(output_dir):
    """Test loading scoreboard data."""
    score = Scoreboard(
        GameDate="12/25/2018",
        output_dir=output_dir
    )
    score.get()

    for dataset in score.datasets:
        assert score.get_data(dataset).empty
