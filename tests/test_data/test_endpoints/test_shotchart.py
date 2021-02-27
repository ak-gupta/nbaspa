"""Test loading shotchart data."""

from pathlib import Path

from nbaspa.data.endpoints import ShotChart

def test_shotchart(output_dir):
    """Test loading shotchart data."""
    shot = ShotChart(
        GameID="00218DUMMY",
        Season="2018-19",
        output_dir=output_dir
    )

    assert shot.fpath == output_dir / Path("shotchartdetail", "data_00218DUMMY.json")
    assert shot.exists()

    shot.get()

    for dataset in shot.datasets:
        assert shot.get_data(dataset).empty
