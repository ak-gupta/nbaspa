"""Test scoreboard endpoint."""

from pathlib import Path

from nbaspa.data.endpoints import Scoreboard

def test_scoreboard(output_dir):
    """Test loading scoreboard data."""
    score = Scoreboard(
        GameDate="12/25/2018",
        output_dir=output_dir
    )

    assert score.fpath == output_dir / Path("scoreboardv2", "data_20181225.json")
    assert score.exists()

    score.get()

    for dataset in score.datasets:
        assert score.get_data(dataset).empty
