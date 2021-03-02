"""Test boxscore endpoint."""

from pathlib import Path

from nbaspa.data.endpoints import BoxScoreTraditional

def test_load_boxscore(output_dir):
    """Test loading boxscore data."""
    box = BoxScoreTraditional(GameID="00218DUMMY", output_dir=output_dir)

    assert box.fpath == output_dir / Path("boxscoretraditionalv2", "data_00218DUMMY.json")
    assert box.exists()

    box.get()

    for dataset in box.datasets:
        assert box.get_data(dataset).empty
