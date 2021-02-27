"""Test boxscore endpoint."""

from nbaspa.data.endpoints import BoxScoreTraditional

def test_load_boxscore(output_dir):
    """Test loading boxscore data."""
    box = BoxScoreTraditional(GameID="00218DUMMY", output_dir=output_dir)
    box.get()

    for dataset in box.datasets:
        assert box.get_data(dataset).empty
